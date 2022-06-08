from pygenesis.destatis import get_catalogue, get_metadata


class Statistic:
    def __init__(self, name: str) -> None:
        self.name = name
        self.metadata: dict = get_metadata("statistic", name).get("Object", {})
        self.cubes: list = get_catalogue(
            "cubes2statistic", {"name": name, "selection": ""}
        ).get("List", [])
        self.variables: list = get_catalogue(
            "variables2statistic", {"name": name, "selection": ""}
        ).get("List", [])
        self.tables: list = get_catalogue(
            "tables2statistic", {"name": name, "selection": ""}
        ).get("List", [])


if __name__ == "__main__":
    stat = Statistic("23211")
    print("metadata:", stat.metadata)
    print("cubes:", stat.cubes)
    print("variables:", stat.variables)
    print("tables:", stat.tables)
