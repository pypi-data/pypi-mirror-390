import abc

from ._swordfishcpp import (  # type: ignore
    create_type_enum, create_array_type_enum,
    VOID, BOOL, CHAR, SHORT, INT, LONG,
    DATE, MONTH, TIME, MINUTE, SECOND, DATETIME,
    TIMESTAMP, NANOTIME, NANOTIMESTAMP, DATEHOUR,
    FLOAT, DOUBLE, SYMBOL, STRING, UUID, FUNCTIONDEF,
    HANDLE, CODE, DATASOURCE, RESOURCE, ANY, DICTIONARY,
    IPADDR, INT128, BLOB, COMPLEX, POINT, DURATION, OBJECT,
    SCALAR, VECTOR, PAIR, MATRIX, SET, DICT, TABLE,
    VAR, SHARED, DEF,
    DEBUG, INFO, ERROR, WARNING,
    ALL, FIRST, LAST, NONE,
    SEQ, VALUE, RANGE, LIST, COMPO, HASH,
    EnumInt, DataType, DataForm,
)


class DECIMALENUM(abc.ABC):
    __decimal_type__: int

    def __call__(self, scale: int) -> DataType:
        return create_type_enum(self.__decimal_type__, scale)

    def __int__(self) -> int:
        return self.__decimal_type__


class __DECIMAL32(DECIMALENUM):
    """
    Creates instances of the DECIMAL32 DataType.

    Examples
    -------
    >>> import swordfish as sf
    >>> decimal32 = sf.types.DECIMAL32(3)
    >>> decimal32
    DataType(DECIMAL32(3), val=-2147287003)
    >>> sf.scalar("1.23", type=decimal32)
    Decimal32(1.230, scale=3)
    >>> sf.scalar("1.23", type="DECIMAL32(3)")
    Decimal32(1.230, scale=3)
    """
    __decimal_type__ = 37


class __DECIMAL64(DECIMALENUM):
    """
    Creates instances of the DECIMAL64 DataType.

    Examples
    -------
    >>> import swordfish as sf
    >>> decimal64 = sf.types.DECIMAL64(4)
    >>> decimal64
    DataType(DECIMAL64(4), val=-2147221466)
    >>> sf.scalar("1.23", type=decimal64)
    Decimal64(1.2300, scale=4)
    >>> sf.scalar("1.23", type="DECIMAL64(4)")
    Decimal64(1.2300, scale=4)
    """
    __decimal_type__ = 38


class __DECIMAL128(DECIMALENUM):
    """
    Creates instances of the DECIMAL128 DataType.

    Examples
    -------
    >>> import swordfish as sf
    >>> decimal128 = sf.types.DECIMAL128(5)
    >>> decimal128
    DataType(DECIMAL128(5), val=-2147155929)
    >>> sf.scalar("1.23", type=decimal128)
    Decimal128(1.23000, scale=5)
    >>> sf.scalar("1.23", type="DECIMAL128(5)")
    Decimal128(1.23000, scale=5)
    """
    __decimal_type__ = 39


DECIMAL32 = __DECIMAL32()
DECIMAL64 = __DECIMAL64()
DECIMAL128 = __DECIMAL128()


class __ARRAY:
    """
    Creates instances of the ARRAY DataType.

    Examples
    -------
    >>> import swordfish as sf
    >>> sf.array_vector([[True], [False, None]], type=sf.types.ARRAY(sf.types.BOOL))
    ArrayVector([[1],[0,00b]], type=BOOL[])
    >>> sf.array_vector([[True], [False, None]], type="BOOL[]")
    ArrayVector([[1],[0,00b]], type=BOOL[])
    """
    def __call__(self, sub_type: DataType) -> DataType:
        return create_array_type_enum(sub_type)


ARRAY = __ARRAY()


def _create_new_type_class(name, type_enum: EnumInt):
    return _TYPE_HINT(
        "_" + name,
        (),
        {
            '_data_type': type_enum,
            '_data_form': name,
        },
    )


class _TYPE_HINT(type):
    def __new__(cls, name, bases, dct):
        return super().__new__(cls, name, bases, dct)


SCALAR.set_function(_create_new_type_class)


__all__ = [
    "EnumInt", "DataType", "DataForm",
    "VOID", "BOOL", "CHAR", "SHORT", "INT", "LONG",
    "DATE", "MONTH", "TIME", "MINUTE", "SECOND", "DATETIME",
    "TIMESTAMP", "NANOTIME", "NANOTIMESTAMP", "DATEHOUR",
    "FLOAT", "DOUBLE", "SYMBOL", "STRING", "UUID", "FUNCTIONDEF",
    "HANDLE", "CODE", "DATASOURCE", "RESOURCE", "ANY", "DICTIONARY",
    "IPADDR", "INT128", "BLOB", "COMPLEX", "POINT", "DURATION", "OBJECT",
    "DECIMAL32", "DECIMAL64", "DECIMAL128",
    "ARRAY",
    "SCALAR", "VECTOR", "PAIR", "MATRIX", "SET", "DICT", "TABLE",
    "VAR", "SHARED", "DEF",
    "DEBUG", "INFO", "ERROR", "WARNING",
    "ALL", "FIRST", "LAST", "NONE",
    "SEQ", "RANGE", "VALUE", "LIST", "COMPO", "HASH",
]
