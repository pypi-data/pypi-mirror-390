import os
import sys
import toml
from pathlib import Path
from typing import Type, TypeVar, Generic, Optional, Dict, List
from ._swordfishcpp import (  # type: ignore
    sw_check,
    sw_is_ce_edition,
    _global_call,
    Scalar,
    ProgrammingError,
)
from .tools import get_random_available_port


ENV_NAME_HOME = "SWORDFISH_PYTHON_HOME_PATH"
ENV_NAME_CONFIG = "SWORDFISH_PYTHON_CONFIG_PATH"
ENV_NAME_LICENSE = "SWORDFISH_PYTHON_LICENSE_PATH"
ENV_NAME_HOST = "SWORDFISH_PYTHON_HOST"
ENV_NAME_PORT = "SWORDFISH_PYTHON_PORT"
ENV_NAME_ALIAS = "SWORDFISH_PYTHON_ALIAS"
ENV_NAME_EXTRA = "SWORDFISH_PYTHON_COMMAND"


def _getenv(env_name: str):
    val = os.getenv(env_name)
    return val if val else None


def _get_absolute_path_env(env_name: str):
    return Path(_getenv(env_name)).expanduser()


T = TypeVar('T')


class ConfigDescriptor(Generic[T]):
    """
    A descriptor for managing configuration values.
    """
    config_name: str
    """
    The name of the configuration.
    """
    config_type: Type[T]
    """
    The type of the configuration value.
    """
    config_value: Optional[T]
    """
    The current value of the configuration.
    """

    def __init__(self, val_type: Type[T], default_value: Optional[T] = None):
        self.init(val_type, default_value)

    def init(self, val_type: Type[T], default_value: Optional[T] = None):
        self.config_type = val_type
        self.config_value = val_type(default_value) if default_value is not None else None
        self.default_value = self.config_value

    def __set_name__(self, owner: "Config", name):
        self.name = name
        owner.config_dict[name] = self

    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass

    def get_value_str(self):
        if self.config_value is None:
            return None
        if isinstance(self.config_value, bool):
            return str(self.config_value).lower()
        return str(self.config_value)

    def is_default(self) -> bool:
        """
        Checks if the configuration value matches the default value.

        Returns
        -------
        bool
            True if the current value is the default, False otherwise.
        """
        return self.config_value == self.default_value

    def _wrap_config_value(self, val: Scalar):
        if val.is_null():
            return None
        if self.config_type is Path:
            return Path(val.to_python())
        return val.to_python()


class StaticConfigDescriptor(ConfigDescriptor):
    """
    A descriptor for handling static configuration values.
    """
    def __get__(self, instance, owner):
        if not sw_check():
            return self.config_value if self.config_value is not None else None
        val = _global_call("getConfig", self.name)
        return self._wrap_config_value(val)

    def __set__(self, instance, value):
        if sw_check():
            raise ProgrammingError("Cannot modify static configuration after initialization.")
        if not isinstance(value, self.config_type) and value is not None:
            self.config_value = self.config_type(value)
        else:
            self.config_value = value


# class DynamicConfigDescriptor(ConfigDescriptor):
#     def __get__(self, instance, owner):
#         if not sw_check():
#             return self.config_value if self.config_value is not None else None
#         val = _global_call("getConfig", self.name)
#         return self._wrap_config_value(val)

#     def __set__(self, instance, value):
#         if not isinstance(value, self.config_type) and value is not None:
#             value = self.config_type(value)
#         if sw_check():
#             if isinstance(value, Path):
#                 value = str(value)
#             set_dynamic_config(self.name, value)
#         else:
#             self.config_value = value


class DynamicConfigDescriptor(StaticConfigDescriptor):
    """
    A descriptor for dynamic configuration values.

    Currently, dynamic configuration is not supported.
    """
    pass


