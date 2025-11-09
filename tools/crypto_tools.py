"""
Cryptocurrency trading tools for BTC and ETH
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Supported cryptocurrencies
SUPPORTED_CRYPTOS = ["BTC", "ETH"]


def load_crypto_price_data(crypto_symbol: str, data_dir: str = "data") -> Dict:
    """
    Load cryptocurrency intraday price data from JSON file.
    """
    if crypto_symbol not in SUPPORTED_CRYPTOS:
        raise ValueError(f"Unsupported cryptocurrency: {crypto_symbol}")

    price_file = os.path.join(data_dir, f"crypto_prices_{crypto_symbol}.json")

    if not os.path.exists(price_file):
        print(f"⚠️  Price data not found for {crypto_symbol}: {price_file}")
        return {}

    try:
        with open(price_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {crypto_symbol} data: {e}")
        return {}

def load_crypto_daily_price_data(crypto_symbol: str, data_dir: str = "data") -> Dict:
    """
    Load cryptocurrency daily price data from JSON file.
    """
    if crypto_symbol not in SUPPORTED_CRYPTOS:
        raise ValueError(f"Unsupported cryptocurrency: {crypto_symbol}")

    price_file = os.path.join(data_dir, f"crypto_prices_{crypto_symbol}_daily.json")

    if not os.path.exists(price_file):
        print(f"⚠️  Daily price data not found for {crypto_symbol}: {price_file}")
        return {}

    try:
        with open(price_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading daily {crypto_symbol} data: {e}")
        return {}


def get_crypto_price_on_date(
    crypto_symbol: str, target_date: str, price_type: str = "close"
) -> Optional[float]:
    """
    Get the latest cryptocurrency price on a specific date from intraday data.
    """
    data = load_crypto_price_data(crypto_symbol)

    latest_datetime_str = None
    latest_dt = None

    for dt_str in data.keys():
        if dt_str.startswith(target_date):
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.strptime(dt_str, "%Y-%m-%d")
            if latest_dt is None or dt > latest_dt:
                latest_dt = dt
                latest_datetime_str = dt_str

    if latest_datetime_str:
        return data[latest_datetime_str].get(price_type, None)

    return None

def format_crypto_price_data(crypto_symbol: str, target_date: str) -> str:
    """
    Format cryptocurrency price data for display in agent prompt.
    """
    data = load_crypto_price_data(crypto_symbol)
    
    formatted_prices = []
    for dt_str, price_data in sorted(data.items()):
        if dt_str.startswith(target_date):
            prices = price_data
            formatted_prices.append(f"""{crypto_symbol} ({prices.get('date')}):
  Open:  ${prices.get('open', 'N/A'):,.2f}
  High:  ${prices.get('high', 'N/A'):,.2f}
  Low:   ${prices.get('low', 'N/A'):,.2f}
  Close: ${prices.get('close', 'N/A'):,.2f}""")

    if formatted_prices:
        return "\n".join(formatted_prices)

    return f"{crypto_symbol}: No data available for {target_date}"


def calculate_crypto_returns(
    crypto_symbol: str, purchase_date: str, purchase_price: float, sale_date: str
) -> Optional[Dict]:
    """
    Calculate returns from a crypto trade
    """
    sale_price = get_crypto_price_on_date(crypto_symbol, sale_date, "close")

    if sale_price is None:
        return None

    profit = sale_price - purchase_price
    return_pct = (profit / purchase_price) * 100

    return {
        "symbol": crypto_symbol,
        "purchase_date": purchase_date,
        "purchase_price": purchase_price,
        "sale_date": sale_date,
        "sale_price": sale_price,
        "profit": profit,
        "return_percentage": return_pct,
    }


def validate_crypto_data(crypto_symbols: list = None) -> Dict[str, bool]:
    """
    Validate that crypto price data is available and loaded
    """
    if crypto_symbols is None:
        crypto_symbols = SUPPORTED_CRYPTOS

    results = {}
    for symbol in crypto_symbols:
        data = load_crypto_price_data(symbol)
        results[symbol] = len(data) > 0

    return results


def get_crypto_price_summary(crypto_symbols: list = None) -> str:
    """
    Get summary of available crypto price data
    """
    if crypto_symbols is None:
        crypto_symbols = SUPPORTED_CRYPTOS

    summary = "Cryptocurrency Price Data Summary:\n"
    summary += "-" * 50 + "\n"

    for symbol in crypto_symbols:
        data = load_crypto_price_data(symbol)
        if data:
            dates = sorted(data.keys())
            latest_price = data[dates[-1]]["close"]
            summary += f"{symbol}: {len(data)} days | Latest: ${latest_price:,.2f}\n"
        else:
            summary += f"{symbol}: No data available\n"

    return summary
