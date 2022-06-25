import pandas as pd

from pygenesis.destatis import get_catalogue


class Hierarchy:
    def __init__(self, name: int = None):
        self.name = name
        self.catalogue = self._query_hierarchy()

    def _query_hierarchy(self):

        classification: pd.DataFrame = pd.read_csv(
            "data/evas.csv", encoding="utf8", sep=";", index_col=0
        )

        if self.name is None:
            return classification.loc[0:10]

        elif self.name < 100:
            filter_min = self.name * 10
            filter_max = (self.name * 10) + 9
            return classification.loc[int(filter_min) : int(filter_max)]

        else:
            df = get_catalogue("tables", {"selection": f"{self.name}*"}).get(
                "List"
            )
            return df


if __name__ == "__main__":
    hierarchy = Hierarchy(211)
    print(hierarchy.catalogue)
