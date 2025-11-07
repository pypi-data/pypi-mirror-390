from __future__ import annotations

import abc
from decimal import Decimal
from enum import Enum
from pathlib import Path
from types import FunctionType
from typing import (
    Any,
    BinaryIO,
    Dict,
    List,
    Literal,
    Optional,
    overload,
    Tuple,
    Union,
)
from typing_extensions import Self

import numpy as np
import pandas as pd

from ._engine import (
    Builder,
    StreamBroadcastEngineBuilder,
    CrossSectionalEngineBuilder,
    TimeSeriesEngineBuilder,
    ReactiveStateEngineBuilder,
    StreamFilterEngineBuilder,
)
from .plugins import matching_engine_simulator as plugin_simulator
from .types import TypeDict
from .function import DFLT
from .connection import Connection


def sw_init(args: List[str]) -> None: ...
def sw_uninit() -> None: ...
def sw_check() -> bool: ...
def sw_is_ce_edition() -> bool: ...
def sw_info(host: str, port: int, alias: str): ...


def set_dynamic_config(config_name: str, config_value: Any): ...


def _global_exec(script: str, vars: Optional[Dict[str, Any]] = None) -> Constant: ...
def _global_call(function: str, *args) -> Constant: ...
def _global_vars(var_dict: Dict[str, Any]) -> bool: ...
def _global_undef(name: str) -> None: ...
def _global_sql(script: str, vars: Optional[Dict[str, Any]] = None) -> Constant: ...


EXPARAM_DEFAULT = -0x7fffffff - 1


class Session:
    """
    A Swordfish session that provides script execution and function calling
    capabilities.
    """
    def exec(self, script: str, vars: Optional[Dict[str, Any]] = None) -> Constant:
        """
        Executes Swordfish scripts and returns the result.
        """
        ...

    def call(self, function: str, *args) -> Constant:
        """
        Calls a Swordfish function with the provided arguments.
        """
        ...

    def variable(self, val_maps: Dict[str, Any]) -> bool:
        """
        Defines variables in the Swordfish session based on Python variables.

        Returns
        -------
        bool
            True if variables are successfully defined, False otherwise.
        """
        ...


class RemoteSession(Session):
    pass


class ConnectionImpl:
    def __enter__(self) -> ConnectionImpl: ...
    def __exit__(self, exc_type, exc_value, traceback): ...
    def sql(self, sql: str, *, vars: Dict[str, Any]) -> Constant: ...
    def session(self) -> Session: ...


class BaseConnectionImpl(ConnectionImpl):
    pass


class DefaultSessionConnectionImpl(BaseConnectionImpl):
    @classmethod
    def create(cls) -> DefaultSessionConnectionImpl: ...


class RemoteConnectionImpl(ConnectionImpl):
    @classmethod
    def create(cls, host: str, port: int, user: str = "", password: str = "") -> RemoteConnectionImpl: ...


class Constant:
    """
    The base class for all Swordfish objects.

    All data types (such as `Int`, `String`) and data forms (such as `Vector`,
    `Table`) inherit from this class.

    Provides common operations and properties for all Swordfish data objects.
    """
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    def __copy__(self) -> Constant: ...
    def __deepcopy__(self, memo) -> Constant: ...
    def __bool__(self) -> bool: ...
    def __int__(self) -> int: ...
    def __len__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __contains__(self, o) -> Bool: ...
    def __neg__(self) -> Constant: ...
    def __abs__(self) -> Constant: ...
    def __add__(self, o: Union[Constant, Any]) -> Constant: ...
    def __radd__(self, o: Union[Constant, Any]) -> Constant: ...
    def __sub__(self, o: Union[Constant, Any]) -> Constant: ...
    def __rsub__(self, o: Union[Constant, Any]) -> Constant: ...
    def __mul__(self, o: Union[Constant, Any]) -> Constant: ...
    def __rmul__(self, o: Union[Constant, Any]) -> Constant: ...
    def __truediv__(self, o: Union[Constant, Any]) -> Constant: ...
    def __rtruediv__(self, o: Union[Constant, Any]) -> Constant: ...
    def __floordiv__(self, o: Union[Constant, Any]) -> Constant: ...
    def __rfloordiv__(self, o: Union[Constant, Any]) -> Constant: ...
    def __mod__(self, o: Union[Constant, Any]) -> Constant: ...
    def __rmod__(self, o: Union[Constant, Any]) -> Constant: ...
    def __pow__(self, o: Union[Constant, Any]) -> Constant: ...
    def __rpow__(self, o: Union[Constant, Any]) -> Constant: ...
    def __lt__(self, o: Union[Constant, Any]) -> Constant: ...
    def __le__(self, o: Union[Constant, Any]) -> Constant: ...
    def __eq__(self, o: Union[Constant, Any]) -> Constant: ...
    def __ne__(self, o: Union[Constant, Any]) -> Constant: ...
    def __gt__(self, o: Union[Constant, Any]) -> Constant: ...
    def __ge__(self, o: Union[Constant, Any]) -> Constant: ...
    def __and__(self, o: Union[Constant, Any]) -> Constant: ...
    def __rand__(self, o: Union[Constant, Any]) -> Constant: ...
    def __or__(self, o: Union[Constant, Any]) -> Constant: ...
    def __ror__(self, o: Union[Constant, Any]) -> Constant: ...
    def __xor__(self, o: Union[Constant, Any]) -> Constant: ...
    def __rxor__(self, o: Union[Constant, Any]) -> Constant: ...

    @property
    def form(self) -> DataForm:
        """
        Retrieves the data form (DataForm) of a Constant object.

        Returns
        -------
        DataForm
            The data form representing the structure of the data (e.g. SCALAR,
            VECTOR, TABLE).
        """
        ...

    @property
    def type(self) -> DataType:
        """
        Retrieves the data type (DataType) of a Constant object.

        Returns
        -------
        DataType
            The data type representing the type of the data (e.g., INT, FLOAT,
            STRING).
        """
        ...

    def is_null(self) -> Constant:
        """
        Checks if the object is a NULL value or contains NULL elements.

        Returns
        -------
        Constant
            A boolean Constant indicating whether elements are NULL. For scalar
            input, returns a single boolean value. For non-scalar input, returns a
            result with the same shape as the input.
        """
        ...

    def rows(self) -> Int:
        """
        Returns the number of rows in the object.

        Returns
        -------
        Int
            The number of rows. For scalar objects, returns 1.
        """
        ...

    def cols(self) -> Int:
        """
        Returns the number of columns in the object.

        Returns
        -------
        Int
            The number of columns. For scalar objects, returns 1.
        """
        ...


class Iterator(Constant):
    """
    Iterator for Constant objects.

    Provides a standard way to iterate over the elements of any Swordfish object.
    This follows Python's iterator protocol and can be used in for loops and other
    iteration contexts.
    """
    def __iter__(self) -> Iterator: ...
    def __next__(self) -> Constant: ...


class Scalar(Constant):
    """
    Superclass for scalar types.

    Represents single-value data types like `Int`, `String`, and `Float`. Inherits
    from `Constant` and provides functionality specific to scalar values.
    """

    def to_python(self) -> Any:
        """Converts the Scalar to a corresponding Python type.

        Returns:
            Any: A Python object that represents the same value as the Scalar. 
            The exact type depends on the Scalar's data type (e.g., int, str, float).
        """
        ...


class EnumInt(Scalar):
    """
    A base class for enumerated integer constants.

    This class serves as the parent class for various enumeration types, such as
    DataType, DataForm, and ObjectType.
    """
    def __init__(self, desc: str, val: int, type: int) -> None: ...
    def __int__(self) -> int: ...
    def __getitem__(self) -> Any: ...
    def set_function(self, func): ...


class DataType(EnumInt):
    """
    Enumeration defining Swordfish data types.

    Defines various data types, such as INT, FLOAT, STRING, etc. Inherits from
    EnumInt and provides type information for Constant objects. The data type of a
    Constant object can be retrieved using ``Constant.type``.
    """
    ...


class DataForm(EnumInt):
    """
    Enumeration defining Swordfish data forms.

    Defines various data forms, such as SCALAR, VECTOR, TABLE, etc. Inherits from
    EnumInt and provides structural information for Constant objects. The data form
    of a Constant object can be retrieved using ``Constant.form``.
    """
    ...


class ObjectType(EnumInt):
    """
    Enumeration defining Swordfish object types.

    Defines object types including VAR (local variable), SHARED (shared variable),
    and DEF (function definition). This helps categorize different kinds of objects
    in the Swordfish system.
    """
    ...


class LogLevel(EnumInt):
    """
    Enumeration representing log levels.

    Defines logging levels including DEBUG, INFO, WARNING, and ERROR. Used to
    control the verbosity and filtering of log messages in the system.
    """
    ...


class FunctionDef(Constant):
    """
    Represents a function definition.

    Inherits from the Constant class and provides a way to treat function
    definitions.
    """
    # FIXME:
    @overload
    def __init__(self, func: FunctionType, *, name: str = "<lambda>", aggregation: bool = None):
        """
        Initializes a FunctionDef object from a Python function.

        Creates a lambda function that can be used in Swordfish from a Python
        function object.

        Parameters
        ----------
        func : FunctionType
            The Python function to be wrapped.
        name : str, optional
            The name of the function. Defaults to "<lambda>".
        aggregation : bool, optional
            Indicates whether this is an aggregate function. Defaults to None.
        """
        ...

    # FIXME:
    @overload
    def __init__(self, code: str, *, state: bool = False):
        """
        Initializes a FunctionDef object from a Swordfish function definition string.

        Creates a function definition from Swordfish syntax code string containing a
        single anonymous function definition.

        Parameters
        ----------
        code : str
            A string containing a single anonymous function definition in Swordfish
            syntax.
        state : bool, optional
            State parameter for the function. Defaults to False.
        """
        ...

    def __copy__(self) -> FunctionDef: ...
    def __deepcopy__(self, memo) -> FunctionDef: ...
    def __get__(self): ...
    def __call__(self, *args, **kwargs) -> Constant: ...
    def set_meta(self, signature, alias) -> None: ...


class Vector(Constant):
    """
    Represents a one-dimensional vector.

    Inherits from the Constant class and provides functionality for working with
    vector data structures. Supports conversion to/from Python lists, tuples, and
    NumPy arrays.
    """

    def __getitem__(self, index) -> Scalar: ...
    def __setitem__(self, index, value) -> None: ...
    def __iter__(self) -> Iterator: ...

    @classmethod
    def from_list(cls, data: list, type: DataType = None) -> Vector:
        """
        Constructs a Vector object from a Python list.

        Parameters
        ----------
        data : list
            The input data as a Python list instance.
        type : DataType, optional
            An enumeration value from the DataType enum, specifying the target data
            type for the vector elements.

        Returns
        -------
        Vector
            A new Vector object containing the data from the input list, converted
            to the specified data type.
        """
        ...

    @classmethod
    def from_tuple(cls, data: tuple, type: DataType = None) -> Vector:
        """
        Constructs a Vector object from a Python tuple.

        Parameters
        ----------
        data : tuple
            The input data as a Python tuple instance.
        type : DataType, optional
            An enumeration value from the DataType enum, specifying the target data
            type for the vector elements.

        Returns
        -------
        Vector
            A new Vector object containing the data from the input tuple, converted
            to the specified data type.
        """
        ...

    @classmethod
    def from_numpy(cls, data: np.ndarray, type: DataType = None) -> Vector:
        """
        Constructs a Vector object from a NumPy array.

        Parameters
        ----------
        data : np.ndarray
            The input data as a 1-dimensional ndarray.
        type : DataType, optional
            An enumeration value from the DataType enum, specifying the target data
            type for the vector elements.

        Returns
        -------
        Vector
            A new Vector object containing the data from the input NumPy array.
        """
        ...

    def to_numpy(self) -> np.ndarray:
        """
        Converts the Vector object to a NumPy ndarray.

        Returns
        -------
        np.ndarray
            A new 1-dimensional NumPy array containing all the elements of the
            Vector.
        """
        ...

    def to_list(self) -> list:
        """
        Converts the Vector object to a Python list.

        Returns
        -------
        list
            A new Python list containing all the elements of the Vector.
        """
        ...


class AnyVector(Vector):
    """
    A versatile vector container that can store elements of any type.

    Extends the Vector class to allow storage of heterogeneous elements, making it
    suitable for mixed-type data scenarios.
    """
    def __getitem__(self, index) -> Constant: ...
    def __setitem__(self, index, value) -> None: ...

    @classmethod
    def from_list(cls, data: list) -> AnyVector:
        """
        Constructs an AnyVector object from a Python list.

        Parameters
        ----------
        data : list
            The input data as a Python list instance.

        Returns
        -------
        AnyVector
            A new AnyVector object containing the data from the input list. The
            elements retain their original types.
        """
        ...

    @classmethod
    def from_tuple(cls, data: tuple) -> AnyVector:
        """
        Constructs an AnyVector object from a Python tuple.

        Parameters
        ----------
        data : tuple
            The input data as a Python tuple instance.

        Returns
        -------
        AnyVector
            A new AnyVector object containing the data from the input tuple. The
            elements retain their original types.
        """
        ...

    @classmethod
    def from_numpy(cls, data: np.ndarray) -> AnyVector:
        """
        Constructs an AnyVector object from a NumPy ndarray.

        Parameters
        ----------
        data : np.ndarray
            The input data as a NumPy ndarray.

        Returns
        -------
        AnyVector
            A new AnyVector object containing the data from the input ndarray.
        """
        ...

    def to_numpy(self) -> np.ndarray:
        """
        Converts the AnyVector to a NumPy ndarray.

        Returns
        -------
        np.ndarray
            A NumPy array containing the data from the AnyVector. The array has
            dtype="object" and each element is a Constant.
        """
        ...

    def to_list(self) -> list:
        """
        Converts the AnyVector to a Python list.

        Returns
        -------
        list
            A Python list containing the data from the AnyVector. Each element in
            the list is a Constant object.
        """
        ...


class ArrayVector(Vector):
    """
    A vector container designed to store arrays as its elements.
    """
    def __getitem__(self, index) -> Vector: ...
    def __setitem__(self, index, value) -> None: ...

    @classmethod
    def from_list(cls, data: list, type: DataType = None) -> ArrayVector:
        """
        Constructs an ArrayVector object from a Python list of arrays.

        Parameters
        ----------
        data : list
            A list where each element is an array-like object.
        type : DataType, optional
            An enumeration value from the DataType enum, specifying the target data
            type for the array elements. If None, the type will be inferred.

        Returns
        -------
        ArrayVector
            A new ArrayVector object containing the arrays from the input list.
        """
        ...

    @classmethod
    def from_tuple(cls, data: tuple, type: DataType = None) -> ArrayVector:
        """
        Constructs an ArrayVector object from a Python tuple.

        Parameters
        ----------
        data : tuple
            A tuple where each element is an array-like object.
        type : DataType, optional
            An enumeration value from the DataType enum, specifying the target data
            type for the array elements. If None, the type will be inferred.

        Returns
        -------
        ArrayVector
            A new ArrayVector object containing the arrays from the input tuple.
        """
        ...

    @classmethod
    def from_numpy(cls, data: np.ndarray, type: DataType = None) -> ArrayVector:
        """
        Constructs an ArrayVector object from a NumPy ndarray.

        Parameters
        ----------
        data : np.ndarray
            A NumPy array.
        type : DataType, optional
            An enumeration value from the DataType enum, specifying the target data
            type for the array elements. If None, the type will be inferred from the
            NumPy array's dtype.

        Returns
        -------
        ArrayVector
            A new ArrayVector object containing the arrays from the input NumPy
            array.
        """
        ...

    def to_numpy(self) -> np.ndarray:
        """
        Converts the ArrayVector to a NumPy ndarray.

        Returns
        -------
        np.ndarray
            A NumPy array with dtype="object".
        """
        ...

    def to_list(self) -> list:
        """
        Converts the ArrayVector to a Python list of lists.

        Returns
        -------
        list
            A Python list where each element is also a list.
        """
        ...


