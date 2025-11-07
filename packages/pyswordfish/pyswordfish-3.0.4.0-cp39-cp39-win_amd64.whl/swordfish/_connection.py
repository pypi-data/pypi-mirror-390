from ._swordfishcpp import (  # type: ignore
    Constant, MetaCode,
    DefaultSessionConnectionImpl,
    MetaCodeContextImpl, EmptyContextImpl,
    ConnectionImpl,
    RemoteConnectionImpl,
    OLTPConnectionImpl, CatalogConnectionImpl, SchemaImpl, StorageType,
    SEQ, RANGE, VALUE, LIST, HASH, COMPO, INT,
    ALL, LAST, FIRST,
    _global_call, Table, EnumInt, FunctionDef, Handle,
    ProgrammingError,
    subscribe_impl_with_conn, SubscriptionHelper
)
from ._helper import Config
from .types import TypeDict
from . import data as sf_data

from typing import Dict, Any, Optional
from typing import TypeVar, Generic, Literal, List, overload, Union
from typing import final


T = TypeVar('T', bound=ConnectionImpl)


class Connection(Generic[T]):
    """
    A generic connection class that wraps various types of connection
    implementations.
    """
    def __init__(self, impl: T):
        self.impl = impl
        self.is_closed = False
        self.is_context = False

    @property
    @final
    def __sf_connection__(self) -> Optional[T]:
        if self.is_closed:
            return None
        return self.impl

    @final
    def _assert_alive(self):
        if self.is_closed:
            raise ProgrammingError("Connection is closed.")

    @final
    def __enter__(self):
        """
        Enters the context for the connection.

        Returns
        -------
        ConnectionImpl
            A `ConnectionImpl` instance.
        """
        self._assert_alive()
        if self.is_context:
            raise ProgrammingError("Connection cannot enter twice.")
        self.is_context = True
        self.impl.__enter__()
        return self

    @final
    def __exit__(self, exc_type, exc_value, traceback):
        self._assert_alive()
        assert self.is_context
        self.impl.__exit__(exc_type, exc_value, traceback)
        self.is_context = False

    @final
    def sql(self, sql: str, *, vars: Optional[Dict[str, Any]] = None):
        """
        Executes a SQL query.

        Parameters
        ----------
        sql : str
            The SQL query string to be executed.
        vars : dict, optional
            A dictionary of variables to bind to the SQL query.

        Returns
        -------
        Constant
            The result of the SQL query execution.
        """
        self._assert_alive()
        return self._sql_impl(sql, vars=vars)

    def _sql_impl(self, sql: str, *, vars: Optional[Dict[str, Any]] = None):
        return self.impl.sql(sql, vars=vars)

    @final
    def close(self):
        """
        Closes the connection.
        """
        self._assert_alive()
        if self.is_context:
            raise ProgrammingError("Cannot close connection in context.")
        self.is_closed = True
        self.impl = None

    @final
    def commit(self) -> None:
        """
        Commits the current transaction.

        Raises
        ------
        NotImplementedError
            The commit operation is not implemented.
        """
        self._assert_alive()
        self._commit_impl()

    def _commit_impl(self) -> None:
        raise NotImplementedError()

    @final
    def in_transaction(self) -> bool:
        """
        Checks whether the connection is in an active transaction context.

        Returns
        -------
        bool
            True if in an active transaction context, False otherwise.

        Raises
        ------
        NotImplementedError
            The in_transaction operation is not implemented.
        """
        self._assert_alive()
        return self._in_transaction_impl()

    def _in_transaction_impl(self) -> bool:
        raise NotImplementedError()

    @final
    def rollback(self) -> None:
        """
        Rolls back the current transaction.

        Raises
        ------
        NotImplementedError
            The rollback operation is not implemented.
        """
        self._assert_alive()
        self._rollback_impl()

    def _rollback_impl(self) -> None:
        raise NotImplementedError()


