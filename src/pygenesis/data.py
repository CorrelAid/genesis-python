"""Provides functionality to download data from GENESIS data endpoint."""
from typing import Literal

import pandas as pd

from pygenesis.cache import cache_data
from pygenesis.cube import parse_cube, rename_axes
from pygenesis.http_helper import get_response_from_endpoint
from pygenesis.table import get_tablefile_data

METHODS = Literal["tablefile", "cubefile"]


@cache_data
def get_data(
    *, name: str, method: METHODS, area: str = "all", **kwargs
) -> pd.DataFrame:
    """Download data from GENESIS.

    Based on the name, area and additional query parameters the
    given method from the data-endpoint will be queried.

    Args:
        name (str): Name of the object.
        method (str): Method of the data endpoint used to query data. One of ["tablefile", "cubefile"].
        area (str, optional): Area the object is stored. Defaults to "all".

    Returns:
        pd.DataFrame: Parsed data file.
    """
    kwargs = kwargs or {}

    params = {
        "name": name,
        "area": area,
    }

    if method == "tablefile":
        params["format"] = "ffcsv"

    params |= kwargs

    response = get_response_from_endpoint("data", method, params)
    data = response.text

    if method == "tablefile":
        return _get_tablefile_data(data)
    else:
        return _get_cubefile_data(data)


def _get_cubefile_data(data: str) -> pd.DataFrame:
    cube = rename_axes(parse_cube(data))
    return cube["QEI"]


def _get_tablefile_data(data: str) -> pd.DataFrame:
    return get_tablefile_data(data)
