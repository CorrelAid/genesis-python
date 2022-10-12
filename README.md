# pystatis

pystatis is a Python wrapper for the GENESIS web service interface (API).

> The GENESIS-Online database of the Federal Statistical Office contains a wide range of tables which you can configure according to your needs. As a matter of fact, GENESIS-Online can be used free of charge and without registering under the "Data Licence Germany - Namensnennung - Version 2.0".

See the official documentation [here](https://www.destatis.de/EN/Service/OpenData/api-webservice.html).

## Installation

You can install the package via

```bash
$ pip install pystatis
```

If everything worked out correctly, you should be able to import pystatis like this

```python
import pystatis as pystat

print("Version:", pystat.__version__)
```

## Setup for first use

To be able to use the web service/API of GENESIS-Online, you have to be a registered user. You can create your user [here](https://www-genesis.destatis.de/genesis/online?Menu=Anmeldung).

Once you have a registered user, you can use your username and password as credentials for authentication against the GENESIS-Online API.

To avoid entering your credentials each time you use `pystatis`, your credentials will be stored locally with the `init_config()` helper function. This function accepts both a `username` and `password` argument and stores your credentials in a configuration file named `config.ini` that is stored under `<user home>/.pystatis/config.ini` by default. You can change this path with the optional `config_dir` argument.

So before you can use `pystatis` you have to execute the following code **once**:

```python
from pystatis import init_config

init_config(username="myusername", password="mypassword")
```

After executing this code you should have a new `config.ini` file under the `<user home>/.pystatis` directory.

Each time `pystatis` is communicating with GENESIS-Online via the API, it is automatically using the stored credentials in this `config.ini`, so you don't have to specify them again. In case of updated credentials, you can either run `init_config()` again or update the values directly in the `config.ini` file.

GENESIS-Online provides a `helloworld` endpoint that can be used to check your credentials:
```python
from pystatis import logincheck

logincheck()
>>> '{"Status":"Sie wurden erfolgreich an- und abgemeldet!","Username":"ASFJ582LJ"}'
```

If you can see a response like this, your setup is complete and you can start downloading data.


## Developer information

To contribute to this project, please follow these steps:

1. Install [poetry](https://python-poetry.org/docs/). We recommend installing `poetry` via [pipx](https://pypa.github.io/pipx/) which gives you a global `poetry` command in an isolated virtual environment.
2. Clone the repository via git.
3. Change into the project root directory.
4. Run `poetry install` to create the virtual environment within `poetry`'s cache folder (run `poetry env info` to see the details of this new virtual environment). `poetry` has installed all dependencies for you, as well as the package itself.
5. Install pre-commit: `poetry run pre-commit install`. This will activate the pre-commit hooks that will run prior every commit to ensure code quality.
6. Do your changes.
7. Run `poetry run pytest` to see if all existing tests still run through. It is important to use `poetry run` to call `pytest` so that `poetry` uses the created virtual environment and not the system's default Python interpreter. Alternatively, you can run `poetry shell` to let `poetry` activate the virtual environment for the current session. Afterwards, you can run `pytest` as usual without any prefix. You can leave the poetry shell with the `exit` command.
8. Add new tests depending on your changes.
9. Run `poetry run pytest` again to make sure your tests are also passed.
10. Commit and push your changes.
11. Create a PR.

To learn more about `poetry`, see [Dependency Management With Python Poetry](https://realpython.com/dependency-management-python-poetry/#command-reference) by realpython.com.
