"""Wrapper module for the data endpoint."""
import json
import logging
import time
from pathlib import Path
from typing import Union

import requests

from pygenesis.cache import cache_data, hit_in_cash, read_from_cache
from pygenesis.config import load_config
from pygenesis.custom_exceptions import DestatisStatusError

logger = logging.getLogger(__name__)


def load_data(
    endpoint: str, method: str, params: dict, as_json: bool = False
) -> Union[str, dict]:
    """Load data identified by endpoint, method and params.

    Either load data from cache (previous download) or from Destatis.

    Args:
        endpoint (str): The endpoint for this data request.
        method (str): The method for this data request.
        params (dict): The dictionary holding the params for this data request.
        as_json (bool, optional): If True, result will be parsed as JSON. Defaults to False.

    Returns:
        Union[str, dict]: The data as raw text or JSON dict.
    """
    config = load_config()
    cache_dir = Path(config["DATA"]["cache_dir"])
    name = params.get("name")

    if hit_in_cash(cache_dir, name, endpoint, method, params):
        data = read_from_cache(cache_dir, name, endpoint, method, params)
    else:
        data = get_data_from_endpoint(endpoint, method, params)

        if endpoint == "data":
            cache_data(cache_dir, name, endpoint, method, params, data)

    if as_json:
        parsed_data: dict = json.loads(data)
        return parsed_data
    else:
        return data


def get_data_from_endpoint(endpoint: str, method: str, params: dict) -> str:
    """
    Wrapper method which constructs an url for querying data from Destatis and
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

    # params is used to calculate hash for caching so don't alter params dict here!
    params_ = params.copy()
    params_.update(
        {
            "username": config["GENESIS API"]["username"],
            "password": config["GENESIS API"]["password"],
        }
    )

    response = requests.get(url, params=params_, timeout=(5, 15))

    # if the response requires starting a job, the user is prompted to decide
    try:
        # test for job-relevant status code
        response_status_code = response.json().get("Status").get("Code")

        if response_status_code == 98:
            # ask for user input
            new_params = _jobs_params(params)

            # start job if decided by user input
            if type(new_params) == dict:
                jobs_response = get_data_from_endpoint(
                    endpoint=endpoint, method=method, params=new_params
                )

                # return _jobs_process(jobs_response, new_params)

                jobs_catalogue_params, job_id = _jobs_job_id(
                    jobs_response, params
                )
                return _jobs_catalogue_process(jobs_catalogue_params, job_id)
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


def _jobs_params(params: dict) -> dict:
    """
    Helper method which handles too large data requests with option of starting a job.

    Args:
        params (dict): dictionary of query parameters

    Returns:
        dict: new dict to start a job
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

        job_bool = input("Sollen wir einen Job starten? \n Ja/Nein")

        if job_bool.lower() not in (positive + negative):
            logger.warning(
                "Keinen Input erhalten, es wird kein Job angestoßen."
            )
            job_bool = "nein"

    # retry request with job parameter set to True
    if job_bool.lower() in positive:
        params.update({"job": "true"})

    else:
        params = None

    # retry request with job parameter set to True
    # params.update({"job": "true"})
    return params


def _jobs_process(
    response: str, params: dict, timeperiod: float = 90
) -> requests.Response:
    """
    Helper method which handles overall job process.
    Args:
        response (str): Response text str
        params (dict): dictionary of query parameters with {"job": "true"}
        timeperiod (float): period until timeout
    Returns:
        requests.Response: the response from Destatis
    """
    # check status code of the response
    job_true_response = json.loads(response)
    assert (
        job_true_response.get("Status").get("Code") == 99
    ), "Unexpected status code when automatically starting a job!"

    # check out job_id & inform user
    s = job_true_response.get("Status").get("Content")
    job_id = s.split(":")[1].strip()
    logger.info("Der Job wurde angestoßen mit der ID: %s", job_id)

    # check job status via catalogue
    params.update({"sortcriterion": "time"})
    catalogue_state = None

    # set timeout of 90 seconds from now
    timeout = time.time() + timeperiod
    while (
        catalogue_state not in ["Fertig", "finished"] and time.time() < timeout
    ):
        # fetch current process status
        catalogue_response = get_data_from_endpoint(
            "catalogue", "jobs?", params
        )
        # convert response.text str to json
        catalogue_response = json.loads(catalogue_response)
        # assess that response relates to the current/ last (element [-1]) request
        if catalogue_response.get("List")[-1].get("Code") == job_id:
            catalogue_state = catalogue_response.get("List")[-1].get("State")
        else:
            pass

        # inform user
        logger.info(
            "Der Endpunkt catalogue/jobs wurde mit der ID %s angesprochen. Der Status ist: %s",
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
        result = load_data("data", "resultfile?", params_resultfile)

        return result

    else:
        failed_response = _generic_status_dict(
            -1,
            "The started job did not finish successfully!",
            "Fehler",
        )

        return failed_response


def _jobs_job_id(response: requests.Response, params: dict) -> dict:
    """
    Helper method which handles too large data requests and gives access to job id.

    Args:
        params (dict): dictionary of query parameters
        response (requests.Response): Response from endpoint request with job set equal true

    Returns:
        dict: new dict to observe status of job in catalogue
    """
    # check status code of the response
    job_true_response = json.loads(response)
    assert (
        job_true_response.get("Status").get("Code") == 99
    ), "Unexpected status code when automatically starting a job!"

    # check out job_id & inform user
    s = job_true_response.get("Status").get("Content")
    job_id = s.split(":")[1].strip()
    logger.info("Der Job wurde angestoßen mit der ID: %s", job_id)

    # new params to check job status via catalogue
    params.update({"sortcriterion": "time"})
    return params, job_id


def _jobs_catalogue_process(
    params: dict, job_id: str, timeperiod: float = 90
) -> json:
    """
    Helper method which checks the status of job in catalogue endpoint and returns final data.
    Data is automatically cached.

    Args:
        params (dict): dictionary of query parameters
        job_id (str): string of job_id for catalogue endpoint
        timeperiod (float): optional float for timeout

    Returns:
        json: json of requested data
    """
    # while loop timeout after 'timeperiod'
    timeout = time.time() + timeperiod
    catalogue_state = None

    while time.time() < timeout:
        time.sleep(5)
        # check job status
        catalogue_response = json.loads(
            get_data_from_endpoint(
                endpoint="catalogue", method="jobs", params=params
            )
        )
        if catalogue_response.get("List")[-1].get("Code") == job_id:
            catalogue_state = catalogue_response.get("List")[-1].get("State")

        logger.info(
            "Der Endpunkt catalogue/jobs wurde mit der ID %s angesprochen. Der Status ist: %s",
            job_id,
            catalogue_state,
        )

        # exit early if job has finished
        if catalogue_state in ["Fertig", "finished"]:
            break

        # wait to allow processing on the server side & try again if not finished
        time.sleep(15)

    # download the data if job finished successfully
    if catalogue_state in ["Fertig", "finished"]:
        params_resultfile = {
            "name": job_id,
            "area": "all",
            "language": "de",
        }
        result = load_data(
            endpoint="data", method="resultfile", params=params_resultfile
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
