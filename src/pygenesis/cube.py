"""Module provides functionality to parse cubefile data provided by GENESIS."""
import copy
import json

import pandas as pd

from pygenesis.http_helper import get_data_from_endpoint


class Cube:
    def __init__(self, name: str):
        self.name = name
        self.raw_data = ""
        self.data = pd.DataFrame()
        self.cube = {}
        self.metadata = {}

    def get_data(self, area: str = "all", **kwargs):
        params = {"name": self.name, "area": area}

        params |= kwargs

        raw_data = get_data_from_endpoint(
            endpoint="data", method="cubefile", params=params
        )
        self.raw_data = raw_data
        self.cube = assign_correct_types(rename_axes(parse_cube(raw_data)))
        self.data = self.cube["QEI"]

        raw_data = get_data_from_endpoint(
            endpoint="metadata", method="cube", params=params
        )
        self.metadata = json.loads(raw_data)


def parse_cube(data: str) -> dict:
    """Main function for parsing a cubefile.

    Args:
        data (str): The content of a cubefile as returned by GENESIS.

    Returns:
        dict: A dictionary with each header type as key and the corresponding header block as value.
    """
    cube = {}
    header = None
    data_block: list[str] = []

    for line in data.splitlines():
        # skip all rows until first header
        if header is None and not _is_cube_metadata_header(line):
            continue

        if _is_cube_metadata_header(line):
            if data_block:
                cube[header_type] = pd.DataFrame(data_block, columns=header)

            header = _get_cube_metadata_header(line, rename_duplicates=True)
            header_type: str = _get_cube_metadata_header_type(line)
            data_block = []
            continue

        line_content = _parse_cube_data_line(line)
        data_block.append(line_content)

    # the last data block has no header after it so we have to do it here
    # for cubes with more than one variable in DQI, we have to repeat the last four columns
    last_four_columns = header[-4:]
    header = header[:-4]
    for var in cube["DQI"]["NAME"]:
        header.extend([f"{var}_{col}" for col in last_four_columns])

    cube[header_type] = pd.DataFrame(data_block, columns=header)

    return cube


def rename_axes(
    cube: dict,
    rename_classifying_variables: bool = True,
    rename_time_variable: bool = True,
) -> dict:
    """Rename the generic axes of a cubefile with the names found in the metadata.

    Args:
        cube (dict): A dictionary holding the cube data as returned by `parse_cube()`.
        rename_classifying_variables (bool, optional): If True, rename classifying variables.
            Defaults to True.
        rename_time_variable (bool, optional): If True, rename the time variable.
            Defaults to True.

    Returns:
        dict: Same dict as cube but with renamed axes for QEI.
    """
    cube = copy.deepcopy(cube)

    old_cols = []
    new_cols = []

    if rename_classifying_variables:
        old_cols.extend(
            [col for col in cube["QEI"].columns if col.startswith("FACH-SCHL")]
        )
        new_cols.extend(cube["DQA"].sort_values("RHF-ACHSE")["NAME"].to_list())

    if rename_time_variable:
        old_cols.append("ZI-WERT")
        new_cols.extend(cube["DQZ"]["NAME"].to_list())

    cube["QEI"].rename(columns=dict(zip(old_cols, new_cols)), inplace=True)

    return cube


def assign_correct_types(cube: dict) -> dict:
    """Assign correct value types to column 'WERT'.

    Args:
        cube (dict): A dictionary holding the cube data as returned by `parse_cube()`.

    Returns:
        dict: Same dict as cube but with changed column types for QEI.
    """
    cube = copy.deepcopy(cube)

    for var, dtype in zip(cube["DQI"]["NAME"], cube["DQI"]["DST"]):
        if dtype == "GANZ":
            cast_type = int
        elif dtype == "FEST":
            cast_type = float
        else:
            cast_type = None

        if cast_type is not None:
            cube["QEI"].loc[:, f"{var}_WERT"] = (
                cube["QEI"].loc[:, f"{var}_WERT"].astype(cast_type)
            )

    return cube


def _is_cube_metadata_header(line: str) -> bool:
    """Check if a line is a cube metadata header."""
    return line[0] == "K"


def _get_cube_metadata_header_type(line: str) -> str:
    """Return the header type."""
    return line.split(";")[1]


def _get_cube_metadata_header(
    line: str, rename_duplicates: bool = False
) -> list[str]:
    """Return the metadata header of a cubefile."""
    raw_header = line.split(";")[2:]
    raw_header = [
        name
        for name in raw_header
        if name not in ['"nur Werte"', '"mit Werten"']
    ]

    if not rename_duplicates:
        return raw_header

    # header can have multiple entries with same label, which is problematic for pandas
    # so lets just add a counter
    header = [""] * len(raw_header)
    for name in set(raw_header):
        if raw_header.count(name) == 1:
            header[raw_header.index(name)] = name
        else:
            for counter in range(raw_header.count(name)):
                header[raw_header.index(name) + counter] = f"{name}-{counter+1}"

    return header


def _parse_cube_data_line(line: str) -> list[str]:
    """Return the content of a cube data line."""
    return line.split(";")[1:]