class Partition:
    """
    A class for implementing data partitioning.
    """
    def __init__(self, partition_type, partition_scheme):
        self.partition_type = partition_type
        self.partition_scheme = partition_scheme

    def __str__(self):
        return f"Partition({self.partition_type}, {self.partition_scheme})"

    def __repr__(self):
        return str(self)

    def build(self):
        if self.partition_type != COMPO:
            return self.partition_type, self.partition_scheme
        return self.partition_type, sf_data.any_vector([_._build_for_compo() for _ in self.partition_scheme])

    def _build_for_compo(self):
        type_, scheme_ = self.build()
        return _global_call("database", "", type_, scheme_)

    @classmethod
    def seq(cls, n):
        """
        Partitions data into `n` partitions using the SEQ partitioning type.

        Parameters
        ----------
        n : Any
            The number of partitions to create.

        Returns
        -------
        Partition
            A Partition object that divides the data into `n` partitions.

        Examples
        --------
        >>> import swordfish as sf
        >>> sf.Partition.seq(8)
        Partition(SEQ, 8)
        """
        return Partition(SEQ, sf_data.scalar(n))

    @classmethod
    def range(cls, v):
        """
        Partitions data using the specified range boundaries.

        Parameters
        ----------
        v : Any
            A list of values representing the range boundaries.

        Returns
        -------
        Partition
            A Partition object that divides the data based on the specified
            range boundaries.

        Examples
        --------
        >>> import swordfish as sf
        >>> sf.Partition.range([0, 5, 10])
        Partition(RANGE, [0,5,10])
        """
        return Partition(RANGE, sf_data.vector(v))

    @classmethod
    def value(cls, v):
        """
        Partitions data based on the specified values in the partitioning column.

        Parameters
        ----------
        v : Any
            A list of values to partition the data.

        Returns
        -------
        Partition
            A Partition object that divides the data based on the provided values.

        Examples
        --------
        >>> import swordfish as sf
        >>> sf.Partition.value([1, 2, 3])
        Partition(VALUE, [1,2,3])
        """
        return Partition(VALUE, sf_data.vector(v))

    @classmethod
    def list(cls, v):
        """
        Partitions data based on specified sets of values in the partitioning
        column.

        Parameters
        ----------
        v : Any
            A list of lists representing the partition.

        Returns
        -------
        Partition
            A Partition object that divides the data based on the provided lists.

        Examples
        --------
        >>> import swordfish as sf
        >>> sf.Partition.list([[1, 2, 3], [4, 5]])
        Partition(LIST, ([1,2,3],[4,5]))
        """
        return Partition(LIST, sf_data.any_vector(v))

    @classmethod
    def hash(cls, t, n):
        """
        Partitions data using a hash function on the partitioning column.

        Parameters
        ----------
        t : int
            The type of the partitioning column.
        n : int
            The number of partitions to create.

        Returns
        -------
        Partition
            A Partition object that divides data based on the given arguments.

        Examples
        --------
        >>> import swordfish as sf
        >>> sf.Partition.hash(sf.types.INT, 8)
        Partition(HASH, [4,8])
        """
        return Partition(HASH, sf_data.vector([t, n], type=INT))

    @classmethod
    def compo(cls, partitions: List['Partition']):
        """
        Partitions data using the COMPO partitioning type, which combines two or
        three dimensions.

        Parameters
        ----------
        partitions : list of Partition
            A list of Partition objects.

        Returns
        -------
        Partition
            A Partition object that combines the provided partitions.

        Examples
        --------
        >>> import swordfish as sf
        >>> sf.Partition.compo([sf.Partition.seq(2), sf.Partition.seq(5)])
        Partition(COMPO, [Partition(SEQ, 2), Partition(SEQ, 5)])
        """
        return Partition(COMPO, partitions)


# In-Memory Connection (Default)
class DefaultSessionConnection(Connection[DefaultSessionConnectionImpl]):
    pass


# OLTP Connection
class OLTPOption(Config):
    """Configuration options for OLTP connections.
    """
    readOnly: bool = False
    """
    If True, the database will be opened in read-only mode, allowing only queries
    but preventing any write operations (insert, delete, update) or structural
    changes (create/drop tables).

    A database can be opened in read-only mode multiple times simultaneously,
    whether in the same process or different processes. However, if it is opened
    in write mode, no other process can access it simultaneously.

    Notes
    -----
    Avoid opening the same database multiple times in read-only mode
    within the same process unless necessary. Each time the database is opened,
    all data is loaded into memory, which can impact performance.
    """
    enableWAL: bool = True
    """
    - If set to false, all data is stored in memory and will be lost once the
      database is closed.
    - If set to true, the write-ahead logging will be turned on for persistence.

    Notes
    -----
    Set this option to True if you want to prevent ANY data loss.
    """
    syncOnTxnCommit: bool = False
    """
    This option is relevant only when `enableWAL` is set to True.

    - If True, before committing a write transaction, the database must ensure that
      all write-ahead logs for the transaction are fully persisted.
    - If False, the database can recover from a process crash but not from an OS crash.
      This mode generally offers better performance.

    Notes
    -----
    - Set this option to True if you want to prevent data loss even in the event of an OS crash.
    - Set it to False if you prefer better performance and can tolerate data loss from an OS crash.
    """
    enableCheckpoint: bool = True
    """
    If True, the database will automatically perform a checkpoint based on
    `checkpointThreshold` and `checkpointInterval`.
    """
    checkpointThreshold: int = 100
    """
    Forces a checkpoint when the size of write-ahead logs exceeds the specified
    number of MiB.
    """
    checkpointInterval: int = 60
    """
    Forces a checkpoint at regular intervals, specified in seconds.
    """


