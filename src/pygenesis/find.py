import pandas as pd

from pygenesis.csv_helper import get_df_from_text
from pygenesis.http_helper import get_response_from_endpoint

pd.set_option("max_colwidth", None)
pd.set_option("expand_frame_repr", False)


def get_find_data(query: str, category: str, **kwargs) -> pd.DataFrame:
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

    return pd.DataFrame(response_json).replace("\n", "", regex=True)


class SummaryResults:
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
        self.statistics = get_find_data(query, "statistics")
        self.variables = get_find_data(query, "variables")
        self.tables = get_find_data(query, "tables")

        print(self._print_summary())

    def _print_summary(self):
        return "\n".join(
            [
                "##### Results #####",
                "{}".format("-" * 40),
                "# Number of tables: {}".format(len(self.tables)),
                "# Preview:",
                str(self.tables.iloc[0 : self.top_n_preview]),
                "{}".format("-" * 40),
                "# Number of statistics: {}".format(len(self.statistics)),
                "# Preview:",
                str(self.statistics.iloc[0 : self.top_n_preview]),
                "{}".format("-" * 40),
                "# Number of variables: {}".format(len(self.variables)),
                "# Preview:",
                str(self.variables.iloc[0 : self.top_n_preview]),
                "{}".format("-" * 40),
                "# Info: Use object.tables, object.statistics or object.variables to get all results.",
                "{}".format("-" * 40),
            ]
        )
