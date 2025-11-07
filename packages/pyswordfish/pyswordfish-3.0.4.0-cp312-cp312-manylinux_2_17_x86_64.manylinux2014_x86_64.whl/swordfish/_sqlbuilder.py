from ._swordfishcpp import (  # type: ignore
    MetaCode, Table, Constant, Duration, Pair,
    ProgrammingError,
)

from . import (
    function as sf_F,
    connection as sf_conn,
    data as sf_data,
)

from typing import Literal, List, Dict, Union, Any, Tuple, overload, Iterable


from enum import Enum

import abc


def _process_expr(expr: Union[MetaCode, str]):
    if hasattr(expr, "__sf_constant__"):
        expr = expr.__sf_constant__
    if isinstance(expr, MetaCode):
        return expr
    if isinstance(expr, str):
        return sf_conn.meta_code().parse(str(expr))
    return sf_conn.meta_code().const(expr)


def _process_on_cols(on: Union[Iterable[str], str, None]):
    if on is None:
        return sf_data.DFLT
    if isinstance(on, Iterable) and not isinstance(on, str):
        return sf_data.vector([str(v) for v in on], type="STRING")
    return sf_data.scalar(on, type="STRING")


class JOINKIND(Enum):
    INNER_JOIN = 0
    OUTER_JOIN = 1
    LEFT_JOIN = 2
    LEFT_SEMI_JOIN = 3
    RIGHT_JOIN = 4
    PREFIX_JOIN = 5
    ASOF_JOIN = 6
    FULL_JOIN = 7
    WINDOW_JOIN = 8
    SORT_EQUI_JOIN = 9
    PREVAILING_WINDOW_JOIN = 10