class OLTPConnection(Connection[OLTPConnectionImpl]):
    """
    Manages connections to OLTP databases.

    Examples
    --------
    >>> import swordfish as sf
    >>> conn = sf.connect(url="/path/to/file")
    """
    def __init__(self, impl):
        super().__init__(impl)

    def _sql_impl(self, sql: str, *, vars: Optional[Dict[str, Any]] = None):
        if not self.impl.check_transaction():
            self.impl.begin_transaction()
        return self.impl.sql(sql, vars=vars)

    def _commit_impl(self):
        self.impl.commit()

    def _in_transaction_impl(self):
        return self.impl.check_transaction()

    def _rollback_impl(self):
        self.impl.rollback()

    def create_table(self, name: str, types: TypeDict, primary, secondary=None):
        """
        Creates a new table in the database.

        Parameters
        ----------
        name : str
            The name of the table to create.
        types : TypeDict
            A dictionary specifying the column names and their data types.
        primary : list of str or str
            The primary key of the table.
        secondary : list of tuple, optional
            Secondary indexes or constraints for the table. Defaults to None.

        Returns
        -------
        Table
            A new table created based on the given parameters.

        Examples
        --------
        >>> conn.create_table("table_name", {
        ...     'a': "INT",
        ...     'b': "INT",
        ...     'c': "BOOL",
        ...     'd': "LONG",
        ...     'e': "STRING",
        ... }, "a", [[True, ["b", "c", "d"]], [False, ["d"]]])
        """
        if secondary is None:
            secondary = []
        return self.impl.create_table(name, types=types, primary=primary, secondary=secondary)

    def drop_table(self, name: str):
        """
        Drops a table from the database.

        Parameters
        ----------
        name : str
            The name of the table to drop.

        Examples
        --------
        >>> conn.drop_table("table_name")
        """
        return self.impl.drop_table(name)

    def list_tables(self):
        """
        Retrieves the names of all tables in the database.

        Returns
        -------
        list
            A list of table names in the database.

        Examples
        --------
        >>> conn.list_tables()
        """
        return self.impl.list_table()

    def exists_table(self, name: str) -> bool:
        return self.impl.exists_table(name)

    def table(self, name: str) -> Table:
        """
        Retrieves a specific table from the database.

        Parameters
        ----------
        name : str
            The name of the table.

        Returns
        -------
        Table
            The corresponding table object.

        Examples
        --------
        >>> t = conn.table("table_name")
        """
        return self.impl.get_table(name)


