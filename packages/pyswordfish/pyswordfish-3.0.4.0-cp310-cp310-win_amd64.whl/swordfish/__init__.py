from ._core import ModuleResources
from ._runtime import _init_without_args, exec, call, variable, sql
from ._config import config
from .infos import info
from . import types, data, function, io, tools, module
from .data import partial, scalar, vector, any_vector, array_vector, pair
from .data import matrix, set, dictionary, table
from .data import NULL, DFLT, Nothing

from .connection import meta_code, empty_context
from ._swordfishcpp import (  # type: ignore
    Warning,
    Error,
    InterfaceError,
    DatabaseError,
    DataError,
    OperationalError,
    IntegrityError,
    InternalError,
    ProgrammingError,
    NotSupportedError,
)
from ._sqlbuilder import msql

from ._swordfishcpp import fast_convert  # type: ignore


ModuleResources()

_init_without_args()

if tools.check_import_pro():
    from . import streaming, engine
    from .connection import connect, list_catalogs, exists_catalog, create_catalog, drop_catalog
    from .connection import Partition
    from . import plugins

__version__ = "3.0.4.0"

apilevel = "2.0"            # DBAPI 2.0
threadsafety = 0            # thread safety level, need to check & modify
paramstyle = "qmark"        # param style for Engine URL

__all__ = [
    "dist_version",
    "__version__",
    "exec",
    "call",
    "variable",
    "sql",
    "msql",

    "info",

    "types",
    "data",
    "config",
    "function",
    "io",
    "tools",
    "streaming",
    "engine",
    "plugins",
    "module",

    "partial",
    "scalar",
    "vector",
    "any_vector",
    "array_vector",
    "pair",
    "matrix",
    "set",
    "dictionary",
    "table",

    "NULL",
    "DFLT",
    "Nothing",

    "connect",
    "list_catalogs",
    "exists_catalog",
    "create_catalog",
    "drop_catalog",
    "meta_code",
    "empty_context",
    "Partition",

    "Warning",
    "Error",
    "InterfaceError",
    "DatabaseError",
    "DataError",
    "OperationalError",
    "IntegrityError",
    "InternalError",
    "ProgrammingError",
    "NotSupportedError",

    "fast_convert",
]
