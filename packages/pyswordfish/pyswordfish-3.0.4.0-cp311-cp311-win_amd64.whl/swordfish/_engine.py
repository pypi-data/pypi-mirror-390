from ._swordfishcpp import (  # type: ignore
    EngineType, StreamEngine, _create_engine,
    StreamBroadcastEngine, TimeSeriesEngine, CrossSectionalEngine,
    ReactiveStateEngine, StreamFilterEngine,
    ProgrammingError,
    Constant, Table, FunctionDef, MetaCode,
    _global_exec, _global_call
)

from .types import TypeDict
from . import data as sf_data

from typing import Literal, Any, List, Union, Tuple, Optional, Dict

import abc
from pathlib import Path


class Builder(abc.ABC):
    name: str
    """The name of the engine.
    """

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def submit(self) -> StreamEngine:
        """
        Abstract method to build a StreamEngine.

        Returns
        -------
        StreamEngine
            An instance of a built StreamEngine.
        """
        pass


def generate_create_method(builder_class):
    def _create_classmethod(cls, *args, **kwargs):
        return builder_class(*args, **kwargs)
    return _create_classmethod


def __internal_list_engine(dst_type: Optional[EngineType] = None):
    res_tb = _global_exec("getStreamEngineList()")
    engine_types = res_tb["engineType"].to_list()
    engine_names = res_tb["engineName"].to_list()
    users = res_tb["user"].to_list()
    res_list = []
    for engine_name, engine_type, user in zip(engine_names, engine_types, users):
        engine_type = EngineType.get_from_str(engine_type)
        if dst_type and engine_type != dst_type:
            continue
        res_list.append((engine_name, engine_type, user))
    return res_list


def generate_list_method(engine_class):
    def _list_classmethod(cls):
        return __internal_list_engine(engine_class.engine_type)
    return _list_classmethod


def generate_get_method(engine_class):
    def _get_classmethod(cls, name: str):
        engine = _global_call("getStreamEngine", name)
        if engine.engine_type != engine_class.engine_type:
            raise ProgrammingError("Cannot get StreamEngine with name: " + name)
        return engine
    return _get_classmethod


class StreamBroadcastEngineBuilder(Builder):
    def __init__(self, name, table_schema: Union[Table, TypeDict], outputs: List[Table]):
        super().__init__(name)
        if isinstance(table_schema, dict):
            table_schema = sf_data.table(types=table_schema, size=0, capacity=1)
        self._dummy = table_schema
        self._outs = outputs

    def submit(self) -> StreamBroadcastEngine:
        return _create_engine(EngineType.StreamBroadcastEngine, self.name, self._dummy, self._outs)


StreamBroadcastEngine.create = classmethod(generate_create_method(StreamBroadcastEngineBuilder))
StreamBroadcastEngine.list = classmethod(generate_list_method(StreamBroadcastEngine))
StreamBroadcastEngine.get = classmethod(generate_get_method(StreamBroadcastEngine))