class Schema:
    """
    Manages catalog schemas.
    """
    def __init__(self, impl: SchemaImpl):
        self.impl = impl

    @property
    def handle(self) -> Handle:
        """
        Obtains a schema handle.

        Returns
        -------
        Handle
            The schema handle.
        """
        return self.impl.get_handle()

    @overload
    def create_table(
        self,
        name: str,
        table_schema,
        partition_cols: List[str],
        *,
        compress_methods: Dict[str, str] = None,
    ):
        pass

    @overload
    def create_table(
        self,
        name: str,
        table_schema,
        *,
        compress_methods: Dict[str, str] = None,
    ):
        pass

    @overload
    def create_table(
        self,
        name: str,
        table_schema,
        partition_cols: List[str],
        *,
        compress_methods: Dict[str, str] = None,
        sort_cols: List[str] = None,
        keep_duplicates: Union[Literal["ALL", "LAST", "FIRST"], EnumInt] = "ALL",
        sort_key_mapping_function: List[FunctionDef] = None,
        soft_delete: bool = False,
        indexes: List[str] = None,
    ) -> Table:
        pass

    @overload
    def create_table(
        self,
        name: str,
        table_schema,
        *,
        compress_methods: Dict[str, str] = None,
        sort_cols: List[str] = None,
        keep_duplicates: Union[Literal["ALL", "LAST", "FIRST"], EnumInt] = "ALL",
        soft_delete: bool = False,
        indexes: List[str] = None,
    ) -> Table:
        pass

    @overload
    def create_table(
        self,
        name: str,
        table_schema,
        partition_cols: List[str],
        *,
        compress_methods: Dict[str, str] = None,
        primary_key_cols: List[str] = None,
        indexes: List[str] = None,
    ) -> Table:
        pass

    @overload
    def create_table(
        self,
        name: str,
        table_schema,
        *,
        compress_methods: Dict[str, str] = None,
        primary_key_cols: List[str] = None,
        indexes: List[str] = None,
    ) -> Table:
        pass

    def create_table(
        self,
        name: str,
        table_schema,
        partition_cols: List[str] = None,
        *,
        compress_methods: Dict[str, str] = None,
        sort_cols: List[str] = None,
        primary_key_cols: List[str] = None,
        keep_duplicates: Union[Literal["ALL", "LAST", "FIRST"], EnumInt, None] = None,
        sort_key_mapping_function: List[FunctionDef] = None,
        soft_delete: Optional[bool] = None,
        indexes: List[str] = None,
    ) -> Table:
        """
        Creates a table using a specific storage engine with optional partitioning.

        This method supports creating tables with three different storage
        engines: OLAP, TSDB, PKEY. Each engine supports creating either:

        - Partitioned tables: Require `partition_cols` for data partitioning
        - Dimension tables: Do not use partitioning but retain other engine
          capabilities

        Engine Compatibility Chart:
            +---------------------+-------------------+-------------------+-------------------+
            | Feature             | OLAP Engine       | TSDB Engine       | PKEY Engine       |
            +=====================+===================+===================+===================+
            | partition_cols      | ✓ (required) [1]_ | ✓ (required) [1]_ | ✓ (required) [1]_ |
            +---------------------+-------------------+-------------------+-------------------+
            | compress_methods    | ✓                 | ✓                 | ✓                 |
            +---------------------+-------------------+-------------------+-------------------+
            | sort_cols           |                   | ✓                 |                   |
            +---------------------+-------------------+-------------------+-------------------+
            | primary_key_cols    |                   |                   | ✓                 |
            +---------------------+-------------------+-------------------+-------------------+
            | keep_duplicates     |                   | ✓                 |                   |
            +---------------------+-------------------+-------------------+-------------------+
            | sort_key [2]_       |                   | ✓                 |                   |
            +---------------------+-------------------+-------------------+-------------------+
            | soft_delete         |                   | ✓                 |                   |
            +---------------------+-------------------+-------------------+-------------------+
            | indexes             |                   | ✓                 | ✓                 |
            +---------------------+-------------------+-------------------+-------------------+

            .. [1] Required for partitioned tables only, not for dimension tables
            .. [2] `sort_key_mapping_function` is only available for TSDB
              partitioned tables, not dimension tables

        Parameters
        ----------
        name : str
            The name of the table.
        table_schema : Any
            The schema definition of the table, a mapping of column names to
            data types.
        partition_cols : list of str, optional
            The partitioning column(s). Defaults to None.
        compress_methods : dict of str to str, optional
            Compression methods for specific columns, where the key is the
            column name and the value is the compression method. Defaults to
            None.
        sort_cols : list of str, optional
            Columns used for sorting to optimize query performance, applicable
            for the TSDB engine. Defaults to None.
        primary_key_cols : list of str, optional
            Columns that act as primary keys, applicable for the PKEY engine.
            Defaults to None.
        keep_duplicates : {"ALL", "LAST", "FIRST"}, EnumInt, optional
            Deduplication strategy, applicable for the TSDB engine. Defaults to
            None.
            - "ALL": Allows all duplicate values.
            - "LAST": Retains only the latest value.
            - "FIRST": Retains only the earliest value.
        sort_key_mapping_function : list of FunctionDef, optional
            A list of functions for defining sorting key mappings, applicable
            for the TSDB engine (partitioned table). Defaults to None.
        soft_delete : bool, optional
            Enables soft delete functionality, applicable for the TSDB engine.
            Defaults to None.
        indexes : list of str, optional
            A list of columns to create indexes on, used for query
            optimization. Applicable for the TSDB and PKEY engine. Defaults to
            None.

        Returns
        -------
        Table
            The created table instance.

        Examples
        --------
        Creating a partitioned table with the OLAP engine
            >>> schema.create_table("quote", table_schema={'id': "INT",
            ... 'date': "DATE", 'value': "DOUBLE"}, partition_cols=["id"],
            ... compress_methods={"id": "lz4"}))

        Creating a dimension table with the OLAP engine
            >>> schema.create_table("quote", table_schema={'id': "INT",
            ... 'date': "DATE", 'value': "DOUBLE"}, compress_methods={"id":
            ... "lz4"})

        Creating a partitioned table with the TSDB engine
            >>> import swordfish as sf
            >>> import swordfish.function as F
            >>> schema.create_table(
            ...     name="quote",
            ...     table_schema={'id': "INT", 'date': "DATE", 'value':
            ...     "DOUBLE"},
            ...     partition_cols=["id"],
            ...     compress_methods={"id": "lz4"},
            ...     sort_cols=["date", "id"],
            ...     keep_duplicates="LAST",
            ...     sort_key_mapping_function=[sf.partial(F.hashBucket,
            ...     buckets=5)],
            ...     soft_delete=True,
            ...     indexes=["id", "date"],
            ... )

        Creating a dimension table with the TSDB engine
            >>> schema.create_table(
            ...     name="quote",
            ...     table_schema={'id': "INT", 'date': "DATE", 'value':
            ...     "DOUBLE"},
            ...     compress_methods={"id": "lz4"},
            ...     sort_cols=['timestamp', 'value'],
            ...     keep_duplicates="LAST",
            ...     soft_delete=True,
            ...     indexes=['name', 'timestamp'],
            ... )

        Creating a partitioned table with the PKEY engine
            >>> schema.create_table(
            ...     name="quote",
            ...     table_schema={'id': "INT", 'date': "DATE", 'value':
            ...     "DOUBLE"},
            ...     partition_cols=["id"],
            ...     compress_methods={"id": "lz4"},
            ...     primary_key_cols=["id"],
            ...     indexes=["timestamp"],
            ... )

        Creating a dimension table with the PKEY engine
            >>> schema.create_table(
            ...     name="quote",
            ...     table_schema={'id': "INT", 'date': "DATE", 'value':
            ...     "DOUBLE"},
            ...     compress_methods={"value": "lz4"},
            ...     primary_key_cols=["id"],
            ...     indexes=["name"],
            ... )
        """
        if compress_methods is None:
            compress_methods = sf_data.Nothing
        if sort_cols is None:
            sort_cols = sf_data.Nothing
        if primary_key_cols is not None:
            sort_cols = primary_key_cols
        if keep_duplicates is None:
            keep_duplicates = sf_data.Nothing
        if sort_key_mapping_function is None:
            sort_key_mapping_function = sf_data.Nothing
        if soft_delete is None:
            soft_delete = sf_data.Nothing
        if indexes is None:
            indexes = sf_data.Nothing

        if isinstance(table_schema, dict):
            table_schema = sf_data.table(types=table_schema, size=0, capacity=1)
        if isinstance(keep_duplicates, str):
            map_d = {
                'ALL': ALL,
                'LAST': LAST,
                'FIRST': FIRST,
            }
            keep_duplicates = map_d[keep_duplicates]
        if partition_cols is None:
            # create dimension table
            return self.impl.create_dimension_table(
                table_schema,
                name,
                compress_methods,
                sort_cols,
                keep_duplicates,
                soft_delete,
                indexes,
            )
        return self.impl.create_partitioned_table(
            table_schema,
            name,
            partition_cols,
            compress_methods,
            sort_cols,
            keep_duplicates,
            sort_key_mapping_function,
            soft_delete,
            indexes,
        )

    def list_tables(self):
        """
        Retrieves the names of all tables in the schema.

        Returns
        -------
        list of str
            A list of table names.

        Examples
        --------
        >>> schema.list_tables()
        """
        return self.impl.list_table()

    def exists_table(self, name: str) -> bool:
        return self.impl.exists_table(name)

    def drop_table(self, name: str):
        """
        Drops a table from the schema.

        Parameters
        ----------
        name : str
            The name of the table to be dropped.

        Examples
        --------
        >>> schema.drop_table("table_name")
        """
        return self.impl.drop_table(name)

    def truncate_table(self, name: str):
        """
        Truncates a table in the schema.

        Parameters
        ----------
        name : str
            The name of the table to truncate.

        Examples
        --------
        >>> schema.truncate_table("table_name")
        """
        return self.impl.truncate_table(name)

    def table(self, name: str):
        """
        Retrieves a table by name.

        Parameters
        ----------
        name : str
            The name of the table to retrieve.

        Returns
        -------
        Table
            The Table corresponding to the specified name.

        Examples
        --------
        >>> schema.table("table_name")
        """
        return self.impl.get_table(name)

    @property
    def engine_type(self) -> StorageType:
        """
        Retrieves the storage engine type.

        Returns
        -------
        StorageType
            The type of storage engine.
        """
        return self.impl.get_engine_type()


