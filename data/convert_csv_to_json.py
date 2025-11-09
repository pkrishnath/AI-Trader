#!/usr/bin/env python3
"""
Convert TradingView CSV data to multiple JSON timeframes using Polars.
Creates both a daily and a 60-minute intraday JSON file from a single CSV.
"""

import json
import os
from pathlib import Path

import polars as pl


def convert_csv_to_json(csv_file, output_dir="data"):
    """
    Convert a single TradingView CSV file to two JSON files:
    1. A daily OHLC file for higher-timeframe bias.
    2. A 60-minute OHLC file for intraday analysis.

    Args:
        csv_file (str): Path to the input CSV file.
        output_dir (str): Directory to save the JSON files.
    """
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    # --- 1. Load and Prepare Data with Polars ---
    filename = Path(csv_file).stem
    symbol = filename.split("_")[0] if "_" in filename else filename

    print(f"Processing {csv_file} for symbol {symbol}...")

    # Read CSV and convert UNIX timestamp to datetime
    df = pl.read_csv(csv_file).with_columns(
        pl.from_epoch(pl.col("time"), time_unit="s").alias("datetime")
    )

    # --- 2. Resample to Daily Data ---
    df_daily = (
        df.group_by_dynamic("datetime", every="1d", period="1d", closed="left")
        .agg(
            pl.col("open").first().alias("open"),
            pl.col("high").max().alias("high"),
            pl.col("low").min().alias("low"),
            pl.col("close").last().alias("close"),
            pl.col("volume").sum().alias("volume"),
        )
        .sort("datetime")
    )

    # --- 3. Resample to 60-Minute Data ---
    df_hourly = (
        df.group_by_dynamic("datetime", every="60m", period="60m", closed="left")
        .agg(
            pl.col("open").first().alias("open"),
            pl.col("high").max().alias("high"),
            pl.col("low").min().alias("low"),
            pl.col("close").last().alias("close"),
            pl.col("volume").sum().alias("volume"),
        )
        .sort("datetime")
    )

    # --- 4. Convert to Dictionary and Save ---
    def to_ohlc_dict(dataframe: pl.DataFrame, time_col: str) -> dict:
        ohlc_dict = {}
        for row in dataframe.to_dicts():
            # Format timestamp as string key
            ts_key = row[time_col].strftime(
                "%Y-%m-%d"
                if time_col == "datetime" and row[time_col].hour == 0
                else "%Y-%m-%d %H:%M:%S"
            )
            ohlc_dict[ts_key] = {
                "date": ts_key,
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"],
            }
        return ohlc_dict

    daily_dict = to_ohlc_dict(df_daily, "datetime")
    hourly_dict = to_ohlc_dict(df_hourly, "datetime")

    # --- 5. Save Files ---
    os.makedirs(output_dir, exist_ok=True)
    asset_prefix = (
        "future_prices" if symbol.upper() in ["NQ1", "ES"] else "daily_prices"
    )

    # Save daily file
    daily_filename = f"{output_dir}/{asset_prefix}_{symbol}_daily.json"
    with open(daily_filename, "w") as f:
        json.dump(daily_dict, f, indent=2)
    print(f"✓ Saved DAILY data to {daily_filename} ({len(daily_dict)} records)")

    # Save intraday file
    intraday_filename = f"{output_dir}/{asset_prefix}_{symbol}.json"
    with open(intraday_filename, "w") as f:
        json.dump(hourly_dict, f, indent=2)
    print(f"✓ Saved 60-MINUTE data to {intraday_filename} ({len(hourly_dict)} records)")

    return daily_filename, intraday_filename


def convert_all_csv_files(csv_dir="tv_data", output_dir="data"):
    """
    Convert all CSV files in a directory to JSON.
    """
    if not os.path.exists(csv_dir):
        print(f"ℹ️  No CSV directory found: {csv_dir}")
        return []

    csv_files = list(Path(csv_dir).glob("*.csv"))
    if not csv_files:
        print(f"ℹ️  No CSV files found in {csv_dir}")
        return []

    print(f"\n{'='*60}\nCONVERTING CSV FILES TO JSON\n{'='*60}")
    print(f"Found {len(csv_files)} CSV files in {csv_dir}\n")

    converted_files = []
    for csv_file in csv_files:
        try:
            daily_file, intraday_file = convert_csv_to_json(str(csv_file), output_dir)
            converted_files.extend([daily_file, intraday_file])
            print()
        except Exception as e:
            print(f"✗ Error converting {csv_file}: {e}\n")

    print(
        f"{'='*60}\n✓ Conversion complete! {len(converted_files)} total files created.\n{'='*60}\n"
    )
    return converted_files


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        convert_csv_to_json(sys.argv[1])
    else:
        convert_all_csv_files()
