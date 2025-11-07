from typing import Any, List, Union
import typing

from ._swordfishcpp import (  # type: ignore
    Constant, Scalar, Vector, Table, Matrix, Set, Dictionary,
    AnyVector, ArrayVector, Pair,
    Void, Bool, Char, Short, Int, Long, Float, Double,
    String, Blob, Date, Month, Time, Minute, Second,
    DateTime, Timestamp, NanoTime, NanoTimestamp, DateHour,
    Uuid, Int128, Ipaddr, Duration, MetaCode, Point,
    Decimal32, Decimal64, Decimal128,
    FunctionDef,

    _global_call,
    convert_scalar, convert_vector, create_partial,
    convert_matrix, convert_set, convert_dictionary, convert_table,
    create_vector, create_any_vector, create_array_vector, create_pair,
    create_matrix, create_set, create_dictionary_with_key_and_val, create_dictionary, create_table,
    ProgrammingError,
)

from . import function as F

from .types import DataType, TypeDict, TypeList
from .types import ANY


NULL = Void.NULL_VALUE
DFLT = Void.DFLT_VALUE
Nothing = Void.VOID_VALUE


def partial(func: FunctionDef, *args, **kwargs):
    """
    Creates a partially applied function by binding arguments to the original
    function.

    Parameters
    ----------
    func : FunctionDef
        The original function to partially apply arguments to.
    *args
        Positional arguments to bind to the function.
    **kwargs
        Keyword arguments to bind to the function.

    Returns
    -------
    FunctionDef
        A Swordfish FunctionDef object representing the partially applied
        function.

    Examples
    --------
    >>> import swordfish as sf
    >>> import swordfish.function as F
    >>> @F.swordfish_udf
    >>> def add(a,b):
    ...    return a+b
    >>> partial_func1 = sf.partial(add, 1)
    >>> partial_func1(3)
    Long(4)
    >>> partial_func2 = sf.partial(add, b=4)
    >>> partial_func2(3)
    Long(7)
    """
    return create_partial(func, *args, **kwargs)


def scalar(data: Any, *, type: DataType = None) -> Scalar:
    """
    Creates a Swordfish Scalar from a Python object.

    Parameters
    ----------
    data : Any
        The input data to be converted into a Scalar.
    type : DataType, optional
        The desired data type for the Scalar. Defaults to None.

    Returns
    -------
    Scalar
        A Swordfish Scalar object representing the input data.

    Examples
    --------
    >>> import swordfish as sf
    >>> x = sf.scalar(3)
    >>> x
    Long(3)
    >>> y = sf.scalar(3, type="INT")
    >>> y
    Int(3)
    """
    return convert_scalar(data, type)


@typing.overload
def vector(data: Any = None, *, type: DataType = None) -> Vector:
    ...


@typing.overload
def vector(*, type: DataType = None, size: int = 0, capacity: int = 1, default: Any = None) -> Vector:
    ...


def vector(
    data: Any = None,
    *,
    type: DataType = None,
    size: int = 0,
    capacity: int = 1,
    default: Any = None
):
    """
    Creates a Swordfish Vector from a Python object or initializes one with
    specified type, size, capacity, and default value.

    There are two modes of initialization:

    - If ``data`` is provided, it converts the given Python object into a Vector
      of the specified ``type``.
    - If ``data`` is not provided, a new Vector is created with the specified
      ``type``, ``size``, ``capacity``, and ``default`` value.

    Parameters
    ----------
    data : Any, optional
        The input data to initialize the Vector. Defaults to None.
    type : DataType, optional
        The data type for the Vector. Defaults to None.
    size : int, optional
        The number of elements in the Vector (used when ``data`` is None).
        Defaults to 0.
    capacity : int, optional
        The initial capacity of the Vector (used when ``data`` is None).
        Defaults to 1.
    default : Any, optional
        The value used to fill the Vector (used when ``data`` is None).
        Defaults to None.

    Returns
    -------
    Vector
        A Swordfish Vector initialized based on the provided arguments.

    Examples
    --------
    Creating a Vector from existing data:
        >>> import swordfish as sf
        >>> x = sf.vector([1, 2, 3])
        >>> x
        Vector([1,2,3], type=LONG)

    Creating an empty Vector with specific type, size, capacity, and default value:
        >>> y = sf.vector(type="INT", size=3, capacity=5, default=0)
        >>> y
        Vector([0,0,0], type=INT)
    """
    # overload 1
    if data is not None:
        return convert_vector(data, 0, type)
    # overload 2
    return create_vector(type, size, capacity, default)


