"""Module loads the config (.env) file. (Placeholder for additional logic related to the config.)"""
from pathlib import Path

from dotenv import dotenv_values

if Path(".env").exists():
    CONFIG = dotenv_values()
