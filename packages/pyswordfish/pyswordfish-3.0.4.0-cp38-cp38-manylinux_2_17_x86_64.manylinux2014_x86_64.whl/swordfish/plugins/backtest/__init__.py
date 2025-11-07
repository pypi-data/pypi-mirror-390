from ...tools import check_plugin_license

if not check_plugin_license("Backtest"):
    raise ImportError("The Backtest plugin requires a special license. "
                      "Update the license or contact technical support.")


from .backtest import (
    AssetType, MarketType, MarketDataType, MatchingMode,
    AccountType, Account,
    BacktestBasicConfig, StockConfig, MarginConfig, OptionConfig,
    FuturesConfig, BondConfig, CryptoConfig,
    StrategyTemplate, StrategyInterface,
    Backtester, TraditionalBacktester,
    StockOrderMixin, FuturesOrderMixin, OptionOrderMixin,
    MarginOrderMixin, BondOrderMixin,
    CryptoOrderMixin,
    trigger_time,
    AlgoOrderMixin,
)

from .translator import translator

__all__ = [
    "AssetType", "MarketType", "MarketDataType", "MatchingMode",
    "AccountType", "Account",
    "BacktestBasicConfig", "StockConfig", "MarginConfig", "OptionConfig",
    "FuturesConfig", "BondConfig", "CryptoConfig",
    "StrategyTemplate", "StrategyInterface",
    "Backtester", "TraditionalBacktester",
    "StockOrderMixin", "FuturesOrderMixin", "OptionOrderMixin",
    "MarginOrderMixin", "BondOrderMixin",
    "CryptoOrderMixin",

    "translator",
    "trigger_time",
    "AlgoOrderMixin",
]
