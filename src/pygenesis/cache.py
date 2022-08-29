"""Module provides functions/decorators to cache downloaded data."""
import logging
from datetime import date
from functools import wraps
from pathlib import Path
from typing import Callable

import pandas as pd

from pygenesis.config import load_config

logger = logging.getLogger(__name__)


def cache_data(func: Callable) -> Callable:
    """Store downloaded data on disk with download time as parent folder.

    Args:
        func (Callable): One of the data methods of the data endpoint.
    """

    @wraps(func)
    def wrapper_func(**kwargs):
        config = load_config()
        cache_dir = Path(config["DATA"]["cache_dir"])

        if not cache_dir.is_dir() or not cache_dir.exists():
            logger.critical(
                "Cache dir does not exist! Please make sure init_config() was run properly. Path: %s",
                cache_dir,
            )

        name = kwargs["name"]
        data_dir = cache_dir / name
        if data_dir.exists():
            # TODO: Implement solution for updated data.
            #   So don't return latest version but check first for newer version in GENESIS.
            # if data_dir exists, there has to be at least one stored version of this data
            versions = sorted((p.name for p in data_dir.glob("*")), key=int)
            latest = versions[-1]
            data = pd.read_csv(data_dir / latest / f"{name}.xz")
        else:
            data: pd.DateFrame = func(**kwargs)
            file_path = (
                data_dir / str(date.today()).replace("-", "") / f"{name}.xz"
            )
            file_path.parent.mkdir(parents=True, exist_ok=True)
            data.to_csv(file_path, index=False)

        return data

    return wrapper_func
