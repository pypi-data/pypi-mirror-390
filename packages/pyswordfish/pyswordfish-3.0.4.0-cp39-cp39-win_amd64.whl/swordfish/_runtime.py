from typing import Any, Dict, List, Optional, Literal

from ._swordfishcpp import (  # type: ignore
    sw_init, sw_uninit, sw_is_ce_edition, sw_info,
    _global_exec, _global_call, _global_vars, _global_sql,
    Constant,
)
from ._config import config
from .tools import parse_site

import atexit


class Runtime(object):
    # static
    _instanc = None
    _initial = False

    _host: str = None
    _port: int = None
    _alias: str = None

    def __new__(cls, *args, **kwargs):
        if cls._instanc is None:
            cls._instanc = super().__new__(cls)
        return cls._instanc

    def set_info(self, host: str, port: int, alias: str):
        sw_info(host, port, alias)
        self._host = host
        self._port = port
        self._alias = alias

    def initialize(self, args: Optional[List[str]] = None):
        if args is None:
            args = []
        if not Runtime._initial:
            sw_init(args)
            atexit.register(self.clean)
            Runtime._initial = True

    def clean(self):
        if Runtime._initial:
            sw_uninit()
            Runtime._initial = False

    def check(self):
        return Runtime._initial

    def __del__(self):
        self.clean()


def _init_without_args():
    args = ["swordfish"] + config.build()
    Runtime().initialize(args)
    Runtime().set_info(*parse_site(config.localSite))


def exec(script: str) -> Constant:
    """
    Execute the given script.

    Parameters
    ----------
    script : str
        A string containing the script to be executed.

    Returns
    -------
    Constant
        The result of executing the script.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.exec("1+2")
    Int(3)
    """
    return _global_exec(script, None)


def call(function: str, *args) -> Constant:
    """
    Call the specified function with the provided arguments.

    Parameters
    ----------
    function : str
        A string indicating the name of the function to be called.

    Returns
    -------
    Constant
        The result of calling the function.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.call("add", 10, 20)
    Long(30)
    """
    return _global_call(function, *args)


def variable(vars: Dict[str, Any]) -> bool:
    """
    Set variables with the provided values.

    Parameters
    ----------
    vars : dict
        A dictionary where keys are variable names and values are the
        corresponding values to be set for those variables.

    Returns
    -------
    bool
        True if the variables were successfully set, False otherwise.

    Examples
    --------
    >>> import swordfish as sf
    >>> vars_to_set = {
    ...     "username": "john_doe",
    ...     "age": 30,
    ...     "is_admin": True,
    ... }
    >>> sf.variable(vars_to_set)
    True
    """
    return _global_vars(vars)


def sql(sql: str, *, vars: Optional[Dict[str, Any]] = None) -> Constant:
    """
    Executes a SQL query.

    Parameters
    ----------
    sql : str
        The SQL query to be executed.
    vars : dict, optional
        A dictionary of variables to be involved in the query. Default is None.

    Returns
    -------
    Constant
        The result of executing the SQL query.

    Examples
    --------
    >>> import swordfish as sf
    >>> import swordfish.function as F
    >>> sf.sql("SELECT * FROM table(1..10 as a) WHERE Func(a) > 0",
    ...        vars={'Func': F.abs})
    """
    return _global_sql(sql, vars)
