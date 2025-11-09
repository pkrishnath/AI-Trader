import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

mcp = FastMCP("LocalPrices")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """
    Health check endpoint.
    """
    return PlainTextResponse("OK")


def _workspace_data_path(filename: str) -> Path:
    base_dir = Path(__file__).resolve().parents[1]
    return base_dir / "data" / filename


def _validate_date(date_str: str) -> None:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("date must be in YYYY-MM-DD format") from exc


@mcp.tool()
def get_price_local(symbol: str, date: str) -> Dict[str, Any]:
    """
    Read OHLCV data for specified stock and date.
    Get historical information for specified stock.

    Args:
        symbol: Stock symbol, e.g. 'IBM' or '600243.SHH'.
        date: Date in 'YYYY-MM-DD' format.

    Returns:
        Dictionary containing symbol, date and ohlcv data.
    """
    filename = "merged.jsonl"
    try:
        _validate_date(date)
    except ValueError as e:
        return {"error": str(e), "symbol": symbol, "date": date}

    data_path = _workspace_data_path(filename)
    if not data_path.exists():
        print(f"⚠️  Data file not found: {data_path}.", file=sys.stderr)
        return {
            "error": f"Data file not found: {data_path}",
            "symbol": symbol,
            "date": date,
            "status": "data_loading",
        }

    with data_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            doc = json.loads(line)
            meta = doc.get("Meta Data", {})
            if meta.get("2. Symbol") != symbol:
                continue
            series = doc.get("Time Series (Daily)", {})
            day = series.get(date)
            if day is None:
                sample_dates = sorted(series.keys(), reverse=True)[:5]
                return {
                    "error": f"Data not found for date {date}. "
                             f"Sample available dates: {sample_dates}",
                    "symbol": symbol,
                    "date": date,
                }
            return {
                "symbol": symbol,
                "date": date,
                "ohlcv": {
                    "open": day.get("1. buy price"),
                    "high": day.get("2. high"),
                    "low": day.get("3. low"),
                    "close": day.get("4. sell price"),
                    "volume": day.get("5. volume"),
                },
            }

    return {
        "error": f"No records found for stock {symbol} in local data",
        "symbol": symbol,
        "date": date,
    }


if __name__ == "__main__":
    try:
        port = int(os.getenv("GETPRICE_HTTP_PORT", "8003"))
        print(f"🚀 LocalPrices service starting on port {port}...", flush=True)
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Error starting LocalPrices service: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise