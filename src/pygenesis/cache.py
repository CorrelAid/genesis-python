"""Module provides functions/decorators to cache downloaded data as well as remove cached data."""
import logging
import shutil
import zipfile
from datetime import date
from functools import wraps
from pathlib import Path
from typing import Callable, Optional

from pygenesis.config import load_config

logger = logging.getLogger(__name__)


def cache_data_from_response(func: Callable[..., str]) -> Callable[..., str]:
    """Store downloaded data on disk with download time as parent folder.

    Args:
        func (Callable): One of the data methods of the data endpoint.
    """

    @wraps(func)
    def wrapper_func(**kwargs) -> str:
        endpoint = kwargs.get("endpoint")
        method = kwargs.get("method")
        genesis_id = kwargs.get("params", {}).get("name")

        if endpoint is None or method is None or endpoint != "data":
            return func(**kwargs)

        config = load_config()
        cache_dir = Path(config["DATA"]["cache_dir"])

        if not cache_dir.is_dir() or not cache_dir.exists():
            logger.critical(
                "Cache dir does not exist! Please make sure init_config() was run properly. Path: %s",
                cache_dir,
            )

        data_dir = cache_dir / genesis_id
        if data_dir.exists():
            # TODO: Implement solution for updated data.
            #   So don't return latest version but check first for newer version in GENESIS.
            # if data_dir exists, there has to be at least one stored version of this data
            versions = sorted(
                (p.name for p in data_dir.glob("*")),
                key=lambda name: int(name.split("_")[0]),
            )
            file_name = versions[-1]
            file_path = data_dir / file_name
            with zipfile.ZipFile(file_path, "r") as myzip:
                with myzip.open(file_name.replace(".zip", ".txt")) as file:
                    data = file.read().decode()
        else:
            data = func(**kwargs)
            file_name = (
                f"{str(date.today()).replace('-', '')}_{endpoint}_{method}.txt"
            )
            file_path = data_dir / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
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

        return data

    return wrapper_func


def clear_cache(name: Optional[str] = None) -> None:
    """Clean the data cache completely or just a specified name.

    Args:
        name (str, optional): Unique name to be deleted from cached data.
    """
    config = load_config()

    # check for cache_dir in DATA section of the config.ini
    try:
        cache_dir = Path(config["DATA"]["cache_dir"])
    except KeyError as e:
        logger.critical(
            "Cache dir does not exist! Please make sure init_config() was run properly. Error: %s",
            e,
        )

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