class CatalogConnection(Connection[CatalogConnectionImpl]):
    """
    Manages connections to database catalogs.

    Examples
    --------
    >>> import swordfish as sf
    >>> conn = sf.connect(catalog="catalog_name")
    """
    def __init__(self, impl):
        super().__init__(impl)

    def create_schema(
        self,
        name,
        partition: Partition,
        *,
        engine: Literal["OLAP", "TSDB", "PKEY"] = "OLAP",
        atomic: Literal["TRANS", "CHUNK"] = "TRANS",
    ) -> Schema:
        """
        Creates a new schema.

        Parameters
        ----------
        name : str
            The name of the schema to create.
        partition : Partition
            Defines the partitioning type and scheme.
        engine : {"OLAP", "TSDB", "PKEY"}, optional
            The storage engine type to use. Defaults to "OLAP".
        atomic : {"TRANS", "CHUNK"}, optional
            In cases of concurrent writes to the same partition, write conflicts
            can occur. Swordfish manages these conflicts through the atomic
            parameter set during schema creation, offering two modes:

            - 'TRANS' (default): Write operations are terminated upon detecting a
              conflict, ensuring transaction atomicity. Users themselves must
              ensure that concurrent writes to the same partition are prevented.

            - 'CHUNK': The system automatically handles conflicts and retries
              writes, but splits a single write operation into multiple
              transactions, which cannot guarantee overall atomicity.

        Returns
        -------
        Schema
            A Schema created based on the given parameters.

        Examples
        --------
        >>> conn = sf.connect("catalog_name")
        >>> conn.create_schema(name="my_schema", engine="OLAP",
        ...     partition=sf.Partition.range(sf.vector([0, 5, 10], type="INT")))
        """
        partition_type, partition_scheme = partition.build()
        locations = sf_data.Nothing
        impl = self.impl.create_schema(url=name, engine=engine,
                                       partition_type=partition_type,
                                       partition_scheme=partition_scheme,
                                       locations=locations, atomic=atomic)
        return Schema(impl)

    def list_schemas(self):
        """
        Lists all schemas available in the catalog.

        Returns
        -------
        list of str
            A list of the names of schemas.

        Examples
        --------
        >>> conn.list_schemas()
        """
        return self.impl.list_schema()

    def exists_schema(self, name: str) -> bool:
        return self.impl.exists_schema(name)

    def drop_schema(self, name: str):
        """
        Drops the specified schema from the catalog.

        Parameters
        ----------
        name : str
            The name of the schema to drop.
        """
        return self.impl.drop_schema(name)

    def schema(self, name: str) -> Schema:
        """
        Retrieves a schema by name.

        Parameters
        ----------
        name : str
            The name of the schema to retrieve.

        Returns
        -------
        Schema
            The schema corresponding to the given name.
        """
        return Schema(self.impl.get_schema(name))


