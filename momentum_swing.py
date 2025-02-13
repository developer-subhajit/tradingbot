"""
Momentum Swing Trading Strategy Implementation

This module implements a momentum-based swing trading strategy for stocks listed in specified indices.
The strategy calculates momentum based on weekly returns over a 12-week period and ranks stocks
based on their momentum scores. Trading decisions are made based on momentum thresholds and
portfolio management rules.

Author: Your Name
License: MIT
"""

import datetime
import json
from pathlib import Path
import pandas as pd
import concurrent.futures
import instances
import utils


class MomentumSwing:
    """
    A class implementing momentum-based swing trading strategy.
    
    The strategy:
    1. Fetches historical data for stocks in the specified index
    2. Calculates weekly returns and momentum indicators
    3. Ranks stocks based on momentum
    4. Makes trading decisions based on momentum thresholds
    5. Manages portfolio according to specified parameters
    
    Attributes:
        cash (float): Initial investment amount
        index (str): Benchmark index to trade (e.g., "nifty next 50")
        portfolio_size (int): Number of stocks to hold in portfolio
        threshold (float): Momentum threshold for trading decisions
        path (Path): Root directory for data and logs
    """

    def __init__(
        self,
        cash: int | float,
        benchmark_index: str,
        portfolio_size: int,
        threshold: float = 0.25,
        path: Path = None,
    ):
        """
        Initialize the MomentumSwing trading strategy.

        Args:
            cash: Initial investment amount
            benchmark_index: Index to trade (e.g., "nifty next 50")
            portfolio_size: Number of stocks to hold in portfolio
            threshold: Momentum threshold for trading decisions (default: 0.25)
            path: Root directory for data and logs (default: current directory)
        """
        self.cash = cash
        self.index = benchmark_index
        self.portfolio_size = portfolio_size
        self.threshold = threshold
        self.path = path or Path.cwd()

        self.log_dir = self._join_path("log")
        self.data_dir = self._join_path("data")

        self._initiate

    def _join_path(self, directory: Path) -> Path:
        """Create and return a subdirectory path."""
        new_path = Path.joinpath(self.path, directory)
        Path.mkdir(new_path, exist_ok=True)
        return new_path

    @property
    def _initiate(self):
        """Initialize Telegram bot and Fyers client instances."""
        self.telegramBot, self.FyersClient = instances.get_instance(self.log_dir)

    def getSymbols(self) -> list:
        """
        Fetch list of stock symbols from the specified index.
        
        Returns:
            list: List of stock symbols in the index
        """
        # common headers
        headers = {"User-Agent": "Mozilla/5.0"}

        # import stock list from nse website
        with open("SectorMap.json", "r") as json_file:
            filenames = json.load(json_file)

        filename = filenames.get(self.index.lower())
        stock_details = utils.read_url(
            url=f"https://www.niftyindices.com/IndexConstituent/{filename}",
            headers=headers,
        )

        # import symbol details from Fyers website
        symbol_details = utils.read_url(
            url="https://public.fyers.in/sym_details/NSE_CM.csv",
            headers=headers,
            columns=(
                "Fytoken", "Symbol Details", "Exchange Instrument type",
                "Minimum lot size", "Tick size", "ISIN", "Trading Session",
                "Last update date", "Expiry date", "Symbol", "Exchange",
                "Segment", "Scrip code", "Underlying scrip code",
                "Strike price", "Option type", "Underlying FyToken",
                "Fytoken1", "NA",
            ),
        )

        #  filters for specific scrip codes
        return symbol_details[
            symbol_details.ISIN.isin(stock_details["ISIN Code"].to_list())
        ].Symbol.to_list()

    @property
    def import_historical_data(self):
        """
        Import historical price data from parquet file.
        
        Returns:
            tuple: (file path, historical data DataFrame)
        """
        fpath = Path.joinpath(self.data_dir, "ohlc_data.parquet.gzip")
        try:
            historical_data = pd.read_parquet(fpath)
        except FileNotFoundError as e:
            print("File not found...")
            historical_data = pd.DataFrame()
        except Exception as e:
            raise e
        return fpath, historical_data

    def update_historical_data(self):
        """
        Update historical price data for all symbols in the index.
        
        Returns:
            DataFrame: Updated historical price data
        """
        #  import symbols
        symbols = self.getSymbols()

        # import stored historical data
        fpath, historical_data = self.import_historical_data

        # import recent data
        data = {
            "resolution": "D",
            "range_to": datetime.datetime.now().date(),
        }

        hist_data = lambda symbol: historical_data[
            historical_data["symbol"] == symbol
        ].copy()
        
        input_data = []
        for symbol in symbols:
            stock_data = hist_data(symbol)
            if len(stock_data):
                if stock_data.date.dt.date.max() != datetime.datetime.now().date():
                    temp_data = {
                        "symbol": symbol,
                        "range_from": stock_data.date.dt.date.max()
                        + datetime.timedelta(days=1),
                    }
                else:
                    temp_data = {
                        "symbol": symbol,
                        "range_from": datetime.datetime.now().date(),
                    }
            else:
                print(f"No stock data available for {symbol}")
                temp_data = {
                    "symbol": symbol,
                    "range_from": datetime.date(2010, 1, 1),
                }
            input_data.append(data | temp_data)

        updated_data = [self.FyersClient.history_daily(data) for data in input_data]
        #  update the historical data file with recent data
        historical_data = pd.concat([historical_data, *updated_data])
        historical_data.to_parquet(fpath, compression="gzip", index=None)
        return historical_data

    def get_momentum(self, historical_data, symbol):
        """
        Calculate momentum indicator for a given symbol.
        
        The momentum is calculated as the 12-week rolling product of weekly returns.
        
        Args:
            historical_data: DataFrame containing historical price data
            symbol: Stock symbol to calculate momentum for
            
        Returns:
            DataFrame: Historical data with momentum indicator
        """
        symbolData = historical_data[historical_data.symbol == symbol].copy()
        symbolData["date"] = pd.to_datetime(symbolData["date"], format="%Y-%m-%d")
        symbolData.set_index("date", inplace=True)
        symbolData.sort_index(inplace=True)
        weekly_returns = symbolData.resample("W-FRI")["close"].last().pct_change()
        short_term_returns = (
            weekly_returns.rolling(window=12)
            .apply(lambda x: (x + 1).prod() - 1)
            .round(5)
        )
        symbolData["momentum"] = short_term_returns
        return symbolData


