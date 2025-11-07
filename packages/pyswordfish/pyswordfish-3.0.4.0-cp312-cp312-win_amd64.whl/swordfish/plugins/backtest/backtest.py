from ..._swordfishcpp import (  # type: ignore
    plugin_backtest_setUniverse,
    plugin_backtest_createBacktestEngine,
    plugin_backtest_dropBacktestEngine,
    plugin_backtest_submitOrder,
    plugin_backtest_cancelOrder,
    plugin_backtest_getPosition,
    plugin_backtest_getDailyPosition,
    plugin_backtest_appendQuotationMsg,
    plugin_backtest_getAvailableCash,
    plugin_backtest_getTodayPnl,
    plugin_backtest_getTradeDetails,
    plugin_backtest_getContextDict,
    plugin_backtest_getDailyTotalPortfolios,
    plugin_backtest_getReturnSummary,
    plugin_backtest_backtestGetOpenOrders,
    plugin_backtest_getBacktestEngineList,
    plugin_backtest_subscribeIndicator,
    plugin_backtest_getLastestPrices,
    plugin_backtest_getTotalPortfolios,
    plugin_backtest_getMarginSecuPosition,
    plugin_backtest_getMarginTradingPosition,
    plugin_backtest_getSecuLendingPosition,
    plugin_backtest_setSecurityReferenceData,
    plugin_backtest_endWaitAPI,
    plugin_backtest_initialize,
    plugin_backtest_setRealTimeOutputTable,
    plugin_backtest_genIndicatorColumns,
    plugin_backtest_createBacktester,
    plugin_backtest_triggerDailySettlement,
    plugin_backtest_getStockTotalPortfolios,
    plugin_backtest_getFuturesTotalPortfolios,
    plugin_backtest_getOptionTotalPortfolios,
    plugin_backtest_setSimulatorTradingMode,
    plugin_backtest_updatePosition,
    plugin_backtest_getCryptocurrencyPosition,
    plugin_backtest_getCryptocurrencyTotalPortfolios,
    plugin_backtest_setPosition,
    plugin_backtest_getConfig,
    plugin_backtest_appendEndMarker,
)

from ..._swordfishcpp import (  # type: ignore
    Resource,
    Table,
    Timestamp,
    ProgrammingError,
)

from ..._helper import Config
from ..._runtime import Runtime

from ...data import (
    scalar as sf_scalar,
    vector as sf_vector,
    dictionary as sf_dictionary,
)

from ...function import (
    swordfish_udf as F_swordfish_udf,
)

from ... import (
    data as sf_data,
)

import datetime
import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import (
    TypeVar, Type,
    Union, List, Dict,
    final,
)
from collections.abc import Iterable
from collections import defaultdict
import weakref


def _generate_name():
    return "BACKTESTER_PSF_" + uuid.uuid4().hex[:8]


class AssetType(Enum):
    """The asset type.
    """
    STOCK = "stock"
    FUTURES = "futures"
    OPTION = "option"
    CRYPTO = "cryptocurrency"
    MARGIN = "securityCreditAccount"
    CFETS_BOND = "CFETSBond"
    XSHG_BOND = "XSHGBond"
    UNIVERSAL = "universal"     # in futures
    MULTIASSET = "multiAsset"


class MarketType(Enum):
    SNAPSHOT = 1
    SNAPSHOT_TICK = 2
    MINUTE = 3
    DAILY = 4
    STOCK_TICK_WIDE = 5
    SNAPSHOT_TICK_WIDE = 6


class MarketDataType(Enum):
    SNAPSHOT = "snapshot"
    TICK = "tick"
    KLINE = "kline"
    OHLC = "ohlc"
    TRADE = "trade"
    SNAPSHOT_KLINE = "snapshot_kline"
    SNAPSHOT_OHLC = "snapshot_ohlc"


class MatchingMode(Enum):
    CLOSE_MATCH = 1
    OPEN_MATCH = 2
    ORDER_MATCH = 3


class AccountType(Enum):
    SPOT = "spot"
    STOCK = "stock"
    FUTURES = "futures"
    OPTION = "option"
    DEFAULT = "default"


def _convert_Nothing(v):
    return v if v is not None else sf_data.Nothing


def _convert_account(v: AccountType):
    return v.value if v is not AccountType.DEFAULT else sf_data.String()


class Account:
    account_type: AccountType
    engine: "BacktesterBase"

    def __init__(self, account_type: AccountType, engine: "BacktesterBase"):
        self.account_type = account_type
        self.engine = engine

    @property
    def cash(self):
        """Query available cash in the account.
        """
        if self.account_type == AccountType.DEFAULT:
            return plugin_backtest_getAvailableCash(self.engine.engine_handle)
        return plugin_backtest_getAvailableCash(self.engine.engine_handle, self.account_type.value)

    @property
    def trade_details(self):
        """Retrieve order trade details.

        Returns
        -------
        Table
            Return a table with the following structure:
            
            +----------------+-------------------------------------------------------------------------------------------------+
            | Field          | Description                                                                                     |
            +================+=================================================================================================+
            | orderId        | Order ID                                                                                        |
            +----------------+-------------------------------------------------------------------------------------------------+
            | symbol         | Security code                                                                                   |
            +----------------+-------------------------------------------------------------------------------------------------+
            | direction      | Order direction:                                                                                |
            |                | 1: Buy open                                                                                     |
            |                | 2: Sell open                                                                                    |
            |                | 3: Sell close                                                                                   |
            |                | 4: Buy close                                                                                    |
            +----------------+-------------------------------------------------------------------------------------------------+
            | sendTime       | Order submission time                                                                           |
            +----------------+-------------------------------------------------------------------------------------------------+
            | orderPrice     | Order submission price                                                                          |
            +----------------+-------------------------------------------------------------------------------------------------+
            | orderQty       | Order quantity                                                                                  |
            +----------------+-------------------------------------------------------------------------------------------------+
            | tradeTime      | Trade time                                                                                      |
            +----------------+-------------------------------------------------------------------------------------------------+
            | tradePrice     | Trade price                                                                                     |
            +----------------+-------------------------------------------------------------------------------------------------+
            | tradeQty       | Trade quantity                                                                                  |
            +----------------+-------------------------------------------------------------------------------------------------+
            | orderStatus    | Order status:                                                                                   |
            |                | 4: Submitted                                                                                    |
            |                | 2: Cancel successful                                                                            |
            |                | 1: Filled                                                                                       |
            |                | 0: Partially filled                                                                             |
            |                | -1: Approval rejected                                                                           |
            |                | -2: Cancel rejected                                                                             |
            |                | -3: Unfilled order                                                                              |
            +----------------+-------------------------------------------------------------------------------------------------+
            | label          | Label                                                                                           |
            +----------------+-------------------------------------------------------------------------------------------------+
            | outputOrderInfo| Risk control log, included only if engine parameter outputOrderInfo=true                        |
            +----------------+-------------------------------------------------------------------------------------------------+
            | seqNum         | Sequence number column, included only if engine parameter outputSeqNum=true                     |
            +----------------+-------------------------------------------------------------------------------------------------+

        """
        if self.account_type == AccountType.DEFAULT:
            return plugin_backtest_getTradeDetails(self.engine.engine_handle)
        return plugin_backtest_getTradeDetails(self.engine.engine_handle, self.account_type.value)

    def get_position(self, symbol: str = None):
        """Retrieve position information.
        
        - If symbol is not specified, a table is returned.
        
        - If symbol is specified, a dictionary is returned.
        
        - When JIT optimization is enabled, symbol must be specified.

        Parameters
        ----------
        symbol : str, optional
            A STRING scalar indicating the symbol code.

        Returns
        -------
        Table
            For assets other than SSE bonds, the returned structure is as follows:
            
            +-----------------------+----------------------------------+
            | Field                 | Description                      |
            +=======================+==================================+
            | symbol                | Stock symbol                     |
            +-----------------------+----------------------------------+
            | lastDayLongPosition   | Long position at previous close  |
            +-----------------------+----------------------------------+
            | lastDayShortPosition  | Short position at previous close |
            +-----------------------+----------------------------------+
            | longPosition          | Current long position            |
            +-----------------------+----------------------------------+
            | longPositionAvgPrice  | Average price of long position   |
            +-----------------------+----------------------------------+
            | shortPosition         | Current short position           |
            +-----------------------+----------------------------------+
            | shortPositionAvgPrice | Average price of short position  |
            +-----------------------+----------------------------------+
            | todayBuyVolume        | Buy volume today                 |
            +-----------------------+----------------------------------+
            | todayBuyValue         | Buy value today                  |
            +-----------------------+----------------------------------+
            | todaySellVolume       | Sell volume today                |
            +-----------------------+----------------------------------+
            | todaySellValue        | Sell value today                 |
            +-----------------------+----------------------------------+
            
            For SSE bonds, the returned structure is as follows:
            
            +--------------------+----------------------------------+
            | Field              | Description                      |
            +====================+==================================+
            | symbol             | Bond symbol                      |
            +--------------------+----------------------------------+
            | lastDayLongPosition | Long position at previous close |
            +--------------------+----------------------------------+
            | longPosition       | Current long position            |
            +--------------------+----------------------------------+
            | longPositionAvgPrice | Average price of long position |
            +--------------------+----------------------------------+
            | todayBuyVolume     | Buy volume today                 |
            +--------------------+----------------------------------+
            | todayBuyValue      | Buy value today                  |
            +--------------------+----------------------------------+
            | totalValue         | Total position value             |
            +--------------------+----------------------------------+
            | accruedInterest    | Accrued interest                 |
            +--------------------+----------------------------------+
            | fullBondPrice      | Full bond price                  |
            +--------------------+----------------------------------+
            | lastPrice          | Bond clean price                 |
            +--------------------+----------------------------------+
            | yield              | Yield                            |
            +--------------------+----------------------------------+
            | interestIncome     | Interest income                  |
            +--------------------+----------------------------------+
            | floatingProfit     | Floating profit/loss             |
            +--------------------+----------------------------------+
            | realizedProfit     | Realized profit/loss             |
            +--------------------+----------------------------------+
            | totalProfit        | Total profit/loss                |
            +--------------------+----------------------------------+
            | duration           | Duration                         |
            +--------------------+----------------------------------+
            | convexity          | Convexity                        |
            +--------------------+----------------------------------+
            | DV01               | DV01                             |
            +--------------------+----------------------------------+

        """
        if self.account_type == AccountType.DEFAULT:
            return plugin_backtest_getPosition(self.engine.engine_handle, _convert_Nothing(symbol))
        return plugin_backtest_getPosition(self.engine.engine_handle, _convert_Nothing(symbol), self.account_type.value)

    def set_position(self, symbol: str, qty: int, order_price: float, last_price: float = None):
        """Set the initial position. This function must be called before "append_data" is used to insert market data, 
        and it is typically invoked within the ``initialize`` callback function.

        Unlike *set_last_day_position* config, which defines base positions that do not occupy initial capital, 
        ``set_position`` defines initial positions whose cost does occupy initial capital.

        Parameters
        ----------
        symbol : str
            A STRING scalar indicating the security code.
        qty : int
            An INT scalar indicating the position quantity:

            -  qty > 0: indicates a long (buy) position.

            - qty < 0: indicates a short (sell) position. Short selling is not supported for stocks and bonds.
        order_price : float
            A DOUBLE scalar indicating the cost price of the position.
        last_price : float, optional
            A DOUBLE scalar indicating the latest price of the security (i.e., the previous closing price). 
            If omitted or set to 0, the default value is orderPrice.

        """
        if self.account_type == AccountType.DEFAULT:
            return plugin_backtest_setPosition(self.engine.engine_handle, symbol, qty, order_price, _convert_Nothing(last_price))
        return plugin_backtest_setPosition(self.engine.engine_handle, symbol, qty, order_price, _convert_Nothing(last_price), self.account_type.value)

    def get_daily_position(self, symbol: str = None):
        """This function is typically called after the backtest completes to retrieve detailed end-of-day position data.

        If it is called during the trading session, the current day's data will be unavailable, 
        and only the previous day's position data will be returned.
        
        When the asset type is stocks, futures, or options, the structure of the 
        returned position detail table is as follows:
          
        +-----------------------+--------------------------------------+
        | Field                 | Description                          |
        +=======================+======================================+
        | symbol                | Symbol code                          |
        +-----------------------+--------------------------------------+
        | tradeDate             | Trading date                         |
        +-----------------------+--------------------------------------+
        | lastDayLongPosition   | Long position from the previous day  |
        +-----------------------+--------------------------------------+
        | lastDayShortPosition  | Short position from the previous day |
        +-----------------------+--------------------------------------+
        | longPosition          | Current long position                |
        +-----------------------+--------------------------------------+
        | longPositionAvgPrice  | Average long trade price             |
        +-----------------------+--------------------------------------+
        | shortPosition         | Current short position               |
        +-----------------------+--------------------------------------+
        | shortPositionAvgPrice | Average short trade price            |
        +-----------------------+--------------------------------------+
        | todayBuyVolume        | Today's total buy volume             |
        +-----------------------+--------------------------------------+
        | todayBuyValue         | Today's total buy amount             |
        +-----------------------+--------------------------------------+
        | todaySellVolume       | Today's total sell volume            |
        +-----------------------+--------------------------------------+
        | todaySellValue        | Today's total sell amount            |
        +-----------------------+--------------------------------------+

        When in margin trading mode, the detailed position table has the following structure:
        
        +------------------------------------+-----------------------------------------------+
        | Field                              | Description                                   |
        +====================================+===============================================+
        | symbol                             | Symbol code                                   |
        +------------------------------------+-----------------------------------------------+
        | tradeDate                          | Trading date                                  |
        +------------------------------------+-----------------------------------------------+
        | lastDayMarginSecuPosition          | Collateral buy position at previous close     |
        +------------------------------------+-----------------------------------------------+
        | lastDayMarginDebt                  | Margin loan debt at previous close            |
        +------------------------------------+-----------------------------------------------+
        | lastDaySecuLendingDebt             | Securities lending debt at previous close     |
        +------------------------------------+-----------------------------------------------+
        | marginSecuPosition                 | Collateral buy position                       |
        +------------------------------------+-----------------------------------------------+
        | marginSecuAvgPrice                 | Average price of collateral buy position      |
        +------------------------------------+-----------------------------------------------+
        | marginBuyPosition                  | Margin buy position                           |
        +------------------------------------+-----------------------------------------------+
        | marginBuyValue                     | Margin buy value                              |
        +------------------------------------+-----------------------------------------------+
        | secuLendingPosition                | Securities lending (short sell) position      |
        +------------------------------------+-----------------------------------------------+
        | secuLendingSellValue               | Securities lending (short sell) value         |
        +------------------------------------+-----------------------------------------------+
        | closePrice                         | Closing price                                 |
        +------------------------------------+-----------------------------------------------+
        | longPositionConcentration          | Long position concentration ratio             |
        +------------------------------------+-----------------------------------------------+
        | shortPositionConcentration         | Net short position concentration ratio        |
        +------------------------------------+-----------------------------------------------+
        | marginBuyProfit                    | Profit/loss from margin buying                |
        +------------------------------------+-----------------------------------------------+
        | financialFee                       | Margin interest fee                           |
        +------------------------------------+-----------------------------------------------+
        | secuLendingProfit                  | Profit/loss from securities lending           |
        +------------------------------------+-----------------------------------------------+
        | secuLendingFee                     | Securities lending fee                        |
        +------------------------------------+-----------------------------------------------+

        When the asset type is a bond, the detailed position table has the following structure:
        
        +------------------------+--------------------------------------------+
        | Field                  | Description                                |
        +========================+============================================+
        | symbol                 | Symbol code                                |
        +------------------------+--------------------------------------------+
        | tradeDate              | Trading date                               |
        +------------------------+--------------------------------------------+
        | lastDayLongPosition    | Long position quantity at previous close   |
        +------------------------+--------------------------------------------+
        | longPosition           | Long position quantity                     |
        +------------------------+--------------------------------------------+
        | longPositionAvgPrice   | Average buy price                          |
        +------------------------+--------------------------------------------+
        | todayBuyVolume         | Buy volume of the day                      |
        +------------------------+--------------------------------------------+
        | todayBuyValue          | Buy value of the day                       |
        +------------------------+--------------------------------------------+
        | totalValue             | Total position value                       |
        +------------------------+--------------------------------------------+
        | accruedInterest        | Accrued interest                           |
        +------------------------+--------------------------------------------+
        | fullBondPrice          | Full bond price                            |
        +------------------------+--------------------------------------------+
        | lastPrice              | Net bond price                             |
        +------------------------+--------------------------------------------+
        | yield                  | Yield                                      |
        +------------------------+--------------------------------------------+
        | interestIncome         | Interest income                            |
        +------------------------+--------------------------------------------+
        | floatingProfit         | Unrealized profit/loss                     |
        +------------------------+--------------------------------------------+
        | realizedProfit         | Realized profit/loss                       |
        +------------------------+--------------------------------------------+
        | totalProfit            | Total profit/loss                          |
        +------------------------+--------------------------------------------+
        | duration               | Duration                                   |
        +------------------------+--------------------------------------------+
        | convexity              | Convexity                                  |
        +------------------------+--------------------------------------------+
        | DV01                   | DV01 (Dollar Value of 1 Basis Point)       |
        +------------------------+--------------------------------------------+

        Parameters
        ----------
        symbol : str, optional
            A STRING scalar indicating the target instrument to query. The default is empty, 
            in which case the function returns position data for all instruments.

        """
        if self.account_type == AccountType.DEFAULT:
            return plugin_backtest_getDailyPosition(self.engine.engine_handle, _convert_Nothing(symbol))
        return plugin_backtest_getDailyPosition(self.engine.engine_handle, _convert_Nothing(symbol), self.account_type.value)

    @property
    def total_portfolios(self):
        """Retrieve the current strategy equity metrics.

        Returns
        -------
        Dictionary
            A dictionary is returned with the following structure:
            
            **For stocks:**
            
            +------------------+--------------------------------------+
            | Field Name       | Description                          |
            +==================+======================================+
            | tradeDate        | Trading date                         |
            +------------------+--------------------------------------+
            | cash             | Available cash                       |
            +------------------+--------------------------------------+
            | totalMarketValue | Total market value of the account    |
            +------------------+--------------------------------------+
            | totalEquity      | Total equity of the account          |
            +------------------+--------------------------------------+
            | netValue         | Unit net value of the account        |
            +------------------+--------------------------------------+
            | totalReturn      | Cumulative return up to the day      |
            +------------------+--------------------------------------+
            | ratio            | Daily return of the account          |
            +------------------+--------------------------------------+
            | pnl              | Daily profit and loss of the account |
            +------------------+--------------------------------------+
            | frozenFunds      | Frozen funds                         |
            +------------------+--------------------------------------+
            | totalFee         | Total fees                           |
            +------------------+--------------------------------------+
            | floatingPnl      | Floating profit and loss             |
            +------------------+--------------------------------------+
            | realizedPnl      | Realized profit and loss             |
            +------------------+--------------------------------------+
            | totalPnl         | Total profit and loss                |
            +------------------+--------------------------------------+

            **For Margin Trading and Securities Lending:**

            +---------------------------+-------------------------------------------+
            | Field Name                | Description                               |
            +===========================+===========================================+
            | tradeDate                 | Trading date                              |
            +---------------------------+-------------------------------------------+
            | lineOfCredit              | Credit line                               |
            +---------------------------+-------------------------------------------+
            | availableCash             | Available cash                            |
            +---------------------------+-------------------------------------------+
            | lastDayMarginDebt         | Margin debt at previous close             |
            +---------------------------+-------------------------------------------+
            | lastDaySecuLendingDebt    | Securities lending debt at previous close |
            +---------------------------+-------------------------------------------+
            | marginSecuMarketValue     | Market value of collateral purchased      |
            +---------------------------+-------------------------------------------+
            | marginDebt                | Margin debt                               |
            +---------------------------+-------------------------------------------+
            | secuLendingSellValue      | Securities lending sell value             |
            +---------------------------+-------------------------------------------+
            | marginBalance             | Margin trading balance                    |
            +---------------------------+-------------------------------------------+
            | secuLendingDebt           | Securities lending debt                   |
            +---------------------------+-------------------------------------------+
            | financialFee              | Financing interest                        |
            +---------------------------+-------------------------------------------+
            | secuLendingFee            | Securities lending fee                    |
            +---------------------------+-------------------------------------------+
            | maintenanceMargin         | Maintenance margin ratio                  |
            +---------------------------+-------------------------------------------+
            | availableMarginBalance    | Available margin balance                  |
            +---------------------------+-------------------------------------------+
            | totalMarketValue          | Total market value of the account         |
            +---------------------------+-------------------------------------------+
            | totalEquity               | Total equity of the account               |
            +---------------------------+-------------------------------------------+
            | netValue                  | Unit net value of the account             |
            +---------------------------+-------------------------------------------+
            | totalReturn               | Cumulative return up to the day           |
            +---------------------------+-------------------------------------------+
            | yield                     | Daily return of the account               |
            +---------------------------+-------------------------------------------+
            | pnl                       | Daily profit and loss of the account      |
            +---------------------------+-------------------------------------------+
            | frozenFunds               | Frozen funds                              |
            +---------------------------+-------------------------------------------+

            **For Futures/Options:**

            +-------------------+---------------------------------------+
            | Field Name        | Description                           |
            +===================+=======================================+
            | tradeDate         | Trading date                          |
            +-------------------+---------------------------------------+
            | margin            | Margin used                           |
            +-------------------+---------------------------------------+
            | floatingPnl       | Floating PnL                          |
            +-------------------+---------------------------------------+
            | realizedPnl       | Realized cumulative PnL               |
            +-------------------+---------------------------------------+
            | totalPnl          | Total PnL                             |
            +-------------------+---------------------------------------+
            | cash              | Available cash                        |
            +-------------------+---------------------------------------+
            | totalEquity       | Total equity of the account           |
            +-------------------+---------------------------------------+
            | marginRatio       | Margin usage ratio                    |
            +-------------------+---------------------------------------+
            | pnl               | Daily profit and loss                 |
            +-------------------+---------------------------------------+
            | netValue          | Account unit net value                |
            +-------------------+---------------------------------------+
            | totalReturn       | Cumulative return up to the day       |
            +-------------------+---------------------------------------+
            | ratio             | Daily return of the account           |
            +-------------------+---------------------------------------+
            | totalFee          | Total fees                            |
            +-------------------+---------------------------------------+

            **For Bonds:**

            +-------------------+-------------------------------+
            | Field Name        | Description                   |
            +===================+===============================+
            | tradeDate         | Trading date                  |
            +-------------------+-------------------------------+
            | cash              | Available cash                |
            +-------------------+-------------------------------+
            | totalMarketValue  | Total market value of account |
            +-------------------+-------------------------------+
            | totalEquity       | Total equity of account       |
            +-------------------+-------------------------------+
            | netValue          | Account unit net value        |
            +-------------------+-------------------------------+
            | totalReturn       | Cumulative return up to date  |
            +-------------------+-------------------------------+
            | ratio             | Daily return                  |
            +-------------------+-------------------------------+
            | pnl               | Daily profit and loss         |
            +-------------------+-------------------------------+
            | totalProfit       | Total profit and loss         |
            +-------------------+-------------------------------+
            
        """
        if self.account_type == AccountType.DEFAULT:
            return plugin_backtest_getTotalPortfolios(self.engine.engine_handle)
        return plugin_backtest_getTotalPortfolios(self.engine.engine_handle, self.account_type.value)

    @property
    def daily_total_portfolios(self):
        """Called at the end of a backtest to obtain the strategy's daily equity metrics table. 

        Returns
        -------
        Table
            Return a table. The structure of the returned table varies depending on the asset type of the backtest.
            
            **For Stocks:**

            +---------------------+------------------------------------------------------------------+
            | Field Name          | Description                                                      |
            +=====================+==================================================================+
            | tradeDate           | Date                                                             |
            +---------------------+------------------------------------------------------------------+
            | cash                | Available cash                                                   |
            +---------------------+------------------------------------------------------------------+
            | totalMarketValue    | Total market value of the account                                |
            +---------------------+------------------------------------------------------------------+
            | totalEquity         | Total equity of the account                                      |
            +---------------------+------------------------------------------------------------------+
            | netValue            | Unit net value of the account                                    |
            +---------------------+------------------------------------------------------------------+
            | totalReturn         | Cumulative return up to the current day                          |
            +---------------------+------------------------------------------------------------------+
            | ratio               | Daily return of the account                                      |
            +---------------------+------------------------------------------------------------------+
            | pnl                 | Daily P&L of the account                                         |
            +---------------------+------------------------------------------------------------------+
            | frozenFunds         | Frozen funds                                                     |
            +---------------------+------------------------------------------------------------------+
            | totalFee            | Total fees                                                       |
            +---------------------+------------------------------------------------------------------+
            | floatingPnl         | Floating P&L                                                     |
            +---------------------+------------------------------------------------------------------+
            | realizedPnl         | Realized P&L                                                     |
            +---------------------+------------------------------------------------------------------+
            | totalPnl            | Total P&L                                                        |
            +---------------------+------------------------------------------------------------------+
            | benchmarkClosePrice | Benchmark daily closing price; returned only if benchmark is set |
            +---------------------+------------------------------------------------------------------+
            | benchmarkNetValue   | Benchmark daily net value; returned only if benchmark is set     |
            +---------------------+------------------------------------------------------------------+

            **For Margin Trading and Securities Lending:**

            +------------------------+------------------------------------------------------------------+
            | Field Name             | Description                                                      |
            +========================+==================================================================+
            | tradeDate              | Date                                                             |
            +------------------------+------------------------------------------------------------------+
            | lineOfCredit           | Line of credit                                                   |
            +------------------------+------------------------------------------------------------------+
            | availableCash          | Available cash                                                   |
            +------------------------+------------------------------------------------------------------+
            | lastDayMarginDebt      | Previous day's closing margin debt                               |
            +------------------------+------------------------------------------------------------------+
            | lastDaySecuLendingDebt | Previous day's closing securities lending debt                   |
            +------------------------+------------------------------------------------------------------+
            | marginSecuMarketValue  | Market value of collateral purchased                             |
            +------------------------+------------------------------------------------------------------+
            | marginDebt             | Margin debt                                                      |
            +------------------------+------------------------------------------------------------------+
            | secuLendingSellValue   | Amount from securities lending sell (lending liability)          |
            +------------------------+------------------------------------------------------------------+
            | marginBalance          | Margin trading and securities lending balance                    |
            +------------------------+------------------------------------------------------------------+
            | secuLendingDebt        | Securities lending debt                                          |
            +------------------------+------------------------------------------------------------------+
            | financialFee           | Financing interest                                               |
            +------------------------+------------------------------------------------------------------+
            | secuLendingFee         | Securities lending fee                                           |
            +------------------------+------------------------------------------------------------------+
            | maintenanceMargin      | Maintenance margin ratio                                         |
            +------------------------+------------------------------------------------------------------+
            | availableMarginBalance | Available margin balance                                         |
            +------------------------+------------------------------------------------------------------+
            | totalMarketValue       | Total market value of the account                                |
            +------------------------+------------------------------------------------------------------+
            | totalEquity            | Total equity of the account                                      |
            +------------------------+------------------------------------------------------------------+
            | netValue               | Unit net value of the account                                    |
            +------------------------+------------------------------------------------------------------+
            | totalReturn            | Cumulative return up to the current day                          |
            +------------------------+------------------------------------------------------------------+
            | yield                  | Daily return of the account                                      |
            +------------------------+------------------------------------------------------------------+
            | pnl                    | Daily P&L of the account                                         |
            +------------------------+------------------------------------------------------------------+
            | benchmarkClosePrice    | Benchmark daily closing price; returned only if benchmark is set |
            +------------------------+------------------------------------------------------------------+
            | benchmarkNetValue      | Benchmark daily net value; returned only if benchmark is set     |
            +------------------------+------------------------------------------------------------------+

            **For Futures/Options:**

            +------------------------+------------------------------------------------------------------+
            | Field Name             | Description                                                      |
            +========================+==================================================================+
            | tradeDate              | Date                                                             |
            +------------------------+------------------------------------------------------------------+
            | margin                 | Margin used                                                      |
            +------------------------+------------------------------------------------------------------+
            | floatingPnl            | Floating P&L                                                     |
            +------------------------+------------------------------------------------------------------+
            | realizedPnl            | Realized cumulative P&L                                          |
            +------------------------+------------------------------------------------------------------+
            | totalPnl               | Total P&L                                                        |
            +------------------------+------------------------------------------------------------------+
            | totalMarketValue       | Total market value (options only)                                |
            +------------------------+------------------------------------------------------------------+
            | cash                   | Available cash                                                   |
            +------------------------+------------------------------------------------------------------+
            | totalEquity            | Total equity of the account                                      |
            +------------------------+------------------------------------------------------------------+
            | marginRatio            | Margin usage ratio                                               |
            +------------------------+------------------------------------------------------------------+
            | pnl                    | Daily P&L of the account                                         |
            +------------------------+------------------------------------------------------------------+
            | netValue               | Unit net value of the account                                    |
            +------------------------+------------------------------------------------------------------+
            | totalReturn            | Cumulative return up to the current day                          |
            +------------------------+------------------------------------------------------------------+
            | ratio                  | Daily return of the account                                      |
            +------------------------+------------------------------------------------------------------+
            | benchmarkClosePrice    | Benchmark daily closing price; returned only if benchmark is set |
            +------------------------+------------------------------------------------------------------+
            | benchmarkNetValue      | Benchmark daily net value; returned only if benchmark is set     |
            +------------------------+------------------------------------------------------------------+
            
            **For Bonds:**

            +------------------------+------------------------------------------------------------------+
            | Field Name             | Description                                                      |
            +========================+==================================================================+
            | tradeDate              | Date                                                             |
            +------------------------+------------------------------------------------------------------+
            | cash                   | Available cash                                                   |
            +------------------------+------------------------------------------------------------------+
            | totalMarketValue       | Total market value of the account                                |
            +------------------------+------------------------------------------------------------------+
            | totalEquity            | Total equity of the account                                      |
            +------------------------+------------------------------------------------------------------+
            | netValue               | Unit net value of the account                                    |
            +------------------------+------------------------------------------------------------------+
            | totalReturn            | Cumulative return up to the current day                          |
            +------------------------+------------------------------------------------------------------+
            | ratio                  | Daily return of the account                                      |
            +------------------------+------------------------------------------------------------------+
            | pnl                    | Daily P&L of the account                                         |
            +------------------------+------------------------------------------------------------------+
            | totalProfit            | Total profit/loss                                                |
            +------------------------+------------------------------------------------------------------+
            | benchmarkClosePrice    | Benchmark daily closing price; returned only if benchmark is set |
            +------------------------+------------------------------------------------------------------+
            | benchmarkNetValue      | Benchmark daily net value; returned only if benchmark is set     |
            +------------------------+------------------------------------------------------------------+
        
        """
        if self.account_type == AccountType.DEFAULT:
            return plugin_backtest_getDailyTotalPortfolios(self.engine.engine_handle)
        return plugin_backtest_getDailyTotalPortfolios(self.engine.engine_handle, self.account_type.value)

    @property
    def return_summary(self):
        """Used to calculate the strategy's performance summary at the end of backtesting.

        Returns
        -------
        Table
            A table is returned with the following structure:
            
            **For Stocks/Futures/Options/Bonds:**

            +--------------------+--------------------------------------------------------+
            | Field Name         | Description                                            |
            +====================+========================================================+
            | totalReturn        | Total return                                           |
            +--------------------+--------------------------------------------------------+
            | annualReturn       | Annualized return                                      |
            +--------------------+--------------------------------------------------------+
            | annualVolatility   | Annualized volatility                                  |
            +--------------------+--------------------------------------------------------+
            | annualSkew         | Return skewness                                        |
            +--------------------+--------------------------------------------------------+
            | annualKur          | Return kurtosis                                        |
            +--------------------+--------------------------------------------------------+
            | sharpeRatio        | Sharpe ratio                                           |
            +--------------------+--------------------------------------------------------+
            | maxDrawdown        | Maximum drawdown                                       |
            +--------------------+--------------------------------------------------------+
            | drawdownRatio      | Drawdown-to-return ratio                               |
            +--------------------+--------------------------------------------------------+
            | beta               | Beta coefficient                                       |
            +--------------------+--------------------------------------------------------+
            | alpha              | Alpha coefficient                                      |
            +--------------------+--------------------------------------------------------+
            | benchmarkReturn    | Benchmark return                                       |
            +--------------------+--------------------------------------------------------+
            | annualExcessReturn | Annualized excess return                               |
            +--------------------+--------------------------------------------------------+
            | turnoverRate       | Turnover rate                                          |
            +--------------------+--------------------------------------------------------+
            | dailyWinningRate   | Daily winning rate                                     |
            +--------------------+--------------------------------------------------------+
            | maxMarginRatio     | Maximum margin usage (field unique to futures/options) |
            +--------------------+--------------------------------------------------------+
        
            In Margin Trading and Securities Lending mode, the returned table contains the above fields 
            as well as the following additional fields:    
            
            +-------------------+------------------------------------------+
            | Field Name        | Description                              |
            +===================+==========================================+
            | totalFee          | Total commission and fees                |
            +-------------------+------------------------------------------+
            | financialFee      | Financing interest                       |
            +-------------------+------------------------------------------+
            | secuLendingFee    | Securities lending fee                   |
            +-------------------+------------------------------------------+
            | bottomRet         | Base position return                     |
            +-------------------+------------------------------------------+
            | bottomExcessRet   | Base position excess return              |
            +-------------------+------------------------------------------+

        
        """
        if self.account_type == AccountType.DEFAULT:
            return plugin_backtest_getReturnSummary(self.engine.engine_handle)
        return plugin_backtest_getReturnSummary(self.engine.engine_handle, self.account_type.value)


