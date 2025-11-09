import json
import os
import sys
from typing import Any, Dict

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.general_tools import get_config_value, write_config_value
from tools.price_tools import get_latest_position, get_open_prices

mcp = FastMCP("TradeTools")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """
    Health check endpoint.
    """
    return PlainTextResponse("OK")


@mcp.tool()
def buy(symbol: str, amount: int) -> Dict[str, Any]:
    """
    Buy stock function
    """
    signature = get_config_value("SIGNATURE")
    if signature is None:
        raise ValueError("SIGNATURE environment variable is not set")

    today_date = get_config_value("TODAY_DATE")

    try:
        current_position, current_action_id = get_latest_position(today_date, signature)
    except Exception as e:
        print(e)
        print(current_position, current_action_id)
        print(today_date, signature)

    try:
        this_symbol_price = get_open_prices(today_date, [symbol])[f"{symbol}_price"])
    except KeyError:
        return {
            "error": f"Symbol {symbol} not found! This action will not be allowed.",
            "symbol": symbol,
            "date": today_date,
        }

    try:
        cash_left = current_position["CASH"] - this_symbol_price * amount
    except Exception:
        print(current_position, "CASH", this_symbol_price, amount)
        raise

    if cash_left < 0:
        return {
            "error": "Insufficient cash! This action will not be allowed.",
            "required_cash": this_symbol_price * amount,
            "cash_available": current_position.get("CASH", 0),
            "symbol": symbol,
            "date": today_date,
        }
    else:
        new_position = current_position.copy()
        new_position["CASH"] = cash_left
        new_position[symbol] += amount

        position_file_path = os.path.join(
            project_root, "data", "agent_data", signature, "position", "position.jsonl"
        )
        with open(position_file_path, "a") as f:
            log_data = {
                "date": today_date,
                "id": current_action_id + 1,
                "this_action": {"action": "buy", "symbol": symbol, "amount": amount},
                "positions": new_position,
            }
            print(f"Writing to position.jsonl: {json.dumps(log_data)}")
            f.write(json.dumps(log_data) + "\n")

        write_config_value("IF_TRADE", True)
        print("IF_TRADE", get_config_value("IF_TRADE"))
        return new_position


@mcp.tool()
def sell(symbol: str, amount: int) -> Dict[str, Any]:
    """
    Sell stock function
    """
    signature = get_config_value("SIGNATURE")
    if signature is None:
        raise ValueError("SIGNATURE environment variable is not set")

    today_date = get_config_value("TODAY_DATE")

    current_position, current_action_id = get_latest_position(today_date, signature)

    try:
        this_symbol_price = get_open_prices(today_date, [symbol])[f"{symbol}_price"])
    except KeyError:
        return {
            "error": f"Symbol {symbol} not found! This action will not be allowed.",
            "symbol": symbol,
            "date": today_date,
        }

    if symbol not in current_position:
        return {
            "error": f"No position for {symbol}! This action will not be allowed.",
            "symbol": symbol,
            "date": today_date,
        }

    if current_position[symbol] < amount:
        return {
            "error": "Insufficient shares! This action will not be allowed.",
            "have": current_position.get(symbol, 0),
            "want_to_sell": amount,
            "symbol": symbol,
            "date": today_date,
        }

    new_position = current_position.copy()
    new_position[symbol] -= amount
    new_position["CASH"] = new_position.get("CASH", 0) + this_symbol_price * amount

    position_file_path = os.path.join(
        project_root, "data", "agent_data", signature, "position", "position.jsonl"
    )
    with open(position_file_path, "a") as f:
        log_data = {
            "date": today_date,
            "id": current_action_id + 1,
            "this_action": {"action": "sell", "symbol": symbol, "amount": amount},
            "positions": new_position,
        }
        print(f"Writing to position.jsonl: {json.dumps(log_data)}")
        f.write(json.dumps(log_data) + "\n")

    write_config_value("IF_TRADE", True)
    return new_position


if __name__ == "__main__":
    port = int(os.getenv("TRADE_HTTP_PORT", "8002"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)