"""Wrapper module for the data endpoint."""
import json
import warnings

import requests

from pygenesis.config import load_config

config = load_config()


def get_response_from_endpoint(
    endpoint: str, method: str, params: dict
) -> requests.Response:
    """
    Wrapper method which constructs a url for querying data from Destatis and
    sends a GET request.

    Args:
        endpoint (str): Destatis endpoint (eg. data, catalogue, ..)
        method (str): Destatis method (eg. cube, tablefile, ...)
        params (dict): dictionary of query parameters

    Returns:
        requests.Response: the response from Destatis
    """
    url = f"{config['GENESIS API']['base_url']}{endpoint}/{method}"

    params |= {
        "username": config["GENESIS API"]["username"],
        "password": config["GENESIS API"]["password"],
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
        AssertionError: Assert that status is not 4xx or 5xx
    """
    assert status_code // 100 not in [
        4,
        5,
    ], f"Error {status_code}: The server returned a {status_code} status code"


def _check_invalid_destatis_status_code(response: requests.Response) -> None:
    """
    Helper method which handles the status code returned from Destatis
    (if exists)

    Args:
        response (requests.Response): The response object from the request

    """
    try:
        response_dict = response.json()
    # catch possible errors raised by .json() (and only .json())
    except (
        UnicodeDecodeError,
        json.decoder.JSONDecodeError,
        requests.exceptions.JSONDecodeError,
    ):
        response_dict = None

    if response_dict is not None:
        _check_destatis_status(response_dict.get("Status", {}))


def _check_destatis_status(destatis_status: dict) -> None:
    """
    Helper method which checks the status message from Destatis.
    If the status message is erroneous an error will be raised.

    Possible Codes (2.1.2 Grundstruktur der Responses):
    - 0: "erfolgreich" (Type: "Information")
    - 22: "erfolgreich mit Parameteranpassung" (Type: "Warnung")
    - 104: "Kein passendes Objekt zu Suche" (Type: "Information")

    Args:
        destatis_status (dict): Status response dict from Destatis

    Raises:
        # TODO: Is this a Value or KeyError?
        ValueError: If the status code or type displays an error (caused by the user inputs)
    """
    # -1 status code for unexpected errors and if no status code is given (faulty response)
    destatis_status_code = destatis_status.get("Code", -1)
    destatis_status_type = destatis_status.get("Type")
    destatis_status_content = destatis_status.get("Content")

    error_en_de = ["Error", "Fehler"]
    warning_en_de = ["Warning", "Warnung"]

    # check for generic/ system error
    if destatis_status_code == -1:
        raise ValueError(
            "Error: There is a system error.\
                Please check your query parameters."
        )

    # check for destatis/ query errors
    elif (destatis_status_code == 104) or (destatis_status_type in error_en_de):
        raise ValueError(destatis_status_content)

    # print warnings to user
    elif (destatis_status_code == 22) or (
        destatis_status_type in warning_en_de
    ):
        warnings.warn(destatis_status_content, UserWarning, stacklevel=2)

    # TODO: pass response information to user, however logger.info might be overlooked
    # as standard only shows beyond warning -> HowTo?
