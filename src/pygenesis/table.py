"""Module contains business logic related to destatis tables."""
import pandas as pd

from pygenesis.cache import cache_data
from pygenesis.csv_helper import get_df_from_text
from pygenesis.http_helper import get_response_from_endpoint


@cache_data
def get_tablefile_data(
    *, name: str, area: str = "all", **kwargs
) -> pd.DataFrame:
    """Return table file data as pandas data frame.

    Based on the table name, table area and additional query parameters the
    tablefile method from the data-endpoint will be queried.

    Args:
        name (str): Name of the table.
        area (str, optional): Area of the table. Defaults to "all".

    Returns:
        pd.DataFrame: Parsed table file.
    """

    kwargs = kwargs or {}

    params = {
        "name": name,
        "area": area,
        "format": "ffcsv",
    }

    params |= kwargs

    response = get_response_from_endpoint("data", "tablefile", params)

    return get_df_from_text(response.text)
