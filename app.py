import json
from pathlib import Path  # required for handling paths
import instances  # required to load telegram instance and Fyers instance

if __name__ == "__main__":
    # set root/ parent directories
    root = Path.cwd()

    # create a log directory
    logdir = Path.joinpath(root, "log")
    Path.mkdir(logdir, exist_ok=True)

    telegramBot, Fyers = instances.get_instance(logdir)
    json_str = lambda x: json.dumps(x, indent=4, default=str)
    print(json_str(Fyers.holdings))