class SQLBuilder:
    def __init__(self, t):
        self._t = t

    def update(self, **kwargs: MetaCode) -> "StatementUPDATE":
        return StatementUPDATE(self._t, **kwargs)

    def select(self, *args: Union[MetaCode, str], **kwargs: Union[MetaCode, str]) -> "StatementSELECT":
        return StatementSELECT(self._t, *args, **kwargs)

    def delete(self) -> "StatementDELETE":
        return StatementDELETE(self._t)

    def inner_join(
        self, right,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None
    ) -> MetaCode:
        return self._join(
            right, how="inner",
            on=on, left_on=left_on, right_on=right_on,
        )

    equi_join = inner_join

    def sort_equi_join(
        self, right,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None,
    ) -> MetaCode:
        return self._join(
            right, how="sort_equi",
            on=on, left_on=left_on, right_on=right_on,
        )

    def outer_join(self, right) -> MetaCode:
        return self._join(right, how="outer")

    cross_join = outer_join

    def left_join(
        self, right,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None,
    ) -> MetaCode:
        return self._join(
            right, how="left",
            on=on, left_on=left_on, right_on=right_on,
        )

    def left_semi_join(
        self, right,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None,
    ) -> MetaCode:
        return self._join(
            right, how="left_semi",
            on=on, left_on=left_on, right_on=right_on,
        )

    def right_join(
        self, left,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None,
    ) -> MetaCode:
        return self._join(
            left, how="right",
            on=on, left_on=left_on, right_on=right_on,
        )

    def prefix_join(
        self, right,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None,
    ) -> MetaCode:
        return self._join(
            right, how="prefix",
            on=on, left_on=left_on, right_on=right_on
        )

    def asof_join(
        self, right,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None,
    ) -> MetaCode:
        return self._join(
            right, how="asof",
            on=on, left_on=left_on, right_on=right_on
        )

    def full_join(
        self, right,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None,
    ) -> MetaCode:
        return self._join(
            right, how="full",
            on=on, left_on=left_on, right_on=right_on
        )

    def window_join(
        self, right,
        window: Union[Tuple[int, int], Tuple[Duration, Duration], Pair] = None,
        aggs: Union[List[MetaCode], MetaCode] = None,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None,
    ) -> MetaCode:
        return self._join(
            right, how="window",
            on=on, left_on=left_on, right_on=right_on,
            window=window, aggs=aggs,
        )

    def prevailing_window_join(
        self, right,
        window: Union[Tuple[int, int], Tuple[Duration, Duration], Pair] = None,
        aggs: Union[List[MetaCode], MetaCode] = None,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None,
    ) -> MetaCode:
        return self._join(
            right, how="prevailing_window",
            on=on, left_on=left_on, right_on=right_on,
            window=window, aggs=aggs,
        )

    def _join(
        self, right,
        how: Literal["inner", "outer", "left", "left_semi"] = "inner",
        *,
        on: Union[Iterable[str], str] = None,
        left_on: Union[Iterable[str], str] = None,
        right_on: Union[Iterable[str], str] = None,
        filter: Constant = None,
        left_filter: Constant = None,
        right_filter: Constant = None,
        window: Union[Tuple[int, int], Tuple[Duration, Duration], Pair] = None,
        aggs: Union[List[MetaCode], MetaCode] = None,
    ) -> MetaCode:
        kind_map = {
            'inner': JOINKIND.INNER_JOIN,
            'equi': JOINKIND.INNER_JOIN,
            'outer': JOINKIND.OUTER_JOIN,
            'cross': JOINKIND.OUTER_JOIN,
            'left': JOINKIND.LEFT_JOIN,
            'left_semi': JOINKIND.LEFT_SEMI_JOIN,
            'right': JOINKIND.RIGHT_JOIN,
            'prefix': JOINKIND.PREFIX_JOIN,
            'asof': JOINKIND.ASOF_JOIN,
            'full': JOINKIND.FULL_JOIN,
            'window': JOINKIND.WINDOW_JOIN,
            'sort_equi': JOINKIND.SORT_EQUI_JOIN,
            'prevailing_window': JOINKIND.PREVAILING_WINDOW_JOIN,
        }

        kind = kind_map[how]

        func_map = {
            JOINKIND.INNER_JOIN: "ej",
            JOINKIND.OUTER_JOIN: "cj",
            JOINKIND.LEFT_JOIN: "lj",
            JOINKIND.LEFT_SEMI_JOIN: "lsj",
            JOINKIND.RIGHT_JOIN: "rj",
            JOINKIND.PREFIX_JOIN: "pj",
            JOINKIND.ASOF_JOIN: "aj",
            JOINKIND.FULL_JOIN: "fj",
            JOINKIND.WINDOW_JOIN: "wj",
            JOINKIND.SORT_EQUI_JOIN: "sej",
            JOINKIND.PREVAILING_WINDOW_JOIN: "pwj",
        }

        func = func_map[kind]

        if on is not None:
            left_on = _process_on_cols(on)
            right_on = _process_on_cols(on)
        else:
            left_on = _process_on_cols(left_on)
            right_on = _process_on_cols(right_on)

        if filter is not None:
            left_filter = filter if filter is not None else sf_data.DFLT
            right_filter = sf_data.DFLT
        else:
            left_filter = left_filter if left_filter is not None else sf_data.DFLT
            right_filter = right_filter if right_filter is not None else sf_data.DFLT

        if window is not None:
            if (isinstance(window, list) or isinstance(window, tuple)) and len(window) == 2:
                window = sf_data.pair(window[0], window[1])
            if not isinstance(window, Pair):
                raise ProgrammingError("Invalid param: window.")
        else:
            window = sf_data.DFLT

        aggs = aggs if aggs is not None else sf_data.DFLT

        if kind in [JOINKIND.OUTER_JOIN]:
            with sf_conn.meta_code() as m:
                return m.make_table_joiner(func, self._t, right)
        if kind in [
            JOINKIND.INNER_JOIN, JOINKIND.LEFT_JOIN, JOINKIND.LEFT_SEMI_JOIN, JOINKIND.RIGHT_JOIN,
            JOINKIND.SORT_EQUI_JOIN,
        ]:
            with sf_conn.meta_code() as m:
                return m.make_table_joiner(func, self._t, right, left_on, right_on, left_filter, right_filter)
        if kind in [
            JOINKIND.ASOF_JOIN, JOINKIND.FULL_JOIN, JOINKIND.PREFIX_JOIN,
        ]:
            with sf_conn.meta_code() as m:
                return m.make_table_joiner(func, self._t, right, left_on, right_on)
        if kind in [JOINKIND.WINDOW_JOIN, JOINKIND.PREVAILING_WINDOW_JOIN]:
            with sf_conn.meta_code() as m:
                return m.make_table_joiner(func, self._t, right, window, aggs, left_on, right_on)


