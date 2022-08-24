import json

import pytest
import requests

from src.pygenesis.http_helper import (
    _check_invalid_destatis_status_code,
    _check_invalid_status_code,
)

# TODO: Add generic dummy request to the server, which is not getting us timed out,
# to test get_response_from_endpoint completely?


def test__check_invalid_status_code_with_error():
    """
    Basic tests to check an error status code (4xx, 5xx)
    for _handle_status_code method.
    """
    for status_code in [400, 500]:
        with pytest.raises(AssertionError) as e:
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


def _generic_request_status(
    status_response: bool = True,
    code: int = 0,
    status_type: str = "Information",
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
            "Content": "Erfolg/ Success/ Some Issue",
            "Type": status_type,
        },
    }

    response_text = "Some text for a successful response without status..."

    # set up generic requests.Reponse
    request_status = requests.Response()
    request_status.status_code = 200  # success

    # TODO: Why is specific (UTF-8) encoding necessary?
    if status_response:

        request_status._content = json.dumps(status_dict).encode("utf-8")
    else:
        request_status._content = response_text.encode("utf-8")

    return request_status


def test__check_invalid_destatis_status_code_with_error():
    """
    Basic tests to check an error status code as defined in the
    documentation via code (e.g. 104) or type ('Error', 'Fehler').
    """
    for status in [
        _generic_request_status(code=104),
        _generic_request_status(status_type="Error"),
        _generic_request_status(status_type="Fehler"),
    ]:
        # extract status content which is raised
        status_content = status.json().get("Status").get("Content")

        with pytest.raises(ValueError) as e:
            _check_invalid_destatis_status_code(status)
        assert str(e.value) == status_content


def test__check_invalid_destatis_status_code_with_warning():
    """
    Basic tests to check a warning status code as defined in the
    documentation via code (e.g. 22) or type ('Warning', 'Warnung').
    """

    for status in [
        _generic_request_status(code=22),
        _generic_request_status(status_type="Warnung"),
        _generic_request_status(status_type="Warning"),
    ]:
        # TODO: Is the best/ most specific way to capture the warning?
        with pytest.warns(UserWarning):
            _check_invalid_destatis_status_code(status)


def test__check_invalid_destatis_status_code_without_error():
    """
    Basic tests to check the successful status code 0 or only text response as defined in the documentation.
    """
    for status in [
        _generic_request_status(),
        _generic_request_status(status_response=False),
    ]:
        try:
            _check_invalid_destatis_status_code(status)
        except Exception:
            assert False
