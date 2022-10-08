"""pystatis is a Python wrapper for the GENESIS web service interface (API).

Basic usage:

```python
import pystatis as pstat
print("Version:", pstat.__version__)
```
"""
from pystatis.cache import clear_cache
from pystatis.config import init_config
from pystatis.cube import Cube
from pystatis.find import Find
from pystatis.table import Table

__version__ = "0.1.0"

__all__ = ["clear_cache", "init_config", "Cube", "Table", "Find"]
