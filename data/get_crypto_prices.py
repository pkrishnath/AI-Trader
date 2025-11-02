#!/usr/bin/env python3
"""
Fetch cryptocurrency price data from CoinGecko API
Supports: Bitcoin (BTC) and Ethereum (ETH)
CoinGecko API is free and doesn't require authentication
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests

# CoinGecko API endpoints
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Cryptocurrency mapping
CRYPTO_MAP = {"BTC": "bitcoin", "ETH": "ethereum"}


def get_crypto_historical_data(symbol: str, days: int = 30) -> dict:
    """
    Fetch historical cryptocurrency price data from CoinGecko

    Args:
        symbol: Crypto symbol (BTC, ETH)
        days: Number of days of historical data to fetch

    Returns:
        Dictionary with OHLCV data
    """
    if symbol not in CRYPTO_MAP:
        raise ValueError(f"Unsupported crypto symbol: {symbol}")

    crypto_id = CRYPTO_MAP[symbol]

    try:
        url = f"{COINGECKO_API}/coins/{crypto_id}/market_chart"
        params = {"vs_currency": "usd", "days": days, "interval": "daily"}

        print(f"Fetching {days}-day historical data for {symbol}...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        prices = data.get("prices", [])

        if not prices:
            print(f"No price data found for {symbol}")
            return {}

        # Convert to OHLCV format (using close price as all four OHLC values for simplicity)
        ohlcv_data = {}
        for price_point in prices:
            timestamp = price_point[0]  # milliseconds
            price = price_point[1]

            # Convert timestamp to date string
            date = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")

            if date not in ohlcv_data:
                ohlcv_data[date] = {
                    "date": date,
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": 0,
                }
            else:
                # Update high/low if needed
                ohlcv_data[date]["high"] = max(ohlcv_data[date]["high"], price)
                ohlcv_data[date]["low"] = min(ohlcv_data[date]["low"], price)
                ohlcv_data[date]["close"] = price

        print(f"✓ Retrieved {len(ohlcv_data)} days of data for {symbol}")
        return ohlcv_data

    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching data for {symbol}: {e}")
        return {}


def get_crypto_current_price(symbol: str) -> float:
    """
    Get current price for a cryptocurrency

    Args:
        symbol: Crypto symbol (BTC, ETH)

    Returns:
        Current price in USD
    """
    if symbol not in CRYPTO_MAP:
        raise ValueError(f"Unsupported crypto symbol: {symbol}")

    crypto_id = CRYPTO_MAP[symbol]

    try:
        url = f"{COINGECKO_API}/simple/price"
        params = {"ids": crypto_id, "vs_currencies": "usd"}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        price = data.get(crypto_id, {}).get("usd", 0)

        print(f"{symbol} current price: ${price:,.2f}")
        return price

    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching current price for {symbol}: {e}")
        return 0


def save_crypto_data(symbol: str, data: dict, output_dir: str = "data") -> str:
    """
    Save cryptocurrency data to JSON file

    Args:
        symbol: Crypto symbol
        data: OHLCV data dictionary
        output_dir: Output directory path

    Returns:
        Path to saved file
    """
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{output_dir}/crypto_prices_{symbol}.json"

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Saved {symbol} data to {filename}")
    return filename


def fetch_all_crypto_data(
    symbols: list = None, days: int = 30, output_dir: str = "data"
):
    """
    Fetch and save data for all cryptocurrencies

    Args:
        symbols: List of crypto symbols (default: BTC, ETH)
        days: Number of days of historical data
        output_dir: Output directory
    """
    if symbols is None:
        symbols = ["BTC", "ETH"]

    print("\n" + "=" * 60)
    print("CRYPTOCURRENCY PRICE DATA FETCHER")
    print("=" * 60)
    print(f"Fetching {days}-day historical data for: {', '.join(symbols)}")
    print(f"Using free CoinGecko API (no authentication required)")
    print("=" * 60 + "\n")

    for symbol in symbols:
        try:
            # Fetch historical data
            historical_data = get_crypto_historical_data(symbol, days)

            if historical_data:
                # Save to file
                save_crypto_data(symbol, historical_data, output_dir)

                # Show current price
                current_price = get_crypto_current_price(symbol)
                print()
            else:
                print(f"⚠️  Failed to fetch data for {symbol}\n")

        except Exception as e:
            print(f"✗ Error processing {symbol}: {e}\n")

    print("=" * 60)
    print("✓ Cryptocurrency data fetch complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Fetch cryptocurrency price data.')
    parser.add_argument('--symbols', type=str, default='BTC,ETH', help='Comma-separated list of crypto symbols to fetch.')
    parser.add_argument('--days', type=int, default=60, help='Number of days of historical data to fetch.')
    args = parser.parse_args()
    
    symbols = [s.strip().upper() for s in args.symbols.split(',')]
    
    # Fetch historical data for the given symbols
    fetch_all_crypto_data(symbols=symbols, days=args.days, output_dir=".")