class Pair(Constant):
    """
    Represents a pair of values in Swordfish.

    A container that holds exactly two values. Instances of this class should not be
    created directly. Use the swordfish.pair() function to create Pair objects.
    """
    def __getitem__(self, index) -> Scalar: ...
    def __setitem__(self, index, value) -> None: ...
    def __iter__(self) -> Iterator: ...

    def to_list(self) -> list:
        """
        Converts the Pair to a Python list.

        Returns
        -------
        list
            A Python list containing two elements. Each element is converted to its
            corresponding Python type.
        """
        ...


class Matrix(Vector):
    """
    Represents a two-dimensional matrix.
    """
    def __getitem__(self, index) -> Constant: ...
    def __setitem__(self, index, value) -> None: ...

    @classmethod
    def from_numpy(cls, data: np.ndarray, type: DataType = None) -> Matrix:
        """
        Constructs a Matrix object from a one-dimensional or two-dimensional NumPy
        ndarray.

        Parameters
        ----------
        data : np.ndarray
            A 1D or 2D NumPy array to be converted into a Matrix.
        type : DataType, optional
            An enumeration value from the DataType enum, specifying the target data
            type for the matrix elements. If None, the type will be inferred from the
            NumPy array's dtype.

        Returns
        -------
        Matrix
            A new Matrix object containing the data from the input NumPy array.
        """
        ...

    def to_numpy(self) -> np.ndarray:
        """
        Converts the Matrix to a two-dimensional NumPy ndarray.

        Returns
        -------
        np.ndarray
            A 2D NumPy array containing the data from the Matrix.
        """
        ...

    def to_list(self) -> list:
        """
        Converts the Matrix to a nested Python list.

        Returns
        -------
        list
            A list of lists representing the Matrix. Each inner list corresponds to a
            column of the Matrix.
        """
        ...


class Set(Constant):
    """
    Represents a container with no duplicate values.
    """
    def __iter__(self) -> Iterator: ...

    @classmethod
    def from_set(cls, data: set, type: DataType = None) -> Set:
        """
        Constructs a Set object from a Python set.

        Parameters
        ----------
        data : set
            A Python set containing the elements to be included in the new Set.
        type : DataType, optional
            An enumeration value from the DataType enum, specifying the target data
            type for the Set elements. If None, the type will be inferred from the
            input set's elements. Defaults to None.

        Returns
        -------
        Set
            A new Set object containing the elements from the input Python set.
        """
        ...

    def to_set(self) -> set:
        """
        Converts the Set to a Python set.

        Returns
        -------
        set
            A Python set containing the elements of this Set. Each element in the
            returned set is a Constant object.
        """
        ...


class Dictionary(Constant):
    """
    Represents a container type that holds unique key-value pairs.

    A mapping structure similar to Python's dict, but with Swordfish-specific type
    handling and conversion capabilities.
    """
    def __getitem__(self, index) -> Constant: ...
    def __setitem__(self, index, value) -> None: ...
    def __iter__(self) -> Iterator: ...

    @classmethod
    def from_dict(cls, data: dict, *, key_type: DataType = None, val_type: DataType = None) -> Dictionary:
        """
        Constructs a Dictionary object from a Python dict.

        Parameters
        ----------
        data : dict
            A Python dict containing the key-value pairs to be included in the new
            Dictionary.
        key_type : DataType, optional
            An enumeration value from the DataType enum, specifying the target data
            type for the Dictionary keys. If None, the type will be inferred from the
            input dict's keys. Defaults to None.
        val_type : DataType, optional
            An enumeration value from the DataType enum, specifying the target data
            type for the Dictionary values. If None, the type will be inferred from
            the input dict's values. Defaults to None.

        Returns
        -------
        Dictionary
            A new Dictionary object containing the key-value pairs from the input
            Python dict.
        """
        ...

    def to_dict(self) -> dict:
        """
        Converts the Dictionary to a Python dict.

        Returns
        -------
        dict
            A Python dict representing this Dictionary object. If the Dictionary's
            value type is 'Any': keys are converted to their corresponding Python
            types, values are Constant objects. Otherwise, both keys and values are
            converted to their corresponding Python types.
        """
        ...

    def keys(self) -> Constant:
        """
        Retrieves the keys of the Dictionary.

        Returns
        -------
        Constant
            The retrieved dictionary keys.
        """
        ...

    def values(self) -> Constant:
        """
        Retrieves the values of the Dictionary.

        Returns
        -------
        Constant
            The retrieved dictionary values.
        """
        ...

    def items(self) -> DictionaryItems:
        """
        Retrieves an iterator over the Dictionary's key-value pairs.

        Returns
        -------
        DictionaryItems
            An iterable object that yields key-value pairs from the Dictionary.
        """
        ...


class DictionaryItems:
    def __iter__(self) -> DictionaryItemsIterator: ...


class DictionaryItemsIterator:
    def __next__(self) -> AnyVector: ...


class Table(Constant):
    """
    Represents a tabular data structure.

    In tables, data is logically organized in a row-and-column format. Each row
    represents a unique record, and each column represents a field in the record.
    Provides comprehensive functionality for data manipulation and analysis.
    """
    def __getitem__(self, index) -> Constant: ...
    def __setitem__(self, index, value) -> None: ...
    def __iter__(self) -> Iterator: ...
    def __getattr__(self, name: str) -> Constant: ...

    @classmethod
    def from_pandas(cls, data: pd.DataFrame, *, types: Dict[str, DataType] = None) -> Table:
        """
        Creates a Table instance from a Pandas DataFrame.

        Parameters
        ----------
        data : pd.DataFrame
            The Pandas DataFrame to convert.
        types : Dict[str, DataType], optional
            Column type mappings where keys are column names and values are DataType
            enumerations. If None, types are inferred automatically.

        Returns
        -------
        Table
            A new Table instance containing the DataFrame data.
        """
        ...

    def to_pandas(self) -> pd.DataFrame:
        """
        Converts this Table to a Pandas DataFrame.

        Returns
        -------
        pd.DataFrame
            A DataFrame with equivalent data and column types automatically mapped
            to compatible Pandas dtypes.
        """
        ...

    @property
    def types(self) -> Dict[str, DataType]:
        """
        Returns the data types of all table columns.

        Returns
        -------
        Dict[str, DataType]
            Mapping of column names to their corresponding DataType values.
        """
        ...

    @property
    def name(self) -> str:
        """
        Returns the table's name.

        Returns
        -------
        str
            The assigned name of this table.
        """
        ...

    @property
    def is_shared(self) -> bool:
        """
        Indicates whether this table is shared across sessions.

        Returns
        -------
        bool
            True if shared, False if private to current session.
        """
        ...

    def share(self, name: str, readonly: bool = False) -> Self:
        """
        Makes this table accessible across sessions with the specified name.

        Parameters
        ----------
        name : str
            Global name for the shared table.
        readonly : bool, optional
            Whether to restrict the table to read-only access. Defaults to False.

        Returns
        -------
        Self
            This table instance for method chaining.
        """
        ...

    def schema(self) -> Dictionary:
        """
        Returns the table's schema information.

        Returns
        -------
        Dictionary
            Column names mapped to their respective data types.
        """
        ...

    def head(self, n: Constant = DFLT) -> Constant:
        """
        Returns the first n rows of the table.

        Parameters
        ----------
        n : Constant, optional
            Number of rows to return. Uses default if not specified.

        Returns
        -------
        Constant
            A table containing the first n rows.
        """
        ...

    def tail(self, n: Constant = DFLT) -> Constant:
        """
        Retrieves the last n rows of the table.

        Parameters
        ----------
        n : Constant, optional
            The number of rows to retrieve. Defaults to DFLT.

        Returns
        -------
        Constant
            A subset of the table containing the last n rows.
        """
        ...

    def count(self) -> Constant:
        """
        Counts the number of rows in the table.

        Returns
        -------
        Constant
            The number of rows in the table.
        """
        ...

    def summary(self, interpolation: Constant = DFLT, characteristic: Constant = DFLT,
                percentile: Constant = DFLT, precision: Constant = DFLT,
                partitionSampling: Constant = DFLT) -> Constant:
        """
        Computes comprehensive summary statistics for numeric columns.

        Parameters
        ----------
        interpolation : Constant, optional
            Percentile interpolation method. Available options: "linear" (default),
            "nearest", "lower", "higher", "midpoint".
        characteristic : Constant, optional
            Statistics to calculate. Options: "avg" (mean), "std" (standard deviation).
            Default computes both ["avg", "std"].
        percentile : Constant, optional
            List of percentile values (0-1) to compute. Default is [0.25, 0.50, 0.75]
            for 25th, 50th, and 75th percentiles.
        precision : Constant, optional
            Convergence threshold for iterative calculations. Recommended range:
            [1e-3, 1e-9]. Default: 1e-3.
        partitionSampling : Constant, optional
            For partitioned tables, either the number of partitions to sample
            (integer) or sampling ratio (0-1]. No effect on non-partitioned tables.

        Returns
        -------
        Constant
            Summary table with min, max, count, mean, std dev, and percentiles for
            each numeric column.
        """
        ...

    def sortBy_(self, sortColumns: Constant, sortDirections: Constant = DFLT) -> Constant:
        """
        Sorts the table in-place by specified columns and directions.

        For partitioned tables, sorting occurs within each partition independently.
        Parallel processing is used when localExecutors > 0 configuration is enabled.

        Parameters
        ----------
        sortColumns : Constant
            Column name(s) to sort by. Accepts string, list of strings, or meta code
            expression.
        sortDirections : Constant, optional
            Sort order for each column. True/1 for ascending (default), False/0 for
            descending.

        Returns
        -------
        Constant
            The sorted table.
        """
        ...


class Void(Scalar):
    VOID_VALUE: Void
    """
    A void value constant representing no data.
    """
    NULL_VALUE: Void
    """
    A null value constant representing absence of value.
    """
    DFLT_VALUE: Void
    """
    A default value constant for void type.
    """
    def __init__(self) -> None: ...

    def is_nothing(self) -> bool:
        """
        Checks if the current value represents "Nothing".

        This method verifies whether the current instance holds the `VOID_VALUE`,
        which signifies an absence of meaningful data. Typically used to check if an
        argument has been properly provided.

        Returns
        -------
        bool
            True if the current value is `VOID_VALUE`; False otherwise.
        """
        ...

    def is_default(self) -> bool:
        """
        Checks if the current value represents the default value.

        This method verifies whether the current instance holds the `DFLT_VALUE`.

        Returns
        -------
        bool
            True if the current value is DFLT_VALUE, False otherwise.
        """
        ...


class Bool(Scalar):
    """Represents a Swordfish Bool object, initialized optionally with a Python bool value.

    Examples:
        >>> import swordfish as sf
        >>> sf.data.Bool()
        Bool(null)
        >>> sf.data.Bool(True)
        Bool(true)
    """
    NULL_VALUE: Bool

    @overload
    def __init__(self, data: bool) -> None:
        """Initializes Bool with a boolean value."""
        ...

    @overload
    def __init__(self) -> None:
        """Initializes Bool with null value."""
        ...


class Char(Scalar):
    """Represents a Swordfish Char object, initialized optionally with a Python str or int value.

    Examples:
        >>> import swordfish as sf
        >>> sf.data.Char()
        Char(null)
        >>> sf.data.Char('c')
        Char(c)
        >>> sf.data.Char(100)
        Char(d)
    """
    NULL_VALUE: Char

    @overload
    def __init__(self, data: str) -> None:
        """Initializes Char with a string value."""
        ...

    @overload
    def __init__(self, data: int) -> None:
        """Initializes Char with an integer value."""
        ...

    @overload
    def __init__(self) -> None:
        """Initializes Char with null value."""
        ...


class Short(Scalar):
    """Represents a Swordfish Short object, initialized optionally with a Python int value.

    Examples:
        >>> import swordfish as sf
        >>> sf.data.Short()
        Short(null)
        >>> sf.data.Short(28)
        Short(28)
    """
    NULL_VALUE: Short

    @overload
    def __init__(self, data: int) -> None:
        """Initializes Short with an integer value."""
        ...

    @overload
    def __init__(self) -> None:
        """Initializes Short with null value."""
        ...


class Int(Scalar):
    """Represents a Swordfish Int object, initialized optionally with a Python int value.

    Examples:
        >>> import swordfish as sf
        >>> sf.data.Int()
        Int(null)
        >>> sf.data.Int(23)
        Int(23)
    """
    NULL_VALUE: Int

    @overload
    def __init__(self, data: int) -> None:
        """Initializes Int with an integer value."""
        ...

    @overload
    def __init__(self) -> None:
        """Initializes Int with null value."""
        ...


class Long(Scalar):
    """Represents a Swordfish Long object, initialized optionally with a Python int value.

    Examples:
        >>> import swordfish as sf
        >>> sf.data.Long()
        Long(null)
        >>> sf.data.Long(123)
        Long(123)
    """
    NULL_VALUE: Long

    @overload
    def __init__(self, data: int) -> None:
        """Initializes Long with an integer value."""
        ...

    @overload
    def __init__(self) -> None:
        """Initializes Long with null value."""
        ...


class Float(Scalar):
    """
    Represents a Swordfish Float object, initialized optionally with a Python float
    value.

    Parameters
    ----------
    data : float, optional
        A Python float used to initialize the Float object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Float()
    Float(null)
    >>> sf.data.Float(3.14)
    Float(3.14)
    """
    NULL_VALUE: Float

    @overload
    def __init__(self, data: float) -> None:
        """Initialize Float with a float value."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize Float with null value."""
        ...


class Double(Scalar):
    """
    Represents a Swordfish Double object, initialized optionally with a Python float
    value.

    Parameters
    ----------
    data : float, optional
        A Python float used to initialize the Double object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Double()
    Double(null)
    >>> sf.data.Double(3.14)
    Double(3.14)
    """
    NULL_VALUE: Double

    @overload
    def __init__(self, data: float) -> None:
        """Initialize Double with a float value."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize Double with null value."""
        ...


class String(Scalar):
    """
    Represents a Swordfish String object, initialized optionally with a Python str
    value.

    Parameters
    ----------
    data : str, optional
        A Python str used to initialize the String object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.String()
    String(null)
    >>> sf.data.String("hello")
    String(hello)
    """
    NULL_VALUE: String

    @overload
    def __init__(self, data: str) -> None:
        """Initialize String with a string value."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize String with null value."""
        ...


class Blob(Scalar):
    """
    Represents a Swordfish Blob object, initialized optionally with a Python str
    value.

    Parameters
    ----------
    data : str, optional
        A Python str used to initialize the Blob object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Blob()
    Blob(null)
    >>> sf.data.Blob(b"hello")
    Blob(hello)
    """
    NULL_VALUE: Blob

    @overload
    def __init__(self, data: str) -> None:
        """Initialize Blob with a string value."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize Blob with null value."""
        ...


class Date(Scalar):
    """
    Represents a Swordfish Date object, initialized in one of three ways: with no
    arguments, with a Python int value, or with three ints indicating year, month,
    and day.

    Parameters
    ----------
    data : int, optional
        A Python int used to initialize the Date object.
    year : int, optional
        The year component of the Date object.
    month : int, optional
        The month component of the Date object.
    day : int, optional
        The day component of the Date object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Date()
    Date(null)
    >>> sf.data.Date(1)
    Date(1970.01.02)
    >>> sf.data.Date(2000, 1, 1)
    Date(2000.01.01)
    """
    NULL_VALUE: Date

    @overload
    def __init__(self, data: int) -> None:
        """Initialize Date with an integer value."""
        ...

    @overload
    def __init__(self, year: int, month: int, day: int) -> None:
        """Initialize Date with year, month, and day values."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize Date with null value."""
        ...