@typing.overload
def any_vector(data: Any = None) -> AnyVector:
    ...


@typing.overload
def any_vector(*, size: int = 0, capacity: int = 1, default: Any = None) -> AnyVector:
    ...


def any_vector(
    data: Any = None,
    *,
    size: int = 0,
    capacity: int = 1,
    default: Any = None
) -> AnyVector:
    """
    Creates a Swordfish AnyVector from a Python object or initializes one with
    specified size, capacity, and default value.

    There are two modes of initialization:

    - If ``data`` is provided, it converts the given Python object into an
      AnyVector.
    - If ``data`` is not provided, a new AnyVector is created with the specified
      `size`, `capacity`, and `default` value.

    Parameters
    ----------
    data : Any, optional
        The input data to initialize the AnyVector. Defaults to None.
    size : int, optional
        The number of elements in the AnyVector (used when ``data`` is None).
        Defaults to 0.
    capacity : int, optional
        The initial capacity of the AnyVector (used when ``data`` is None).
        Defaults to 1.
    default : Any, optional
        The value to fill the AnyVector (used when ``data`` is None).
        Defaults to None.

    Returns
    -------
    AnyVector
        A Swordfish AnyVector initialized based on the provided arguments.

    Examples
    --------
    Creating an AnyVector from existing data:
        >>> import swordfish as sf
        >>> x = sf.any_vector([1, 2, 3])
        >>> x
        AnyVector((1,2,3))

    Creating an empty AnyVector with specific size, capacity, and default value:
        >>> y = sf.any_vector(size=5, capacity=10, default=3)
        >>> y
        AnyVector((3,3,3,3,3))
    """
    if data is not None:
        return convert_vector(data, 1, ANY)
    return create_any_vector(size, capacity, default)


@typing.overload
def array_vector(data: Any = None, *, type: DataType = None) -> ArrayVector:
    ...


@typing.overload
def array_vector(*, index: Any = None, value: Any = None, type: DataType = None) -> ArrayVector:
    ...


def array_vector(
    data: Any = None,
    *,
    index: Any = None,
    value: Any = None,
    type: DataType = None
) -> ArrayVector:
    """
    Creates a Swordfish ArrayVector from a Python object or using specified
    index, value, and type.

    There are two modes of initialization:

    - If ``data`` is provided, it converts the given Python object into an
      ArrayVector of the specified ``type``.
    - If ``data`` is not provided, an ArrayVector is constructed using the
      given ``index`` and ``value``, with an optional ``type``.

    Parameters
    ----------
    data : Any, optional
        The input data to initialize the ArrayVector. Defaults to None.
    index : Any, optional
        The index portion of the ArrayVector, typically a sequence of indices
        (used when ``data`` is None). Defaults to None.
    value : Any, optional
        The value portion of the ArrayVector, typically a sequence of values
        (used when ``data`` is None). Defaults to None.
    type : DataType, optional
        The data type of the ArrayVector. If None, it is inferred. Defaults to
        None.

    Returns
    -------
    ArrayVector
        A Swordfish ArrayVector initialized based on the provided arguments.

    Examples
    --------
    Creating an ArrayVector from existing data:
        >>> import swordfish as sf
        >>> sf.array_vector([[1, 2], [3, 4, 5], []], type="INT")
        ArrayVector([[1,2],[3,4,5],], type=INT[])

    Creating an ArrayVector using index and value:
        >>> sf.array_vector(index=[1, 2, 3], value=[10, 20, 30], type="SHORT")
        ArrayVector([[10],[20],[30]], type=SHORT[])
    """
    if data is not None:
        return convert_vector(data, 2, type)
    if index is None or value is None:
        raise RuntimeError("ERROR!")
    return create_array_vector(index, value, type)


def pair(a: Any, b: Any, *, type: DataType = None) -> Pair:
    """
    Creates a Swordfish Pair from two Scalar values.

    Parameters
    ----------
    a : Any
        The first value in the Pair.
    b : Any
        The second value in the Pair.
    type : DataType, optional
        The data type of the Pair. Defaults to None.

    Returns
    -------
    Pair
        A Swordfish Pair object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.pair(1, 0, type="LONG")
    Pair(1 : 0, type=LONG)
    """
    if not isinstance(a, Constant):
        a = scalar(a, type=type)
    if not isinstance(b, Constant):
        b = scalar(b, type=type)
    return create_pair(a, b)


