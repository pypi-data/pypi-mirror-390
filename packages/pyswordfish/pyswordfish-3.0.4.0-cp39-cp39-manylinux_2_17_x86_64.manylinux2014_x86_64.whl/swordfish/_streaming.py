from ._swordfishcpp import (  # type: ignore
    StreamTable, Topic,
    convert_stream_table as convert_table,
    create_stream_table as create_table,
    ProgrammingError,
    _global_exec, _global_call,
)
from .types import TypeDict, TypeList
from . import data as sf_data

import typing
from typing import Any, List, Union, Optional


@typing.overload
def table(data: Any = None, *, types: TypeDict = None) -> StreamTable:
    ...


@typing.overload
def table(data: Any = None, *, names: List[str] = None, types: TypeList = None) -> StreamTable:
    ...


@typing.overload
def table(*, types: TypeDict = None, size: int = 0, capacity: int = 1) -> StreamTable:
    ...


@typing.overload
def table(*, names: List[str] = None, types: TypeList = None, size: int = 0, capacity: int = 1) -> StreamTable:
    ...


def table(
    data: Any = None,
    *,
    names: List[str] = None,
    types: Union[TypeDict, TypeList] = None,
    size: int = 0,
    capacity: int = 1,
) -> StreamTable:
    """
    Creates a StreamTable from data, schema, or empty specification.

    Parameters
    ----------
    data : Any, optional
        Input data to be converted into a StreamTable. Default is None.
    names : list of str, optional
        List of column names for the StreamTable. Used with `types`.
    types : dict or list, optional
        Dictionary mapping column names to types, or list of types for columns.
    size : int, optional
        Initial number of rows in the StreamTable. Default is 0.
    capacity : int, optional
        Initial allocated capacity for storing rows. Default is 1.

    Returns
    -------
    StreamTable
        An instance of StreamTable created from the provided data and schema.

    Examples
    --------
    Create from dict and type dict:
        >>> import swordfish as sf
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
        >>> x = sf.streaming.table(my_dict, types=column_types)
        >>> x
        id name    age
        -- ------- ---
        1  Alice   25
        2  Bob     30
        3  Charlie 35
        4  David   40

    Create from dict, names, and type list:
        >>> table = sf.streaming.table(
        ...     data=my_dict,
        ...     names=["id", "name", "age"],
        ...     types=["LONG", "STRING", "INT"]
        ... )
        >>> table
        id name    age
        -- ------- ---
        1  Alice   25
        2  Bob     30
        3  Charlie 35
        4  David   40

    Create empty table with type dict, size, and capacity:
        >>> column_types = {
        ...     "id": "LONG",
        ...     "name": "STRING",
        ...     "age": "INT",
        ... }
        >>> table = sf.streaming.table(types=column_types, size=5, capacity=10)
        >>> table
        id name age
        -- ---- ---

    Create empty table with names, type list, size, and capacity:
        >>> table = sf.streaming.table(
        ...     names=["id", "name", "age"],
        ...     types=["INT", "STRING", "INT"],
        ...     size=5,
        ...     capacity=10
        ... )
        >>> table
        id name age
        -- ---- ---

    Raises
    ------
    ProgrammingError
        If the number of names and types do not match, or schema is invalid.
    """
    if data is not None:
        if names is None and types is None:
            return convert_table(data, dict())
        if isinstance(names, list) and isinstance(types, list):
            if len(names) != len(types):
                raise ProgrammingError(
                    "The number of column names should be the same as the "
                    "number of data types."
                )
            new_types = dict()
            for n, t in zip(names, types):
                new_types[n] = t
            return convert_table(data, new_types)
        elif isinstance(types, dict):
            return convert_table(data, types)
        elif types is None:
            return convert_table(data, dict())
        else:
            raise ProgrammingError(
                "Can't create Table with invalid names or types."
            )
    if names is None and types is None:
        raise ProgrammingError(
            "Can't create Table with empty names and empty types."
        )
    if isinstance(names, list) and isinstance(types, list):
        if len(names) != len(types):
            raise ProgrammingError(
                "The number of column names should be the same as the "
                "number of data types."
            )
        new_types = dict()
        for n, t in zip(names, types):
            new_types[n] = t
        types = new_types
    if isinstance(types, dict):
        return create_table(types, size, capacity)
    if types is None:
        raise ProgrammingError(
            "Can't create Table with empty names and empty types."
        )
    raise ProgrammingError("Can't create Table with invalid names or types.")

