"""Module provides functions/decorators to cache downloaded data as well as remove cached data."""
import hashlib
import json
import logging
import shutil
import zipfile
from datetime import date
from pathlib import Path
from typing import Optional

from pygenesis.config import load_config

logger = logging.getLogger(__name__)


def cache_data(
    cache_dir: Path,
    name: str,
    endpoint: str,
    method: str,
    params: dict,
    data: str,
) -> None:
    """Compress and archive data within the configured cache directory.

    Data will be stored in a zip file within the cache directory.
    The folder structure will be `<name>/<endpoint>/<method>/<hash(params)>.
    This allows to cache different results for different params.

    Args:
        cache_dir (Path): The cash directory as configured in the config.
        name (str): The unique identifier in GENESIS-Online.
        endpoint (str): The endpoint for this data request.
        method (str): The method for this data request.
        params (dict): The dictionary holding the params for this data request.
        data (str): The actual raw text data as returned by GENESIS-Online.
    """
    # pylint: disable=too-many-arguments
    data_dir = build_file_path(cache_dir, name, endpoint, method, params)
    file_name = f"{str(date.today()).replace('-', '')}.txt"

    # create parent dirs, if necessary
    file_path = data_dir / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # we have to first save the content to a text file, before we can add it to a
    #   compressed archive, and finally have to delete the file so only the archive remains
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(data)

    with zipfile.ZipFile(
        str(file_path).replace(".txt", ".zip"),
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as myzip:
        myzip.write(file_path, arcname=file_name)

    file_path.unlink()
    logger.info("Data was successfully cached under %s.", file_path)


def read_from_cache(
    cache_dir: Path, name: str, endpoint: str, method: str, params: dict
) -> str:
    """Read and return compressed data from cache.

    Args:
        cache_dir (Path): The cash directory as configured in the config.
        name (str): The unique identifier in GENESIS-Online.
        endpoint (str): The endpoint for this data request.
        method (str): The method for this data request.
        params (dict): The dictionary holding the params for this data re

    Returns:
        str: The uncompressed raw text data.
    """
    data_dir = build_file_path(cache_dir, name, endpoint, method, params)

    versions = sorted(
        data_dir.glob("*"),
        key=lambda path: int(path.stem),
    )
    file_name = versions[-1].name
    file_path = data_dir / file_name
    with zipfile.ZipFile(file_path, "r") as myzip:
        with myzip.open(file_name.replace(".zip", ".txt")) as file:
            data = file.read().decode()

    return data


def build_file_path(
    cache_dir: Path, name: str, endpoint: str, method: str, params: dict
) -> Path:
    params_hash = hashlib.md5(json.dumps(params).encode("UTF-8")).hexdigest()
    data_dir = cache_dir / name / endpoint / method / params_hash
    return data_dir


def hit_in_cash(
    cache_dir: Path, name: str, endpoint: str, method: str, params: dict
) -> bool:
    data_dir = build_file_path(cache_dir, name, endpoint, method, params)
    return data_dir.exists()


def clear_cache(name: Optional[str] = None) -> None:
    """Clean the data cache completely or just a specified name.

    Args:
        name (str, optional): Unique name to be deleted from cached data.
    """
    config = load_config()
    cache_dir = Path(config["DATA"]["cache_dir"])

    # remove specified file (directory) from the data cache
    # or clear complete cache (remove childs, preserve base)
    file_paths = [cache_dir / name] if name is not None else cache_dir.iterdir()

    for file_path in file_paths:
        # delete if file or symlink, otherwise remove complete tree
        try:
            if file_path.is_file() or file_path.is_symlink():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
        except (OSError, ValueError, FileNotFoundError) as e:
            logger.warning("Failed to delete %s. Reason: %s", file_path, e)

        logger.info("Removed files: %s", file_paths)
