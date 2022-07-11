"""Module contains business logic related to destatis tables."""
import pandas as pd

from pygenesis.config_loader import CONFIG
from pygenesis.csv_helper import get_df_from_text
from pygenesis.http_helper import get_response_from_endpoint


def get_tablefile_data(
    table_name: str, table_area: str, query_params: dict = None
) -> pd.DataFrame:
    """
    Based on the table name, table area and additional query parameters the
    tablefile method from the data-endpoint will be queried.

    Args:
        table_name (str): Name of the table
        table_area (str): Area of the table (all, ..)
        query_params (dict, optional): Additional query parameters

    Returns:
        pd.DataFrame
    """

    query_params = query_params or {}
    params = {
        "username": CONFIG["PYGENESIS_USERNAME"],
        "password": CONFIG["PYGENESIS_PASSWORD"],
        "name": table_name,
        "area": table_area,
    }

    params |= query_params

    response = get_response_from_endpoint("data", "tablefile", params)
    return get_df_from_text(response.text, skiprows=6)
