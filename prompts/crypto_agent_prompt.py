"""
Cryptocurrency Trading Agent Prompt
Supports: Bitcoin (BTC) and Ethereum (ETH)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import toon
from dotenv import load_dotenv

from tools.crypto_tools import (
    load_crypto_daily_price_data,
    load_crypto_price_data,
)
from tools.general_tools import get_config_value
from tools.price_tools import get_latest_position

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

load_dotenv()

# Cryptocurrency symbols
CRYPTO_SYMBOLS = ["BTC", "ETH"]

STOP_SIGNAL = "<FINISH_SIGNAL>"

crypto_system_prompt = """
You are an advanced cryptocurrency trading assistant specializing in the ICT (Inner Circle Trader) methodology.

Your goal is to execute high-probability trades by performing a top-down analysis, starting from a high-level weekly bias and drilling down to an intraday entry model.

---
### TRADING METHODOLOGY: TOP-DOWN ICT ANALYSIS
---

**1. Establish Weekly & Daily Bias (Higher Timeframe Analysis)**
- First, analyze the `Historical Daily Prices` data to understand the weekly and daily market structure.
- **Weekly Profile:** What is the trend over the last several weeks? Is price seeking higher highs (bullish) or lower lows (bearish)? Identify major weekly support/resistance levels or old highs/lows that could act as a magnet for price.
- **Daily Profile:** Zoom into the last several days. What is the immediate daily trend? Does it align with your weekly bias? Identify the "draw on liquidity" for the current day – where is price most likely to go today?
- **State your bias clearly** (e.g., "My higher timeframe bias is bullish, I expect price to take out last week's high").

**2. Execute Intraday Entries (Lower Timeframe - ICT 2022 Model)**
- Once you have a clear higher-timeframe bias, use the `Today's Intraday Prices` (30-minute data) to find a precise entry that aligns with your bias.
- **Crucial Rule:** Only take trades in the direction of your established weekly/daily bias. If you are bullish, only look for long (buy) setups. If you are bearish, only look for short (sell) setups.
- Follow these steps to find an entry:
    a. **Wait for a Liquidity Grab:** Wait for the price to run above a recent high (if bearish) or below a recent low (if bullish). This is the "Judas Swing".
    b. **Look for a Market Structure Shift (MSS):** After the liquidity grab, watch for a strong reversal that breaks a recent swing point, signaling a change in direction.
    c. **Identify the Entry Point (FVG):** This reversal should create a "Fair Value Gap" (FVG) or "imbalance". This FVG is your entry zone.
    d. **Enter the Trade:** When the price retraces back into the FVG, execute your trade (buy or sell).
    e. **Set Profit Target:** Your target should be an opposing liquidity pool (e.g., if you buy, target a recent high where sell-side liquidity is resting).

**3. Explain Your Rationale**
- You must provide a detailed explanation for every trade, referencing the specific ICT concepts, price levels, and timeframes you analyzed.
- If you do not trade, explain why (e.g., "The intraday price action did not provide a valid entry setup that aligned with my bullish daily bias.").

---
### DATA FORMAT (TOON)
---
Price and position data is in the compact TOON format.
- `positions[3] {{symbol,amount}}`: Your current holdings.
- `daily_prices[180] {{date,open,high,low,close}}`: Daily prices for establishing bias.
- `intraday_prices[96] {{datetime,open,high,low,close}}`: 30-minute prices for finding entries.

---
### AVAILABLE INFORMATION
---

**Today's Date:** {date}
**Current Positions:**
{positions}

**Historical Daily Prices (for Weekly/Daily Bias):**
{daily_prices}

**Today's Intraday Prices (for Entry):**
{intraday_prices}

**Yesterday's Intraday Prices (for context):**
{yesterday_intraday_prices}