class TimeSeriesEngineBuilder(Builder):
    def __init__(
        self, name: str, table_schema: Union[Table, TypeDict], outputs: Table,
        window_size, step, metrics, *,
        time_col: Optional[Union[List[str], str]] = None,
        use_system_time: bool = False,
        key_col: Optional[Union[List[str], str]] = None,
        garbage_size: int = 50000,
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
    ):
        super().__init__(name)
        if isinstance(table_schema, dict):
            table_schema = sf_data.table(types=table_schema, size=0, capacity=1)
        self._dummy = table_schema
        self._outputs = outputs
        self._window_size = window_size
        self._step = step
        self._metrics = metrics
        self.time_col(time_col)
        self.use_system_time(use_system_time)
        self.key_col(key_col)
        self.garbage_size(garbage_size)
        self.update_time(update_time)
        self.use_window_start_time(use_window_start_time)
        self.round_time(round_time)
        self.snapshot_dir(snapshot_dir)
        self.snapshot_interval_in_msg_count(snapshot_interval_in_msg_count)
        self.fill(fill)
        self.force_trigger_time(force_trigger_time)
        self.key_purge_freq_in_sec(key_purge_freq_in_sec)
        self.closed(closed)
        self.output_elapsed_microseconds(output_elapsed_microseconds)
        self.sub_window(sub_window)
        self.parallelism(parallelism)
        self.accepted_delay(accepted_delay)
        self.output_handler(output_handler)
        self.msg_as_table(msg_as_table)

    def time_col(self, val: Optional[Union[List[str], str]] = None):
        """
        Sets the time column(s) for the subscribed stream table.

        Parameters
        ----------
        val : Union[List[str], str], optional
            Specifies the time column(s). If provided as a list, it must contain
            exactly two elements: a date (as a DATE type) and a time (as a TIME,
            SECOND, or NANOTIME type). In such cases, the first column of the
            output table will combine these elements into a single datetime value,
            with the data type matching the result of `concatDateTime(date, time)`.
            Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._time_col = val
        return self

    def use_system_time(self, val: bool = False):
        """
        Sets whether to perform calculations based on system time when ingesting data.

        Parameters
        ----------
        val : bool, optional
            If True, the engine will regularly window the streaming data at fixed
            time intervals for calculations according to the ingestion time (local
            system time with millisecond precision, independent of any temporal
            columns in the streaming table) of each record. As long as a window
            contains data, the calculation will be performed automatically when the
            window ends. The first column in output table indicates the timestamp
            when the calculation occurred. If False, the engine windows data based
            on a specified time column in the stream table. The calculation for a
            window is triggered by the first record arriving after the previous
            window, excluding the triggering record. Defaults to False.

        Returns
        -------
        Self
            The instance itself.
        """
        self._use_system_time = val
        return self

    def key_col(self, val: Optional[Union[List[str], str]] = None):
        """
        Sets the name of the grouping column(s).

        Parameters
        ----------
        val : Union[List[str], str], optional
            The name of the grouping column(s). Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._key_col = val
        return self

    def garbage_size(self, val: int = 50000):
        """
        Sets the threshold for garbage collection of historical data.

        Parameters
        ----------
        val : int, optional
            The threshold for garbage collection in number of rows. Defaults to
            50,000.

        Returns
        -------
        Self
            The instance itself.
        """
        self._garbage_size = val
        return self

    def update_time(self, val: int = None):
        """
        Sets the interval to trigger window calculations before the window ends.

        Parameters
        ----------
        val : int, optional
            The interval to trigger window calculations. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._update_time = val
        return self

    def use_window_start_time(self, val: bool = False):
        """
        Sets whether the time column in the output table uses the starting time of
        the windows.

        Parameters
        ----------
        val : bool, optional
            Whether to use the starting time of the windows. If False, the
            timestamps in the output table represent the end time of the windows.
            If `window_size` is a list, `use_window_startTime` must be False.
            Defaults to False.

        Returns
        -------
        Self
            The instance itself.
        """
        self._use_window_start_time = val
        return self

    def round_time(self, val: bool = True):
        """
        Aligns the window boundary based on the specified alignment rule.

        Parameters
        ----------
        val : bool, optional
            If True, uses the multi-minute rule for alignment. If False, uses the
            one-minute rule. Defaults to True.

        Returns
        -------
        Self
            The instance itself.
        """
        self._round_time = val
        return self

    def snapshot_dir(self, val: Optional[Union[Path, str]] = None):
        """
        Sets the directory where the streaming engine snapshot is saved.

        Parameters
        ----------
        val : Union[Path, str], optional
            The directory path for saving the snapshot. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._snapshot_dir = str(val) if val is not None else None
        return self

    def snapshot_interval_in_msg_count(self, val: int = None):
        """
        Sets the number of messages to receive before saving the next snapshot.

        Parameters
        ----------
        val : int, optional
            The number of messages before the next snapshot. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._snapshot_interval_in_msg_count = val
        return self

    def fill(self, val: Union[Literal["none", "null", "ffill"], Constant, List[Union[Literal["null", "ffill"], Constant]]] = "none"):
        """
        Sets the filling method(s) to deal with an empty window (in a group).

        Parameters
        ----------
        val : Union[Literal["none", "null", "ffill"], Constant,
                   List[Union[Literal["null", "ffill"], Constant]]], optional
            The filling method or a list of filling methods. Defaults to "none".

        Returns
        -------
        Self
            The instance itself.
        """
        self._fill = val
        return self

    def force_trigger_time(self, val: int = None):
        """
        Sets the waiting time to force trigger calculation in uncalculated windows
        for each group.

        Parameters
        ----------
        val : int, optional
            The waiting time in milliseconds to trigger window calculation. Defaults
            to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._force_trigger_time = val
        return self

    def key_purge_freq_in_sec(self, val: int = None):
        """
        Sets the interval in seconds to remove groups with no incoming data for a
        long time.

        Parameters
        ----------
        val : int, optional
            The interval (in seconds) to purge inactive groups. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._key_purge_freq_in_sec = val
        return self

    def closed(self, val: Literal["left", "right"] = "left"):
        """
        Specifies whether the left or right boundary is included in the window.

        Parameters
        ----------
        val : Literal["left", "right"], optional
            Specifies which boundary is included. Defaults to "left".

        Returns
        -------
        Self
            The instance itself.
        """
        self._closed = val
        return self

    def output_elapsed_microseconds(self, val: bool = False):
        """
        Determines whether to output the elapsed time (in microseconds).

        Parameters
        ----------
        val : bool, optional
            Whether to output the elapsed time. Defaults to False.

        Returns
        -------
        Self
            The instance itself.
        """
        self._output_elapsed_microseconds = val
        return self

    def sub_window(self, val: Optional[Union[int, Constant]] = None):
        """
        Specifies the range of the subwindow within the window defined by
        `window_size`.

        Parameters
        ----------
        val : Union[int, Constant], optional
            The range of the subwindow. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._sub_window = val
        return self

    def parallelism(self, val: int = 1):
        """
        Sets the number of worker threads for parallel computation.

        Parameters
        ----------
        val : int, optional
            The number of worker threads. Defaults to 1.

        Returns
        -------
        Self
            The instance itself.
        """
        self._parallelism = val
        return self

    def accepted_delay(self, val: int = 0):
        """
        Sets the maximum delay for each window to accept data.

        Parameters
        ----------
        val : int, optional
            A positive integer specifying the maximum delay. Defaults to 0.

        Returns
        -------
        Self
            The instance itself.
        """
        self._accepted_delay = val
        return self

    def output_handler(self, val: FunctionDef = None):
        """
        Sets a unary or partial function to handle the output. If specified, the
        engine will not write calculation results to the output table directly.

        Parameters
        ----------
        val : FunctionDef, optional
            The function to handle the output. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._output_handler = val
        return self

    def msg_as_table(self, val: bool = False):
        """
        Sets whether the output data is passed into the function (specified by
        `output_handler`) as a table or as an AnyVector.

        Parameters
        ----------
        val : bool, optional
            Whether to pass data as a table (`True`) or as an AnyVector (`False`).
            Defaults to False.

        Returns
        -------
        Self
            The instance itself.
        """
        self._msg_as_table = val
        return self

    def submit(self) -> TimeSeriesEngine:
        return _create_engine(
            EngineType.TimeSeriesEngine, self.name,
            self._window_size, self._step, self._metrics,
            self._dummy, self._outputs,
            self._time_col,
            self._use_system_time,
            self._key_col,
            self._garbage_size,
            self._update_time,
            self._use_window_start_time,
            self._round_time,
            self._snapshot_dir,
            self._snapshot_interval_in_msg_count,
            self._fill,
            self._force_trigger_time,
            sf_data.Nothing,
            self._key_purge_freq_in_sec,
            self._closed,
            self._output_elapsed_microseconds,
            self._sub_window,
            self._parallelism,
            self._accepted_delay,
            self._output_handler,
            self._msg_as_table,
        )


TimeSeriesEngine.create = classmethod(generate_create_method(TimeSeriesEngineBuilder))
TimeSeriesEngine.list = classmethod(generate_list_method(TimeSeriesEngine))
TimeSeriesEngine.get = classmethod(generate_get_method(TimeSeriesEngine))


class CrossSectionalEngineBuilder(Builder):
    def __init__(
        self, name: str, table_schema: Union[Table, TypeDict],
        key_col: Union[List[str], str], *,
        metrics=None,
        output: Table = None,
        triggering_pattern: Literal["per_batch", "per_row", "interval", "key_count", "data_interval"] = "per_batch",
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
    ):
        super().__init__(name)
        if isinstance(table_schema, dict):
            table_schema = sf_data.table(types=table_schema, size=0, capacity=1)
        self._dummy = table_schema
        self._key_col = key_col
        self.metrics(metrics)
        self.output(output)
        self.triggering_pattern(triggering_pattern)
        self.triggering_interval(triggering_interval)
        self.use_system_time(use_system_time)
        self.time_col(time_col)
        self.last_batch_only(last_batch_only)
        self.context_by_col(context_by_col)
        self.snapshot_dir(snapshot_dir)
        self.snapshot_interval_in_msg_count(snapshot_interval_in_msg_count)
        self.output_elapsed_microseconds(output_elapsed_microseconds)
        self.round_time(round_time)
        self.key_filter(key_filter)
        self.updated_context_groups_only(updated_context_groups_only)

    def metrics(self, val: Union[MetaCode, List[MetaCode]] = None):
        """
        Specifies the formulas for calculation using MetaCode or an AnyVector.

        The value can be:
            - Built-in or user-defined aggregate functions, e.g., `<myfunc(qty)>`

            >>> @F.swordfish_udf
            >>> def myFunc(x):
            ...     return x + 1
            ...
            >>> with sf.meta_code() as m:
            ...     metircs = myFunc(m.col("qty"))

            - Expressions on previous results, e.g., `<avg(price1)>`.

            >>> with sf.meta_code() as m:
            ...     metrics = F.avg(m.col("price1"))

            - Calculations on multiple columns, e.g., `<[std(price1-price2)]>`.

            >>> with sf.meta_code() as m:
            ...     metrics = F.std(m.col("price1") - m.col("price2"))

            - Functions with multiple returns, such as `<func(price) as `col1`col2>`.

            >>> with sf.meta_code() as m:
            ...     metrics = m.col_alias(func(m.col("price")), ["col1", "col2"])

        The column names specified in `metrics` are not case-sensitive and can be
        inconsistent with the column names of the input tables.

        Parameters
        ----------
        val : Union[MetaCode, List[MetaCode]], optional
            MetaCode or an AnyVector specifying the formulas. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._metrics = val
        return self

    def output(self, val: Table = None):
        """
        Specifies the output table for the results.

        - If context_by_col is not specified, the output columns are in the following
          order:

          - The first column is of TIMESTAMP type, storing the time when each
            calculation starts. If ``time_col`` is specified, it takes the values of
            ``time_col``.

          - The column(s) storing calculation results. The data types of the
            column(s) must be the same as the results of metrics.

          - A column of LONG type storing the calculation time of each batch. Output
            only when output_elapsed_microseconds=True.

          - A column of INT type storing the number of records of each batch. Output
            only when output_elapsed_microseconds=True.

        - If context_by_col is specified, the output columns are in the following
          order:

          - The first column is of TIMESTAMP type, storing the time when each
            calculation starts. If time_col is specified, it takes the values of
            time_col.

          - The second column is the column specified by context_by_col.

          - The column(s) storing calculation results. The data types of the
            column(s) must be the same as the results of metrics.

          - A column of LONG type storing the calculation time of each batch. Output
            only when output_elapsed_microseconds=true.

          - A column of INT type storing the number of records of each batch. Output
            only when output_elapsed_microseconds=true.

        Parameters
        ----------
        val : Table, optional
            an in-memory table or a DFS table, by default None

        Returns
        -------
        Self
            The instance itself.
        """
        self._output = val
        return self

    _inner_pattern_map = {
        "per_batch": "perBatch",
        "per_row": "perRow",
        "interval": "interval",
        "key_count": "keyCount",
        "data_interval": "dataInterval",
    }

    def triggering_pattern(self, val: Literal["per_batch", "per_row", "interval", "key_count", "data_interval"] = "per_batch"):
        """
        Specifies how to trigger the calculations.
        The engine returns a result every time a calculation is triggered.

        Parameters
        ----------
        val : Literal["per_batch", "per_row", "interval", "key_count", "data_interval"], optional

            - 'per_batch' (default): Calculates when a batch of data arrives.

            - 'per_row': Calculates when a new record arrives.

            - 'interval': Calculates at intervals specified by `triggering_interval`,
              using system time.

            - 'key_count': When data with the same timestamp arrives in batches, the
              calculation is triggered when the number of keys with the latest
              timestamp reaches `triggering_interval`, or data with a newer timestamp
              arrives.

            - 'data_interval': Calculates at intervals based on timestamps in the data.
              Requires `time_col` to be specified and `use_system_time` to be False.

        .. note::
            To use 'key_count' or 'data_interval', `time_col` must be specified and
            `use_system_time` must be set to False. Out-of-order data will be
            discarded in these cases.

        Returns
        -------
        Self
            The instance itself.
        """
        self._triggering_pattern = val
        return self

    def triggering_interval(self, val: Any = None):
        """
        Sets the triggering interval for the system based on the triggering pattern.

        The behavior of `triggering_interval` depends on the value of
        `triggering_pattern`:

        - If `triggering_pattern` = 'interval', `triggering_interval` is a positive
          integer indicating the interval in milliseconds between 2 adjacent
          calculations. Default is 1,000 milliseconds. A calculation is triggered
          every `triggering_interval` milliseconds if the data in the engine has not
          been calculated.

        - If `triggering_pattern` = 'keyCount', `triggering_interval` can either be:

          - An integer specifying a threshold for the number of uncalculated
            records.

          - A tuple of 2 elements:

            - The first element is an integer specifying the threshold of records
              with the latest timestamp to trigger a calculation.

            - The second element can be either:

              - An int threshold

              - A Duration value. For example, when `triggering_interval` is set to (c1, c2):

                - If c2 is an integer and the number of keys with the latest
                  timestamp t1 doesn't reach c1, calculation will not be
                  triggered and the system goes on to save data with greater
                  timestamp t2 (t2>t1). Data with t1 will be calculated when
                  either of the events happens: the number of keys with
                  timestamp t2 reaches c2, or data with greater timestamp t3
                  (t3>t2) arrives. Note that c2 must be smaller than c1.

                - If c2 is a duration and the number of keys with the latest
                  timestamp t1 doesn't reach c1, calculation will not be
                  triggered and the system goes on to save data with greater
                  timestamp t2 (t2>t1). Once data with t2 starts to come in,
                  data with t1 will not be calculated until any of the events
                  happens: the number of keys with timestamp t1 reaches c1, or
                  data with greater timestamp t3 (t3>t2) arrives, or the
                  Duration c2 comes to an end.

        - If `triggering_pattern` = 'dataInterval', `triggering_interval` is a
          positive integer in the same units as the timestamps in `time_col`. Default
          is 1,000 milliseconds. A calculation is triggered for all data in the
          current window when the first record of the next window arrives. A
          calculation is triggered only for windows containing data.

        Parameters
        ----------
        val : Any, optional
            The triggering interval or conditions. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        if isinstance(val, int):
            val = sf_data.Int(val)
        self._triggering_interval = val
        return self

    def use_system_time(self, val: bool = True):
        """
        Sets whether calculations are performed based on the system time when data is
        ingested into the engine.

        - If `use_system_time` is True, the time column of output table is the system
          time.
        - If `use_system_time` is False, the `time_Col` parameter must be specified,
          and the time column of output table uses the timestamp of each record.

        Parameters
        ----------
        val : bool, optional
            Indicates whether to use system time for calculations. Defaults to True.

        Returns
        -------
        Self
            The instance itself.
        """
        self._use_system_time = val
        return self

    def time_col(self, val: Optional[str] = None):
        """
        Specifies the time column in the stream table to which the engine subscribes
        when `use_system_time` is False. The column must be of Timestamp type.

        Parameters
        ----------
        val : Optional[str], optional
            The name of the time column. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._time_col = val
        return self

    def last_batch_only(self, val: bool = False):
        """
        Determines whether to keep only the records with the latest timestamp in the
        engine.

        When `last_batch_only` is true, `triggering_pattern` must be set to
        'keyCount', and the cross-sectional engine will only maintain key values with
        the latest timestamp for calculation.

        Otherwise, the engine updates and retains all values for calculation.

        Parameters
        ----------
        val : bool, optional
            Whether to keep only the latest timestamped records. Defaults to False.

        Returns
        -------
        Self
            The instance itself.
        """
        self._last_batch_only = val
        return self

    def context_by_col(self, val: Optional[Union[List[str], str]] = None):
        """
        Specifies the grouping column(s) by which calculations are performed within
        groups. This parameter only takes effect if `metrics` and `output` are
        specified.

        If `metrics` contain only aggregate functions, the results will be the same as
        a SQL query using `group by`.

        Otherwise, the results will be consistent with using `context by`.

        Parameters
        ----------
        val : Optional[Union[List[str], str]], optional
            The grouping column(s) for the calculation. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._context_by_col = val
        return self

    def snapshot_dir(self, val: Optional[Union[Path, str]] = None):
        """
        Sets the directory where the streaming engine snapshot is saved.

        The directory must already exist, or an exception will be raised. If a
        snapshot directory is specified, the system checks for an existing snapshot in
        the directory when creating the streaming engine.

        If found, the snapshot is loaded to restore the engine's state. Multiple
        streaming engines can share a directory, with snapshot files named after the
        engine names.

        Snapshot file extensions:
            - `<engineName>.tmp`: Temporary snapshot.
            - `<engineName>.snapshot`: A snapshot that is flushed to disk.
            - `<engineName>.old`: If a snapshot with the same name exists, the previous
              one is renamed to `<engineName>.old`.

        Parameters
        ----------
        val : Optional[Union[Path, str]], optional
            The directory path for saving the snapshot. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._snapshot_dir = str(val) if val is not None else None
        return self

    def snapshot_interval_in_msg_count(self, val: Optional[int] = None):
        """
        Sets the number of messages to receive before saving the next snapshot.

        Parameters
        ----------
        val : Optional[int], optional
            The number of messages before the next snapshot. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._snapshot_interval_in_msg_count = val
        return self

    def output_elapsed_microseconds(self, val: bool = False):
        """
        Determines whether to output the elapsed time (in microseconds).

        The elapsed time is measured from when the calculation is triggered to when
        the result is output for each window. When both
        `output_elapsed_microseconds` and `useSystemTime` parameters are set to true,
        aggregate function cannot be used in `metrics`.

        Parameters
        ----------
        val : bool, optional
            Whether to output the elapsed time. Defaults to False.

        Returns
        -------
        Self
            The instance itself.
        """
        self._output_elapsed_microseconds = val
        return self

    def round_time(self, val: bool = True):
        """
        Aligns the window boundary based on the specified alignment rule.

        If the time precision is in milliseconds or seconds and the step is greater
        than one minute, this method determines whether to apply multi-minute or
        one-minute alignment.

        Parameters
        ----------
        val : bool, optional
            If True, uses the multi-minute rule for alignment. If False, uses the
            one-minute rule. Defaults to True.

        Returns
        -------
        Self
            The instance itself.
        """
        self._round_time = val
        return self

    def key_filter(self, val: Optional[MetaCode] = None):
        """
        Specifies the conditions for filtering keys in the keyed table returned by the
        engine.

        Only data with keys satisfying the filtering conditions will be taken for
        calculation. The MetaCode represents an expression or function call that
        returns a bool vector.

        Parameters
        ----------
        val : Optional[MetaCode], optional
            MetaCode of the filtering conditions. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._key_filter = val
        return self

    def updated_context_groups_only(self, val: bool = False):
        """
        Indicates whether to compute only the groups updated with new data since the
        last output.

        Parameters
        ----------
        val : bool, optional
            Whether to compute only updated groups. Defaults to False.

        Returns
        -------
        Self
            The instance itself.
        """
        self._updated_context_groups_only = val
        return self

    def submit(self) -> CrossSectionalEngine:
        return _create_engine(
            EngineType.CrossSectionalEngine,
            self.name, self._metrics, self._dummy,
            self._output, self._key_col,
            self._inner_pattern_map[str(self._triggering_pattern)],
            self._triggering_interval,
            self._use_system_time,
            self._time_col,
            self._last_batch_only,
            self._context_by_col,
            self._snapshot_dir,
            self._snapshot_interval_in_msg_count,
            sf_data.Nothing,
            self._output_elapsed_microseconds,
            self._round_time,
            self._key_filter,
            # self._updated_context_groups_only
        )


