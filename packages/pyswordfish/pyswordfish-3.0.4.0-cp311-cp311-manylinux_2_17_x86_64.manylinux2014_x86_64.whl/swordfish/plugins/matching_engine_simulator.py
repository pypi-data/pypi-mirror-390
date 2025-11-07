from ..tools import check_plugin_license

if not check_plugin_license("MatchingEngineSimulator"):
    raise ImportError("The MatchingEngineSimulator plugin requires a special license. "
                      "Update the license or contact technical support.")


from .._swordfishcpp import (  # type: ignore
    MatchingEngineSimulator,
    createMatchingEngineSimulator,

    Table,
)

from .._engine import (
    Builder,
    generate_create_method,
)

from .._helper import Config
from ..types import TypeDict
from ..data import (
    dictionary as sf_dictionary,
    table as sf_table,
)

from .. import (
    data as sf_data,
)

from enum import Enum
from typing import Dict, Union


class Exchange(Enum):
    """
    The supported exchanges are as following:
       
    """
    XSHE = "XSHE"
    """Shenzhen Stock Exchange
    """
    XSHG = "XSHG"
    """Shanghhai Stock Exchange
    """
    COMMODITY = "commodity"
    """Commodity futures/options.
    """
    EQUITY = "equity"
    """Treasury/Index futures or equity options.
    """
    UNIVERSAL = "universal"
    """Assets without trading time limit.
    """
    CFFEX = "CFFEX"
    """Shanghai exchange bonds.
    """
    CFETS = "CFETS"
    """Interbank Xbond market.

    """


class MarketDataType(Enum):
    """
    The supported market types are as following:       
    """
    STOCK_TICK = 0
    """Stock tick-by-tick.
    """
    STOCK_SNAPSHOT = 1
    """Stock snapshot.
    """
    BOND_SNAPSHOT = 3
    """Interbank/Exchange bond snapshot.
    """
    STOCK_MINUTE = 4
    """Stock minute data.
    """
    STOCK_DAILY = 5
    """Stock daily.
    """
    FUTURES_OPTION_SNAPSHOT = 6
    """Futures/options snapshot.
    """
    FUTURES_OPTION_MINUTE = 7
    """Futures/options minute.
    """
    FUTURES_OPTION_DAILY = 8
    """Futures/options daily.
    """
    CRYPTO_SNAPSHOT = 13
    """Crypto snapshot.
    """
    CRYPTO_MINUTE = 14
    """Crypto minute.
    """
    CRYPTO_DAILY = 15
    """Crypto daily.
    """


class MatchingEngineSimulatorConfig(Config):
    quote_col_map: Dict[str, str] = None
    """The configuration parameters for the matching engine simulator.
    """
    user_order_col_map: Dict[str, str] = None

    depth: float = None
    output_interval: float = None
    latency: float = None
    orderbook_matching_ratio: float = None
    matching_mode: int = None
    matching_ratio: float = None

    order_details_and_snapshot_output: Table = None
    snapshot_output: Table = None

    output_time_info: bool = None
    output_reject_details: bool = None
    output_queue_position: int = None
    output_order_confirmation: bool = None
    output_order_trade_flag: bool = None

    cpu_id: int = None
    user_defined_order_id: bool = None
    order_by_price: bool = None

    immediate_order_confirmation: bool = None
    immediate_cancel: bool = None

    trade_in_lots: bool = None
    output_seq_num: bool = None