class Config:
    """
    A class that manages various configuration settings.
    """
    config_dict: Dict[str, ConfigDescriptor] = dict()
    """
    :meta hide-value:
    """

    dataSync: int = StaticConfigDescriptor(int, 1)
    """
    :meta hide-value:

    Whether database logs are forced to persist to disk before the transaction is
    committed.

    - If `dataSync=1` (default), the redo logs, data, and metadata are forced to
      persist to disk.
    - If `dataSync=0`, the operating system will decide when to write the log files
      to disk.
    """

    decimalRoundingMode: str = StaticConfigDescriptor(str, "trunc")
    """
    :meta hide-value:

    Specifies the rounding mode for Decimal type. The default is `"trunc"`, meaning
    the decimal part is truncated. Set it to `"round"` to round the decimal part.
    It is applicable to the following conversion scenarios:

    - Parsing floating-point numeric strings to DECIMAL type (e.g., loading files
      with `loadText`).
    - Converting floating-point numbers to Decimal type.
    - Converting Decimal values to Integral type.
    - Converting high-precision Decimal values to low-precision Decimal values.

    Note
    ----
    The rounding mode for the first case is rounding. For other scenarios,
    truncation was used.
    """

    enableChunkGranularityConfig: bool = StaticConfigDescriptor(bool, True)
    """
    :meta hide-value:

    Specifies the chunk granularity to determine the level of the lock of a
    transaction. When writing to a chunk, the transaction locks it to prevent other
    transactions from writing to it.

    The default value is `True`. You can specify the chunk granularity with the
    parameter `chunkGranularity` of function `database`.

    If set to `False`, the chunk granularity is at the table level, i.e., each
    tablet of a partition is a chunk. Concurrent writes to different tables in the
    same partition are thus allowed.
    """

    enableConcurrentDimensionalTableWrite: bool = StaticConfigDescriptor(bool, False)
    """
    :meta hide-value:

    Whether to allow conducting concurrent write or update/delete on dimension
    tables.

    The default value is `False`, indicating concurrent write and update/delete is
    disabled for dimension tables.
    """

    enableDFS: bool = StaticConfigDescriptor(bool, False if sw_is_ce_edition() else True)
    """
    :meta hide-value:
    """

    enableInsertStatementForDFSTable: bool = StaticConfigDescriptor(bool, True)
    """
    :meta hide-value:

    Whether to enable the insert into statement for DFS tables. The default value is
    `True`.
    """

    enableLocalDatabase: bool = StaticConfigDescriptor(bool, False)
    """
    :meta hide-value:

    Whether to enable the creation of a local database. The default value is `False`.
    """

    home: Path = StaticConfigDescriptor(Path, None)
    """
    :meta hide-value:

    The DolphinDB home directory (`<HomeDir>`). It can only be specified in command
    line.
    """

    ignoreSpecialCharacterInPartitionId: bool = StaticConfigDescriptor(bool, False)
    """
    :meta hide-value:

    Whether to ignore ``":"`` and ``"."`` in partitioning columns when creating
    partition directories for value-partitioned tables with partitioning columns of
    STRING or SYMBOL type.

    The default value is `False`. The  "." and ":" will be included as part of the
    path, which means data written to the ".a:bc." and "abc" partitions will be
    separated into different paths.

    If set to `True`, keys like ``".a:bc."`` and "abc" of the partitioning column
    will map to the same directory path since ":" and "." are ignored. So data
    written to partitions ".a:bc." and "abc" will both end up being stored under
    "abc".
    """

    init: Path = StaticConfigDescriptor(Path, None)
    """
    :meta hide-value:

    This file is executed when the system starts. The default file is `{package
    install dir}/asset/dolphindb.dos`.

    It usually contains definitions of system-level functions that are visible to
    all users and cannot be overwritten.
    """

    license: Path = StaticConfigDescriptor(Path, None)
    """
    :meta hide-value:
    """

    localSite: str = StaticConfigDescriptor(str, None)
    """
    :meta hide-value:

    The LAN information of the node, including host address, port number and alias
    of the node, separated by ``":"``.
    """

    logFile: Path = StaticConfigDescriptor(Path, None)
    """
    :meta hide-value:

    The path and name of the log file. It displays the Swordfish configuration
    specifications, warnings, and error messages.
    """

    logicOrIgnoreNull: bool = StaticConfigDescriptor(bool, False)
    """
    :meta hide-value:

    Whether function `or` ignores null values.
    
    When set to False (default), it always returns NULL regardless of the value of
    the other operand, which matches the behavior in prior versions.

    When set to True:
    
    - If the other operand is non-zero, it returns True.
    - If the other operand is zero, it returns False.
    - If the other operand is a null value, it returns NULL.
    """

    logLevel: str = DynamicConfigDescriptor(str, "ERROR")
    """
    :meta hide-value:

    The level equal to and above which logs are printed to help users locate the
    error message in the log. From the lowest to the highest level, the possible
    values are `DEBUG`, `INFO`, `WARNING`, and `ERROR`. The default value is
    `ERROR`.
    """

    logRetentionTime: float = StaticConfigDescriptor(float, None)
    """
    :meta hide-value:

    To prevent excessive resource usage from old logs, the `logRetentionTime`
    parameter can be used to specify the amount of time (in days) to keep a log file
    before deleting it.

    The default value is 30 (of floating-point data type). For example, 0.5 means
    12 hours. If set to 0, log files are not deleted.
    """

    marketHolidayDir: Path = StaticConfigDescriptor(Path, None)
    """
    :meta hide-value:

    The directory to the file of market holidays. Either an absolute or relative
    directory can be specified.

    The system searches the relative directory in the following order: home
    directory of the node, the working directory of the node, and the directory with
    the DolphinDB executable.

    The default directory is `{package install dir}/asset/marketHoliday`. The file
    must be a single-column CSV file with `Date` data. Based on the CSV files under
    `marketHolidayDir`, a trading calendar is created with the file name as its
    identifier.

    Notes
    -----
    - Weekends are recognized as holidays by default; therefore, only weekday
      holidays need to be filled in the file.
    - It is recommended to name the file in Market Identifier Code, e.g.,
      `"XNYS.csv"`.
    """

    maxBlockSizeForReservedMemory: float = DynamicConfigDescriptor(float, None)
    """
    :meta hide-value:

    The maximum size (in units of KB) of the memory block that DolphinDB allocates
    for each memory request when its available memory is less than `reservedMemSize`.
    The default value is 64.

    It is not recommended to set it too high as exceptions or crashes may occur if
    there isn't enough memory left for critical database operations.
    """

    maxConnections: int = DynamicConfigDescriptor(int, None)
    """
    :meta hide-value:

    The maximum number of connections to the local node.
    """

    maxLogSize: int = StaticConfigDescriptor(int, None)
    """
    :meta hide-value:

    The system will archive the Swordfish log after it reaches the specified size
    limit (in MB). The default value is 1024 and the minimum value is 100.

    Upon reaching this limit, Swordfish automatically generates a new log with a
    timestamp prefix in seconds. The prefix is in the format of `<date><seq>`, e.g.,
    `20181109000`. `<seq>` has 3 digits and starts with `000`.
    """

    maxMemSize: float = DynamicConfigDescriptor(float, None)
    """
    :meta hide-value:

    The maximum memory (in units of GB) allocated to Swordfish. The default value is
    0, meaning no limits on memory usage. The value of `maxMemSize` cannot exceed
    the machine memory.
    """

    maxPartitionNumPerQuery: int = DynamicConfigDescriptor(int, 65536)
    """
    :meta hide-value:

    The maximum number of partitions that a single query can search. The default
    value is `65536`.
    """

    maxPubConnections: int = StaticConfigDescriptor(int, 64)
    """
    :meta hide-value:

    The maximum number of subscriber nodes that the publisher node can connect to.
    The default value is 64.

    For the node to serve as a publisher, we must set `maxPubConnections > 0`.
    """

    maxSubConnections: int = StaticConfigDescriptor(int, None)
    """
    :meta hide-value:

    The maximum number of publisher nodes that the subscriber node can connect to.
    The default value is 64.
    """

    maxSubQueueDepth: int = StaticConfigDescriptor(int, None)
    """
    :meta hide-value:

    The maximum depth (number of records) of a message queue on the subscriber node.
    The default value is `10,000,000`.
    """

    memLimitOfAllTempResults: float = DynamicConfigDescriptor(float, None)
    """
    :meta hide-value:

    The total memory limit (in GB) for all temporary results generated during SQL
    distributed queries. The default value is `20% * maxMemSize`.

    If the memory usage exceeds the limit, temporary results are spilled to disk.
    """

    memLimitOfQueryResult: float = DynamicConfigDescriptor(float, None)
    """
    :meta hide-value:

    The memory limit for a query result. The default value is `min(50% * maxMemSize,
    8G)`, and it must be smaller than `80% * maxMemSize`.
    """

    memLimitOfTaskGroupResult: float = DynamicConfigDescriptor(float, None)
    """
    :meta hide-value:

    In the Map phase of MapReduce, a single query is divided into several tasks,
    among which the remote tasks are sent to remote nodes in batches (task groups).
    `memLimitOfTaskGroupResult` is used to set the memory limit of a task group sent
    from the current node.

    The default value is min(20% * `maxMemSize`, 2G), and it must be smaller than
    50% * `maxMemSize`.
    """

    moduleDir: Path = StaticConfigDescriptor(Path, None)
    """
    :meta hide-value:

    The directory for the module files. It can be an absolute path or a relative
    directory, with `modules` as the default.

    The system searches the relative directory `modules` in the following order:
    home directory, the working directory, and the directory with the swordfish
    package.
    """

    newValuePartitionPolicy: str = StaticConfigDescriptor(str, "add")
    """
    :meta hide-value:

    How new data outside of existing VALUE partitions are handled in databases. It
    can be "add", "skip", or "fail".

    - `"add"` (default): Creates new VALUE partitions to add all data.
    - `"skip"`: Appends data that belongs to existing VALUE partitions and ignores
      out-of-scope data.
    - `"fail"`: Throws exception if out-of-scope data is included. None of the data
      will be written. In most cases, `"add"` is recommended.
    """

    nullAsMinValueForComparison: bool = StaticConfigDescriptor(bool, None)
    """
    :meta hide-value:

    Whether a null value is treated as the minimum value in data comparison. The
    default value is True.

    If it is set to False, the result of comparison involving null values is NULL.
    """

    OLAPCacheEngineSize: float = DynamicConfigDescriptor(float, 0.5)
    """
    :meta hide-value:

    The capacity of cache engine in units of GB. After cache engine is enabled, data
    is not written to disk until data in cache exceeds 30% of
    `OLAPCacheEngineSize`.

    The default value is 0.5. To enable the cache engine, we must set
    `OLAPCacheEngineSize` > 0 and `dataSync` = 1.
    """

    parseDecimalAsFloatingNumber: bool = StaticConfigDescriptor(bool, None)
    """
    :meta hide-value:

    Whether decimal numbers are parsed to Double or Decimal64 type.

    - If set to `True` (default), decimals are parsed to Double floating point
      numbers.
    - If set to `False`, decimals are parsed to Decimal64 fixed point numbers.
    """

    persistenceDir: Path = StaticConfigDescriptor(Path, None)
    """
    :meta hide-value:

    The directory where shared stream tables are persisted to. To enable
    persistence, `persistenceDir` must be specified.
    """

    # recoveryWorkers: int = DynamicConfigDescriptor(int, None)
    # """
    # :meta hide-value:
    # The number of workers that can be used to recover chunks synchronously in node
    # recovery. The default value is 1.

    # Notes
    # -----
    # If the number of existing threads is fewer than that of the newly configured
    # threads, the system will create the missing threads. If it is larger, the
    # system will block and reclaim the excess threads.
    # There is no hard upper limit on `recoveryWorkers`, but it is subject to the
    # constraints of the operating system.
    # """

    regularArrayMemoryLimit: float = StaticConfigDescriptor(float, None)
    """
    :meta hide-value:

    The limit on the maximum memory size (in MB) of a regular array. Its value must
    be a power of 2. The default value is 2048 (MB).

    The actual available memory is `min(regularArrayMemoryLimit, maxMemSize/2)`. If
    the memory occupied by an array exceeds this limit, the system will create a big
    array instead.
    """

    removeSpecialCharInColumnName: bool = StaticConfigDescriptor(bool, False)
    """
    :meta hide-value:

    Whether to normalize column names.

    - If set to `False` (default), column names can contain special characters
      (except underscores) or start without letters.
    - If set to `True`, column names are normalized.
    """

    reservedMemSize: float = DynamicConfigDescriptor(float, None)
    """
    :meta hide-value:

    A positive number specified in units of GB. When the available memory in
    Swordfish is less than `reservedMemSize`, Swordfish only allocates a memory
    block of limited size (as specified by `maxBlockSizeForReservedMemory`) for each
    memory request.

    `reservedMemSize` is provided to restrict the memory allocation for each memory
    request to improve the likelihood that there is enough memory for critical
    operations that use a small amount of memory (error reporting, rollbacks, etc.).

    For example, when data writes fail due to insufficient memory, the transactions
    can be rolled back to guarantee data consistency. If the parameter is not
    specified, the system sets `reservedMemSize` = 5% * `maxMemSize` and
    `reservedMemSize` must be between 64MB and 1GB.
    """

    stdoutLog: int = StaticConfigDescriptor(int, 1)
    """
    :meta hide-value:

    Where to output the system log. It can be:

    - 0: dolphindb.log;
    - 1 (default): stdout;
    - 2: both stdout and dolphindb.log.
    """

    # strictPermissionMode: bool = StaticConfigDescriptor(bool, True)
    # """
    # :meta hide-value:
    # Whether to enable strict permission mode. The default value is True. Operations
    # such as disk read/write are only allowed for administrators.

    # Related functions include: `saveTextFile`, `saveAsNpy`, `backup`, `restore`,
    # `restoreDB`, `restoreTable`, `backupDB`, `backupTable`, `migrate`, `file`,
    # `files`, `writeObject`, `readObject`, `loadPlugin`, `close`, `fflush`,
    # `mkdir`, `rmdir`, `rm`, `writeLog`, `run`, `runScript`, `test`, `saveTable`,
    # `savePartition`, `saveDualPartition`, `saveDatabase`, `saveText`,
    # `loadText`, `loadModule`, `saveModule`.
    # """

    subExecutors: int = StaticConfigDescriptor(int, 8)
    """
    :meta hide-value:

    The number of message processing threads in the subscriber node. Only when
    subscription is enabled is this parameter relevant.

    The default value is 8. If it is set to 0, it means the thread can conduct
    message parsing and can also process messages.
    """

    subThrottle: int = StaticConfigDescriptor(int, 1000)
    """
    :meta hide-value:

    A non-negative integer in milliseconds, indicating the interval at which the
    system checks whether the `throttle` parameter in the `subscribe` function has
    been reached.The default value is 1000.

    If the interval specified by the `throttle` parameter in `subscribe` is less
    than `subThrottle`, the `handler` parameter in `subscribe` will be triggered to
    process messages at an interval of `subThrottle`.

    To set `throttle` to less than 1 second, you need to modify the configuration
    parameter `subThrottle` first. For example, to set `throttle = 0.001` (second),
    please set `subThrottle = 1` first.

    Notes
    -----
    This parameter is only valid if the parameter `batch_size` is specified in
    function `subscribe`.
    """

    tcpNoDelay: bool = StaticConfigDescriptor(bool, None)
    """
    :meta hide-value:

    Whether to enable the `TCP_NODELAY` socket option. The default value is False.
    """

    tcpUserTimeout: int = StaticConfigDescriptor(int, None)
    """
    :meta hide-value:

    Set the socket option `TCP_USER_TIMEOUT`. The default value is 300000 (in ms).
    """

    tempResultsSpillDir: Path = StaticConfigDescriptor(Path, None)
    """
    :meta hide-value:

    The directory for storing temporary results generated during distributed queries
    when they exceed memory limits. The default directory is `<HomeDir>/tempResults`.

    Temporary results exceeding the memory limit (specified by
    `memLimitOfAllTempResults`) are spilled to the directory. Files are
    automatically deleted after query completion.

    Notes
    -----
    This directory is recreated after Swordfish initialization, deleting any
    existing contents.
    """

    TSDBCacheEngineSize: float = DynamicConfigDescriptor(float, 1)
    """
    :meta hide-value:

    A positive number indicating the capacity (in GB) of the TSDB cache engine. The
    default value is 1.

    The memory used by the cache engine may reach twice the set value as an extra
    memoryblock will be allocated to cache the incoming data while data in the
    original memory is being flushed to disk.

    - If the flush process is not fast enough, the newly allocated memory may also
      reach `TSDBCacheEngineSize` and thus block the writer thread.
    - If the parameter is set too small, data in the cache engine may be flushed to
      disk too frequently, thus affecting the write performance;
    - If set too high, a large volume of cached data is not flushed to disk until it
      reaches `TSDBCacheEngineSize` (or after 10 minutes).
    - If power failure or shutdown occurs in such cases, numerous redo logs are to
      be replayed when the system is restarting, causing a slow startup.
    """

    tzdb: Path = StaticConfigDescriptor(Path, None)
    """
    :meta hide-value:

    The directory of the time zone database. The default value is `{package install
    dir}/asset/tzdb`.
    """

    warningMemSize: float = StaticConfigDescriptor(float, 20)
    """
    :meta hide-value:

    When memory usage exceeds `warningMemSize` (in units of GB), the system will
    automatically clean up the cache of some databases to avoid OOM exceptions. The
    default value is 20.
    """

    workerNum: int = StaticConfigDescriptor(int, None)
    """
    :meta hide-value:

    The size of worker pool for regular interactive jobs. The default value is the
    number of CPU cores.
    """

    def __setitem__(self, key, value):
        self.config_dict[key].__set__(self, value)

    def __getitem__(self, key):
        return self.config_dict[key].__get__(self, type(self))

    def __str__(self):
        max_len = (max([len(k) for k in self.config_dict]) // 5 + 1) * 5
        str_list = [
            f"{k.ljust(max_len)}: {str(v.__get__(self, type(self)))}" for k, v in self.config_dict.items()
        ]
        return "\n".join(str_list)

    def build(self):
        """Builds a list of command-line arguments based on the configuration.

        Returns
        -------
        list
            A list of command-line arguments.
        """

        # step 1: config path [ENV_NAME_CONFIG, ENV_NAME_HOME, CWD]
        config_search_path: List[Path] = []
        if _getenv(ENV_NAME_CONFIG):
            config_search_path.append(_get_absolute_path_env(ENV_NAME_CONFIG))
        if _getenv(ENV_NAME_HOME):
            config_search_path.append(_get_absolute_path_env(ENV_NAME_HOME))
        config_search_path.append(Path(f"{os.getcwd()}"))

        extra_config = None

        for path in config_search_path:
            file_path = path / "swordfish.toml" if path.is_dir() else path
            if file_path.exists():
                extra_config = self.read_config_from_toml(file_path)
                break

        # step 2: home path [ENV_NAME_HOME, config["home"], CWD]
        home_search_path: List[Path] = []
        if _getenv(ENV_NAME_HOME):
            home_search_path.append(_get_absolute_path_env(ENV_NAME_HOME))
        if not self.config_dict["home"].is_default():
            home_search_path.append(self.home)
        home_search_path.append(Path(f"{os.getcwd()}"))

        assert len(home_search_path) > 0
        self.home = home_search_path[0]

        # step 3: license path [ENV_NAME_LICENSE, config["license"], home]
        license_search_path: List[Path] = []
        if _getenv(ENV_NAME_LICENSE):
            license_search_path.append(_get_absolute_path_env(ENV_NAME_LICENSE))
        if not self.config_dict["license"].is_default():
            license_search_path.append(self.license)
        license_search_path.append(self.home)

        for path in license_search_path:
            file_path = path / "dolphindb.lic" if path.is_dir() else path
            if file_path.exists():
                self.license = file_path
                break

        # step 4: localSite [ENV_NAME_HOST/PORT/ALIAS, config]
        host = _getenv(ENV_NAME_HOST)
        host = extra_config["host"] if host is None and extra_config else host
        host = "0.0.0.0" if host is None else host

        port = _getenv(ENV_NAME_PORT)
        port = extra_config["port"] if port is None and extra_config else port
        port = get_random_available_port() if port is None else port

        alias = _getenv(ENV_NAME_ALIAS)
        alias = extra_config["alias"] if alias is None and extra_config else alias
        alias = "default" if alias is None else alias

        if not sw_is_ce_edition():
            config.localSite = f"{host}:{port}:{alias}"

        # step 5: extra configs
        args = []
        if _getenv(ENV_NAME_EXTRA):
            args = [v.strip() for v in _getenv(ENV_NAME_EXTRA).split(" ")]

        if self.config_dict["init"].is_default():
            self.config_dict["init"].init(Path, Path(__file__).parent / "asset" / "dolphindb.dos")
        if self.config_dict["logFile"].is_default():
            self.config_dict["logFile"].init(Path, "dolphindb.log")
        if self.config_dict["marketHolidayDir"].is_default():
            self.config_dict["marketHolidayDir"].init(Path, Path(__file__).parent / "asset" / "marketHoliday")
        if self.config_dict["moduleDir"].is_default():
            self.config_dict["moduleDir"].init(Path, Path(__file__).parent / "asset" / "modules")
        if self.config_dict["tempResultsSpillDir"].is_default():
            self.config_dict["tempResultsSpillDir"].init(Path, "tempResults")
        if self.config_dict["persistenceDir"].is_default():
            self.config_dict["persistenceDir"].init(Path, "persistenceDir")
        if self.config_dict["tzdb"].is_default() and sys.platform.startswith("win"):
            self.config_dict["tzdb"].init(Path, Path(__file__).parent / "asset" / "tzdb")

        res_list = []
        for name, item in self.config_dict.items():
            value = item.get_value_str()
            if value is not None:
                res_list += [f"-{name}", value]
        return args + res_list

    def read_config_from_toml(self, file_path: Path):
        def _set_config(_configs: dict, config_name: str, k1: str, k2: str):
            val = _configs.get(k1, dict()).get(k2, None)
            if val is not None:
                setattr(self, config_name, val)

        configs = toml.load(file_path)

        _set_config(configs, "home", "initial", "home")
        host = configs.get("initial", dict()).get("host", None)
        port = configs.get("initial", dict()).get("port", None)
        alias = configs.get("initial", dict()).get("alias", None)

        classify = "initial"
        _set_config(configs, "init", classify, "init")
        _set_config(configs, "license", classify, "license")
        _set_config(configs, "marketHolidayDir", classify, "marketHolidayDir")
        _set_config(configs, "moduleDir", classify, "moduleDir")
        _set_config(configs, "tzdb", classify, "tzdb")

        classify = "logging"
        _set_config(configs, "stdoutLog", classify, "stdoutLog")
        _set_config(configs, "logFile", classify, "logFile")
        _set_config(configs, "logLevel", classify, "logLevel")
        _set_config(configs, "logRetentionTime", classify, "logRetentionTime")
        _set_config(configs, "maxLogSize", classify, "maxLogSize")

        classify = "network"
        _set_config(configs, "maxConnections", classify, "maxConnections")
        _set_config(configs, "tcpNoDelay", classify, "tcpNoDelay")
        _set_config(configs, "tcpUserTimeout", classify, "tcpUserTimeout")

        classify = "behavior"
        _set_config(configs, "decimalRoundingMode", classify, "decimalRoundingMode")
        _set_config(configs, "ignoreSpecialCharacterInPartitionId", classify, "ignoreSpecialCharacterInPartitionId")
        _set_config(configs, "logicOrIgnoreNull", classify, "logicOrIgnoreNull")
        _set_config(configs, "nullAsMinValueForComparison", classify, "nullAsMinValueForComparison")
        _set_config(configs, "parseDecimalAsFloatingNumber", classify, "parseDecimalAsFloatingNumber")
        _set_config(configs, "removeSpecialCharInColumnName", classify, "removeSpecialCharInColumnName")

        classify = "caching"
        _set_config(configs, "OLAPCacheEngineSize", classify, "OLAPCacheEngineSize")
        _set_config(configs, "TSDBCacheEngineSize", classify, "TSDBCacheEngineSize")

        classify = "concurrency"
        _set_config(configs, "workerNum", classify, "workerNum")

        classify = "resource"
        _set_config(configs, "dataSync", classify, "dataSync")
        _set_config(configs, "maxBlockSizeForReservedMemory", classify, "maxBlockSizeForReservedMemory")
        _set_config(configs, "maxMemSize", classify, "maxMemSize")
        _set_config(configs, "regularArrayMemoryLimit", classify, "regularArrayMemoryLimit")
        _set_config(configs, "reservedMemSize", classify, "reservedMemSize")
        _set_config(configs, "warningMemSize", classify, "warningMemSize")
        _set_config(configs, "maxPartitionNumPerQuery", classify, "maxPartitionNumPerQuery")
        _set_config(configs, "memLimitOfAllTempResults", classify, "memLimitOfAllTempResults")
        _set_config(configs, "memLimitOfQueryResult", classify, "memLimitOfQueryResult")
        _set_config(configs, "memLimitOfTaskGroupResult", classify, "memLimitOfTaskGroupResult")
        _set_config(configs, "tempResultsSpillDir", classify, "tempResultsSpillDir")

        classify = "storage"
        _set_config(configs, "newValuePartitionPolicy", classify, "newValuePartitionPolicy")

        classify = "streaming"
        _set_config(configs, "maxPubConnections", classify, "maxPubConnections")
        _set_config(configs, "maxSubConnections", classify, "maxSubConnections")
        _set_config(configs, "maxSubQueueDepth", classify, "maxSubQueueDepth")
        _set_config(configs, "persistenceDir", classify, "persistenceDir")
        _set_config(configs, "subExecutors", classify, "subExecutors")
        _set_config(configs, "subThrottle", classify, "subThrottle")

        return {
            "host": host,
            "port": port,
            "alias": alias,
        }


config = Config()
