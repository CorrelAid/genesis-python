"""Module provides functionality to parse a cube data as returned by the /data/cubefile endpoint of GENESIS."""
import copy

import pandas as pd


def is_cube_metadata_header(line: str) -> bool:
    return line[0] == "K"


def get_cube_metadata_header_type(line: str) -> str:
    return line.split(";")[1]


def get_cube_metadata_header(
    line: str, rename_duplicates: bool = False
) -> list[str]:
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
    header = [None] * len(raw_header)
    for name in set(raw_header):
        if raw_header.count(name) == 1:
            header[raw_header.index(name)] = name
        else:
            for counter in range(raw_header.count(name)):
                header[raw_header.index(name) + counter] = f"{name}-{counter+1}"

    return header


def parse_cube_data_line(line: str) -> list[str]:
    return line.split(";")[1:]


def parse_cube_metadata_block(
    rows: list[list[str]], header: list[str]
) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=header)


def parse_cube(data: str) -> dict:
    cube = {}
    header = None
    data_block = []

    for line in data.splitlines():
        # skip all rows until first header
        if header is None and not is_cube_metadata_header(line):
            continue

        if is_cube_metadata_header(line):
            if data_block:
                cube[header_type] = pd.DataFrame(data_block, columns=header)

            header = get_cube_metadata_header(line, rename_duplicates=True)
            header_type = get_cube_metadata_header_type(line)
            data_block = []
            continue

        line_content = parse_cube_data_line(line)
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

    return cube["QEI"].rename(
        columns={old: new for old, new in zip(old_cols, new_cols)}
    )
