"""Module provides functions to work with the GENESIS REST-API."""
import dotenv
import requests

config = dotenv.dotenv_values()


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
        endpoint (str): One of the supported endpoints, e.g. statistic.
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

    response = requests.request("GET", url, params=params, verify=False)

    return response.json()


def get_catalogue(endpoint: str, query_params: dict) -> list[dict]:
    """Method for downloading catalogue data from www-genesis.destatis.de.

    Args:
        endpoint (str): One of the supported endpoints, e.g. cubes.
        query_params (dict): The query parameter as defined by the API.

    Returns:
        list: A list of hits in the catalog matching the query parameter.
    """
    url = f"https://www-genesis.destatis.de/genesisWS/rest/2020/catalogue/{endpoint}"

    params = {
        "username": config["PYGENESIS_USERNAME"],
        "password": config["PYGENESIS_PASSWORD"],
    }
    params |= query_params

    response = requests.request("GET", url, params=params, verify=False)

    return response.json()


def get_cubefile(query_params: dict) -> str:
    """Method for downloading cube files from www-genesis.destatis.de.

    Args:
        query_params (dict): The query parameter as defined by the API.

    Returns:
        str: The content of the cubefile.
    """
    url = "https://www-genesis.destatis.de/genesisWS/rest/2020/data/cubefile"

    params = {
        "username": config["PYGENESIS_USERNAME"],
        "password": config["PYGENESIS_PASSWORD"],
    }
    params |= query_params

    response = requests.request("GET", url, params=params, verify=False)

    return response.text
