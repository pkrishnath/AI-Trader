import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import toon
from dotenv import load_dotenv

from tools.general_tools import get_config_value
from tools.price_tools import (
    get_open_prices,
    get_today_init_position,
    get_yesterday_date,
    get_yesterday_open_and_close_price,
    get_yesterday_profit,
)

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

load_dotenv()

all_nasdaq_100_symbols = [
    "NQ1!",
    "NVDA",
    "MSFT",
    "AAPL",
    "GOOG",
    "GOOGL",
    "AMZN",
    "META",
    "AVGO",
    "TSLA",
    "NFLX",
    "PLTR",
    "COST",
    "ASML",
    "AMD",
    "CSCO",
    "AZN",
    "TMUS",
    "MU",
    "LIN",
    "PEP",
    "SHOP",
    "APP",
    "INTU",
    "AMAT",
    "LRCX",
    "PDD",
    "QCOM",
    "ARM",
    "INTC",
    "BKNG",
    "AMGN",
    "TXN",
    "ISRG",
    "GILD",
    "KLAC",
    "PANW",
    "ADBE",
    "HON",
    "CRWD",
    "CEG",
    "ADI",
    "ADP",
    "DASH",
    "CMCSA",
    "VRTX",
    "MELI",
    "SBUX",
    "CDNS",
    "ORLY",
    "SNPS",
    "MSTR",
    "MDLZ",
    "ABNB",
    "MRVL",
    "CTAS",
    "TRI",
    "MAR",
    "MNST",
    "CSX",
    "ADSK",
    "PYPL",
    "FTNT",
    "AEP",
    "WDAY",
    "REGN",
    "ROP",
    "NXPI",
    "DDOG",
    "AXON",
    "ROST",
    "IDXX",
    "EA",
    "PCAR",
    "FAST",
    "EXC",
    "TTWO",
    "XEL",
    "ZS",
    "PAYX",
    "WBD",
    "BKR",
    "CPRT",
    "CCEP",
    "FANG",
    "TEAM",
    "CHTR",
    "KDP",
    "MCHP",
    "GEHC",
    "VRSK",
    "CTSH",
    "CSGP",
    "KHC",
    "ODFL",
    "DXCM",
    "TTD",
    "ON",
    "BIIB",
    "LULU",
    "CDW",
    "GFS",
]

STOP_SIGNAL = "<FINISH_SIGNAL>"

agent_system_prompt = """
You are a stock fundamental analysis trading assistant.

Your goals are:
- Think and reason by calling available tools.
- You need to think about the prices of various stocks and their returns.
- Your long-term goal is to maximize returns through this portfolio.
- Before making decisions, gather as much information as possible through search tools to aid decision-making.

Thinking standards:
- Clearly show key intermediate steps:
  - Read input of yesterday's positions and today's prices
  - Update valuation and adjust weights for each target (if strategy requires)
- **Provide a detailed explanation for your trading decisions. This explanation should be included in your final output and will be used for backtesting and analysis.**
  - **Explain the "why" behind your decision, including the factors you considered.**
  - **Discuss the risk assessment and any mitigating factors.**
  - **If you decide not to trade, explain why.**

Data Format (TOON):
The positions and price data are provided in the TOON format, a compact way to represent tabular data.
It looks like this:
positions[101] {symbol,shares}
  AAPL 10.0
  MSFT 5.0
  CASH 7500.25
  ...
The first line `positions[101]` indicates the number of assets.
The second line `{{symbol,shares}}` defines the columns.
Each subsequent line is an asset and the number of shares you hold. CASH is also included.

Notes:
- You don't need to request user permission during operations, you can execute directly
- You must execute operations by calling tools, directly output operations will not be accepted

Here is the information you need:

Today's date:
{date}

Yesterday's closing positions:
{positions}

Yesterday's closing prices:
{yesterday_close_price}

Today's buying prices:
{today_buy_price}

When you think your task is complete, output
{STOP_SIGNAL}
"""


def price_dict_to_toon_list(price_dict: Dict[str, Optional[float]]) -> List[Dict]:
    """Converts a price dictionary to a list of dictionaries for TOON."""
    price_list = []
    for key, value in price_dict.items():
        if key.endswith("_price"):
            symbol = key[: -len("_price")]
            price_list.append({"symbol": symbol, "price": value})
    return price_list


def positions_dict_to_toon_list(positions_dict: Dict[str, float]) -> List[Dict]:
    """Converts a positions dictionary to a list of dictionaries for TOON."""
    positions_list = []
    for symbol, shares in positions_dict.items():
        positions_list.append({"symbol": symbol, "shares": shares})
    return positions_list


def get_agent_system_prompt(today_date: str, signature: str) -> str:
    print(f"signature: {signature}")
    print(f"today_date: {today_date}")
    # Get yesterday's buy and sell prices
    yesterday_buy_prices, yesterday_sell_prices = get_yesterday_open_and_close_price(
        today_date, all_nasdaq_100_symbols
    )
    today_buy_price = get_open_prices(today_date, all_nasdaq_100_symbols)
    today_init_position = get_today_init_position(today_date, signature)
    yesterday_profit = get_yesterday_profit(
        today_date, yesterday_buy_prices, yesterday_sell_prices, today_init_position
    )

    # Convert data to TOON format
    positions_toon_str = toon.dumps(positions_dict_to_toon_list(today_init_position))
    yesterday_close_price_toon_str = toon.dumps(
        price_dict_to_toon_list(yesterday_sell_prices)
    )
    today_buy_price_toon_str = toon.dumps(price_dict_to_toon_list(today_buy_price))

    return agent_system_prompt.format(
        date=today_date,
        positions=positions_toon_str,
        STOP_SIGNAL=STOP_SIGNAL,
        yesterday_close_price=yesterday_close_price_toon_str,
        today_buy_price=today_buy_price_toon_str,
        yesterday_profit=yesterday_profit,
    )


if __name__ == "__main__":
    today_date = get_config_value("TODAY_DATE")
    signature = get_config_value("SIGNATURE")
    if signature is None:
        raise ValueError("SIGNATURE environment variable is not set")
    print(get_agent_system_prompt(today_date, signature))
