from configparser import ConfigParser

from mock import patch

from pygenesis.helloworld import logincheck, whoami
from tests.test_http_helper import _generic_request_status, mock_config_dict


@patch("requests.get")
@patch("pygenesis.helloworld.load_config")
def test_whoami(mock_config, mock_requests):
    mock_config.return_value = mock_config_dict()
    mock_requests.return_value = _generic_request_status()

    whoami()


@patch("requests.get")
@patch("pygenesis.helloworld.load_config")
def test_logincheck(mock_config, mock_requests):
    mock_config.return_value = mock_config_dict()
    mock_requests.return_value = _generic_request_status()

    logincheck()
