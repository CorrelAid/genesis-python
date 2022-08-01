import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from pygenesis.cache import cache_data
from pygenesis.config import (
    DEFAULT_SETTINGS_FILE,
    _write_config,
    init_config,
    load_settings,
)

SLEEP_TIME = 0.1


@pytest.fixture()
def cache_dir(tmp_path_factory):
    return tmp_path_factory.mktemp(".pygenesis")


@pytest.fixture(autouse=True)
def restore_settings():
    old_settings = load_settings()
    yield
    _write_config(old_settings, DEFAULT_SETTINGS_FILE)


@cache_data
def decorated_data(*, name):
    time.sleep(SLEEP_TIME)
    return pd.DataFrame(
        np.random.random(size=(10, 5)), columns=["a", "b", "c", "d", "e"]
    )


def test_cache_data_wrapper(cache_dir):
    init_config(cache_dir)

    assert len(list((cache_dir / "data").glob("*"))) == 0

    data = decorated_data(name="test_cache_decorator")

    assert isinstance(data, pd.DataFrame)
    assert not data.empty

    cached_data_file: Path = (
        cache_dir
        / "data"
        / "test_cache_decorator"
        / str(date.today()).replace("-", "")
        / "test_cache_decorator.xz"
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
    assert objs_in_name_dir[0] == cached_data_file.parent

    restored_data = pd.read_csv(cached_data_file)

    pd.testing.assert_frame_equal(data, restored_data, check_index_type=False)


def test_cache_data_twice(cache_dir):
    init_config(cache_dir)

    load_time = time.perf_counter()
    data = decorated_data(name="test_cache_decorator")
    load_time = time.perf_counter() - load_time

    assert load_time >= SLEEP_TIME

    load_time = time.perf_counter()
    data = decorated_data(name="test_cache_decorator")
    load_time = time.perf_counter() - load_time

    assert load_time < SLEEP_TIME
