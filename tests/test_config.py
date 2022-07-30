import logging
from configparser import ConfigParser
from pathlib import Path

import pytest

from pygenesis.config import (
    DEFAULT_SETTINGS_FILE,
    _write_config,
    get_config_path_from_settings,
    init_config,
    load_config,
    load_settings,
)


@pytest.fixture()
def config_dir(tmp_path_factory):
    config_dir = tmp_path_factory.mktemp(".pygenesis")
    return config_dir


@pytest.fixture(autouse=True)
def restore_settings():
    old_settings = load_settings()
    yield
    _write_config(old_settings, DEFAULT_SETTINGS_FILE)


def test_settings():
    assert DEFAULT_SETTINGS_FILE.exists() and DEFAULT_SETTINGS_FILE.is_file()


def test_load_settings():
    settings = load_settings()

    assert isinstance(settings, ConfigParser)
    assert settings.has_option("SETTINGS", "config_dir")


def test_get_config_path_from_settings():
    config_path = get_config_path_from_settings()

    assert isinstance(config_path, Path)


def test_init_config_with_config_dir(config_dir, caplog):
    caplog.clear()
    caplog.set_level(logging.INFO)

    init_config(config_dir)

    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[1].levelname == "INFO"
    assert "Settings file updated" in caplog.text
    assert "New config was created" in caplog.text

    config = load_config()

    assert isinstance(config, ConfigParser)
    assert len(config.sections()) > 0
    config_file = get_config_path_from_settings()
    assert config_file.exists() and config_file.is_file()


def test_load_config(config_dir):
    init_config(config_dir)
    config: ConfigParser = load_config()

    for section in ["GENESIS API", "DATA"]:
        assert config.has_section(section)

    assert config.options("GENESIS API") == [
        "base_url",
        "username",
        "password",
        "doku",
    ]
    assert config.options("DATA") == ["cache_dir"]


def test_missing_username(config_dir, caplog):
    init_config(config_dir)

    caplog.clear()

    _ = load_config()

    assert caplog.records[0].levelname == "CRITICAL"
    assert "Username and/or password are missing!" in caplog.text


def test_missing_file(config_dir, caplog):
    init_config(config_dir)
    (config_dir / "config.ini").unlink()

    caplog.clear()

    config = load_config()
    assert not config.sections()

    for record in caplog.records:
        assert record.levelname == "CRITICAL"