@typing.overload
def matrix(data: Any = None, *, type: DataType = None) -> Matrix:
    ...


@typing.overload
def matrix(*, type: DataType = None, rows: int = 1, cols: int = 1, columns_capacity: int = 1, default: Any = None) -> Matrix:
    ...


def matrix(
    data: Any = None,
    *,
    type: DataType = None,
    rows: int = 1,
    cols: int = 1,
    columns_capacity: int = 1,
    default: Any = None
) -> Matrix:
    """
    Creates a Swordfish Matrix from a Python object or initializes one with
    specified parameters.

    There are two modes of initialization:

    - If ``data`` is provided, it converts the given Python object into a
      Matrix of the specified ``type``.
    - If ``data`` is not provided, a new Matrix is created with the
      specified ``type``, ``rows``, ``cols``, ``columns_capacity``, and
      ``default`` value.

    Parameters
    ----------
    data : Any, optional
        The input data to initialize the Matrix. Defaults to None.
    type : DataType, optional
        The data type for the Matrix. Defaults to None.
    rows : int, optional
        The number of rows in the Matrix (used when `data` is None). Defaults to
        1.
    cols : int, optional
        The number of columns in the Matrix (used when `data` is None). Defaults
        to 1.
    columns_capacity : int, optional
        The capacity for each column in the Matrix (used when `data` is None).
        Defaults to 1.
    default : Any, optional
        The value used to fill the Matrix (used when `data` is None). Defaults
        to None.

    Returns
    -------
    Matrix
        A Swordfish Matrix initialized based on the provided arguments.

    Examples
    --------
    Creating a Matrix from existing data:
        >>> import swordfish as sf
        >>> sf.matrix([1, 2, 3], type="INT")
        Matrix(#0 #1 #2
        -- -- --
        1  2  3
        , type=INT)

    Creating an empty Matrix with specific type, rows, columns, and default value:
        >>> sf.matrix(type="INT", rows=2, cols=2, columns_capacity=1, default=1)
        Matrix(#0 #1
        -- --
        1  1
        1  1
        , type=INT)
    """
    if data is not None:
        return convert_matrix(data, type)
    return create_matrix(type, rows, cols, columns_capacity, default)

@typing.overload
def set(data: Any = None, *, type: DataType = None) -> Set:
    ...


@typing.overload
def set(*, type: DataType = None, capacity: int = 0) -> Set:
    ...


def set(data: Any = None, *, type: DataType = None, capacity: int = 0) -> Set:
    """
    Creates a Swordfish Set from a Python object or initializes one with a
    specified type and capacity.

    There are two modes of initialization:

    - If ``data`` is provided, it converts the given Python object into a
      Set of the specified ``type``.
    - If ``data`` is not provided, a new Set is created with the specified
      ``type`` and ``capacity``.

    Parameters
    ----------
    data : Any, optional
        The input data to initialize the Set. Defaults to None.
    type : DataType, optional
        The data type for the Set. Defaults to None.
    capacity : int, optional
        The initial capacity of the Set (used when ``data`` is None).
        Defaults to 0.

    Returns
    -------
    Set
        A Swordfish Set initialized based on the provided arguments.

    Examples
    --------
    Creating a Set from existing data:
        >>> import swordfish as sf
        >>> sf.set({1, 2, 3}, type="INT")
        Set(set(3, 2, 1), type=INT)

    Creating an empty Set with a specific type and capacity:
        >>> sf.set(type="CHAR", capacity=5)
        Set(set(), type=CHAR)
    """
    if data is not None:
        return convert_set(data, type)
    return create_set(type, capacity)


@typing.overload
def dictionary(
    data: Any = None,
    *,
    key_type: DataType = None,
    val_type: DataType = None,
    ordered: bool = True,
) -> Dictionary:
    ...


@typing.overload
def dictionary(
    *,
    keys: Any = None,
    vals: Any = None,
    key_type: DataType = None,
    val_type: DataType = None,
    ordered: bool = True,
) -> Dictionary:
    ...


@typing.overload
def dictionary(
    *,
    key_type: DataType = None,
    val_type: DataType = None,
    ordered: bool = True,
) -> Dictionary:
    ...


