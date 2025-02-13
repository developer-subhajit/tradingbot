# Momentum Swing Trading Bot

A Python-based automated trading bot that implements a momentum swing trading strategy using the Fyers trading platform. The bot analyzes stocks from specified indices (like Nifty 50 or Nifty Next 50) and makes trading decisions based on momentum indicators.

## Features

- Automated momentum-based trading strategy
- Integration with Fyers trading platform
- Historical data analysis and storage
- Telegram notifications for trade alerts
- Portfolio management with customizable parameters
- Concurrent processing for efficient data handling

## Prerequisites

- Python 3.8+
- Fyers Trading Account
- Telegram Bot Token (optional, for notifications)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/tradingbot.git
cd tradingbot
```

2. Install dependencies using pipenv:
```bash
pipenv install
```

3. Create a `.env` file in the root directory with your credentials:
```env
fyers_app_id=your_app_id
fyers_app_type=your_app_type
fyers_secret_key=your_secret_key
fyers_id=your_fyers_id
fyers_totp_key=your_totp_key
fyers_userpin=your_pin
telegram_bot_token=your_telegram_bot_token
telegram_chat_id=your_chat_id
```

## Project Structure

```
tradingbot/
├── momentum_swing.py     # Main trading strategy implementation
├── fyersLogin.py        # Fyers authentication handling
├── fyersModel.py        # Fyers API interaction model
├── telegram.py          # Telegram notification implementation
├── instances.py         # Instance management
├── utils/              # Utility functions
├── data/               # Historical data storage
└── log/                # Application logs
```

## Usage

1. Set up your environment variables in the `.env` file
2. Run the trading bot:
```bash
python momentum_swing.py
```

## Configuration

The bot can be configured with the following parameters:

- `cash`: Initial investment amount
- `benchmark_index`: Index to trade (e.g., "nifty next 50")
- `portfolio_size`: Number of stocks to hold in portfolio
- `threshold`: Momentum threshold for trading decisions

Example:
```python
ms = MomentumSwing(
    cash=30000,
    benchmark_index="nifty next 50",
    portfolio_size=5,
    threshold=0.25
)
```

## Trading Strategy

The bot implements a momentum swing trading strategy:

1. Fetches historical data for stocks in the specified index
2. Calculates weekly returns and momentum indicators
3. Ranks stocks based on momentum
4. Makes trading decisions based on momentum thresholds
5. Manages portfolio according to specified parameters

## Security

- Never commit your `.env` file
- Keep your API keys and credentials secure
- Use environment variables for sensitive information
- Enable 2FA on your trading account

## Disclaimer

This trading bot is for educational and demonstration purposes only. Trading in financial markets carries risk, and past performance does not guarantee future results. Use at your own risk.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 