class Month(Scalar):
    """
    Represents a Swordfish Month object, initialized in one of three ways: with no
    arguments, with a Python int value, or two ints indicating year and month.

    Parameters
    ----------
    data : int, optional
        A Python int used to initialize the Month object.
    year : int, optional
        The year component of the Month object.
    month : int, optional
        The month component of the Month object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Month()
    Month(null)
    >>> sf.data.Month(1)
    Month(0000.02M)
    >>> sf.data.Month(2025, 2)
    Month(2025.02M)
    """
    NULL_VALUE: Month

    @overload
    def __init__(self, data: int) -> None:
        """Initialize Month with an integer value."""
        ...

    @overload
    def __init__(self, year: int, month: int) -> None:
        """Initialize Month with year and month values."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize Month with null value."""
        ...


class Time(Scalar):
    """
    Represents a Swordfish Time object, initialized in one of three ways: with no
    arguments, with a Python int value, or with separate ints indicating hour,
    minute, second, and millisecond.

    Parameters
    ----------
    data : int, optional
        A Python int used to initialize the Time object.
    hour : int, optional
        The hour component of the Time object.
    minute : int, optional
        The minute component of the Time object.
    second : int, optional
        The second component of the Time object.
    millisecond : int, optional
        The millisecond component of the Time object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Time()
    Time(null)
    >>> sf.data.Time(100)
    Time(00:00:00.100)
    >>> sf.data.Time(12, 1, 2, 0)
    Time(12:01:02.000)
    """
    NULL_VALUE: Time

    @overload
    def __init__(self, data: int) -> None:
        """Initialize Time with an integer value."""
        ...

    @overload
    def __init__(self, hour: int, minute: int, second: int, millisecond: int) -> None:
        """Initialize Time with hour, minute, second, and millisecond values."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize Time with null value."""
        ...


class Minute(Scalar):
    """
    Represents a Swordfish Minute object, initialized in one of three ways: with no
    arguments, with a Python int value, or with two ints indicating hour and minute.

    Parameters
    ----------
    data : int, optional
        A Python int used to initialize the Minute object.
    hour : int, optional
        The hour component of the Minute object.
    minute : int, optional
        The minute component of the Minute object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Minute()
    Minute(null)
    >>> sf.data.Minute(20)
    Minute(00:20m)
    >>> sf.data.Minute(11, 50)
    Minute(11:50m)
    """
    NULL_VALUE: Minute

    @overload
    def __init__(self, data: int) -> None:
        """Initialize Minute with an integer value."""
        ...

    @overload
    def __init__(self, hour: int, minute: int) -> None:
        """Initialize Minute with hour and minute values."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize Minute with null value."""
        ...


class Second(Scalar):
    """
    Represents a Swordfish Second object, initialized in one of three ways: with no
    arguments, with a Python int value, or with separate ints indicating hour,
    minute, and second.

    Parameters
    ----------
    data : int, optional
        A Python int used to initialize the Second object.
    hour : int, optional
        The hour component of the Second object.
    minute : int, optional
        The minute component of the Second object.
    second : int, optional
        The second component of the Second object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Second()
    Second(null)
    >>> sf.data.Second(10)
    Second(00:00:10)
    >>> sf.data.Second(10,20,30)
    Second(10:20:30)
    """
    NULL_VALUE: Second

    @overload
    def __init__(self, data: int) -> None:
        """Initialize Second with an integer value."""
        ...

    @overload
    def __init__(self, hour: int, minute: int, second: int) -> None:
        """Initialize Second with hour, minute, and second values."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize Second with null value."""
        ...


class DateTime(Scalar):
    """
    Represents a Swordfish DateTime object, initialized in one of three ways: with no
    arguments, with a Python int value, or with separate ints for year, month, day,
    hour, minute, and second.

    Parameters
    ----------
    data : int, optional
        A Python int used to initialize the DateTime object (e.g., a timestamp).
    year : int, optional
        The year component of the DateTime object.
    month : int, optional
        The month component of the DateTime object.
    day : int, optional
        The day component of the DateTime object.
    hour : int, optional
        The hour component of the DateTime object.
    minute : int, optional
        The minute component of the DateTime object.
    second : int, optional
        The second component of the DateTime object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.DateTime()
    DateTime(null)
    >>> sf.data.DateTime(20)
    DateTime(1970.01.01T00:00:20)
    >>> sf.data.DateTime(2025,1,2,12,0,45)
    DateTime(2025.01.02T12:00:45)
    """
    NULL_VALUE: DateTime

    @overload
    def __init__(self, data: int) -> None:
        """Initialize DateTime with an integer value."""
        ...

    @overload
    def __init__(self, year: int, month: int, day: int, hour: int, minute: int,
                 second: int) -> None:
        """Initialize DateTime with year, month, day, hour, minute, and second values."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize DateTime with null value."""
        ...


class Timestamp(Scalar):
    """
    Represents a Swordfish Timestamp object.

    Parameters
    ----------
    data : int, optional
        A Python int used to initialize the Timestamp object.
    year : int, optional
        The year component of the Timestamp object.
    month : int, optional
        The month component of the Timestamp object.
    day : int, optional
        The day component of the Timestamp object.
    hour : int, optional
        The hour component of the Timestamp object.
    minute : int, optional
        The minute component of the Timestamp object.
    second : int, optional
        The second component of the Timestamp object.
    millisecond : int, optional
        The millisecond component of the Timestamp object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Timestamp()
    Timestamp(null)
    >>> sf.data.Timestamp(0)
    Timestamp(1970.01.01T00:00:00.000)
    >>> sf.data.Timestamp(2025, 1, 1, 12, 0, 20, 0)
    Timestamp(2025.01.01T12:00:20.000)
    """
    NULL_VALUE: Timestamp

    @overload
    def __init__(self, data: int) -> None:
        """Initialize Timestamp with an integer value."""
        ...

    @overload
    def __init__(
        self, year: int, month: int, day: int, hour: int, minute: int, second: int,
        millisecond: int
    ) -> None:
        """Initialize Timestamp with year, month, day, hour, minute, second, and millisecond values."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize Timestamp with null value."""
        ...


class NanoTime(Scalar):
    """
    Represents a Swordfish NanoTime object.

    Parameters
    ----------
    data : int, optional
        A Python int used to initialize the NanoTime object (e.g., a timestamp).
    hour : int, optional
        The hour component of the NanoTime object.
    minute : int, optional
        The minute component of the NanoTime object.
    second : int, optional
        The second component of the NanoTime object.
    nanosecond : int, optional
        The nanosecond component of the NanoTime object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.NanoTime()
    NanoTime(null)
    >>> sf.data.NanoTime(3)
    NanoTime(00:00:00.000000003)
    >>> sf.data.NanoTime(18, 0, 40, 30)
    NanoTime(18:00:40.000000030)
    """
    NULL_VALUE: NanoTime

    @overload
    def __init__(self, data: int) -> None:
        """Initialize NanoTime with an integer value."""
        ...

    @overload
    def __init__(
        self, hour: int, minute: int, second: int, nanosecond: int
    ) -> None:
        """Initialize NanoTime with hour, minute, second, and nanosecond values."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize NanoTime with null value."""
        ...


class NanoTimestamp(Scalar):
    """
    Represents a Swordfish NanoTimestamp object.

    Parameters
    ----------
    data : int, optional
        A Python int used to initialize the NanoTimestamp object (e.g., a timestamp).
    year : int, optional
        The year component of the NanoTimestamp object.
    month : int, optional
        The month component of the NanoTimestamp object.
    day : int, optional
        The day component of the NanoTimestamp object.
    hour : int, optional
        The hour component of the NanoTimestamp object.
    minute : int, optional
        The minute component of the NanoTimestamp object.
    second : int, optional
        The second component of the NanoTimestamp object.
    nanosecond : int, optional
        The nanosecond component of the NanoTimestamp object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.NanoTimestamp()
    NanoTimestamp(null)
    >>> sf.data.NanoTimestamp(15)
    NanoTimestamp(1970.01.01T00:00:00.000000015)
    >>> sf.data.NanoTimestamp(2025, 1, 1, 7, 0, 0, 0)
    NanoTimestamp(2025.01.01T07:00:00.000000000)
    """
    NULL_VALUE: "NanoTimestamp"

    @overload
    def __init__(self, data: int) -> None:
        """Initialize NanoTimestamp with an integer value."""
        ...

    @overload
    def __init__(
        self, year: int, month: int, day: int, hour: int, minute: int, second: int,
        nanosecond: int
    ) -> None:
        """Initialize NanoTimestamp with year, month, day, hour, minute, second, and nanosecond values."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize NanoTimestamp with null value."""
        ...


class DateHour(Scalar):
    """
    Represents a Swordfish DateHour object.

    Parameters
    ----------
    data : int, optional
        A Python int used to initialize the DateHour object.
    year : int, optional
        The year component of the DateHour object.
    month : int, optional
        The month component of the DateHour object.
    day : int, optional
        The day component of the DateHour object.
    hour : int, optional
        The hour component of the DateHour object.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.DateHour()
    DateHour(null)
    >>> sf.data.DateHour(1000)
    DateHour(1970.02.11T16)
    >>> sf.data.DateHour(2025,2,2,9)
    DateHour(2025.02.02T09)
    """
    NULL_VALUE: DateHour

    @overload
    def __init__(self, data: int) -> None:
        """Initialize DateHour with an integer value."""
        ...

    @overload
    def __init__(self, year: int, month: int, day: int, hour: int) -> None:
        """Initialize DateHour with year, month, day, and hour values."""
        ...

    @overload
    def __init__(self) -> None:
        """Initialize DateHour with null value."""
        ...


class Uuid(Scalar):
    """Represents a Swordfish Uuid object."""
    NULL_VALUE: Uuid


class Int128(Scalar):
    """Represents a Swordfish Int128 object."""
    NULL_VALUE: Int128


class Ipaddr(Scalar):
    """Represents a Swordfish Ipaddr object."""
    NULL_VALUE: Ipaddr


class Duration(Scalar):
    """
    Represents a Swordfish Duration object.

    Parameters
    ----------
    data : str
        A Python str used to initialize the Duration object.
    val : int
        The value of the Duration.
    unit : str, optional
        The unit of the Duration. Defaults to "ns".

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Duration("20w")
    Duration(20w)
    >>> sf.data.Duration(3, "m")
    Duration(3m)
    >>> sf.data.Duration(10)
    Duration(10ns)
    """
    NULL_VALUE: Duration

    @overload
    def __init__(self, data: str) -> None:
        """Initialize Duration with a string value."""
        ...

    @overload
    def __init__(self, val: int, unit: str = "ns") -> None:
        """Initialize Duration with value and unit."""
        ...


class Handle(Scalar):
    """Represents a Swordfish Handle object."""


class Resource(Scalar):
    """Represents a Swordfish Resource object."""


class MetaCode(Scalar):
    """
    Represents a Swordfish MetaCode object.
    """

    def eval(self, conn: Connection = None) -> Constant:
        """
        Evaluates the MetaCode.

        Parameters
        ----------
        conn : Connection, optional
            The connection to evaluate this metacode.

        Returns
        -------
        Constant
            The evaluated result of the MetaCode.
        """
        ...


class Decimal32(Scalar):
    """
    Represents a Swordfish Decimal32 object.

    Parameters
    ----------
    data : int or Decimal
        The raw data representation or value of the Decimal32.
    scale : int, optional
        The scale of the Decimal32. Defaults to EXPARAM_DEFAULT.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Decimal32(314, 2)
    Decimal32(3.14, scale=2)
    >>> sf.data.Decimal32(3.141,3)
    Decimal32(3.141, scale=3)
    """
    NULL_VALUE: Decimal32

    @overload
    def __init__(self, data: int, scale: int = EXPARAM_DEFAULT) -> None:
        """Initialize Decimal32 with an integer value and scale."""
        ...

    @overload
    def __init__(self, data: Decimal, scale: int = EXPARAM_DEFAULT) -> None:
        """Initialize Decimal32 with a Decimal value and scale."""
        ...


class Decimal64(Scalar):
    """
    Represents a Swordfish Decimal64 object.

    Parameters
    ----------
    data : int or Decimal
        The raw data representation or value of the Decimal64.
    scale : int, optional
        The scale of the Decimal64. Defaults to EXPARAM_DEFAULT.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Decimal64(12345, 3)
    Decimal64(12.345, scale=3)
    >>> sf.data.Decimal64(3.14,2)
    Decimal64(3.14, scale=2)
    """
    NULL_VALUE: Decimal64

    @overload
    def __init__(self, data: int, scale: int = EXPARAM_DEFAULT) -> None:
        """Initialize Decimal64 with an integer value and scale."""
        ...

    @overload
    def __init__(self, data: Decimal, scale: int = EXPARAM_DEFAULT) -> None:
        """Initialize Decimal64 with a Decimal value and scale."""
        ...


class Decimal128(Scalar):
    """
    Represents a Swordfish Decimal128 object.

    Parameters
    ----------
    data : int or Decimal
        The raw data representation or value of the Decimal128.
    scale : int, optional
        The scale of the Decimal128. Defaults to EXPARAM_DEFAULT.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.data.Decimal128(12345, 6)
    Decimal128(0.012345, scale=6)
    >>> sf.data.Decimal128(3.14,5)
    Decimal128(3.14000, scale=5)
    """
    NULL_VALUE: Decimal128

    @overload
    def __init__(self, data: int, scale: int = EXPARAM_DEFAULT) -> None:
        """Initialize Decimal128 with an integer value and scale."""
        ...

    @overload
    def __init__(self, data: Decimal, scale: int = EXPARAM_DEFAULT) -> None:
        """Initialize Decimal128 with a Decimal value and scale."""
        ...


class Point(Scalar):
    """
    Represents a Swordfish Point object, defined by x and y coordinates.

    Parameters
    ----------
    x : float
        The x-coordinate of the Point.
    y : float
        The y-coordinate of the Point.
    """
    def __init__(self, x: float, y: float) -> None:
        """Initializes Point with x and y coordinates.

        Args:
            x (float): The x-coordinate.
            y (float): The y-coordinate.
        """
        ...


class Unknown(Constant):
    ...


#####################################################################
# Enum Module
#####################################################################


def create_type_enum(type: int, exparam: int) -> DataType: ...


def create_array_type_enum(sub_type: DataType) -> DataType: ...


def create_form_enum(form: int) -> DataForm: ...


ALL: EnumInt
FIRST: EnumInt
LAST: EnumInt
NONE: EnumInt

VOID: DataType
BOOL: DataType
CHAR: DataType
SHORT: DataType
INT: DataType
LONG: DataType
DATE: DataType
MONTH: DataType
TIME: DataType
MINUTE: DataType
SECOND: DataType
DATETIME: DataType
TIMESTAMP: DataType
NANOTIME: DataType
NANOTIMESTAMP: DataType
FLOAT: DataType
DOUBLE: DataType
SYMBOL: DataType
STRING: DataType
UUID: DataType
FUNCTIONDEF: DataType
HANDLE: DataType
CODE: DataType
DATASOURCE: DataType
RESOURCE: DataType
ANY: DataType
DICTIONARY: DataType
DATEHOUR: DataType
IPADDR: DataType
INT128: DataType
BLOB: DataType
COMPLEX: DataType
POINT: DataType
DURATION: DataType
OBJECT: DataType

SCALAR: DataForm
VECTOR: DataForm
PAIR: DataForm
MATRIX: DataForm
SET: DataForm
DICT: DataForm
TABLE: DataForm

VAR: ObjectType
SHARED: ObjectType
DEF: ObjectType

DEBUG: LogLevel
INFO: LogLevel
ERROR: LogLevel
WARNING: LogLevel


#####################################################################
# Exception Module
#####################################################################


class Warning(Exception):
    ...


class Error(Exception):
    ...


class InterfaceError(Error):
    ...


class DatabaseError(Error):
    ...


class DataError(DatabaseError):
    ...


class OperationalError(DatabaseError):
    ...


class IntegrityError(DatabaseError):
    ...


class InternalError(DatabaseError):
    ...


class ProgrammingError(DatabaseError):
    ...


class NotSupportedError(DatabaseError):
    ...


#####################################################################
# IO Module
#####################################################################


