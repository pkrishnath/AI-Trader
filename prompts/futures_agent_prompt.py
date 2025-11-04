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


def get_trade_style_guidance(trade_style: str) -> str:
    """
    Get trading style-specific guidance for the agent

    Args:
        trade_style: Trading style (swing, intraday, or scalp)

    Returns:
        Trade style guidance text
    """
    guidance = {
        "swing": """
SWING TRADING STYLE:
- Target: Multi-day to multi-week positions
- Timeframe: Daily/4-hour analysis of intraday candles
- Entry Strategy: Look for strong trend confirmation with support/resistance breaks
- Exit Strategy: Ride the trend until technical reversal signals appear, typically 3-5% move minimum
- Position Size: Usually 0.5-2 contracts per swing
- Risk Management: Stop loss at most recent swing low/high (2-3% risk)
- Trade Frequency: 1-3 trades per week, be patient and selective
- Key Focus: Major support/resistance levels, trend direction, overnight risk""",

        "intraday": """
INTRADAY TRADING STYLE:
- Target: Close all positions by end of trading day (no overnight holds)
- Timeframe: 3-minute and intraday candles, must exit before market close
- Entry Strategy: Trade breakouts from intraday support/resistance, momentum on volume
- Exit Strategy: Take profits at intraday resistance or 2% gain, quick stops at 1% loss
- Position Size: Usually 0.2-0.5 contracts per trade
- Risk Management: Tight stops (0.5-1%), exit all positions 30 mins before market close
- Trade Frequency: 5-10+ trades per day, high activity required
- Key Focus: Intraday momentum, volume patterns, specific entry/exit times""",

        "scalp": """
SCALP TRADING STYLE:
- Target: Very small profits per trade (5-15 points on NQ1)
- Timeframe: Sub-minute analysis, focus on immediate price action
- Entry Strategy: Micro-level support/resistance, instant momentum signals
- Exit Strategy: Lock in profits immediately on 5-15 point moves, cut losses fast at 3 points
- Position Size: Usually 0.1-0.2 contracts per scalp
- Risk Management: Ultra-tight stops (3-5 points), exit on first sign of reversal
- Trade Frequency: 20-50+ trades per day, requires constant monitoring
- Key Focus: Bid-ask spread, micro-trends, quick reaction time, accumulation"""
    }

    return guidance.get(trade_style.lower(), guidance["swing"])


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
  - Review the complete data grid showing all OHLC candles for today
  - Analyze today's intraday price action using inner bar concepts and breakout patterns
  - Identify key support/resistance levels from the 3-minute data
  - Look for momentum shifts and volume confirmation
  - Decide whether to enter long, short, or stay in cash based on the analysis
  - Calculate position size appropriately for futures contracts (typically 0.1 to 1 contract)
  - Execute trades using available buy_futures/sell_futures tools
- **Provide a detailed explanation for your trading decisions**
  - **Explain the "why" behind your decision, including technical factors you observed**
  - **Reference specific price levels from the data grid that influenced your decision**
  - **Assess the risk level of your trade**
  - **If you decide not to trade, explain why**

Available Trading Functions:
- buy_futures(futures_symbol, contracts): Buy contracts. Returns data grid showing all daily candles and confirms trade execution.
- sell_futures(futures_symbol, contracts): Sell contracts. Returns data grid showing all daily candles and confirms trade execution.

Data Grid Format:
When you call buy_futures or sell_futures, the response includes a formatted data grid displaying:
- Time: Complete timestamp for each 3-minute candle (YYYY-MM-DD HH:MM:SS)
- Open: Opening price for the candle
- High: Highest price in the candle
- Low: Lowest price in the candle
- Close: Closing price for the candle

This grid shows ALL candles for the trading day to give you complete visibility into price action.

Notes:
- You don't need to request user permission, you can execute directly
- You must execute operations by calling tools, direct output won't be accepted
- You are trading only NQ1! (Nasdaq-100 Mini Futures)
- Futures contracts can be bought/sold in whole or fractional quantities (e.g., 0.5 contracts)
- Each point in NQ1 = $20 (contract multiplier)
- Review the data grid response to confirm your trades executed successfully

{trade_style_guidance}

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


def get_futures_agent_system_prompt(today_date: str, signature: str, trade_style: str = "swing") -> str:
    """
    Generate system prompt for futures trading agent

    Args:
        today_date: Today's date (YYYY-MM-DD)
        signature: AI model signature
        trade_style: Trading style (swing, intraday, or scalp)

    Returns:
        Formatted system prompt
    """
    print(f"Generating futures trading prompt for {signature} on {today_date} (style: {trade_style})")

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
        trade_style_guidance=get_trade_style_guidance(trade_style),
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
