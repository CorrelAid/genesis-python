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

1. Clone the repository via git.
2. Change into the project root directory.
3. Run `pip install . -e[dev]` to make an editable install that contains additional dependencies for development.
4. Do your changes.
5. Run `pytest` to see if all existing tests still run through.
6. Add new tests depending on your changes.
7. Run `pytest` again to make sure your tests are also passed.
8. Create a PR.