def dump(obj: Constant, file: BinaryIO) -> None:
    """
    Serialize a Constant object and write the serialized data to a writable
    BinaryIO object.

    Parameters
    ----------
    obj : Constant
        The object to serialize. Must be a Constant object.
    file : BinaryIO
        A writable BinaryIO object to store the serialized data.
    """
    ...


def load(file: BinaryIO) -> Constant:
    """
    Read serialized data from a readable BinaryIO object and deserialize it into a
    Constant object.

    Parameters
    ----------
    file : BinaryIO
        A readable BinaryIO object.

    Returns
    -------
    Constant
        The deserialized object.
    """
    ...


def dumps(obj: Constant) -> bytes:
    """
    Serialize a Constant object and return the serialized data as bytes.

    Parameters
    ----------
    obj : Constant
        The object to serialize. Must be a Constant object.

    Returns
    -------
    bytes
        The serialized representation of `obj`.
    """
    ...


def loads(data: bytes) -> Constant:
    """
    Deserialize a Constant object from a bytes-like object.

    Parameters
    ----------
    data : bytes
        The serialized data.

    Returns
    -------
    Constant
        The deserialized `Constant` object.
    """
    ...


#####################################################################
# Streaming Engine Module
#####################################################################


class EngineType(Enum):
    """
    Enumeration of streaming engine types in Swordfish.
    """

    StreamBroadcastEngine: int
    TimeSeriesEngine: int
    CrossSectionalEngine: int
    ReactiveStateEngine: int
    StreamFilterEngine: int
    ExtensionEngine: int

    def get_from_str(cls, name: str) -> "EngineType":
        """
        Returns the corresponding EngineType for a given string.

        Parameters
        ----------
        name : str
            String representation of the EngineType.

        Returns
        -------
        EngineType
            Matching EngineType enum member.
        """
        ...


class EngineStat:
    pass


class StreamEngine(Table, abc.ABC):
    """
    Abstract base class representing a streaming engine.

    This class serves as the base for all streaming engine types in Swordfish.
    """

    engine_type: EngineType
    """
    The type of the streaming engine.
    """

    stat: EngineStat
    """
    Descriptive statistics related to the streaming engine.
    """

    @classmethod
    def create(cls, name: str, *args, **kwargs) -> Builder: ...

    @classmethod
    def list(cls) -> List[Tuple[str, EngineType, str]]: ...

    @classmethod
    def get(cls, name: str) -> Self: ...


def _create_engine(engine_type: EngineType, *args) -> StreamEngine: ...


class StreamBroadcastEngineStat(EngineStat):
    user: str
    """
    Name of the user who created the streaming engine.
    """
    status: Literal["OK", "FATAL"]
    """
    Status of the streaming engine. "OK" means available; "FATAL" means unavailable.
    """
    last_err_msg: str
    """
    The latest error message.
    """
    num_groups: int
    """
    The number of groups that the streaming engine has handled.
    """
    num_rows: int
    """
    The number of records that has entered the streaming engine.
    """
    num_metrics: int
    """
    The number of metrics calculated by the streaming engine.
    """
    metrics: str
    """
    The metacode of the metrics calculated by the streaming engine.
    """
    snapshot_dir: str
    """
    The directory to save engine snapshot.
    """
    snapshot_interval: int
    """
    The interval to save snapshot.
    """
    snapshot_msg_id: int
    """
    The msgId of engine snapshot.
    """
    snapshot_timestamp: Timestamp
    """
    The timestamp of snapshot.
    """
    garbage_size: int
    """
    The threshold of the number of records in memory that triggers memory cleaning.
    """
    memory_used: int
    """
    The amount of memory used.
    """


class StreamBroadcastEngine(StreamEngine):
    """
    The stream broadcast engine distributes the same data stream to different target tables.

    Use this engine when you need to process a single stream of data in multiple ways.
    For example, save one copy to disk while sending another copy to a computing engine
    for further processing.

    ``StreamBroadcastEngine.create`` returns a Builder object, and then call submit to
    create an Engine object to which you can ingest the data for stream processing.
    """
    engine_type: EngineType
    stat: StreamBroadcastEngineStat

    @classmethod
    def create(
        cls, name: str, table_schema: Union[Table, TypeDict], outputs: List[Table]
    ) -> StreamBroadcastEngineBuilder:
        """
        Creates a new instance of a StreamBroadcastEngine.

        Parameters
        ----------
        name : str
            The name of the engine. It can have letters, numbers and "_" and must
            start with a letter.
        table_schema : Union[Table, TypeDict]
            Specifies the column names and corresponding types of the input stream.
            If a Table is provided, its schema must match the schema of the subscribed
            stream table. Whether the table contains data or not doesn't matter.
        outputs : List[Table]
            A list of two or more tables. The schema of each table must match
            ``table_schema``.

        Returns
        -------
        StreamBroadcastEngineBuilder
            A builder object to configure and create the StreamBroadcastEngine.

        Examples
        --------
        >>> import swordfish as sf
        >>> table_schema = {"id": "LONG", "name": "STRING"}
        >>> output_table1 = sf.table(types=table_schema)
        >>> output_table2 = sf.table(types=table_schema)
        >>> my_engine = sf.engine.StreamBroadcastEngine.create(
        ...     "MainStreamEngine", table_schema, [output_table1, output_table2]
        ... ).submit()
        """
        ...


class TimeSeriesEngineStat(EngineStat):
    user: str
    """
    Name of the user who created the streaming engine.
    """
    status: Literal["OK", "FATAL"]
    """
    Status of the streaming engine. "OK" means available; "FATAL" means unavailable.
    """
    last_err_msg: str
    """
    The latest error message.
    """
    window_time: str
    """
    The size of the data window.
    """
    step: int
    """
    The duration between 2 adjacent windows.
    """
    use_system_time: bool
    """
    Whether the calculations are performed based on the system time when data is
    ingested into the engine.
    """
    num_groups: int
    """
    The number of groups that the streaming engine has handled.
    """
    num_rows: int
    """
    The number of records that has entered the streaming engine.
    """
    num_metrics: int
    """
    The number of metrics calculated by the streaming engine.
    """
    metrics: str
    """
    The metacode of the metrics calculated by the streaming engine.
    """
    snapshot_dir: str
    """
    The directory to save engine snapshot.
    """
    snapshot_interval: int
    """
    The interval to save snapshot.
    """
    snapshot_msg_id: int
    """
    The msgId of engine snapshot.
    """
    snapshot_timestamp: Timestamp
    """
    The timestamp of snapshot.
    """
    garbage_size: int
    """
    The threshold of the number of records in memory that triggers memory cleaning.
    """
    memory_used: int
    """
    The amount of memory currently used by the engine (in bytes).
    """


class TimeSeriesEngine(StreamEngine):
    """The time-series streaming engine conducts real-time time-series calculations with moving
    windows.

    ``TimeSeriesEngine.create`` returns a Builder object, and then call the submit to create an
    Engine object to which you can ingest the data for stream processing.

    There are two types of aggregate operators in the time-series engine: incremental operators
    and full operators. Incremental operators incrementally aggregate the data as they arrive
    without keeping the historical data. Full operators (e.g., user-defined aggregate functions,
    unoptimized built-in aggregate functions, or functions with nested state functions) keep all
    the data in a window and recompute the output as a full refresh whenever new data arrives.

    The following aggregate operators in the time-series engine are optimized for incremental
    computations: ``corr``, ``covar``, ``first``, ``last``, ``max``, ``med``, ``min``,
    ``percentile``, ``quantile``, ``std``, ``var``, ``sum``, ``sum2``, ``sum3``, ``sum4``,
    ``wavg``, ``wsum``, ``count``, ``firstNot``, ifirstNot, lastNot, ilastNot, imax, imin,
    ``nunique``, ``prod``, ``sem``, ``mode``, ``searchK``, ``beta``, ``avg``.

    **Windowing Logic**

    Window boundaries: The engine automatically adjusts the starting point of the first window.
    (See parameter description for ``step`` and ``round_time``, and the Alignment Rules section).

    Window properties:

    ``window_size`` - the size of each window;
    ``closed`` - whether the left/right boundaries of a window is inclusive/exclusive;
    ``step`` - the duration of time between windows;
    ``use_system_time`` - specifies how values are windowed, which is based on the time column in
    the data or the system time of data ingestion.

    **Calculation Rules**

    - If ``time_col`` is specified, its values must be increasing. If ``key_col`` is specified to
      group the data, the values in ``time_col`` must be increasing with each group specified by
      ``key_col``. Otherwise, out-of-order data will be discarded.
    - If ``use_system_time`` = true, the calculation of a window is triggered as soon as the
      window ends. If ``use_system_time`` = false (with ``time_col`` specified), the calculation
      of a window is triggered by the arrival of the next record after the window ends. To
      trigger the calculation for the uncalculated windows, you can specify the parameter
      ``update_time`` or ``force_trigger_time``.
    - If ``fill`` is unspecified or "None", only windows with calculation results are output. If
      ``fill`` is specified, all windows are output, and the empty windows are filled using the
      specified filling method.
    - If ``update_time`` = 0, incoming records in the current window can be immediately
      calculated and output.

    **Other Features**

    - Data/state cleanup: You can set a cleanup rule to clear historical data. (See parameters
      ``key_purge_filter`` and ``key_purge_freq_in_sec``)
    - Snapshot: Snapshot mechanism is used to restore the streaming engine to the latest
      snapshot after system interruption. (See parameters ``snapshot_dir`` and
      ``snapshot_interval_in_msg_count``)

    **Alignment Rules**

    To facilitate observation and comparison of calculation results, the engine automatically
    adjusts the starting point of the first window. The alignment size (integer) is determined by
    the parameters `step`, `round_time`, and the precision of `time_column`. When the time series
    engine calculates within groups, all groups' windows will be uniformly aligned, and the
    boundaries of each window are the same for each group.

    - Case 1: `time_column` is of type Minute (HH:mm)

      +----------------+-------------------+
      | Range          | alignment_size    |
      +================+===================+
      | 0 ~ 2          | 2                 |
      +----------------+-------------------+
      | 3              | 3                 |
      +----------------+-------------------+
      | 4 ~ 5          | 5                 |
      +----------------+-------------------+
      | 6 ~ 10         | 10                |
      +----------------+-------------------+
      | 11 ~ 15        | 15                |
      +----------------+-------------------+
      | 16 ~ 20        | 20                |
      +----------------+-------------------+
      | 21 ~ 30        | 30                |
      +----------------+-------------------+
      | > 30           | 60 (1 hour)       |
      +----------------+-------------------+

      If `round_time` = True:
        - The value of `alignment_size` is the same as the above table if `step` ≤ 30.
        - If `step` > 30, then:

      +----------------+-------------------+
      | step           | alignment_size    |
      +================+===================+
      | 31 ~ 60        | 60 (1 hour)       |
      +----------------+-------------------+
      | 61 ~ 120       | 120 (2 hours)     |
      +----------------+-------------------+
      | 121 ~ 180      | 180 (3 hours)     |
      +----------------+-------------------+
      | 181 ~ 300      | 300 (5 hours)     |
      +----------------+-------------------+
      | 301 ~ 600      | 600 (10 hours)    |
      +----------------+-------------------+
      | 601 ~ 900      | 900 (15 hours)    |
      +----------------+-------------------+
      | 901 ~ 1200     | 1200 (20 hours)   |
      +----------------+-------------------+
      | 1201 ~ 1800    | 1800 (30 hours)   |
      +----------------+-------------------+
      | > 1800         | 3600 (60 hours)   |
      +----------------+-------------------+

    - Case 2: `time_column` is of type Datetime (yyyy-MM-dd HH:mm:ss) or Second (HH:mm:ss)

      If `round_time` = False:

      +----------------+-------------------+
      | step           | alignment_size    |
      +================+===================+
      | 0 ~ 2          | 2                 |
      +----------------+-------------------+
      | 3              | 3                 |
      +----------------+-------------------+
      | 4 ~ 5          | 5                 |
      +----------------+-------------------+
      | 6 ~ 10         | 10                |
      +----------------+-------------------+
      | 11 ~ 15        | 15                |
      +----------------+-------------------+
      | 16 ~ 20        | 20                |
      +----------------+-------------------+
      | 21 ~ 30        | 30                |
      +----------------+-------------------+
      | > 30           | 60 (1 minute)     |
      +----------------+-------------------+

      If `round_time` = True:
        - The value of `alignment_size` is the same as the above table if `step` ≤ 30.
        - If `step` > 30, then:

      +----------------+-------------------+
      | step           | alignment_size    |
      +================+===================+
      | 31 ~ 60        | 60 (1 minute)     |
      +----------------+-------------------+
      | 61 ~ 120       | 120 (2 minutes)   |
      +----------------+-------------------+
      | 121 ~ 180      | 180 (3 minutes)   |
      +----------------+-------------------+
      | 181 ~ 300      | 300 (5 minutes)   |
      +----------------+-------------------+
      | 301 ~ 600      | 600 (10 minutes)  |
      +----------------+-------------------+
      | 601 ~ 900      | 900 (15 minutes)  |
      +----------------+-------------------+
      | 901 ~ 1200     | 1200 (20 minutes) |
      +----------------+-------------------+
      | 1201 ~ 1800    | 1800 (30 minutes) |
      +----------------+-------------------+
      | > 1800         | 3600 (1 hour)     |
      +----------------+-------------------+

    - Case 3: `time_column` is of type Timestamp (yyyy-MM-dd HH:mm:ss.mmm) or TIME (HH:mm:ss.mmm)

      If `round_time` = False:

      +----------------+-------------------+
      | step           | alignment_size    |
      +================+===================+
      | 0 ~ 2ns        | 2ns               |
      +----------------+-------------------+
      | 3ns ~ 5ns      | 5ns               |
      +----------------+-------------------+
      | 6ns ~ 10ns     | 10ns              |
      +----------------+-------------------+
      | 11ns ~ 20ns    | 20ns              |
      +----------------+-------------------+
      | 21ns ~ 25ns    | 25ns              |
      +----------------+-------------------+
      | 26ns ~ 50ns    | 50ns              |
      +----------------+-------------------+
      | 51ns ~ 100ns   | 100ns             |
      +----------------+-------------------+
      | 101ns ~ 200ns  | 200ns             |
      +----------------+-------------------+
      | 201ns ~ 250ns  | 250ns             |
      +----------------+-------------------+
      | 251ns ~ 500ns  | 500ns             |
      +----------------+-------------------+
      | > 500ns        | 1000ns            |
      +----------------+-------------------+

      If `round_time` = True:
        - The value of `alignment_size` is the same as the above table if `step` ≤ 30000.
        - If `step` > 30000, then:

      +------------------+---------------------+
      | step             | alignment_size      |
      +==================+=====================+
      | 30001 ~ 60000    | 60000 (1 minute)    |
      +------------------+---------------------+
      | 60001 ~ 120000   | 120000 (2 minutes)  |
      +------------------+---------------------+
      | 120001 ~ 300000  | 300000 (5 minutes)  |
      +------------------+---------------------+
      | 300001 ~ 600000  | 600000 (10 minutes) |
      +------------------+---------------------+
      | 600001 ~ 900000  | 900000 (15 minutes) |
      +------------------+---------------------+
      | 900001 ~ 1200000 | 1200000 (20 minutes)|
      +------------------+---------------------+
      | 1200001 ~ 1800000| 1800000 (30 minutes)|
      +------------------+---------------------+
      | > 1800000        | 3600000 (1 hour)    |
      +------------------+---------------------+

    - Case 4: `time_column` is of type Nanotimestamp (yyyy-MM-dd HH:mm:ss.nnnnnnnnn) or NANOTIME
      (HH:mm:ss.nnnnnnnnn)

      If `round_time` = False:

      +----------------+-------------------+
      | step           | alignment_size    |
      +================+===================+
      | 0 ~ 2ns        | 2ns               |
      +----------------+-------------------+
      | 3ns ~ 5ns      | 5ns               |
      +----------------+-------------------+
      | 6ns ~ 10ns     | 10ns              |
      +----------------+-------------------+
      | 11ns ~ 20ns    | 20ns              |
      +----------------+-------------------+
      | 21ns ~ 25ns    | 25ns              |
      +----------------+-------------------+
      | 26ns ~ 50ns    | 50ns              |
      +----------------+-------------------+
      | 51ns ~ 100ns   | 100ns             |
      +----------------+-------------------+
      | 101ns ~ 200ns  | 200ns             |
      +----------------+-------------------+
      | 201ns ~ 250ns  | 250ns             |
      +----------------+-------------------+
      | 251ns ~ 500ns  | 500ns             |
      +----------------+-------------------+
      | > 500ns        | 1000ns            |
      +----------------+-------------------+

      If `round_time` = True:

      +----------------+-------------------+
      | step           | alignment_size    |
      +================+===================+
      | 1000ns ~ 1ms   | 1ms               |
      +----------------+-------------------+
      | 1ms ~ 10ms     | 10ms              |
      +----------------+-------------------+
      | 10ms ~ 100ms   | 100ms             |
      +----------------+-------------------+
      | 100ms ~ 1s     | 1s                |
      +----------------+-------------------+
      | 1s ~ 2s        | 2s                |
      +----------------+-------------------+
      | 2s ~ 3s        | 3s                |
      +----------------+-------------------+
      | 3s ~ 5s        | 5s                |
      +----------------+-------------------+
      | 5s ~ 10s       | 10s               |
      +----------------+-------------------+
      | 10s ~ 15s      | 15s               |
      +----------------+-------------------+
      | 15s ~ 20s      | 20s               |
      +----------------+-------------------+
      | 20s ~ 30s      | 30s               |
      +----------------+-------------------+
      | > 30s          | 1min              |
      +----------------+-------------------+

    If the time of the first record is x with data type of Timestamp, then the starting time of
    the first window is adjusted to be `timeType_cast(x/alignment_size*alignment_size+step-
    window_size)`, where "/" produces only the integer part after division. For example, if the
    time of the first record is 2018.10.08T01:01:01.365, ``window_size`` = 120000, and ``step`` =
    60000, then ``alignment_size`` = 60000, and the starting time of the first window is
    ``timestamp(2018.10.08T01:01:01.365/60000*60000+60000-120000)=2018.10.08T01:01:00.000``.
    """
    engine_type: EngineType
    stat: TimeSeriesEngineStat

    @classmethod
    def create(
        cls, name: str, table_schema: Union[Table, TypeDict], outputs: Table,
        window_size, step, metrics, *,
        time_col: Optional[Union[List[str], str]] = None,
        use_system_time: bool = False,
        key_col: Optional[Union[List[str], str]] = None,
        garbage_size: int = 5000,
        update_time: Optional[int] = None,
        use_window_start_time: bool = False,
        round_time: bool = True,
        snapshot_dir: Optional[Union[Path, str]] = None,
        snapshot_interval_in_msg_count: Optional[int] = None,
        fill: Union[Literal["none", "null", "ffill"], Constant, List[Union[Literal["null", "ffill"], Constant]]] = "none",
        force_trigger_time: Optional[int] = None,
        key_purge_freq_in_sec: Optional[int] = None,
        closed: Literal["left", "right"] = "left",
        output_elapsed_microseconds: bool = False,
        sub_window: Optional[Union[int, Constant]] = None,
        parallelism: int = 1,
        accepted_delay: int = 0,
        output_handler: Optional[FunctionDef] = None,
        msg_as_table: bool = False,
    ) -> TimeSeriesEngineBuilder:
        """
        Creates a time-series streaming engine with the specified parameters.

        Parameters
        ----------
        name : str
            The name of the engine. Can contain letters, numbers, and "_", and must
            start with a letter.
        table_schema : Union[Table, TypeDict]
            Column names and types of the input stream. If a Table is provided,
            its schema must match the subscribed stream table.
        outputs : Table
            The output table for results. Can be in-memory or DFS. Create an empty
            table and specify column names and types before calling `create`.
            Output columns:

            - First column is TIMESTAMP type.

              - If `use_system_time` is True, stores calculation start time.

              - If False, uses `time_col` values.

            - Next column is `context_by_col` (if specified).

            - If `output_elapsed_microseconds` is True, add LONG and INT columns.

            - Remaining columns store metric results. If a metric result is an array vector,
              the output column must be array vector type.

        window_size : int or list of int
            Size(s) of the calculation windows.
        step : int
            Step size for moving windows. Must be divisible by `window_size`.
            Unit depends on `use_system_time`:

            - If True, unit is millisecond.

            - If False, unit matches `time_col`.

        metrics : MetaCode or AnyVector
            Calculation formulas. Can be:

            - Aggregate functions, e.g., `<[sum(qty), avg(price)]>`.

            - Expressions on previous results, e.g., `<[avg(price1)-avg(price2)]>`.

            - Calculations on multiple columns, e.g., `<[std(price1-price2)]>`.

            - Functions with multiple returns, e.g., `<func(price) as `col1`col2>`.

            Column names in `metrics` are not case-sensitive and can differ from
            input table columns. Nested aggregate functions are not supported.
        time_col : Optional[Union[List[str], str]], optional
            Time column(s) for the stream table. Default is None.
        use_system_time : bool, optional
            Whether to use system time for calculations. Default is False.
        key_col : Optional[Union[List[str], str]], optional
            Grouping column(s). Default is None.
        garbage_size : int, optional
            Threshold for garbage collection of historical data. Default is 5000.
        update_time : Optional[int], optional
            Interval to trigger window calculations before window ends. Default is None.
        use_window_start_time : bool, optional
            Whether output table time column uses window start time. Default is False.
        round_time : bool, optional
            Align window boundary by alignment rule. Default is True.
        snapshot_dir : Optional[Union[Path, str]], optional
            Directory to save engine snapshot. Default is None.
        snapshot_interval_in_msg_count : Optional[int], optional
            Number of messages before saving next snapshot. Default is None.
        fill : Union[Literal["none", "null", "ffill"], Constant,
            List[Union[Literal["null", "ffill"], Constant]]], optional
            Filling method(s) for empty windows in a group. Default is "none".
        force_trigger_time : Optional[int], optional
            Waiting time to force trigger calculation in uncalculated windows.
            Default is None.
        key_purge_freq_in_sec : Optional[int], optional
            Interval in seconds to remove inactive groups. Default is None.
        closed : Literal["left", "right"], optional
            Whether left or right boundary is included in window. Default is "left".
        output_elapsed_microseconds : bool, optional
            Whether to output elapsed time (in microseconds). Default is False.
        sub_window : Optional[Union[int, Constant]], optional
            Range of subwindow within window defined by `window_size`. Default is None.
        parallelism : int, optional
            Number of worker threads for parallel computation. Default is 1.
        accepted_delay : int, optional
            Maximum delay for each window to accept data. Default is 0.
        output_handler : Optional[FunctionDef], optional
            Unary or partial function to handle output. If set, engine does not
            write results to output table directly. Default is None.
        msg_as_table : bool, optional
            Whether output data is passed to `output_handler` as table or AnyVector.
            Default is False.

        Returns
        -------
        TimeSeriesEngineBuilder
            Instance for further configuration and execution.

        Examples
        --------
        >>> import swordfish as sf
        >>> table_schema = {"timestamp": "DATETIME", "sensor_id": "LONG",
        ...     "temperature": "DOUBLE", "humidity": "DOUBLE"}
        >>> output_table_1 = sf.table(types={"timestamp": "DATETIME",
        ...     "sensor_id": "LONG", "temperature": "DOUBLE"})
        >>> output_table_2 = sf.table(types={"timestamp": "DATETIME",
        ...     "sensor_id": "LONG", "humidity": "DOUBLE"})
        >>> my_engine = sf.engine.TimeSeriesEngine.create(
        ...     name="SensorTimeSeriesEngine",
        ...     table_schema=table_schema,
        ...     outputs=[output_table_1, output_table_2],
        ...     window_size=5,
        ...     step=1,
        ...     metrics=["temperature", "humidity"],
        ...     time_col="timestamp",
        ...     use_system_time=True,
        ...     key_col="sensor_id",
        ...     garbage_size=5000,
        ...     update_time=1000,
        ...     snapshot_dir="/path/to/snapshot/dir",
        ...     snapshot_interval_in_msg_count=100,
        ...     fill="ffill",
        ...     parallelism=4,
        ...     accepted_delay=10,
        ...     output_handler=None,
        ...     msg_as_table=True,
        ... ).submit()
        """
        ...


