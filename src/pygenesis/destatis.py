import dotenv
import requests

config = dotenv.dotenv_values()
print(config)


def get_metadata(endpoint: str, name: str) -> dict:
    """Method for downloading metadata from www-genesis.destatis.de.

    Method supports the following endpoints:
    - cube
    - statistic
    - table
    - timeseries
    - value
    - variable

    Args:
        endpoint (str): One of the supported endpoints, e.g. statistic
        name (str): Unique name of the object.

    Returns:
        dict: Content of "Object" response.
    """
    url = f"https://www-genesis.destatis.de/genesisWS/rest/2020/metadata/{endpoint}"

    params = {
        "username": config["PYGENESIS_USERNAME"],
        "password": config["PYGENESIS_PASSWORD"],
        "name": name,
    }
    headers = {}

    response = requests.request("GET", url, params=params, verify=False)

    return response.json()


def get_catalogue(endpoint: str, query_params: dict) -> list:
    url = f"https://www-genesis.destatis.de/genesisWS/rest/2020/catalogue/{endpoint}"

    params = {
        "username": config["PYGENESIS_USERNAME"],
        "password": config["PYGENESIS_PASSWORD"],
    }
    params |= query_params

    response = requests.request("GET", url, params=params, verify=False)

    return response.json()