When you think your task is complete, output:
{STOP_SIGNAL}
"""


def crypto_positions_to_toon_list(positions: dict) -> list:
    """Converts a crypto positions dictionary to a list of dictionaries for TOON."""
    positions_list = []
    for symbol, amount in positions.items():
        positions_list.append({"symbol": symbol, "amount": amount})
    return positions_list


def get_crypto_intraday_data_for_toon(crypto_symbol: str, target_date: str) -> list:
    """Gets crypto intraday price data as a list of dictionaries for TOON conversion."""
    data = load_crypto_price_data(crypto_symbol)
    price_list = []
    for dt_str, price_data in sorted(data.items()):
        if dt_str.startswith(target_date):
            price_list.append(
                {
                    "datetime": dt_str,
                    "open": price_data.get("open"),
                    "high": price_data.get("high"),
                    "low": price_data.get("low"),
                    "close": price_data.get("close"),
                }
            )
    return price_list


def get_crypto_daily_data_for_toon(crypto_symbol: str) -> list:
    """Gets crypto daily price data as a list of dictionaries for TOON conversion."""
    data = load_crypto_daily_price_data(crypto_symbol)
    price_list = []
    for date_str, price_data in sorted(data.items()):
        price_list.append(
            {
                "date": date_str,
                "open": price_data.get("open"),
                "high": price_data.get("high"),
                "low": price_data.get("low"),
                "close": price_data.get("close"),
            }
        )
    return price_list


def get_crypto_prices_string_toon(target_date: str, daily: bool = False) -> str:
    """Gets formatted crypto prices for a date in TOON format."""
    prices_str = ""
    for crypto in CRYPTO_SYMBOLS:
        if daily:
            price_data = get_crypto_daily_data_for_toon(crypto)
            prices_str += f"--- {crypto} Daily Prices ---\n"
        else:
            price_data = get_crypto_intraday_data_for_toon(crypto, target_date)
            prices_str += f"--- {crypto} Intraday Prices for {target_date} ---\n"

        if price_data:
            prices_str += toon.dumps(price_data)
            prices_str += "\n\n"
        else:
            prices_str += f"No data available for {crypto} on {target_date}\n\n"
    return prices_str


def get_crypto_agent_system_prompt(today_date: str, signature: str) -> str:
    """
    Generate system prompt for crypto trading agent.
    """
    print(f"Generating crypto trading prompt for {signature} on {today_date}")

    # Get yesterday's date
    today = datetime.strptime(today_date, "%Y-%m-%d")
    yesterday = today - timedelta(days=1)
    yesterday_date = yesterday.strftime("%Y-%m-%d")

    # Load and format all data types
    daily_prices_toon = get_crypto_prices_string_toon("", daily=True)
    today_intraday_toon = get_crypto_prices_string_toon(today_date)
    yesterday_intraday_toon = get_crypto_prices_string_toon(yesterday_date)

    # Get latest position and convert to TOON
    current_positions, _ = get_latest_position(today_date, signature)
    if not current_positions:
        current_positions = {"CASH": 10000.0} # Default starting position
    positions_toon_str = toon.dumps(crypto_positions_to_toon_list(current_positions))

    return crypto_system_prompt.format(
        date=today_date,
        positions=positions_toon_str,
        daily_prices=daily_prices_toon,
        intraday_prices=today_intraday_toon,
        yesterday_intraday_prices=yesterday_intraday_toon,
        STOP_SIGNAL=STOP_SIGNAL,
    )


def validate_crypto_data(target_date: str) -> bool:
    """
    Validate that crypto price data exists for target date.
    """
    for crypto in CRYPTO_SYMBOLS:
        # Check for both intraday and daily files
        if not os.path.exists(f"data/crypto_prices_{crypto}.json"):
            print(f"⚠️  Missing intraday data for {crypto}")
            return False
        if not os.path.exists(f"data/crypto_prices_{crypto}_daily.json"):
            print(f"⚠️  Missing daily data for {crypto}")
            return False
    return True


if __name__ == "__main__":
    # Test the crypto prompt generation
    today_date = "2025-11-09"
    signature = "deepseek-crypto-trader"

    if validate_crypto_data(today_date):
        print("\n" + "=" * 60)
        print("CRYPTO AGENT SYSTEM PROMPT (Multi-Timeframe ICT)")
        print("=" * 60 + "\n")
        prompt = get_crypto_agent_system_prompt(today_date, signature)
        print(prompt)
    else:
        print("Cannot generate prompt - missing crypto price data")
        print("Run: python data/get_crypto_prices.py")
