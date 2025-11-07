from ..tools import check_plugin_license, get_plugin_version


if check_plugin_license("Backtest"):
    from . import backtest

if check_plugin_license("MatchingEngineSimulator"):
    from . import matching_engine_simulator


__version__ = get_plugin_version()


__all__ = [
    "backtest",
    "matching_engine_simulator",
]