CrossSectionalEngine.create = classmethod(generate_create_method(CrossSectionalEngineBuilder))
CrossSectionalEngine.list = classmethod(generate_list_method(CrossSectionalEngine))
CrossSectionalEngine.get = classmethod(generate_get_method(CrossSectionalEngine))


class ReactiveStateEngineBuilder(Builder):
    def __init__(
        self, name: str, table_schema: Union[Table, TypeDict],
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
    ):
        super().__init__(name)
        if isinstance(table_schema, dict):
            table_schema = sf_data.table(types=table_schema, size=0, capacity=1)
        self._dummy = table_schema
        self._output = output
        self._metrics = metrics
        self.key_col(key_col)
        self.filter(filter)
        self.snapshot_dir(snapshot_dir)
        self.snapshot_interval_in_msg_count(snapshot_interval_in_msg_count)
        self.keep_order(keep_order)
        self.key_purge_filter(key_purge_filter)
        self.key_purge_freq_in_second(key_purge_freq_in_second)
        self.output_elapsed_microseconds(output_elapsed_microseconds)
        self.key_capacity(key_capacity)
        self.parallelism(parallelism)
        self.output_handler(output_handler)
        self.msg_as_table(msg_as_table)

    def key_col(self, val: Optional[Union[List[str], str]] = None):
        """
        Specifies the grouping column(s) for the calculation.

        The calculation is conducted within each group defined by the specified
        column(s).

        Parameters
        ----------
        val : Optional[Union[List[str], str]], optional
            The column(s) to group by. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._key_col = val
        return self

    def filter(self, val: Optional[MetaCode] = None):
        """
        Specifies the filtering conditions for the output table.

        The MetaCode represents the filtering conditions, which must be an
        expression and can only include columns of `dummy_table`. Multiple
        conditions can be combined using logical operators (and, or). Only
        results satisfying the filter conditions are included in the output
        table.

        Parameters
        ----------
        val : Optional[MetaCode], optional
            The MetaCode representing the filtering conditions. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._filter = val
        return self

    def snapshot_dir(self, val: Optional[Union[Path, str]] = None):
        """
        Sets the directory where the streaming engine snapshot is saved.

        The directory must already exist, or an exception will be raised. If a
        snapshot directory is specified, the system checks for an existing
        snapshot in the directory when creating the streaming engine.

        If found, the snapshot is loaded to restore the engine's state. Multiple
        streaming engines can share a directory, with snapshot files named after
        the engine names.

        Snapshot file extensions:
            - `<engineName>.tmp`: Temporary snapshot.
            - `<engineName>.snapshot`: A snapshot that is flushed to disk.
            - `<engineName>.old`: If a snapshot with the same name exists, the
              previous one is renamed to `<engineName>.old`.

        Parameters
        ----------
        val : Optional[Union[Path, str]], optional
            The directory path for saving the snapshot. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._snapshot_dir = str(val) if val is not None else None
        return self

    def snapshot_interval_in_msg_count(self, val: Optional[int] = None):
        """
        Sets the number of messages to receive before saving the next snapshot.

        Parameters
        ----------
        val : Optional[int], optional
            The number of messages before the next snapshot. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._snapshot_interval_in_msg_count = val
        return self

    def keep_order(self, val: Optional[bool] = None):
        """
        Specifies whether to preserve the insertion order of records in the output
        table.

        If `key_col` contains a time column, the default value is True; otherwise,
        it is False.

        Parameters
        ----------
        val : Optional[bool], optional
            Whether to preserve the insertion order. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._keep_order = val
        return self

    def key_purge_filter(self, val: Optional[MetaCode] = None):
        """
        Sets the filtering conditions to identify the data to be purged from the
        cache.

        To clean up unnecessary data after calculations, specify both
        `key_purge_filter` and `key_purge_freq_in_second`.

        This is MetaCode composed of conditional expressions that must refer to
        columns in the output table. The filter is effective only when `key_col`
        is specified.

        Parameters
        ----------
        val : Optional[MetaCode], optional
            The MetaCode filter conditions. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._key_purge_filter = val
        return self

    def key_purge_freq_in_second(self, val: Optional[int] = None):
        """
        Sets the time interval (in seconds) to trigger a purge. The purge is
        triggered when the time since the last data ingestion meets or exceeds
        this interval.

        The filter is effective only when `key_col` is specified.

        For each data ingestion, a purge is triggered if the following conditions
        are met:

        1. The time elapsed since the last data ingestion is equal to or greater
           than `key_purge_freq_in_second` (for the first check, the time elapsed
           between data ingestion and engine creation is used).
        2. If the first condition is met, `key_purge_filter` is applied to
           determine the data to be purged.
        3. The number of groups containing data to be purged is equal to or
           greater than 10% of the total groups in the engine.

        To check engine status before and after the purge, access the attribute
        `ReactiveStateEngine.stat`, where the `numGroups` field indicates the
        number of groups in the reactive state engine.

        Parameters
        ----------
        val : Optional[int], optional
            The time interval (in seconds) to trigger the purge. Defaults to None.

        Returns
        -------
        Self
            The instance itself.
        """
        self._key_purge_freq_in_second = val
        return self

    def output_elapsed_microseconds(self, val: bool = False):
        """
        Determines whether to output the elapsed time (in microseconds).

        The elapsed time is measured from when the calculation is triggered to
        when the result is output for each window. When both
        `output_elapsed_microseconds` and `useSystemTime` parameters are set to
        true, aggregate function cannot be used in `metrics`.

        Parameters
        ----------
        val : bool, optional
            Whether to output the elapsed time. Defaults to False.

        Returns
        -------
        Self
            The instance itself.
        """
        self._output_elapsed_microseconds = val
        return self

    def key_capacity(self, val: int = 1024):
        """
        A positive integer indicating the amount of memory allocated for buffering
        state of each group.

        The memory is allocated on a row basis. The default value is 1024. For
        data with a large number of groups, setting this parameter can reduce
        latency.

        Parameters
        ----------
        val : int, optional
            A positive integer. Defaults to 1024.

        Returns
        -------
        Self
            The instance itself.
        """
        self._key_capacity = val
        return self

    def parallelism(self, val: int = 1):
        """
        A positive integer no greater than 63, indicating the maximum number of
        workers that can run in parallel.

        The default value is 1. For large computation workloads, adjusting this
        parameter can effectively utilize computing resources and reduce
        computation time.

        Note: `parallelism` cannot exceed the lesser of the numbers of logical
        cores minus one.

        Parameters
        ----------
        val : int, optional
            A positive integer. Defaults to 1.

        Returns
        -------
        Self
            The instance itself.
        """
        self._parallelism = val
        return self

    def output_handler(self, val: Optional[FunctionDef] = None):
        """
        A unary function or a partial function with a single unfixed parameter.

        If set, the engine will not write the calculation results to the output
        table directly. Instead, the results will be passed as a parameter to the
        specified function.

        Parameters
        ----------
        val : Optional[FunctionDef], optional
            A unary function or a partial function with a single unfixed
            parameter. The default value is null, which means the result will be
            written to the output table.

        Returns
        -------
        Self
            The instance itself.
        """
        self._output_handler = val
        return self

    def msg_as_table(self, val: bool = False):
        """
        Sets whether the output data is passed into the function (specified by
        `output_handler`) as a Table or as an AnyVector. If True, the data is
        passed as a Table; otherwise, it is passed as AnyVector of columns.

        Parameters
        ----------
        val : bool, optional
            Whether to pass data as a Table (True) or as an AnyVector (False).
            Defaults to False.

        Returns
        -------
        Self
            The instance itself.
        """
        self._msg_as_table = val
        return self

    def submit(self) -> ReactiveStateEngine:
        return _create_engine(
            EngineType.ReactiveStateEngine,
            self.name, self._metrics, self._dummy,
            self._output,
            self._key_col,
            self._filter,
            self._snapshot_dir,
            self._snapshot_interval_in_msg_count,
            self._keep_order,
            self._key_purge_filter,
            self._key_purge_freq_in_second,
            sf_data.Nothing,
            self._output_elapsed_microseconds,
            self._key_capacity,
            self._parallelism,
            self._output_handler,
            self._msg_as_table,
        )