def dictionary(
    data: Any = None,
    *,
    keys: Any = None,
    vals: Any = None,
    key_type: DataType = None,
    val_type: DataType = None,
    ordered: bool = True,
) -> Dictionary:
    """
    Creates a Swordfish Dictionary from a Python object, from separate keys and
    values, or as an empty dictionary with specified key and value types.

    This function provides three modes of initialization:

    - If ``data`` is provided, it converts a given Python object into a
      Dictionary, optionally with the specified ``key_type`` and
      ``val_type``.
    - If ``keys`` and ``vals`` are provided, it constructs a Dictionary
      from these separate sequences, optionally with the specified
      ``key_type`` and ``val_type``.
    - If neither ``data`` nor ``keys`` and ``vals`` are provided, it
      initializes an empty Dictionary with the specified ``key_type`` and
      ``val_type``.

    Parameters
    ----------
    data : Any, optional
        The Python object to initialize the Dictionary. Defaults to None.
    keys : Any, optional
        The keys for the Dictionary (used when ``data`` is None). Defaults to
        None.
    vals : Any, optional
        The values for the Dictionary (used when ``data`` is None). Defaults to
        None.
    key_type : DataType, optional
        The data type of the Dictionary keys. Defaults to None.
    val_type : DataType, optional
        The data type of the Dictionary values. Defaults to None.
    ordered : bool, optional
        Whether to maintain the insertion order of the Dictionary elements.
        Defaults to True.

    Returns
    -------
    Dictionary
        A Swordfish Dictionary initialized based on the provided arguments.

    Examples
    --------
    Creating a Dictionary from existing data:
        >>> import swordfish as sf
        >>> my_dict = {"name": "Alice", "age": 25}
        >>> sf.dictionary(my_dict, key_type="STRING", val_type="ANY", ordered=True)
        Dictionary(name->Alice
        age->25
        , key_type=STRING, val_type=ANY)

    Creating a Dictionary using separate keys and values:
        >>> sf.dictionary(keys=[1, 2, 3], vals=['a', 'b', 'c'],
        ...               key_type="INT", val_type="STRING", ordered=False)
        Dictionary(3->c
        2->b
        1->a
        , key_type=INT, val_type=STRING)

    Creating an empty Dictionary with specified key and value types:
        >>> sf.dictionary(key_type="STRING", val_type="INT", ordered=True)
        Dictionary(, key_type=STRING, val_type=INT)
    """
    if data is not None:
        # func1
        return convert_dictionary(data, key_type, val_type, ordered)
    if keys is not None and vals is not None:
        # func2
        return create_dictionary_with_key_and_val(keys, vals, key_type, val_type, ordered)
    # func3
    return create_dictionary(key_type, val_type, ordered)


@typing.overload
def table(data: Any = None, *, types: TypeDict = None) -> Table:
    ...


@typing.overload
def table(data: Any = None, *, names: List[str] = None, types: TypeList = None) -> Table:

    ...


@typing.overload
def table(*, types: TypeDict = None, size: int = 0, capacity: int = 1) -> Table:
    ...


@typing.overload
def table(*, names: List[str] = None, types: TypeList = None, size: int = 0, capacity: int = 1) -> Table:
    ...


@typing.overload
def table(data: str) -> Table:
    ...


