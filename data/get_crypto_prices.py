#!/usr/bin/env python3
"""
Fetch cryptocurrency price data from CoinGecko API
Supports: Bitcoin (BTC) and Ethereum (ETH)
"""

import json
import os
import time
from datetime import datetime, timedelta

import polars as pl
import requests

COINGECKO_API = "https://api.coingecko.com/api/v3"
CRYPTO_MAP = {"BTC": "bitcoin", "ETH": "ethereum"}


def get_crypto_daily_data(symbol: str, days: int = 180) -> dict:
    """
    Fetch historical daily cryptocurrency price data from CoinGecko.
    """
    crypto_id = CRYPTO_MAP.get(symbol)
    if not crypto_id:
        raise ValueError(f"Unsupported crypto symbol: {symbol}")

    try:
        url = f"{COINGECKO_API}/coins/{crypto_id}/ohlc"
        params = {"vs_currency": "usd", "days": str(days)}
        print(f"Fetching {days}-day DAILY OHLC data for {symbol}...")
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        if not data:
            return {}

        ohlcv_data = {
            datetime.fromtimestamp(p[0] / 1000).strftime("%Y-%m-%d"): {
                "date": datetime.fromtimestamp(p[0] / 1000).strftime("%Y-%m-%d"),
                "open": p[1], "high": p[2], "low": p[3], "close": p[4], "volume": 0,
            }
            for p in data
        }
        print(f"✓ Retrieved {len(ohlcv_data)} daily data points for {symbol}")
        return ohlcv_data
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching daily data for {symbol}: {e}")
        return {}


def get_crypto_intraday_data(symbol: str, from_date: datetime, to_date: datetime) -> dict:
    """
    Fetch and resample historical intraday (hourly) data using the market_chart/range endpoint.
    """
    crypto_id = CRYPTO_MAP.get(symbol)
    if not crypto_id:
        raise ValueError(f"Unsupported crypto symbol: {symbol}")

    from_ts = int(from_date.timestamp())
    to_ts = int(to_date.timestamp())

    try:
        url = f"{COINGECKO_API}/coins/{crypto_id}/market_chart/range"
        params = {"vs_currency": "usd", "from": str(from_ts), "to": str(to_ts)}
        print(f"Fetching INTRADAY data for {symbol} from {from_date} to {to_date}...")
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        if not data.get("prices"):
            return {}

        # Use Polars to resample price data into hourly OHLC
        df = pl.DataFrame(data["prices"], schema=["timestamp", "price"])
        df = df.with_columns(
            (pl.col("timestamp") / 1000).cast(pl.Int64).alias("timestamp_s"),
        ).with_columns(
            pl.from_epoch(pl.col("timestamp_s"), time_unit="s").alias("datetime")
        )

        df_ohlc = df.group_by_dynamic("datetime", every="1h").agg(
            pl.col("price").first().alias("open"),
            pl.col("price").max().alias("high"),
            pl.col("price").min().alias("low"),
            pl.col("price").last().alias("close"),
        )

        ohlcv_data = {
            row["datetime"].strftime("%Y-%m-%d %H:%M:%S"): {
                "date": row["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                "open": row["open"], "high": row["high"], "low": row["low"], "close": row["close"], "volume": 0,
            }
            for row in df_ohlc.to_dicts()
        }
        print(f"✓ Resampled into {len(ohlcv_data)} hourly data points for {symbol}")
        return ohlcv_data
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching intraday data for {symbol}: {e}")
        return {}


def save_crypto_data(symbol: str, data: dict, output_dir: str = "data", suffix: str = ""):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/crypto_prices_{symbol}{suffix}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved {symbol} data to {filename}")


def fetch_all_crypto_data(
    symbols: list = None, intraday_days: int = 3, daily_days: int = 180, output_dir: str = "data"
):
    if symbols is None:
        symbols = ["BTC", "ETH"]

    print("\n" + "=" * 60)
    print("CRYPTOCURRENCY PRICE DATA FETCHER")
    print(f"Fetching data for: {', '.join(symbols)}")
    print("=" * 60 + "\n")

    to_date = datetime.now()
    intraday_from_date = to_date - timedelta(days=intraday_days)
    daily_from_date = to_date - timedelta(days=daily_days)

    for symbol in symbols:
        try:
            daily_data = get_crypto_daily_data(symbol, days=daily_days)
            if daily_data:
                save_crypto_data(symbol, daily_data, output_dir, suffix="_daily")
            else:
                print(f"⚠️  Failed to fetch daily data for {symbol}\n")

            time.sleep(2)

            intraday_data = get_crypto_intraday_data(symbol, from_date=intraday_from_date, to_date=to_date)
            if intraday_data:
                save_crypto_data(symbol, intraday_data, output_dir, suffix="")
            else:
                print(f"⚠️  Failed to fetch intraday data for {symbol}\n")

        except Exception as e:
            print(f"✗ Error processing {symbol}: {e}\n")

        print("-" * 20)
        time.sleep(2)

    print("=" * 60)
    print("✓ Cryptocurrency data fetch complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch cryptocurrency price data.")
    parser.add_argument("--symbols", type=str, default="BTC,ETH", help="Comma-separated list of crypto symbols.")
    parser.add_argument("--intraday_days", type=int, default=3, help="Number of days of high-granularity data.")
    parser.add_argument("--daily_days", type=int, default=180, help="Number of days of daily data for context.")
    args = parser.parse_args()
    
    symbols_list = [s.strip().upper() for s in args.symbols.split(',')]
    
    fetch_all_crypto_data(
        symbols=symbols_list,
        intraday_days=args.intraday_days,
        daily_days=args.daily_days,
        output_dir="data",
    )