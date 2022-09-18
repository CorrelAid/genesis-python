import re
from configparser import ConfigParser
from pathlib import Path

import pytest
from mock import patch

from pygenesis.profile import password, remove_result
from tests.test_http_helper import _generic_request_status, mock_config_dict


@pytest.fixture()
def cache_dir(tmp_path_factory):
    # remove white-space and non-latin characters (issue fo some user names)
    temp_dir = str(tmp_path_factory.mktemp(".pygenesis"))
    temp_dir = re.sub(r"[^\x00-\x7f]", r"", temp_dir.replace(" ", ""))

    return Path(temp_dir)


@patch("pygenesis.profile.get_config_path_from_settings")
@patch("pygenesis.profile.get_data_from_endpoint")
@patch("pygenesis.profile.load_config")
def test_password(mock_config, mock_requests, mock_config_dir, cache_dir):
    mock_config.return_value = mock_config_dict()
    mock_requests.return_value = _generic_request_status()
    mock_config_dir.return_value = cache_dir

    password("new_password")


@patch("pygenesis.profile.get_config_path_from_settings")
@patch("pygenesis.profile.get_data_from_endpoint")
@patch("pygenesis.profile.load_config")
def test_password_keyerror(
    mock_config, mock_requests, mock_config_dir, cache_dir
):
    # define empty config (no password)
    config = ConfigParser()
    mock_config.return_value = config["GENESIS API"] = {}
    mock_requests.return_value = _generic_request_status()
    mock_config_dir.return_value = cache_dir

    with pytest.raises(KeyError) as e:
        password("new_password")
    assert (
        "Password not found in config! Please make sure \
            init_config() was run properly & your user data is set correctly!"
        in str(e.value)
    )


@patch("pygenesis.profile.get_data_from_endpoint")
def test_remove_result(mock_requests):
    mock_requests.return_value = _generic_request_status()

    remove_result("11111-0001")