class MatchingEngineSimulatorBuilder(Builder):
    def __init__(
        self,
        name: str,
        exchange: Union[Exchange, str],
        data_type: Union[MarketDataType, int],
        order_detail_output: Table,
        quote_schema: Union[Table, TypeDict] = None,
        user_order_schema: Union[Table, TypeDict] = None,
        *,
        config: MatchingEngineSimulatorConfig = None,
    ):
        super().__init__(name)
        self._exchange = exchange.value if isinstance(exchange, Exchange) else str(exchange)

        if isinstance(quote_schema, dict):
            self._quote_table = sf_table(types=quote_schema, size=0, capacity=1)
        else:
            self._quote_table = quote_schema
        if isinstance(user_order_schema, dict):
            self._user_order_table = sf_table(types=user_order_schema, size=0, capacity=1)
        else:
            self._user_order_table = user_order_schema

        self._order_detail_output = order_detail_output

        self._config_d = sf_dictionary(key_type="STRING", val_type="DOUBLE")
        self.config(config)
        self._config_d["dataType"] = data_type.value if isinstance(data_type, MarketDataType) else int(data_type)

    def _extract_default_col_map(self, t: Table):
        cols = t.keys()
        return sf_dictionary(keys=cols, vals=cols)

    def _extract_config(self, config: MatchingEngineSimulatorConfig):
        config = MatchingEngineSimulatorConfig(config)
        config_d = sf_dictionary(key_type="STRING", val_type="DOUBLE")
        if config.get("quote_col_map") is not None:
            self._quote_col_map = config["quote_col_map"]
        else:
            self._quote_col_map = self._extract_default_col_map(self._quote_table)
        if config.get("user_order_col_map") is not None:
            self._user_order_col_map = config["user_order_col_map"]
        else:
            self._user_order_col_map = self._extract_default_col_map(self._user_order_table)

        if config.get("depth") is not None:
            config_d["depth"] = config["depth"]
        if config.get("output_interval") is not None:
            config_d["outputInterval"] = config["output_interval"]
        if config.get("latency") is not None:
            config_d["latency"] = config["latency"]
        if config.get("orderbook_matching_ratio") is not None:
            config_d["orderBookMatchingRatio"] = config["orderbook_matching_ratio"]
        if config.get("matching_mode") is not None:
            config_d["matchingMode"] = config["matching_mode"]
        if config.get("matching_ratio") is not None:
            config_d["matchingRatio"] = config["matching_ratio"]

        if config.get("order_details_and_snapshot_output") is not None:
            config_d["enableOrderDetailsAndSnapshotOutput"] = True
            self._order_details_and_snapshot_output = config["order_details_and_snapshot_output"]
        else:
            self._order_details_and_snapshot_output = sf_data.DFLT
        if config.get("snapshot_output") is not None:
            config_d["outputOrderBook"] = True
            self._snapshot_output = config["snapshot_output"]
        else:
            self._snapshot_output = sf_data.DFLT

        if config.get("output_time_info") is not None:
            config_d["outputTimeInfo"] = config["output_time_info"]
        if config.get("output_reject_details") is not None:
            config_d["outputRejectDetails"] = config["output_reject_details"]
        if config.get("output_queue_position") is not None:
            config_d["outputQueuePosition"] = config["output_queue_position"]
        if config.get("output_order_confirmation") is not None:
            config_d["outputOrderConfirmation"] = config["output_order_confirmation"]
        if config.get("output_order_trade_flag") is not None:
            config_d["outputOrderTradeFlag"] = config["output_order_trade_flag"]

        if config.get("cpu_id") is not None:
            config_d["cpuId"] = config["cpu_id"]
        if config.get("user_defined_order_id") is not None:
            config_d["userDefinedOrderId"] = config["user_defined_order_id"]
        if config.get("order_by_price") is not None:
            config_d["orderByPrice"] = config["order_by_price"]
        if config.get("immediate_order_confirmation") is not None:
            config_d["immediateOrderConfirmation"] = config["immediate_order_confirmation"]
        if config.get("immediate_cancel") is not None:
            config_d["immediateCancel"] = config["immediate_cancel"]
        if config.get("trade_in_lots") is not None:
            config_d["tradeInLots"] = config["trade_in_lots"]
        if config.get("output_seq_num") is not None:
            config_d["outputSeqNum"] = config["output_seq_num"]
        return config_d

    def config(self, val: MatchingEngineSimulatorConfig):
        config_d = self._extract_config(val)
        for k, v in config_d.items():
            self._config_d[k] = v
        return self

    def submit(self) -> MatchingEngineSimulator:
        return createMatchingEngineSimulator(
            self.name, self._exchange, self._config_d, self._quote_table,
            self._quote_col_map, self._user_order_table, self._user_order_col_map, self._order_detail_output,
            self._order_details_and_snapshot_output, self._snapshot_output,
        )


MatchingEngineSimulator.create = classmethod(generate_create_method(MatchingEngineSimulatorBuilder))
