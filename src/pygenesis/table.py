"""Module contains business logic related to destatis tables."""
from io import StringIO

import pandas as pd

from pygenesis.http_helper import get_response_from_endpoint


class Table:
    def __init__(self, name: str):
        self.name = name
        self.raw_data = ""
        self.data = pd.DataFrame()
        self.metadata = {}

    def get_data(self, area: str = "all", **kwargs):
        params = {"name": self.name, "area": area, "format": "ffcsv"}

        params |= kwargs

        response = get_response_from_endpoint("data", "tablefile", params)
        self.raw_data = response.text
        data_str = StringIO(self.raw_data)
        self.data = pd.read_csv(data_str, sep=";")

        response = get_response_from_endpoint("metadata", "table", params)
        self.metadata = response.json()
