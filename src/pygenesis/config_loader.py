from dotenv import dotenv_values, load_dotenv

if load_dotenv():
    CONFIG = dotenv_values()
