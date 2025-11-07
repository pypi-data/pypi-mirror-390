from ._swordfishcpp import Constant  # type: ignore
from ._swordfishcpp import FunctionDef  # type: ignore
from ._swordfishcpp import ProgrammingError  # type: ignore
from ._translator import _translate_wrapper
from ._helper import _ParamAlias
from typing import Literal, Union, TypeVar, Callable, get_args

import inspect

py_print = print
py_bool = bool
py_dict = dict


T = TypeVar('T', bound=Callable[..., Constant])


def __check_sig(func):
    params = inspect.signature(func).parameters
    for name, param in params.items():
        if param.kind != inspect._ParameterKind.POSITIONAL_OR_KEYWORD:
            raise ProgrammingError("udf only support POSITIONAL_OR_KEYWORD param.")


def __create_udf_from_func(func, is_aggregation, is_state, mode: Literal["default", "translate"], frame=None):
    __check_sig(func)
    if mode == "default":
        if is_state:
            raise ProgrammingError("udf does not support state function in default mode.")
        return FunctionDef(func, name=func.__name__, aggregation=is_aggregation)
    elif mode == "translate":
        return _translate_wrapper(func, frame=frame, is_aggregation=is_aggregation, is_state=is_state)
    else:
        raise ValueError("Invalid mode: " + str(mode))


def __set_meta(func, newdef: FunctionDef):
    signature = inspect.signature(func)
    params = signature.parameters
    alias_dict = py_dict()
    for v in params.values():
        main_name = v.name
        annotation = v.annotation
        alias = []
        if annotation != inspect._empty and annotation != Constant:
            types = get_args(annotation)
            for t in types:
                if issubclass(t, _ParamAlias):
                    alias.append(t.name)
        if alias:
            for a in alias:
                alias_dict[a] = main_name
    if alias_dict:
        newdef.set_meta(signature, alias_dict)
    else:
        newdef.set_meta(signature, None)


def swordfish_udf(func=None, *, is_aggregation: py_bool = False, is_state: py_bool = False, mode: Literal["default", "translate"] = "default"):
    """
    Registers a user-defined function (UDF) in Swordfish.

    This enables Python functions to be used within Swordfish SQL queries and
    higher-order functions. The function can be registered in different modes.

    Parameters
    ----------
    func : Optional[Callable], optional
        The UDF to be registered. Defaults to None.
    is_aggregation : bool, optional
        Specifies whether the UDF performs aggregation operations. Defaults to
        False.
    is_state : bool, optional
        Specifies whether the UDF maintains state across calls. Defaults to
        False.
    mode : Literal["default", "translate"], optional
        Determines how the UDF is registered. Defaults to "default".

        - "defalut": The function is saved as a Python UDF object which depends
          on the Python environment to run.
        - "translate": The function is translated into Swordfish's internal
          representation. This eliminates Python environment dependency but
          supports a limited subset of Python syntax.

    Returns
    -------
    FunctionDef
        The FunctionDef object representing the registered UDF.

    Examples
    --------
    >>> import swordfish.function as F
    >>> @F.swordfish_udf(is_aggregation=True)
    >>> def avg_func(a: int, b: int) -> float:
    ...     return (a + b) / 2

    >>> @F.swordfish_udf(is_state=True)
    >>> def counter(state: int, increment: int) -> int:
    ...     return state + increment

    >>> @F.swordfish_udf(mode="translate")
    >>> def translate_to_uppercase(text: str) -> str:
    ...     return text.upper()

    >>> @F.swordfish_udf()
    >>> def add(a: int, b: int) -> int:
    ...     return a + b
    """
    frame = inspect.currentframe()
    frame = inspect.getouterframes(frame)[1].frame
    if func is not None:
        return __create_udf_from_func(func, is_aggregation, is_state, mode, frame)

    def __inner(_func):
        return __create_udf_from_func(_func, is_aggregation, is_state, mode, frame)
    return __inner


def builtin_function(functionDef: FunctionDef) -> Callable[[Union[T, FunctionDef]], Union[T, FunctionDef]]:
    def decorator(func: Union[T, FunctionDef]) -> Union[T, FunctionDef]:
        functionDef.__doc__ = func.__doc__
        __set_meta(func, functionDef)
        return functionDef
    return decorator
