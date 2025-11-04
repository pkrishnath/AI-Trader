"""
Futures trading tools for NQ1!, ES, and other CME futures contracts
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Supported futures contracts
SUPPORTED_FUTURES = ["NQ1", "ES", "MES", "MNQ", "YM", "GC", "CL", "ZB", "ZS", "ZC", "ZW"]


def load_futures_price_data(futures_symbol: str, data_dir: str = "data") -> Dict:
    """
    Load futures price data from JSON file

    Args:
        futures_symbol: Futures symbol (NQ1, ES, etc.)
        data_dir: Directory containing price data

    Returns:
        Dictionary with datetime -> OHLCV data
    """
    if futures_symbol not in SUPPORTED_FUTURES:
        raise ValueError(f"Unsupported futures contract: {futures_symbol}")

    price_file = os.path.join(data_dir, f"future_prices_{futures_symbol}.json")

    if not os.path.exists(price_file):
        print(f"⚠️  Price data not found for {futures_symbol}: {price_file}")
        return {}

    try:
        with open(price_file, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading {futures_symbol} data: {e}")
        return {}


def get_futures_price_on_date(
    futures_symbol: str, target_date: str, price_type: str = "close"
) -> Optional[float]:
    """
    Get the latest futures price on a specific date.

    Args:
        futures_symbol: Futures symbol (NQ1, ES, etc.)
        target_date: Date string (YYYY-MM-DD)
        price_type: Type of price (open, close, high, low)

    Returns:
        Price value or None if not found
    """
    data = load_futures_price_data(futures_symbol)

    latest_datetime_str = None
    latest_dt = None

    for dt_str in data.keys():
        if dt_str.startswith(target_date):
            # Handle both formats: "YYYY-MM-DD HH:MM:SS" and "YYYY-MM-DD"
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

def get_futures_price_at_time(
    futures_symbol: str, target_date: str, target_time: str, price_type: str = "close"
) -> Optional[float]:
    """
    Get the futures price at a specific time on a specific date.

    Args:
        futures_symbol: Futures symbol (NQ1, ES, etc.)
        target_date: Date string (YYYY-MM-DD)
        target_time: Time string (HH:MM)
        price_type: Type of price (open, close, high, low)

    Returns:
        Price value or None if not found
    """
    data = load_futures_price_data(futures_symbol)

    target_datetime_str = f"{target_date} {target_time}:00"
    if target_datetime_str in data:
        return data[target_datetime_str].get(price_type)

    # If exact time not found, find the closest available time
    target_dt = datetime.strptime(target_datetime_str, "%Y-%m-%d %H:%M:%S")
    closest_dt = None
    min_diff = float('inf')

    for dt_str in data.keys():
        if dt_str.startswith(target_date):
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            diff = abs((dt - target_dt).total_seconds())
            if diff < min_diff:
                min_diff = diff
                closest_dt = dt

    if closest_dt:
        return data[closest_dt.strftime("%Y-%m-%d %H:%M:%S")].get(price_type)

    return None


def get_futures_price_on_date(
    futures_symbol: str, target_date: str, price_type: str = "close"
) -> Optional[float]:
    """
    Get the latest futures price on a specific date.

    Args:
        futures_symbol: Futures symbol (NQ1, ES, etc.)
        target_date: Date string (YYYY-MM-DD)
        price_type: Type of price (open, close, high, low)

    Returns:
        Price value or None if not found
    """
    return get_futures_price_at_time(futures_symbol, target_date, "23:59", price_type)


def format_futures_price_data(futures_symbol: str, target_date: str) -> str:
    """
    Format futures price data for display in agent prompt.

    Args:
        futures_symbol: Futures symbol (NQ1, ES, etc.)
        target_date: Date to get prices for

    Returns:
        Formatted string with all intraday price data for the day.
    """
    data = load_futures_price_data(futures_symbol)

    formatted_prices = []
    for dt_str, price_data in sorted(data.items()):
        if dt_str.startswith(target_date):
            prices = price_data
            formatted_prices.append(
                f'''{futures_symbol} ({prices.get('date')}):
  Open:  ${prices.get('open', 'N/A'):,.2f}
  High:  ${prices.get('high', 'N/A'):,.2f}
  Low:   ${prices.get('low', 'N/A'):,.2f}
  Close: ${prices.get('close', 'N/A'):,.2f}'''
            )

    if formatted_prices:
        return "\n".join(formatted_prices)

    return f"{futures_symbol}: No data available for {target_date}"


def calculate_futures_returns(
    futures_symbol: str, entry_date: str, entry_price: float, exit_date: str
) -> Optional[Dict]:
    """
    Calculate returns from a futures trade

    Args:
        futures_symbol: Futures symbol (NQ1, ES, etc.)
        entry_date: Entry date (YYYY-MM-DD)
        entry_price: Entry price
        exit_date: Exit date (YYYY-MM-DD)

    Returns:
        Dictionary with return metrics or None if dates not found
    """
    exit_price = get_futures_price_on_date(futures_symbol, exit_date, "close")

    if exit_price is None:
        return None

    profit = exit_price - entry_price
    return_pct = (profit / entry_price) * 100

    return {
        "symbol": futures_symbol,
        "entry_date": entry_date,
        "entry_price": entry_price,
        "exit_date": exit_date,
        "exit_price": exit_price,
        "profit": profit,
        "return_percentage": return_pct,
    }


def validate_futures_data(futures_symbols: list = None) -> Dict[str, bool]:
    """
    Validate that futures price data is available and loaded

    Args:
        futures_symbols: List of symbols to validate (default: all)

    Returns:
        Dictionary with symbol -> available status
    """
    if futures_symbols is None:
        futures_symbols = SUPPORTED_FUTURES

    results = {}
    for symbol in futures_symbols:
        data = load_futures_price_data(symbol)
        results[symbol] = len(data) > 0

    return results


def get_futures_price_summary(futures_symbols: list = None) -> str:
    """
    Get summary of available futures price data

    Args:
        futures_symbols: List of symbols (default: all)

    Returns:
        Formatted summary string
    """
    if futures_symbols is None:
        futures_symbols = SUPPORTED_FUTURES

    summary = "Futures Price Data Summary:\n"
    summary += "-" * 50 + "\n"

    for symbol in futures_symbols:
        data = load_futures_price_data(symbol)
        if data:
            dates = sorted(data.keys())
            latest_price = data[dates[-1]]["close"]
            summary += f"{symbol}: {len(data)} candles | Latest: ${latest_price:,.2f}\n"
        else:
            summary += f"{symbol}: No data available\n"

    return summary
