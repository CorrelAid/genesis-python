"""Wrapper module for the data endpoint."""
import requests

from pygenesis.config_loader import CONFIG

# TODO: \global vars init? .env?
base_url = "https://www-genesis.destatis.de/genesisWS/rest/2020"


def get_response_from_endpoint(
    endpoint: str, method: str, params: dict
) -> requests.Response:
    """
    Wrapper method which constructs a url for querying data from destatis and
    sends a GET request.

    Args:
        endpoint (str): Destatis endpoint (eg. data, catalogue, ..)
        method (str): Destatis method (eg. cube, tablefile, ...)
        params (dict): dictionary of query parameters

    Returns:
        requests.Response: the response from destatis
    """
    url = f"{base_url}/{endpoint}/{method}"

    params |= {
        "username": CONFIG["PYGENESIS_USERNAME"],
        "password": CONFIG["PYGENESIS_PASSWORD"],
    }

    response = requests.get(url, params=params)

    response.encoding = "UTF-8"

    _check_invalid_status_code(response.status_code)
    _check_invalid_destatis_status_code(response)
    return response


def _check_invalid_status_code(status_code: int) -> None:
    """
    Helper method which handles the status code from the response

    Args:
        status_code (int): Status code from the response object

    Raises:
        Exception: Generic exception if 401 is returned
    """
    if (status_code // 100) == 4:
        raise Exception(
            f"Error {status_code}: The server returned a {status_code} status code"
        )


def _check_invalid_destatis_status_code(response: requests.Response) -> None:
    """
    Helper method which handles the status code returned from destatis
    (if exists)

    Args:
        response (requests.Response): The response object from the request

    """
    try:
        response_dict = response.json()
    except ValueError:
        return None
    _check_destatis_status_code(response_dict.get("Status", {}).get("Code"))
    return None


def _check_destatis_status_code(destatis_status_code: int) -> None:
    """
    Helper method which checks the status code from destatis.
    If the status code is not valid an exception will be raised.

    Args:
        destatis_status_code (int): Status code from destatis

    Raises:
        Exception: Generic exception if the status code from destatis is equal
        to -1
    """
    if destatis_status_code == -1:
        raise Exception(
            "Error: There is a system error.\
                Please check your query parameters."
        )
