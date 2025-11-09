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

# --- Generic ICT System Prompt ---
ICT_GENERIC_PROMPT = """
You are a cryptocurrency trading assistant specialized in Bitcoin (BTC) and Ethereum (ETH).

Your goals are to analyze market trends and execute trades to maximize portfolio returns.

Thinking standards:
- Analyze today's prices and market conditions using Inner Circle Trader (ICT) concepts. Your analysis must be detailed and include specific price levels:
    - **Liquidity Pools & Order Blocks:** Identify key areas of liquidity and order blocks.
    - **Fair Value Gaps (FVGs):** Look for FVGs and quantify their size.
    - **Market Structure:** Analyze the market structure, including breaks of structure and changes of character.
- Decide which assets to buy/sell and in what quantities.
- Provide a detailed explanation for your trading decisions.

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

**Historical Daily Prices (for HTF Bias):**
{daily_prices}

**Today's Intraday Prices (for Entry):**
{intraday_prices}

**Yesterday's Intraday Prices (for context):**
{yesterday_intraday_prices}

When you think your task is complete, output:
{STOP_SIGNAL}
"""

# --- ICT 2022 Model System Prompt ---
ICT_2022_MODEL_PROMPT = """
You are an advanced trading assistant specializing in the ICT (Inner Circle Trader) methodology.
Your goal is to execute high-probability trades by performing a top-down, multi-timeframe analysis.

---
### TRADING METHODOLOGY: TOP-DOWN ICT ANALYSIS (2022 Model)
---

**1. Establish Weekly & Daily Bias (Higher Timeframe Analysis)**
- First, analyze the `Historical Daily Prices` to determine the weekly and daily market structure and directional bias.
- **State your bias clearly** (e.g., "My higher timeframe bias is bullish, I expect price to take out last week's high").

**2. Execute Intraday Entries (Lower Timeframe - ICT 2022 Model)**
- Use the `Today's Intraday Prices` to find a precise entry that aligns with your higher-timeframe bias.
- **Crucial Rule:** Only take trades in the direction of your established weekly/daily bias.
- Follow these steps to find an entry:
    a. **Liquidity Grab:** Wait for the price to run above a recent high (if bearish) or below a recent low (if bullish).
    b. **Market Structure Shift (MSS):** After the grab, watch for a strong reversal that breaks a recent swing point.
    c. **Entry Point (FVG):** Identify a "Fair Value Gap" (FVG) created during the MSS. This is your entry zone.
    d. **Enter:** Execute your trade when the price retraces back into the FVG.
    e. **Target:** Your profit target should be an opposing liquidity pool.

**3. Explain Your Rationale**
- You must provide a detailed explanation for every trade, referencing the specific ICT concepts and price levels.
- If you do not trade, explain why.

---
### DATA FORMAT (TOON)
---
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
    def __init__(self, asset_type: str, symbols: list, model_type: str = "generic"):
        self.asset_type = asset_type
        self.symbols = symbols
        self.model_type = model_type

        if self.asset_type == "crypto":
            from tools.crypto_tools import load_crypto_daily_price_data, load_crypto_price_data
            self.daily_loader = load_crypto_daily_price_data
            self.intraday_loader = load_crypto_price_data
        elif self.asset_type == "stock":
            from tools.price_tools import load_stock_daily_data, load_stock_intraday_data
            self.daily_loader = load_stock_daily_data
            self.intraday_loader = load_stock_intraday_data
        elif self.asset_type == "futures":
            from tools.futures_tools import load_futures_daily_data, load_futures_intraday_data
            self.daily_loader = load_futures_daily_data
            self.intraday_loader = load_futures_intraday_data
        else:
            raise NotImplementedError(f"Asset type '{self.asset_type}' is not yet supported.")

    def _positions_to_toon_list(self, positions: dict) -> list:
        # ... (implementation is correct)
        pass

    def _daily_data_to_toon_list(self, symbol: str) -> list:
        # ... (implementation is correct)
        pass

    def _intraday_data_to_toon_list(self, symbol: str, target_date: str) -> list:
        # ... (implementation is correct)
        pass

    def _get_prices_string_toon(self, target_date: str = "", daily: bool = False) -> str:
        # ... (implementation is correct)
        pass

    def generate_prompt(self, today_date: str, signature: str) -> str:
        print(f"Generating ICT prompt for {signature} on {today_date} (Asset: {self.asset_type}, Model: {self.model_type})")

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

        if self.model_type == "2022_model":
            prompt_template = ICT_2022_MODEL_PROMPT
        else:
            prompt_template = ICT_GENERIC_PROMPT

        return prompt_template.format(
            date=today_date,
            positions=positions_toon_str,
            daily_prices=daily_prices_toon,
            intraday_prices=today_intraday_toon,
            yesterday_intraday_prices=yesterday_intraday_toon,
            STOP_SIGNAL=STOP_SIGNAL,
        )