class WhereClause:
    _conditions: List[MetaCode] = None

    def where(self, *conditions):
        self._conditions = [_process_expr(cond) for cond in conditions]
        return self


class FromClause:
    _from_t: MetaCode = None

    def from_(self, t):
        self._from_t = t
        return self


class HavingClause:
    _having: MetaCode = None

    def having(self, *conditions):
        self._having = [_process_expr(cond) for cond in conditions]
        return self


class OrderbyClause:
    _orderby: MetaCode = None
    _asc_orderby: bool = True

    def orderby(self, *cols, asc: Union[bool, List[bool]] = True):
        self._orderby = [_process_expr(col) for col in cols]
        if isinstance(asc, bool):
            self._asc_orderby = asc
        elif isinstance(asc, Iterable) and not isinstance(asc, str):
            self._asc_orderby = [bool(x) for x in asc]
        else:
            raise ProgrammingError("asc must be bool or list of bool.")
        return self


class TopClause:
    _top: Any = None

    @overload
    def top(self, count: int) -> "TopClause":
        ...

    @overload
    def top(self, start: int, end: int) -> "TopClause":
        ...

    def top(self, start: int, end: int = None) -> "TopClause":
        if end is None:
            self._top = sf_data.scalar(start)
        else:
            self._top = sf_data.pair(start, end)
        return self


class MapClause:
    _map: bool = False

    def map(self, enable: bool = True):
        self._map = enable
        return self


class CsortClause:
    _csort: MetaCode = None
    _asc_csort: bool = True

    def csort(self, *cols, asc: Union[bool, List[bool]] = True):
        self._csort = [_process_expr(col) for col in cols]
        if isinstance(asc, bool):
            self._asc_csort = asc
        elif isinstance(asc, Iterable) and not isinstance(asc, str):
            self._asc_csort = [bool(x) for x in asc]
        else:
            raise ProgrammingError("asc must be bool or list of bool.")
        return self


class GROUPKIND(Enum):
    NONE = -1
    CONTEXTBY = 0
    GROUPBY = 1
    PIVOTBY = 2


class GroupByLike:
    _group_flag: GROUPKIND = GROUPKIND.NONE


class GroupByClause(GroupByLike, HavingClause):
    _groupby: MetaCode = None

    def groupby(self, *cols: Union[MetaCode, str], **key_cols: Union[MetaCode, str]):
        if self._group_flag not in [GROUPKIND.NONE, GROUPKIND.GROUPBY]:
            raise RuntimeError("Cannot specify group by clause after context by or pivot by.")
        fields = []
        with sf_conn.meta_code() as m:
            for field in cols:
                fields.append(_process_expr(field))
            for k, v in key_cols.items():
                fields.append(m.col_alias(_process_expr(v), k))
        self._groupby = fields
        self._group_flag = GROUPKIND.GROUPBY
        return self


class ContextByClause(GroupByLike, HavingClause, CsortClause):
    _contextby: Any = None

    def contextby(self, *cols: Union[MetaCode, str]):
        if self._group_flag not in [GROUPKIND.NONE, GROUPKIND.CONTEXTBY]:
            raise RuntimeError("Cannot specify context by clause after group by or pivot by.")
        self._contextby = [_process_expr(col) for col in cols]
        self._group_flag = GROUPKIND.CONTEXTBY
        return self


class PivotByClause(GroupByLike):
    _pivotby: MetaCode = None

    def pivotby(self, *cols: Union[MetaCode, str]):
        if self._group_flag not in [GROUPKIND.NONE, GROUPKIND.PIVOTBY]:
            raise RuntimeError("Cannot specify context by clause after group by or pivot by.")
        self._pivotby = [_process_expr(col) for col in cols]
        self._group_flag = GROUPKIND.PIVOTBY
        return self