class RemoteTable:
    def __init__(self, conn, name: str):
        self.conn = conn
        self.name = name

    def subscribe(
        self, action_name, handler, *,
        offset: int = -1, msg_as_table: bool = False, batch_size: int = 0,
        throttle: float = 1, hash: int = -1, reconnect: bool = False, filter=None,
        persist_offset: bool = False, time_trigger: bool = False,
        handler_need_msg_id: bool = False,
    ) -> SubscriptionHelper:
        """
        Subscribes to a remote table for receiving messages.

        Examples
        --------
        >>> def my_handler(msg):
        ...     print(msg)
        >>> t = conn.table("remote_table")
        >>> topic = t.subscribe("my_action", my_handler, offset=0, msg_as_table=True).submit()
        """
        return subscribe_impl_with_conn(
            self.conn.impl,
            self.name,
            action_name,
            handler,
            offset=offset,
            msg_as_table=msg_as_table,
            batch_size=batch_size,
            throttle=throttle,
            hash=hash,
            reconnect=reconnect,
            filter=filter,
            persist_offset=persist_offset,
            time_trigger=time_trigger,
            handler_need_msg_id=handler_need_msg_id,
        )


class RemoteConnection(Connection[RemoteConnectionImpl]):
    """
    Manages connections to OLTP databases.

    Examples
    --------
    >>> import swordfish as sf
    >>> conn = sf.connect(host="192.168.1.2", port=8848, user="admin", passwd="123456")
    """
    def __init__(self, impl):
        super().__init__(impl)

    def table(self, name: str) -> RemoteTable:
        """
        Retrieves a specific table handle from the remote database.

        Parameters
        ----------
        name : str
            The name of the table.

        Returns
        -------
        Table
            The corresponding table object.

        Examples
        --------
        >>> t = conn.table("table_name")
        """
        count = self.impl.session().exec(f"""EXEC count(*) FROM objs(true) WHERE name = "{name}" AND form = "TABLE";""")
        if count.to_python():
            return RemoteTable(self, name)
        raise ProgrammingError(f"RemoteTable '{name}' does not exist.")


