from typing import Dict, List, Union

from ._enums import DataType, DataForm
from ._enums import VOID, BOOL, CHAR, SHORT, INT, LONG
from ._enums import DATE, MONTH, TIME, MINUTE, SECOND, DATETIME
from ._enums import TIMESTAMP, NANOTIME, NANOTIMESTAMP, DATEHOUR
from ._enums import FLOAT, DOUBLE, SYMBOL, STRING, UUID, FUNCTIONDEF
from ._enums import HANDLE, CODE, DATASOURCE, RESOURCE, ANY, DICTIONARY
from ._enums import IPADDR, INT128, BLOB, COMPLEX, POINT, DURATION, OBJECT
from ._enums import DECIMAL32, DECIMAL64, DECIMAL128
from ._enums import ARRAY
from ._enums import SCALAR, VECTOR, PAIR, MATRIX, SET, DICT, TABLE


TypeDict = Dict[str, Union[DataType, str]]
TypeList = List[Union[DataType, str]]


__all__ = [
    "DataType", "DataForm", "TypeDict", "TypeList",
    "VOID", "BOOL", "CHAR", "SHORT", "INT", "LONG",
    "DATE", "MONTH", "TIME", "MINUTE", "SECOND", "DATETIME",
    "TIMESTAMP", "NANOTIME", "NANOTIMESTAMP", "DATEHOUR",
    "FLOAT", "DOUBLE", "SYMBOL", "STRING", "UUID", "FUNCTIONDEF",
    "HANDLE", "CODE", "DATASOURCE", "RESOURCE", "ANY", "DICTIONARY",
    "IPADDR", "INT128", "BLOB", "COMPLEX", "POINT", "DURATION", "OBJECT",
    "DECIMAL32", "DECIMAL64", "DECIMAL128",
    "ARRAY",
    "SCALAR", "VECTOR", "PAIR", "MATRIX", "SET", "DICT", "TABLE",
]
