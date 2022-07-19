import pytest

from src.pygenesis.http_helper import _handle_status_code


def test__handle_status_code_with_error():
    """
    Basic tests to check an error status code (4xx, 5xx)
    for _handle_status_code method.
    """
    status_code = 400
    with pytest.raises(Exception) as e:
        _handle_status_code(status_code)
    assert (
        str(e.value)
        == f"Error {status_code}: The server returned a {status_code} status code"
    )


def test__handle_status_code_without_error():
    """
    Basic test to check a valid status code (2xx)
    for the _handle_status_code method.
    """
    status_code = 200
    try:
        _handle_status_code(status_code)
    except Exception:
        assert False
