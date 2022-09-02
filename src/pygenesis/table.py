"""Module contains business logic related to destatis tables."""
import json
from io import StringIO

import pandas as pd

from pygenesis.http_helper import get_data_from_endpoint


class Table:
    def __init__(self, name: str):
        self.name = name
        self.raw_data = ""
        self.data = pd.DataFrame()
        self.metadata = {}

    def get_data(self, area: str = "all", **kwargs):
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
