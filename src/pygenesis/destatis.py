"""Module provides functions to work with the GENESIS REST-API."""
from pygenesis.config import load_config
from pygenesis.http_helper import get_response_from_endpoint

config = load_config()


def get_metadata(endpoint: str, name: str) -> str:
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
        str: Content of "Object" response.
    """
    params = {
        "name": name,
    }

    return get_response_from_endpoint("metadata", endpoint, params).text


def get_catalogue(endpoint: str, params: dict) -> dict:
    """Method for downloading catalogue data from www-genesis.destatis.de.

    Args:
        endpoint (str): One of the supported endpoints, e.g. cubes.
        params (dict): The query parameter as defined by the API.

    Returns:
        dict: JSON formated response for the given query parameters.
    """

    return get_response_from_endpoint("catalogue", endpoint, params).json()


def get_cubefile(params: dict) -> str:
    """Method for downloading cube files from www-genesis.destatis.de.

    Args:
        params (dict): The query parameter as defined by the API.

    Returns:
        str: The content of the cubefile.
    """

    return get_response_from_endpoint("data", "cubefile", params).text
