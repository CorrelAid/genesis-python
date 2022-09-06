"""Wrapper module for the data endpoint."""
import json
import logging
import select
import sys
import time
import warnings

import requests

from pygenesis.cache import cache_data_from_response
from pygenesis.config import load_config
from pygenesis.custom_exceptions import DestatisStatusError

config = load_config()
logger = logging.getLogger(__name__)


@cache_data_from_response
def get_data_from_endpoint(*, endpoint: str, method: str, params: dict) -> str:
    """
    Wrapper method which constructs a url for querying data from Destatis and
    sends a GET request.

    Args:
        endpoint (str): Destatis endpoint (eg. data, catalogue, ..)
        method (str): Destatis method (eg. cube, tablefile, ...)
        params (dict): dictionary of query parameters

    Returns:
        str: the raw text response from Destatis.
    """
    config = load_config()
    url = f"{config['GENESIS API']['base_url']}{endpoint}/{method}"

    params.update(
        {
            "username": config["GENESIS API"]["username"],
            "password": config["GENESIS API"]["password"],
        }
    )

    response = requests.get(url, params=params, timeout=(1, 15))

    # if the response requires starting a job, automatically do so
    try:
        # test for job-relevant status code and catch possible error
        response_status_code = response.json().get("Status").get("Code")
        if response_status_code == 98:
            new_params = _jobs_params(params)
            if type(new_params) == dict:
                jobs_response = get_response_from_endpoint(
                    endpoint, method, new_params
                )
                response = _jobs_process(jobs_response, params)
    except json.decoder.JSONDecodeError:
        pass

    response.encoding = "UTF-8"

    _check_invalid_status_code(response.status_code)
    _check_invalid_destatis_status_code(response)

    return str(response.text)


# TODO: test (Marco)
def _generic_status_dict(
    status_code: int, status_content: str, status_type: str
) -> requests.Response:
    """
    Helper method which creates generic status dict.

    Args:
        status_code (int): Status code of the response
        status_content (str): Status content of the response
        status_type (str): Status type of the response (Information/ Warnung/ Fehler)

    Returns:
        requests.Response: the response from Destatis
    """
    # set up personalized requests.Reponse
    request_status = requests.Response()
    request_status.status_code = 42

    # define status warning and texts
    status_dict = {
        "Status": {
            "Code": status_code,
            "Content": status_content,
            "Type": status_type,
        },
    }

    request_status._content = json.dumps(status_dict).encode("utf-8")

    return request_status


# TODO: test schreiben (mit automatic y/n) - oder aber y/n entfernen
def _jobs_params(params: dict, timeperiod: float = 15) -> requests.Response:
    """
    Helper method which handles too large data requests with option of starting a job.

    Args:
        response_status_code (int): Status code from the response object with job
        params (dict): dictionary of query parameters
        endpoint (str): Destatis endpoint (eg. data, catalogue, ..)
        method (str): Destatis method (eg. cube, tablefile, ...)

    Returns:
        requests.Response: the response from Destatis
    """
    # matching cases for user inputs
    positive = ["ja", "j", "y", "yes"]
    negative = ["nein", "n", "no"]

    job_bool = [""]
    while job_bool[0].lower() not in positive + negative:
        # get user input whether to start a job
        logger.warning(
            "Die Daten sind zu groß um direkt abgerufen zu werden."
            + "Es muss ein Job gestartet werden, der einige Sekunden braucht,"
            + "um die Daten bereitzustellen und abzurufen."
            + "\n Sollen wir einen Job starten?"
            + "\n Ja/Nein:"
        )
        job_bool, o, e = select.select([sys.stdin], [], [], timeperiod)
        if not job_bool:
            logger.warning(
                "Keinen Input erhalten, es wird kein Job angestoßen."
            )
            job_bool = "Nein"

    if job_bool.lower() in negative:
        negative_response = _generic_status_dict(
            -1,
            "You aborted starting a job and therefore receive no data!",
            "Warnung",
        )

        return negative_response

    # retry request with job parameter set to True
    params |= {"job": "true"}
    return params


