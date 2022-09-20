import json
import logging
import re
from pathlib import Path

import pytest
import requests
from mock import patch

from pygenesis.custom_exceptions import DestatisStatusError
from pygenesis.http_helper import (
    _check_invalid_destatis_status_code,
    _check_invalid_status_code,
    _jobs_catalogue_process,
    _jobs_job_id,
    get_data_from_endpoint,
)


def _generic_request_status(
    status_response: bool = True,
    code: int = 0,
    status_type: str = "Information",
    status_content: str = "Erfolg/ Success/ Some Issue",
) -> requests.Response:
    """
    Helper method which allows to create a generic request.Response that covers all Destatis answers

    Args:
        status_response (bool): Whether Destatis answer contains a status response
        code (str): Status response code
        status_type (str): Status reponse type/ name

    Returns:
        requests.Response: the response from Destatis
    """
    # define possible status dict and texts
    status_dict = {
        "Ident": {
            "Service": "A DESTATIS service",
            "Method": "A DESTATIS method",
        },
        "Status": {
            "Code": code,
            "Content": status_content,
            "Type": status_type,
        },
    }

    response_text = "Some text for a successful response without status..."

    # set up generic requests.Response
    request_status = requests.Response()
    request_status.status_code = 200  # success

    # Define UTF-8 encoding as requests guesses otherwise
    if status_response:
        request_status._content = json.dumps(status_dict).encode("UTF-8")
    else:
        request_status._content = response_text.encode("UTF-8")

    return request_status


@patch("requests.get")
@patch("pygenesis.http_helper.load_config")
def test_get_response_from_endpoint(mock_config, mock_requests):
    """
    Test once with generic API response, more detailed tests
    of subfunctions and specific cases below.
    """
    mock_config.return_value = {
        "GENESIS API": {
            "base_url": "mocked_url",
            "username": "JaneDoe",
            "password": "password",
        }
    }
    mock_requests.return_value = _generic_request_status()

    get_data_from_endpoint(endpoint="endpoint", method="method", params={})


def test__check_invalid_status_code_with_error():
    """
    Basic tests to check an error status code (4xx, 5xx)
    for _handle_status_code method.
    """
    for status_code in [400, 500]:
        with pytest.raises(requests.exceptions.HTTPError) as e:
            _check_invalid_status_code(status_code)
        assert (
            str(e.value)
            == f"Error {status_code}: The server returned a {status_code} status code"
        )


def test__check_invalid_status_code_without_error():
    """
    Basic test to check a valid status code (2xx)
    for the _handle_status_code method.
    """
    status_code = 200
    try:
        _check_invalid_status_code(status_code)
    except Exception:
        assert False


def test__check_invalid_destatis_status_code_with_error():
    """
    Basic tests to check an error status code as defined in the
    documentation via code (e.g. -1, 104) or type ('Error', 'Fehler').
    """
    for status in [
        _generic_request_status(code=104),
        _generic_request_status(status_type="Error"),
        _generic_request_status(status_type="Fehler"),
    ]:
        # extract status content which is raised
        status_content = status.json().get("Status").get("Content")

        with pytest.raises(DestatisStatusError) as e:
            _check_invalid_destatis_status_code(status)
        assert str(e.value) == status_content

    # also test generic -1 error code
    generic_error_status = _generic_request_status(code=-1)

    with pytest.raises(DestatisStatusError) as e:
        _check_invalid_destatis_status_code(generic_error_status)
    assert (
        str(e.value)
        == "Error: There is a system error. Please check your query parameters."
    )


def test__check_invalid_destatis_status_code_with_warning(caplog):
    """
    Basic tests to check a warning status code as defined in the
    documentation via code (e.g. 22) or type ('Warning', 'Warnung').
    """
    caplog.set_level(logging.WARNING)

    for status in [
        _generic_request_status(code=22),
        _generic_request_status(status_type="Warnung"),
        _generic_request_status(status_type="Warning"),
    ]:
        # extract status content which is contained in warning
        status_content = status.json().get("Status").get("Content")

        _check_invalid_destatis_status_code(status)

        assert status_content in caplog.text


def test__check_invalid_destatis_status_code_without_error(caplog):
    """
    Basic tests to check the successful status code 0 or only text response as defined in the documentation.
    """
    # JSON response with status code
    caplog.set_level(logging.INFO)
    status = _generic_request_status()
    status_content = status.json().get("Status").get("Content")
    _check_invalid_destatis_status_code(status)

    assert status_content in caplog.text

    # text only response
    status_text = _generic_request_status(status_response=False)
    try:
        _check_invalid_destatis_status_code(status_text)
    except Exception:
        assert False


def test__jobs_job_id_successful():
    """
    Testing successfully returning the updated params dict and the correct job_id
    """
    status_content = (
        "Der Bearbeitungsauftrag wurde erstellt. "
        "Die Tabelle kann in Kürze als Ergebnis mit folgendem Namen abgerufen werden: 42151-0001_976196443"
    )
    response = json.loads(
        str(
            _generic_request_status(
                True, 99, "Information", status_content
            ).text
        )
    )
    params = {}
    new_params, job_id = _jobs_job_id(response, params)
    assert new_params.get("selection") == f"*42151-0001_976196443*"
    assert job_id == f"42151-0001_976196443"


def test__jobs_job_id_no_status_content():
    """
    Testing no status_content
    """
    status_content = None
    response = json.loads(
        str(
            _generic_request_status(
                True, 99, "Information", status_content
            ).text
        )
    )
    params = {}
    try:
        _jobs_job_id(response, params)
    except AttributeError:
        # failed successfully
        pass


def test__jobs_job_id_wrong_status_code():
    """
    Testing no status_content
    """
    status_content = (
        "Der Bearbeitungsauftrag wurde erstellt. "
        "Die Tabelle kann in Kürze als Ergebnis mit folgendem Namen abgerufen werden: 42151-0001_976196443"
    )
    response = json.loads(
        str(
            _generic_request_status(
                True, 98, "Information", status_content
            ).text
        )
    )
    params = {}
    try:
        _jobs_job_id(response, params)
    except AssertionError:
        # failed successfully
        pass
