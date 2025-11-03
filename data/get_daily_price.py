import os

import requests
from dotenv import load_dotenv

load_dotenv()
import json

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


def get_daily_price(SYMBOL: str):
    FUNCTION = "TIME_SERIES_DAILY"
    OUTPUTSIZE = "compact"
    APIKEY = os.getenv("ALPHAADVANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function={FUNCTION}&symbol={SYMBOL}&outputsize={OUTPUTSIZE}&apikey={APIKEY}"
    r = requests.get(url)
    data = r.json()
    print(data)
    if data.get("Note") is not None or data.get("Information") is not None:
        print(f"Error")
        return
    with open(f"./daily_prices_{SYMBOL}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    if SYMBOL == "QQQ":
        with open(f"./Adaily_prices_{SYMBOL}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Fetch daily stock prices.')
    parser.add_argument('--symbols', type=str, help='Comma-separated list of stock symbols to fetch.')
    args = parser.parse_args()

    if args.symbols:
        symbols_to_fetch = [s.strip().upper() for s in args.symbols.split(',')]
    else:
        symbols_to_fetch = all_nasdaq_100_symbols

    for symbol in symbols_to_fetch:
        get_daily_price(symbol)

    if "QQQ" not in symbols_to_fetch:
        get_daily_price("QQQ")
