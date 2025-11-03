"""
Cryptocurrency Trading Agent Prompt
Supports: Bitcoin (BTC) and Ethereum (ETH)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv

from tools.crypto_tools import (
    SUPPORTED_CRYPTOS,
    format_crypto_price_data,
    get_crypto_latest_price,
    get_crypto_price_on_date,
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
You are a cryptocurrency trading assistant specialized in Bitcoin (BTC) and Ethereum (ETH).

Your goals are:
- Analyze cryptocurrency market trends and prices
- Make informed trading decisions based on technical and fundamental analysis
- Maximize portfolio returns through strategic buying and selling
- Use available tools to gather market data before making decisions

Thinking standards:
- Clearly show key intermediate steps:
  - Read current positions and available cash
  - Analyze today's prices and market conditions using Inner Circle Trader (ICT) concepts (liquidity pools, order blocks, fair value gaps, market structure).
  - Decide which cryptos to buy/sell and quantities
  - Execute trades using available tools
- **Provide a detailed explanation for your trading decisions. This explanation should be included in your final output and will be used for backtesting and analysis.**
  - **Explain the "why" behind your decision, including the factors you considered.**
  - **Explicitly state which ICT concepts you applied in your analysis.**
  - **Discuss the risk assessment and any mitigating factors.**
  - **If you decide not to trade, explain why.**

Notes:
- You don't need to request user permission, you can execute directly
- You must execute operations by calling tools, direct output won't be accepted
- You are trading only BTC (Bitcoin) and ETH (Ethereum)
- Each crypto can be bought/sold in fractional amounts

Tools available:
__TOOL_NAMES__

__TOOLS__

Here is the information you need:

Today's date:
{date}

Yesterday's closing positions (format: BTC: 0.5, ETH: 2.0, CASH: $5000):
{positions}

Yesterday's closing prices:
{yesterday_close_price}

Today's opening prices:
{today_open_price}

When you think your task is complete, output:
{STOP_SIGNAL}
"""


def get_crypto_positions_string(positions: dict) -> str:
    """
    Format crypto positions for agent prompt

    Args:
        positions: Dictionary with BTC, ETH, CASH

    Returns:
        Formatted position string
    """
    btc = positions.get("BTC", 0)
    eth = positions.get("ETH", 0)
    cash = positions.get("CASH", 0)

    return f"BTC: {btc:.6f}, ETH: {eth:.6f}, CASH: ${cash:,.2f}"


def get_crypto_prices_string(target_date: str) -> str:
    """
    Get formatted crypto prices for a date

    Args:
        target_date: Date string (YYYY-MM-DD)

    Returns:
        Formatted price string
    """
    prices_str = ""
    for crypto in CRYPTO_SYMBOLS:
        prices_str += format_crypto_price_data(crypto, target_date)
        prices_str += "\n"

    return prices_str


def get_crypto_agent_system_prompt(today_date: str, signature: str) -> str:
    """
    Generate system prompt for crypto trading agent

    Args:
        today_date: Today's date (YYYY-MM-DD)
        signature: AI model signature

    Returns:
        Formatted system prompt
    """
    print(f"Generating crypto trading prompt for {signature} on {today_date}")

    # Get yesterday's date
    from datetime import datetime, timedelta

    today = datetime.strptime(today_date, "%Y-%m-%d")
    yesterday = today - timedelta(days=1)
    yesterday_date = yesterday.strftime("%Y-%m-%d")

    # Get prices
    yesterday_prices = get_crypto_prices_string(yesterday_date)
    today_prices = get_crypto_prices_string(today_date)

    # Get latest position
    current_positions, _ = get_latest_position(today_date, signature)
    positions_str = get_crypto_positions_string(current_positions)

    return crypto_system_prompt.format(
        date=today_date,
        positions=positions_str,
        STOP_SIGNAL=STOP_SIGNAL,
        yesterday_close_price=yesterday_prices,
        today_open_price=today_prices,
    )


def validate_crypto_data(target_date: str) -> bool:
    """
    Validate that crypto price data exists for target date

    Args:
        target_date: Date to validate

    Returns:
        True if all crypto data available, False otherwise
    """
    for crypto in CRYPTO_SYMBOLS:
        data = load_crypto_price_data(crypto)
        if target_date not in data:
            print(f"⚠️  Missing data for {crypto} on {target_date}")
            return False

    return True


if __name__ == "__main__":
    # Test the crypto prompt generation
    today_date = "2025-10-15"
    signature = "gpt-5"

    if validate_crypto_data(today_date):
        print("\n" + "=" * 60)
        print("CRYPTO AGENT SYSTEM PROMPT")
        print("=" * 60 + "\n")
        prompt = get_crypto_agent_system_prompt(today_date, signature)
        print(prompt)
    else:
        print("Cannot generate prompt - missing crypto price data")
        print("Run: python data/get_crypto_prices.py")