class CrossSectionalEngineStat(EngineStat):
    user: str
    """
    Name of the user who created the streaming engine.
    """
    status: Literal["OK", "FATAL"]
    """
    Status of the streaming engine. "OK" means available; "FATAL" means unavailable.
    """
    last_err_msg: str
    """
    The latest error message from the engine.
    """
    num_rows: int
    """
    The number of records that has entered the streaming engine.
    """
    num_metrics: int
    """
    The number of metrics calculated by the streaming engine.
    """
    metrics: str
    """
    The metacode of the metrics calculated by the streaming engine.
    """
    triggering_pattern: str
    """
    How calculations are triggered in the engine.
    """
    triggering_interval: int
    """
    The duration in milliseconds between 2 adjacent calculations.
    """
    snapshot_dir: str
    """
    The directory where engine snapshots are saved.
    """
    snapshot_interval: int
    """
    The interval at which to save snapshots.
    """
    snapshot_msg_id: int
    """
    The message ID of the engine snapshot.
    """
    snapshot_timestamp: Timestamp
    """
    The timestamp when the snapshot was created.
    """
    memory_used: int
    """
    The amount of memory currently used by the engine (in bytes).
    """


class CrossSectionalEngine(StreamEngine):
    """
    The cross-sectional streaming engine is used for real-time computing on
    cross-sectional data, which is a collection of observations (behaviors) for
    multiple subjects (entities such as different stocks) at a single point in time.

    ``CrossSectionalEngine.create`` returns a Builder object, and then call the
    submit to create a keyed table object with the `key_col` parameter as the key.
    The keyed table is updated every time a new record arrives. If the
    `last_batch_only` parameter is set to True, the table only maintains the latest
    record in each group. When new data is ingested into the engine:

    - If `metrics` and `output` are specified, the engine first updates the keyed
      table, then performs calculations on the latest data and outputs the results
      to `output`.

    - If `metrics` and `output` are not specified, the engine only updates the keyed
      table.

    Calculation can be triggered by the number of records or time interval. See
    ``create`` parameters `triggering_pattern` and `triggering_interval`. Note that
    if `context_by_col` is specified, the data will be grouped by the specified
    columns and calculated by group.

    Snapshot mechanism is used to restore the streaming engine to the latest
    snapshot after system interruption. (See ``create`` parameters `snapshot_dir`
    and `snapshot_interval_in_msg_count`)
    """
    engine_type: EngineType
    stat: CrossSectionalEngineStat

    @classmethod
    def create(
        cls, name: str, table_schema: Union[Table, TypeDict],
        key_col: Union[List[str], str],
        *,
        metrics=None,
        output: Table = None,
        triggering_pattern: Literal["per_batch", "per_row", "interval", "key_count",
                                    "data_interval"] = "per_batch",
        triggering_interval: Any = None,
        use_system_time: bool = True,
        time_col: Optional[str] = None,
        last_batch_only: bool = False,
        context_by_col: Optional[Union[List[str], str]] = None,
        snapshot_dir: Optional[Union[Path, str]] = None,
        snapshot_interval_in_msg_count: Optional[int] = None,
        output_elapsed_microseconds: bool = False,
        round_time: bool = True,
        key_filter: Optional[MetaCode] = None,
        updated_context_groups_only: bool = False,
    ) -> CrossSectionalEngineBuilder:
        """
        Creates a cross-sectional streaming engine with the specified parameters and
        configuration.

        Parameters
        ----------
        name : str
            The name of the engine. It can contain letters, numbers and "_" and must
            start with a letter.
        table_schema : Union[Table, TypeDict]
            Specifies the column names and corresponding types of the input stream.
            If a Table is provided, its schema must match the schema of the subscribed
            stream table. Whether the table contains data or not doesn't matter.
        key_col : Union[List[str], str]
            One or more columns in the stream table as the key columns. For each key
            entry, only the latest record is used in the calculation.
        metrics : optional
            The formulas for calculation using MetaCode or an AnyVector. Defaults to
            None.
        output : Table
            The output table for the results. It can be an in-memory table or a DFS
            table. Create an empty table and specify the column names and types before
            calling `create`. Make sure the column types match the calculation results
            of the corresponding metrics. The columns in the output table are in the
            following order:

            - The first column is of TIMESTAMP type.

              - If ``use_system_time`` = True, the column stores the time when each
                calculation starts.

              - If ``use_system_time`` = False, it takes the values of ``time_col``.

            - The following column is the ``context_by_col`` (if specified).

            - If the ``output_elapsed_microseconds`` is set to True, specify two more
              columns: a LONG column and an INT column.

            - The remaining columns store the calculation results of metrics.

        triggering_pattern : Literal["per_batch", "per_row", "interval", "key_count", "data_interval"], optional
            Specifies how to trigger the calculations.
        triggering_interval : Any, optional
            The triggering interval for the system based on the triggering pattern.
            Defaults to None.
        use_system_time : bool, optional
            Whether the calculations are performed based on the system time when data
            is ingested into the engine. Defaults to True.
        time_col : Optional[str], optional
            The time column in the stream table to which the engine subscribes if
            ``use_system_time`` = False. Defaults to None.
        last_batch_only : bool, optional
            Whether to keep only the records with the latest timestamp in the engine.
            Defaults to False.
        context_by_col : Optional[Union[List[str], str]], optional
            The grouping column(s) by which calculations are performed within groups.
            Only takes effect if `metrics` and `output` are specified. Defaults to None.
        snapshot_dir : Optional[Union[Path, str]], optional
            The directory where the streaming engine snapshot is saved. Defaults to None.
        snapshot_interval_in_msg_count : Optional[int], optional
            The number of messages to receive before saving the next snapshot. Defaults
            to None.
        output_elapsed_microseconds : bool, optional
            Whether to output the elapsed time (in microseconds). Defaults to False.
        round_time : bool, optional
            Aligns the window boundary based on the specified alignment rule. Defaults
            to True.
        key_filter : Optional[MetaCode], optional
            The conditions for filtering keys in the keyed table returned by the engine.
            Defaults to None.
        updated_context_groups_only : bool, optional
            Whether to compute only the groups updated with new data since the last
            output. Defaults to False.

        Returns
        -------
        CrossSectionalEngineBuilder
            An instance of ``CrossSectionalEngineBuilder`` that allows further
            configuration and execution of the cross-sectional engine. This object
            enables setting up the opional parameters.

        Examples
        --------
        >>> import swordfish as sf
        >>> table_schema = {"timestamp": "DATETIME", "symbol": "STRING", "price":
        ...     "DOUBLE", "volume": "LONG"}
        >>> output_table = sf.table(types={"symbol": "STRING", "avg_price": "DOUBLE",
        ...     "total_volume": "LONG"})
        >>> my_engine = sf.engine.CrossSectionalEngine.create(
        ...     name="StockAnalysisEngine",
        ...     table_schema=table_schema,
        ...     key_col="symbol",
        ...     metrics=["avg(price)", "sum(volume)"],
        ...     output=output_table,
        ...     triggering_pattern="interval",
        ...     triggering_interval=10,
        ...     use_system_time=True,
        ...     time_col="timestamp",
        ...     last_batch_only=False,
        ...     snapshot_dir="/path/to/snapshot",
        ...     snapshot_interval_in_msg_count=1000,
        ...     round_time=True,
        ...     updated_context_groups_only=True
        ... ).submit()
        """
        ...


