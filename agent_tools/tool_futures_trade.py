import json
import os
import sys
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Add project root directory to Python path BEFORE importing local modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.general_tools import get_config_value, write_config_value
from tools.futures_tools import (
    get_futures_price_on_date,
    format_futures_price_data,
    load_futures_price_data,
)

mcp = FastMCP("FuturesTradeTools")

from starlette.requests import Request
from starlette.responses import PlainTextResponse


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """
    Health check endpoint.
    Returns: A simple plain text response indicating server health.
    """
    return PlainTextResponse("OK")


def get_futures_data_grid(futures_symbol: str, target_date: str) -> str:
    """
    Get formatted data grid showing all OHLC data for the day

    Args:
        futures_symbol: Futures symbol (NQ1, ES, etc.)
        target_date: Target date (YYYY-MM-DD)

    Returns:
        Formatted data grid string
    """
    data = load_futures_price_data(futures_symbol)

    # Filter data for target date
    day_data = {}
    for dt_str, ohlc in sorted(data.items()):
        if dt_str.startswith(target_date):
            day_data[dt_str] = ohlc

    if not day_data:
        return f"No data available for {futures_symbol} on {target_date}"

    # Format as data grid with improved timestamp visibility
    grid = f"\n{'='*110}\n"
    grid += f"📊 DATA GRID: {futures_symbol} on {target_date} ({len(day_data)} candles)\n"
    grid += f"{'='*110}\n"
    grid += f"{'TIMESTAMP':<25} {'OPEN':>15} {'HIGH':>15} {'LOW':>15} {'CLOSE':>15}\n"
    grid += f"{'-'*85}\n"

    for dt_str, ohlc in day_data.items():
        grid += f"{dt_str:<25} ${ohlc['open']:>14,.2f} ${ohlc['high']:>14,.2f} ${ohlc['low']:>14,.2f} ${ohlc['close']:>14,.2f}\n"

    grid += f"{'='*110}\n"
    return grid


@mcp.tool()
def buy_futures(futures_symbol: str, contracts: float) -> Dict[str, Any]:
    """
    Buy futures contract function

    This function simulates futures buying operations for contracts like NQ1! (Nasdaq-100)
    Steps:
    1. Validate futures symbol is supported
    2. Get current position and operation ID
    3. Get futures price for the day
    4. Show data grid for informed decision
    5. Validate buy conditions (sufficient cash)
    6. Update position (increase contracts, decrease cash)
    7. Record transaction to position.jsonl file

    Args:
        futures_symbol: Futures symbol (NQ1, ES, MNQ, YM, etc.)
        contracts: Number of contracts to buy

    Returns:
        Dict[str, Any]:
          - Success: Returns new position dictionary with updated futures contracts and cash
          - Failure: Returns {"error": error message, ...} dictionary

    Example:
        >>> result = buy_futures("NQ1", 0.5)
        >>> print(result)  # {"NQ1": 0.5, "CASH": 49000.0, ...}
    """
    # Step 1: Get environment variables
    signature = get_config_value("SIGNATURE")
    if signature is None:
        raise ValueError("SIGNATURE environment variable is not set")

    today_date = get_config_value("TODAY_DATE")

    # Validate futures symbol
    SUPPORTED_FUTURES = ["NQ1", "ES", "MES", "MNQ", "YM", "GC", "CL", "ZB", "ZS", "ZC", "ZW"]
    if futures_symbol not in SUPPORTED_FUTURES:
        return {
            "error": f"Unsupported futures contract: {futures_symbol}. Supported: {', '.join(SUPPORTED_FUTURES)}",
            "symbol": futures_symbol,
            "date": today_date,
        }

    # Step 2: Get current position
    from tools.price_tools import get_latest_position
    current_position, current_action_id = get_latest_position(today_date, signature)

    # Step 3: Get futures price for the day
    try:
        price = get_futures_price_on_date(futures_symbol, today_date, "open")
    except KeyError:
        return {
            "error": f"Symbol {futures_symbol} not found! This action will not be allowed.",
            "symbol": futures_symbol,
            "date": today_date,
        }

    # Show data grid
    data_grid = get_futures_data_grid(futures_symbol, today_date)

    # Step 4: Validate buy conditions
    if price is None:
        return {
            "error": f"Price for {futures_symbol} not available on {today_date}! This action will not be allowed.",
            "symbol": futures_symbol,
            "date": today_date,
            "data_grid": data_grid,
        }

    # NQ1 contract multiplier is typically 20 (each point = $20)
    contract_multiplier = 20
    cost_per_contract = price * contract_multiplier
    total_cost = cost_per_contract * contracts

    cash_left = current_position["CASH"] - total_cost

    if cash_left < 0:
        return {
            "error": "Insufficient cash! This action will not be allowed.",
            "required_cash": total_cost,
            "cash_available": current_position.get("CASH", 0),
            "cost_per_contract": cost_per_contract,
            "symbol": futures_symbol,
            "contracts": contracts,
            "price": price,
            "date": today_date,
            "data_grid": data_grid,
        }

    # Step 5: Execute buy operation
    new_position = current_position.copy()
    new_position[futures_symbol] = new_position.get(futures_symbol, 0) + contracts
    new_position["CASH"] = cash_left

    # Step 6: Record transaction
    position_file = f"data/agent_data/{signature}/position/position.jsonl"
    os.makedirs(os.path.dirname(position_file), exist_ok=True)

    transaction_record = {
        "date": today_date,
        "action_id": current_action_id,
        "action": "buy_futures",
        "symbol": futures_symbol,
        "contracts": contracts,
        "price": price,
        "total_cost": total_cost,
        "positions": new_position,
    }

    with open(position_file, "a") as f:
        f.write(json.dumps(transaction_record) + "\n")

    return {
        "success": True,
        "action": "buy_futures",
        "symbol": futures_symbol,
        "contracts": contracts,
        "price_per_point": price,
        "cost_per_contract": cost_per_contract,
        "total_cost": total_cost,
        "new_cash": cash_left,
        "positions": new_position,
        "date": today_date,
        "data_grid": data_grid,
    }