class Statement(abc.ABC):
    def __init__(self, tb: Table):
        self._tb = tb

    @property
    def __sf_constant__(self) -> MetaCode:
        return self.__sf_meta_code__

    @property
    @abc.abstractmethod
    def __sf_meta_code__(self) -> MetaCode:
        pass

    def __str__(self):
        return str(self.__sf_meta_code__)

    def eval(self, conn=None):
        return self.__sf_meta_code__.eval(conn)


class StatementSELECT(
    Statement,
    WhereClause,
    GroupByClause,
    ContextByClause,
    PivotByClause,
    HavingClause,
    OrderbyClause,
    TopClause,
    MapClause,
):
    _exec: bool = False

    def __init__(self, tb: Table, *fields: MetaCode, **key_fields: MetaCode):
        super().__init__(tb)
        fields_ = []
        with sf_conn.meta_code() as m:
            for field in fields:
                fields_.append(_process_expr(field))
            for k, v in key_fields.items():
                fields_.append(m.col_alias(_process_expr(v), k))
            if not fields_:
                fields_ = m.col("*")
        self._fields = fields_

    @property
    def __sf_meta_code__(self) -> MetaCode:
        p_fields = self._fields
        p_table = self._tb
        p_where = self._conditions if self._conditions is not None else sf_data.DFLT
        if self._group_flag == GROUPKIND.GROUPBY:
            p_groupby = self._groupby
        elif self._group_flag == GROUPKIND.CONTEXTBY:
            p_groupby = self._contextby
        elif self._group_flag == GROUPKIND.PIVOTBY:
            p_groupby = self._pivotby
        else:
            p_groupby = sf_data.DFLT
        p_groupflag = self._group_flag.value if self._group_flag != GROUPKIND.NONE else sf_data.DFLT
        p_csort = self._csort if self._csort is not None else sf_data.DFLT
        p_ascsort = self._asc_csort if self._csort is not None else sf_data.DFLT
        p_having = self._having if self._having is not None else sf_data.DFLT
        p_orderby = self._orderby if self._orderby is not None else sf_data.DFLT
        p_ascorder = self._asc_orderby if self._orderby is not None else sf_data.DFLT
        p_top = self._top if self._top is not None else sf_data.DFLT
        p_exec = self._exec
        p_map = self._map
        with sf_conn.empty_context():
            return sf_F.sql(
                p_fields,
                p_table,
                p_where,
                p_groupby,
                p_groupflag,
                p_csort,
                p_ascsort,
                p_having,
                p_orderby,
                p_ascorder,
                p_top,
                sf_data.DFLT,
                p_exec,
                p_map
            )


class StatementEXECUTE(Statement):
    _exec: bool = True


class StatementUPDATE(Statement, FromClause, WhereClause, ContextByClause):
    def __init__(self, tb: Table, **kwargs: MetaCode):
        super().__init__(tb)
        set_ = []
        with sf_conn.meta_code() as m:
            for k, v in kwargs.items():
                set_.append(m.col_alias(_process_expr(v), k))
        self._set = set_

    @property
    def __sf_meta_code__(self) -> MetaCode:
        p_table = self._tb
        p_updates = self._set
        p_from = self._from_t if self._from_t is not None else sf_data.DFLT
        p_where = self._conditions if self._conditions is not None else sf_data.DFLT
        p_contextby = self._contextby if self._contextby is not None else sf_data.DFLT
        p_csort = self._csort if self._csort is not None else sf_data.DFLT
        p_asccsort = self._asc_csort if self._csort is not None else sf_data.DFLT
        p_having = self._having if self._having is not None else sf_data.DFLT
        with sf_conn.empty_context():
            return sf_F.sqlUpdate(
                p_table,
                p_updates,
                p_from,
                p_where,
                p_contextby,
                p_csort,
                p_asccsort,
                p_having,
            )


class StatementDELETE(Statement, WhereClause, FromClause):
    def __init__(self, tb):
        super().__init__(tb)

    @property
    def __sf_meta_code__(self) -> MetaCode:
        p_table = self._tb
        p_where = self._conditions if self._conditions is not None else sf_data.DFLT
        p_from = self._from_t if self._from_t is not None else sf_data.DFLT
        with sf_conn.empty_context():
            return sf_F.sqlDelete(
                p_table,
                p_where,
                p_from,
            )


def msql(table: Union[Table, MetaCode]):
    return SQLBuilder(table)
