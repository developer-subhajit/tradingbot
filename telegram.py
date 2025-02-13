"""
Telegram Bot Integration Module

This module provides functionality to send notifications and alerts via Telegram.
It uses the Telegram Bot API to send messages to a specified chat or channel.

Environment Variables Required:
    - telegram_bot_token: Your Telegram Bot API token
    - telegram_chat_id: The chat ID where messages will be sent

Author: Your Name
License: MIT
"""

import os
import utils as utils


class TelegramCredentials:
    token = os.environ.get("telegram_token")
    group_chat_id = os.environ.get("telegram_group_chat_id")
    personal_chat_id = os.environ.get("telegram_personal_chat_id")


class TelegramBot(utils.ExceptionLogger):
    """
    A class to handle Telegram bot notifications.
    
    This class provides methods to send messages, including trade alerts and error notifications,
    to a specified Telegram chat or channel.
    
    Attributes:
        bot_token (str): Telegram Bot API token
        chat_id (str): Telegram chat ID where messages will be sent
        base_url (str): Base URL for Telegram Bot API
    """

    def __init__(self, log_path: str = "log"):
        """
        Initialize the TelegramBot instance.
        
        Args:
            log_path: Path where log files will be stored
        """
        utils.ExceptionLogger.__init__(self, level="DEBUG", log_path=log_path)
        self.bot_token = os.environ.get("telegram_bot_token")
        self.chat_id = os.environ.get("telegram_chat_id")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        os.makedirs(self.log_path, exist_ok=True)

    @property
    def _validate_credentials(self):
        """
        Validate that required credentials are present.
        
        Raises:
            ValueError: If bot_token or chat_id is missing
        """
        if not all([self.bot_token, self.chat_id]):
            raise ValueError("Telegram credentials not found in environment variables")

    def make_request(self, func):
        # create a looger instance
        logger = utils.ExceptionLogger(
            level="DEBUG", log_path=self.log_path, reraise_on_exception=False)
        # create a HTTP request handler
        client = utils.RestClient()
        wrapper = logger.log_exception(client.request(func))
        return wrapper()

    def sendMessage(self, text):
        """
        Send a text message via the Telegram Bot API.

        Args:
            text (str): The text of the message.

        Returns:
            dict: The API request parameters.
        """
        try:
            self._validate_credentials
            inputs = {"method": "POST", "url": f"{self.base_url}/sendMessage", "params": {
                "chat_id": self.chat_id, "text": text}}
            return self.make_request(lambda: inputs)
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {str(e)}")
            return None

    def sendDocument(self, document_path, caption=""):
        """
        Send a document via the Telegram Bot API.

        Args:
            document_path (str): The path to the document file.
            caption (str, optional): The caption for the document (default is '').

        Returns:
            dict: The API request parameters.
        """
        try:
            self._validate_credentials
            inputs = {
                "method": "POST",
                "url": f"{self.base_url}/sendDocument",
                "params": {"chat_id": self.chat_id, "caption": caption},
                "files": {"document": open(document_path, "rb")},
            }
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {str(e)}")
        except Exception as e:
            raise e
        return self.make_request(lambda: inputs)

    def sendPhoto(self, photo_path, caption=""):
        """
        Send a photo via the Telegram Bot API.

        Args:
            photo_path (str): The path to the photo file.
            caption (str, optional): The caption for the photo (default is '').

        Returns:
            dict: The API request parameters.
        """
        try:
            self._validate_credentials
            inputs = {
                "method": "POST",
                "url": f"{self.base_url}/sendPhoto",
                "params": {"chat_id": self.chat_id, "caption": caption},
                "files": {"photo": open(photo_path, "rb")},
            }
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {str(e)}")
        except Exception as e:
            raise e
        return self.make_request(lambda: inputs)


if __name__ == "__main__":
    telebot = TelegramBot(log_path=f"{os.getcwd()}/log")
    telebot.sendMessage("Hello world")
