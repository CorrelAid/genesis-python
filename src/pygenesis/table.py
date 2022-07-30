"""Module contains business logic related to destatis tables."""
import pandas as pd

from pygenesis.csv_helper import get_df_from_text
from pygenesis.http_helper import get_response_from_endpoint


def get_tablefile_data(
    table_name: str, table_area: str = "all", **kwargs
) -> pd.DataFrame:
    """
    Based on the table name, table area and additional query parameters the
    tablefile method from the data-endpoint will be queried.

    Args:
        table_name (str): Name of the table
        table_area (str, optional): Area of the table (Defaul: all)
        query_params (dict, optional): Additional query parameters
        (Default: None)
    Returns:
        pd.DataFrame
    """

    kwargs = kwargs or {}

    params = {
        "name": table_name,
        "area": table_area,
        "format": "ffcsv",
    }

    params |= kwargs

    response = get_response_from_endpoint("data", "tablefile", params)
    return get_df_from_text(response.text)
