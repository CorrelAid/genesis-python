"""Module contains the business logic for CSV related operations."""
from io import StringIO

import pandas as pd


def get_df_from_text(data_text: str) -> pd.DataFrame:
    """
    Helper function to convert response text to a pandas DataFrame.

    Args:
        data_text (str): the text converted to a DataFrame

    Returns:
        pd.DataFrame
    """
    data_str = StringIO(data_text)
    return pd.read_csv(data_str, sep=";")
