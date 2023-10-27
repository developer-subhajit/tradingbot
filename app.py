import datetime  # required for datetime
from pathlib import Path  # required for handling paths
import dill  # required ford pickling


import instances # required to load telegram instance and Fyers instance
import json

if __name__ == "__main__":
    # set root/ parent directories
    root = Path.cwd()

    # create a log directory
    logdir = Path.joinpath(root, "log")
    Path.mkdir(logdir, exist_ok=True)

    telegramBot, Fyers = instances.get_instance(logdir)

    print(dir(Fyers))
    print(Fyers.access_token)
    print(json.dumps(Fyers.get_profile(), indent=4, default=str))
    print(json.dumps(Fyers.tradebook(), indent=4, default=str))
    print(json.dumps(Fyers.funds(), indent=4, default=str))
    print(json.dumps(Fyers.holdings(), indent=4, default=str))
    print(json.dumps(Fyers.orderbook(), indent=4, default=str))
    print(json.dumps(Fyers.positions(), indent=4, default=str))