class ReactiveStateEngineStat(EngineStat):
    user: str
    """
    Name of the user who created the streaming engine.
    """
    status: Literal["OK", "FATAL"]
    """
    Status of the streaming engine. "OK" means available; "FATAL" means unavailable.
    """
    last_err_msg: str
    """
    The latest error message from the engine.
    """
    num_groups: int
    """
    The number of groups that the streaming engine has handled.
    """
    num_rows: int
    """
    The number of records that has entered the streaming engine.
    """
    num_metrics: int
    """
    The number of metrics calculated by the streaming engine.
    """
    snapshot_dir: str
    """
    The directory where engine snapshots are saved.
    """
    snapshot_interval: int
    """
    The interval at which to save snapshots.
    """
    snapshot_msg_id: int
    """
    The message ID of the engine snapshot.
    """
    snapshot_timestamp: Timestamp
    """
    The timestamp when the snapshot was created.
    """
    memory_used: int
    """
    The amount of memory currently used by the engine (in bytes).
    """


class ReactiveStateEngine(StreamEngine):
    """
    The reactive state streaming engine maintains and updates states for stateful
    computations, ensuring efficient processing of continuous data streams. It
    triggers an output for each input record, supports only vectorized functions
    as operators, and optimizes stateful operations.

    .. note::
        Only the following optimized state functions can be used in the engine.
        Alternatively, you can implement a stateful indicator by defining a user-
        defined function and declaring it with keyword @state before the definition.
        Aggregate functions should be avoided.

    Cumulative functions: `cumavg`, `cumsum`, `cumprod`, `cumcount`, `cummin`,
    `cummax`, `cumvar`, `cumvarp`, `cumstd`, `cumstdp`, `cumcorr`, `cumcovar`,
    `cumbeta`, `cumwsum`, `cumwavg`, `cumfirstNot`, `cumlastNot`, `cummed`,
    `cumpercentile`, `cumnunique`, `cumPositiveStreak`, `cummdd`

    Moving functions: `ema`, `mavg`, `msum`, `mcount`, `mprod`, `mvar`, `mvarp`,
    `mstd`, `mstdp`, `mskew`, `mkurtosis`, `mmin`, `mmax`, `mimin`, `mimax`,
    `mmed`, `mpercentile`, `mrank`, `mcorr`, `mcovar`, `mbeta`, `mwsum`,
    `mwavg`, `mmad`, `mfirst`, `mlast`, `mslr`, `tmove`, `tmfirst`, `tmlast`,
    `tmsum`, `tmavg`, `tmcount`, `tmvar`, `tmvarp`, `tmstd`, `tmstdp`,
    `tmprod`, `tmskew`, `tmkurtosis`, `tmmin`, `tmmax`, `tmmed`,
    `tmpercentile`, `tmrank`, `tmcovar`, `tmbeta`, `tmcorr`, `tmwavg`,
    `tmwsum`, `tmoving`, `moving`, `sma`, `wma`, `dema`, `tema`, `trima`,
    `linearTimeTrend`, `talib`, `t3`, `ma`, `mmaxPositiveStreak`

    .. note::
        If `talib` is used as a state function, its first parameter must be a state
        function.

    Row-based functions: `rowMin`, `rowMax`, `rowAnd`, `rowOr`, `rowXor`,
    `rowProd`, `rowSum`, `rowSum2`, `rowSize`, `rowCount`, `rowAvg`,
    `rowKurtosis`, `rowSkew`, `rowVar`, `rowVarp`, `rowStd`, `rowStdp`

    Order-sensitive functions: `deltas`, `ratios`, `ffill`, `move`, `prev`,
    `iterate`, `ewmMean`, `ewmVar`, `ewmStd`, `ewmCov`, `ewmCorr`,
    `prevState`, `percentChange`

    TopN functions: `msumTopN`, `mavgTopN`, `mstdpTopN`, `mstdTopN`,
    `mvarpTopN`, `mvarTopN`, `mcorrTopN`, `mbetaTopN`, `mcovarTopN`,
    `mwsumTopN`, `cumwsumTopN`, `cumsumTopN`, `cumvarTopN`, `cumvarpTopN`,
    `cumstdTopN`, `cumstdpTopN`, `cumcorrTopN`, `cumbetaTopN`, `cumavgTopN`,
    `cumskewTopN`, `cumkurtosisTopN`, `mskewTopN`, `mkurtosisTopN`,
    `tmsumTopN`, `tmavgTopN`, `tmstdTopN`, `tmstdpTopN`, `tmvarTopN`,
    `tmvarpTopN`, `tmskewTopN`, `tmkurtosisTopN`, `tmbetaTopN`, `tmcorrTopN`,
    `tmcovarTopN`, `tmwsumTopN`

    Higher-order functions: `segmentby` (whose first parameter can only take
    `cumsum`, `cummax`, `cummin`, `cumcount`, `cumavg`, `cumstd`, `cumvar`,
    `cumstdp`, `cumvarp`), `moving`, `byColumn`, `accumulate`, `window`

    Others: `talibNull`, `topRange`, `lowRange`, `trueRange`

    Functions that can only be used in the reactive state engine:
    `stateIterate`, `conditionalIterate`, `genericStateIterate`,
    `genericTStateIterate`

    Calculation Rules
    -----------------
    The reactive state engine outputs a result for each input. If multiple
    records are ingested into the reactive state engine at the same time, the
    data is calculated in batches. The number of records in each batch is
    determined by the system.

    - To output only the results that met the specified conditions, set the
      parameter `filter`.
    - To perform calculations by group, set the parameter `key_col`.
    - To preserve the insertion order of the records in the output table, set
      the parameter `keep_order`.

    Features
    --------
    - State cleanup: States in the engine are maintained by group. A large
      number of groups may lead to high memory overhead, and you can set a
      cleanup rule to clear data that are no longer needed. (See parameters
      `key_purge_filter` and `key_purge_fre_in_second`)
    - Snapshot: Snapshot mechanism is used to restore the streaming engine to
      the latest snapshot after system interruption. (See parameters
      `snapshot_dir` and `snapshot_interval_in_msg_count`)
    """
    engine_type: EngineType
    stat: ReactiveStateEngineStat

    @classmethod
    def create(
        cls, name: str, table_schema: Union[Table, TypeDict],
        output: Table, metrics,
        *,
        key_col: Optional[Union[List[str], str]] = None,
        filter: Optional[MetaCode] = None,
        snapshot_dir: Optional[Union[Path, str]] = None,
        snapshot_interval_in_msg_count: Optional[int] = None,
        keep_order: Optional[bool] = None,
        key_purge_filter: Optional[MetaCode] = None,
        key_purge_freq_in_second: Optional[int] = None,
        output_elapsed_microseconds: bool = False,
        key_capacity: int = 1024,
        parallelism: int = 1,
        output_handler: Optional[FunctionDef] = None,
        msg_as_table: bool = False,
    ) -> ReactiveStateEngineBuilder:
        """
        Creates a reactive state streaming engine with the specified parameters
        and configuration.

        Parameters
        ----------
        name : str
            The name of the engine. It can contain letters, numbers and "_" and
            must start with a letter.
        table_schema : Union[Table, TypeDict]
            Specifies the column names and corresponding types of the input
            stream. If a Table is provided, its schema must match the schema of
            the subscribed stream table. Whether the table contains data or not
            doesn't matter.
        output : Table
            The output table for the results. It can be an in-memory table or a
            DFS table. Create an empty table and specify the column names and
            types before calling `create`. The columns in the output table are
            in the following order: (1) If `key_col` is specified, the first few
            columns must match its order. (2) If `output_elapsed_microseconds`
            is set to True, specify two more columns: a LONG column for elapsed
            time of each batch and an INT column for total records in each
            batch. (3) The remaining columns store the calculation results of
            metrics. Make sure the column types match the calculation results of
            the corresponding metrics.
        metrics
            MetaCode specifying the formulas for calculation. The metacode can
            include one or more expressions, built-in or user-defined functions,
            or a constant scalar/vector. Note that the output column for a
            constant vector must be in array vector form.
        key_col : Optional[Union[List[str], str]], optional
            The grouping column(s) for the calculation. Defaults to None.
        filter : Optional[MetaCode], optional
            The filtering conditions for the output table. Defaults to None.
        snapshot_dir : Optional[Union[Path, str]], optional
            The directory where the streaming engine snapshot is saved. Defaults
            to None.
        snapshot_interval_in_msg_count : Optional[int], optional
            The number of messages to receive before saving the next snapshot.
            Defaults to None.
        keep_order : Optional[bool], optional
            Whether to preserve the insertion order of records in the output
            table. Defaults to None.
        key_purge_filter : Optional[MetaCode], optional
            The filtering conditions to identify the data to be purged from the
            cache. Defaults to None.
        key_purge_freq_in_second : Optional[int], optional
            The time interval (in seconds) to trigger a purge. Defaults to None.
        output_elapsed_microseconds : bool, optional
            Whether to output the elapsed time (in microseconds). Defaults to
            False.
        key_capacity : int, optional
            A positive integer indicating the amount of memory allocated for
            buffering state of each group. Defaults to 1024.
        parallelism : int, optional
            A positive integer no greater than 63, indicating the maximum number
            of workers that can run in parallel. Defaults to 1.
        output_handler : Optional[FunctionDef], optional
            A unary function or a partial function with a single unfixed
            parameter. If set, the engine will not write the calculation results
            to the output table directly. Instead, the results will be passed as
            a parameter to the specified function. Defaults to None.
        msg_as_table : bool, optional
            Whether the output data is passed into the function (specified by
            `output_handler`) as a table or as an AnyVector. Defaults to False.

        Returns
        -------
        ReactiveStateEngineBuilder
            An instance of `ReactiveStateEngineBuilder` that allows further
            configuration and execution of the reactive state engine. This
            object enables setting up the optional parameters.

        Examples
        --------
        >>> import swordfish as sf
        >>> table_schema = {"timestamp": "DATETIME", "device_id": "STRING",
        ...     "temperature": "DOUBLE", "status": "STRING"}
        >>> output_table = sf.table(types={"device_id": "STRING",
        ...     "max_temperature": "DOUBLE", "last_status": "STRING"})
        >>> my_engine = sf.engine.ReactiveStateEngine.create(
        ...     name="DeviceStateTracker",
        ...     table_schema=table_schema,
        ...     output=output_table,
        ...     metrics=["max(temperature)", "last(status)"],
        ...     key_col="device_id",
        ...     filter=None,
        ...     snapshot_dir="/path/to/snapshot",
        ...     snapshot_interval_in_msg_count=1000,
        ...     keep_order=True,
        ...     key_purge_filter=None,
        ...     key_purge_freq_in_second=60,
        ...     key_capacity=4096,
        ...     parallelism=2,
        ...     output_handler=None,
        ...     msg_as_table=True,
        ... ).submit()
        """
        ...


class StreamFilterEngineStat(EngineStat):
    user: str
    """
    Name of the user who created the streaming engine.
    """

    status: Literal["OK", "FATAL"]
    """
    Status of the streaming engine. "OK" means available; "FATAL" means unavailable.
    """

    last_err_msg: str
    """
    The latest error message from the engine.
    """

    num_rows: int
    """
    The number of records that has entered the streaming engine.
    """

    filters: str
    """
    The metacode of the filters used by the streaming engine.
    """


filter_dict = Dict[Literal["timeRange", "condition", "handler"], Any]


class StreamFilterEngine(StreamEngine):
    engine_type: EngineType
    stat: StreamFilterEngineStat

    @classmethod
    def create(
        cls, name: str, table_schema: Union[Table, TypeDict],
        filter: Union[filter_dict, List[filter_dict]],
        *,
        msg_schema: Optional[Dict] = None,
        time_col: Optional[str] = None,
        condition_col: Optional[str] = None,
    ) -> StreamFilterEngineBuilder:
        ...


#####################################################################
# Storage Module
#####################################################################


class StorageType(Enum):
    """
    Swordfish provides the following storage engines.

    OLAP
    ----
    Well-suited for large-scale data analysis (e.g., querying trading volumes
    for all stocks in a specific time period). The OLAP engine utilizes data
    partitioning to horizontally divide large datasets into multiple
    partitions based on specified rules. Within each partition, the engine
    employs columnar storage for data management. Data partitioning allows
    for selective column access, reducing unnecessary I/O operations and
    significantly enhancing query performance.

    TSDB
    ----
    Implemented based on the LSM-Tree (Log Structured Merge Tree) model. The
    TSDB engine is optimized for handling time-series data, providing
    improved performance and efficiency in data storage, retrieval, and
    analysis.

    PKEY
    ----
    Designed to store data with a unique identifier for each record within a
    table. The PKEY engine enables faster sorting, searching, and querying
    operations. It is suitable for real-time updates and efficient queries
    (e.g., real-time data analysis through CDC integration with OLTP
    systems).
    """
    OLAP: "StorageType" = 0
    OLTP: "StorageType" = 1
    TSDB: "StorageType" = 2
    PKEY: "StorageType" = 4


class OLTPConnectionImpl(BaseConnectionImpl):
    @classmethod
    def connect(cls, url: str, option: dict) -> "OLTPConnectionImpl": ...

    def begin_transaction(self): ...
    def check_transaction(self): ...
    def commit(self): ...
    def rollback(self): ...

    def create_table(self, name: str, **kwargs): ...
    def drop_table(self, name: str): ...
    def list_table(self): ...
    def exists_table(self, name: str) -> bool: ...
    def get_table(self, name: str): ...


class SchemaImpl:
    def create_partitioned_table(self, *args) -> Table: ...
    def create_dimension_table(self, *args) -> Table: ...
    def list_table(self) -> List[str]: ...
    def exists_table(self, name: str) -> bool: ...
    def drop_table(self, name: str): ...
    def truncate_table(self, name: str): ...
    def get_table(self, name: str) -> Table: ...
    def get_engine_type(self) -> StorageType: ...
    def get_handle(self) -> Handle: ...


class CatalogConnectionImpl(BaseConnectionImpl):
    @classmethod
    def connect(cls, catalog: str) -> "CatalogConnectionImpl": ...

    def create_schema(self, **kwargs) -> SchemaImpl: ...
    def list_schema(self) -> List[str]: ...
    def exists_schema(self, name: str) -> bool: ...
    def drop_schema(self, name: str): ...
    def get_schema(self, name: str) -> SchemaImpl: ...


#####################################################################
# Streaming Module
#####################################################################


class PersistenceMetaInfo:
    size_in_memory: int
    """
    The number of records currently stored in memory.
    """

    asyn_write: bool
    """
    Whether data is persisted to disk in asynchronous mode.
    """

    total_size: int
    """
    The total number of records in the stream table.
    """

    compress: bool
    """
    Whether data is stored in compression mode.
    """

    memory_offset: int
    """
    The offset position of the first message in memory relative to all records in
    the stream table.
    """

    size_on_disk: int
    """
    The number of records that have been persisted to disk.
    """

    retention_minutes: int
    """
    How long (in minutes) the log file will be retained.
    """

    persistence_dir: str
    """
    The directory path where persistent data is stored.
    """

    hash_value: int
    """
    The identifier of the thread responsible for persisting the table to disk.
    """

    disk_offset: int
    """
    The offset position of the first message on disk relative to all records in
    the stream table.
    """


class StreamTableInfo:
    cache_size: int
    """
    When cache is purged by size, the threshold for the number of records to be
    retained in memory is determined based on ``cache_size``.
    """

    cache_purge_time_column: Optional[str]
    """
    The time column in the stream table. When cache is purged by time, it will be
    conducted based on this column.
    """

    cache_purge_interval: Duration
    """
    The interval to trigger a purge when cache is purged by time.
    """

    cache_retention_time: Duration
    """
    The retention time of cached data when cache is purged by time.
    """

    rows_in_memory: int
    """
    The number of rows currently stored in memory.
    """

    total_rows: int
    """
    The total number of rows in the stream table.
    """

    memory_used: int
    """
    Memory used by the stream table (in bytes).
    """


