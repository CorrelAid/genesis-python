# pygenesis

pygenesis is a Python wrapper for the GENESIS web service interface (API).

> The GENESIS-Online database of the Federal Statistical Office contains a wide range of tables which you can configure according to your needs. As a matter of fact, GENESIS-Online can be used free of charge and without registering under the "Data Licence Germany - Namensnennung - Version 2.0".

See the official documentation [here](https://www.destatis.de/EN/Service/OpenData/api-webservice.html).

## Setup

You can install the package via

```bash
$ pip install pygenesis
```

If everything worked out correctly, you should be able to import pygenesis like this

```python
import pygenesis as pgen

print("Version:", pgen.__version__)
```

## Developer information

To contribute to this project, please follow these steps:

1. Install [poetry](https://python-poetry.org/docs/). We recommend installing `poetry` via `pipx` which gives you a global `poetry` command in an isolated virtual environment.
2. Clone the repository via git.
3. Change into the project root directory.
4. Run `poetry install` to create the virtual environment within `poetry`'s cache folder (run `poetry env info` to see the details of this new virtual environment). `poetry` has installed all dependencies for you, as well as the package itself.
5. Do your changes.
6. Run `poetry run pytest` to see if all existing tests still run through. It is important to use `poetry run` to call `pytest` so that `poetry` uses the created virtual environment and not the system's default Python interpreter. Alternatively, you can run `poetry shell` to let `poetry` activate the virtual environment for the current session. Afterwards, you can run `pytest` as usual without any prefix. You can leave the poetry shell with the `exit` command.
7. Add new tests depending on your changes.
8. Run `poetry run pytest` again to make sure your tests are also passed.
9.  Create a PR.

To learn more about `poetry`, see [Dependency Management With Python Poetry](https://realpython.com/dependency-management-python-poetry/#command-reference) by realpython.com.