ReactiveStateEngine.create = classmethod(generate_create_method(ReactiveStateEngineBuilder))
ReactiveStateEngine.list = classmethod(generate_list_method(ReactiveStateEngine))
ReactiveStateEngine.get = classmethod(generate_get_method(ReactiveStateEngine))


filter_dict = Dict[Literal["timeRange", "condition", "handler"], Any]


class StreamFilterEngineBuilder(Builder):
    def __init__(
        self, name: str, table_schema: Union[Table, TypeDict],
        filter: Union[filter_dict, List[filter_dict]],
        *,
        msg_schema: Optional[Dict] = None,
        time_col: Optional[str] = None,
        condition_col: Optional[str] = None,
    ):
        super().__init__(name)
        if isinstance(table_schema, dict):
            table_schema = sf_data.table(types=table_schema, size=0, capacity=1)
        self._dummy = table_schema
        self._filter = filter
        self.msg_schema(msg_schema)
        self.time_col(time_col)
        self.condition_col(condition_col)

    def msg_schema(self, val: Optional[Dict] = None):
        self._msg_schema = val
        return self

    def time_col(self, val: Optional[str] = None):
        self._time_col = val
        return self

    def condition_col(self, val: Optional[str] = None):
        self._condition_col = val
        return self

    def submit(self) -> StreamFilterEngine:
        return _create_engine(
            EngineType.StreamFilterEngine,
            self.name, self._dummy, self._filter,
            self._msg_schema,
            self._time_col,
            self._condition_col,
        )


StreamFilterEngine.create = classmethod(generate_create_method(StreamFilterEngineBuilder))
StreamFilterEngine.list = classmethod(generate_list_method(StreamFilterEngine))
StreamFilterEngine.get = classmethod(generate_get_method(StreamFilterEngine))


def list() -> List[Tuple[str, EngineType, str]]:
    """
    Retrieves all stream engines in the system.

    Returns
    -------
    List[Tuple[str, str, str]]
        [engine_name, engine_type, user]
    """
    return __internal_list_engine()


def drop(name: str):
    """
    Drops a stream engine by its name.

    Parameters
    ----------
    name : str
        The name of the stream engine to be dropped.
    """
    _global_call("dropStreamEngine", name)


def get(name: str) -> StreamEngine:
    """
    Retrieves a stream engine by its name.

    Parameters
    ----------
    name : str
        The name of the stream engine to retrieve.

    Returns
    -------
    StreamEngine
        The corresponding StreamEngine.
    """
    return _global_call("getStreamEngine", name)