class BacktestBasicConfig(Config):
    start_date: datetime.date
    end_date: datetime.date
    asset_type: AssetType
    data_type: MarketType
    cash: Union[Dict[AccountType, float], float] = None
    matching_mode: MatchingMode = None

    universe: List[str] = None

    context: dict = None

    latency: int = None
    benchmark: str = None
    data_retention_window: Union[str, int] = None

    is_backtest_mode: bool = True
    msg_as_table: bool = False      # always False
    enable_indicator_optimize: bool = False
    add_time_column_in_indicator: bool = False

    orderbook_matching_ratio: float = 1.0
    output_order_info: bool = False
    matching_ratio: float = None


class StockConfig(BacktestBasicConfig):
    set_last_day_position: Table = None
    prev_close_price: Table = None
    enable_subscription_to_tick_quotes: bool = False
    commission: float = None
    tax: float = None
    output_queue_position: int = 0
    stock_dividend: Table = None
    frequency: int = 0
    callback_for_snapshot: int = 0


class MarginConfig(BacktestBasicConfig):
    line_of_credit: float
    margin_trading_interest_rate: float
    secu_lending_interest_rate: float
    maintenance_margin: List[float]
    long_concentration: List[float] = None
    short_concentration: List[float] = None
    repay_without_margin_buy: bool = None
    set_last_day_position: Table = None


class OptionConfig(BacktestBasicConfig):
    security_reference: Table
    frequency: int = 0
    callback_for_snapshot: int = 0
    maintenance_margin: float = 1.0


class FuturesConfig(BacktestBasicConfig):
    security_reference: Table
    frequency: int = 0
    futures_type: str = None
    enable_algo_order: bool
    callback_for_snapshot: int = 0
    maintenance_margin: float = 1.0


class BondConfig(BacktestBasicConfig):
    security_reference: Table


class CryptoConfig(BacktestBasicConfig):
    security_reference: Table
    funding_rate: Table


class BacktesterBase(ABC):
    engine_handle: Resource
    accounts: Dict[AccountType, Account]

    @abstractmethod
    def append_data(self, data):
        pass

    @abstractmethod
    def append_end(self):
        pass

    @property
    @abstractmethod
    def context_dict(self):
        """Return the logical context.
        """
        pass

    @property
    @abstractmethod
    def universe(self):
        """Set the symbol pool for the engine.
        """
        pass

    @universe.setter
    @abstractmethod
    def universe(self, val: List[str]):
        pass

    @property
    @abstractmethod
    def config(self) -> sf_data.Dictionary:
        """Return the backtest configuration.
        """
        pass


class StrategyBase:
    engine: BacktesterBase


def trigger_time(t: str):
    """A timer event that triggers at a specified time or frequency. Set the trigger using 
    the @trigger_time decorator. Only intervals in seconds (SECOND) are supported.

    Parameters
    ----------
    t : str
        A STRING scalar specifying the trigger time in "HH:MM:SS" format. The callback function will be executed at this time.

    """
    if isinstance(t, str):
        t = sf_scalar(t, type="SECOND")
    elif isinstance(t, Iterable):
        t = sf_vector(t, type="SECOND")

    if not isinstance(t, sf_data.Second) and not isinstance(t, sf_data.Vector):
        raise ProgrammingError("The trigger time must be a Second object or a Second Vector object.")

    def wrapper(func):
        func._is_timer_func = True
        func._timer_time = t
        return func
    return wrapper