class CaseWhen:
    def __init__(self, ctx: "MetaCodeContext"):
        self.ctx = ctx
        self._whens = []
        self._values = []
        self._other = sf_data.NULL

    def _process_expr(self, expr: Any):
        if hasattr(expr, "__sf_constant__"):
            expr = expr.__sf_constant__
        if isinstance(expr, MetaCode):
            return expr
        if isinstance(expr, str):
            return self.ctx.parse(str(expr))
        return self.ctx.const(expr)

    def when(self, cond: Union[MetaCode, str], then: Union[MetaCode, str]):
        self._whens.append(self._process_expr(cond))
        self._values.append(self._process_expr(then))
        return self

    def else_(self, then: Union[MetaCode, str]):
        self._other = self._process_expr(then)
        return self

    @property
    def __sf_constant__(self):
        return self.ctx.impl.casewhen(self._whens, self._values, self._other)


class MetaCodeContext:
    """
    Used for generating meta code.

    Examples
    --------
    >>> with sf.meta_code() as m:
    ...     code = m.var("a")
    >>> code
    MetaCode(< a >)
    """
    def __init__(self, impl: MetaCodeContextImpl) -> None:
        self.impl = impl

    def __enter__(self):
        self.impl.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.impl.__exit__(exc_type, exc_value, traceback)

    def var(self, name: str) -> MetaCode:
        """
        Generates meta code representing a variable by its name.

        Parameters
        ----------
        name : str
            The name of the variable.

        Returns
        -------
        MetaCode
            The generated meta code.

        Examples
        --------
        >>> with sf.meta_code() as m:
        ...     code = m.var("a")
        >>> code
        MetaCode(< a >)
        """
        return self.impl.var(name)

    def const(self, obj: Constant) -> MetaCode:
        """
        Generates meta code representing a Constant.

        Parameters
        ----------
        obj : Constant
            The constant object.

        Returns
        -------
        MetaCode
            The generated meta code.

        Examples
        --------
        >>> with sf.meta_code():
        ...     code = x.const(2)
        >>> code
        MetaCode(< 2 >)
        """
        return self.impl.const(obj)

    def col(self, name: str, *, qualifier: str = None) -> MetaCode:
        """
        Generates meta code for a column.

        Parameters
        ----------
        name : str
            The name of the column.
        qualifier : str, optional
            The qualifier for the column. Defaults to None.

        Returns
        -------
        MetaCode
            The generated meta code.

        Examples
        --------
        >>> with sf.meta_code():
        ...     code = x.col("id", qualifier="t")
        >>> code
        MetaCode(< t.id >)
        """
        return self.impl.col(name, qualifier=qualifier)

    def col_alias(self, obj: MetaCode, name: Union[str, List[str]]) -> MetaCode:
        """
        Generates meta code for assigning an alias to a column or aliases to columns.

        Parameters
        ----------
        obj : MetaCode
            The original meta code for the column.
        name : Union[str, List[str]]
            The alias name(s).

        Returns
        -------
        MetaCode
            The meta code with the column alias applied.

        Examples
        --------
        >>> with sf.meta_code():
        ...     code = x.col_alias(x.col("id"), "col1")
        >>> code
        MetaCode(< id as col1 >)
        """
        return self.impl.col_alias(obj, name)

    def parse(self, expression: str) -> MetaCode:
        """
        Parses a string expression into corresponding meta code.

        Parameters
        ----------
        expression : str
            The expression to parse into meta code.

        Returns
        -------
        MetaCode
            The parsed meta code corresponding to the expression.

        Examples
        --------
        >>> with sf.meta_code():
        ...     code = x.parse("a == 5")
        >>> code
        MetaCode(< a == 5 >)
        """
        return self.impl.parse(expression)

    def call(self, func, *args) -> MetaCode:
        return self.impl.call(func, *args)

    def make_table_joiner(self, func, *args) -> MetaCode:
        return self.impl.tablejoiner(func, *args)

    @property
    def case_(self):
        return CaseWhen(self)


class EmptyContext:
    """
    Used for generating empty context.

    Examples
    --------
    >>> with sf.empty_context() as ctx:
    ...     pass
    """
    def __init__(self, impl: EmptyContextImpl) -> None:
        self.impl = impl

    def __enter__(self):
        self.impl.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.impl.__exit__(exc_type, exc_value, traceback)


