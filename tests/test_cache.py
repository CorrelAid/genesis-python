import logging
import re
import zipfile
from datetime import date
from pathlib import Path

import pytest

from pygenesis.cache import cache_data_from_response, clear_cache
from pygenesis.config import (
    DEFAULT_SETTINGS_FILE,
    _write_config,
    init_config,
    load_settings,
)

SLEEP_TIME = 0.1


@pytest.fixture()
def cache_dir(tmp_path_factory):
    # remove white-space and non-latin characters (issue fo some user names)
    temp_dir = str(tmp_path_factory.mktemp(".pygenesis"))
    temp_dir = re.sub(r"[^\x00-\x7f]", r"", temp_dir.replace(" ", ""))

    return Path(temp_dir)


@pytest.fixture(autouse=True)
def restore_settings():
    old_settings = load_settings()
    yield
    _write_config(old_settings, DEFAULT_SETTINGS_FILE)


@cache_data_from_response
def decorated_data(*, endpoint, method, params):
    return "test data"


def test_cache_data_wrapper(cache_dir):
    init_config(cache_dir)

    assert len(list((cache_dir / "data").glob("*"))) == 0

    data = decorated_data(
        endpoint="data", method="test", params={"name": "test_cache_decorator"}
    )

    assert isinstance(data, str)
    assert len(data) > 0

    cached_data_file: Path = (
        cache_dir
        / "data"
        / "test_cache_decorator"
        / (str(date.today()).replace("-", "") + "_" + "data_test.zip")
    )

    assert cached_data_file.exists() and cached_data_file.is_file()

    objs_in_data = [p for p in cache_dir.joinpath("data").glob("*") if p]

    assert len(objs_in_data) == 1
    assert objs_in_data[0] == cache_dir / "data" / "test_cache_decorator"

    objs_in_name_dir = [
        p
        for p in cache_dir.joinpath("data/test_cache_decorator").glob("*")
        if p
    ]

    assert len(objs_in_name_dir) == 1
    assert objs_in_name_dir[0] == cached_data_file

    with zipfile.ZipFile(cached_data_file, "r") as myzip:
        with myzip.open(cached_data_file.name.replace(".zip", ".txt")) as file:
            restored_data = file.read().decode()

    assert restored_data == data


def test_cache_data_twice(cache_dir, caplog):
    init_config(cache_dir)

    with caplog.at_level(logging.INFO):
        _ = decorated_data(
            endpoint="data",
            method="test",
            params={"name": "test_cache_decorator"},
        )

        assert "Data was successfully cached under" in caplog.text

    caplog.clear()

    with caplog.at_level(logging.INFO):
        _ = decorated_data(
            endpoint="data",
            method="test",
            params={"name": "test_cache_decorator"},
        )

        assert "Data was successfully cached under" not in caplog.text


def test_clean_cache(cache_dir):
    init_config(cache_dir)

    name = "test_clean_cache_cache_file"
    _ = decorated_data(endpoint="data", method="test", params={"name": name})

    cached_data_file: Path = next((cache_dir / "data" / name).glob("*.zip"))

    assert cached_data_file.exists() and cached_data_file.is_file()

    clear_cache(name=name)

    assert not cached_data_file.exists() and not cached_data_file.is_file()