class InterfaceMeta(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        new_cls._timer_funcs = defaultdict(dict)

        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and getattr(attr_value, '_is_timer_func', False):
                time_key = attr_value._timer_time
                func_name = attr_value.__name__
                new_cls._timer_funcs[func_name] = time_key

        return new_cls


class StrategyInterface(metaclass=InterfaceMeta):
    def initialize(self, context):
        """Strategy initialization callback function, triggered when the backtester is created. 
        It is used for preparatory tasks such as loading parameters, initializing states, 
        and registering indicators.

        Parameters
        ----------
        context : _type_
            A dictionary representing the global context of the strategy. It is used to store 
            and manage all user-defined variables within the strategy. In addition, 
            the backtesting engine maintains four internal variables within the context:

            - context.tradeTime — Returns the latest market timestamp.

            - context.tradeDate — Returns the current trading date.

            - context.BarTime — Returns the current bar timestamp when market snapshots 
              are aggregated into lower-frequency bars.
              
            - context.engine — Returns the internal instance handle of the backtesting engine.
        """
        pass

    def before_trading(self, context):
        """The daily callback function is triggered before the market opens each trading day.

        Parameters
        ----------
        context : _type_
            A dictionary representing the global context of the strategy. It is used to store 
            and manage all user-defined variables within the strategy. In addition, 
            the backtesting engine maintains four internal variables within the context:

            - context.tradeTime — Returns the latest market timestamp.

            - context.tradeDate — Returns the current trading date.

            - context.BarTime — Returns the current bar timestamp when market snapshots 
              are aggregated into lower-frequency bars.
              
            - context.engine — Returns the internal instance handle of the backtesting engine.
        """
        pass

    def on_tick(self, context, msg, indicator):
        """The callback function is triggered whenever the latest tick-by-tick order or trade data is received.

        Parameters
        ----------
        context : _type_
            A dictionary representing the global context of the strategy. It is used to store 
            and manage all user-defined variables within the strategy. In addition, 
            the backtesting engine maintains four internal variables within the context:

            - context.tradeTime — Returns the latest market timestamp.

            - context.tradeDate — Returns the current trading date.

            - context.BarTime — Returns the current bar timestamp when market snapshots 
              are aggregated into lower-frequency bars.
              
            - context.engine — Returns the internal instance handle of the backtesting engine.
        msg : _type_
            Represents the tick-level market data. Each record is provided as either a dictionary object 
            or a table (depending on the msg_as_table configuration). The specific fields vary 
            by asset type. For details, refer to the msg data section below.
        indicator : _type_        
            A dictionary or nested dictionary with a structure consistent with the corresponding msg, 
            containing the data subscribed to by the strategy.
           
            
        Msg data
        ---------------
        
        - Stock Tick / Margin Trading
        
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | Field        | Type      | Description                                                                                             |
          +==============+===========+=========================================================================================================+
          | symbol       | SYMBOL    | Stock code:                                                                                             |
          |              |           | - Ends with ".XSHG" for Shanghai Stock Exchange                                                         |
          |              |           | - Ends with ".XSHE" for Shenzhen Stock Exchange                                                         |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | symbolSource | STRING    | ".XSHG" (Shanghai Stock Exchange) or ".XSHE" (Shenzhen Stock Exchange)                                  |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | timestamp    | TIMESTAMP | Timestamp                                                                                               |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | sourceType   | INT       | 0 represents entrust data; 1 represents trade data                                                      |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | orderType    | INT       | - entrust:                                                                                              |
          |              |           |                                                                                                         |
          |              |           |   1: Market order                                                                                       |
          |              |           |                                                                                                         |
          |              |           |   2: Limit order                                                                                        |
          |              |           |                                                                                                         |
          |              |           |   3: Best own side price                                                                                |
          |              |           |                                                                                                         |
          |              |           |   10: Cancel order (Shanghai only, cancel records are in entrust)                                       |
          |              |           | - trade:                                                                                                |
          |              |           |                                                                                                         |
          |              |           |   0: Trade                                                                                              |
          |              |           |                                                                                                         |
          |              |           |   1: Cancel order (Shenzhen only, cancel records are in trade)                                          |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | price        | DOUBLE    | Order price                                                                                             |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | qty          | LONG      | Order quantity                                                                                          |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | buyNo        | LONG      | Original buy order number in trade; filled for entrust orders                                           |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | sellNo       | LONG      | Original sell order number in trade; filled for entrust orders                                          |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | direction    | INT       | 1 (Buy) or 2 (Sell)                                                                                     |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | channelNo    | INT       | Channel number                                                                                          |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+
          | seqNum       | LONG      | Tick data sequence number                                                                               |
          +--------------+-----------+---------------------------------------------------------------------------------------------------------+

        - Stock Tick or Tick + Snapshot
        
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | Field        | Type      | Description                                                                                              |
          +==============+===========+==========================================================================================================+
          | symbol       | SYMBOL    | Stock code:                                                                                              |
          |              |           |                                                                                                          |
          |              |           | - Ends with ".XSHG" for Shanghai Stock Exchange                                                          |
          |              |           |                                                                                                          |
          |              |           | - Ends with ".XSHE" for Shenzhen Stock Exchange                                                          |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | symbolSource | STRING    | ".XSHG" (Shanghai Stock Exchange) or ".XSHE" (Shenzhen Stock Exchange)                                   |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | timestamp    | TIMESTAMP | Timestamp                                                                                                |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | sourceType   | INT       | 0 represents entrust data; 1 represents trade data                                                       |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | orderType    | INT       | - entrust:                                                                                               |
          |              |           |                                                                                                          |
          |              |           |   1: Market order                                                                                        |
          |              |           |                                                                                                          |
          |              |           |   2: Limit order                                                                                         |
          |              |           |                                                                                                          |
          |              |           |   3: Best own side price                                                                                 |
          |              |           |                                                                                                          |
          |              |           |   10: Cancel order (Shanghai only; cancel records are in entrust)                                        |
          |              |           |                                                                                                          |
          |              |           | - trade:                                                                                                 |
          |              |           |                                                                                                          |
          |              |           |   0: Trade                                                                                               |
          |              |           |                                                                                                          |
          |              |           |   1: Cancel order (Shenzhen only; cancel records are in trade)                                           |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | price        | DOUBLE    | Order price                                                                                              |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | qty          | LONG      | Order quantity                                                                                           |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | buyNo        | LONG      | Original buy order number in trade; filled for entrust orders                                            |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | sellNo       | LONG      | Original sell order number in trade; filled for entrust orders                                           |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | direction    | INT       | 1 (Buy) or 2 (Sell)                                                                                      |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | channelNo    | INT       | Channel number                                                                                           |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | seqNum       | LONG      | Tick data sequence number                                                                                |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
        
        - Stock Tick (Wide Table)
        
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | Field        | Type      | Description                                                                                              |
          +==============+===========+==========================================================================================================+
          | symbol       | SYMBOL    | Stock code:                                                                                              |
          |              |           |                                                                                                          |
          |              |           | - Ends with ".XSHG" for Shanghai Stock Exchange                                                          |
          |              |           |                                                                                                          |
          |              |           | - Ends with ".XSHE" for Shenzhen Stock Exchange                                                          |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | symbolSource | STRING    | ".XSHG" (Shanghai Stock Exchange) or ".XSHE" (Shenzhen Stock Exchange)                                   |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | timestamp    | TIMESTAMP | Timestamp                                                                                                |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | sourceType   | INT       | 0 represents entrust data; 1 represents trade data                                                       |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | orderType    | INT       | - entrust:                                                                                               |
          |              |           |                                                                                                          |
          |              |           |   1: Market order                                                                                        |
          |              |           |                                                                                                          |
          |              |           |   2: Limit order                                                                                         |
          |              |           |                                                                                                          |
          |              |           |   3: Best own side price                                                                                 |
          |              |           |                                                                                                          |
          |              |           |   10: Cancel order (Shanghai only; cancel records are in entrust)                                        |
          |              |           |                                                                                                          |
          |              |           | - trade:                                                                                                 |
          |              |           |                                                                                                          |
          |              |           |   0: Trade                                                                                               |
          |              |           |                                                                                                          |
          |              |           |   1: Cancel order (Shenzhen only; cancel records are in trade)                                           |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | price        | DOUBLE    | Order price                                                                                              |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | qty          | LONG      | Order quantity                                                                                           |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | buyNo        | LONG      | Original buy order number in trade; filled for entrust orders                                            |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | sellNo       | LONG      | Original sell order number in trade; filled for entrust orders                                           |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | direction    | INT       | 1 (Buy) or 2 (Sell)                                                                                      |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | channelNo    | INT       | Channel number                                                                                           |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | seqNum       | LONG      | Tick data sequence number                                                                                |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+
          | reserve1     | DOUBLE    | Reserved field 1 (for wide table)                                                                        |
          +--------------+-----------+----------------------------------------------------------------------------------------------------------+

        - Stock Tick + Snapshot (Wide Table)
        
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | Field          | Type           | Description                                                                                                  |
          +================+================+==============================================================================================================+
          | symbol         | SYMBOL         | Stock code:                                                                                                  |
          |                |                |                                                                                                              |
          |                |                | - Ends with ".XSHG" for Shanghai Stock Exchange                                                              |
          |                |                | - Ends with ".XSHE" for Shenzhen Stock Exchange                                                              |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | symbolSource   | STRING         | ".XSHG" (Shanghai Stock Exchange) or ".XSHE" (Shenzhen Stock Exchange)                                       |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | timestamp      | TIMESTAMP      | Timestamp                                                                                                    |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | sourceType     | INT            | 0 represents entrust data; 1 represents trade; 2 represents snapshot                                         |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | orderType      | INT            | - entrust:                                                                                                   |
          |                |                |                                                                                                              |
          |                |                |   1: Market order                                                                                            |
          |                |                |                                                                                                              |
          |                |                |   2: Limit order                                                                                             |
          |                |                |                                                                                                              |
          |                |                |   3: Best own side price                                                                                     |
          |                |                |                                                                                                              |
          |                |                |   10: Cancel order (Shanghai only; cancel records are in entrust)                                            |
          |                |                |                                                                                                              |
          |                |                | - trade:                                                                                                     |
          |                |                |                                                                                                              |
          |                |                |   0: Trade                                                                                                   |
          |                |                |                                                                                                              |
          |                |                |   1: Cancel order (Shenzhen only; cancel records are in trade)                                               |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | price          | DOUBLE         | Order price                                                                                                  |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | qty            | LONG           | Order quantity                                                                                               |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | buyNo          | LONG           | Original buy order number in trade; filled for entrust orders                                                |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | sellNo         | LONG           | Original sell order number in trade; filled for entrust orders                                               |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | direction      | INT            | 1 (Buy) or 2 (Sell)                                                                                          |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | channelNo      | INT            | Channel number                                                                                               |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | seqNum         | LONG           | Tick data sequence number                                                                                    |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | lastPrice      | DOUBLE         | Latest trade price                                                                                           |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | upLimitPrice   | DOUBLE         | Upper limit price                                                                                            |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | downLimitPrice | DOUBLE         | Lower limit price                                                                                            |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | totalBidQty    | LONG           | Interval buy quantity                                                                                        |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | totalOfferQty  | LONG           | Interval sell quantity                                                                                       |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | bidPrice       | DOUBLE[]       | List of buy prices                                                                                           |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | bidQty         | LONG[]         | List of buy quantities                                                                                       |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | offerPrice     | DOUBLE[]       | List of sell prices                                                                                          |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | offerQty       | LONG[]         | List of sell quantities                                                                                      |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | prevClosePrice | DOUBLE         | Previous close price                                                                                         |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | reserve1       | DOUBLE         | Reserved field 1 (for wide table)                                                                            |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+
          | reserve2       | DOUBLE         | Reserved field 2 (for wide table)                                                                            |
          +----------------+----------------+--------------------------------------------------------------------------------------------------------------+

        """
        pass

    def on_snapshot(self, context, msg, indicator):
        """The callback function is triggered upon receiving snapshot market data.

        Parameters
        ----------
        context : _type_
            A dictionary representing the global context of the strategy. It is used to store 
            and manage all user-defined variables within the strategy. In addition, 
            the backtesting engine maintains four internal variables within the context:

            - context.tradeTime — Returns the latest market timestamp.

            - context.tradeDate — Returns the current trading date.

            - context.BarTime — Returns the current bar timestamp when market snapshots 
              are aggregated into lower-frequency bars.
              
            - context.engine — Returns the internal instance handle of the backtesting engine.
        msg : _type_
            Represents the tick-level market data. Each record is provided as either a dictionary object 
            or a table (depending on the msg_as_table configuration). The specific fields vary 
            by asset type. For details, refer to the msg data section below.
        indicator : _type_
            A dictionary or nested dictionary with a structure consistent with the corresponding msg, 
            containing the data subscribed to by the strategy.
        
        
        Msg data
        ---------------
        
        - Stock Tick / Margin Trading
        
          +-----------------+-----------+-----------------------------------------------------------+
          | Field           | Type      | Description                                               |
          +=================+===========+===========================================================+
          | symbol          | SYMBOL    | Stock code                                                |
          |                 |           | - Ends with ".XSHG" for Shanghai Stock Exchange           |
          |                 |           | - Ends with ".XSHE" for Shenzhen Stock Exchange           |
          +-----------------+-----------+-----------------------------------------------------------+
          | symbolSource    | SYMBOL    | Stock market                                              |
          |                 |           |                                                           |
          |                 |           | - ".XSHG": Shanghai Stock Exchange                        |
          |                 |           | - ".XSHE": Shenzhen Stock Exchange                        |
          +-----------------+-----------+-----------------------------------------------------------+
          | timestamp       | TIMESTAMP | Timestamp                                                 |
          +-----------------+-----------+-----------------------------------------------------------+
          | lastPrice       | DOUBLE    | Latest trade price                                        |
          +-----------------+-----------+-----------------------------------------------------------+
          | upLimitPrice    | DOUBLE    | Upper limit price                                         |
          +-----------------+-----------+-----------------------------------------------------------+
          | downLimitPrice  | DOUBLE    | Lower limit price                                         |
          +-----------------+-----------+-----------------------------------------------------------+
          | totalBidQty     | LONG      | Total bid quantity                                        |
          +-----------------+-----------+-----------------------------------------------------------+
          | totalOfferQty   | LONG      | Total offer quantity                                      |
          +-----------------+-----------+-----------------------------------------------------------+
          | bidPrice        | DOUBLE[]  | List of bid prices                                        |
          +-----------------+-----------+-----------------------------------------------------------+
          | bidQty          | LONG[]    | List of bid quantities                                    |
          +-----------------+-----------+-----------------------------------------------------------+
          | offerPrice      | DOUBLE[]  | List of offer prices                                      |
          +-----------------+-----------+-----------------------------------------------------------+
          | offerQty        | LONG[]    | List of offer quantities                                  |
          +-----------------+-----------+-----------------------------------------------------------+
          | signal          | DOUBLE[]  | List of indicators                                        |
          +-----------------+-----------+-----------------------------------------------------------+

        - Stock tick or tick + snapshot
        
          +-----------------+------------+----------------------------------------------------------------------------------+
          | Name            | Type       | Description                                                                      |
          +=================+============+==================================================================================+
          | symbol          | SYMBOL     | Stock code                                                                       |
          |                 |            |                                                                                  |
          |                 |            | - Ends with ".XSHG" for Shanghai Stock Exchange                                  |
          |                 |            | - Ends with ".XSHE" for Shenzhen Stock Exchange                                  |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | symbolSource    | STRING     | Stock market                                                                     |
          |                 |            |                                                                                  |
          |                 |            | - ".XSHG": Shanghai Stock Exchange                                               |
          |                 |            | - ".XSHE": Shenzhen Stock Exchange                                               |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | timestamp       | TIMESTAMP  | Timestamp                                                                        |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | lastPrice       | DOUBLE     | Latest trade price                                                               |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | upLimitPrice    | DOUBLE     | Upper limit price                                                                |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | downLimitPrice  | DOUBLE     | Lower limit price                                                                |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | totalBidQty     | LONG       | Total bid quantity                                                               |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | totalOfferQty   | LONG       | Total offer quantity                                                             |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | bidPrice        | DOUBLE[]   | List of bid prices                                                               |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | bidQty          | LONG[]     | List of bid quantities                                                           |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | offerPrice      | DOUBLE[]   | List of offer prices                                                             |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | offerQty        | LONG[]     | List of offer quantities                                                         |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | signal          | DOUBLE[]   | Other indicators                                                                 |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | open            | DOUBLE     | Open price of the aggregated bar data                                            |
          |                 |            | *(Available only when data_type = 1 or 2, and callback_for_snapshot = 1 or 2)*   |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | close           | DOUBLE     | Close price of the aggregated bar data                                           |
          |                 |            | *(Available only when data_type = 1 or 2, and callback_for_snapshot = 1 or 2)*   |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | low             | DOUBLE     | Lowest price of the aggregated bar data                                          |
          |                 |            | *(Available only when data_type = 1 or 2, and callback_for_snapshot = 1 or 2)*   |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | high            | DOUBLE     | Highest price of the aggregated bar data                                         |
          |                 |            | *(Available only when data_type = 1 or 2, and callback_for_snapshot = 1 or 2)*   |
          +-----------------+------------+----------------------------------------------------------------------------------+
          | volume          | LONG       | Trading volume of the aggregated bar data                                        |
          |                 |            | *(Available only when data_type = 1 or 2, and callback_for_snapshot = 1 or 2)*   |
          +-----------------+------------+----------------------------------------------------------------------------------+
        
        - Stock Snapshot + Tick
        
          +-----------------+------------+---------------------------------------------------------------------------------+
          | Field           | Type       | Description                                                                     |
          +=================+============+=================================================================================+
          | symbol          | SYMBOL     | Stock code                                                                      |
          |                 |            |                                                                                 |
          |                 |            | - Ends with ".XSHG" for Shanghai Stock Exchange                                 |
          |                 |            | - Ends with ".XSHE" for Shenzhen Stock Exchange                                 |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | symbolSource    | STRING     | Stock market identifier                                                         |
          |                 |            |                                                                                 |
          |                 |            | - ".XSHG": Shanghai Stock Exchange                                              |
          |                 |            | - ".XSHE": Shenzhen Stock Exchange                                              |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | timestamp       | TIMESTAMP  | Timestamp                                                                       |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | lastPrice       | DOUBLE     | Latest traded price                                                             |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | upLimitPrice    | DOUBLE     | Upper limit price                                                               |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | downLimitPrice  | DOUBLE     | Lower limit price                                                               |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | totalBidQty     | LONG       | Total bid quantity executed                                                     |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | totalOfferQty   | LONG       | Total offer quantity executed                                                   |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | bidPrice        | DOUBLE[]   | List of bid prices                                                              |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | bidQty          | LONG[]     | List of bid quantities                                                          |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | offerPrice      | DOUBLE[]   | List of offer prices                                                            |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | offerQty        | LONG[]     | List of offer quantities                                                        |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | signal          | DOUBLE[]   | Other indicators                                                                |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | open            | DOUBLE     | Open price of the aggregated bar data                                           |
          |                 |            | *(Available only when data_type = 1 or 2, and callback_for_snapshot = 1 or 2)*  |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | close           | DOUBLE     | Close price of the aggregated bar data                                          |
          |                 |            | *(Available only when data_type = 1 or 2, and callback_for_snapshot = 1 or 2)*  |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | low             | DOUBLE     | Lowest price of the aggregated bar data                                         |
          |                 |            | *(Available only when data_type = 1 or 2, and callback_for_snapshot = 1 or 2)*  |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | high            | DOUBLE     | Highest price of the aggregated bar data                                        |
          |                 |            | *(Available only when data_type = 1 or 2, and callback_for_snapshot = 1 or 2)*  |
          +-----------------+------------+---------------------------------------------------------------------------------+
          | volume          | LONG       | Trading volume of the aggregated bar data                                       |
          |                 |            | *(Available only when data_type = 1 or 2, and callback_for_snapshot = 1 or 2)*  |
          +-----------------+------------+---------------------------------------------------------------------------------+

        - Stock Tick (Wide Table)
        
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | Field         | Type       | Description                                                                                                                               |
          +===============+============+===========================================================================================================================================+
          | symbol        | SYMBOL     | Stock code                                                                                                                                |
          |               |            |                                                                                                                                           |
          |               |            | - Ends with ".XSHG" for Shanghai Stock Exchange                                                                                           |
          |               |            | - Ends with ".XSHE" for Shenzhen Stock Exchange                                                                                           |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | symbolSource  | STRING     | Stock market identifier                                                                                                                   |
          |               |            |                                                                                                                                           |
          |               |            | - ".XSHG": Shanghai Stock Exchange                                                                                                        |
          |               |            | - ".XSHE": Shenzhen Stock Exchange                                                                                                        |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | timestamp     | TIMESTAMP  | Timestamp                                                                                                                                 |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | sourceType    | INT        | Source type indicator                                                                                                                     |
          |               |            |                                                                                                                                           |
          |               |            | - 0: Entrust data (`entrust`)                                                                                                             |
          |               |            | - 1: Trade data (`trade`)                                                                                                                 |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | orderType     | INT        | Order type                                                                                                                                |
          |               |            |                                                                                                                                           |
          |               |            | - For `entrust`:                                                                                                                          |
          |               |            |                                                                                                                                           |
          |               |            |   1 = Market order; 2 = Limit order; 3 = Best bid/ask; 10 = Cancel order *(only for SSE, since cancellations are recorded in `entrust`)*  |
          |               |            |                                                                                                                                           |
          |               |            | - For `trade`:                                                                                                                            |
          |               |            |                                                                                                                                           |
          |               |            |   0 = Trade; 1 = Cancel order *(only for SZSE, since cancellations are recorded in `trade`)*                                              |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | price         | DOUBLE     | Order price                                                                                                                               |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | qty           | LONG       | Order quantity                                                                                                                            |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | buyNo         | LONG       | For `trade`: Corresponds to the original data.                                                                                            |
          |               |            | For `entrust`: Populated with the entrust order number.                                                                                   |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | sellNo        | LONG       | For `trade`: Corresponds to the original data.                                                                                            |
          |               |            | For `entrust`: Populated with the entrust order number.                                                                                   |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | direction     | INT        | Trade direction: 1 = Buy, 2 = Sell                                                                                                        |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | channelNo     | INT        | Channel number                                                                                                                            |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | seqNum        | LONG       | Tick-by-tick data sequence number                                                                                                         |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+
          | reserve1      | DOUBLE     | Reserved field 1 (for wide table)                                                                                                         |
          +---------------+------------+-------------------------------------------------------------------------------------------------------------------------------------------+

        - Stock Tick + Snapshot (Wide Table)
        
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | Field            | Type       | Description                                                                                                                      |
          +==================+============+==================================================================================================================================+
          | symbol           | SYMBOL     | Stock code                                                                                                                       |
          |                  |            |                                                                                                                                  |
          |                  |            | - Ends with ".XSHG" for Shanghai Stock Exchange                                                                                  |
          |                  |            | - Ends with ".XSHE" for Shenzhen Stock Exchange                                                                                  |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | symbolSource     | STRING     | Stock market identifier                                                                                                          |
          |                  |            |                                                                                                                                  |
          |                  |            | - ".XSHG": Shanghai Stock Exchange                                                                                               |
          |                  |            | - ".XSHE": Shenzhen Stock Exchange                                                                                               |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | timestamp        | TIMESTAMP  | Timestamp                                                                                                                        |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | sourceType       | INT        | Source type indicator                                                                                                            |
          |                  |            |                                                                                                                                  |
          |                  |            | - 0: Entrust data (`entrust`)                                                                                                    |
          |                  |            | - 1: Trade data (`trade`)                                                                                                        |
          |                  |            | - 2: Snapshot data (`snapshot`)                                                                                                  |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | orderType        | INT        | Order type                                                                                                                       |
          |                  |            |                                                                                                                                  |
          |                  |            | - For `entrust`:                                                                                                                 |
          |                  |            |                                                                                                                                  |
          |                  |            |   1 = Market order; 2 = Limit order; 3 = Best bid/ask; 10 = Cancel order *(only for SSE, cancellations recorded in `entrust`)*   |
          |                  |            |                                                                                                                                  |
          |                  |            | - For `trade`:                                                                                                                   |
          |                  |            |                                                                                                                                  |
          |                  |            |   0 = Trade; 1 = Cancel order *(only for SZSE, cancellations recorded in `trade`)*                                               |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | price            | DOUBLE     | Order price                                                                                                                      |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | qty              | LONG       | Order quantity                                                                                                                   |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | buyNo            | LONG       | For `trade`: corresponds to the original data                                                                                    |
          |                  |            | For `entrust`: populated with the entrust order number                                                                           |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | sellNo           | LONG       | For `trade`: corresponds to the original data                                                                                    |
          |                  |            | For `entrust`: populated with the entrust order number                                                                           |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | direction        | INT        | Trade direction: 1 = Buy, 2 = Sell                                                                                               |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | channelNo        | INT        | Channel number                                                                                                                   |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | seqNum           | LONG       | Tick-by-tick data sequence number                                                                                                |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | lastPrice        | DOUBLE     | Last traded price                                                                                                                |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | upLimitPrice     | DOUBLE     | Upper limit price                                                                                                                |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | downLimitPrice   | DOUBLE     | Lower limit price                                                                                                                |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | totalBidQty      | LONG       | Total bid quantity in the interval                                                                                               |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | totalOfferQty    | LONG       | Total ask quantity in the interval                                                                                               |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | bidPrice         | DOUBLE[]   | List of bid prices                                                                                                               |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | bidQty           | LONG[]     | List of bid quantities                                                                                                           |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | offerPrice       | DOUBLE[]   | List of ask prices                                                                                                               |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | offerQty         | LONG[]     | List of ask quantities                                                                                                           |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | prevClosePrice   | DOUBLE     | Previous closing price                                                                                                           |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | reserve1         | DOUBLE     | Reserved field 1 (for wide table)                                                                                                |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+
          | reserve2         | DOUBLE     | Reserved field 2 (for wide table)                                                                                                |
          +------------------+------------+----------------------------------------------------------------------------------------------------------------------------------+

        - Options snapshot
        
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | Name              | Type           | Description                                                                    |
          +===================+================+================================================================================+
          | symbol            | SYMBOL         | Option code                                                                    |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | symbolSource      | STRING         | Exchange                                                                       |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | timestamp         | TIMESTAMP      | Timestamp                                                                      |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | tradingDay        | DATE           | Trading day / Settlement date                                                  |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | lastPrice         | DOUBLE         | Latest trade price                                                             |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | upLimitPrice      | DOUBLE         | Upper limit price                                                              |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | downLimitPrice    | DOUBLE         | Lower limit price                                                              |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | totalBidQty       | LONG           | Interval total buy quantity                                                    |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | totalOfferQty     | LONG           | Interval total sell quantity                                                   |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | bidPrice          | DOUBLE[]       | List of bid prices                                                             |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | bidQty            | LONG[]         | List of bid quantities                                                         |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | offerPrice        | DOUBLE[]       | List of ask prices                                                             |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | offerQty          | LONG[]         | List of ask quantities                                                         |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | highPrice         | DOUBLE         | Highest price                                                                  |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | lowPrice          | DOUBLE         | Lowest price                                                                   |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | signal            | DOUBLE[]       | List of other fields                                                           |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | prevClosePrice    | DOUBLE         | Previous closing price                                                         |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | settlementPrice   | DOUBLE         | Settlement price                                                               |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | prevSettlementPrice | DOUBLE       | Previous settlement price                                                      |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | underlyingPrice   | DOUBLE         | Underlying asset price                                                         |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | Theta             | DOUBLE         | /                                                                              |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | Vega              | DOUBLE         | /                                                                              |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | Gamma             | DOUBLE         | /                                                                              |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | Delta             | DOUBLE         | /                                                                              |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | IV                | DOUBLE         | /                                                                              |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | open              | DOUBLE         | Open price of synthetic bar (available only if data_type = 1 or 2, and         |
          |                   |                | callback_for_snapshot = 1 or 2)                                                |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | close             | DOUBLE         | Close price of synthetic bar (available only if data_type = 1 or 2, and        |
          |                   |                | callback_for_snapshot = 1 or 2)                                                |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | low               | DOUBLE         | Lowest price of synthetic bar (available only if data_type = 1 or 2, and       |
          |                   |                | callback_for_snapshot = 1 or 2)                                                |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | high              | DOUBLE         | Highest price of synthetic bar (available only if data_type = 1 or 2, and      |
          |                   |                | callback_for_snapshot = 1 or 2)                                                |
          +-------------------+----------------+--------------------------------------------------------------------------------+
          | volume            | LONG           | Volume of synthetic bar (available only if data_type = 1 or 2, and             |
          |                   |                | callback_for_snapshot = 1 or 2)                                                |
          +-------------------+----------------+--------------------------------------------------------------------------------+

        .. note::
            When generating bar data from snapshots (frequency > 0 and callback_for_snapshot = 1 or 2), 
            the input parameter msg should additionally include five fields: "open", "close", "low", "high", "volume".
        
        - Futures Snapshot

          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | Field               | Type      | Description                                                                                  |
          +=====================+===========+==============================================================================================+
          | symbol              | SYMBOL    | Futures contract code                                                                        |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | symbolSource        | STRING    | Exchange                                                                                     |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | timestamp           | TIMESTAMP | Timestamp                                                                                    |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | tradingDay          | DATE      | Trading day / settlement date                                                                |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | lastPrice           | DOUBLE    | Last traded price                                                                            |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | upLimitPrice        | DOUBLE    | Upper limit price                                                                            |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | downLimitPrice      | DOUBLE    | Lower limit price                                                                            |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | totalBidQty         | LONG      | Total buy quantity in the interval                                                           |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | totalOfferQty       | LONG      | Total sell quantity in the interval                                                          |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | bidPrice            | DOUBLE[]  | List of bid prices                                                                           |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | bidQty              | LONG[]    | List of bid quantities                                                                       |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | offerPrice          | DOUBLE[]  | List of ask prices                                                                           |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | offerQty            | LONG[]    | List of ask quantities                                                                       |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | highPrice           | DOUBLE    | Highest price                                                                                |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | lowPrice            | DOUBLE    | Lowest price                                                                                 |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | signal              | DOUBLE[]  | List of other fields                                                                         |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | prevClosePrice      | DOUBLE    | Previous closing price                                                                       |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | settlementPrice     | DOUBLE    | Settlement price                                                                             |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | prevSettlementPrice | DOUBLE    | Previous settlement price                                                                    |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | open                | DOUBLE    | Open price of the synthesized bar (available only when dataType = 1 or 2 and                 |
          |                     |           | callbackForSnapshot = 1 or 2)                                                                |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | close               | DOUBLE    | Close price of the synthesized bar (available only when dataType = 1 or 2 and                |
          |                     |           | callbackForSnapshot = 1 or 2)                                                                |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | low                 | DOUBLE    | Lowest price of the synthesized bar (available only when dataType = 1 or 2 and               |
          |                     |           | callbackForSnapshot = 1 or 2)                                                                |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | high                | DOUBLE    | Highest price of the synthesized bar (available only when dataType = 1 or 2 and              |
          |                     |           | callbackForSnapshot = 1 or 2)                                                                |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+
          | volume              | LONG      | Volume of the synthesized bar (available only when dataType = 1 or 2 and                     |
          |                     |           | callbackForSnapshot = 1 or 2)                                                                |
          +---------------------+-----------+----------------------------------------------------------------------------------------------+

        .. note::
            When generating bar data from snapshots (frequency > 0 and callbackForSnapshot = 1 or 2), 
            the input parameter msg should additionally include five fields: "open", "close", "low", "high", "volume".        
        
        - Interbank Bond Snapshot
        
          +----------------+-----------+-----------------------------------+
          | Field          | Type      | Description                       |
          +================+===========+===================================+
          | symbol         | SYMBOL    | Instrument code                   |
          +----------------+-----------+-----------------------------------+
          | messageSource  | SYMBOL    | Market: Interbank "X_BOND"        |
          +----------------+-----------+-----------------------------------+
          | byield         | TIMESTAMP | Timestamp                         |
          +----------------+-----------+-----------------------------------+
          | ayield         | DOUBLE[]  | Bid yields                        |
          +----------------+-----------+-----------------------------------+
          | bmdEntryPrice  | DOUBLE[]  | Bid net price (CNY)               |
          +----------------+-----------+-----------------------------------+
          | amdEntryPrice  | DOUBLE[]  | Ask net price (CNY)               |
          +----------------+-----------+-----------------------------------+
          | bmdEntrySize   | LONG[]    | Bid quantity (CNY)                |
          +----------------+-----------+-----------------------------------+
          | amdEntrySize   | LONG[]    | Ask quantity (CNY)                |
          +----------------+-----------+-----------------------------------+
          | bsettlType     | LONG[]    | Buy settlement speed              |
          +----------------+-----------+-----------------------------------+
          | asettlType     | LONG[]    | Sell settlement speed             |
          +----------------+-----------+-----------------------------------+
          | settlType      | LONG[]    | Interval settlement speed         |
          +----------------+-----------+-----------------------------------+
          | tradePrice     | DOUBLE[]  | List of interval trade prices     |
          +----------------+-----------+-----------------------------------+
          | tradeYield     | DOUBLE[]  | Yield to maturity                 |
          +----------------+-----------+-----------------------------------+
          | tradeQty       | LONG[]    | List of interval trade quantities |
          +----------------+-----------+-----------------------------------+

        - Cryptocurrency Snapshot

          +---------------------+----------------+--------------------------------------------------------------------------------+
          | Field               | Type           | Description                                                                    |
          +=====================+================+================================================================================+
          | symbol              | STRING         | Instrument code                                                                |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | symbolSource        | STRING         | Exchange                                                                       |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | timestamp           | TIMESTAMP      | Timestamp                                                                      |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | tradingDay          | DATE           | Trading day / settlement date                                                  |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | lastPrice           | DECIMAL128(8)  | Last traded price                                                              |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | upLimitPrice        | DECIMAL128(8)  | Upper limit price                                                              |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | downLimitPrice      | DECIMAL128(8)  | Lower limit price                                                              |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | totalBidQty         | DECIMAL128(8)  | Interval bid quantity                                                          |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | totalOfferQty       | DECIMAL128(8)  | Interval ask quantity                                                          |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | bidPrice            | DECIMAL128(8)[]| List of bid prices                                                             |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | bidQty              | DECIMAL128(8)[]| List of bid quantities                                                         |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | offerPrice          | DECIMAL128(8)[]| List of ask prices                                                             |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | offerQty            | DECIMAL128(8)[]| List of ask quantities                                                         |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | highPrice           | DECIMAL128(8)  | Highest price                                                                  |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | lowPrice            | DECIMAL128(8)  | Lowest price                                                                   |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | signal              | DOUBLE[]       | Other indicator fields                                                         |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | prevClosePrice      | DECIMAL128(8)  | Previous closing price                                                         |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | settlementPrice     | DECIMAL128(8)  | Settlement price                                                               |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | prevSettlementPrice | DECIMAL128(8)  | Previous settlement price                                                      |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          | contractType        | INT            | Instrument type:                                                               |
          |                     |                |                                                                                |
          |                     |                | 0: Spot                                                                        |
          |                     |                |                                                                                |
          |                     |                | 1: Delivery contract                                                           |
          |                     |                |                                                                                |
          |                     |                | 2: Perpetual contract                                                          |
          |                     |                |                                                                                |
          |                     |                | 3: Option                                                                      |
          +---------------------+----------------+--------------------------------------------------------------------------------+
          """
        pass

    def on_bar(self, context, msg, indicator):
        """The callback function (minute or daily frequency) is triggered when subscribed 
        snapshot data is aggregated into bar data.

        Parameters
        ----------
        context : _type_
            A dictionary representing the global context of the strategy. It is used to store 
            and manage all user-defined variables within the strategy. In addition, 
            the backtesting engine maintains four internal variables within the context:

            - context.tradeTime — Returns the latest market timestamp.

            - context.tradeDate — Returns the current trading date.

            - context.BarTime — Returns the current bar timestamp when market snapshots 
              are aggregated into lower-frequency bars.
              
            - context.engine — Returns the internal instance handle of the backtesting engine.
        msg : _type_
            Represents the tick-level market data. Each record is provided as either a dictionary object 
            or a table (depending on the msg_as_table configuration). The specific fields vary 
            by asset type. For details, refer to the msg data section below.
        indicator : _type_
            A dictionary or nested dictionary with a structure consistent with the corresponding msg, 
            containing the data subscribed to by the strategy.
           
            
        Msg data
        ----------------
        
        - Stock snapshot / Snapshot + tick trade details / Minute or daily frequency
        
          +----------------+---------------+--------------------------------------------------------+
          | Field          | Type          | Description                                            |
          +================+===============+========================================================+
          | symbol         | SYMBOL        | Stock code                                             |
          |                |               | Ends with ".XSHG" for SSE                              |
          |                |               | Ends with ".XSHE" for SZSE                             |
          +----------------+---------------+--------------------------------------------------------+
          | tradeTime      | TIMESTAMP     | Trading day                                            |
          +----------------+---------------+--------------------------------------------------------+
          | open           | DOUBLE        | Opening price                                          |
          +----------------+---------------+--------------------------------------------------------+
          | low            | DOUBLE        | Lowest price                                           |
          +----------------+---------------+--------------------------------------------------------+
          | high           | DOUBLE        | Highest price                                          |
          +----------------+---------------+--------------------------------------------------------+
          | close          | DOUBLE        | Closing price                                          |
          +----------------+---------------+--------------------------------------------------------+
          | volume         | LONG          | Trading volume                                         |
          +----------------+---------------+--------------------------------------------------------+
          | amount         | DOUBLE        | Trading amount                                         |
          +----------------+---------------+--------------------------------------------------------+
          | upLimitPrice   | DOUBLE        | Upper limit price                                      |
          +----------------+---------------+--------------------------------------------------------+
          | downLimitPrice | DOUBLE        | Lower limit price                                      |
          +----------------+---------------+--------------------------------------------------------+
          | prevClosePrice | DOUBLE        | Previous closing price                                 |
          +----------------+---------------+--------------------------------------------------------+
          | signal         | DOUBLE[]      | Other indicators / metrics                             |
          +----------------+---------------+--------------------------------------------------------+
        
        - Option snapshot
        
          When callback_for_snapshot = 1 or 2 is configured in the backtesting engine, 
          the callback function on_bar will be triggered. The input parameter msg represents 
          a K-line bar, with each K-line containing the following fields:
          
          +---------------------+---------------+----------------------------------------------------------+
          | Field               | Type          | Description                                              |
          +=====================+===============+==========================================================+
          | symbol              | SYMBOL        | Option code                                              |
          +---------------------+---------------+----------------------------------------------------------+
          | symbolSource        | STRING        | Exchange                                                 |
          +---------------------+---------------+----------------------------------------------------------+
          | tradeTime           | TIMESTAMP     | Timestamp                                                |
          +---------------------+---------------+----------------------------------------------------------+
          | tradingDay          | DATE          | Trading day / settlement date                            |
          +---------------------+---------------+----------------------------------------------------------+
          | open                | DOUBLE        | Opening price                                            |
          +---------------------+---------------+----------------------------------------------------------+
          | low                 | DOUBLE        | Lowest price                                             |
          +---------------------+---------------+----------------------------------------------------------+
          | high                | DOUBLE        | Highest price                                            |
          +---------------------+---------------+----------------------------------------------------------+
          | close               | DOUBLE        | Closing price                                            |
          +---------------------+---------------+----------------------------------------------------------+
          | volume              | LONG          | Trading volume                                           |
          +---------------------+---------------+----------------------------------------------------------+
          | amount              | DOUBLE        | Trading amount                                           |
          +---------------------+---------------+----------------------------------------------------------+
          | upLimitPrice        | DOUBLE        | Upper limit price                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | downLimitPrice      | DOUBLE        | Lower limit price                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | signal              | DOUBLE[]      | Other indicators / metrics                               |
          +---------------------+---------------+----------------------------------------------------------+
          | prevClosePrice      | DOUBLE        | Previous closing price                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | settlementPrice     | DOUBLE        | Settlement price                                         |
          +---------------------+---------------+----------------------------------------------------------+
          | prevSettlementPrice | DOUBLE        | Previous settlement price                                |
          +---------------------+---------------+----------------------------------------------------------+
          | underlyingPrice     | DOUBLE        | Underlying asset price                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | Theta               | DOUBLE        | /                                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | Vega                | DOUBLE        | /                                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | Gamma               | DOUBLE        | /                                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | Delta               | DOUBLE        | /                                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | IV                  | DOUBLE        | /                                                        |
          +---------------------+---------------+----------------------------------------------------------+
        
        - Option minute or daily frequency
        
          The input parameter msg represents a K-line bar, with each K-line containing the following fields:
          
          +---------------------+---------------+----------------------------------------------------------+
          | Field               | Type          | Description                                              |
          +=====================+===============+==========================================================+
          | symbol              | SYMBOL        | Option code                                              |
          +---------------------+---------------+----------------------------------------------------------+
          | symbolSource        | STRING        | Exchange                                                 |
          +---------------------+---------------+----------------------------------------------------------+
          | tradeTime           | TIMESTAMP     | Timestamp                                                |
          +---------------------+---------------+----------------------------------------------------------+
          | tradingDay          | DATE          | Trading day / settlement date                            |
          +---------------------+---------------+----------------------------------------------------------+
          | open                | DOUBLE        | Opening price                                            |
          +---------------------+---------------+----------------------------------------------------------+
          | low                 | DOUBLE        | Lowest price                                             |
          +---------------------+---------------+----------------------------------------------------------+
          | high                | DOUBLE        | Highest price                                            |
          +---------------------+---------------+----------------------------------------------------------+
          | close               | DOUBLE        | Closing price                                            |
          +---------------------+---------------+----------------------------------------------------------+
          | volume              | LONG          | Trading volume                                           |
          +---------------------+---------------+----------------------------------------------------------+
          | amount              | DOUBLE        | Trading amount                                           |
          +---------------------+---------------+----------------------------------------------------------+
          | upLimitPrice        | DOUBLE        | Upper limit price                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | downLimitPrice      | DOUBLE        | Lower limit price                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | signal              | DOUBLE[]      | Other fields list                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | prevClosePrice      | DOUBLE        | Previous closing price                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | settlementPrice     | DOUBLE        | Settlement price                                         |
          +---------------------+---------------+----------------------------------------------------------+
          | prevSettlementPrice | DOUBLE        | Previous settlement price                                |
          +---------------------+---------------+----------------------------------------------------------+
          | underlyingPrice     | DOUBLE        | Underlying asset price                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | Theta               | DOUBLE        | /                                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | Vega                | DOUBLE        | /                                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | Gamma               | DOUBLE        | /                                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | Delta               | DOUBLE        | /                                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | IV                  | DOUBLE        | /                                                        |
          +---------------------+---------------+----------------------------------------------------------+
        
        - Futures snapshot
        
          When callbackForSnapshot = 1, the callback function on_bar will be triggered. 
          The input parameter msg represents a K-line bar, with each K-line containing the following fields:
          
          +---------------------+---------------+----------------------------------------------------------+
          | Field               | Type          | Description                                              |
          +=====================+===============+==========================================================+
          | symbol              | SYMBOL        | Futures code                                             |
          +---------------------+---------------+----------------------------------------------------------+
          | symbolSource        | STRING        | Exchange                                                 |
          +---------------------+---------------+----------------------------------------------------------+
          | timestamp           | TIMESTAMP     | Timestamp                                                |
          +---------------------+---------------+----------------------------------------------------------+
          | tradingDay          | DATE          | Trading day / settlement date                            |
          +---------------------+---------------+----------------------------------------------------------+
          | lastPrice           | DOUBLE        | Latest traded price                                      |
          +---------------------+---------------+----------------------------------------------------------+
          | upLimitPrice        | DOUBLE        | Upper limit price                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | downLimitPrice      | DOUBLE        | Lower limit price                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | totalBidQty         | LONG          | Interval buy quantity                                    |
          +---------------------+---------------+----------------------------------------------------------+
          | totalOfferQty       | LONG          | Interval sell quantity                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | bidPrice            | DOUBLE[]      | List of bid prices                                       |
          +---------------------+---------------+----------------------------------------------------------+
          | bidQty              | LONG[]        | List of bid quantities                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | offerPrice          | DOUBLE[]      | List of ask prices                                       |
          +---------------------+---------------+----------------------------------------------------------+
          | offerQty            | LONG[]        | List of ask quantities                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | highPrice           | DOUBLE        | Highest price                                            |
          +---------------------+---------------+----------------------------------------------------------+
          | lowPrice            | DOUBLE        | Lowest price                                             |
          +---------------------+---------------+----------------------------------------------------------+
          | signal              | DOUBLE[]      | Other fields list                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | prevClosePrice      | DOUBLE        | Previous closing price                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | settlementPrice     | DOUBLE        | Settlement price                                         |
          +---------------------+---------------+----------------------------------------------------------+
          | prevSettlementPrice | DOUBLE        | Previous settlement price                                |
          +---------------------+---------------+----------------------------------------------------------+
        
        - Futures minute or daily frequency
        
          The input parameter msg represents a K-line bar, with each K-line containing the following fields:
          
          +---------------------+---------------+----------------------------------------------------------+
          | Field               | Type          | Description                                              |
          +=====================+===============+==========================================================+
          | symbol              | SYMBOL        | Futures code                                             |
          +---------------------+---------------+----------------------------------------------------------+
          | symbolSource        | STRING        | Exchange                                                 |
          +---------------------+---------------+----------------------------------------------------------+
          | timestamp           | TIMESTAMP     | Timestamp                                                |
          +---------------------+---------------+----------------------------------------------------------+
          | tradingDay          | DATE          | Trading day / settlement date                            |
          +---------------------+---------------+----------------------------------------------------------+
          | lastPrice           | DOUBLE        | Latest traded price                                      |
          +---------------------+---------------+----------------------------------------------------------+
          | upLimitPrice        | DOUBLE        | Upper limit price                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | downLimitPrice      | DOUBLE        | Lower limit price                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | totalBidQty         | LONG          | Interval buy quantity                                    |
          +---------------------+---------------+----------------------------------------------------------+
          | totalOfferQty       | LONG          | Interval sell quantity                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | bidPrice            | DOUBLE[]      | List of bid prices                                       |
          +---------------------+---------------+----------------------------------------------------------+
          | bidQty              | LONG[]        | List of bid quantities                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | offerPrice          | DOUBLE[]      | List of ask prices                                       |
          +---------------------+---------------+----------------------------------------------------------+
          | offerQty            | LONG[]        | List of ask quantities                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | highPrice           | DOUBLE        | Highest price                                            |
          +---------------------+---------------+----------------------------------------------------------+
          | lowPrice            | DOUBLE        | Lowest price                                             |
          +---------------------+---------------+----------------------------------------------------------+
          | signal              | DOUBLE[]      | Other fields list                                        |
          +---------------------+---------------+----------------------------------------------------------+
          | prevClosePrice      | DOUBLE        | Previous closing price                                   |
          +---------------------+---------------+----------------------------------------------------------+
          | settlementPrice     | DOUBLE        | Settlement price                                         |
          +---------------------+---------------+----------------------------------------------------------+
          | prevSettlementPrice | DOUBLE        | Previous settlement price                                |
          +---------------------+---------------+----------------------------------------------------------+
        
        - Digital currency minute or daily frequency
        
          +---------------------+----------------+--------------------------------------------------+
          | Field               | Type           | Description                                      |
          +=====================+================+==================================================+
          | symbol              | SYMBOL         | Instrument code                                  |
          +---------------------+----------------+--------------------------------------------------+
          | symbolSource        | SYMBOL         | Exchange                                         |
          +---------------------+----------------+--------------------------------------------------+
          | tradeTime           | TIMESTAMP      | Timestamp                                        |
          +---------------------+----------------+--------------------------------------------------+
          | tradingDay          | DATE           | Trading day / settlement date                    |
          +---------------------+----------------+--------------------------------------------------+
          | open                | DECIMAL128(8)  | Opening price                                    |
          +---------------------+----------------+--------------------------------------------------+
          | low                 | DECIMAL128(8)  | Lowest price                                     |
          +---------------------+----------------+--------------------------------------------------+
          | high                | DECIMAL128(8)  | Highest price                                    |
          +---------------------+----------------+--------------------------------------------------+
          | close               | DECIMAL128(8)  | Closing price                                    |
          +---------------------+----------------+--------------------------------------------------+
          | volume              | DECIMAL128(8)  | Trading volume                                   |
          +---------------------+----------------+--------------------------------------------------+
          | amount              | DECIMAL128(8)  | Trading amount                                   |
          +---------------------+----------------+--------------------------------------------------+
          | upLimitPrice        | DECIMAL128(8)  | Upper limit price                                |
          +---------------------+----------------+--------------------------------------------------+
          | downLimitPrice      | DECIMAL128(8)  | Lower limit price                                |
          +---------------------+----------------+--------------------------------------------------+
          | signal              | DOUBLE[]       | Other fields list                                |
          +---------------------+----------------+--------------------------------------------------+
          | prevClosePrice      | DECIMAL128(8)  | Previous closing price                           |
          +---------------------+----------------+--------------------------------------------------+
          | settlementPrice     | DECIMAL128(8)  | Settlement price                                 |
          +---------------------+----------------+--------------------------------------------------+
          | prevSettlementPrice | DECIMAL128(8)  | Previous settlement price                        |
          +---------------------+----------------+--------------------------------------------------+
          | contractType        | INT            | Instrument type                                  |
          |                     |                |                                                  |
          |                     |                | 0: Spot                                          |
          |                     |                |                                                  |
          |                     |                | 1: Delivery contract                             |
          |                     |                |                                                  |
          |                     |                | 2: Perpetual contract                            |
          |                     |                |                                                  |
          |                     |                | 3: Option                                        |
          +---------------------+----------------+--------------------------------------------------+
       
        """
        pass

    def on_transaction(self, context, msg, indicator):
        """The callback function is triggered upon receiving tick-level trade details. 
        It is supported only for bonds traded on the Shanghai Stock Exchange.

        Parameters
        ----------
        context : _type_
            A dictionary representing the global context of the strategy. It is used to store 
            and manage all user-defined variables within the strategy. In addition, 
            the backtesting engine maintains four internal variables within the context:

            - context.tradeTime — Returns the latest market timestamp.

            - context.tradeDate — Returns the current trading date.

            - context.BarTime — Returns the current bar timestamp when market snapshots 
              are aggregated into lower-frequency bars.
              
            - context.engine — Returns the internal instance handle of the backtesting engine.
        msg : _type_
            Represents the market data. Each record is provided as either a dictionary object 
            or a table (depending on the msg_as_table configuration).
        indicator : _type_
            A dictionary or nested dictionary with a structure consistent with the corresponding msg, 
            containing the data subscribed to by the strategy.
        """
        pass

    def on_order(self, context, orders):
        """The order update notification function is triggered when an order status changes.

        Parameters
        ----------
        context : _type_
            A dictionary representing the global context of the strategy. It is used to store 
            and manage all user-defined variables within the strategy. In addition, 
            the backtesting engine maintains four internal variables within the context:

            - context.tradeTime — Returns the latest market timestamp.

            - context.tradeDate — Returns the current trading date.

            - context.BarTime — Returns the current bar timestamp when market snapshots 
              are aggregated into lower-frequency bars.
              
            - context.engine — Returns the internal instance handle of the backtesting engine.
        orders : _type_
            A dictionary containing order information. The field structure varies 
            depending on the asset type (for example, Shanghai Stock Exchange bonds 
            have a different order field structure than other asset classes).

            - Shanghai Stock Exchange Bonds
            
              +------------------+------------+------------------------------------------------------------+
              | Field            | Type       | Description                                                |
              +==================+============+============================================================+
              | orderId          | LONG       | Order ID                                                   |
              +------------------+------------+------------------------------------------------------------+
              | symbol           | STRING     | Security code                                              |
              +------------------+------------+------------------------------------------------------------+
              | timestamp        | TIMESTAMP  | Order timestamp                                            |
              +------------------+------------+------------------------------------------------------------+
              | bidQty           | LONG       | Bid quantity                                               |
              +------------------+------------+------------------------------------------------------------+
              | bidPrice         | DOUBLE     | Bid price                                                  |
              +------------------+------------+------------------------------------------------------------+
              | bidTotalVolume   | LONG       | Executed bid quantity                                      |
              +------------------+------------+------------------------------------------------------------+
              | askQty           | LONG       | Ask quantity                                               |
              +------------------+------------+------------------------------------------------------------+
              | askPrice         | DOUBLE     | Ask price                                                  |
              +------------------+------------+------------------------------------------------------------+
              | askTotalVolume   | LONG       | Executed ask quantity                                      |
              +------------------+------------+------------------------------------------------------------+
              | status           | INT        | Order status. Possible values:                             |
              |                  |            |                                                            |
              |                  |            | 4: Reported                                                |
              |                  |            |                                                            |
              |                  |            | 0: Partially filled                                        |
              |                  |            |                                                            |
              |                  |            | 1: Fully filled                                            |
              |                  |            |                                                            |
              |                  |            | 2: Cancelled                                               |
              |                  |            |                                                            |
              |                  |            | -1: Rejected                                               |
              |                  |            |                                                            |
              |                  |            | -2: Cancel reject                                          |
              |                  |            |                                                            |
              |                  |            | -3: Unfilled                                               |
              +------------------+------------+------------------------------------------------------------+
              | direction        | INT        | Order direction. Possible values:                          |
              |                  |            |                                                            |
              |                  |            | 1: Buy                                                     |
              |                  |            |                                                            |
              |                  |            | 2: Sell                                                    |
              |                  |            |                                                            |
              |                  |            | 3: Two-sided                                               |
              +------------------+------------+------------------------------------------------------------+
              | bidTradeValue    | DOUBLE     | Executed buy value                                         |
              +------------------+------------+------------------------------------------------------------+
              | askTradeValue    | DOUBLE     | Executed sell value                                        |
              +------------------+------------+------------------------------------------------------------+
              | label            | STRING     | Label, used to add remarks to the order                    |
              +------------------+------------+------------------------------------------------------------+
              | updateTime       | TIMESTAMP  | Update time                                                |
              +------------------+------------+------------------------------------------------------------+

            - Other Assets (excluding SSE Bonds)
            
              +----------------+------------+------------------------------------------------------------+
              | Field          | Type       | Description                                                |
              +================+============+============================================================+
              | orderId        | LONG       | Order ID                                                   |
              +----------------+------------+------------------------------------------------------------+
              | symbol         | STRING     | Security code                                              |
              +----------------+------------+------------------------------------------------------------+
              | symbolSource   | STRING     | Exchange (futures only)                                    |
              +----------------+------------+------------------------------------------------------------+
              | timestamp      | TIMESTAMP  | Order timestamp                                            |
              +----------------+------------+------------------------------------------------------------+
              | qty            | LONG       | Order quantity                                             |
              +----------------+------------+------------------------------------------------------------+
              | price          | DOUBLE     | Order price                                                |
              +----------------+------------+------------------------------------------------------------+
              | status         | INT        | Order status. Possible values:                             |
              |                |            |                                                            |
              |                |            | 4: Reported                                                |
              |                |            |                                                            |
              |                |            | 0: Partially filled                                        |
              |                |            |                                                            |
              |                |            | 1: Fully filled                                            |
              |                |            |                                                            |
              |                |            | 2: Cancelled                                               |
              |                |            |                                                            |
              |                |            | -1: Rejected                                               |
              |                |            |                                                            |
              |                |            | -2: Cancel reject                                          |
              +----------------+------------+------------------------------------------------------------+
              | direction      | INT        | Order direction. Possible values:                          |
              |                |            |                                                            |
              |                |            | 1: Open long                                               |
              |                |            |                                                            |
              |                |            | 2: Open short                                              |
              |                |            |                                                            |
              |                |            | 3: Close short                                             |
              |                |            |                                                            |
              |                |            | 4: Close long                                              |
              +----------------+------------+------------------------------------------------------------+
              | tradeQty       | LONG       | Total executed quantity                                    |
              +----------------+------------+------------------------------------------------------------+
              | tradeValue     | DOUBLE     | Total executed value                                       |
              +----------------+------------+------------------------------------------------------------+
              | label          | STRING     | Label, used to add remarks to the order                    |
              +----------------+------------+------------------------------------------------------------+
              | updateTime     | TIMESTAMP  | Update time                                                |
              +----------------+------------+------------------------------------------------------------+
        """
        pass

    def on_trade(self, context, trades):
        """The trade update notification function is triggered when an order is executed.

        Parameters
        ----------
        context : _type_
            A dictionary representing the global context of the strategy. It is used to store 
            and manage all user-defined variables within the strategy. In addition, 
            the backtesting engine maintains four internal variables within the context:

            - context.tradeTime — Returns the latest market timestamp.

            - context.tradeDate — Returns the current trading date.

            - context.BarTime — Returns the current bar timestamp when market snapshots 
              are aggregated into lower-frequency bars.
              
            - context.engine — Returns the internal instance handle of the backtesting engine.
        trades : _type_
            A dictionary containing trade information. The field definitions are as follows:
            
            +----------------+------------+------------------------------------------------------------+
            | Field          | Type       | Description                                                |
            +================+============+============================================================+
            | orderId        | LONG       | Order ID                                                   |
            +----------------+------------+------------------------------------------------------------+
            | symbol         | STRING     | Security code                                              |
            +----------------+------------+------------------------------------------------------------+
            | tradePrice     | DOUBLE     | Trade price of the current execution                       |
            +----------------+------------+------------------------------------------------------------+
            | tradeQty       | LONG       | Trade quantity of the current execution                    |
            +----------------+------------+------------------------------------------------------------+
            | tradeValue     | DOUBLE     | Trade value of the current execution                       |
            +----------------+------------+------------------------------------------------------------+
            | totalFee       | DOUBLE     | Total transaction fee                                      |
            +----------------+------------+------------------------------------------------------------+
            | bidTotalQty    | LONG       | Cumulative buy quantity                                    |
            +----------------+------------+------------------------------------------------------------+
            | bidTotalValue  | DOUBLE     | Cumulative buy value                                       |
            +----------------+------------+------------------------------------------------------------+
            | askTotalQty    | LONG       | Cumulative sell quantity                                   |
            +----------------+------------+------------------------------------------------------------+
            | askTotalValue  | DOUBLE     | Cumulative sell value                                      |
            +----------------+------------+------------------------------------------------------------+
            | direction      | INT        | Order direction. Possible values:                          |
            |                |            |                                                            |
            |                |            | 1: Open long                                               |
            |                |            |                                                            |
            |                |            | 2: Open short                                              |
            |                |            |                                                            |
            |                |            | 3: Close short                                             |
            |                |            |                                                            |
            |                |            | 4: Close long                                              |
            +----------------+------------+------------------------------------------------------------+
            | tradeTime      | TIMESTAMP  | Trade time                                                 |
            +----------------+------------+------------------------------------------------------------+
            | orderPrice     | DOUBLE     | Order price                                                |
            +----------------+------------+------------------------------------------------------------+
            | label          | STRING     | Label, used to add remarks to the order                    |
            +----------------+------------+------------------------------------------------------------+
        """
        pass

    def after_trading(self, context):
        """The callback function is triggered at the end of each trading day. 
        It can be used to summarize the day's trades, positions, and other statistics.
        
        Note: This function is not required for cryptocurrency strategies.

        Parameters
        ----------
        context : _type_
            A dictionary representing the global context of the strategy. It is used to store 
            and manage all user-defined variables within the strategy. In addition, 
            the backtesting engine maintains four internal variables within the context:

            - context.tradeTime — Returns the latest market timestamp.

            - context.tradeDate — Returns the current trading date.

            - context.BarTime — Returns the current bar timestamp when market snapshots 
              are aggregated into lower-frequency bars.
              
            - context.engine — Returns the internal instance handle of the backtesting engine.
        """
        pass

    def finalize(self, context):
        """The strategy termination callback function is triggered when the backtest completes.

        Parameters
        ----------
        context : _type_
            A dictionary representing the global context of the strategy. It is used to store 
            and manage all user-defined variables within the strategy. In addition, 
            the backtesting engine maintains four internal variables within the context:

            - context.tradeTime — Returns the latest market timestamp.

            - context.tradeDate — Returns the current trading date.

            - context.BarTime — Returns the current bar timestamp when market snapshots 
              are aggregated into lower-frequency bars.
              
            - context.engine — Returns the internal instance handle of the backtesting engine.
        """
        pass


class StrategyTemplate(StrategyBase, StrategyInterface):
    def __init__(self, engine: BacktesterBase):
        self.engine = weakref.ref(engine)

    @final
    @property
    def accounts(self):
        """Get the corresponding account based on the account type, and perform operations 
        or retrieve information using this account.
        
        """
        return self.engine().accounts

    @final
    def submit_order(self, msg, label: str = "", order_type: int = 0, account_type: AccountType = AccountType.DEFAULT):
        """This function can be called within callback functions to submit an order and returns the order ID.

        Parameters
        ----------
        msg : _type_
            A tuple representing the order information. The format varies depending on the asset type. 
            Please see details in "Order Format by Asset Type"
        label : str, optional
            A STRING scalar, used to assign a label to the order for categorization.
        order_type : int, optional
            An INT scalar. Optional values:

            - 0: Default, general order

            - 5: Limit stop-loss/take-profit order

            - 6: Market stop-loss/take-profit order

            - 8: Two-sided quote order (supported only for futures and options)
            
            Note: Types 5, 6, and 8 are algorithmic orders. Types 5 and 6 are supported 
            for stocks, futures, and options. Type 8 is supported only for futures and 
            options and can be enabled via the enableAlgoOrder configuration.
        account_type : AccountType, optional
            A STRING scalar, indicating the account type. Optional values: 
            "spot", "futures", "option", representing spot, futures/perpetual, 
            and option accounts, respectively. This parameter is applicable only for cryptocurrency strategies.


        Order Format by Asset Type
        ---------------------------
        - For orderType = 0, the format is:
        
          +-------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------+
          | Asset Type                          | Format                                                                                                                    | Description                                                                                                                                      |
          +=====================================+===========================================================================================================================+==================================================================================================================================================+
          | Stock (including                    | (Stock Code, Order Time, Order Type, Order Price, Order Quantity, Buy/Sell Direction)                                     | **Buy/Sell Direction:**                                                                                                                          |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
          | convertible bonds, funds)           |                                                                                                                           | 1: Buy Open; 2: Sell Open; 3: Sell Close; 4: Buy Close                                                                                           |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | **Order Type:**                                                                                                                                  |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | *Shanghai Stock Exchange:*                                                                                                                       |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 0: Market order - best 5 levels immediate or cancel                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 1: Market order - best 5 levels immediate and remaining as limit order                                                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 2: Market order - best price on own side                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 3: Market order - best price on opposite side                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 5: Limit order                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 6: Cancel order                                                                                                                                |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | *Shenzhen Stock Exchange:*                                                                                                                       |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 0: Market order - best 5 levels immediate or cancel                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 1: Market order - immediate or cancel remaining order                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 2: Market order - best price on own side                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 3: Market order - best price on opposite side                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 4: Market order - fill or kill order                                                                                                           |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 5: Limit order                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 6: Cancel order                                                                                                                                |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          +-------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------+
          | Futures / Options                   | (Symbol, Exchange Code, Time, Order Type, Order Price, Stop Loss/Take Profit Price, Order Quantity, Buy/Sell Direction,   | **Buy/Sell Direction:**                                                                                                                          |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     | Order Validity)                                                                                                           | 1: Buy Open; 2: Sell Open; 3: Sell Close; 4: Buy Close; 5: Option Exercise (only supported in multi-asset backtesting mode;                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | underlyingCode must be configured in the instrument info table)                                                                                  |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | **Order Type:**                                                                                                                                  |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 0: Market order - submitted at limit up/down price, time priority                                                                              |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 1: Market stop-loss order                                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 2: Market take-profit order                                                                                                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 3: Limit stop-loss order                                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 4: Limit take-profit order                                                                                                                     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 5: Limit order (default)                                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 6: Cancel order                                                                                                                                |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 9: Auto-trading mode (only Buy Open=1 or Sell Open=2 supported):                                                                               |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           |   * If Buy Open (1):                                                                                                                             |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           |     - If order quantity > longPosition, submit a Buy Open order.                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           |     - If order quantity ≤ longPosition, submit a Sell Close (3) order.                                                                           | 
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
          |                                     |                                                                                                                           |   * If Sell Open (2):                                                                                                                            |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           |     - If order quantity > shortPosition, submit a Sell Open order.                                                                               |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           |     - If order quantity ≤ shortPosition, submit a Buy Close (4) order.                                                                           |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | **Order Validity:**                                                                                                                              |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 0: Good for the day (default)                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 1: Fill or Kill (FOK)                                                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 2: Fill and Kill (FAK)                                                                                                                         |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | Stop loss/take profit prices are currently not supported and default to 0.                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          +-------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------+
          | Margin Trading / Securities Lending | (Stock Code, Order Time, Order Type, Order Price, Order Quantity, Buy/Sell Flag)                                          | **Order Type:**                                                                                                                                  |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 0: Market order                                                                                                                                |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 5: Limit order                                                                                                                                 |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | **Buy/Sell Flag:**                                                                                                                               |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 1: Collateral purchase                                                                                                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 2: Collateral sale                                                                                                                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 3: Margin purchase                                                                                                                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 4: Short selling                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 5: Direct repayment                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 6: Sell-to-repay                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 7: Direct stock return                                                                                                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 8: Buy-to-return                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          +-------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------+
          | Bond                                | (Symbol, Order Time, Order Type, Clearing Speed, Bid Price, Bid Volume, Ask Price, Ask Volume, Buy/Sell Direction,        | **Buy/Sell Flag:**                                                                                                                               |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     | User Order ID, Channel)                                                                                                   | - 1: Buy Open                                                                                                                                    |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 2: Sell Close                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 3: Two-way quote                                                                                                                               |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | **Order Type:**                                                                                                                                  |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 1: Limit order                                                                                                                                 |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 3: Market-to-cancel order                                                                                                                      |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 4: Market-to-limit order                                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 5: Elastic order                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 7: FAK - execute immediately, cancel unfilled portion                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 8: FOK - execute immediately in full, cancel otherwise                                                                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          +-------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------+
          | Cryptocurrency / Multi-Asset        | (Symbol, Exchange Code, Time, Order Type, Order Price, Stop Loss Price, Take Profit Price, Order Quantity, Buy/Sell       | **Buy/Sell Direction:**                                                                                                                          |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     | Direction, Slippage, Order Validity, Expiration Time)                                                                     | 1: Buy Open; 2: Sell Open; 3: Sell Close; 4: Buy Close                                                                                           |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | **Order Type:**                                                                                                                                  |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 5: Limit order (default)                                                                                                                       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 0: Market order - submitted at limit up/down price, time priority                                                                              |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | **Order Validity:**                                                                                                                              |
          |                                     |                                                                                                                           |                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 0: Good for the day (default)                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 1: Fill or Kill (FOK)                                                                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          |                                     |                                                                                                                           | - 2: Fill and Kill (FAK)                                                                                                                         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
          +-------------------------------------+---------------------------------------------------------------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------+
        
        - For orderType = 5 or 6, the tuple format is: (Symbol, Exchange Code, Time, Order Type, Order Price, Stop Loss Price, 
          Take Profit Price, Order Quantity, Buy/Sell Direction, Slippage, Order Validity, Expiration Time).
          
        - For orderType = 8, the format is:
        
          +------------------+---------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
          | Asset Type       | Format                                                  | Description                                                                                                                                          |
          +==================+=========================================================+======================================================================================================================================================+
          | Futures / Options| (Contract Code, Exchange Code, Time, Order Type,        | **Notes:**                                                                                                                                           |
          |                  | Buy Open/Close Flag, Buy Price, Buy Quantity,           | The fields *bidDifftolerance*, *askDifftolerance*, and *quantityAllowed* are reserved.                                                               |
          |                  | Sell Open/Close Flag, Sell Price, Sell Quantity,        |                                                                                                                                                      |
          |                  | bidDifftolerance, askDifftolerance, quantityAllowed)    | **Buy/Sell Direction:**                                                                                                                              |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 1: Buy open                                                                                                                                          |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 2: Sell open                                                                                                                                         |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 3: Sell close                                                                                                                                        |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 4: Buy close                                                                                                                                         |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 5: Option exercise (only supported in multi-asset backtesting mode; the *underlyingCode* field in the basic information table must be configured)    |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | **Order Type:**                                                                                                                                      |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 0: Market order — submitted at limit up or limit down price, following time priority                                                                 |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 1: Market stop-loss order                                                                                                                            |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 2: Market take-profit order                                                                                                                          |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 3: Limit stop-loss order                                                                                                                             |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 4: Limit take-profit order                                                                                                                           |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 5: Limit order (default)                                                                                                                             |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 6: Cancel order                                                                                                                                      |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | **Order Validity:**                                                                                                                                  |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 0: Good for the day (default)                                                                                                                        |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 1: Fill or kill (FOK) — execute fully immediately or cancel                                                                                          |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | 2: Fill-and-kill (FAK) — execute immediately, cancel any unfilled portion                                                                            |
          |                  |                                                         |                                                                                                                                                      |
          |                  |                                                         | Stop-loss and take-profit prices are currently not supported (default value: 0).                                                                     |
          +------------------+---------------------------------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
        
        """
        return plugin_backtest_submitOrder(self.engine().engine_handle, msg, label, sf_scalar(order_type, type="INT"), _convert_account(account_type))

    @final
    def cancel_order(self, *, symbol=None, orders=None, label=None):
        """Cancel orders.

        Parameters
        ----------
        symbol : _type_, optional
            A STRING scalar, indicating the security code of the orders to be canceled.
            The default value is None.
        orders : _type_, optional
            An INTEGRAL vector, indicating the list of order IDs to be canceled. The default value is None.
        label : _type_, optional
            A STRING scalar, indicating the label or remark associated with the 
            orders to be canceled. The default value is None.
        """
        return plugin_backtest_cancelOrder(self.engine().engine_handle, symbol, orders, label)

    @final
    def get_open_orders(self, symbol=None, orders=None, label=None, output_queue_position: bool = False):
        """Query the information of unfilled orders.
        
        - If symbol is specified, queries unfilled orders for that security.

        - If symbol is empty but orders is specified, queries unfilled orders in the provided orders list.

        - If both symbol and orders are empty, queries unfilled orders specified by label.

        Parameters
        ----------
        symbol : _type_, optional
            A STRING scalar, indicating the security code. The default value is None.
        orders : _type_, optional
            An INTEGRAL vector, indicating a list of order IDs. The default value is None.
        label : _type_, optional
            A STRING scalar, indicating a remark or label. The default value is None.
        output_queue_position : bool, optional
            A BOOL scalar, indicating whether to output detailed information, 
            including openVolumeWithBetterPrice, openVolumeWithWorsePrice, 
            openVolumeAtOrderPrice, priorOpenVolumeAtOrderPrice, and depthWithBetterPrice. 
            Default is false, indicating no detailed output. This parameter is supported only for stocks and futures.

        Returns
        -------
        Dictionary
            Returns a dictionary or table. 
            
            For all asset types except Shanghai Stock Exchange bonds, the table structure is as follows:
            
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | Key                         | Value Type  | Description                                                                                                                              |
            +=============================+=============+==========================================================================================================================================+
            | orderId                     | LONG        | Order ID                                                                                                                                 |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | timestamp                   | TIMESTAMP   | Time                                                                                                                                     |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | symbol                      | STRING      | Symbol code                                                                                                                              |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | price                       | DOUBLE      | Order price                                                                                                                              |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | totalQty                    | LONG        | Total quantity of the order                                                                                                              |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | openQty                     | LONG        | Remaining quantity of the order                                                                                                          |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | direction                   | INT         | 1: Buy open; 2: Sell open; 3: Sell close; 4: Buy close                                                                                   |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | isMacthing                  | INT         | Indicates whether the order has reached the matching time                                                                                |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | openVolumeWithBetterPrice   | LONG        | Total quantity of unfilled orders with better prices (returned only when ``outputQueuePosition = true``)                                 |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | openVolumeWithWorsePrice    | LONG        | Total quantity of unfilled orders with worse prices (returned only when ``outputQueuePosition = true``)                                  |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | openVolumeAtOrderPrice      | LONG        | Total quantity of unfilled orders at the same price (returned only when ``outputQueuePosition = true``)                                  |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | priorOpenVolumeAtOrderPrice | LONG        | Total quantity of unfilled orders at the same price placed earlier (returned only when ``outputQueuePosition = true``)                   |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | depthVolumeWithBetterPrice  | INT         | Depth level of unfilled quotes with better prices (returned only when ``outputQueuePosition = true``)                                    |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+
            | updateTime                  | TIMESTAMP   | Last update time                                                                                                                         |
            +-----------------------------+-------------+------------------------------------------------------------------------------------------------------------------------------------------+

            For Shanghai Stock Exchange bonds, the table structure is as follows:
            
            +----------------+-------------+----------------------------------------------------+
            | Name           | Type        | Description                                        |
            +================+=============+====================================================+
            | orderId        | LONG        | Order ID                                           |
            +----------------+-------------+----------------------------------------------------+
            | time           | TIMESTAMP   | Timestamp                                          |
            +----------------+-------------+----------------------------------------------------+
            | symbol         | STRING      | Security code                                      |
            +----------------+-------------+----------------------------------------------------+
            | bidPrice       | DOUBLE      | Bid price                                          |
            +----------------+-------------+----------------------------------------------------+
            | bidTotalQty    | LONG        | Total bid quantity placed by the user              |
            +----------------+-------------+----------------------------------------------------+
            | bidRemainQty   | LONG        | Remaining bid quantity of the user order           |
            +----------------+-------------+----------------------------------------------------+
            | askPrice       | DOUBLE      | Ask price                                          |
            +----------------+-------------+----------------------------------------------------+
            | askTotalQty    | LONG        | Total ask quantity placed by the user              |
            +----------------+-------------+----------------------------------------------------+
            | askRemainQty   | LONG        | Remaining ask quantity of the user order           |
            +----------------+-------------+----------------------------------------------------+
            | direction      | INT         | Trade direction:                                   |
            |                |             |                                                    |
            |                |             | 1: Buy                                             |
            |                |             |                                                    |
            |                |             | 2: Sell                                            |
            |                |             |                                                    |
            |                |             | 3: Two-way                                         |
            +----------------+-------------+----------------------------------------------------+
            | label          | STRING      | Remarks                                            |
            +----------------+-------------+----------------------------------------------------+

        """
        return plugin_backtest_backtestGetOpenOrders(self.engine().engine_handle, symbol, orders, label, output_queue_position)

    @final
    @property
    def universe(self):
        """Set the symbol pool for the engine.

        """
        return self.engine().universe

    @final
    @universe.setter
    def universe(self, val: List[str]):
        self.engine().universe = val

    @final
    def subscribe_indicator(self, market_data_type: MarketDataType, metrics, account_type: AccountType = AccountType.DEFAULT):
        """Set the market data indicators to subscribe.

        Parameters
        ----------
        market_data_type : MarketDataType
            The type of market data to subscribe to. Optional values:

            - SNAPSHOT: Snapshot

            - TICK: Tick-by-tick order data

            - KLINE / OHLC: K-line data

            - TRADE: Tick-by-tick trade details

            - SNAPSHOT_KLINE / SNAPSHOT_OHLC: Snapshot-based K-line data
        metrics : _type_
            Metaprogramming object, can be generated using ``sf.meta_code``.
        account_type : AccountType, optional
            A STRING scalar, indicating the account type.

        """
        return plugin_backtest_subscribeIndicator(self.engine().engine_handle, market_data_type.value, metrics, _convert_account(account_type))


T = TypeVar("T", bound=StrategyInterface)


class Backtester(BacktesterBase):
    def __init__(self, strategy_cls: Type[T], config: BacktestBasicConfig):
        self.strategy_cls = strategy_cls
        self._config = config
        self._universe = None
        self.engine_handle = None

        self.strategy = self.strategy_cls(self)

        if hasattr(strategy_cls, "context"):
            config_d = self._extract_config(config, strategy_cls.context)
        else:
            config_d = self._extract_config(config)

        callback_d = sf_dictionary(key_type="STRING", val_type="ANY")

        wkptr = weakref.ref(self)

        def real_initialize(context):
            wkptr().engine_handle = context["engine"]
            F_swordfish_udf(getattr(wkptr().strategy, "initialize"))(context)

        callback_d["initialize"] = F_swordfish_udf(real_initialize)
        self._check_valid_callback(callback_d, "beforeTrading", "before_trading")
        self._check_valid_callback(callback_d, "onTick", "on_tick")
        self._check_valid_callback(callback_d, "onSnapshot", "on_snapshot")
        self._check_valid_callback(callback_d, "onBar", "on_bar")
        self._check_valid_callback(callback_d, "onTransaction", "on_transaction")
        self._check_valid_callback(callback_d, "onOrder", "on_order")
        self._check_valid_callback(callback_d, "onTrade", "on_trade")
        self._check_valid_callback(callback_d, "afterTrading", "after_trading")
        self._check_valid_callback(callback_d, "finalize", "finalize")
        on_timer_d = sf_dictionary(key_type="SECOND", val_type="ANY")
        for k in self.strategy_cls._timer_funcs:
            child_method = getattr(self.strategy, k)
            t = self.strategy_cls._timer_funcs[k]
            if isinstance(t, sf_data.Vector):
                for tt in t:
                    on_timer_d[tt] = F_swordfish_udf(child_method)
            else:
                on_timer_d[self.strategy_cls._timer_funcs[k]] = F_swordfish_udf(child_method)
        callback_d["onTimer"] = on_timer_d

        if hasattr(strategy_cls, "callback_d"):
            for k, v in strategy_cls.callback_d.items():
                callback_d[k] = v

        security_reference = self._config.get("security_reference", None)
        engine_name = _generate_name()
        while engine_name in plugin_backtest_getBacktestEngineList():
            engine_name = _generate_name()
        if isinstance(config["cash"], dict):
            self.accounts = {}
            for k in config.cash.keys():
                if isinstance(k, list) or isinstance(k, tuple):
                    for x in k:
                        self.accounts[x] = Account(x, self)
                else:
                    self.accounts[k] = Account(k, self)
        else:
            self.accounts = {
                AccountType.DEFAULT: Account(AccountType.DEFAULT, self)
            }
        self.engine_handle = plugin_backtest_createBacktester(engine_name, config_d, callback_d, False, security_reference)
        self.engine_name = engine_name

    def __del__(self):
        if self.engine_handle is None:
            return
        if not Runtime().check():
            return
        if self.engine_name in plugin_backtest_getBacktestEngineList().keys():
            plugin_backtest_dropBacktestEngine(self.engine_name)
            self.engine_handle = None

    @final
    def _extract_config(self, config: BacktestBasicConfig, context=None):
        config_d = sf_dictionary(key_type="STRING", val_type="ANY")
        config_d["startDate"] = sf_scalar(config["start_date"], type="DATE")
        config_d["endDate"] = sf_scalar(config["end_date"], type="DATE")
        config_d["strategyGroup"] = config["asset_type"].value
        config_d["dataType"] = sf_scalar(config["data_type"].value, type="INT")
        if isinstance(config["cash"], dict):
            cash_d = sf_dictionary(key_type="STRING", val_type="ANY")
            for k, v in config.cash.items():
                if isinstance(k, list) or isinstance(k, tuple):
                    cash_d[", ".join([_.value for _ in k])] = sf_scalar(v, type="DOUBLE")
                else:
                    cash_d[k.value] = sf_scalar(v, type="DOUBLE")
            config_d["cash"] = cash_d
        else:
            config_d["cash"] = sf_scalar(config["cash"], type="DOUBLE")
        if hasattr(config, "matching_mode") and config["matching_mode"] is not None:
            config_d["matchingMode"] = sf_scalar(config["matching_mode"].value, type="INT")
        if hasattr(config, "universe"):
            config_d["universe"] = config["universe"]
        if hasattr(config, "context"):
            if context is not None:
                new_context = sf_dictionary(config["context"], key_type="STRING", val_type="ANY")
                for k, v in new_context.items():
                    context[k] = v
                config_d["context"] = context
            else:
                config_d["context"] = sf_dictionary(config["context"], key_type="STRING", val_type="ANY")
        elif context is not None:
            config_d["context"] = context
        if hasattr(config, "latency"):
            config_d["latency"] = sf_scalar(config["latency"], type="INT")
        if hasattr(config, "benchmark"):
            config_d["benchmark"] = sf_scalar(config["benchmark"], type="STRING")
        if hasattr(config, "data_retention_window"):
            if isinstance(config["data_retention_window"], int):
                config_d["dataRetentionWindow"] = sf_scalar(config["data_retention_window"], type="INT")
            elif isinstance(config["data_retention_window"], str):
                config_d["dataRetentionWindow"] = sf_scalar(config["data_retention_window"], type="STRING")
            else:
                config_d["dataRetentionWindow"] = config["data_retention_window"]
        if hasattr(config, "is_backtest_mode"):
            config_d["isBacktestMode"] = sf_scalar(config["is_backtest_mode"], type="BOOL")
        if hasattr(config, "enable_indicator_optimize"):
            config_d["enableIndicatorOptimize"] = sf_scalar(config["enable_indicator_optimize"], type="BOOL")
        if hasattr(config, "add_time_column_in_indicator"):
            config_d["addTimeColumnInIndicator"] = sf_scalar(config["add_time_column_in_indicator"], type="BOOL")
        if hasattr(config, "orderbook_matching_ratio"):
            config_d["orderBookMatchingRatio"] = sf_scalar(config["orderbook_matching_ratio"], type="DOUBLE")
        if hasattr(config, "matching_ratio"):
            config_d["matchingRatio"] = sf_scalar(config["matching_ratio"], type="DOUBLE")
        if hasattr(config, "output_order_info"):
            config_d["outputOrderInfo"] = sf_scalar(config["output_order_info"], type="BOOL")

        # STOCK config
        if hasattr(config, "set_last_day_position"):
            config_d["setLastDayPosition"] = config["set_last_day_position"]   # Table
        if hasattr(config, "prev_close_price"):
            config_d["prevClosePrice"] = config["prev_close_price"]   # Table
        if hasattr(config, "enable_subscription_to_tick_quotes"):
            config_d["enableSubscriptionToTickQuotes"] = sf_scalar(config["enable_subscription_to_tick_quotes"], type="BOOL")
        if hasattr(config, "commission"):
            config_d["commission"] = sf_scalar(config["commission"], type="DOUBLE")
        if hasattr(config, "tax"):
            config_d["tax"] = sf_scalar(config["tax"], type="DOUBLE")
        if hasattr(config, "output_queue_position"):
            config_d["outputQueuePosition"] = sf_scalar(config["output_queue_position"], type="INT")
        if hasattr(config, "stock_dividend"):
            config_d["stockDividend"] = config["stock_dividend"]   # Table
        if hasattr(config, "frequency"):
            config_d["frequency"] = sf_scalar(config["frequency"], type="INT")
        if hasattr(config, "callback_for_snapshot"):
            config_d["callbackForSnapshot"] = sf_scalar(config["callback_for_snapshot"], type="INT")

        # MARGIN config
        if hasattr(config, "line_of_credit"):
            config_d["lineOfCredit"] = sf_scalar(config["line_of_credit"], type="DOUBLE")
        if hasattr(config, "margin_trading_interest_rate"):
            config_d["marginTradingInterestRate"] = sf_scalar(config["margin_trading_interest_rate"], type="DOUBLE")
        if hasattr(config, "secu_lending_interest_rate"):
            config_d["secuLendingInterestRate"] = sf_scalar(config["secu_lending_interest_rate"], type="DOUBLE")
        if hasattr(config, "maintenance_margin"):
            if isinstance(config, MarginConfig):
                config_d["maintenanceMargin"] = sf_vector(config["maintenance_margin"], type="DOUBLE")
            else:
                config_d["maintenanceMargin"] = sf_scalar(config["maintenance_margin"], type="DOUBLE")
        if hasattr(config, "long_concentration"):
            if config["long_concentration"] is None:
                config_d["longConcentration"] = sf_data.Nothing
            else:
                config_d["longConcentration"] = sf_vector(config["long_concentration"], type="DOUBLE")
        if hasattr(config, "short_concentration"):
            if config["short_concentration"] is None:
                config_d["shortConcentration"] = sf_data.Nothing
            else:
                config_d["shortConcentration"] = sf_vector(config["short_concentration"], type="DOUBLE")
        if hasattr(config, "repay_without_margin_buy"):
            config_d["repayWithoutMarginBuy"] = sf_scalar(config["repay_without_margin_buy"], type="BOOL")
        # set_last_day_position (stock)

        # BOND config

        # OPTION config
        # frequency (stock)
        # callback_for_snapshot (stock)
        # maintenance_margin (margin)

        # FUTURES config
        # frequency (stock)
        if hasattr(config, "futures_type") and config["futures_type"] is not None:
            config_d["futuresType"] = sf_scalar(config["futures_type"], type="STRING")
        if hasattr(config, "enable_algo_order"):
            config_d["enableAlgoOrder"] = sf_scalar(config["enable_algo_order"], type="BOOL")
        # callback_for_snapshot (stock)
        # maintenance_margin (margin)

        # CRYPTO config
        if hasattr(config, "funding_rate"):
            config_d["fundingRate"] = config["funding_rate"]   # Table
        return config_d

    @final
    def append_data(self, data):
        """Insert market data to execute the backtesting strategy.

        Parameters
        ----------
        data : _type_
            A table containing market data.
        """
        plugin_backtest_appendQuotationMsg(self.engine_handle, data)

    @final
    def append_end(self):
        """Insert end marker to indicate the end of market data.
        """
        plugin_backtest_appendEndMarker(self.engine_handle)

    @final
    def _check_valid_callback(self, callback_d, callback_name: str, method_name: str):
        parent_method = getattr(StrategyInterface, method_name, None)
        child_method = getattr(self.strategy_cls, method_name, None)
        if child_method is not parent_method:
            callback_d[callback_name] = F_swordfish_udf(getattr(self.strategy, method_name))

    @final
    @property
    def context_dict(self):
        """Return the logical context.

        """
        return plugin_backtest_getContextDict(self.engine_handle)

    @final
    @property
    def universe(self):
        """Set the symbol pool for the engine.

        """
        return self._universe

    @final
    @universe.setter
    def universe(self, val: List[str]):
        plugin_backtest_setUniverse(self.engine_handle, val)
        self._universe = val

    @final
    @property
    def config(self) -> sf_data.Dictionary:
        return plugin_backtest_getConfig(self.engine_handle)


class AlgoOrderMixin(StrategyBase):

    @final
    def submit_limit_tp_sl_order(
        self,
        code: str,
        exchange: str,
        time: Timestamp,
        order_type: int,
        order_price: float,
        stop_loss_price: float,
        take_profit_price: float,
        quantity: int,
        direct: int,
        slippage: float,
        order_validity: int,
        expiration_time: Timestamp,
        /,
        label: str = "",
        account_type: AccountType = AccountType.DEFAULT,
    ):
        """Submit a take-profit/stop-loss limit algorithmic order.

        Parameters
        ----------
        code : str
            A STRING scalar, indicating the futures code.
        exchange : str
            A STRING scalar, indicating the exchange code.
        time : Timestamp
            A TIMESTAMP scalar, indicating the order timestamp.
        order_type : int
            An INT scalar, indicating the order type:

            - 0: Market order (submitted at limit up/limit-down price, following time-priority rules)
            
            - 1: Stop-loss market order
            
            - 2: Take-profit market order
            
            - 3: Stop-loss limit order
            
            - 4: Take-profit limit order
            
            - 5: Limit order (default)
            
            - 6: Cancel order request
        order_price : float
            A FLOAT scalar indicating the order price.
        stop_loss_price : float
            A FLOAT scalar indicating the stop-loss price.
        take_profit_price : float
            A FLOAT scalar indicating the take-profit price.
        quantity : int
            An INT scalar indicating the order quantity.
        direct : int
            An INT scalar indicating the buy/sell direction.
        slippage : float
            A FLOAT scalar indicating the slippage.
        order_validity : int
            An INT scalar indicating the validity of the order.
        expiration_time : Timestamp
            A TIMESTAMP scalar indicating the order timestamp. 
        label : str, optional
            A STRING scalar used to specify the tag for order categorization.
        account_type : AccountType, optional
            An Enum value indicating the account type:

            - SPOT: Cash account

            - STOCK: Stock account

            - FUTURES: Futures account

            - OPTION: Options account

        """
        return plugin_backtest_submitOrder(
            self.engine().engine_handle,
            [
                code,
                exchange,
                time,
                order_type,
                order_price,
                stop_loss_price,
                take_profit_price,
                quantity,
                direct,
                slippage,
                order_validity,
                expiration_time,
            ],
            label,
            sf_scalar(5, type="INT"),
            _convert_account(account_type),
        )

    @final
    def submit_market_tp_sl_order(
        self,
        code: str,
        exchange: str,
        time: Timestamp,
        order_type: int,
        order_price: float,
        stop_loss_price: float,
        take_profit_price: float,
        quantity: int,
        direct: int,
        slippage: float,
        order_validity: int,
        expiration_time: Timestamp,
        /,
        label: str = "",
        account_type: AccountType = AccountType.DEFAULT,
    ):
        """Submit a take-profit/stop-loss market algorithmic order.

        Parameters
        ----------
        code : str
            A STRING scalar, indicating the futures code.
        exchange : str
            A STRING scalar, indicating the exchange code.
        time : Timestamp
            A TIMESTAMP scalar, indicating the order timestamp.
        order_type : int
            An INT scalar, indicating the order type:

            - 0: Market order (submitted at limit up/limit-down price, following time-priority rules)
            
            - 1: Stop-loss market order
            
            - 2: Take-profit market order
            
            - 3: Stop-loss limit order
            
            - 4: Take-profit limit order
            
            - 5: Limit order (default)
            
            - 6: Cancel order request
        order_price : float
            A FLOAT scalar indicating the order price.
        stop_loss_price : float
            A FLOAT scalar indicating the stop-loss price.
        take_profit_price : float
            A FLOAT scalar indicating the take-profit price.
        quantity : int
            An INT scalar indicating the order quantity.
        direct : int
            An INT scalar indicating the buy/sell direction.
        slippage : float
            A FLOAT scalar indicating the slippage.
        order_validity : int
            An INT scalar indicating the validity of the order.
        expiration_time : Timestamp
            A TIMESTAMP scalar indicating the order timestamp. 
        label : str, optional
            A STRING scalar used to specify the tag for order categorization.
        account_type : AccountType, optional
            An Enum value indicating the account type:

            - SPOT: Cash account

            - STOCK: Stock account

            - FUTURES: Futures account

            - OPTION: Options account

        """
        return plugin_backtest_submitOrder(
            self.engine().engine_handle,
            [
                code,
                exchange,
                time,
                order_type,
                order_price,
                stop_loss_price,
                take_profit_price,
                quantity,
                direct,
                slippage,
                order_validity,
                expiration_time,
            ],
            label,
            sf_scalar(6, type="INT"),
            _convert_account(account_type),
        )

    @final
    def submit_ask_bid_order(
        self,
        code: str,
        exchange: str,
        time: Timestamp,
        order_type: int,
        bid_offset_flag: int,
        bid_price: float,
        bid_qty: int,
        ask_offset_flag: int,
        ask_price: float,
        ask_qty: int,
        bid_difftolerance: float,
        ask_difftolerance: float,
        quantity_allowed: bool,
        /,
        label: str = "",
        account_type: AccountType = AccountType.DEFAULT,
    ):
        """Submit a two sided quote order.

        Parameters
        ----------
        code : str
            A STRING scalar, indicating the futures code.
        exchange : str
            A STRING scalar, indicating the exchange code.
        time : Timestamp
            A TIMESTAMP scalar, indicating the order timestamp.
        order_type : int
            An INT scalar, indicating the order type:

            - 0: Market order (submitted at limit up/limit-down price, following time-priority rules)
            
            - 1: Stop-loss market order
            
            - 2: Take-profit market order
            
            - 3: Stop-loss limit order
            
            - 4: Take-profit limit order
            
            - 5: Limit order (default)
            
            - 6: Cancel order request
        bid_offset_flag : int
            An INT scalar indicating the status of buy action, where 1 represents 
            buy to open and 4 represents buy to close.
        bid_price : float
            A FLOAT scalar indicating the bid price.
        bid_qty : int
            An INT scalar indicating the bid quantity.
        ask_offset_flag : int
            An INT scalar indicating the status of sell action, where 2 represents 
            sell to open and 3 represents sell to close.
        ask_price : float
            A FLOAT scalar indicating the ask price.
        ask_qty : int
            An INT scalar indicating the ask quantity.
        bid_difftolerance : float
            A FLOAT scalar indicating the maximum allowable deviation between 
            the bid price and the reference market price.
        ask_difftolerance : float
            A FLOAT scalar indicating the maximum allowable deviation between 
            the ask price and the reference market price.
        quantity_allowed : bool
            _description_
        label : str, optional
            A STRING scalar used to specify the tag for order categorization.
        account_type : AccountType, optional
            An Enum value representing the account type:

            - SPOT: Cash account

            - STOCK: Stock account

            - FUTURES: Futures account

            - OPTION: Options account

        """
        return plugin_backtest_submitOrder(
            self.engine().engine_handle,
            [
                code,
                exchange,
                time,
                order_type,
                bid_offset_flag,
                bid_price,
                bid_qty,
                ask_offset_flag,
                ask_price,
                ask_qty,
                bid_difftolerance,
                ask_difftolerance,
                quantity_allowed,
            ],
            label,
            sf_scalar(8, type="INT"),
            _convert_account(account_type),
        )

    @final
    def submit_auto_order(
        self,
        code: str,
        exchange: str,
        time: Timestamp,
        order_type: int,
        order_price: float,
        stop_price: float,
        quantity: int,
        direct: int,
        order_validity: int,
        /,
        label: str = None,
        account_type: AccountType = AccountType.DEFAULT,
    ):
        """Submit a auto order.

        Parameters
        ----------
        code : str
            A STRING scalar, indicating the futures code.
        exchange : str
            A STRING scalar, indicating the exchange code.
        time : Timestamp
            A TIMESTAMP scalar, indicating the order timestamp.
        order_type : int
            An INT scalar, indicating the order type:

            - 0: Market order (submitted at limit up/limit-down price, following time-priority rules)
            
            - 1: Stop-loss market order
            
            - 2: Take-profit market order
            
            - 3: Stop-loss limit order
            
            - 4: Take-profit limit order
            
            - 5: Limit order (default)
            
            - 6: Cancel order request
        order_price : float
            A FLOAT scalar indicating the bid or ask price.
        stop_price : float
            A FLOAT scalar indicating the take-profit or stop-loss price.
        quantity : int
            An INT scalar indicating the order quantity.
        direct : int
            An INT scalar indicating the trade side.
        order_validity : int
            An INT scalar indicating the validity of the order.
        label : str, optional
            A STRING scalar used to specify the tag for order categorization.
        account_type : AccountType, optional
            An Enum value representing the account type:

            - SPOT: Cash account

            - STOCK: Stock account

            - FUTURES: Futures account

            - OPTION: Options account
        """
        return plugin_backtest_submitOrder(
            self.engine().engine_handle,
            [
                code,
                exchange,
                time,
                order_type,
                order_price,
                stop_price,
                quantity,
                direct,
                order_validity,
            ],
            _convert_Nothing(label),
            sf_scalar(9, type="INT"),
            _convert_account(account_type),
        )


class StockOrderMixin(StrategyBase):
    @final
    def submit_stock_order(self, code: str, time: Timestamp, order_type: int, order_price: float, quantity: int, direct: int, /, label: str = None, account_type: AccountType = AccountType.DEFAULT):
        """Submit a stock order.

        Parameters
        ----------
        code : str
            A STRING scalar indicating the stock code.
        time : Timestamp
            A TIMESTAMP scalar indicating the order timestamp.
        order_type : int
            An INT scalar indicating the order type. Available values:

            - Shanghai Stock Exchange:

              - 0: best five levels immediate or cancel (IOC).

              - 1: best five levels immediate-or-convert-to-limit.

              - 2: best price on own side.

              - 3: best price on counterparty side.

              - 5: Limit order.

              - 6: Cancel order.

            - Shenzhen Stock Exchange:

              - 0: best five levels immediate or cancel (IOC).

              - 1: immediate or cancel (IOC).

              - 2: best price on own side.

              - 3: best price on counterparty side.

              - 4: fill or kill (FOK).

              - 5: Limit order.

              - 6: Cancel order.
        order_price : float
            A FLOAT scalar indicating the order price.
        quantity : int
            An INT scalar indicating the order quantity.
        direct : int
            An INT scalar indicating the trade direction. Optional values:

            - 1: Buy open

            - 2: Sell open

            - 3: Sell close

            - 4: Buy close
        label : str, optional
            A STRING scalar indicating the tag for categorizing the order.
        account_type : AccountType, optional
            Account type. Optional values:

            - SPOT: Cash account

            - STOCK: Stock account

            - FUTURES: Futures account

            - OPTION: Options account
        """
        return plugin_backtest_submitOrder(self.engine().engine_handle, [code, time, order_type, order_price, quantity, direct], _convert_Nothing(label), sf_scalar(0, type="INT"), _convert_account(account_type))

    @final
    def get_today_pnl(self, symbol: str):
        """This interface is applicable only to stocks and is used to retrieve account profit and loss (P&L).

        Parameters
        ----------
        symbol : str
            A STRING scalar, representing the stock symbol.

        Returns
        -------
        Dictionary
        
            A dictionary with the following structure:
            
            +-----------+------------------------------------------------------------+
            | Key       | Description                                                |
            +===========+============================================================+
            | symbol    | Security code                                              |
            +-----------+------------------------------------------------------------+
            | pnl       | Profit or loss amount of the specified security in the     |
            |           | current account                                            |
            +-----------+------------------------------------------------------------+
            | todayPnl  | Profit or loss amount of the specified security for the    |
            |           | current trading day                                        |
            +-----------+------------------------------------------------------------+
        """
        return plugin_backtest_getTodayPnl(self.engine().engine_handle, symbol)

    @final
    @property
    def stock_total_portfolios(self):
        """Retrieve the current equity metrics of the stock strategy.

        Returns
        -------
        Dictionary
            A dictionary with the following key-value pairs:
            
            - tradeDate: The date
            
            - cash: Available cash
            
            - totalMarketValue: Total market value of the account
            
            - totalEquity: Total equity of the account
            
            - netValue: Net value per unit of the account
            
            - totalReturn: Cumulative return up to the current day
            
            - ratio: Daily return of the account
            
            - pnl: Profit and loss of the account for the current day
        """
        return plugin_backtest_getStockTotalPortfolios(self.engine().engine_handle)


class FuturesOrderMixin(StrategyBase):
    @final
    def submit_futures_order(self, code: str, exchange: str, time: Timestamp, order_type: int, order_price: float, stop_price: float, quantity: int, direct: int, order_validity: int, /, label: str = None, account_type: AccountType = AccountType.DEFAULT):
        """Submits a futures order.

        Parameters
        ----------
        code : str
            A STRING scalar representing the futures symbol.
        exchange : str
            A STRING scalar representing the exchange code.
        time : Timestamp
            A TIMESTAMP scalar indicating the order timestamp.
        order_type : int
            An INT scalar specifying the order type. Possible values are:

            - 0: Market order, submitted at the limit up or limit down price, following the time priority rule.

            - 1: Market stop-loss order.

            - 2: Market take-profit order.

            - 3: Limit stop-loss order.

            - 4: Limit take-profit order.

            - 5: Limit order (default).

        order_price : float
            A FLOAT scalar representing the order price.
        stop_price : float
            A FLOAT scalar representing the stop-loss or take-profit price.
        quantity : int
            An INT scalar representing the order quantity.
        direct : int
            An INT scalar specifying the trade direction. Possible values are:

            - 1: Buy open

            - 2: Sell open

            - 3: Sell close

            - 4: Buy close

            - 5: Option exercise
        order_validity : int
            An INT scalar indicating the order validity type. Possible values are:

            - 0: Good for day (default).

            - 1: Fill or kill (FOK) — execute immediately in full or cancel.

            - 2: Fill and kill (FAK) — execute immediately and cancel any remaining quantity.
        label : str, optional
            A STRING scalar used to tag or categorize the order.
        account_type : AccountType, optional
            The account type. Possible values are:

            - SPOT: Cash account

            - STOCK: Stock account

            - FUTURES: Futures account

            - OPTION: Options account

        """
        return plugin_backtest_submitOrder(self.engine().engine_handle, [code, exchange, time, order_type, order_price, stop_price, quantity, direct, order_validity], _convert_Nothing(label), sf_scalar(0, type="INT"), _convert_account(account_type))

    @final
    @property
    def futures_total_portfolios(self):
        """Query the daily futures profit and loss.
        
        Returns
        -------
        Table
            Return a table with the following structure:
            
            +------------+-----------------------------+
            | Field Name | Description                 |
            +============+=============================+
            | tradeDate  | Date                        |
            +------------+-----------------------------+
            | margin     | Margin Occupied             |
            +------------+-----------------------------+
            | floatingPnl| Floating PnL                |
            +------------+-----------------------------+
            | realizedPnl| Realized Cumulative PnL     |
            +------------+-----------------------------+
            | totalPnl   | Total PnL                   |
            +------------+-----------------------------+
            | cash       | Available Cash              |
            +------------+-----------------------------+
            | totalEquity| Total Equity                |
            +------------+-----------------------------+
            | marginRatio| Margin Occupancy Ratio      |
            +------------+-----------------------------+
            | pnl        | Daily PnL                   |
            +------------+-----------------------------+
            | netValue   | Unit Net Value              |
            +------------+-----------------------------+
            | totalReturn| Cumulative Return as of Date|
            +------------+-----------------------------+
            | ratio      | Daily Return                |
            +------------+-----------------------------+

        """
        return plugin_backtest_getFuturesTotalPortfolios(self.engine().engine_handle)


class OptionOrderMixin(StrategyBase):
    @final
    def submit_option_order(self, code: str, exchange: str, time: Timestamp, order_type: int, order_price: float, stop_price: float, quantity: int, direct: int, order_validity: int, /, label: str = None, account_type: AccountType = AccountType.DEFAULT):
        """Submits an options order.

        Parameters
        ----------
        code : str
            A STRING scalar representing the option symbol.
        exchange : str
            A STRING scalar representing the exchange code.
        time : Timestamp
            A TIMESTAMP scalar indicating the order timestamp.
        order_type : int
            An INT scalar specifying the order type. Possible values are:

            - 0: Market order, submitted at the limit up or limit down price, following the time priority rule.

            - 1: Market stop-loss order.

            - 2: Market take-profit order.

            - 3: Limit stop-loss order.

            - 4: Limit take-profit order.

            - 5: Limit order (default).

            - 6: Cancel order.

            - 9: Auto order mode. In this mode, only directions 1 and 2 are supported:

              - If direct = 1:

                - When the order quantity is greater than the current long position (longPosition), a buy open order is submitted.

                - When the order quantity is less than or equal to longPosition, a sell close (direction = 3) order is submitted.

              - If direct = 2:

                - When the order quantity is greater than the current short position (shortPosition), a sell open order is submitted.

                - When the order quantity is less than or equal to shortPosition, a buy close (direction = 4) order is submitted.
        order_price : float
            A FLOAT scalar representing the order price.
        stop_price : float
            A FLOAT scalar representing the stop-loss or take-profit price.
        quantity : int
            An INT scalar representing the order quantity.
        direct : int
            An INT scalar specifying the trade direction. Possible values are:

            - 1: Buy open

            - 2: Sell open

            - 3: Sell close

            - 4: Buy close

            - 5: Option exercise
        order_validity : int
            An INT scalar indicating the order validity type. Possible values are:

            - 0: Good for day (default).

            - 1: Fill or kill (FOK) — execute immediately in full or cancel.

            - 2: Fill and kill (FAK) — execute immediately and cancel any remaining quantity.
            
            The stop-loss/take-profit price is not currently supported and defaults to 0.
        label : str, optional
            A STRING scalar used to tag or categorize the order.
        account_type : AccountType, optional
            The account type. Possible values are:

            - SPOT: Cash account

            - STOCK: Stock account

            - FUTURES: Futures account

            - OPTION: Options account

        """
        return plugin_backtest_submitOrder(self.engine().engine_handle, [code, exchange, time, order_type, order_price, stop_price, quantity, direct, order_validity], _convert_Nothing(label), sf_scalar(0, type="INT"), _convert_account(account_type))

    @final
    @property
    def option_total_portfolios(self):
        """Query daily option PnL

        Returns
        -------
        Table
            Return a table with the following structure:
            
            +----------------+--------------------------------------+
            | Field Name     | Description                          |
            +================+======================================+
            | tradeDate      | Date                                 |
            +----------------+--------------------------------------+
            | margin         | Margin occupied                      |
            +----------------+--------------------------------------+
            | floatingPnl    | Floating PnL                         |
            +----------------+--------------------------------------+
            | realizedPnl    | Realized cumulative PnL              |
            +----------------+--------------------------------------+
            | totalPnl       | Total cumulative PnL                 |
            +----------------+--------------------------------------+
            | cash           | Available cash                       |
            +----------------+--------------------------------------+
            | totalEquity    | Total account equity                 |
            +----------------+--------------------------------------+
            | marginRatio    | Margin ratio                         |
            +----------------+--------------------------------------+
            | pnl            | Daily PnL                            |
            +----------------+--------------------------------------+
            | netValue       | Account unit net value               |
            +----------------+--------------------------------------+
            | totalReturn    | Cumulative return up to the day      |
            +----------------+--------------------------------------+
            | ratio          | Daily return                         |
            +----------------+--------------------------------------+

        """
        return plugin_backtest_getOptionTotalPortfolios(self.engine().engine_handle)


class MarginOrderMixin(StrategyBase):
    @final
    def submit_margin_order(self, code: str, time: Timestamp, order_type: int, order_price: float, quantity: int, direct: int, /, label: str = None, account_type: AccountType = AccountType.DEFAULT):
        """Submit a margin trading order.

        Parameters
        ----------
        code : str
            A STRING scalar indicating the stock symbol.
        time : Timestamp
            A TIMESTAMP scalar indicating the timestamp of the order.
        order_type : int
            An INT scalar indicating the order type. Available values include:
            
            - 0: Market order
            
            - 5: Limit order
        order_price : float
            A FLOAT scalar indicating the order price.
        quantity : int
            An INT scalar indicating the order quantity.
        direct : int
            An INT scalar indicating the trade direction. Available values include:
            
            - 1: Collateral purchase
            
            - 2: Collateral sale
            
            - 3: Margin purchase
            
            - 4: Short sale
            
            - 5: Direct repayment
            
            - 6: Sell for repayment
            
            - 7: Direct return of borrowed shares
            
            - 8: Buy for return of borrowed shares
        label : str, optional
            A STRING scalar indicating the label assigned to the order for classification.
        account_type : AccountType, optional
            The account type. Available values include:
            
            - SPOT: Cash account
            
            - STOCK: Stock account
            
            - FUTURES: Futures account
            
            - OPTION: Options account
        """
        return plugin_backtest_submitOrder(self.engine().engine_handle, [code, time, order_type, order_price, quantity, direct], _convert_Nothing(label), sf_scalar(0, type="INT"), _convert_account(account_type))

    @final
    def get_margin_secu_position(self, symbols: List[str] = None):
        """Query the collateral purchase position information.        
        

        Parameters
        ----------
        symbols : List[str], optional
            A STRING vector indicating the list of stock symbols. If omitted, 
            the function returns all collateral purchase positions.

        Returns
        -------
        Dictionary or Table
            - When the length of symbolList is 1, the function returns a dictionary.

            - When the length of symbolList is not 1, an error is raised.

            - When symbolList is omitted, the function returns a table.            
                         
            The returned table's structure is as follows:
            
            +---------------------+------------------------------------------------------------+
            | Name                | Description                                                |
            +=====================+============================================================+
            | symbol              | Stock symbol.                                              |
            +---------------------+------------------------------------------------------------+
            | lastDayLongPosition | Collateral purchase position quantity at the previous      |
            |                     | day's close.                                               |
            +---------------------+------------------------------------------------------------+
            | lastDayBuyValue     | Collateral purchase value at the previous day's close.     |
            +---------------------+------------------------------------------------------------+
            | longPosition        | Current collateral purchase position quantity.             |
            +---------------------+------------------------------------------------------------+
            | buyValue            | Current collateral purchase value.                         |
            +---------------------+------------------------------------------------------------+
            | todayBuyVolume      | Collateral purchase traded quantity for the current day.   |
            +---------------------+------------------------------------------------------------+
            | todayBuyValue       | Collateral purchase traded value for the current day.      |
            +---------------------+------------------------------------------------------------+
        
        """
        return plugin_backtest_getMarginSecuPosition(self.engine().engine_handle, _convert_Nothing(symbols))

    @final
    def get_margin_trading_position(self, symbols: List[str] = None):
        """Queries margin purchase position information.

        Parameters
        ----------
        symbols : List[str], optional
            A STRING vector indicating the list of stock symbols. If omitted, 
            the function returns margin purchase positions for all stocks.

        Returns
        -------
        Dictionary or Table
            - When symbolList contains only one symbol, a dictionary is returned.

            - When symbolList contains more than one symbol, an error is raised.

            - When symbolList is omitted, a table is returned. 
                         
            The returned table's structure is as follows:
            
            +--------------------+----------------+-----------------------------------------------+
            | Field              | Type           | Description                                   |
            +====================+================+===============================================+
            | symbol             | STRING         | Stock symbol                                  |
            +--------------------+----------------+-----------------------------------------------+
            | lastDayLongPosition| DECIMAL128(8)  | Margin purchase position at previous day's    |
            |                    |                | close                                         |
            +--------------------+----------------+-----------------------------------------------+
            | lastDayBuyValue    | DECIMAL128(8)  | Margin purchase amount at previous day's      |
            |                    |                | close                                         |
            +--------------------+----------------+-----------------------------------------------+
            | lastDayMarginDebt  | DECIMAL128(8)  | Margin debt at previous day's close           |
            +--------------------+----------------+-----------------------------------------------+
            | longPosition       | DECIMAL128(8)  | Current margin purchase position              |
            +--------------------+----------------+-----------------------------------------------+
            | buyValue           | DECIMAL128(8)  | Current margin purchase amount                |
            +--------------------+----------------+-----------------------------------------------+
            | todayBuyVolume     | DECIMAL128(8)  | Margin purchase traded volume today           |
            +--------------------+----------------+-----------------------------------------------+
            | todayBuyValue      | DECIMAL128(8)  | Margin purchase traded amount today           |
            +--------------------+----------------+-----------------------------------------------+
            | marginBuyProfit    | DECIMAL128(8)  | Profit or loss of margin purchase             |
            +--------------------+----------------+-----------------------------------------------+
            | financialFee       | DECIMAL128(8)  | Financing interest                            |
            +--------------------+----------------+-----------------------------------------------+
  
        """
        return plugin_backtest_getMarginTradingPosition(self.engine().engine_handle, _convert_Nothing(symbols))

    @final
    def get_secu_lending_position(self, symbols: List[str] = None):
        """Query short sale positions.

        Parameters
        ----------
        symbols : List[str], optional
            A STRING vector indicating a list of stock symbols. If omitted, all 
            short-sale positions will be returned by default.

        Returns
        -------
        Dictionary or Table
            - When the length of symbolList is 1, a dictionary is returned.

            - When the length of symbolList is not 1, an error is raised.

            - If symbolList is omitted, a table is returned.          
                             
            The returned table's structure is as follows:
            
            +------------------------+----------------------------+
            | Name                   | Description                |
            +========================+============================+
            | symbol                 | The underlying stock symbol|
            +------------------------+----------------------------+
            | lastDayShortPosition   | Short-sale position at     |
            |                        | previous close             |
            +------------------------+----------------------------+
            | lastDayShortValue      | Short-sale value at        |
            |                        | previous close             |
            +------------------------+----------------------------+
            | lastDaySecuLendingDebt | Short-sale debt at         |
            |                        | previous close             |
            +------------------------+----------------------------+
            | shortPosition          | Current short-sale position|
            +------------------------+----------------------------+
            | shortValue             | Current short-sale value   |
            +------------------------+----------------------------+
            | todayShortVolume       | Executed short-sale volume |
            |                        | for the day                |
            +------------------------+----------------------------+
            | todayShortValue        | Executed short-sale value  |
            |                        | for the day                |
            +------------------------+----------------------------+
            | secuLendingProfit      | Profit or loss from short  |
            |                        | selling                    |
            +------------------------+----------------------------+
            | secuLendingFee         | Fees for short selling     |
            +------------------------+----------------------------+
           
        """
        return plugin_backtest_getSecuLendingPosition(self.engine().engine_handle, _convert_Nothing(symbols))


class BondOrderMixin(StrategyBase):
    @final
    def submit_bond_order(self, code: str, time: Timestamp, order_type: int, settlement_speed: int, bid_price: float, bid_quantity: int, ask_price: float, ask_quantity: int, direct: int, order_id: int, channel: str, /, label: str = None, account_type: AccountType = AccountType.DEFAULT):
        """Submit a bond order.

        Parameters
        ----------
        code : str
            A STRING scalar representing the option symbol.
        time : Timestamp
            A TIMESTAMP scalar indicating the order timestamp.
        order_type : int
            An INT scalar specifying the order type. Possible values are:

            - 0: A Market order.

            - 9: For automated orders, the buy/sell direction can only be set to 1 or 2.
        settlement_speed : int
            An INT scalar indiacting the settlement speed.
        bid_price : float
            A FLOAT scalar indicating buy order price.
        bid_quantity : int
            An INT scalar indicating the buy order quantity.
        ask_price : float
            A FLOAT scalar indicating sell order price.
        ask_quantity : int
            An INT scalar indicating the sell order quantity.
        direct : int
            An INT scalar indicating the order direction.
        order_id : int
            An INT scalar indicating the order id.
        channel : str
            A STRING scalar indicating the channel number.
        label : str, optional
            A STRING scalar indicating the label assigned to the order for classification.
        account_type : AccountType, optional
            The account type. Available values include:

            - SPOT: Cash account

            - STOCK: Stock account

            - FUTURES: Futures account

            - OPTION: Options account

        """
        return plugin_backtest_submitOrder(self.engine().engine_handle, [code, time, order_type, settlement_speed, bid_price, bid_quantity, ask_price, ask_quantity, direct, order_id, channel], _convert_Nothing(label), sf_scalar(0, type="INT"), _convert_account(account_type))

    @final
    def update_position(self, symbol: str, quantity: int, price: float = None):
        """Update positions and return the order ID. This interface can only be called in simulated trading mode.

        Parameters
        ----------
        symbol : str
            A STRING scalar, indicating the instrument.
        quantity : int
            An INT scalar, positive to increase position, negative to decrease position.
        price : float, optional
            A DOUBLE scalar, indicating the trade price. If set to 0 or left empty, the latest market price is used.

        """
        return plugin_backtest_updatePosition(self.engine().engine_handle, symbol, quantity, _convert_Nothing(price))


class CryptoOrderMixin(StrategyBase):
    @final
    def submit_crypto_order(self, code: str, exchange: str, time: Timestamp, order_type: int, order_price: float, stop_loss_price: float, take_profit_price: float, quantity: int, direct: int, slippage: float, order_validity: int, expiration_time: Timestamp, /, label: str = None, account_type: AccountType = AccountType.DEFAULT):
        """Submit an cryptocurrency order.

        Parameters
        ----------
        code : str
            A STRING scalar, representing the crypto code.
        exchange : str
            A STRING scalar, representing the exchange code.
        time : Timestamp
            A TIMESTAMP scalar, representing the order timestamp.
        order_type : int
            An INT scalar, representing the order type:

            - 5: Limit order (default).

            - 0: Market order, submitted at daily price limits, following time-priority rules.
        order_price : float
            A FLOAT scalar, representing the order price.
        stop_loss_price : float
            A FLOAT scalar, representing the stop-loss price.
        take_profit_price : float
            A FLOAT scalar, representing the take-profit price.
        quantity : int
            An INT scalar, representing the order quantity.
        direct : int
            An INT scalar, representing the buy/sell direction:

            - 1: Buy open

            - 2: Sell open

            - 3: Sell close

            - 4: Buy close
        slippage : float
            FLOAT, representing slippage.
        order_validity : int
            An INT scalar, representing order validity:

            - 0: Valid for the day (default)

            - 1: Immediate full execution or cancel (FOK)

            - 2: Immediate partial execution, remaining canceled (FAK)
        expiration_time : Timestamp
            A TIMESTAMP scalar, representing the order expiration time.
        label : str, optional
            A STRING scalar, a tag for categorizing the order.
        account_type : AccountType, optional
            An Enum value representing the account type:

            - SPOT: Cash account

            - STOCK: Stock account

            - FUTURES: Futures account

            - OPTION: Options account

        """
        return plugin_backtest_submitOrder(self.engine().engine_handle, [code, exchange, time, order_type, order_price, stop_loss_price, take_profit_price, quantity, direct, slippage, order_validity, expiration_time], _convert_Nothing(label), sf_scalar(0, type="INT"), _convert_account(account_type))


class TraditionalBacktester(BacktesterBase):
    def __init__(self, engine_name: sf_data.String, strategy_cls: Type[T], config: sf_data.Dictionary, security_reference: sf_data.Table = None):
        self.strategy_cls = strategy_cls
        self._config = config
        self._universe = None
        self.engine_handle = None

        self.strategy = self.strategy_cls(self)

        context = sf_dictionary(key_type="STRING", val_type="ANY")
        if "context" in self._config:
            for k, v in self._config["context"].items():
                context[k] = v
        if hasattr(strategy_cls, "context"):
            for k, v in strategy_cls.context.items():
                context[k] = v
        config["context"] = context

        callback_d = sf_dictionary(key_type="STRING", val_type="ANY")

        wkptr = weakref.ref(self)

        def real_initialize(context):
            wkptr().engine_handle = context["engine"]
            F_swordfish_udf(getattr(wkptr().strategy, "initialize"))(context)

        callback_d["initialize"] = F_swordfish_udf(real_initialize)
        self._check_valid_callback(callback_d, "beforeTrading", "before_trading")
        self._check_valid_callback(callback_d, "onTick", "on_tick")
        self._check_valid_callback(callback_d, "onSnapshot", "on_snapshot")
        self._check_valid_callback(callback_d, "onBar", "on_bar")
        self._check_valid_callback(callback_d, "onTransaction", "on_transaction")
        self._check_valid_callback(callback_d, "onOrder", "on_order")
        self._check_valid_callback(callback_d, "onTrade", "on_trade")
        self._check_valid_callback(callback_d, "afterTrading", "after_trading")
        self._check_valid_callback(callback_d, "finalize", "finalize")
        on_timer_d = sf_dictionary(key_type="SECOND", val_type="ANY")
        for k in self.strategy_cls._timer_funcs:
            child_method = getattr(self.strategy, k)
            on_timer_d[self.strategy_cls._timer_funcs[k]] = F_swordfish_udf(child_method)
        callback_d["onTimer"] = on_timer_d

        if hasattr(strategy_cls, "callback_d"):
            for k, v in strategy_cls.callback_d.items():
                callback_d[k] = v

        self.engine_handle = plugin_backtest_createBacktester(engine_name, config, callback_d, False, _convert_Nothing(security_reference))
        self.engine_name = engine_name

        if isinstance(config["cash"], sf_data.Dictionary):
            self.accounts = {}
            for k in config["cash"].keys():
                keys = [_.strip() for _ in str(k).split(",")]
                for key in keys:
                    self.accounts[AccountType(key)] = Account(AccountType(key), self.engine_handle)
        else:
            self.accounts = {
                AccountType.DEFAULT: Account(AccountType.DEFAULT, self.engine_handle)
            }

    def __del__(self):
        if self.engine_handle is None:
            return
        if not Runtime().check():
            return
        if self.engine_name in plugin_backtest_getBacktestEngineList().keys():
            plugin_backtest_dropBacktestEngine(self.engine_name)
            self.engine_handle = None

    @final
    def append_data(self, data):
        """Insert market data to execute a strategy backtest.

        Parameters
        ----------
        data : _type_
            A table containing market data as input.
        """
        plugin_backtest_appendQuotationMsg(self.engine_handle, data)

    @final
    def append_end(self):
        """Insert end marker to indicate the end of market data.
        """
        plugin_backtest_appendEndMarker(self.engine_handle)

    @final
    def _check_valid_callback(self, callback_d, callback_name: str, method_name: str):
        parent_method = getattr(StrategyInterface, method_name, None)
        child_method = getattr(self.strategy_cls, method_name, None)
        if child_method is not parent_method:
            callback_d[callback_name] = F_swordfish_udf(getattr(self.strategy, method_name))

    @final
    @property
    def context_dict(self): 
        """Return the logical context.

        """
        return plugin_backtest_getContextDict(self.engine_handle)

    @final
    @property
    def universe(self):
        """Set the symbol pool for the engine.

        """
        return self._universe

    @final
    @universe.setter
    def universe(self, val: List[str]):
        plugin_backtest_setUniverse(self.engine_handle, val)
        self._universe = val

    @final
    @property
    def config(self) -> sf_data.Dictionary:
        return plugin_backtest_getConfig(self.engine_handle)
