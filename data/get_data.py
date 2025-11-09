#!/usr/bin/env python3
"""
Unified data fetcher - checks for local CSV first, then falls back to APIs
"""

import os
from pathlib import Path
from datetime import datetime
from convert_csv_to_json import convert_csv_to_json, convert_all_csv_files
from get_crypto_prices import (
    fetch_all_crypto_data as fetch_from_coingecko,
    get_crypto_current_price,
)
import requests
from dotenv import load_dotenv
import json

load_dotenv()

def fetch_futures_data(symbols: list):
    """
    Fetch intraday futures data from Alpha Vantage and save it to JSON files.
    """
    print("\n" + "=" * 60)
    print("DATA FETCHER - FUTURES HANDLER")
    print("=" * 60)

    for symbol in symbols:
        print(f"Fetching data for {symbol}...")
        # The GitHub workflow uses NQ1, but AlphaVantage expects NQ1!
        api_symbol = f"{symbol}!" if symbol == "NQ1" else symbol
        
        FUNCTION = "TIME_SERIES_INTRADAY"
        INTERVAL = "60min"
        OUTPUTSIZE = "compact"
        APIKEY = os.getenv("ALPHAADVANTAGE_API_KEY")
        url = f"https://www.alphavantage.co/query?function={FUNCTION}&symbol={api_symbol}&interval={INTERVAL}&outputsize={OUTPUTSIZE}&entitlement=delayed&apikey={APIKEY}"
        
        try:
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()

            if "Note" in data or "Information" in data:
                print(f"Error fetching data for {symbol}: {data.get('Note') or data.get('Information')}")
                continue

            time_series_key = f"Time Series ({INTERVAL})"
            if time_series_key not in data:
                print(f"Error: '{time_series_key}' not in response for {symbol}")
                continue
            
            time_series = data[time_series_key]
            
            formatted_data = {}
            for timestamp, values in time_series.items():
                formatted_data[timestamp] = {
                    "open": float(values["1. open"]),
                    "high": float(values["2. high"]),
                    "low": float(values["3. low"]),
                    "close": float(values["4. close"]),
                    "volume": int(values["5. volume"])
                }

            output_filename = f"future_prices_{symbol}.json"
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(formatted_data, f, ensure_ascii=False, indent=4)
            
            print(f"Successfully saved data for {symbol} to {output_filename}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {symbol}: {e}")
        except (KeyError, TypeError) as e:
            print(f"Error processing data for {symbol}: {e}")


def get_data(use_local_csv=True, asset_type="crypto", symbols=None, days=7):
    """
    Fetch market data - prefer local CSV, fall back to APIs
    """

    if symbols is None:
        symbols = ["BTC", "ETH"]

    print("\n" + "=" * 60)
    print("DATA FETCHER - UNIFIED CSV/API HANDLER")
    print("=" * 60)

    if asset_type == "futures":
        fetch_futures_data(symbols)
        return

    # Step 1: Check for local CSV files
    if use_local_csv:
        print("\n📁 Checking for local CSV files in tv_data/...\n")

        csv_dir = Path("tv_data")
        if csv_dir.exists():
            csv_files = list(csv_dir.glob("*.csv"))
            if csv_files:
                print(f"Found {len(csv_files)} CSV file(s):")
                for csv_file in csv_files:
                    print(f"  • {csv_file.name}")

                print("\n🔄 Converting CSV to JSON format...\n")
                converted = convert_all_csv_files("tv_data", ".")

                if converted:
                    print("\n✅ Local CSV data loaded successfully!")
                    print(f"   {len(converted)} files converted and ready for trading")
                    return
                else:
                    print("\n⚠️  CSV conversion failed, falling back to API...")
            else:
                print("ℹ️  No CSV files found in tv_data/")
                print("   Tip: Add TradingView CSV exports to tv_data/ folder\n")
        else:
            print("ℹ️  tv_data/ directory not found")
            print("   Creating: mkdir tv_data")
            os.makedirs("tv_data", exist_ok=True)

    # Step 2: Fall back to API based on asset type
    if asset_type == "crypto":
        print("\n📡 Fetching data from CoinGecko API...")
        print(f"   Symbols: {', '.join(symbols)}")
        print(f"   Days: {days}\n")
        fetch_from_coingecko(symbols=symbols, days=days, output_dir=".")
        print("\n✅ Data fetched successfully from CoinGecko!")
    elif asset_type == "stock":
        print("\n📡 Fetching stock data is not implemented yet in the fallback.")
        # Here you could add a stock API fetcher, e.g., using Alpha Vantage
    else:
        print(f"\n⚠️  Unsupported asset type for API fallback: {asset_type}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Unified data fetcher")
    parser.add_argument(
        "--no-csv", action="store_true", help="Skip local CSV, use API only"
    )
    parser.add_argument(
        "--asset-type", default="crypto", help="Asset type: crypto, stock, or futures"
    )
    parser.add_argument(
        "--symbols", default="BTC,ETH", help="Comma-separated symbols"
    )

    args = parser.parse_args()

    # Calculate days from environment variables
    start_str = os.getenv("START_DATETIME")
    end_str = os.getenv("END_DATETIME")
    days_to_fetch = 7  # Default value

    if start_str and end_str:
        try:
            start_dt = datetime.strptime(start_str, "%m%d%y %H%M")
            end_dt = datetime.strptime(end_str, "%m%d%y %H%M")
            delta = end_dt - start_dt
            # Add 1 to make the range inclusive
            days_to_fetch = delta.days + 1
            if days_to_fetch <= 0:
                days_to_fetch = 1
            print(f"🗓️ Calculated days to fetch from environment variables: {days_to_fetch}")
        except ValueError:
            print(f"⚠️ Could not parse START_DATETIME or END_DATETIME. Using default {days_to_fetch} days.")
    else:
        print(f"🗓️ Using default days to fetch: {days_to_fetch}")

    symbols = [s.strip().upper() for s in args.symbols.split(",")]

    get_data(
        use_local_csv=not args.no_csv,
        asset_type=args.asset_type,
        symbols=symbols,
        days=days_to_fetch,
    )
