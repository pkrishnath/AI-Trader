#!/usr/bin/env python3
"""
Convert TradingView CSV data to JSON format for crypto/stock trading
Supports both 3-minute and hourly CSV data from TradingView
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path


def convert_csv_to_json(csv_file, output_dir="data"):
    """
    Convert TradingView CSV file to JSON format

    Detects asset type (crypto vs futures) and saves with appropriate prefix:
    - Crypto: crypto_prices_BTC.json
    - Futures: future_prices_NQ1.json

    Args:
        csv_file: Path to CSV file (e.g., "tv_data/NQ1_MINI_CME_3min.csv")
        output_dir: Directory to save JSON output

    Returns:
        Path to saved JSON file
    """

    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    # Extract symbol from filename (e.g., "NQ1_MINI_CME_3min.csv" -> "NQ1")
    filename = Path(csv_file).stem  # Get filename without extension
    parts = filename.split('_')
    symbol = parts[0] if parts else "UNKNOWN"

    os.makedirs(output_dir, exist_ok=True)

    # Detect asset type: futures contracts (NQ1!, ES, MES, etc.) vs crypto (BTC, ETH, etc.)
    futures_symbols = ["NQ1", "ES", "MES", "MNQ", "YM", "GC", "CL", "ZB", "ZS", "ZC", "ZW"]
    crypto_symbols = ["BTC", "ETH", "SOL", "ADA", "XRP", "DOGE"]

    is_futures = symbol.upper() in futures_symbols
    asset_type = "futures" if is_futures else "crypto"

    ohlc_data = {}

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                # Get timestamp (Unix timestamp in seconds)
                timestamp = int(row['time'])

                # Convert to datetime
                dt_object = datetime.fromtimestamp(timestamp)
                datetime_str = dt_object.strftime("%Y-%m-%d %H:%M:%S")

                # Extract OHLC values
                ohlc_data[datetime_str] = {
                    "date": datetime_str,
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": 0,  # Not provided in TradingView CSV
                }
            except (KeyError, ValueError) as e:
                print(f"⚠️  Skipping row: {e}")
                continue

    if not ohlc_data:
        raise ValueError(f"No valid OHLC data found in {csv_file}")

    # Save to JSON with appropriate prefix
    prefix = "future_prices" if is_futures else "crypto_prices"
    output_file = f"{output_dir}/{prefix}_{symbol}.json"

    with open(output_file, 'w') as f:
        json.dump(ohlc_data, f, indent=2)

    asset_label = f"({asset_type.upper()})"
    print(f"✓ Converted {csv_file} to {output_file} {asset_label}")
    print(f"  Total records: {len(ohlc_data)}")
    print(f"  Date range: {min(ohlc_data.keys())} to {max(ohlc_data.keys())}")

    return output_file


def convert_all_csv_files(csv_dir="tv_data", output_dir="data"):
    """
    Convert all CSV files in a directory to JSON

    Args:
        csv_dir: Directory containing CSV files
        output_dir: Directory to save JSON output
    """

    if not os.path.exists(csv_dir):
        print(f"ℹ️  No CSV directory found: {csv_dir}")
        return []

    csv_files = list(Path(csv_dir).glob("*.csv"))

    if not csv_files:
        print(f"ℹ️  No CSV files found in {csv_dir}")
        return []

    print(f"\n{'='*60}")
    print(f"CONVERTING CSV FILES TO JSON")
    print(f"{'='*60}")
    print(f"Found {len(csv_files)} CSV files in {csv_dir}\n")

    converted_files = []

    for csv_file in csv_files:
        try:
            json_file = convert_csv_to_json(str(csv_file), output_dir)
            converted_files.append(json_file)
            print()
        except Exception as e:
            print(f"✗ Error converting {csv_file}: {e}\n")

    print(f"{'='*60}")
    print(f"✓ Conversion complete! {len(converted_files)} files created")
    print(f"{'='*60}\n")

    return converted_files


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Convert specific file: python convert_csv_to_json.py tv_data/BTC_USDT.csv
        csv_file = sys.argv[1]
        convert_csv_to_json(csv_file)
    else:
        # Convert all CSV files in tv_data/
        convert_all_csv_files()
