import pandas as pd

pd.set_option("max_colwidth", None)
pd.set_option("expand_frame_repr", False)

from pygenesis.destatis import get_find


class Find:
    def __init__(self, query: str, top_n_preview: int = 5) -> None:
        """Method for retrieving data from find endoint.

        Args:
            query (str): The query that is provided to find endpoint.
            top_n_preview (int): Number of previews in print summary.

        Returns:
            summary: prints number of search results and firsts results
            self.statistics: Statistics that match with the query.
            self.tables: Tables that match with the query.
            self.variables: Variables that match with the query.
        """

        self.query = query
        self.top_n_preview = top_n_preview
        self.statistics: list = pd.DataFrame(
            get_find({"term": query, "category": "statistics"}).get(
                "Statistics"
            )
        ).replace("\n", "", regex=True)
        self.variables: list = pd.DataFrame(
            get_find({"term": query, "category": "variables"}).get("Variables")
        ).replace("\n", "", regex=True)
        self.tables: list = pd.DataFrame(
            get_find({"term": query, "category": "tables"}).get("Tables")
        ).replace("\n", "", regex=True)
        print(self._print_summary())

    def _print_summary(self):
        return "\n".join(
            [
                "##### Resultate #####",
                "{}".format("-" * 40),
                "# Anzahl Tabellen: {}".format(len(self.tables)),
                "# Vorschau:",
                str(self.tables.iloc[0 : self.top_n_preview]),
                "{}".format("-" * 40),
                "# Anzahl Statistiken: {}".format(len(self.statistics)),
                "# Vorschau:",
                str(self.statistics.iloc[0 : self.top_n_preview]),
                "{}".format("-" * 40),
                "# Anzahl Variablen: {}".format(len(self.variables)),
                "# Vorschau:",
                str(self.variables.iloc[0 : self.top_n_preview]),
                "{}".format("-" * 40),
                "# Info: Nutze objekt.tables, objekt.statistics or objekt.variables um weitere Informationen zu erhalten.",
                "{}".format("-" * 40),
            ]
        )


if __name__ == "__main__":
    find = Find("Studienanfänger")
    print("statistics:", find.statistics)
    print("variables:", find.variables)
    print("tables:", find.tables)
