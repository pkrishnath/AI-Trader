import json
import os
import sys
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Add project root directory to Python path BEFORE importing local modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.general_tools import get_config_value, write_config_value
from tools.crypto_tools import (
    get_crypto_price_on_date,
)

mcp = FastMCP("CryptoTradeTools")

from starlette.requests import Request
from starlette.responses import PlainTextResponse


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """
    Health check endpoint.
    Returns: A simple plain text response indicating server health.
    """
    return PlainTextResponse("OK")


@mcp.tool()
def buy_crypto(crypto_symbol: str, amount: float) -> Dict[str, Any]:
    """
    Buy cryptocurrency function

    This function simulates cryptocurrency buying operations, including the following steps:
    1. Get current position and operation ID
    2. Get crypto price for the day
    3. Validate buy conditions (sufficient cash)
    4. Update position (increase crypto quantity, decrease cash)
    5. Record transaction to position.jsonl file

    Args:
        crypto_symbol: Crypto symbol, such as "BTC", "ETH", etc.
        amount: Buy quantity, can be a fractional amount.

    Returns:
        Dict[str, Any]:
          - Success: Returns new position dictionary (containing crypto quantity and cash balance)
          - Failure: Returns {"error": error message, ...} dictionary

    Raises:
        ValueError: Raised when SIGNATURE environment variable is not set

    Example:
        >>> result = buy_crypto("BTC", 0.1)
        >>> print(result)  # {"BTC": 0.6, "ETH": 2.0, "CASH": 5000.0, ...}
    """
    # Step 1: Get environment variables and basic information
    signature = get_config_value("SIGNATURE")
    if signature is None:
        raise ValueError("SIGNATURE environment variable is not set")

    today_date = get_config_value("TODAY_DATE")

    # Step 2: Get current latest position and operation ID
    from tools.price_tools import get_latest_position
    current_position, current_action_id = get_latest_position(today_date, signature)

    # Step 3: Get crypto price for the day
    try:
        this_symbol_price = get_crypto_price_on_date(crypto_symbol, today_date, "open")
    except KeyError:
        return {
            "error": f"Symbol {crypto_symbol} not found! This action will not be allowed.",
            "symbol": crypto_symbol,
            "date": today_date,
        }

    # Step 4: Validate buy conditions
    if this_symbol_price is None:
        return {
            "error": f"Price for {crypto_symbol} not available on {today_date}! This action will not be allowed.",
            "symbol": crypto_symbol,
            "date": today_date,
        }

    cash_left = current_position["CASH"] - this_symbol_price * amount

    if cash_left < 0:
        return {
            "error": "Insufficient cash! This action will not be allowed.",
            "required_cash": this_symbol_price * amount,
            "cash_available": current_position.get("CASH", 0),
            "symbol": crypto_symbol,
            "date": today_date,
        }
    else:
        # Step 5: Execute buy operation, update position
        new_position = current_position.copy()
        new_position["CASH"] = cash_left
        new_position[crypto_symbol] = new_position.get(crypto_symbol, 0) + amount

        # Step 6: Record transaction to position.jsonl file
        position_file_path = os.path.join(
            project_root, "data", "agent_data", signature, "position", "position.jsonl"
        )
        with open(position_file_path, "a") as f:
            f.write(
                json.dumps(
                    {
                        "date": today_date,
                        "id": current_action_id + 1,
                        "this_action": {
                            "action": "buy_crypto",
                            "symbol": crypto_symbol,
                            "amount": amount,
                        },
                        "positions": new_position,
                    }
                )
                + "\n"
            )
        # Step 7: Return updated position
        write_config_value("IF_TRADE", True)
        return new_position


@mcp.tool()
def sell_crypto(crypto_symbol: str, amount: float) -> Dict[str, Any]:
    """
    Sell cryptocurrency function

    This function simulates cryptocurrency selling operations, including the following steps:
    1. Get current position and operation ID
    2. Get crypto price for the day
    3. Validate sell conditions (position exists, sufficient quantity)
    4. Update position (decrease crypto quantity, increase cash)
    5. Record transaction to position.jsonl file

    Args:
        crypto_symbol: Crypto symbol, such as "BTC", "ETH", etc.
        amount: Sell quantity, can be a fractional amount.

    Returns:
        Dict[str, Any]:
          - Success: Returns new position dictionary (containing crypto quantity and cash balance)
          - Failure: Returns {"error": error message, ...} dictionary

    Raises:
        ValueError: Raised when SIGNATURE environment variable is not set

    Example:
        >>> result = sell_crypto("BTC", 0.1)
        >>> print(result)  # {"BTC": 0.4, "ETH": 2.0, "CASH": 15000.0, ...}
    """
    # Step 1: Get environment variables and basic information
    signature = get_config_value("SIGNATURE")
    if signature is None:
        raise ValueError("SIGNATURE environment variable is not set")

    today_date = get_config_value("TODAY_DATE")

    # Step 2: Get current latest position and operation ID
    from tools.price_tools import get_latest_position
    current_position, current_action_id = get_latest_position(today_date, signature)

    # Step 3: Get crypto price for the day
    try:
        this_symbol_price = get_crypto_price_on_date(crypto_symbol, today_date, "open")
    except KeyError:
        return {
            "error": f"Symbol {crypto_symbol} not found! This action will not be allowed.",
            "symbol": crypto_symbol,
            "date": today_date,
        }

    # Step 4: Validate sell conditions
    if this_symbol_price is None:
        return {
            "error": f"Price for {crypto_symbol} not available on {today_date}! This action will not be allowed.",
            "symbol": crypto_symbol,
            "date": today_date,
        }

    if crypto_symbol not in current_position:
        return {
            "error": f"No position for {crypto_symbol}! This action will not be allowed.",
            "symbol": crypto_symbol,
            "date": today_date,
        }

    if current_position[crypto_symbol] < amount:
        return {
            "error": "Insufficient shares! This action will not be allowed.",
            "have": current_position.get(crypto_symbol, 0),
            "want_to_sell": amount,
            "symbol": crypto_symbol,
            "date": today_date,
        }

    # Step 5: Execute sell operation, update position
    new_position = current_position.copy()
    new_position[crypto_symbol] -= amount
    new_position["CASH"] = new_position.get("CASH", 0) + this_symbol_price * amount

    # Step 6: Record transaction to position.jsonl file
    position_file_path = os.path.join(
        project_root, "data", "agent_data", signature, "position", "position.jsonl"
    )
    with open(position_file_path, "a") as f:
        f.write(
            json.dumps(
                {
                    "date": today_date,
                    "id": current_action_id + 1,
                    "this_action": {
                        "action": "sell_crypto",
                        "symbol": crypto_symbol,
                        "amount": amount,
                    },
                    "positions": new_position,
                }
            )
            + "\n"
        )

    # Step 7: Return updated position
    write_config_value("IF_TRADE", True)
    return new_position


if __name__ == "__main__":
    port = int(os.getenv("CRYPTO_TRADE_HTTP_PORT", "8004"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)
