"""Implements find endpoint to retrieve results based on query"""

import pandas as pd

from pygenesis.http_helper import get_response_from_endpoint

pd.set_option("max_colwidth", None)
pd.set_option("expand_frame_repr", False)


class Results:
    """
    A class representing the result object of variables, statistics, cubes and tables.

    Attributes:
        df (pd.DataFrame): The DataFrame that contains the data.
        category (str): Category of the result. E.g. "tables", "cubes".

    Methods:
        get_code(): Gets code based on the index of the object.
        get_metadata(): Gets metadata based on the index of the object.
    """

    def __init__(self, result: pd.DataFrame, category: str):
        """
        Class that contains the results of a find query.

        Args:
            DataFrame (pd.DataFrame): Result of a search query.
            category (str): Category of the result. E.g. "tables", "cubes"
        """
        self.df = result
        self.category = category

    def __repr__(self):
        return self.df.to_markdown()

    def __str__(self):
        return self.df.to_markdown()

    def __len__(self):
        if len(self.df) > 0:
            return len(self.df)
        else:
            return 0

    def get_code(self, index: list):
        """
        Returns the for a given list of tables

        Args:
             index (list): A list that contains the indices from the results objects. This is not the object code."
        Returns:
             table codes (list): Contains the corresponding tables codes.
        """

        codes = self.df.iloc[index]["Code"]
        return list(codes)

    def get_metadata(self, index: list):
        """
        Prints meta data for a given list of tables.

        Args:
              index (list): A list that contains the indices from the results objects. This is not the object code."
        Returns:
              prints meta data for all indices.
        """
        codes = self.df.iloc[index]["Code"]

        for code, ix in zip(codes, index):
            response = self._get_metadata_results(self.category[0:-1], code)

            if self.category == "tables":
                structure_dict = response["Object"]["Structure"]

                output = "\n".join(
                    [
                        f"{self.category.upper()} {code} - {ix}",
                        "Name:",
                        structure_dict["Head"]["Content"],
                        f"{'-' * 20}",
                        "Columns:",
                        "\n".join(
                            [
                                col["Content"]
                                for col in structure_dict["Columns"]
                            ]
                        ),
                        f"{'-' * 20}",
                        "Rows:",
                        "\n".join(
                            [row["Content"] for row in structure_dict["Rows"]]
                        ),
                        f"{'-' * 40}",
                    ]
                )

            elif self.category == "cubes":
                axis_dict = response["Object"]["Structure"]["Axis"]

                output = "\n".join(
                    [
                        f"{self.category.upper()} {code} - {ix}",
                        "Name:",
                        response["Object"]["Content"],
                        f"{'-' * 20}",
                        "Content:",
                        "\n".join(
                            [content["Content"] for content in axis_dict]
                        ),
                        f"{'-' * 40}",
                    ]
                )

            elif self.category == "statistics":
                structure_dict = response["Object"]

                output = "\n".join(
                    [
                        f"{self.category.upper()} {code} - {ix}",
                        "Name:",
                        response["Object"]["Content"],
                        f"{'-' * 20}",
                        "Content:",
                        "\n".join(
                            [
                                f"{structure_dict[content]} {content}"
                                for content in ["Cubes", "Variables", "Updated"]
                            ]
                        ),
                        f"{'-' * 40}",
                    ]
                )

            elif self.category == "variables":
                object_dict = response["Object"]

                output = "\n".join(
                    [
                        f"{self.category.upper()} {code} - {ix}",
                        "Name:",
                        object_dict["Content"],
                        f"{'-' * 20}",
                        "Information:",
                        str(object_dict["Information"]),
                        f"{'-' * 40}",
                    ]
                )

            print(output)

    @staticmethod
    def _get_metadata_results(category: str, code: str):
        """
        Based on the category and code query parameters the metadata will be generated.

        Args:
            category (str): Category of the result. E.g. "tables", "cubes"
            code (str): The code (identifier) of the relevant category object.
        Returns:
            response (json): The response as a json.
        """
        params = {
            "name": code,
        }

        response = get_response_from_endpoint("metadata", category, params)
        response_json = response.json()

        return response_json


class Find:
    """
    A class representing the find object that includes Result objects for variables, statistics, cubes and tables.

    Attributes:
        query (str): The query that is provided to find endpoint.
        top_n_preview (int): Number of previews in print summary.

    Methods:
        _print_summary(): Prints a summary with result previews.
        _get_find_results(): Gets results from the find endpoints.
    """

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
        self.cubes = self._get_find_results(query, "cubes")

        print(self._print_summary())

    def _print_summary(self):
        return "\n".join(
            [
                "##### Results #####",
                f"{'-' * 40}",
                f"# Number of tables: {len(self.tables.df)}",
                "# Preview:",
                self.tables.df.iloc[0 : self.top_n_preview].to_markdown(),
                f"{'-' * 40}"
                f"# Number of statistics: {len(self.statistics.df)}",
                "# Preview:",
                self.statistics.df.iloc[0 : self.top_n_preview].to_markdown(),
                f"{'-' * 40}",
                f"# Number of variables: {len(self.variables.df)}",
                "# Preview:",
                self.variables.df.iloc[0 : self.top_n_preview].to_markdown(),
                f"{'-' * 40}",
                f"# Number of cubes: {len(self.cubes.df)}",
                "# Preview:",
                self.cubes.df.iloc[0 : self.top_n_preview].to_markdown(),
                f"{'-' * 40}",
                "# Info: Use object.tables, object.statistics, object.variables or object.cubes to get all results.",
                f"{'-' * 40}",
            ]
        )

    @staticmethod
    def _get_find_results(query: str, category: str, **kwargs) -> Results:
        """
        Based on the query (term), category and additional query parameters a Result object will be created.

        Args:
            query (str): Search term.
            category (str): Category of the result. E.g. "tables", "cubes"
            query_params (dict, optional): Additional query parameters (Default: None)
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
        response_df = pd.DataFrame(response_json).replace("\n", " ", regex=True)

        return Results(response_df, category)


if __name__ == "__main__":
    results = Find("Rohöl")
    results.tables.get_code([1, 2, 3])
    results.tables.get_metadata([1, 2])
    results.cubes.get_metadata([1, 2])
