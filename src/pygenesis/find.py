import pandas as pd

from pygenesis.csv_helper import get_df_from_text
from pygenesis.http_helper import get_response_from_endpoint

pd.set_option("max_colwidth", None)
pd.set_option("expand_frame_repr", False)


class Results:
    def __init__(self, results: pd.DataFrame):
        """Class that contains the results of a find query.

        Args:
            DataFrame (pd.DataFrame): Result of a search query.
        """
        self.df = results

    def __repr__(self):
        return repr(self.df)

    def __str__(self):
        return repr(self.df)

    def __len__(self):
        len(self.df)

    def get_code(self, index: list):
        code = self.df.iloc[index]["Code"]
        return list(code)


class Find:
    def __init__(self, query: str, top_n_preview: int = 5) -> None:
        """Method for retrieving data from find endpoint.

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
        self.statistics = self._get_find_results(query, "statistics")
        self.variables = self._get_find_results(query, "variables")
        self.tables = self._get_find_results(query, "tables")

        print(self._print_summary())

    def _print_summary(self):
        return "\n".join(
            [
                "##### Results #####",
                "{}".format("-" * 40),
                "# Number of tables: {}".format(len(self.tables.df)),
                "# Preview:",
                str(self.tables.df.iloc[0 : self.top_n_preview]),
                "{}".format("-" * 40),
                "# Number of statistics: {}".format(len(self.statistics.df)),
                "# Preview:",
                str(self.statistics.df.iloc[0 : self.top_n_preview]),
                "{}".format("-" * 40),
                "# Number of variables: {}".format(len(self.variables.df)),
                "# Preview:",
                str(self.variables.df.iloc[0 : self.top_n_preview]),
                "{}".format("-" * 40),
                "# Info: Use object.tables, object.statistics or object.variables to get all results.",
                "{}".format("-" * 40),
            ]
        )

    @staticmethod
    def _get_find_results(query: str, category: str, **kwargs) -> Results:
        """
        Based on the table name, table area and additional query parameters the
        tablefile method from the data-endpoint will be queried.

        Args:
            table_name (str): Name of the table
            table_area (str, optional): Area of the table (Defaul: all)
            query_params (dict, optional): Additional query parameters
            (Default: None)
        Returns:
            pd.DataFrame
        """

        kwargs = kwargs or {}

        params = {
            "term": query,
            "category": category,
        }

        params |= kwargs

        response = get_response_from_endpoint("find", "find", params)
        response_json = response.json()[category.capitalize()]
        resonse_df = pd.DataFrame(response_json).replace("\n", " ", regex=True)

        return Results(resonse_df)
