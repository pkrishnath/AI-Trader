"""
ICT Prompt Generator for the AI-Trader Agent
"""
import os
import sys
from datetime import datetime, timedelta

import toon

# Add project root to path to allow importing from other directories
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.price_tools import get_latest_position

# --- Constants ---
STOP_SIGNAL = "<FINISH_SIGNAL>"

# --- Main ICT System Prompt Template ---
ICT_SYSTEM_PROMPT = """
You are an advanced trading assistant specializing in the ICT (Inner Circle Trader) methodology.

Your goal is to execute high-probability trades by performing a top-down, multi-timeframe analysis.

---
### TRADING METHODOLOGY: TOP-DOWN ICT ANALYSIS
---

**1. Establish Weekly & Daily Bias (Higher Timeframe Analysis)**
- First, analyze the `Historical Daily Prices` data to understand the weekly and daily market structure.
- **Weekly Profile:** What is the trend over the last several weeks? Is price seeking higher highs (bullish) or lower lows (bearish)? Identify major weekly support and resistance levels or old highs/lows that could act as a magnet for price.
- **Daily Profile:** Zoom into the last several days. What is the immediate daily trend, and does it align with your weekly bias? Identify the "draw on liquidity" for the current day – where is price most likely to go today?
- **State your bias clearly** (e.g., "My higher timeframe bias is bullish, I expect price to take out last week's high").

**2. Execute Intraday Entries (Lower Timeframe - ICT 2022 Model)**
- Once you have a clear higher-timeframe bias, use the `Today's Intraday Prices` (e.g., 60-minute for stocks, 30-minute for crypto) to find a precise entry that aligns with your bias.
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
- `intraday_prices[96] {{datetime,open,high,low,close}}`: Intraday prices for finding entries.

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

class IctPromptGenerator:
    def __init__(self, asset_type: str, symbols: list):
        self.asset_type = asset_type
        self.symbols = symbols
        if self.asset_type == 'crypto':
            from tools.crypto_tools import load_crypto_daily_price_data, load_crypto_price_data
            self.daily_loader = load_crypto_daily_price_data
            self.intraday_loader = load_crypto_price_data
        elif self.asset_type == 'stock':
            from tools.price_tools import load_stock_daily_data, load_stock_intraday_data
            self.daily_loader = load_stock_daily_data
            self.intraday_loader = load_stock_intraday_data
        elif self.asset_type == 'futures':
            from tools.futures_tools import load_futures_daily_data, load_futures_intraday_data
            self.daily_loader = load_futures_daily_data
            self.intraday_loader = load_futures_intraday_data
        else:
            raise NotImplementedError(f"Asset type '{self.asset_type}' is not yet supported in the IctPromptGenerator.")

    def _positions_to_toon_list(self, positions: dict) -> list:
        positions_list = []
        for symbol, amount in positions.items():
            positions_list.append({"symbol": symbol, "amount": amount})
        return positions_list

    def _daily_data_to_toon_list(self, symbol: str) -> list:
        data = self.daily_loader(symbol)
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

    def _intraday_data_to_toon_list(self, symbol: str, target_date: str) -> list:
        data = self.intraday_loader(symbol)
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

    def _get_prices_string_toon(self, target_date: str = "", daily: bool = False) -> str:
        prices_str = ""
        for symbol in self.symbols:
            if daily:
                price_data = self._daily_data_to_toon_list(symbol)
                prices_str += f"--- {symbol} Daily Prices ---\n"
            else:
                price_data = self._intraday_data_to_toon_list(symbol, target_date)
                prices_str += f"--- {symbol} Intraday Prices for {target_date} ---\n"

            if price_data:
                prices_str += toon.dumps(price_data)
                prices_str += "\n\n"
            else:
                prices_str += f"No data available for {symbol} on {target_date}\n\n"
        return prices_str

    def generate_prompt(self, today_date: str, signature: str) -> str:
        print(f"Generating ICT prompt for {signature} on {today_date} (Asset: {self.asset_type})")

        today = datetime.strptime(today_date, "%Y-%m-%d")
        yesterday = today - timedelta(days=1)
        yesterday_date = yesterday.strftime("%Y-%m-%d")

        daily_prices_toon = self._get_prices_string_toon(daily=True)
        today_intraday_toon = self._get_prices_string_toon(target_date=today_date)
        yesterday_intraday_toon = self._get_prices_string_toon(target_date=yesterday_date)

        current_positions, _ = get_latest_position(today_date, signature)
        if not current_positions:
            current_positions = {"CASH": 10000.0}
        positions_toon_str = toon.dumps(self._positions_to_toon_list(current_positions))

        return ICT_SYSTEM_PROMPT.format(
            date=today_date,
            positions=positions_toon_str,
            daily_prices=daily_prices_toon,
            intraday_prices=today_intraday_toon,
            yesterday_intraday_prices=yesterday_intraday_toon,
            STOP_SIGNAL=STOP_SIGNAL,
        )
