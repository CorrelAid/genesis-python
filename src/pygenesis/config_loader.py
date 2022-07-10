"""Module loads the config (.env) file. (Placeholder for additional logic related to the config.)"""
from dotenv import dotenv_values, load_dotenv

if load_dotenv():
    CONFIG = dotenv_values()