def table(
    data: Any = None,
    *,
    names: List[str] = None,
    types: Union[TypeDict, TypeList] = None,
    size: int = 0,
    capacity: int = 1,
) -> Table:
    """
    Creates or retrieves a Swordfish Table using various initialization methods.

    There are multiple modes of initialization:

    - If ``data`` is a string, it retrieves a shared Swordfish Table by its
        name.
    - If ``data`` is provided (and not a string), it converts the given
        Python object into a Table, optionally using ``types`` and ``names``.
    - If ``names`` and ``types`` are provided (without ``data``), an empty
        Table is created with the given column names, types, size, and
        capacity.
    - If ``types`` is provided as a dictionary (without ``data``), an empty
        Table is created using the given column types, size, and capacity.

    Parameters
    ----------
    data : Any, optional
        The data to initialize the Table. Can be a Python dict, Pandas DataFrame,
        or a str referring to a shared Table. Defaults to None.
    names : List[str], optional
        The column names for the Table (used when ``data`` is provided).
        Defaults to None.
    types : Union[TypeDict, TypeList], optional
        A mapping of column names to their respective data types, or a list of
        types matching ``names``. Defaults to None.
    size : int, optional
        The initial number of rows in the Table (used when creating an empty
        Table). Defaults to 0.
    capacity : int, optional
        The initial allocated capacity for storing rows in the Table (used when
        creating an empty Table). Defaults to 1.

    Returns
    -------
    Table
        A Swordfish Table initialized based on the provided arguments.

    Examples
    --------
    Retrieving a shared Table by name:
        >>> import swordfish as sf
        >>> table = sf.table("shared_table_name")

    Creating a Table from a Python dictionary with type mapping:
        >>> my_dict = {
        ...     "id": [1, 2, 3, 4],
        ...     "name": ["Alice", "Bob", "Charlie", "David"],
        ...     "age": [25, 30, 35, 40],
        ... }
        >>> column_types = {
        ...     "id": "LONG",
        ...     "name": "STRING",
        ...     "age": "INT",
        ... }
        >>> t = sf.table(my_dict, types=column_types)
        >>> t
        id name    age
        -- ------- ---
        1  Alice   25
        2  Bob     30
        3  Charlie 35
        4  David   40

    Creating a Table using column names and types:
        >>> t = sf.table(data=my_dict, names=["id", "name", "age"],
        ...              types=["LONG", "STRING", "INT"])
        >>> t
        id name    age
        -- ------- ---

    Creating an empty Table with column names, types, and initial size:
        >>> t = sf.table(names=["id", "name", "age"], types=["INT", "STRING",
        ...              "INT"], size=5, capacity=10)
        >>> t
        id name    age
        -- ------- ---

    Creating an empty Table using a type dictionary:
        >>> t = sf.table(types=column_types, size=5, capacity=10)
        >>> t
        id name    age
        -- ------- ---
    """
    if data is not None:
        if isinstance(data, str):
            re = _global_call("objByName", data, True)
            if not isinstance(re, Table):
                raise ProgrammingError("Cannot find the shared table.")
            return re
        if names is None and types is None:
            return convert_table(data, dict())
        if isinstance(names, list) and isinstance(types, list):
            if len(names) != len(types):
                raise ProgrammingError("The number of column names should be the same as the number of data types.")
            new_types = dict()
            for n, t in zip(names, types):
                new_types[n] = t
            return convert_table(data, new_types)
        elif isinstance(types, dict):
            return convert_table(data, types)
        elif types is None:
            return convert_table(data, dict())
        else:
            raise ProgrammingError("Can't create Table with invalid names or types.")
    if names is None and types is None:
        raise ProgrammingError("Can't create Table with empty names and empty types.")
    if isinstance(names, list) and isinstance(types, list):
        if len(names) != len(types):
            raise ProgrammingError("The number of column names should be the same as the number of data types.")
        new_types = dict()
        for n, t in zip(names, types):
            new_types[n] = t
        types = new_types
    if isinstance(types, dict):
        return create_table(types, size, capacity)
    if types is None:
        raise ProgrammingError("Can't create Table with empty names and empty types.")
    raise ProgrammingError("Can't create Table with invalid names or types.")


Constant.rows = F.rows
Constant.cols = F.cols

Vector.rowRank = F.rowRank
Vector.rename_ = F.rename_
Vector.mrank = F.mrank

Set.keys = F.keys

Dictionary.keys = F.keys
Dictionary.values = F.values

Table.schema = F.schema
Table.keys = F.keys
Table.values = F.values
Table.head = F.head
Table.tail = F.tail
Table.count = F.count
Table.summary = F.summary
Table.sortBy_ = F.sortBy_


__all__ = [
    "Constant",
    "Scalar",
    "Vector",
    "Matrix",
    "Set",
    "Dictionary",
    "Table",

    "AnyVector",
    "ArrayVector",

    "Void",
    "NULL",
    "DFLT",
    "Nothing",
    "Bool",
    "Char",
    "Short",
    "Int",
    "Long",
    "Float",
    "Double",
    "String",
    "Blob",
    "Date",
    "Month",
    "Time",
    "Minute",
    "Second",
    "DateTime",
    "Timestamp",
    "NanoTime",
    "NanoTimestamp",
    "DateHour",
    "Uuid",
    "Int128",
    "Ipaddr",
    "Duration",
    "MetaCode",
    "Point",
    "Decimal32",
    "Decimal64",
    "Decimal128",
    "FunctionDef",

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
]
