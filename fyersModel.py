from fyers_apiv3 import fyersModel
from utils import RestClient
from pathlib import Path

# initiate async rest client
client = RestClient()


class SessionModel(fyersModel.SessionModel):
    pass


class Config(fyersModel.Config):
    pass


class FyersModel:
    def __init__(self, client_id: str, token: str):
        """
        Initializes an instance of FyersModelv3.

        Args:
            client_id: The client ID for API authentication.
            token: The token for API authentication.

        """
        self.client_id = client_id
        self.access_token = token
        self.header = "{}:{}".format(self.client_id, self.access_token)
        self.content = "application/json"
        self.headers = {
            "Authorization": self.header,
            "Content-Type": self.content,
            "version": "3",
        }

    @client.request
    def get_profile(self) -> dict:
        """
        Retrieves the user profile information.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "GET",
            "headers": self.headers,
            "url": f"{Config.API}{Config.get_profile}",
            "params": None,
        }

    @client.request
    def tradebook(self) -> dict:
        """
        Retrieves daily trade details of the day.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "GET",
            "headers": self.headers,
            "url": f"{Config.API}{Config.tradebook}",
            "params": None,
        }

    @client.request
    def funds(self) -> dict:
        """
        Retrieves funds details.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "GET",
            "headers": self.headers,
            "url": f"{Config.API}{Config.funds}",
            "params": None,
        }

    @client.request
    def positions(self) -> dict:
        """
        Retrieves information about current open positions.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "GET",
            "headers": self.headers,
            "url": f"{Config.API}{Config.positions}",
            "params": None,
        }

    @client.request
    def holdings(self) -> dict:
        """
        Retrieves information about current holdings.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "GET",
            "headers": self.headers,
            "url": f"{Config.API}{Config.holdings}",
            "params": None,
        }

    @client.request
    def orderbook(self) -> dict:
        """
        Retrieves order details by ID.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "GET",
            "headers": self.headers,
            "url": f"{Config.API}{Config.orderbook}",
            "params": None,
        }

    def get_orders(self, data) -> dict:
        """
        Retrieves order details by ID.

        Args:
            data: The data containing the order ID.

        Returns:
            The response JSON as a dictionary.
        """
        id_list = data.get("id").split(",")
        response = self.orderbook()
        response["orderBook"] = [order for order in response["orderBook"] if order["id"] in id_list]

        return response

    @client.request
    def market_status(self) -> dict:
        """
        Retrieves market status.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "GET",
            "headers": self.headers,
            "url": f"{Config.DATA_API}{Config.market_status}",
            "params": None,
        }

    @client.request
    def convert_position(self, data) -> dict:
        """
        Converts positions from one product type to another based on the provided details.

        Args:
            symbol (str): Symbol of the positions. Eg: "MCX:SILVERMIC20NOVFUT".
            positionSide (int): Side of the positions. 1 for open long positions, -1 for open short positions.
            convertQty (int): Quantity to be converted. Should be in multiples of lot size for derivatives.
            convertFrom (str): Existing product type of the positions. (CNC positions cannot be converted)
            convertTo (str): The new product type to convert the positions to.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "POST",
            "headers": self.headers,
            "url": f"{Config.API}{Config.convert_position}",
            "data": data,
        }

    @client.request
    def cancel_order(self, data) -> dict:
        """
        Cancel order.

        Args:
            id (str, optional): ID of the position to close. If not provided, all open positions will be closed.


        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "DELETE",
            "headers": self.headers,
            "url": f"{Config.API}{Config.orders_endpoint}",
            "params": data,
        }

    @client.request
    def place_order(self, data) -> dict:
        """
        Places an order based on the provided data.

        Args:
        data (dict): A dictionary containing the order details.
            - 'productType' (str): Type of the product. Possible values: 'CNC', 'INTRADAY', 'MARGIN', 'CO', 'BO'.
            - 'side' (int): Side of the order. 1 for Buy, -1 for Sell.
            - 'symbol' (str): Symbol of the product. Eg: 'NSE:SBIN-EQ'.
            - 'qty' (int): Quantity of the product. Should be in multiples of lot size for derivatives.
            - 'disclosedQty' (int): Disclosed quantity. Allowed only for equity. Default: 0.
            - 'type' (int): Type of the order. 1 for Limit Order, 2 for Market Order,
                            3 for Stop Order (SL-M), 4 for Stoplimit Order (SL-L).
            - 'validity' (str): Validity of the order. Possible values: 'IOC' (Immediate or Cancel), 'DAY' (Valid till the end of the day).
            - 'filledQty' (int): Filled quantity. Default: 0.
            - 'limitPrice' (float): Valid price for Limit and Stoplimit orders. Default: 0.
            - 'stopPrice' (float): Valid price for Stop and Stoplimit orders. Default: 0.
            - 'offlineOrder' (bool): Specifies if the order is placed when the market is open (False) or as an AMO order (True).

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "POST",
            "headers": self.headers,
            "url": f"{Config.API}{Config.orders_endpoint}",
            "data": data,
        }

    @client.request
    def modify_order(self, data) -> dict:
        """
        Modifies the parameters of a pending order based on the provided details.

        Parameters:
            id (str): ID of the pending order to be modified.
            limitPrice (float, optional): New limit price for the order. Mandatory for Limit/Stoplimit orders.
            stopPrice (float, optional): New stop price for the order. Mandatory for Stop/Stoplimit orders.
            qty (int, optional): New quantity for the order.
            type (int, optional): New order type for the order.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "PATCH",
            "headers": self.headers,
            "url": f"{Config.API}{Config.orders_endpoint}",
            "data": data,
        }

    @client.request
    def exit_positions(self, data=None) -> dict:
        """
        Closes open positions based on the provided ID or closes all open positions if ID is not passed.

        Args:
            id (str, optional): ID of the position to close. If not provided, all open positions will be closed.


        Returns:
            The response JSON as a dictionary.
        """
        if not data:
            data = {"exit_all": 1}

        return {
            "method": "DELETE",
            "headers": self.headers,
            "url": f"{Config.API}{Config.orders_endpoint}",
            "data": data,
        }

    @client.request
    def cancel_basket_orders(self, data):
        """
        Cancels the orders with the provided IDs.

        Parameters:
            order_ids (list): A list of order IDs to be cancelled.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "DELETE",
            "headers": self.headers,
            "url": f"{Config.API}{Config.multi_orders}",
            "data": data,
        }

    @client.request
    def place_basket_orders(self, data):
        """
        Places multiple orders based on the provided details.

        Parameters:
        orders (list): A list of dictionaries containing the order details.
            Each dictionary should have the following keys:
            - 'symbol' (str): Symbol of the product. Eg: 'MCX:SILVERM20NOVFUT'.
            - 'qty' (int): Quantity of the product.
            - 'type' (int): Type of the order. 1 for Limit Order, 2 for Market Order, and so on.
            - 'side' (int): Side of the order. 1 for Buy, -1 for Sell.
            - 'productType' (str): Type of the product. Eg: 'INTRADAY', 'CNC', etc.
            - 'limitPrice' (float): Valid price for Limit and Stoplimit orders.
            - 'stopPrice' (float): Valid price for Stop and Stoplimit orders.
            - 'disclosedQty' (int): Disclosed quantity. Allowed only for equity.
            - 'validity' (str): Validity of the order. Eg: 'DAY', 'IOC', etc.
            - 'offlineOrder' (bool): Specifies if the order is placed when the market is open (False) or as an AMO order (True).
            - 'stopLoss' (float): Valid price for CO and BO orders.
            - 'takeProfit' (float): Valid price for BO orders.


        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "POST",
            "headers": self.headers,
            "url": f"{Config.API}{Config.multi_orders}",
            "data": data,
        }

    @client.request
    def modify_basket_orders(self, data):
        """
        Modifies multiple pending orders based on the provided details.

        Parameters:
        orders (list): A list of dictionaries containing the order details to be modified.
            Each dictionary should have the following keys:
            - 'id' (str): ID of the pending order to be modified.
            - 'limitPrice' (float): New limit price for the order. Mandatory for Limit/Stoplimit orders.
            - 'stopPrice' (float): New stop price for the order. Mandatory for Stop/Stoplimit orders.
            - 'qty' (int): New quantity for the order.
            - 'type' (int): New order type for the order.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "PATCH",
            "headers": self.headers,
            "url": f"{Config.API}{Config.multi_orders}",
            "data": data,
        }

    @client.request
    def history(self, data=None):
        """
        Fetches candle data based on the provided parameters.

        Parameters:
        symbol (str): Symbol of the product. Eg: 'NSE:SBIN-EQ'.
        resolution (str): The candle resolution. Possible values are:
            'Day' or '1D', '1', '2', '3', '5', '10', '15', '20', '30', '60', '120', '240'.
        date_format (int): Date format flag. 0 to enter the epoch value, 1 to enter the date format as 'yyyy-mm-dd'.
        range_from (str): Start date of the records. Accepts epoch value if date_format flag is set to 0,
            or 'yyyy-mm-dd' format if date_format flag is set to 1.
        range_to (str): End date of the records. Accepts epoch value if date_format flag is set to 0,
            or 'yyyy-mm-dd' format if date_format flag is set to 1.
        cont_flag (int): Flag indicating continuous data and future options. Set to 1 for continuous data.


        Returns:
            The response JSON as a dictionary.
        """

        return {
            "method": "GET",
            "headers": self.headers,
            "url": f"{Config.DATA_API}{Config.history}",
            "data": data,
        }

    @client.request
    def quotes(self, data=None):
        """
        Fetches quotes data for multiple symbols.

        Parameters:
            symbols (str): Comma-separated symbols of the products. Maximum symbol limit is 50. Eg: 'NSE:SBIN-EQ,NSE:HDFC-EQ'.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "GET",
            "headers": self.headers,
            "url": f"{Config.DATA_API}{Config.quotes}",
            "params": data,
        }

    @client.request
    def depth(self, data=None):
        """
        Fetches market depth data for a symbol.

        Parameters:
            symbol (str): Symbol of the product. Eg: 'NSE:SBIN-EQ'.
            ohlcv_flag (int): Flag to indicate whether to retrieve open, high, low, closing, and volume quantity. Set to 1 for yes.

        Returns:
            The response JSON as a dictionary.
        """
        return {
            "method": "GET",
            "headers": self.headers,
            "url": f"{Config.DATA_API}{Config.market_depth}",
            "params": data,
        }
