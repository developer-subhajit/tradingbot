import datetime
import json
from pathlib import Path
import pandas as pd
import concurrent.futures
import instances
import utils


class MomentumSwing:
    def __init__(
        self,
        cash: int | float,
        benchmark_index: str,
        portfolio_size: int,
        threshold: float = 0.25,
        path: Path = None,
    ):
        self.cash = cash
        self.index = benchmark_index
        self.portfolio_size = portfolio_size
        self.threshold = threshold
        self.path = path or Path.cwd()

        self.log_dir = self._join_path("log")
        self.data_dir = self._join_path("data")

        self._initiate

    def _join_path(self, directory: Path) -> Path:
        new_path = Path.joinpath(self.path, directory)
        Path.mkdir(new_path, exist_ok=True)
        return new_path

    @property
    def _initiate(self):
        self.telegramBot, self.FyersClient = instances.get_instance(self.log_dir)

    def getSymbols(self, index: str) -> list:
        # common headers
        headers = {"User-Agent": "Mozilla/5.0"}

        # import stock list from nse website
        with open("SectorMap.json", "r") as json_file:
            filenames = json.load(json_file)

        filename = filenames.get(index.lower())
        stock_details = utils.read_url(
            url=f"https://www.niftyindices.com/IndexConstituent/{filename}",
            headers=headers,
        )

        # import symbol details from Fyers website
        symbol_details = utils.read_url(
            url="https://public.fyers.in/sym_details/NSE_CM.csv",
            headers=headers,
            columns=(
                "Fytoken",
                "Symbol Details",
                "Exchange Instrument type",
                "Minimum lot size",
                "Tick size",
                "ISIN",
                "Trading Session",
                "Last update date",
                "Expiry date",
                "Symbol",
                "Exchange",
                "Segment",
                "Scrip code",
                "Underlying scrip code",
                "Strike price",
                "Option type",
                "Underlying FyToken",
                "Fytoken1",
                "NA",
            ),
        )

        #  filters for specific scrip codes
        return symbol_details[
            symbol_details.ISIN.isin(stock_details["ISIN Code"].to_list())
        ].Symbol.to_list()

    @property
    def import_historical_data(self):
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
        #  import symbols
        symbols = self.getSymbols(index=self.index)

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
            if stock_data := hist_data(symbol):
                if stock_data.date.dt.date.max() != datetime.datetime.now().date():
                    temp_data = {
                        "symbol": symbol,
                        "range_from": stock_data.date.dt.date.max()
                        + datetime.timedelta(days=1),
                    }
                    input_data.append(
                        {
                            data | temp_data,
                        }
                    )
            else:
                print(f"No stock data available for {symbol}")
                input_data.append(
                    {
                        **data,
                        **{
                            "symbol": symbol,
                            "range_from": datetime.date(2010, 1, 1),
                        },
                    }
                )

        updated_data = [self.FyersClient.history_daily(data) for data in input_data]


if __name__ == "__main__":
    ms = MomentumSwing(cash=30000, benchmark_index="nifty next 50", portfolio_size=5)
    print(ms.update_historical_data())


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
