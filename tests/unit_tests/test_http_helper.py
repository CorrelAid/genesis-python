import pytest

from src.pygenesis.http_helper import (
    _check_destatis_status,
    _check_invalid_destatis_status_code,
    _check_invalid_status_code,
)

# TODO: Add generic dummy request to the server, which is not getting us timed out?


def test__check_invalid_status_code_with_error():
    """
    Basic tests to check an error status code (4xx, 5xx)
    for _handle_status_code method.
    """
    for status_code in [400, 500]:
        with pytest.raises(Exception) as e:
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


def _status_dict_helper(code: int = 0, type_: str = "Information") -> dict:
    """ """
    status_dict = {
        "Code": code,
        "Content": "erfolgreich",
        "Type": type_,
    }

    # TODO: add raw response
    """status_dict = {
        "Ident":{
            "Service":"find",
            "Method":"find"
        },
        "Status": {
            "Code": code,
            "Content": "erfolgreich",
            "Type": type_,
        },
    }"""

    return status_dict


# TODO: Is implementation of raw requests response type for actual
# _check_invalid_destatis_status_code test possible?
def test__check_invalid_destatis_status_code_with_error():
    """
    Basic tests to check an error status code as defined in the
    documentation via code (e.g. 104) or name ('Error', 'Fehler').
    """
    for status_dict in [
        _status_dict_helper(code=104),
        _status_dict_helper(type_="Error"),
        _status_dict_helper(type_="Fehler"),
    ]:
        status_content = status_dict.get("Content")

        with pytest.raises(Exception) as e:
            _check_destatis_status(status_dict)
        assert str(e.value) == status_content


def test__check_invalid_destatis_status_code_with_warning():
    """
    Basic tests to check a warning status code as defined in the
    documentation via code (e.g. 22) or name ('Warning', 'Warnung').
    """

    for status_dict in [
        _status_dict_helper(code=22),
        _status_dict_helper(type_="Warnung"),
        _status_dict_helper(type_="Warning"),
    ]:
        # TODO: Is the best/ most specific way to capture the warning?
        with pytest.warns(UserWarning):
            _check_destatis_status(status_dict)


def test__check_invalid_destatis_status_code_without_error():
    """
    Basic tests to check the successful status code 0 as defined in the documentation.
    """
    status_dict = _status_dict_helper()

    try:
        _check_destatis_status(status_dict)
    except Exception:
        assert False
