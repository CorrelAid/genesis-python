import zipfile
from pathlib import Path

import pytest

from pygenesis.cube import Cube, assign_correct_types, parse_cube, rename_axes


@pytest.fixture
def easy_cube():
    with zipfile.ZipFile(Path(__file__).parent / "rsc" / "data.zip") as myzip:
        with myzip.open("12411BJ001.txt", "r") as file:
            return file.read().decode()


@pytest.fixture
def hard_cube():
    with zipfile.ZipFile(Path(__file__).parent / "rsc" / "data.zip") as myzip:
        with myzip.open("22922KJ1141.txt", "r") as file:
            return file.read().decode()


@pytest.fixture
def raw_data(request, easy_cube, hard_cube):
    if request.param == "easy_cube":
        return easy_cube
    elif request.param == "hard_cube":
        return hard_cube


@pytest.mark.parametrize(
    "raw_data, expected_shape, expected_DQ, expected_DQ_ERH, expected_DQA, expected_DQZ, expected_DQI,",
    [
        (
            "hard_cube",
            (19185, 13),
            "22922KJ114",
            "22922",
            ["KREISE", "GES", "ERW122", "ELGAT2"],
            "JAHR",
            ["ELG002", "ELG003"],
        ),
        (
            "easy_cube",
            (42403, 10),
            "12411BJ001",
            "12411",
            ["DINSG", "NAT", "GES", "FAMST8", "ALT013"],
            "STAG",
            ["BEVSTD"],
        ),
    ],
    indirect=["raw_data"],
)
def test_parse_cube(
    raw_data,
    expected_shape,
    expected_DQ,
    expected_DQ_ERH,
    expected_DQA,
    expected_DQZ,
    expected_DQI,
):
    cube = parse_cube(raw_data)

    assert isinstance(cube, dict)
    assert len(cube) == raw_data.count("K;")

    assert cube["QEI"].shape == expected_shape
    assert cube["DQ"]["FACH-SCHL"].values[0] == expected_DQ
    assert cube["DQ-ERH"]["FACH-SCHL"].values[0] == expected_DQ_ERH
    assert cube["DQA"]["NAME"].to_list() == expected_DQA
    assert cube["DQZ"]["NAME"].values[0] == expected_DQZ
    assert cube["DQI"]["NAME"].to_list() == expected_DQI
