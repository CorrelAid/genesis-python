"""Module loads the config (.env) file. (Placeholder for additional logic related to the config.)"""
import os

from dotenv import dotenv_values

if os.path.isfile(".env"):
    CONFIG = dotenv_values()
