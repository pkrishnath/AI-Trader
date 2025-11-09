#!/usr/bin/env python3
"""
Fetch cryptocurrency price data from CoinGecko API
Supports: Bitcoin (BTC) and Ethereum (ETH)
CoinGecko API is free and doesn't require authentication
"""

import json
import os
import time
from datetime import datetime
import requests

# CoinGecko API endpoints
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Cryptocurrency mapping
CRYPTO_MAP = {"BTC": "bitcoin", "ETH": "ethereum"}


def get_crypto_daily_data(symbol: str, days: int = 180) -> dict:
    """
    Fetch historical daily cryptocurrency price data from CoinGecko.
    """
    if symbol not in CRYPTO_MAP:
        raise ValueError(f"Unsupported crypto symbol: {symbol}")
    crypto_id = CRYPTO_MAP[symbol]
    try:
        url = f"{COINGECKO_API}/coins/{crypto_id}/ohlc"
        params = {"vs_currency": "usd", "days": str(days)}
        print(f"Fetching {days}-day DAILY OHLC data for {symbol}...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            print(f"No DAILY OHLC data found for {symbol}")
            return {}

        ohlcv_data = {}
        for ohlc_point in data:
            dt_object = datetime.fromtimestamp(ohlc_point[0] / 1000)
            date_str = dt_object.strftime("%Y-%m-%d")
            ohlcv_data[date_str] = {
                "date": date_str,
                "open": ohlc_point[1],
                "high": ohlc_point[2],
                "low": ohlc_point[3],
                "close": ohlc_point[4],
                "volume": 0,
            }
        print(f"✓ Retrieved {len(ohlcv_data)} daily data points for {symbol}")
        return ohlcv_data
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching daily data for {symbol}: {e}")
        return {}


def get_crypto_intraday_data(symbol: str, days: int = 3) -> dict:
    """
    Fetch historical intraday (30-min) cryptocurrency price data from CoinGecko.
    """
    if symbol not in CRYPTO_MAP:
        raise ValueError(f"Unsupported crypto symbol: {symbol}")
    crypto_id = CRYPTO_MAP[symbol]
    try:
        url = f"{COINGECKO_API}/coins/{crypto_id}/ohlc"
        params = {"vs_currency": "usd", "days": str(days)}
        print(f"Fetching {days}-day INTRADAY OHLC data for {symbol}...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            print(f"No INTRADAY OHLC data found for {symbol}")
            return {}

        ohlcv_data = {}
        for ohlc_point in data:
            dt_object = datetime.fromtimestamp(ohlc_point[0] / 1000)
            datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")
            ohlcv_data[datetime_str] = {
                "date": datetime_str,
                "open": ohlc_point[1],
                "high": ohlc_point[2],
                "low": ohlc_point[3],
                "close": ohlc_point[4],
                "volume": 0,
            }
        print(f"✓ Retrieved {len(ohlcv_data)} intraday data points for {symbol}")
        return ohlcv_data
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching intraday data for {symbol}: {e}")
        return {}


def save_crypto_data(symbol: str, data: dict, output_dir: str = "data", suffix: str = "") -> str:
    """
    Save cryptocurrency data to JSON file.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/crypto_prices_{symbol}{suffix}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved {symbol} data to {filename}")
    return filename


def fetch_all_crypto_data(symbols: list = None, intraday_days: int = 3, daily_days: int = 180, output_dir: str = "data"):
    """
    Fetch and save both daily and intraday data for all cryptocurrencies.
    """
    if symbols is None:
        symbols = ["BTC", "ETH"]

    print("\n" + "=" * 60)
    print("CRYPTOCURRENCY PRICE DATA FETCHER")
    print(f"Fetching data for: {', '.join(symbols)}")
    print("=" * 60 + "\n")

    for symbol in symbols:
        try:
            # Fetch and save daily data for high-level bias
            daily_data = get_crypto_daily_data(symbol, days=daily_days)
            if daily_data:
                save_crypto_data(symbol, daily_data, output_dir, suffix="_daily")
            else:
                print(f"⚠️  Failed to fetch daily data for {symbol}\n")

            # Add a small delay to be nice to the free API
            time.sleep(1)

            # Fetch and save intraday data for entries
            intraday_data = get_crypto_intraday_data(symbol, days=intraday_days)
            if intraday_data:
                save_crypto_data(symbol, intraday_data, output_dir, suffix="")
            else:
                print(f"⚠️  Failed to fetch intraday data for {symbol}\n")

        except Exception as e:
            print(f"✗ Error processing {symbol}: {e}\n")
        
        print("-" * 20)
        time.sleep(1) # Delay before next symbol

    print("=" * 60)
    print("✓ Cryptocurrency data fetch complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Fetch cryptocurrency price data.')
    parser.add_argument('--symbols', type=str, default='BTC,ETH', help='Comma-separated list of crypto symbols to fetch.')
    parser.add_argument('--intraday_days', type=int, default=3, help='Number of days of high-granularity intraday data to fetch.')
    parser.add_argument('--daily_days', type=int, default=180, help='Number of days of daily data to fetch for context.')
    args = parser.parse_args()
    
    symbols_list = [s.strip().upper() for s in args.symbols.split(',')]
    
    fetch_all_crypto_data(symbols=symbols_list, intraday_days=args.intraday_days, daily_days=args.daily_days, output_dir=".")
