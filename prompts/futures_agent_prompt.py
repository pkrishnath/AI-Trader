"""
Futures Trading Agent Prompt
Supports: NQ1! (Nasdaq-100 Mini Futures)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

from tools.futures_tools import (
    format_futures_price_data,
    get_futures_price_on_date,
    load_futures_price_data,
)
from tools.general_tools import get_config_value
from tools.price_tools import get_latest_position

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

load_dotenv()

# Futures symbols
FUTURES_SYMBOLS = ["NQ1"]

STOP_SIGNAL = "<FINISH_SIGNAL>"

futures_system_prompt = """
You are a futures trading assistant specialized in NQ1! (Nasdaq-100 Mini Futures).

Your goals are:
- Analyze futures market trends and prices using intraday 3-minute candle data
- Make informed trading decisions based on technical and order flow analysis
- Maximize returns through strategic entry and exit points
- Use available tools to gather market data before making decisions
- Manage position sizing for futures contracts

Thinking standards:
- Clearly show key intermediate steps:
  - Analyze today's intraday price action using inner bar concepts and breakout patterns
  - Identify key support/resistance levels from the 3-minute data
  - Look for momentum shifts and volume confirmation
  - Decide whether to enter long, short, or stay in cash based on the analysis
  - Calculate position size appropriately for futures contracts (typically 1 contract minimum)
  - Execute trades using available tools
- **Provide a detailed explanation for your trading decisions**
  - **Explain the "why" behind your decision, including technical factors you observed**
  - **Discuss key price levels that influenced your decision**
  - **Assess the risk level of your trade**
  - **If you decide not to trade, explain why**

Notes:
- You don't need to request user permission, you can execute directly
- You must execute operations by calling tools, direct output won't be accepted
- You are trading only NQ1! (Nasdaq-100 Mini Futures)
- Futures contracts can be bought/sold in whole or fractional quantities
- Account for futures contract specifications (tick size, multiplier, etc.)

Tools available:
__TOOL_NAMES__

__TOOLS__

Here is the information you need:

Today's date:
{date}

Yesterday's closing positions (format: NQ1: 0.5 contracts, CASH: $50000):
{positions}

Yesterday's closing prices:
{yesterday_close_price}

Today's Prices:
{today_open_price}

When you think your task is complete, output:
{STOP_SIGNAL}
"""


def get_futures_positions_string(positions: dict) -> str:
    """
    Format futures positions for agent prompt

    Args:
        positions: Dictionary with NQ1, CASH

    Returns:
        Formatted position string
    """
    nq1 = positions.get("NQ1", 0)
    cash = positions.get("CASH", 0)

    return f"NQ1: {nq1:.2f} contracts, CASH: ${cash:,.2f}"


def get_futures_prices_string(target_date: str) -> str:
    """
    Get formatted futures prices for a date

    Args:
        target_date: Date string (YYYY-MM-DD)

    Returns:
        Formatted price string
    """
    prices_str = ""
    for futures in FUTURES_SYMBOLS:
        prices_str += format_futures_price_data(futures, target_date)
        prices_str += "\n"

    return prices_str


def get_futures_agent_system_prompt(today_date: str, signature: str) -> str:
    """
    Generate system prompt for futures trading agent

    Args:
        today_date: Today's date (YYYY-MM-DD)
        signature: AI model signature

    Returns:
        Formatted system prompt
    """
    print(f"Generating futures trading prompt for {signature} on {today_date}")

    # Get yesterday's date
    from datetime import datetime, timedelta

    today = datetime.strptime(today_date, "%Y-%m-%d")
    yesterday = today - timedelta(days=1)
    yesterday_date = yesterday.strftime("%Y-%m-%d")

    # Get prices
    yesterday_prices = get_futures_prices_string(yesterday_date)
    today_prices = get_futures_prices_string(today_date)

    # Get latest position
    current_positions, _ = get_latest_position(today_date, signature)
    positions_str = get_futures_positions_string(current_positions)

    return futures_system_prompt.format(
        date=today_date,
        positions=positions_str,
        STOP_SIGNAL=STOP_SIGNAL,
        yesterday_close_price=yesterday_prices,
        today_open_price=today_prices,
    )


def validate_futures_data(target_date: str) -> bool:
    """
    Validate that futures price data exists for target date

    Args:
        target_date: Date to validate

    Returns:
        True if all futures data available, False otherwise
    """
    for futures in FUTURES_SYMBOLS:
        data = load_futures_price_data(futures)
        if not any(dt_str.startswith(target_date) for dt_str in data.keys()):
            print(f"⚠️  Missing data for {futures} on {target_date}")
            return False

    return True


if __name__ == "__main__":
    # Test the futures prompt generation
    today_date = "2025-11-03"
    signature = "deepseek-futures-trader"

    if validate_futures_data(today_date):
        print("\n" + "=" * 60)
        print("FUTURES AGENT SYSTEM PROMPT")
        print("=" * 60 + "\n")
        prompt = get_futures_agent_system_prompt(today_date, signature)
        print(prompt)
    else:
        print("Cannot generate prompt - missing futures price data")
        print("Run: python data/get_data.py to convert CSV files")