def _jobs_process(
    response: requests.Response, params: dict, timeperiod: float = 90
):

    # receive status from response
    job_true_response = response.json()
    assert (
        job_true_response.get("Status").get("Code") == 99
    ), "Unexpected status code when automatically starting a job!"
    s = job_true_response.get("Status").get("Content")
    job_id = s.split(":")[1].strip()
    logger.info("Der Job wurde angestoßen mit der ID: %s", job_id)

    # check job status via catalogue
    params |= {"sortcriterion": "time"}
    catalogue_state = None

    # set timeout of 90 seconds from now
    timeout = time.time() + timeperiod
    while time.time() < timeout:
        time.sleep(20)
        logger.info(
            "Der Endpunkt catalogue/jobs wurde mit der ID %s angesprochen. Der Status ist: %d",
            job_id,
            catalogue_state,
        )
        catalogue_response = get_response_from_endpoint(
            "catalogue", "jobs?", params
        )
        if catalogue_response.json().get("List")[-1].get("Code") == job_id:
            catalogue_state = (
                catalogue_response.json().get("List")[-1].get("State")
            )
            break
        else:
            # find the correct job in list
            pass

    # download the data if job finished successfully
    if catalogue_state in ["Fertig", "finished"]:
        params_resultfile = {
            "name": job_id,
            "area": "all",
            "language": "de",
        }
        result = get_response_from_endpoint(
            "data", "resultfile?", params_resultfile
        )

        return result

    else:
        failed_response = _generic_status_dict(
            -1,
            "The started job did not finish successfully!",
            "Fehler",
        )

        return failed_response

    # def


def _check_invalid_status_code(status_code: int) -> None:
    """
    Helper method which handles the status code from the response

    Args:
        status_code (int): Status code from the response object

    Raises:
        AssertionError: Assert that status is not 4xx or 5xx
    """
    if status_code // 100 in [4, 5]:
        raise requests.exceptions.HTTPError(
            f"Error {status_code}: The server returned a {status_code} status code"
        )


def _check_invalid_destatis_status_code(response: requests.Response) -> None:
    """
    Helper method which handles the status code returned from Destatis
    (if exists)

    Args:
        response (requests.Response): The response object from the request

    """
    try:
        response_dict = response.json()
    # catch possible errors raised by .json() (and only .json())
    except (
        UnicodeDecodeError,
        json.decoder.JSONDecodeError,
        requests.exceptions.JSONDecodeError,
    ):
        response_dict = None

    if response_dict is not None:
        _check_destatis_status(response_dict.get("Status", {}))


def _check_destatis_status(destatis_status: dict) -> None:
    """
    Helper method which checks the status message from Destatis.
    If the status message is erroneous an error will be raised.

    Possible Codes (2.1.2 Grundstruktur der Responses):
    # TODO: Ask Destatis for full list of error codes
    - 0: "erfolgreich" (Type: "Information")
    - 22: "erfolgreich mit Parameteranpassung" (Type: "Warnung")
    - 104: "Kein passendes Objekt zu Suche" (Type: "Information")

    Args:
        destatis_status (dict): Status response dict from Destatis

    Raises:
        DestatisStatusError: If the status code or type displays an error (caused by the user inputs)
    """
    # -1 status code for unexpected errors and if no status code is given (faulty response)
    destatis_status_code = destatis_status.get("Code", -1)
    destatis_status_type = destatis_status.get("Type", "Information")
    destatis_status_content = destatis_status.get("Content")

    # define status types
    error_en_de = ["Error", "Fehler"]
    warning_en_de = ["Warning", "Warnung"]

    # check for generic/ system error
    if destatis_status_code == -1:
        raise DestatisStatusError(
            "Error: There is a system error. Please check your query parameters."
        )

    # check for destatis/ query errors
    elif (destatis_status_code == 104) or (destatis_status_type in error_en_de):
        raise DestatisStatusError(destatis_status_content)

    # output warnings to user
    elif (destatis_status_code == 22) or (
        destatis_status_type in warning_en_de
    ):
        logger.warning(destatis_status_content)

    # output information to user
    elif destatis_status_type.lower() == "information":
        logger.info(
            "Code %d : %s", destatis_status_code, destatis_status_content
        )
