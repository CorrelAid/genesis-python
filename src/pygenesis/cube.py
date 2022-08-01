"""Module provides functionality to parse cubefile data provided by GENESIS."""
import copy

import pandas as pd


def get_data(data: str) -> pd.DataFrame:
    """Return cubefile data as pandas data frame.

    Args:
        data (str): Raw cubefile content.

    Returns:
        pd.DataFrame: Parsed cube file.
    """
    cube = rename_axes(parse_cube(data))

    return cube["QEI"]


def parse_cube(data: str) -> dict:
    """Main function for parsing a cubefile.

    Args:
        data (str): The content of a cubefile as returned by GENESIS.

    Returns:
        dict: A dictionary with each header type as key and the corresponding header block as value.
    """
    cube = {}
    header = None
    data_block: list[pd.DataFrame] = []

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
    cube[header_type] = pd.DataFrame(data_block, columns=header)

    return cube


def rename_axes(
    cube: dict,
    rename_classifying_variables: bool = True,
    rename_time_variable: bool = True,
    rename_value_variables: bool = True,
) -> dict:
    """Rename the generic axes of a cubefile with the names found in the metadata.

    Args:
        cube (dict): A dictionary holding the cube data as returned by `parse_cube()`.
        rename_classifying_variables (bool, optional): If True, rename classifying variables.
            Defaults to True.
        rename_time_variable (bool, optional): If True, rename the time variable.
            Defaults to True.
        rename_value_variables (bool, optional): If True, rename the value variables.
            Defaults to True.

    Returns:
        dict: _description_
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

    if rename_value_variables:
        old_cols.extend(
            [col for col in cube["QEI"].columns if col.startswith("WERT")]
        )
        new_cols.extend(cube["DQI"]["NAME"].to_list())

    cube["QEI"].rename(columns=dict(zip(old_cols, new_cols)), inplace=True)

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
