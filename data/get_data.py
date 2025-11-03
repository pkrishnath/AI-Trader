#!/usr/bin/env python3
"""
Unified data fetcher - checks for local CSV first, then falls back to CoinGecko API
"""

import os
from pathlib import Path
from convert_csv_to_json import convert_csv_to_json, convert_all_csv_files
from get_crypto_prices import (
    fetch_all_crypto_data as fetch_from_coingecko,
    get_crypto_current_price,
)


def get_data(use_local_csv=True, asset_type="crypto", symbols=None, days=60):
    """
    Fetch market data - prefer local CSV, fall back to CoinGecko

    Args:
        use_local_csv: If True, check for CSV files in tv_data/ first
        asset_type: "crypto" or "stock"
        symbols: List of symbols to fetch (e.g., ["BTC", "ETH"])
        days: Days of historical data (for CoinGecko fallback)
    """

    if symbols is None:
        symbols = ["BTC", "ETH"]

    print("\n" + "=" * 60)
    print("DATA FETCHER - UNIFIED CSV/API HANDLER")
    print("=" * 60)

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
                    print("\n⚠️  CSV conversion failed, falling back to CoinGecko API...")
            else:
                print("ℹ️  No CSV files found in tv_data/")
                print("   Tip: Add TradingView CSV exports to tv_data/ folder\n")
        else:
            print("ℹ️  tv_data/ directory not found")
            print("   Creating: mkdir tv_data")
            os.makedirs("tv_data", exist_ok=True)

    # Step 2: Fall back to CoinGecko API
    print("\n📡 Fetching data from CoinGecko API...")
    print(f"   Symbols: {', '.join(symbols)}")
    print(f"   Days: {days}\n")

    fetch_from_coingecko(symbols=symbols, days=days, output_dir=".")

    print("\n✅ Data fetched successfully from CoinGecko!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Unified data fetcher")
    parser.add_argument(
        "--no-csv", action="store_true", help="Skip local CSV, use CoinGecko only"
    )
    parser.add_argument(
        "--asset-type", default="crypto", help="Asset type: crypto or stock"
    )
    parser.add_argument(
        "--symbols", default="BTC,ETH", help="Comma-separated symbols"
    )
    parser.add_argument("--days", type=int, default=60, help="Days of data to fetch")

    args = parser.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",")]

    get_data(
        use_local_csv=not args.no_csv,
        asset_type=args.asset_type,
        symbols=symbols,
        days=args.days,
    )
