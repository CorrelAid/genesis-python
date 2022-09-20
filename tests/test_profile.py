import re
from configparser import ConfigParser
from pathlib import Path

import pytest
from mock import patch

from pygenesis.profile import change_password, remove_result
from tests.test_http_helper import _generic_request_status


@pytest.fixture()
def cache_dir(tmp_path_factory):
    # remove white-space and non-latin characters (issue fo some user names)
    temp_dir = str(tmp_path_factory.mktemp(".pygenesis"))
    temp_dir = re.sub(r"[^\x00-\x7f]", r"", temp_dir.replace(" ", ""))

    return Path(temp_dir)


@patch("pygenesis.profile.get_config_path_from_settings")
@patch("pygenesis.profile.get_data_from_endpoint")
@patch("pygenesis.profile.load_config")
def test_change_password(
    mock_config, mock_requests, mock_config_dir, cache_dir
):
    # mock configparser to be able to test writing of new password
    config = ConfigParser()
    config["GENESIS API"] = {
        "base_url": "mocked_url",
        "username": "JaneDoe",
        "password": "password",
    }
    mock_config.return_value = config
    mock_requests.return_value = _generic_request_status()
    mock_config_dir.return_value = cache_dir / "config.ini"

    change_password("new_password")


@patch("pygenesis.profile.get_config_path_from_settings")
@patch("pygenesis.profile.get_data_from_endpoint")
@patch("pygenesis.profile.load_config")
def test_change_password_keyerror(
    mock_config, mock_requests, mock_config_dir, cache_dir
):
    # define empty config (no password)
    mock_config.return_value = {"GENESIS API": {}}
    mock_requests.return_value = _generic_request_status()
    mock_config_dir.return_value = cache_dir

    with pytest.raises(KeyError) as e:
        change_password("new_password")
    assert (
        "Password not found in config! Please make sure \
            init_config() was run properly & your user data is set correctly!"
        in str(e.value)
    )


@patch("pygenesis.profile.get_data_from_endpoint")
def test_remove_result(mock_requests):
    mock_requests.return_value = _generic_request_status()

    remove_result("11111-0001")
