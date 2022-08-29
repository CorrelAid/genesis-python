"""Module contains business logic related to destatis tables."""
import pandas as pd

from pygenesis.csv_helper import get_df_from_text


def get_tablefile_data(data: str) -> pd.DataFrame:
    """Return table file data as pandas data frame.

    Args:
        data (str): Raw tablefile content.

    Returns:
        pd.DataFrame: Parsed table file.
    """
    return get_df_from_text(data)
