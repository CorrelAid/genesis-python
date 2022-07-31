import os

import pandas as pd

from pygenesis.destatis import get_catalogue

pd.set_option("max_colwidth", None)
pd.set_option("expand_frame_repr", False)


class Hierarchy:
    def __init__(self, code: int = None):
        """Method for retrieving data based on the Evas hierarchy. The code can be provided partially or fully. If
        the code is None, the first level of Evas will be provided. If one or two code numbers are provided the Evas
        hierarchy is provided. Given three or more digits the tables will be retrieved from the catalogue endpoint.

        Args:
            code (int): The table code.

        Returns:
            self.catalogue: Results of tables.
        """

        self.code = code
        self.catalogue = self._query_hierarchy()
        print(self._print_summary())

    def _query_hierarchy(self):

        evas_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "data", "evas.csv"
        )
        classification: pd.DataFrame = pd.read_csv(
            evas_path, encoding="utf8", sep=";", index_col=0
        )

        if self.code is None:
            return classification.loc[0:10]

        elif self.code < 100:
            filter_min = self.code * 10
            filter_max = (self.code * 10) + 9
            return classification.loc[int(filter_min) : int(filter_max)]

        else:
            df = pd.DataFrame(
                get_catalogue("tables", {"selection": f"{self.code}*"}).get(
                    "List"
                )
            ).replace("\n", "", regex=True)
            return df

    def _print_summary(self):
        return "\n".join(
            [
                "Hierarchie",
                "{}".format("-" * 40),
                str(self.catalogue),
                "{}".format("-" * 40),
                "# Info: Use objekt.catalogue to access results.",
            ]
        )