if __name__ == "__main__":
    # Example usage
    ms = MomentumSwing(
        cash=30000,
        benchmark_index="nifty next 50",
        portfolio_size=5
    )
    historical_data = ms.update_historical_data()
    print("Historical data updated successfully")


"""
# set root directory, log directory and data directory
root = Path.cwd()

log_dir = Path.joinpath(root, "log")
Path.mkdir(log_dir, exist_ok=True)

data_dir = Path.joinpath(root, "data")
Path.mkdir(data_dir, exist_ok=True)

# import telegram bot and Fyers API  client
telegramBot, FyersClient = instances.get_instance(log_dir)

symbols = getSymbols(index="Nifty Next 50")
print(symbols)

#  import previously stored historical data
fpath = Path.joinpath(data_dir, "ohlc_data.parquet.gzip")
try:
    historical_data = pd.read_parquet(fpath)
except FileNotFoundError as e:
    print("File not found...")
    historical_data = pd.DataFrame()
except Exception as e:
    raise e

# update historical data file with recent data

data = {"resolution": "D", "range_to": datetime.datetime.now().date()}

input_data = []
for symbol in symbols:
    stock_data = historical_data[historical_data["symbol"] == symbol].copy()
    if len(stock_data) > 0:
        if stock_data.date.dt.date.max() != datetime.datetime.now().date():
            input_data.append(
                {
                    **data,
                    **{
                        "symbol": symbol,
                        "range_from": stock_data.date.dt.date.max()
                        + datetime.timedelta(days=1),
                    },
                }
            )
    else:
        print(f"No stock data available for {symbol}")
        input_data.append(
            {**data, **{"symbol": symbol, "range_from": datetime.date(2010, 1, 1)}}
        )

updated_data = [FyersClient.history_daily(data) for data in input_data]

#  update the historical data file with recent data
historical_data = pd.concat([historical_data, *updated_data])
historical_data.to_parquet(fpath, compression="gzip", index=None)

print(historical_data.symbol.nunique())

# momentum calculation


def get_momentum(symbol):
    symbolData = historical_data[historical_data.symbol == symbol].copy()
    symbolData["date"] = pd.to_datetime(symbolData["date"], format="%Y-%m-%d")
    symbolData.set_index("date", inplace=True)
    symbolData.sort_index(inplace=True)
    weekly_returns = symbolData.resample("W-FRI")["close"].last().pct_change()
    short_term_returns = (
        weekly_returns.rolling(window=12)
        .apply(lambda x: (x + 1).prod() - 1)
        .round(5)
    )
    symbolData["momentum"] = short_term_returns
    return symbolData


with concurrent.futures.ThreadPoolExecutor(5) as executor:
    responses = list(executor.map(get_momentum, symbols))

momentumData = pd.concat(responses)
momentumData = momentumData.reset_index()

# momentum Ranking
data = momentumData.dropna(subset="momentum").sort_values(by="date")

last_frame = data.groupby("symbol").tail(1)
print(len(symbols), len(last_frame))
last_frame["rank"] = (
    last_frame["momentum"].copy().rank(ascending=False, method="min")
)
last_frame = last_frame.sort_values(by="rank")
my_dict = last_frame.set_index("symbol").to_dict(orient="index")


print(json.dumps(my_dict, indent=4, default=str))

# Holding information
holding_fname = Path.joinpath(
    data_dir, f"{data.date.unique()[-2].strftime('%Y-%m-%d')}_holdings.json"
)

cash = 6000
try:
    with open(holding_fname, "r") as json_file:
        holdings = json.load(json_file)
except FileNotFoundError:
    print(
        "Could not find previous holdings information .... \n Placing fresh orders"
    )
    order_inputs = {
        "type": 1,
        "side": 1,
        "productType": "CNC",
        "stopPrice": 0,
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": False,
        "stopLoss": 0,
        "takeProfit": 0,
    }

    order_queue = [
        {
            **order_inputs,
            **{
                "symbol": symbol,
                "qty": int(cash // values.get("close")),
                "limitPrice": values.get("close"),
            },
        }
        for symbol, values in my_dict.items()
        if values.get("rank") <= 5
    ]
    print(json.dumps(order_queue, default=str, indent=4))
    # print(FyersClient.place_basket_orders(json.dumps(order_queue, default=str)))
"""
