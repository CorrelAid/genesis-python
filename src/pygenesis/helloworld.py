"""Module provides wrapper for HelloWorld GENESIS REST-API functions."""

import requests

from pygenesis.config import load_config
from pygenesis.http_helper import _check_invalid_status_code

config = load_config()


# TODO: Write tests
def whoami() -> str:
    """
    Wrapper method which constructs an URL for testing the Destatis API
    whoami method, which returns host name and IP address.

    Returns:
        str: text test response from Destatis
    """
    url = f"{config['GENESIS API']['base_url']}" + "helloworld/whoami"

    response = requests.get(url)

    _check_invalid_status_code(response.status_code)

    return response.text


def logincheck():
    """
    Wrapper method which constructs an URL for testing the Destatis API
    logincheck method, which tests the login credentials (from the config.ini).

    Returns:
        str: text logincheck response from Destatis
    """
    url = f"{config['GENESIS API']['base_url']}" + "helloworld/logincheck"

    params = {
        "username": config["GENESIS API"]["username"],
        "password": config["GENESIS API"]["password"],
    }

    response = requests.get(url, params=params)

    # NOTE: Cannot use get_response_from_endpoint due to colliding
    # and misleading usage of "Status" key in response
    _check_invalid_status_code(response.status_code)

    return response.text
