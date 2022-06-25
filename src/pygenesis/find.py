from pygenesis.destatis import get_find


class Find:
    def __init__(self, query: str) -> None:
        self.query = query
        self.statistics: list = get_find(
            {"term": query, "category": "statistics"}
        ).get("Statistics")
        self.variables: list = get_find(
            {"term": query, "category": "variables"}
        ).get("Variables")
        self.tables: list = get_find({"term": query, "category": "tables"}).get(
            "Tables"
        )


if __name__ == "__main__":
    find = Find("Erdöl")
    print("cubes:", find.statistics)
    print("variables:", find.variables)
    print("tables:", find.tables)
