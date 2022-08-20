"""Wrapper module for the data endpoint."""
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
        Exception: Generic exception if status 4xx or 5xx is returned
    """
    if (status_code // 100) in [4, 5]:
        raise Exception(
            f"Error {status_code}: The server returned a {status_code} status code"
        )

    return None


def _check_invalid_destatis_status_code(response: requests.Response) -> None:
    """
    Helper method which handles the status code returned from Destatis
    (if exists)

    Args:
        response (requests.Response): The response object from the request

    """
    try:
        response_dict = response.json()
    except ValueError:
        return None
    _check_destatis_status(response_dict.get("Status", {}))

    return None


def _check_destatis_status(destatis_status: dict) -> None:
    """
    Helper method which checks the status message from Destatis.
    If the status message is erroneous an exception will be raised.

    Possible Codes (2.1.2 Grundstruktur der Responses):
    - 0: "erfolgreich" (Type: "Information")
    - 22: "erfolgreich mit Parameteranpassung" (Type: "Warnung")
    - 104: "Kein passendes Objekt zu Suche" (Type: "Information")

    Args:
        destatis_status (dict): Status response dict from Destatis

    Raises:
        Exception: Generic exception if the status code displays an error
    """
    # -1 is a status code that according to the documentation should not occur
    # and thus only is found if the status response dict is empty
    destatis_status_code = destatis_status.get("Code", -1)
    destatis_status_type = destatis_status.get("Type")
    destatis_status_content = destatis_status.get("Content")

    error_en_de = ["Error", "Fehler"]
    warning_en_de = ["Warning", "Warnung"]

    # check for generic/ system error
    if destatis_status_code == -1:
        raise Exception(
            "Error: There is a system error.\
                Please check your query parameters."
        )

    # check for destatis/ query errors
    elif (destatis_status_code == 104) or (destatis_status_type in error_en_de):
        raise Exception(destatis_status_content)

    # print warnings to user
    elif (destatis_status_code == 22) or (
        destatis_status_type in warning_en_de
    ):
        warnings.warn(destatis_status_content, UserWarning, stacklevel=2)

    return None
