"""pygenesis is a Python wrapper for the GENESIS web service interface (API).

Basic usage:

```python
import pygenesis as pgen
print("Version:", pgen.__version__)
```
"""
from pygenesis.cache import clear_cache
from pygenesis.config import init_config
from pygenesis.cube import Cube
from pygenesis.table import Table

__version__ = "0.1.0"