def list_shared_tables() -> List[str]:
    """
    Retrieves the names of all shared StreamTables.

    Returns
    -------
    List[str]
        A list of strings indicating the names of all shared StreamTables.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.streaming.list_shared_tables()
    """
    return _global_exec("exec name from getStreamTables() where shared=true").to_list()


def list_unloaded_persisted_tables() -> List[str]:
    """
    Retrieves the names of all unloaded persisted StreamTable.

    Returns
    -------
    List[str]
        A list of strings indicating the names of all unloaded persisted
        StreamTable.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.streaming.list_unloaded_persisted_tables()
    """
    return _global_exec("exec name from getStreamTables() where isNull(shared)").to_list()


def exists(name: str) -> bool:
    """
    Checks if a StreamTable with the specified name exists.

    Parameters
    ----------
    name : str
        The name of the StreamTable to check.

    Returns
    -------
    bool
        True if the StreamTable exists, False otherwise.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.streaming.exists('table_name')
    """
    return bool(_global_call("existsStreamTable", name))


def drop(name: str, force: bool = False):
    """
    Drops the StreamTable with the specified name.

    Parameters
    ----------
    name : str
        The name of the StreamTable to drop.
    force : bool, optional
        If True, forces the table to be dropped. Defaults to False.

    Examples
    --------
    >>> import swordfish as sf
    >>> sf.streaming.drop('table_name', force=False)
    """
    _global_call("dropStreamTable", name, force)


@typing.overload
def exists_topic(table_name: str, action_name: str) -> bool:
    ...


@typing.overload
def exists_topic(*, topic: Union[Topic, str]) -> bool:
    ...


def exists_topic(table_name: str = None, action_name: str = None, *, topic: Union[Topic, str] = None) -> bool:
    """
    Checks if a specific action exists for a given StreamTable, or if a Topic exists.

    Parameters
    ----------
    table_name : str, optional
        The name of the StreamTable.
    action_name : str, optional
        The name of the action to check for.
    topic : Union[Topic, str], optional
        The Topic to check for existence.

    Returns
    -------
    bool
        True if the specified action exists for the table, or if the Topic exists, False otherwise.

    Examples
    --------
    Check by table and action name:
        >>> import swordfish as sf
        >>> sf.streaming.exists_topic('table_name', 'action_name')

    Check by topic name:
        >>> import swordfish as sf
        >>> sf.streaming.exists_topic(topic='topic_name')
    """
    if topic is None:
        return bool(_global_call("existsSubscriptionTopic", sf_data.Nothing, table_name, action_name))
    if isinstance(topic, str):
        topic = Topic.get_with_topic(topic)
    return bool(_global_call("existsSubscriptionTopic", sf_data.Nothing, topic.info.table_name, topic.info.action_name))



@typing.overload
def topic(table_name: str, action_name: str) -> Topic:
    ...


@typing.overload
def topic(*, topic: str) -> Topic:
    ...


def topic(table_name: Optional[str] = None, action_name: Optional[str] = None, *, topic: Optional[str] = None) -> Topic:
    """
    Retrieves a Topic by its associated StreamTable name and action name, or by its name.

    Parameters
    ----------
    table_name : str, optional
        The name of the StreamTable.
    action_name : str, optional
        The name of the action associated with the StreamTable.
    topic : str, optional
        The name of the Topic.

    Returns
    -------
    Topic
        The Topic corresponding to the provided StreamTable and action names, or topic name.

    Examples
    --------
    Retrieve by table and action name:
        >>> import swordfish as sf
        >>> sf.streaming.topic('table_name', 'action_name')

    Retrieve by topic name:
        >>> import swordfish as sf
        >>> sf.streaming.topic(topic='topic_name')
    """
    if topic is None:
        return Topic.get_with_detail(table_name, action_name)
    return Topic.get_with_topic(topic)
