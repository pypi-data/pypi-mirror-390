from . import backtest

from ..._swordfishcpp import (  # type: ignore
    ProgrammingError,
    FunctionDef,
    Constant,
    check_is_nothing,
)

from ..._translator import (
    Variable, VariableMode, VariableFrame,
    StandardVisitor,
)

from ..._connection import connect as sf_connect

from ...data import (
    dictionary as sf_dictionary,
    DFLT as sf_DFLT,
    create_partial,
)

from ... import data as sf_data

import ast
import inspect
import warnings
import sys

from types import FunctionType, FrameType
from typing import (
    List, Union, Dict,
)

AccountType = backtest.AccountType
MarketDataType = backtest.MarketDataType


class FakeVariable(Variable):
    def __init__(self, data=None):
        super().__init__(data, VariableMode.FAKE)

    def dot(self, o):
        raise ProgrammingError("Cannot use self directly.")

    def at(self, o):
        raise ProgrammingError("Cannot use self directly.")

    def call(self, args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
        raise ProgrammingError("Cannot use self directly.")

    def process(self, visitor):
        raise ProgrammingError("Cannot use self directly.")


class TupleVariable(FakeVariable):
    def __init__(self, data):
        super().__init__(data)

    def process(self, visitor):
        return f"""({','.join([process(v, visitor) for v in self.data])})"""


class LiteralVariable(FakeVariable):
    def __init__(self, data: str):
        super().__init__(data)

    def process(self, visitor):
        return self.data


class DecorateArg(FakeVariable):
    def __init__(self, real: Variable, type_method: str, type_args: List[str] = None):
        super().__init__(real)
        self.type_method = type_method
        self.type_args = type_args or []

    def process(self, visitor):
        if isinstance(self.data, Variable):
            var_str = self.data.process(visitor)
        else:
            var_str = str(self.data)
        if self.type_args:
            args_str = ", ".join(self.type_args)
            return f"{self.type_method}({var_str}, {args_str})"
        else:
            return f"{self.type_method}({var_str})"


class AccountTypeVariable(FakeVariable):
    def __init__(self, kind: AccountType):
        super().__init__(kind)

    def process(self, visitor):
        return f'''"{self.data.value}"'''


class MarketDataTypeVariable(FakeVariable):
    def __init__(self, kind: backtest.MarketDataType):
        super().__init__(kind)

    def process(self, visitor):
        return f'''"{self.data.value}"'''


def _check_enum_type(v: Variable):
    if isinstance(v, Variable) and v.mode == VariableMode.PYTHON:
        if isinstance(v.data, AccountType):
            return AccountTypeVariable(v.data)
        if isinstance(v.data, backtest.MarketDataType):
            return MarketDataTypeVariable(v.data)
    return v


def _wrapper_submit_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["msg"]
    py_kwargs = ["label", "order_type", "account_type"]
    real_order = ["msg", "label", "order_type", "account_type"]
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return result


def _wrapper_submit_limit_tp_sl_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = [
        "code", "exchange", "time", "order_type", "order_price", "stop_loss_price",
        "take_profit_price", "quantity", "direct", "slippage", "order_validity", "expiration_time"
    ]
    py_kwargs = ["label", "account_type"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return [TupleVariable(result[:12])] + result[12:13] + [LiteralVariable("5")] + result[13:]


def _wrapper_submit_market_tp_sl_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = [
        "code", "exchange", "time", "order_type", "order_price", "stop_loss_price",
        "take_profit_price", "quantity", "direct", "slippage", "order_validity", "expiration_time"
    ]
    py_kwargs = ["label", "account_type"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return [TupleVariable(result[:12])] + result[12:13] + [LiteralVariable("6")] + result[13:]


def _wrapper_submit_ask_bid_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = [
        "code",
        "exchange",
        "time",
        "order_type",
        "bid_offset_flag",
        "bid_price",
        "bid_qty",
        "ask_offset_flag",
        "ask_price",
        "ask_qty",
        "bid_difftolerance",
        "ask_difftolerance",
        "quantity_allowed",
    ]
    py_kwargs = ["label", "account_type"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return [TupleVariable(result[:13])] + result[13:14] + [LiteralVariable("8")] + result[14:]


def _wrapper_submit_auto_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = [
        "code",
        "exchange",
        "time",
        "order_type",
        "order_price",
        "stop_price",
        "quantity",
        "direct",
        "order_validity",
    ]
    py_kwargs = ["label", "account_type"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return [TupleVariable(result[:9])] + result[9:10] + [LiteralVariable("9")] + result[10:]


def _wrapper_cancel_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = []
    py_kwargs = ["symbol", "orders", "label"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return result


def _wrapper_get_open_orders(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = []
    py_kwargs = ["symbol", "orders", "label", "output_queue_position"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return result


def _wrapper_update_position(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["symbol", "quantity"]
    py_kwargs = ["price"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return result


def _wrapper_subscribe_indicator(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["market_type", "metrics"]
    py_kwargs = ["account_type"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return result


def _wrapper_submit_stock_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["code", "time", "order_type", "order_price", "quantity", "direct"]
    py_kwargs = ["label", "account_type"]
    real_order = ["code", "time", "order_type", "order_price", "quantity", "direct", "label", "account_type"]
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return [TupleVariable(result[:6])] + result[6:7] + [LiteralVariable("0")] + result[7:]


def _wrapper_get_today_pnl(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["symbol"]
    py_kwargs = []
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return result


def _wrapper_submit_futures_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["code", "exchange", "time", "order_type", "order_price", "stop_price", "quantity", "direct", "order_validity"]
    py_kwargs = ["label", "account_type"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return [TupleVariable(result[:9])] + result[9:10] + [LiteralVariable("0")] + result[10:]


def _wrapper_submit_option_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["code", "exchange", "time", "order_type", "order_price", "stop_price", "quantity", "direct", "order_validity"]
    py_kwargs = ["label", "account_type"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return [TupleVariable(result[:9])] + result[9:10] + [LiteralVariable("0")] + result[10:]


def _wrapper_submit_margin_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["code", "time", "order_type", "order_price", "quantity", "direct"]
    py_kwargs = ["label", "account_type"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return [TupleVariable(result[:6])] + result[6:7] + [LiteralVariable("0")] + result[7:]


def _wrapper_get_margin_secu_position(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = []
    py_kwargs = ["symbols"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return result


def _wrapper_get_margin_trading_position(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = []
    py_kwargs = ["symbols"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return result


def _wrapper_get_secu_lending_position(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = []
    py_kwargs = ["symbols"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return result


def _wrapper_submit_bond_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["code", "time", "order_type", "settlement_speed", "bid_price", "bid_quantity", "ask_price", "ask_quantity", "direct", "order_id", "channel"]
    py_kwargs = ["label", "account_type"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return [TupleVariable(result[:11])] + result[11:12] + [LiteralVariable("0")] + result[12:]


def _wrapper_submit_crypto_order(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["code", "exchange", "time", "order_type", "order_price", "stop_loss_price", "take_profit_price", "quantity", "direct", "slippage", "order_validity", "expiration_time"]
    py_kwargs = ["label", "account_type"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    return [TupleVariable(result[:12])] + result[12:13] + [LiteralVariable("0")] + result[13:]


def _wrapper_get_position(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = []
    py_kwargs = ["symbol"]
    real_order = ["symbol"]
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    return arg_map.apply(args, kwargs)


def _wrapper_set_position(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = ["symbol", "qty", "order_price"]
    py_kwargs = ["last_price"]
    real_order = py_args + py_kwargs
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    result = arg_map.apply(args, kwargs)
    result[1] = DecorateArg(result[1], "long")
    return result


def _wrapper_get_daily_position(args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
    py_args = []
    py_kwargs = ["symbol"]
    real_order = ["symbol"]
    arg_map = ArgsMap(py_args, py_kwargs, real_order)
    return arg_map.apply(args, kwargs)


class SelfVariable(FakeVariable):
    """Self is StrategyTemplate.
    """
    def __init__(self, self_name: str, context_name: str):
        self.self_name = self_name
        super().__init__(f"""{context_name}["engine"]""")

    def dot(self, o: str):
        if o == "accounts":
            return AccountsVariable(self)
        if o == "submit_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_order, self)
        if o == "submit_limit_tp_sl_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_limit_tp_sl_order, self)
        if o == "submit_market_tp_sl_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_market_tp_sl_order, self)
        if o == "submit_ask_bid_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_ask_bid_order, self)
        if o == "submit_auto_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_auto_order, self)
        if o == "cancel_order":
            return FunctionVariable(backtest.plugin_backtest_cancelOrder, _wrapper_cancel_order, self)
        if o == "get_open_orders":
            return FunctionVariable(backtest.plugin_backtest_backtestGetOpenOrders, _wrapper_get_open_orders, self)
        if o == "update_position":
            return FunctionVariable(backtest.plugin_backtest_updatePosition, _wrapper_update_position, self)
        if o == "universe":
            return AttributeVariable(None, backtest.plugin_backtest_setUniverse, self)
        if o == "subscribe_indicator":
            return FunctionVariable(backtest.plugin_backtest_subscribeIndicator, _wrapper_subscribe_indicator, self)
        if o == "submit_stock_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_stock_order, self)
        if o == "get_today_pnl":
            return FunctionVariable(backtest.plugin_backtest_getTodayPnl, _wrapper_get_today_pnl, self)
        if o == "stock_total_portfolios":
            return AttributeVariable(backtest.plugin_backtest_getStockTotalPortfolios, None, self)
        if o == "submit_futures_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_futures_order, self)
        if o == "futures_total_portfolios":
            return AttributeVariable(backtest.plugin_backtest_getFuturesTotalPortfolios, None, self)
        if o == "submit_option_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_option_order, self)
        if o == "option_total_portfolios":
            return AttributeVariable(backtest.plugin_backtest_getOptionTotalPortfolios, None, self)
        if o == "submit_margin_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_margin_order, self)
        if o == "get_margin_secu_position":
            return FunctionVariable(backtest.plugin_backtest_getMarginSecuPosition, _wrapper_get_margin_secu_position, self)
        if o == "get_margin_trading_position":
            return FunctionVariable(backtest.plugin_backtest_getMarginTradingPosition, _wrapper_get_margin_trading_position, self)
        if o == "get_secu_lending_position":
            return FunctionVariable(backtest.plugin_backtest_getSecuLendingPosition, _wrapper_get_secu_lending_position, self)
        if o == "submit_bond_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_bond_order, self)
        if o == "submit_crypto_order":
            return FunctionVariable(backtest.plugin_backtest_submitOrder, _wrapper_submit_crypto_order, self)
        raise ProgrammingError("Unsupported self method: ", o)

    def process(self, visitor):
        return self.data


class DefaultVariable(FakeVariable):
    def __init__(self):
        super().__init__()

    def process(self, visitor):
        return " "


class ArgsMap(dict):
    def __init__(self, args, kwargs, orders):
        super().__init__()
        params = []
        for arg in args:
            params.append(inspect.Parameter(arg, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD))
        for arg in kwargs:
            params.append(inspect.Parameter(arg, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, default=DefaultVariable()))
        self.sig = inspect.Signature(params)
        self.orders = orders

    def apply(self, args, kwargs):
        bound = self.sig.bind(*args, **kwargs)
        bound.apply_defaults()
        result = {
            v: None for v in self.orders
        }
        for k, v in bound.arguments.items():
            result[k] = v
        return [_ for _ in result.values()]


class FunctionVariable(FakeVariable):
    def __init__(self, func: FunctionDef, args_wrapper: FunctionType, self_var: SelfVariable):
        self.args_wrapper = args_wrapper
        self.func = func
        self.self_var = self_var
        super().__init__(func)

    def call(self, args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
        # F(args, kwargs)
        return FunctionCallVariable(self, self.args_wrapper(args, kwargs), self.self_var)


class FunctionCallVariable(FakeVariable):
    def __init__(self, func: FunctionVariable, args, self_var: SelfVariable):
        self.func = func
        self.args = args
        self.self_var = self_var
        super().__init__()

    def process(self, visitor: StandardVisitor):
        name = visitor.update_argvar(self.func)
        if self.args:
            arg_str = ", ".join([process(v, visitor) for v in self.args])
            return f"{name}({self.self_var.data}, {arg_str})"
        else:
            return f"{name}({self.self_var.data})"


class AttributeVariable(FakeVariable):
    def __init__(self, getter: FunctionDef, setter: FunctionDef, self_var: SelfVariable):
        self.getter = getter
        self.setter = setter
        self.self_var = self_var
        super().__init__()

    def assign(self, value: Variable):
        # self.attr = value
        return AttributeAssignVariable(self, value, self.self_var)

    def process(self, visitor):
        if self.getter is None:
            raise ProgrammingError("Unsupported get attribute.")
        name = visitor.update_argvar(Variable(self.getter, VariableMode.PYTHON))
        return f"{name}({self.self_var.data})"


class AttributeAssignVariable(FakeVariable):
    def __init__(self, attr: AttributeVariable, value: Variable, self_var: SelfVariable):
        self.attr = attr
        self.value = value
        self.self_var = self_var
        super().__init__()

    def process(self, visitor):
        if self.setter is None:
            raise ProgrammingError("Unsupported set attribute.")
        name = visitor.update_argvar(Variable(self.attr.setter, VariableMode.PYTHON))
        return f"{name}({self.self_var.data}, {process(self.value, visitor)})"


class AccountsVariable(FakeVariable):
    def __init__(self, self_var):
        super().__init__()
        self.self_var = self_var

    def at(self, o: Union[Variable, str]):
        if isinstance(o, Variable) and o.mode == VariableMode.PYTHON:
            o = o.data
        if isinstance(o, str):
            o = AccountType(o)
        if isinstance(o, AccountType):
            o = AccountTypeVariable(o)
        return ExactAccountVariable(o, self.self_var)


class ExactAccountVariable(FakeVariable):
    def __init__(self, kind: AccountTypeVariable, self_var: SelfVariable):
        super().__init__(kind)
        self.self_var = self_var

    def dot(self, o: str):
        # self.accounts[AccountType].#o
        if o == "cash":
            return ExactAccountAttributeVariable(backtest.plugin_backtest_getAvailableCash, None, self)
        if o == "trade_details":
            return ExactAccountAttributeVariable(backtest.plugin_backtest_getTradeDetails, None, self)
        if o == "get_position":
            return ExactAccountFunctionVariable(backtest.plugin_backtest_getPosition, _wrapper_get_position, self)
        if o == "set_position":
            return ExactAccountFunctionVariable(backtest.plugin_backtest_setPosition, _wrapper_set_position, self)
        if o == "get_daily_position":
            return ExactAccountFunctionVariable(backtest.plugin_backtest_getDailyPosition, _wrapper_get_daily_position, self)
        if o == "total_portfolios":
            return ExactAccountAttributeVariable(backtest.plugin_backtest_getTotalPortfolios, None, self)
        if o == "daily_total_portfolios":
            return ExactAccountAttributeVariable(backtest.plugin_backtest_getDailyTotalPortfolios, None, self)
        if o == "return_summary":
            return ExactAccountAttributeVariable(backtest.plugin_backtest_getReturnSummary, None, self)
        raise ProgrammingError("Unsupported account method: ", o)


class ExactAccountAttributeVariable(AttributeVariable):
    def __init__(self, getter: FunctionDef, setter: FunctionDef, account: ExactAccountVariable):
        super().__init__(getter, setter, account.self_var)
        self.account = account

    def assign(self, value: Variable):
        raise ProgrammingError("Unsupported set account attribute.")

    def process(self, visitor):
        name = visitor.update_argvar(Variable(self.getter, VariableMode.PYTHON))
        if self.account.data.data == AccountType.DEFAULT:
            return f"{name}({self.self_var.data})"
        else:
            return f"{name}({self.self_var.data}, {process(self.account.data, visitor)})"


class ExactAccountFunctionVariable(FunctionVariable):
    def __init__(self, func: FunctionDef, args_wrapper, account: ExactAccountVariable):
        super().__init__(func, args_wrapper, account.self_var)
        self.account = account

    def call(self, args: List[Union[str, Variable]], kwargs: Dict[str, Union[str, Variable]]):
        # F(args, kwargs)
        return ExactAccountFunctionCallVariable(self, self.args_wrapper(args, kwargs), self.account)


class ExactAccountFunctionCallVariable(FunctionCallVariable):
    def __init__(self, func: ExactAccountFunctionVariable, args, account: ExactAccountVariable):
        super().__init__(func, args, account.self_var)
        self.account = account

    def process(self, visitor):
        name = visitor.update_argvar(self.func)
        if self.args:
            args_str = ", ".join([process(v, visitor) for v in self.args])
        if self.account.data.data == AccountType.DEFAULT:
            if self.args:
                return f"{name}({self.self_var.data}, {args_str})"
            else:
                return f"{name}({self.self_var.data})"
        if self.args:
            return f"{name}({self.self_var.data}, {args_str}, {process(self.account.data, visitor)})"
        else:
            return f"{name}({self.self_var.data}, {process(self.account.data, visitor)})"


def process(data, visitor) -> str:
    if isinstance(data, Variable):
        return data.process(visitor)
    return str(data)


class MethodVisitor(StandardVisitor):
    def __init__(self):
        super().__init__()

    def add_arguments(self, node):
        if node.posonlyargs:
            raise ValueError("Unsupported position only arguments.")
        if node.kwonlyargs or node.kw_defaults:
            raise ValueError("Unsupported keyword only arguments.")
        args = [arg.arg for arg in node.args]
        self_name = args[0]
        self.self_var = SelfVariable(self_name, args[1])
        args = set(args[1:])
        frame = VariableFrame.createArgsFrame(args)
        frame.update(self_name, self.self_var)
        self.stack.push(frame)

    def visit_arguments(self, node: ast.arguments):
        if node.posonlyargs:
            raise ValueError("Unsupported position only arguments.")
        if node.kwonlyargs or node.kw_defaults:
            raise ValueError("Unsupported keyword only arguments.")
        all_args_len = len(node.args)
        all_defaults_len = len(node.defaults)
        index = 0
        arg_statements = []
        defaults = node.defaults
        non_defaults = all_args_len - all_defaults_len
        for arg in node.args:
            if index < non_defaults:
                arg_statements.append(arg.arg)
            else:
                arg_statements.append(f"{arg.arg} = {process(self.visit(defaults[index - non_defaults]), self)}")
            index += 1
        if not arg_statements:
            return []
        return arg_statements

    def visit_Subscript(self, node: ast.Subscript):
        value: Variable = self.visit(node.value)        # a[1][2] -> subscript(subscript)
        if isinstance(node.ctx, ast.Store):
            if value.mode == VariableMode.PYTHON:
                raise ValueError("Unsupported subscript assign.")
        slice = self.visit(node.slice)
        if isinstance(value, Variable) and value.mode == VariableMode.FAKE:
            value: FakeVariable
            return value.at(slice)
        return f"{process(value, self)}[{process(slice, self)}]"

    def visit_Name(self, node):
        re = super().visit_Name(node)
        return _check_enum_type(re)

    def visit_Attribute(self, node):
        re = super().visit_Attribute(node)
        return _check_enum_type(re)

    def visit_Call(self, node: ast.Call):
        func: Variable = self.visit(node.func)
        func_str = ""
        if func.mode == VariableMode.PYTHON:
            if isinstance(func.data, Constant):
                func_str = process(func, self)
            else:
                raise ValueError("Unsupport other python variables.")
        elif func.mode == VariableMode.SWORDFISH:
            func_str = process(func, self)
        elif func.mode == VariableMode.FAKE:
            func: FakeVariable
            args = [process(self.visit(_arg), self) for _arg in node.args]
            kwargs = {k.arg: process(self.visit(k.value), self) for k in node.keywords}
            func_call = func.call(args, kwargs)
            return process(func_call, self)
        else:
            raise ValueError("Invalid variable mode.")
        args = [process(self.visit(_arg), self) for _arg in node.args]
        kwargs = [f"{k.arg}={process(self.visit(k.value), self)}" for k in node.keywords]
        all_args = ",".join(args + kwargs)
        return f"{func_str}({all_args})"

    def visit_Assign(self, node: ast.Assign):
        value = self.visit(node.value)
        target_str: str = ""
        for target in node.targets:
            tmp_str: str
            if isinstance(target, ast.Tuple):
                lefts = [self.visit(sub_node) for sub_node in target.elts]
                for left in lefts:
                    if isinstance(left, AttributeVariable):
                        raise ProgrammingError("Unsupported multi assign with self attribute.")
                value_str = process(self.visit(node.value), self)
                tmp_str = ", ".join([process(left, self) for left in lefts])
                target_str += f"{tmp_str} = {value_str};\n"
            elif isinstance(target, ast.Name) or isinstance(target, ast.Subscript):
                left = self.visit(target)
                if isinstance(left, AttributeVariable):
                    tmp = left.assign(value)
                    target_str += f"{process(tmp, self)};\n"
                else:
                    value_str = process(self.visit(node.value), self)
                    tmp_str = process(self.visit(target), self)
                    target_str += f"{tmp_str} = {value_str};\n"
            else:
                raise RuntimeError("Unsupport Assign target.")
        return target_str


class BacktestVisitor(MethodVisitor):
    def __init__(self, cls, frame: FrameType):
        super().__init__()
        self.stack.push(VariableFrame(frame.f_globals))
        self.stack.push(VariableFrame(frame.f_locals))
        self.callback_d = sf_dictionary(key_type="STRING", val_type="ANY")
        self.on_timer_d = sf_dictionary(key_type="SECOND", val_type="ANY")
        self.callback_d["onTimer"] = self.on_timer_d
        self.class_obj = cls

    _callback_map = {
        'on_tick': 'onTick',
        'on_snapshot': 'onSnapshot',
        'on_bar': 'onBar',
        'on_transaction': 'onTransaction',
        'on_order': 'onOrder',
    }

    def generate_functiondef(self, node):
        method_visitor = MethodVisitor()
        method_visitor.stack = self.stack
        method_visitor.add_arguments(node.args)
        self.stack.push()
        args = method_visitor.visit_arguments(node.args)
        args = args[1:]
        args[0] = "mutable " + args[0]

        lines = []
        for stmt in node.body:
            line = method_visitor.visit(stmt)
            lines.append(line)

        vars_args = list(method_visitor.var_dict.keys())
        args_str = ",".join(vars_args + args)

        function_code = f"""
            def ({args_str}) {{
                {"".join(lines)}
            }}
        """
        functiondef = FunctionDef(function_code)
        args = list(method_visitor.var_dict.values())
        if args:
            args = [sf_DFLT if isinstance(arg, Constant) and check_is_nothing(arg) else arg for arg in args]
            functiondef = create_partial(functiondef, *args)
        self.stack.pop()
        self.stack.pop()
        return functiondef

    def visit_FunctionDef(self, node):
        if node.name in self.class_obj._timer_funcs:
            # on_timer
            functiondef = self.generate_functiondef(node)
            trigger_time = self.class_obj._timer_funcs[node.name]
            if isinstance(trigger_time, sf_data.Vector):
                for t in trigger_time:
                    self.on_timer_d[t] = functiondef
            else:
                self.on_timer_d[trigger_time] = functiondef
        else:
            all_methods = dir(backtest.StrategyInterface)
            all_methods = [m for m in all_methods if not m.startswith('__') and not m.endswith('__')]

            if node.name not in all_methods:
                return
            if node.name not in self._callback_map:
                return

            functiondef = self.generate_functiondef(node)
            self.callback_d[self._callback_map[node.name]] = functiondef


class ContextVisitor(StandardVisitor):
    def __init__(self, cls, frame: FrameType):
        super().__init__()
        self.stack.push(VariableFrame(frame.f_globals))
        self.stack.push(VariableFrame(frame.f_locals))
        self.context = sf_dictionary(key_type="STRING", val_type="ANY")

    def visit_Assign(self, node: ast.Assign):
        conn = sf_connect()
        sess = conn.impl.session()
        value_str = process(self.visit(node.value), self)
        for target in node.targets:
            if isinstance(target, ast.Tuple):
                tmps = [process(self.visit(sub_node), self) for sub_node in target.elts]
                sess.variable(self.var_dict)
                tmp_str = ", ".join(tmps) + " = " + value_str
                sess.exec(tmp_str)
                for tmp in tmps:
                    self.context[tmp] = sess.exec(tmp)
            elif isinstance(target, ast.Name):
                tmp_str = process(self.visit_Name(target), self)
                sess.variable(self.var_dict)
                self.context[tmp_str] = sess.exec(value_str)


def translator(cls):
    if sys.version_info.major == 3 and sys.version_info.minor == 8:
        warnings.warn("Classes with the same name may cause translation errors in Python 3.8.")
    frame = inspect.currentframe()
    frame = inspect.getouterframes(frame)[1].frame

    source_lines, line_nums = inspect.getsourcelines(cls)
    if source_lines:
        s = source_lines[0]
        if s.startswith(" "):
            num_spaces = len(s) - len(s.lstrip(' '))
            source_lines = [line[num_spaces:] for line in source_lines]
    cls_code = "".join(source_lines)

    cls_node: ast.ClassDef = ast.parse(cls_code).body[0]

    cls_visitor = BacktestVisitor(cls, frame)

    context_visitor = ContextVisitor(cls, frame)

    for stmt in cls_node.body:
        if isinstance(stmt, ast.FunctionDef):
            cls_visitor.visit(stmt)
        else:
            context_visitor.visit(stmt)

    cls.callback_d = cls_visitor.callback_d
    cls.context = context_visitor.context

    return cls