class StreamTable(Table):
    """
    Stream tables are tables that support real-time data ingestion
    """
    @overload
    def enable_persistence(
        self, *,
        asyn_write: bool = True,
        compress: bool = True,
        cache_size: Optional[int] = None,
        retention_minutes: int = 1440,
        flush_mode: Literal["async", "sync"] = "async",
        pre_cache: Optional[int] = None,
    ) -> Self:
        ...

    @overload
    def enable_persistence(
        self, *,
        asyn_write: bool = True,
        compress: bool = True,
        retention_minutes: int = 1440,
        flush_mode: Literal["async", "sync"] = "async",
        pre_cache: Optional[int] = None,
        cache_purge_time_column: Optional[str] = None,
        cache_purge_interval: Optional[Duration] = None,
        cache_retention_time: Optional[Duration] = None,
    ) -> Self:
        ...

    def enable_persistence(
        self, *,
        asyn_write: bool = True,
        compress: bool = True,
        cache_size: Optional[int] = None,
        retention_minutes: int = 1440,
        flush_mode: Literal["async", "sync"] = "async",
        pre_cache: Optional[int] = None,
        cache_purge_time_column: Optional[str] = None,
        cache_purge_interval: Optional[Duration] = None,
        cache_retention_time: Optional[Duration] = None,
    ) -> Self:
        """
        Enables persistence for the stream table, allowing different configurations for
        cache purge.

        **Prerequisites**

        To enable persistence, specify the ``persistenceDir`` configuration. The
        persistence location of the table is ``<PERSISTENCE_DIR>/<TABLE_NAME>``. The
        directory contains data files (named like ``data0.log``, ``data1.log``...) and an
        index file ``index.log``. The data that has been persisted to disk will be loaded
        into memory after Swordfish is restarted.

        **Persistence Modes**

        The parameter ``asyn_write`` informs the system whether table persistence is in
        asynchronous mode. With asynchronous mode (default), new data are pushed to a
        queue and persistence threads will write the data to disk later. With synchronous
        mode, the table append operation keeps running until new data are persisted to the
        disk. In general, asynchronous mode achieves higher throughput.

        With asynchronous mode, table persistence is conducted by a single persistence
        thread, and the persistence thread may handle multiple tables. If there is only
        one table to be persisted, an increase in the number of persistence threads
        doesn't improve performance.

        Note that if asynchronous mode is enabled for data persistence or flush, data
        loss may occur due to server crash.

        **Cache Purge Settings**

        Stream tables keep all data in memory by default. To prevent excessive memory
        usage, you can clear cached data using either of the following methods:

        - Cache purge by size: Set ``cache_size`` to specify a threshold for the number
          of records retained. Older records exceeding the threshold will be removed.
          The threshold is determined as follows:

          - If the number of records appended in one batch does not exceed
            ``cache_size``, the threshold is 2.5 * ``cache_size``.

          - If the number of records appended in one batch exceeds ``cache_size``, the
            threshold is 1.2 * (appended records + ``cache_size``).

        - Cache purge by time: Set ``cache_purge_time_column``, ``cache_purge_interval``
          and ``cache_retention_time``. The system will clean up data based on the
          ``cache_purge_time_column``. Each time when a new record arrives, the system
          obtains the time difference between the new record and the oldest record kept
          in memory. If the time difference exceeds ``cache_purge_interval``, the system
          will retain only the data with timestamps within ``cache_retention_time`` of
          the new data.


        Parameters
        ----------
        asyn_write : bool, optional
            Whether to enable asynchronous writes. Defaults to True.
        compress : bool, optional
            Whether to save a table to disk in compression mode. Defaults to True.
        cache_size : Optional[int], optional
            Used to determine the maximum number of records to retain in memory.
            Defaults to None.
        retention_minutes : int, optional
            For how long (in minutes) a log file larger than 1GB will be kept after
            the last update. Defaults to 1440.
        flush_mode : {'async', 'sync'}, optional
            Whether to enable synchronous disk flush. Defaults to "async".
        pre_cache : Optional[int], optional
            The number of records to be loaded into memory from the persisted stream
            table on disk when Swordfish is initialized. Defaults to None.
        cache_purge_time_column : Optional[str], optional
            The time column in the stream table. Defaults to None.
        cache_purge_interval : Optional[Duration], optional
            The interval to trigger cache purge. Defaults to None.
        cache_retention_time : Optional[Duration], optional
            The retention time of cached data. Must be smaller than
            ``cache_purge_interval``. Defaults to None.

        Returns
        -------
        Self
            The StreamTable with persistence enabled.

        Examples
        --------
        Enable persistence and set cache purge by size:
            >>> import swordfish as sf
            >>> table = sf.streaming.table(names=["id", "name", "age", "created_at"],
            ...     types=["INT", "STRING", "INT", "TIMESTAMP"], size=0, capacity=10)
            >>> table.share("my_table")
            >>> table.enable_persistence(
            ...     asyn_write=True,
            ...     compress=False,
            ...     cache_size=1024,
            ...     retention_minutes=720,
            ...     flush_mode="sync",
            ...     pre_cache=100,
            ... )
        Enable persistence and set cache purge by time:
            >>> table.enable_persistence(
            ...     asyn_write=True,
            ...     compress=False,
            ...     retention_minutes=720,
            ...     flush_mode="sync",
            ...     pre_cache=100,
            ...     cache_purge_time_column="created_at",
            ...     cache_purge_interval=sf.data.Duration("2H"),
            ...     cache_retention_time=sf.data.Duration("10m"),
            ... )
        """
        ...

    @overload
    def enable_cache_purge(
        self, *,
        cache_size: Optional[int] = None,
    ) -> Self:
        ...

    @overload
    def enable_cache_purge(
        self, *,
        cache_purge_time_column: Optional[str] = None,
        cache_purge_interval: Optional[Duration] = None,
        cache_retention_time: Optional[Duration] = None,
    ) -> Self:
        ...

    def enable_cache_purge(
        self, *,
        cache_size: Optional[int] = None,
        cache_purge_time_column: Optional[str] = None,
        cache_purge_interval: Optional[Duration] = None,
        cache_retention_time: Optional[Duration] = None,
    ) -> Self:
        """
        Enables cache purge for a non-persisted stream table.

        To prevent excessive memory usage, you can clear cached data using either of the
        following methods:

        - Cache purge by size: Set ``cache_size`` to specify a threshold for the number
          of records retained. Older records exceeding the threshold will be removed.
          The threshold is determined as follows:

          - If the number of records appended in one batch does not exceed
            ``cache_size``, the threshold is 2.5 * ``cache_size``.

          - If the number of records appended in one batch exceeds ``cache_size``, the
            threshold is 1.2 * (appended records + ``cache_size``).

        - Cache purge by time: Set ``cache_purge_time_column``, ``cache_purge_interval``
          and ``cache_retention_time``. The system will clean up data based on the
          ``cache_purge_time_column``. Each time when a new record arrives, the system
          obtains the time difference between the new record and the oldest record kept
          in memory. If the time difference exceeds ``cache_purge_interval``, the system
          will retain only the data with timestamps within ``cache_retention_time`` of
          the new data.

        .. note::
            If a record has not been enqueued for publishing, it will not be removed.

        Parameters
        ----------
        cache_size : Optional[int], optional
            Used to determine the maximum number of records to retain in memory.
            Defaults to None.
        cache_purge_time_column : Optional[str], optional
            The time column in the stream table. Defaults to None.
        cache_purge_interval : Optional[Duration], optional
            The interval to trigger cache purge. Defaults to None.
        cache_retention_time : Optional[Duration], optional
            The retention time of cached data. Must be smaller than
            ``cache_purge_interval``. Defaults to None.

        Returns
        -------
        Self
            The StreamTable with cache purge enabled.

        Examples
        --------
        Cache purge by size:
            >>> table.enable_cache_purge(cache_size=1024)
        Cache purge by time:
            >>> table.enable_cache_purge(
            ...     cache_purge_time_column="created_at",
            ...     cache_purge_interval=sf.data.Duration("2H"),
            ...     cache_retention_time=sf.data.Duration("10m")
            ... )
        """
        ...

    def disable_persistence(self) -> Self:
        """
        Disable the table's persistence to disk. Any future update of the table will not
        be persisted to disk.

        Returns
        -------
        Self
            Return the current table instance.

        Examples
        --------
        >>> table.disable_persistence()
        """
        ...

    def clear_persistence(self) -> Self:
        """
        Stop the table's persistence to disk, and delete the contents of the table on disk
        while the table schema remains.

        Returns
        -------
        Self
            Return the current table instance.

        Examples
        --------
        >>> table.clear_persistence()
        """
        ...

    def set_timestamp_column(self, name: str) -> Self:
        """
        Set the timestamp column in the table.

        Parameters
        ----------
        name : str
            The name of the column to be set as the timestamp column.

        Returns
        -------
        Self
            Return the current table instance.

        Examples
        --------
        >>> table.set_timestamp_column("column_name")
        """
        ...

    def set_filter_column(self, name: str) -> Self:
        """
        Set the filter column in the table.

        Parameters
        ----------
        name : str
            The name of the column to be set as the filter column.

        Returns
        -------
        Self
            Return the current table instance.

        Examples
        --------
        >>> table.set_filter_column("column_name")
        """
        ...

    @property
    def is_persisted(self) -> bool:
        """
        Check whether the table has been persisted.

        Returns
        -------
        bool
            True if the table is persisted, False otherwise.
        """
        ...

    @property
    def is_cache_purge(self) -> bool:
        """
        Check whether cache purging is enabled for the table.

        Returns
        -------
        bool
            True if cache purging is enabled, False otherwise.
        """
        ...

    @property
    def persistence_meta(self) -> PersistenceMetaInfo:
        """
        Retrieve metadata information related to the table's persistence.

        Returns
        -------
        PersistenceMetaInfo
            The PersistenceMetaInfo for the table, which includes details about
            persistence settings.
        """
        ...

    @property
    def info(self) -> StreamTableInfo:
        """
        Retrieve information about the stream table.

        Returns
        -------
        StreamTableInfo
            The StreamTableInfo for the table.
        """
        ...

    @property
    def timestamp_column(self) -> str:
        """
        Get the name of the timestamp column used in the table.

        Returns
        -------
        str
            The name of the timestamp column.
        """
        ...

    @property
    def filter_column(self) -> str:
        """
        Get the name of the filter column used in the table for filtering data.

        Returns
        -------
        str
            The name of the filter column.
        """
        ...

    def subscribe(
        self, action_name, handler, *,
        offset: int = -1, msg_as_table: bool = False, batch_size: int = 0,
        throttle: float = 1, hash: int = -1, reconnect: bool = False, filter=None,
        persist_offset: bool = False, time_trigger: bool = False,
        handler_need_msg_id: bool = False,
    ) -> "SubscriptionHelper":
        """
        Subscribes to a stream table on a local or remote server. We can also specify a
        handler to process the subscribed data.

        Submit and return the subscription topic, which is a combination of the alias
        of the node where the stream table is located, stream table name, and the
        subscription task name (``actionName``) separated by "_". If the subscription
        topic already exists, an exception is thrown.

        - If ``batch_size`` is specified, ``handler`` will be triggered if either the
          number of unprocessed messages reaches ``batch_size`` or the duration of time
          since the last time handler was triggered reaches ``throttle`` seconds.

        - If the subscribed table is overwritten, to keep the subscription we need to
          cancel the subscription with ``Topic.unsubscribe`` and then subscribe to the
          new table.

        Here is how to set the socket buffer size in Linux:

        - In the Linux terminal, run the following commands:

        .. code-block:: shell

            sudo sysctl -w net.core.rmem_default=1048576
            sudo sysctl -w net.core.rmem_max=1048576
            sudo sysctl -w net.core.wmem_default=1048576
            sudo sysctl -w net.core.wmem_max=1048576

        - Alternatively, add or modify the values of *net.core.rmem_default*,
          *net.core.rmem_max*, *net.core.wmem_default* and *net.core.wmem_max* to
          1048576 in the */etc/sysctl.conf* file, and then run ``sudo sysctl -p``.

        Parameters
        ----------
        action_name
            A string indicating subscription task name. It starts with a letter and can
            have letters, digits, and underscores.
        handler
            A unary/binary function or a table, which is used to process the subscribed
            data.

            - If ``handler`` is a unary function, the only parameter of the function is
              the subscribed data, which can be a Table or an AnyVector of the
              subscribed table columns.

            - ``handler`` must be specified as a binary function when
              ``handler_need_msg_id`` = True. The parameters of the function are
              msg_body and msg_id. For details, see ``handler_need_msg_id``.

            - If ``handler`` is a table, the subscribed data will be inserted into it
              directly. It can be a streaming engine, a shared table (including stream
              table, in-memory table, keyed table, indexed table), or a DFS table.

        offset : int, optional
            The position of the first message where the subscription begins. Defaults to
            -1.
        msg_as_table : bool, optional
            Indicates whether the subscribed data is ingested into ``handler`` as a Table
            or as an Any Vector. Defaults to False.
        batch_size : int, optional
            The number of unprocessed messages to trigger the ``handler``. Defaults to 0.
        throttle : float, optional
            The maximum waiting seconds before the handler processes the incoming
            messages if the ``batch_size`` condition has not been reached. Defaults to 1.
        hash : int, optional
            A hash value indicating which subscription executor will process the incoming
            messages for this subscription. Defaults to -1.
        reconnect : bool, optional
            Specifies whether to automatically attempt to resume the subscription if
            interrupted. Defaults to False.
        filter : optional
            The filter condition(s). Defaults to None.
        persist_offset : bool, optional
            Indicates whether to persist the offset of the last processed message in the
            current subscription. Defaults to False.
        time_trigger : bool, optional
            If set to True, ``handler`` will be triggered at the intervals specified by
            ``throttle`` even if no new messages arrive. Defaults to False.
        handler_need_msg_id : bool, optional
            Determines the required parameters for the ``handler``. If True, the
            ``handler`` must accept both msgBody (messages to be ingested) and msgId (ID
            of the last ingested message). If False, the ``handler`` only requires
            msgBody. Defaults to false.

        Returns
        -------
        SubscriptionHelper
            An instance of SubscriptionHelper that allows further configuration and
            submit of the subscription. This object enables setting up the optional
            parameters.

        Examples
        --------
        >>> def my_handler(message):
        ...     print(f"Received message: {message}")
        ...
        >>> subscription = table.subscribe(
        ...     action_name="action_name",
        ...     handler=my_handler,
        ...     offset=0,
        ...     batch_size=10,
        ...     reconnect=True,
        ...     persist_offset=True
        ... )
        """
        ...


def convert_stream_table(*args) -> StreamTable: ...
def create_stream_table(*args) -> StreamTable: ...