@mcp.tool()
def sell_futures(futures_symbol: str, contracts: float) -> Dict[str, Any]:
    """
    Sell futures contract function

    Steps:
    1. Validate futures symbol
    2. Get current position
    3. Get futures price for the day
    4. Show data grid
    5. Validate sell conditions (have position)
    6. Update position (decrease contracts, increase cash)
    7. Record transaction

    Args:
        futures_symbol: Futures symbol (NQ1, ES, etc.)
        contracts: Number of contracts to sell

    Returns:
        Dict[str, Any]: Updated position or error message
    """
    signature = get_config_value("SIGNATURE")
    if signature is None:
        raise ValueError("SIGNATURE environment variable is not set")

    today_date = get_config_value("TODAY_DATE")

    # Validate futures symbol
    SUPPORTED_FUTURES = ["NQ1", "ES", "MES", "MNQ", "YM", "GC", "CL", "ZB", "ZS", "ZC", "ZW"]
    if futures_symbol not in SUPPORTED_FUTURES:
        return {
            "error": f"Unsupported futures contract: {futures_symbol}",
            "symbol": futures_symbol,
            "date": today_date,
        }

    # Get current position
    from tools.price_tools import get_latest_position
    current_position, current_action_id = get_latest_position(today_date, signature)

    # Get futures price
    try:
        price = get_futures_price_on_date(futures_symbol, today_date, "open")
    except KeyError:
        return {
            "error": f"Symbol {futures_symbol} not found!",
            "symbol": futures_symbol,
            "date": today_date,
        }

    # Show data grid
    data_grid = get_futures_data_grid(futures_symbol, today_date)

    if price is None:
        return {
            "error": f"Price for {futures_symbol} not available on {today_date}!",
            "symbol": futures_symbol,
            "date": today_date,
            "data_grid": data_grid,
        }

    # Validate sell conditions
    current_contracts = current_position.get(futures_symbol, 0)

    if current_contracts < contracts:
        return {
            "error": f"Insufficient {futures_symbol} contracts! Cannot sell {contracts} contracts when only {current_contracts} are held.",
            "symbol": futures_symbol,
            "held_contracts": current_contracts,
            "requested_sell": contracts,
            "date": today_date,
            "data_grid": data_grid,
        }

    # Execute sell operation
    contract_multiplier = 20
    proceeds = price * contract_multiplier * contracts

    new_position = current_position.copy()
    new_position[futures_symbol] = current_contracts - contracts
    new_position["CASH"] = new_position["CASH"] + proceeds

    # Record transaction
    position_file = f"data/agent_data/{signature}/position/position.jsonl"
    os.makedirs(os.path.dirname(position_file), exist_ok=True)

    transaction_record = {
        "date": today_date,
        "action_id": current_action_id,
        "action": "sell_futures",
        "symbol": futures_symbol,
        "contracts": contracts,
        "price": price,
        "proceeds": proceeds,
        "positions": new_position,
    }

    with open(position_file, "a") as f:
        f.write(json.dumps(transaction_record) + "\n")

    return {
        "success": True,
        "action": "sell_futures",
        "symbol": futures_symbol,
        "contracts": contracts,
        "price_per_point": price,
        "proceeds_per_contract": price * contract_multiplier,
        "total_proceeds": proceeds,
        "new_cash": new_position["CASH"],
        "positions": new_position,
        "date": today_date,
        "data_grid": data_grid,
    }


if __name__ == "__main__":
    port = int(os.getenv("FUTURES_TRADE_HTTP_PORT", 8005))
    mcp.run(port=port)
