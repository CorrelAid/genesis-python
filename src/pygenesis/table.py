"""Module contains business logic related to destatis tables."""
import json
from io import StringIO

import pandas as pd

from pygenesis.http_helper import get_data_from_endpoint


class Table:
    """A wrapper class holding all relevant data and metadata about a given table.

    Args:
        name (str): The unique identifier of this table.
        raw_data (str): The raw tablefile data as returned by the /data/table endpoint.
        data (pd.DataFrame): The parsed data as a pandas data frame.
        metadata (dict): Metadata as returned by the /metadata/table endpoint.
    """

    def __init__(self, name: str):
        self.name: str = name
        self.raw_data = ""
        self.data = pd.DataFrame()
        self.metadata: dict = {}

    def get_data(self, area: str = "all", **kwargs):
        """Downloads raw data and metadata from GENESIS-Online.

        Additional keyword arguments are passed on to the GENESIS-Online GET request for tablefile.

        Args:
            area (str, optional): Area to search for the object in GENESIS-Online. Defaults to "all".
        """
        params = {"name": self.name, "area": area, "format": "ffcsv"}

        params |= kwargs

        raw_data = get_data_from_endpoint(
            endpoint="data", method="tablefile", params=params
        )
        self.raw_data = raw_data
        data_str = StringIO(raw_data)
        self.data = pd.read_csv(data_str, sep=";")

        raw_data = get_data_from_endpoint(
            endpoint="metadata", method="table", params=params
        )
        self.metadata = json.loads(raw_data)
