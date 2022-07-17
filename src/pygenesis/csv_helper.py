"""Module contains the business logic for CSV related operations."""
from io import StringIO

import pandas as pd


def get_df_from_text(data_text: str) -> pd.DataFrame:
    """
    Helper function to convert response text to a pandas DataFrame.

    Args:
        data_text (str): the text convered to a DataFrame
        skiprows (int, optional): How many rows should be skipped. Defaults to 0.

    Returns:
        pd.DataFrame
    """
    if not isinstance(data_text, str):
        return None

    data_str = StringIO(f"""{data_text}""")
    return pd.read_csv(data_str, sep=";")
