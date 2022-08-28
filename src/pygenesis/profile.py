"""Module provides wrapper for Profile GENESIS REST-API functions."""

from pygenesis.config import (
    _write_config,
    get_config_path_from_settings,
    load_config,
)
from pygenesis.http_helper import get_response_from_endpoint


# TODO: write tests
def password(new_password: str):
    """
    Changes Genesis REST-API password and updates local config.

    Args:
        new_password (str): New password for the Genesis REST-API

    Returns:
        str: text response from Destatis
    """
    params = {
        "new": new_password,
        "repeat": new_password,
    }

    # load config.ini beforehand, to ensure passwords are changed at the same time
    config = load_config()
    try:
        config["GENESIS API"]["password"]
    except KeyError as e:
        raise KeyError(
            e,
            "Password not found in config! Please make sure \
            init_config() was run properly & your user data is set correctly!",
        )

    # change remote password
    response = get_response_from_endpoint("profile", "password", params)
    # change local password
    config["GENESIS API"]["password"] = new_password
    _write_config(config, get_config_path_from_settings())

    return response.text


def remove_result():
    pass
