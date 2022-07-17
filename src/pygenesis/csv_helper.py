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
    return _cut_footer(pd.read_csv(data_str, sep=";"))


def _cut_footer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper fucntion to cut the footer of a destatis csv file.

    Args:
        df (pd.DataFrame): DataFrame which contains the footer

    Returns:
        pd.DataFrame
    """
    return df.iloc[:-4, :]