class SubscriptionHelper:
    """
    A helper class for managing the stream subscription, allowing further
    configuration and submit of the subscription.
    """
    def offset(self, val: int = -1) -> Self:
        """
        Sets the position of the first message where the subscription begins.

        Parameters
        ----------
        val : int, optional
            The offset position. Defaults to -1.

        Returns
        -------
        Self
            The instance itself.


        .. note::
            A message is a row of the stream table. The offset is relative to the
            first row of the stream table when it is created. If `val` is
            unspecified or -1, the subscription starts with the next new message.
            If `val` is -2, the system retrieves the persisted offset on disk and
            starts the subscription from there. If some rows were cleared from
            memory due to the cache size limit, they are still considered in
            determining where the subscription starts.
        """
        ...

    def msg_as_table(self, val: bool = False) -> Self:
        """
        Sets whether the subscribed data is ingested into ``handler`` as a table
        or as an AnyVector.

        Parameters
        ----------
        val : bool, optional
            Whether to ingest the subscribed data into the handler as a table.
            Defaults to False.

        Returns
        -------
        Self
            The instance itself.


        .. note::
            If `val` is True, the subscribed data is ingested into the handler as a
            table, allowing it to be processed with SQL statements. The default
            value is False, meaning the subscribed data is ingested as an AnyVector
            of columns.
        """
        ...

    def batch_size(self, val: int = 0) -> Self:
        """
        Sets the number of unprocessed messages required to trigger the
        ``handler``.

        Parameters
        ----------
        val : int, optional
            The batch size threshold. Defaults to 0.

        Returns
        -------
        Self
            The instance itself.


        .. note::
            If ``val`` is positive, the handler does not process messages until the
            number of unprocessed messages reaches ``val``. If ``val`` is
            unspecified or non-positive, the handler processes incoming messages as
            soon as they arrive.
        """
        ...

    def throttle(self, val: float = 1) -> Self:
        """
        Sets the maximum waiting time before the ``handler`` processes incoming
        messages if the `batch_size` condition has not been met.

        Parameters
        ----------
        val : float, optional
            The maximum waiting time in seconds. Defaults to 1.

        Returns
        -------
        Self
            The instance itself.


        .. note::
            This value is in seconds. This parameter has no effect if ``batch_size``
            is not specified. To set ``val`` to less than 1 second, the
            ``subThrottle`` configuration must be modified.
        """
        ...

    def hash(self, val: int = -1) -> Self:
        """
        Sets the hash value determining the subscription executor.

        Parameters
        ----------
        val : int, optional
            The hash value for assigning an executor. Defaults to -1.

        Returns
        -------
        Self
            The instance itself.


        .. note::
            This non-negative integer specifies which subscription executor will
            process the incoming messages. If `val` is unspecified, the system
            automatically assigns an executor. To synchronize messages from multiple
            subscriptions, set the same hash value for all of them to ensure they
            are processed by the same executor.
        """
        ...

    def reconnect(self, val: bool = False) -> Self:
        """
        Sets whether the subscription can be automatically resumed if
        interrupted.

        Parameters
        ----------
        val : bool, optional
            Whether to enable automatic resubscription. Defaults to False.

        Returns
        -------
        Self
            The instance itself.


        .. note::
            If `val` is True, the subscription attempts to resume and retrieve all
            streaming data since the interruption. Behavior depends on the
            interruption type:

            - If the network is disconnected but both nodes remain running,
              reconnection occurs automatically when the network is restored.

            - If the publisher node crashes, the subscriber retries resubscribing
              after the publisher restarts:

              - If the publisher adopts data persistence mode, resubscription
                succeeds only after persisted data has been loaded and the
                publisher reaches the row of data where the subscription was
                interrupted.

              - If the publisher does not adopt data persistence, resubscription
                fails.

            - If the subscriber node crashes, automatic resubscription is not
              possible and subscription must be submitted again.

        """
        ...

    def filter(self, val=None) -> Self:
        """
        Sets the filter condition(s) for the subscription.

        Parameters
        ----------
        val : optional
            The filter condition(s) for the subscription. Defaults to None.

        Returns
        -------
        Self
            The instance itself.


        .. note::
            Must be used with the ``set_filter_column`` function. The filter can be
            used in the following ways:

            - Value filtering: A Vector specifying allowed values.

            - Range filtering: A Pair defining an inclusive lower bound and an
              exclusive upper bound.

            - Hash filtering: An AnyVector where:

              - The first element is the number of buckets.

              - The second element is either a scalar specifying the bucket index
                (starting from 0) or a Pair specifying an index range (inclusive
                lower bound, exclusive upper bound).

            - Custom function filtering: A FunctionDef or a str (indicating function
              name or lambda expression). The subscribed data is passed into the
              function as a table, and the function result is sent to the
              subscriber.

            `filter` does not support Boolean types.
        """
        ...

    def persist_offset(self, val: bool = False) -> Self:
        """
        Sets whether to persist the offset of the last processed message.

        Parameters
        ----------
        val : bool, optional
            Whether to persist the last processed message offset. Defaults to
            False.

        Returns
        -------
        Self
            The instance itself.


        .. note::
            This is useful for resubscription and can be retrieved using
            ``Topic.processed_offset``.

        To resubscribe from the persisted offset, set `persist_offset` to True
        and `remove_offset` in `unsubscribe` to False.
        """
        ...

    def time_trigger(self, val: bool = False) -> Self:
        """
        Sets whether the handler is triggered at intervals even if no new
        messages arrive.

        Parameters
        ----------
        val : bool, optional
            Whether to trigger the handler at fixed intervals. Defaults to False.

        Returns
        -------
        Self
            The instance itself.


        .. note::
            If `val` is True, the handler triggers at the intervals specified by
            `throttle`, even when no new messages are received.
        """
        ...

    def handler_need_msg_id(self, val: bool = False) -> Self:
        """
        Sets whether the ``handler`` requires message IDs.

        Parameters
        ----------
        val : bool, optional
            Whether the handler requires message IDs. Defaults to False.

        Returns
        -------
        Self
            The instance itself.


        .. note::
            If `val` is True, the handler must accept two parameters:

            - `msg_body`: The messages ingested into the streaming engine.

            - `msg_id`: The ID of the last ingested message.

        If `val` is False, the handler must accept only one parameter:
        `msg_body`.
        """
        ...

    def submit(self) -> "Topic":
        """
        Submits the current state of the subscription.

        Returns
        -------
        Topic
            The current topic or stream to which the subscription is submitted.
        """
        ...


class TopicInfo:
    node_alias: str
    table_name: str
    """The name of the table for the topic."""
    action_name: str
    """The action associated with the topic."""


class SubscriptionStat:
    worker_id: int
    """Worker ID. An empty column means the subscriber node has not received data."""
    type: Literal["tcp", "udp"]
    """The subscription method, which can be tcp (TCP) or udp (UDP multicast)."""
    queue_depth_limit: int
    """The maximum depth (number of records) of a message queue that is allowed on the
    subscriber node."""
    queue_depth: int
    """Current depth (number of records) of the message queue on the subscriber node."""
    processed_msg_count: int
    """The number of messages that have been processed."""
    last_msg_id: int
    """The last message ID."""
    failed_msg_count: int
    """The number of messages that failed to be processed."""
    last_failed_msg_id: int
    """The last failed message ID."""
    last_failed_timestamp: Timestamp
    """The timestamp of the latest failed message."""
    last_err_msg: str
    """The last error information on the failed message."""
    msg_as_table: bool
    """Indicates how the subscribed data is ingested into handler. True means the data is
    ingested as a table, and False means data is ingested as an AnyVector."""
    batch_size: int
    """The number of messages batch processed by the handler."""
    throttle: float
    """The waiting time (in seconds) for the handler to process the messages if the
    ``batch_size`` condition has not been reached since the last process."""
    hash: int
    """Indicates which subscription executor to process the incoming messages."""
    filter: str
    """The filtering column of a stream table."""
    persist_offset: bool
    """Indicates whether to persist the offset of the last processed message."""
    time_trigger: bool
    """True means that the handler is triggered at the intervals specified by the
    ``throttle`` even if no new messages arrive."""
    handler_need_msg_id: bool
    """True means that the handler supports two parameters: ``msgBody`` and ``msgId``.
    Default false."""


class Topic:
    info: TopicInfo
    """Information related to the topic."""

    stat: SubscriptionStat
    """Statistics related to the topic's subscription."""

    def __str__(self) -> str: ...

    def unsubscribe(self, remove_offset: bool = True):
        """
        Unsubscribe from the topic.

        Parameters
        ----------
        remove_offset : bool, optional
            Whether to remove the current offset. Defaults to True.
        """
        ...

    def remove_offset(self) -> None:
        """
        Remove the stored offset.
        """
        ...

    @property
    def processed_offset(self) -> int:
        """
        Get the processed data offset.

        Returns
        -------
        int
            The offset.
        """
        ...

    @classmethod
    def get_with_detail(cls, table_name: str, action_name: str,
                        node_alias: str = "") -> "Topic":
        """
        Retrieve a topic along with detailed information by specifying the table
        name, action name, and optional node alias.

        Parameters
        ----------
        table_name : str
            Name of the table associated with the topic.
        action_name : str
            Action name related to the topic.
        node_alias : str, optional
            Alias of the node. Defaults to "".

        Returns
        -------
        Topic
            Topic related to the table and action.
        """
        ...

    @classmethod
    def get_with_topic(cls, topic: str) -> "Topic":
        """
        Retrieve a topic based on the topic string.

        Parameters
        ----------
        topic : str
            Topic string identifier.

        Returns
        -------
        Topic
            Topic corresponding to the given topic identifier.
        """
        ...


#####################################################################
# Plugin Module
#####################################################################


class MatchingEngineSimulatorStat(EngineStat):
    """_summary_

    Parameters
    ----------
    EngineStat : _type_
        _description_
    """
    pass


class MatchingEngineSimulator(StreamEngine):
    engine_type: EngineType
    stat: MatchingEngineSimulatorStat

    @classmethod
    def create(
        cls,
        name: str,
        exchange: Union[plugin_simulator.Exchange, str],
        data_type: Union[plugin_simulator.MarketDataType, int],
        order_detail_output: Table,
        quote_schema: Union[Table, TypeDict] = None,
        user_order_schema: Union[Table, TypeDict] = None,
        *,
        config: plugin_simulator.MatchingEngineSimulatorConfig = None,
    ) -> plugin_simulator.MatchingEngineSimulatorBuilder:
        """
        Create and configure a matching engine simulator instance.

        Parameters
        ----------
        name : str
            Unique engine name.
        exchange : Union[plugin_simulator.Exchange, str]
            Market type. 
        data_type : Union[plugin_simulator.MarketDataType, int]
            Market data type.            
        order_detail_output : Table
            Unique engine name.
        quote_schema : Union[Table, TypeDict], optional
            Unique engine name.
        user_order_schema : Union[Table, TypeDict], optional
            Unique engine name.
        config : plugin_simulator.MatchingEngineSimulatorConfig, optional
            Unique engine name.            
            
        Returns
        -------
        plugin_simulator.MatchingEngineSimulatorBuilder
            An instance of ``MatchingEngineSimulatorBuilder`` instant.
        """
        ...

    def reset(self, cancel_order: bool = False):
        """Clear cached orders and market data.

        Parameters
        ----------
        cancel_order : bool, optional
            Whether to cancel all unfilled user orders.

            - If True, all unfilled user orders will be canceled, and the corresponding 
              cancellation information will be written to the trade detail table (specified via the order_detail_output parameter in create).

            - Default is False, meaning no cancellation is performed.
        """
        ...

    def drop(self):
        """Drop the matching engine.
        """
        ...

    def get_open_orders(self, symbol: str = None) -> Table:
        """Get all unfilled user orders as a table.

        Parameters
        ----------
        symbol : str, optional
            A STRING scalar used to specify a stock for retrieving all unfilled orders.

        Returns
        -------
        Table
            Returns a table containing the following columns:
            
            .. list-table::
                :header-rows: 1
                :widths: 20 15 65

                * - Name
                  - Type
                  - Description
                * - orderId
                  - LONG
                  - Order ID
                * - timestamp
                  - TIMESTAMP
                  - Timestamp
                * - symbol
                  - STRING
                  - Stock symbol
                * - price
                  - DOUBLE
                  - Order price
                * - totalQty
                  - LONG
                  - User order quantity
                * - openQty
                  - LONG
                  - Remaining quantity of user order
                * - direction
                  - INT
                  - 1 = Buy, 2 = Sell
                * - isMatching
                  - INT
                  - Whether the order has reached matching time
                * - openVolumeWithBetterPrice
                  - LONG
                  - Total unfilled order volume at prices better than the order price
                * - openVolumeWithWorsePrice
                  - LONG
                  - Total unfilled order volume at prices worse than the order price
                * - openVolumeAtOrderPrice
                  - LONG
                  - Total unfilled order volume at the order price
                * - priorOpenVolumeAtOrderPrice
                  - LONG
                  - Total unfilled order volume at the order price with earlier timestamp than this order
                * - depthWithBetterPrice
                  - INT
                  - Number of price levels better than the order price
                * - updateTime
                  - TIMESTAMP
                  - Latest update time

            .. note::
                The columns openVolumeWithBetterPrice, openVolumeWithWorsePrice, openVolumeAtOrderPrice, 
                priorOpenVolumeAtOrderPrice, depthWithBetterPrice, and updateTime are included only 
                when output_queue_position=1. (See the config parameter description in the create interface for details.)

        """
        ...

    @property
    def symbol_list(self) -> Vector:
        """Retrieve the list of stock symbols in the engine.

        Returns
        -------
        Vector
            A string vector indicating the list of stock symbols.
        """
        ...

    def insert_market(self, msg_body: Constant) -> None:
        """Insert market data (table or tuple).

        Parameters
        ----------
        msg_body : Constant
            It can be either a table object or a tuple, representing market data or user order data. 
            Its format must conform to the target table structure specified when creating the engine, 
            such as quote_schema or user_order_schema. In particular, when msg_body is a tuple, 
            if a column in the target table is an array vector, the corresponding element in the tuple 
            must be either an array vector (e.g., arrayVector([2], 23.42 23.43)) or a tuple containing 
            only a regular vector (e.g., [23.42 23.43]).
        """
        ...

    def insert_order(self, msg_body: Constant) -> Vector:
        """Insert user order data. Returns order ID.

        Parameters
        ----------
        msg_body : Constant
            It can be either a table object or a tuple, representing market data or user order data. 
            Its format must conform to the target table structure specified when creating the engine, 
            such as quote_schema or user_order_schema. In particular, when msg_body is a tuple, 
            if a column in the target table is an array vector, the corresponding element in the tuple 
            must be either an array vector (e.g., arrayVector([2], 23.42 23.43)) or a tuple containing 
            only a regular vector (e.g., [23.42 23.43]).

        Returns
        -------
        Vector
            A LONG vector indicating the order ID.
        """
        ...

    def set_limit_price(self, data: Table) -> bool:
        """Set limit up/down prices.

        Parameters
        ----------
        data : Table
            A table containing three columns: symbol (STRING), upLimitPrice (DOUBLE), and downLimitPrice (DOUBLE).

        Returns
        -------
        bool
            Returns True if the settings are applied successfully.
        """
        ...

    def set_prev_close(self, prev_close: Union[Dict[str, float], Dictionary]) -> bool:
        """Set the previous closing prices for the matching engine simulator.

        Parameters
        ----------
        prev_close : Union[Dict[str, float], Dictionary]
            A dictionary where keys are stock symbols (strings) and values are the 
            corresponding previous closing prices (floats).

        Returns
        -------
        bool
            Returns True if the settings are applied successfully.
        """
        ...

    def get_snapshot(self, symbol: str = None) -> Table:
        """Get market snapshot from the engine.

        Parameters
        ----------
        symbol : str, optional
            A STRING scalar specifying a stock. If not provided, snapshots for all stocks are retrieved.

        Returns
        -------
        Table
            A table with the following schema:

            +----------------------+-----------+----------------------------------------+
            | Name                 | Type      | Description                            |
            +======================+===========+========================================+
            | symbol               | STRING    | Stock symbol                           |
            +----------------------+-----------+----------------------------------------+
            | timestamp            | TIMESTAMP | Time                                   |
            +----------------------+-----------+----------------------------------------+
            | avgTradePriceAtBid   | DOUBLE    | Average trade price at bid             |
            +----------------------+-----------+----------------------------------------+
            | avgTradePriceAtOffer | DOUBLE    | Average trade price at offer           |
            +----------------------+-----------+----------------------------------------+
            | totalTradeQtyAtBid   | LONG      | Total traded quantity at bid           |
            +----------------------+-----------+----------------------------------------+
            | totalTradeQtyAtOffer | LONG      | Total traded quantity at offer         |
            +----------------------+-----------+----------------------------------------+
            | bidPrice             | DOUBLE[]  | List of bid prices                     |
            +----------------------+-----------+----------------------------------------+
            | bidQty               | LONG[]    | List of bid quantities                 |
            +----------------------+-----------+----------------------------------------+
            | offerPrice           | DOUBLE[]  | List of offer prices                   |
            +----------------------+-----------+----------------------------------------+
            | offerQty             | LONG[]    | List of offer quantities               |
            +----------------------+-----------+----------------------------------------+
            | lastPrice            | DOUBLE    | Last price                             |
            +----------------------+-----------+----------------------------------------+
            | highPrice            | DOUBLE    | Highest price                          |
            +----------------------+-----------+----------------------------------------+
            | lowPrice             | DOUBLE    | Lowest price                           |
            +----------------------+-----------+----------------------------------------+
        """
        ...