def list_catalogs():
    """Retrieves all available catalogs.

    Returns:
        list: A list of all catalogs.

    Examples:
        >>> sf.list_catalogs()
        Vector(["trading"], type=STRING)
    """
    return _global_call("getAllCatalogs")


def exists_catalog(catalog) -> bool:
    """Checkes if a catalog exists.

    Args:
        catalog (str): The name of the catalog to check.

    Returns:
        bool: True if the catalog exists, False otherwise.

    Examples:
        >>> sf.exists_catalog("trading")
        True
    """
    return bool(_global_call("existsCatalog", catalog))


def create_catalog(catalog):
    """Creates a catalog.

    Args:
        catalog (str): The name of the catalog to create.

    Examples:
        >>> sf.create_catalog("catalog_name")
    """
    return _global_call("createCatalog", catalog)


def drop_catalog(catalog):
    """Drops an existing catalog.

    Args:
        catalog (str): The name of the catalog to drop.

    Examples:
        >>> sf.drop_catalog("catalog_name")
    """
    return _global_call("dropCatalog", catalog)


@overload
def connect() -> DefaultSessionConnection:
    pass


@overload
def connect(catalog: str) -> CatalogConnection:
    pass


@overload
def connect(*, url: str, option: Optional[Union[OLTPOption, dict]] = None) -> OLTPConnection:
    pass


@overload
def connect(*, host: str, port: int, user: str = "", passwd: str = "") -> RemoteConnection:
    pass


def connect(catalog: Optional[str] = None, *, url: Optional[str] = None, option: Optional[Union[Config, dict]] = None,
            host: str = None, port: int = None, user: str = "", passwd: str = "") -> Connection:
    """Establishes a connection to different types of databases or sessions based on the provided parameters.

    This function supports multiple connection methods depending on the given arguments:

    1. If no arguments are provided, it establishes a connection to the default session.
    2. If a `catalog` name is provided, it connects to a specific catalog.
    3. If a `url` is provided, it establishes a connection to an OLTP database, optionally using additional connection options.
    4. If `host` and `port` are provided, it connects to a remote database, optionally using `user` and `passwd` for authentication.

    Args:
        catalog (Optional[str], optional): The name of the catalog to connect to. Defaults to `None`.
        url (Optional[str], optional): The URL of the OLTP database. Defaults to `None`.
        option (Config, optional): Additional options for the connection. Defaults to `None`.
        host (str, optional): The hostname of the remote database. Defaults to `None`.
        port (int, optional): The port number of the remote database. Defaults to `None`.
        user (str, optional): The username for authentication. Defaults to an empty string.
        passwd (str, optional): The password for authentication. Defaults to an empty string.

    Returns:
        Connection: An established connection based on the provided arguments.
            - The first method returns a DefaultSessionConnection object.
            - The second method returns a CatalogConnection object.
            - The third method returns a OLTPConnection object.
            - The fourth method returns a RemoteConnection object.

    Examples:
        Connect to the default session:

        >>> conn = sf.connect()

        Connect to a specific catalog:

        >>> conn = sf.connect(catalog="catalog_name")

        Connect to an OLTP database:

        >>> conn = sf.connect(url="url_name", option={'readOnly': True})

        Connect to a remote database:

        >>> conn = sf.connect(host="192.168.1.2", port=8848, user="admin", passwd="123456")
    """
    if url is not None:         # check as OLTP connection
        url = str(url)
        if option is None:
            option = OLTPOption()
        if isinstance(option, dict) and not isinstance(option, Config):
            option = OLTPOption(option)
        return OLTPConnection(OLTPConnectionImpl.connect(url, option))
    elif catalog is not None:   # check as Catalog connection
        catalog = str(catalog)
        return CatalogConnection(CatalogConnectionImpl.connect(catalog))
    elif host is not None and port is not None:
        return RemoteConnection(RemoteConnectionImpl.connect(host, port, user, passwd))
    else:                       # connect to Default
        return DefaultSessionConnection(DefaultSessionConnectionImpl.create())


def meta_code() -> MetaCodeContext:
    """Generates the MetaCode context for working with MetaCode.

    Returns:
        MetaCodeContext: A MetaCodeContext.

    Examples:
        >>> import swordfish as sf
        >>> import swordfish.function as F
        >>> with sf.meta_code() as m:
        ...     metrics = F.add(m.col("a"), 1)
        >>> metrics
        < add(a, 1) >
    """
    return MetaCodeContext(MetaCodeContextImpl.create())


def empty_context() -> EmptyContext:
    return EmptyContext(EmptyContextImpl.create())
