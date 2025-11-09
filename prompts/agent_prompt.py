"""
Stock Trading Agent Prompt
This file now uses the generic IctPromptGenerator.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.general_tools import get_config_value
from tools.ict_prompt_generator import IctPromptGenerator

# Default stock symbols
all_nasdaq_100_symbols = [
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


def get_agent_system_prompt(today_date: str, signature: str) -> str:
    """
    Generate system prompt for the stock trading agent using the generic ICT generator.
    """
    # Instantiate the generator for the 'stock' asset type
    prompt_generator = IctPromptGenerator(
        asset_type="stock", symbols=all_nasdaq_100_symbols
    )

    # Generate and return the prompt
    return prompt_generator.generate_prompt(today_date, signature)


if __name__ == "__main__":
    # Test the stock prompt generation
    today_date = "2025-11-09"
    signature = "deepseek-stock-trader"

    print("\n" + "=" * 60)
    print("STOCK AGENT SYSTEM PROMPT (via Generic ICT Generator)")
    print("=" * 60 + "\n")
    prompt = get_agent_system_prompt(today_date, signature)
    print(prompt)
