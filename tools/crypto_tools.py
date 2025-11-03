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
    Load cryptocurrency price data from JSON file

    Args:
        crypto_symbol: Crypto symbol (BTC, ETH)
        data_dir: Directory containing price data

    Returns:
        Dictionary with date -> OHLCV data
    """
    if crypto_symbol not in SUPPORTED_CRYPTOS:
        raise ValueError(f"Unsupported cryptocurrency: {crypto_symbol}")

    price_file = os.path.join(data_dir, f"crypto_prices_{crypto_symbol}.json")

    if not os.path.exists(price_file):
        print(f"⚠️  Price data not found for {crypto_symbol}: {price_file}")
        return {}

    try:
        with open(price_file, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading {crypto_symbol} data: {e}")
        return {}


def get_crypto_price_on_date(
    crypto_symbol: str, target_date: str, price_type: str = "close", hour: Optional[int] = None
) -> Optional[float]:
    """
    Get cryptocurrency price on a specific date and hour.

    Args:
        crypto_symbol: Crypto symbol (BTC, ETH)
        target_date: Date string (YYYY-MM-DD)
        price_type: Type of price (open, close, high, low)
        hour: Optional hour (0-23). If None, get the latest hour for the date.

    Returns:
        Price value or None if not found
    """
    data = load_crypto_price_data(crypto_symbol)

    if hour is not None:
        target_datetime_str = f"{target_date} {hour:02d}:00:00"
        if target_datetime_str in data:
            return data[target_datetime_str].get(price_type, None)
    else:
        # Find the latest hour for the given date
        latest_hour = -1
        for dt_str in data.keys():
            if dt_str.startswith(target_date):
                h = int(dt_str.split(' ')[1].split(':')[0])
                if h > latest_hour:
                    latest_hour = h
        
        if latest_hour != -1:
            target_datetime_str = f"{target_date} {latest_hour:02d}:00:00"
            return data[target_datetime_str].get(price_type, None)

    return None


def get_crypto_prices_range(crypto_symbol: str, start_date: str, end_date: str) -> Dict:
    """
    Get cryptocurrency prices for a date range

    Args:
        crypto_symbol: Crypto symbol (BTC, ETH)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)

    Returns:
        Dictionary with date -> OHLCV data for the range
    """
    data = load_crypto_price_data(crypto_symbol)

    # Filter by date range
    filtered_data = {}
    for date, prices in data.items():
        if start_date <= date <= end_date:
            filtered_data[date] = prices

    return filtered_data


def get_crypto_latest_price(crypto_symbol: str) -> Optional[float]:
    """
    Get the latest available price for a cryptocurrency

    Args:
        crypto_symbol: Crypto symbol (BTC, ETH)

    Returns:
        Latest close price or None
    """
    data = load_crypto_price_data(crypto_symbol)

    if not data:
        return None

    # Get latest date (last entry)
    latest_date = sorted(data.keys())[-1]
    return data[latest_date].get("close", None)


def format_crypto_price_data(crypto_symbol: str, target_date: str) -> str:
    """
    Format cryptocurrency price data for display in agent prompt

    Args:
        crypto_symbol: Crypto symbol (BTC, ETH)
        target_date: Date to get prices for

    Returns:
        Formatted string with price data for the latest hour of the day
    """
    data = load_crypto_price_data(crypto_symbol)

    latest_hour = -1
    latest_hour_data = None
    for dt_str, price_data in data.items():
        if dt_str.startswith(target_date):
            h = int(dt_str.split(' ')[1].split(':')[0])
            if h > latest_hour:
                latest_hour = h
                latest_hour_data = price_data

    if latest_hour_data:
        prices = latest_hour_data
        return f"""{crypto_symbol} ({prices.get('date')}):
  Open:  ${prices.get('open', 'N/A'):,.2f}
  High:  ${prices.get('high', 'N/A'):,.2f}
  Low:   ${prices.get('low', 'N/A'):,.2f}
  Close: ${prices.get('close', 'N/A'):,.2f}"""

    return f"{crypto_symbol}: No data available for {target_date}"


def calculate_crypto_returns(
    crypto_symbol: str, purchase_date: str, purchase_price: float, sale_date: str
) -> Optional[Dict]:
    """
    Calculate returns from a crypto trade

    Args:
        crypto_symbol: Crypto symbol (BTC, ETH)
        purchase_date: Purchase date (YYYY-MM-DD)
        purchase_price: Purchase price
        sale_date: Sale date (YYYY-MM-DD)

    Returns:
        Dictionary with return metrics or None if dates not found
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

    Args:
        crypto_symbols: List of symbols to validate (default: all)

    Returns:
        Dictionary with symbol -> available status
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

    Args:
        crypto_symbols: List of symbols (default: all)

    Returns:
        Formatted summary string
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
