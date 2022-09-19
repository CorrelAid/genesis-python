"""Wrapper module for the data endpoint."""
import json
import logging
import select
import sys
import time
import warnings
from typing import Optional

import requests

from pygenesis.config import load_config

config = load_config()
logger = logging.getLogger(__name__)


def get_response_from_endpoint(
    endpoint: str, method: str, params: dict
) -> requests.Response:
    """
    Wrapper method which constructs a url for querying data from Destatis and
    sends a GET request.

    Args:
        endpoint (str): Destatis endpoint (eg. data, catalogue, ..)
        method (str): Destatis method (eg. cube, tablefile, ...)
        params (dict): dictionary of query parameters

    Returns:
        requests.Response: the response from Destatis
    """
    url = f"{config['GENESIS API']['base_url']}{endpoint}/{method}"

    params |= {
        "username": config["GENESIS API"]["username"],
        "password": config["GENESIS API"]["password"],
    }

    response = requests.get(url, params=params)

    # if the response requires starting a job, automatically do so
    try:
        # test for job-relevant status code
        response_status_code = response.json().get("Status").get("Code", -1)

        if response_status_code == 98:
            new_params = _jobs_params(params)

            # start job if decided by user input
            if type(new_params) == dict:
                jobs_response = get_response_from_endpoint(
                    endpoint, method, new_params
                )
                response = _jobs_process(jobs_response, new_params)

    # catch if a non-json response (e.g. successful file download) is received
    except json.decoder.JSONDecodeError:
        pass

    response.encoding = "UTF-8"
    _check_invalid_status_code(response.status_code)
    _check_invalid_destatis_status_code(response)

    return response


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
def _jobs_params(params: dict) -> Optional[dict]:
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

    # define initial input for select
    job_bool = ""

    while job_bool.lower() not in positive + negative:
        # get user input whether to start a job
        logger.warning(
            "Die Daten sind zu groß um direkt abgerufen zu werden."
            + "Es muss ein Job gestartet werden, der einige Sekunden braucht,"
            + "um die Daten bereitzustellen und abzurufen."
            + "\n Sollen wir einen Job starten?"
            + "\n Ja/Nein:"
        )

        # TODO: Not working for Windows!
        job_bool = input()

        if not job_bool:
            logger.warning(
                "Keinen Input erhalten, es wird kein Job angestoßen."
            )
            job_bool = "nein"

    # retry request with job parameter set to True
    if job_bool.lower() in positive:
        params |= {"job": "true"}

    else:
        params = None

    return params


def _jobs_process(
    response: requests.Response, params: dict, timeperiod: float = 90
) -> requests.Response:
    """
    Helper method which handles overall job process.

    Args:
        response (requests.Response): Response object with {"job": "true"}
        params (dict): dictionary of query parameters
        timeperiod (float): period until timeout

    Returns:
        requests.Response: the response from Destatis
    """
    # check status code of the response
    job_true_response = response.json()
    assert (
        job_true_response.get("Status").get("Code") == 99
    ), "Unexpected status code when automatically starting a job!"

    # check out job_id & inform user
    s = job_true_response.get("Status").get("Content")
    job_id = s.split(":")[1].strip()
    logger.info("Der Job wurde angestoßen mit der ID: %s", job_id)

    # check job status via catalogue
    params |= {"sortcriterion": "time"}
    catalogue_state = None

    # set timeout of 90 seconds from now
    timeout = time.time() + timeperiod
    while (
        catalogue_state not in ["Fertig", "finished"] and time.time() < timeout
    ):
        # fetch current process status
        catalogue_response = get_response_from_endpoint(
            "catalogue", "jobs?", params
        )
        # assess that response relates to the current/ last (element [-1]) request
        if catalogue_response.json().get("List")[-1].get("Code") == job_id:
            catalogue_state = (
                catalogue_response.json().get("List")[-1].get("State")
            )
        else:
            pass

        # inform user
        logger.info(
            "Der Endpunkt catalogue/jobs wurde mit der ID %s angesprochen. Der Status ist: %d",
            job_id,
            catalogue_state,
        )

        # wait to allow processing on the server side & try again if not finished
        time.sleep(20)

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


def _check_invalid_status_code(status_code: int) -> None:
    """
    Helper method which handles the status code from the response

    Args:
        status_code (int): Status code from the response object

    Raises:
        AssertionError: Assert that status is not 4xx or 5xx
    """
    assert status_code // 100 not in [
        4,
        5,
    ], f"Error {status_code}: The server returned a {status_code} status code"


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
    - 0: "erfolgreich" (Type: "Information")
    - 22: "erfolgreich mit Parameteranpassung" (Type: "Warnung")
    - 104: "Kein passendes Objekt zu Suche" (Type: "Information")

    Args:
        destatis_status (dict): Status response dict from Destatis

    Raises:
        # TODO: Is this a Value or KeyError?
        ValueError: If the status code or type displays an error (caused by the user inputs)
    """
    # -1 status code for unexpected errors and if no status code is given (faulty response)
    destatis_status_code = destatis_status.get("Code", -1)
    destatis_status_type = destatis_status.get("Type")
    destatis_status_content = destatis_status.get("Content")

    error_en_de = ["Error", "Fehler"]
    warning_en_de = ["Warning", "Warnung"]

    # check for generic/ system error
    if destatis_status_code == -1:
        raise ValueError(
            "Error: There is a system error.\
                Please check your query parameters."
        )

    # check for destatis/ query errors
    elif (destatis_status_code == 104) or (destatis_status_type in error_en_de):
        raise ValueError(destatis_status_content)

    # print warnings to user
    elif (destatis_status_code == 22) or (
        destatis_status_type in warning_en_de
    ):
        warnings.warn(destatis_status_content, UserWarning, stacklevel=2)

    # TODO: pass response information to user, see feature branch 45
