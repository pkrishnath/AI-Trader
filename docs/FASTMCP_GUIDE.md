# FastMCP Services: Complete Guide

Comprehensive documentation on how FastMCP works in AI-Trader, tool definitions, HTTP communication, and troubleshooting.

**Table of Contents:**
1. [What is FastMCP?](#what-is-fastmcp)
2. [Service Architecture](#service-architecture)
3. [Tool Definitions](#tool-definitions)
4. [HTTP Communication](#http-communication)
5. [Service Implementations](#service-implementations)
6. [Error Handling](#error-handling)
7. [Troubleshooting](#troubleshooting)

---

## What is FastMCP?

### Overview

**FastMCP** is a Python framework for building lightweight HTTP-based Model Context Protocol (MCP) services that expose Python functions as tools callable by LLMs.

**Traditional LLM Limitation:**
```
LLM (in memory)
    │
    ├─ Can do: Text processing, reasoning, math
    ├─ Cannot do: Access external APIs, fetch live data
    └─ Cannot do: Make changes to systems
```

**With FastMCP:**
```
LLM (in memory) ◄──HTTP──► FastMCP Service
    │                         │
    ├─ Can do: Reasoning      ├─ Can do: Fetch live prices
    ├─ Can use tools          ├─ Can execute trades
    └─ Can plan              └─ Can search the web
```

### Key Benefits

| Feature | Benefit |
|---------|---------|
| **HTTP-based** | Services run anywhere (different machines, containers, cloud) |
| **Tool registration** | Automatically discovers available functions |
| **Structured I/O** | Validates inputs/outputs using Pydantic |
| **Error handling** | Graceful failures with error messages |
| **Scalability** | Multiple instances for load balancing |
| **Async support** | Non-blocking I/O for high performance |

### MCP Protocol Basics

```
Client Request (JSON):
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_price",
    "arguments": {"symbol": "AAPL", "date": "2025-11-02"}
  }
}
                    ↓ (HTTP POST)
              FastMCP Server
                    ↓
Server Response (JSON):
{
  "jsonrpc": "2.0",
  "result": {
    "symbol": "AAPL",
    "date": "2025-11-02",
    "price": 150.25
  }
}
```

---

## Service Architecture

### The 4 Services in AI-Trader

```
┌─────────────────────────────────────────────────────────────┐
│                    BaseAgent (main.py)                      │
│                                                              │
│  Makes trading decisions using LLM reasoning                │
└──────────────────────────────────────────────────────────────┘
              │              │              │              │
              │ HTTP         │ HTTP         │ HTTP         │ HTTP
              │ Port 8000    │ Port 8001    │ Port 8002    │ Port 8003
              ▼              ▼              ▼              ▼
         ┌────────────┐  ┌──────────────┐ ┌───────────┐  ┌──────────────┐
         │   Math     │  │   Search     │ │   Trade   │  │   Prices     │
         │  Service   │  │  Service     │ │  Service  │  │  Service     │
         └────────────┘  └──────────────┘ └───────────┘  └──────────────┘
         • SMA        │  • Web search  │  • Execute │  • Get OHLCV
         • RSI        │  • News fetch  │    trades  │  • Historical
         • MACD       │  • Market data │  • Pos.    │    prices
         • Statistics │  • Jina API    │    tracking│  • Price lookups
```

### Service Discovery & Registration

Each FastMCP service follows this pattern:

```python
from fastmcp import FastMCP

# Create service instance
mcp = FastMCP("ServiceName")

# Register tools (functions that LLM can call)
@mcp.tool()
def my_tool(param1: str, param2: int) -> dict:
    """Tool description for LLM"""
    return {"result": "..."}

# Start HTTP server
if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8000)
```

When service starts:
```
✅ FastMCP Math Service running on http://0.0.0.0:8000/mcp

Available tools:
  1. calculate_sma
     └─ Calculate Simple Moving Average

  2. calculate_rsi
     └─ Calculate Relative Strength Index

  3. calculate_macd
     └─ Calculate MACD indicator
```

---

## Tool Definitions

### Tool Definition Structure

```python
from fastmcp import FastMCP
from typing import Optional, List

mcp = FastMCP("ExampleService")

@mcp.tool()
def my_function(
    required_param: str,
    optional_param: Optional[int] = None,
    list_param: Optional[List[float]] = None
) -> dict:
    """
    This is the tool description that LLM sees.

    Args:
        required_param: Description of required parameter
        optional_param: Description of optional parameter
        list_param: Description of list parameter

    Returns:
        dict: Explanation of return structure

    Raises:
        ValueError: When inputs are invalid
    """
    # Implementation
    return {"status": "success", "data": "..."}
```

### Type Annotations Matter

FastMCP uses Python type hints to validate and document tools:

```python
# ❌ BAD: No type hints
@mcp.tool()
def calculate_average(numbers):
    return sum(numbers) / len(numbers)

# ✅ GOOD: Clear types
@mcp.tool()
def calculate_average(numbers: List[float]) -> float:
    """Calculate arithmetic mean of numbers"""
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
```

FastMCP automatically:
- Validates inputs match types
- Generates API documentation
- Returns helpful error messages
- Enables IDE autocomplete

---

## HTTP Communication

### Request/Response Cycle

```
1. LLM decides to use a tool
   ├─ Tool name: "get_price"
   ├─ Parameters: {"symbol": "AAPL"}
   └─ Reason: "Need current price to decide if buying"

2. Agent formats HTTP request
   POST http://localhost:8003/mcp/tools/call
   {
     "name": "get_price",
     "arguments": {"symbol": "AAPL"}
   }

3. Prices Service receives & validates
   ├─ Check: "symbol" is string ✓
   ├─ Check: "symbol" is AAPL ✓
   └─ Call: get_price(symbol="AAPL")

4. Tool executes
   ├─ Read from merged.jsonl
   ├─ Find AAPL data
   └─ Return latest price

5. Service formats response
   200 OK
   {
     "symbol": "AAPL",
     "price": 150.25,
     "date": "2025-11-02",
     "timestamp": "2025-11-02T13:30:00Z"
   }

6. Agent receives & processes
   ├─ Parse JSON response
   ├─ Extract price: 150.25
   ├─ Use in reasoning
   └─ Make decision
```

### HTTP Headers

```
Request:
POST /mcp/tools/call HTTP/1.1
Host: localhost:8003
Content-Type: application/json
Content-Length: 45
Connection: keep-alive
User-Agent: httpx/0.24.0

Response:
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 128
Server: uvicorn
Date: Sun, 02 Nov 2025 13:30:00 GMT
```

### Error Responses

```
Request with bad parameters:
POST /mcp/tools/call
{
  "name": "get_price",
  "arguments": {"symbol": 123}  # ← Wrong type!
}

Response:
400 Bad Request
{
  "error": "Validation error",
  "message": "symbol must be string, got int",
  "details": {
    "field": "symbol",
    "expected": "str",
    "received": "int"
  }
}
```

---

## Service Implementations

### Service 1: Math Service (Port 8000)

**File:** `/Users/krish/code/github/AI-Trader/agent_tools/tool_math.py`

```python
from fastmcp import FastMCP
from typing import List

mcp = FastMCP("Math")

@mcp.tool()
def calculate_sma(prices: List[float], period: int) -> float:
    """
    Calculate Simple Moving Average (SMA)

    Uses last 'period' prices to smooth price movements.

    Args:
        prices: List of closing prices (in order)
        period: Number of periods (e.g., 50 for 50-day MA)

    Returns:
        float: Simple moving average

    Example:
        >>> calculate_sma([100, 101, 102, 103], 2)
        102.5  # (102 + 103) / 2
    """
    if not prices or period > len(prices):
        raise ValueError(f"Need at least {period} prices")

    recent_prices = prices[-period:]
    return sum(recent_prices) / period

@mcp.tool()
def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI)

    Momentum indicator showing overbought (>70) or oversold (<30).

    Args:
        prices: List of closing prices
        period: RSI period (default 14 days)

    Returns:
        float: RSI value 0-100
    """
    if len(prices) < period + 1:
        raise ValueError(f"Need at least {period + 1} prices")

    # Calculate gains and losses
    changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [c for c in changes if c > 0]
    losses = [-c for c in changes if c < 0]

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)

@mcp.tool()
def calculate_volatility(prices: List[float], period: int = 20) -> float:
    """
    Calculate price volatility (standard deviation)

    Measures price movement. High = risky, Low = stable.

    Args:
        prices: List of closing prices
        period: Lookback period

    Returns:
        float: Volatility percentage
    """
    if len(prices) < period:
        raise ValueError(f"Need at least {period} prices")

    recent = prices[-period:]
    mean = sum(recent) / len(recent)
    variance = sum((p - mean) ** 2 for p in recent) / len(recent)
    std_dev = variance ** 0.5

    volatility = (std_dev / mean) * 100
    return round(volatility, 2)

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8000)
```

**Usage in Agent:**

```python
# Agent calls this tool
math_result = await self.call_tool("calculate_sma", {
    "prices": [100, 101, 102, 103, 104],
    "period": 3
})
# Returns: 103.0

# Agent uses in decision
if current_price > math_result:
    print("Price above 3-day MA - Bullish signal!")
else:
    print("Price below 3-day MA - Bearish signal!")
```

### Service 2: Search Service (Port 8001)

**File:** `/Users/krish/code/github/AI-Trader/agent_tools/tool_jina_search.py`

```python
from fastmcp import FastMCP
import os
import httpx

mcp = FastMCP("Search")

JINA_API_KEY = os.getenv("JINA_API_KEY")
JINA_API_URL = "https://api.jina.ai/search"

@mcp.tool()
async def search_market_news(query: str, limit: int = 5) -> dict:
    """
    Search for market news using Jina API

    Retrieves latest news articles about stocks, crypto, or markets.

    Args:
        query: Search query (e.g., "Apple earnings", "Bitcoin news")
        limit: Number of results to return (1-10)

    Returns:
        dict: {
            "query": "...",
            "results": [
                {
                    "title": "...",
                    "url": "...",
                    "snippet": "...",
                    "source": "..."
                }
            ]
        }

    Example:
        >>> result = await search_market_news("Apple stock surge")
        >>> for article in result["results"]:
        ...     print(f"{article['title']} - {article['source']}")
    """
    if not JINA_API_KEY:
        raise ValueError("JINA_API_KEY environment variable not set")

    if limit < 1 or limit > 10:
        raise ValueError("limit must be between 1 and 10")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                JINA_API_URL,
                headers={"Authorization": f"Bearer {JINA_API_KEY}"},
                params={"q": query, "limit": limit},
                timeout=10.0
            )

            if response.status_code != 200:
                raise ValueError(f"Jina API error: {response.status_code}")

            return response.json()

    except httpx.RequestError as e:
        raise ValueError(f"Failed to connect to Jina API: {str(e)}")

@mcp.tool()
async def search_earnings_calendar(symbol: str) -> dict:
    """
    Search for earnings announcement dates

    Args:
        symbol: Stock symbol (e.g., "AAPL")

    Returns:
        dict: {
            "symbol": "AAPL",
            "next_earnings": "2025-11-15",
            "time": "after market",
            "confidence": 0.95
        }
    """
    query = f"{symbol} earnings date announcement"
    results = await search_market_news(query, limit=3)

    # Parse results to extract earnings date
    # (Simplified - real implementation would parse more carefully)
    return {
        "symbol": symbol,
        "query": query,
        "results_count": len(results.get("results", [])),
        "top_result": results.get("results", [{}])[0]
    }

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8001)
```

**Usage in Agent:**

```python
# Agent wants to research a stock
search_results = await self.call_tool("search_market_news", {
    "query": "Apple stock outlook 2025",
    "limit": 3
})

# Agent reads results
for article in search_results["results"]:
    print(f"Title: {article['title']}")
    print(f"Source: {article['source']}")
    print(f"Snippet: {article['snippet']}\n")

# Agent makes decision based on sentiment
if "positive" in str(search_results).lower():
    print("Bullish news - consider buying")
else:
    print("Bearish news - consider selling")
```

### Service 3: Trade Service (Port 8002)

**File:** `/Users/krish/code/github/AI-Trader/agent_tools/tool_trade.py`

```python
from fastmcp import FastMCP
from datetime import datetime
from typing import Optional, List

mcp = FastMCP("Trade")

# In-memory portfolio (in real system, would use database)
PORTFOLIO = {
    "cash": 10000.0,
    "positions": {},
    "trades": []
}

@mcp.tool()
def execute_trade(
    symbol: str,
    action: str,  # "buy" or "sell"
    quantity: int,
    price: float
) -> dict:
    """
    Execute a buy or sell order

    Args:
        symbol: Stock symbol (e.g., "AAPL")
        action: "buy" or "sell"
        quantity: Number of shares
        price: Price per share

    Returns:
        dict: {
            "success": true/false,
            "order_id": "...",
            "symbol": "AAPL",
            "action": "buy",
            "quantity": 10,
            "price": 150.25,
            "total": 1502.50,
            "timestamp": "2025-11-02T13:30:00Z"
        }

    Raises:
        ValueError: If insufficient cash or invalid symbol
    """
    if action not in ["buy", "sell"]:
        raise ValueError(f"action must be 'buy' or 'sell', got '{action}'")

    if quantity <= 0:
        raise ValueError(f"quantity must be positive, got {quantity}")

    if price <= 0:
        raise ValueError(f"price must be positive, got {price}")

    total_cost = quantity * price

    # Check if can afford
    if action == "buy":
        if total_cost > PORTFOLIO["cash"]:
            raise ValueError(
                f"Insufficient cash: need ${total_cost}, have ${PORTFOLIO['cash']}"
            )

    # Check if have shares to sell
    if action == "sell":
        if symbol not in PORTFOLIO["positions"]:
            raise ValueError(f"No position in {symbol} to sell")

        current_qty = PORTFOLIO["positions"][symbol]["quantity"]
        if quantity > current_qty:
            raise ValueError(
                f"Cannot sell {quantity} shares, only have {current_qty}"
            )

    # Execute trade
    order_id = f"ORD_{len(PORTFOLIO['trades']) + 1:05d}"

    if action == "buy":
        PORTFOLIO["cash"] -= total_cost

        if symbol not in PORTFOLIO["positions"]:
            PORTFOLIO["positions"][symbol] = {
                "quantity": 0,
                "avg_cost": 0,
                "trades": []
            }

        # Update average cost
        pos = PORTFOLIO["positions"][symbol]
        total_qty = pos["quantity"] + quantity
        total_invested = (pos["quantity"] * pos["avg_cost"]) + total_cost
        pos["quantity"] = total_qty
        pos["avg_cost"] = total_invested / total_qty if total_qty > 0 else 0
        pos["trades"].append(order_id)

    else:  # sell
        PORTFOLIO["cash"] += total_cost
        PORTFOLIO["positions"][symbol]["quantity"] -= quantity

        if PORTFOLIO["positions"][symbol]["quantity"] == 0:
            del PORTFOLIO["positions"][symbol]

    # Record trade
    trade = {
        "order_id": order_id,
        "symbol": symbol,
        "action": action,
        "quantity": quantity,
        "price": price,
        "total": total_cost,
        "timestamp": datetime.now().isoformat() + "Z"
    }

    PORTFOLIO["trades"].append(trade)

    return {
        "success": True,
        **trade
    }

@mcp.tool()
def get_portfolio_status() -> dict:
    """
    Get current portfolio status

    Returns:
        dict: {
            "timestamp": "2025-11-02T13:30:00Z",
            "cash": 8500.00,
            "positions": {
                "AAPL": {
                    "quantity": 10,
                    "avg_cost": 150.25,
                    "current_value": 1502.50,
                    "unrealized_pnl": 12.50
                }
            },
            "total_value": 20000.00,
            "total_invested": 19500.00,
            "total_pnl": 500.00
        }
    """
    total_value = PORTFOLIO["cash"]
    total_invested = 0

    for symbol, pos in PORTFOLIO["positions"].items():
        total_invested += pos["quantity"] * pos["avg_cost"]
        total_value += pos["quantity"] * pos["avg_cost"]  # Simplified

    return {
        "timestamp": datetime.now().isoformat() + "Z",
        "cash": PORTFOLIO["cash"],
        "positions": PORTFOLIO["positions"],
        "total_value": total_value,
        "total_invested": total_invested,
        "total_pnl": total_value - 10000  # From initial $10k
    }

@mcp.tool()
def get_trade_history(limit: int = 10) -> List[dict]:
    """
    Get last N trades executed

    Args:
        limit: Number of trades to return

    Returns:
        List of trade records
    """
    return PORTFOLIO["trades"][-limit:]

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8002)
```

### Service 4: Prices Service (Port 8003)

**File:** `/Users/krish/code/github/AI-Trader/agent_tools/tool_get_price_local.py`

```python
from fastmcp import FastMCP
import json
from typing import Optional, List

mcp = FastMCP("Prices")

# Load price data from merged.jsonl
PRICE_DATA = {}

def load_price_data():
    """Load all price data from merged.jsonl"""
    try:
        with open("data/merged.jsonl", "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    symbol = data.get("Meta Data", {}).get("2. Symbol")
                    if symbol:
                        PRICE_DATA[symbol] = data
    except FileNotFoundError:
        print("⚠️  merged.jsonl not found - prices unavailable")

# Load on startup
load_price_data()

@mcp.tool()
def get_price(symbol: str, date: Optional[str] = None) -> dict:
    """
    Get OHLCV data for a symbol

    Args:
        symbol: Stock/crypto symbol (e.g., "AAPL", "BTC")
        date: Specific date (YYYY-MM-DD), or None for latest

    Returns:
        dict: {
            "symbol": "AAPL",
            "date": "2025-11-02",
            "open": 150.10,
            "high": 151.50,
            "low": 149.80,
            "close": 150.25,
            "volume": 50000000
        }

    Raises:
        ValueError: If symbol not found
    """
    if symbol not in PRICE_DATA:
        available = list(PRICE_DATA.keys())
        raise ValueError(
            f"Symbol {symbol} not found. Available: {available[:10]}..."
        )

    data = PRICE_DATA[symbol]
    time_series = data.get("Time Series (Daily)", {})

    if not date:
        # Get latest date
        dates = sorted(time_series.keys(), reverse=True)
        date = dates[0] if dates else None

    if not date or date not in time_series:
        raise ValueError(f"No data for {symbol} on {date}")

    bar = time_series[date]

    return {
        "symbol": symbol,
        "date": date,
        "open": float(bar.get("1. open", bar.get("1. buy price", 0))),
        "high": float(bar.get("2. high", 0)),
        "low": float(bar.get("3. low", 0)),
        "close": float(bar.get("4. close", bar.get("4. sell price", 0))),
        "volume": int(bar.get("5. volume", 0))
    }

@mcp.tool()
def get_price_history(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 60
) -> List[dict]:
    """
    Get historical price data for a symbol

    Args:
        symbol: Stock/crypto symbol
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        limit: Maximum number of days to return

    Returns:
        List of OHLCV data in chronological order
    """
    if symbol not in PRICE_DATA:
        raise ValueError(f"Symbol {symbol} not found")

    data = PRICE_DATA[symbol]
    time_series = data.get("Time Series (Daily)", {})

    # Sort dates and apply limit
    dates = sorted(time_series.keys(), reverse=True)[:limit]

    history = []
    for date in sorted(dates):  # Return in chronological order
        if start_date and date < start_date:
            continue
        if end_date and date > end_date:
            continue

        bar = time_series[date]
        history.append({
            "symbol": symbol,
            "date": date,
            "open": float(bar.get("1. open", bar.get("1. buy price", 0))),
            "high": float(bar.get("2. high", 0)),
            "low": float(bar.get("3. low", 0)),
            "close": float(bar.get("4. close", bar.get("4. sell price", 0))),
            "volume": int(bar.get("5. volume", 0))
        })

    return history

@mcp.tool()
def list_available_symbols() -> dict:
    """
    List all available symbols in price database

    Returns:
        dict: {
            "count": 102,
            "stocks": ["AAPL", "MSFT", ...],
            "crypto": ["BTC", "ETH"]
        }
    """
    stocks = []
    crypto = []

    for symbol in PRICE_DATA.keys():
        if symbol in ["BTC", "ETH"]:
            crypto.append(symbol)
        else:
            stocks.append(symbol)

    return {
        "count": len(PRICE_DATA),
        "stocks": sorted(stocks),
        "crypto": sorted(crypto)
    }

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8003)
```

---

## Error Handling

### Common Errors & Solutions

#### Error 1: Service Not Running

```
ConnectionError: Failed to connect to http://localhost:8000
```

**Cause:** Math service hasn't started

**Solution:**
```bash
docker compose -f docker-compose.yml ps
# Check if math-service is running
# If not: docker compose -f docker-compose.yml up -d math-service
```

#### Error 2: Type Validation Failed

```
ValidationError: symbol must be string, got int
```

**Cause:** Agent passed `{"symbol": 123}` instead of `{"symbol": "AAPL"}`

**Solution:** Check agent logic to ensure parameters match tool signatures

```python
# ❌ Wrong
get_price(symbol=123)

# ✅ Correct
get_price(symbol="AAPL")
```

#### Error 3: Insufficient Data

```
ValueError: Need at least 50 prices for 50-day MA, got 30
```

**Cause:** Not enough historical data available

**Solution:** Use shorter period or wait for more data

```python
# ❌ Fails with few data points
calculate_sma(prices, period=50)

# ✅ Use adaptive period
period = min(50, len(prices) - 1)
calculate_sma(prices, period=period)
```

#### Error 4: API Rate Limit

```
Jina API error: 429 Too Many Requests
```

**Cause:** Too many search requests

**Solution:** Add delay between searches

```python
import asyncio

async def rate_limited_search(query: str):
    result = await search_market_news(query)
    await asyncio.sleep(1)  # Wait 1 second
    return result
```

### Implementing Tool Error Handling

```python
@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# FastMCP automatically:
# 1. Catches the ValueError
# 2. Returns error response:
#    {
#      "error": "Cannot divide by zero",
#      "tool": "divide",
#      "timestamp": "2025-11-02T13:30:00Z"
#    }
# 3. Agent receives error and can retry with different parameters
```

---

## Troubleshooting

### Debug Checklist

```
□ Is Docker running?
  └─ docker ps

□ Are all 4 services running?
  └─ docker compose ps

□ Is service port accessible?
  └─ curl http://localhost:8000/health

□ Are environment variables set?
  └─ echo $JINA_API_KEY
  └─ echo $OPENAI_API_KEY

□ Is merged.jsonl file populated?
  └─ wc -l data/merged.jsonl

□ Are service logs showing errors?
  └─ docker compose logs math-service
  └─ docker compose logs search-service
```

### Common Service Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Python import error | `ModuleNotFoundError: No module named 'fastmcp'` | `pip install fastmcp` in container |
| Port already in use | `Address already in use` | `lsof -i :8000` then `kill <PID>` |
| Missing data file | `FileNotFoundError: merged.jsonl` | Run `python data/merge_jsonl.py` |
| API key invalid | `401 Unauthorized` | Check Jina API key in `.env` |
| Network unreachable | `Connection refused` | Check Docker network: `docker network ls` |

---

## Summary

FastMCP enables:
1. **Tool Registration:** Python functions become LLM-callable tools
2. **HTTP Communication:** Service-to-service via REST APIs
3. **Type Safety:** Pydantic validation of inputs/outputs
4. **Error Handling:** Graceful failures with useful messages
5. **Scalability:** Services run independently in containers

In AI-Trader:
- **4 services** provide distinct capabilities
- **HTTP communication** enables flexibility
- **Docker isolation** ensures reliability
- **Type annotations** prevent errors
- **Async support** enables high performance

This architecture allows the LLM to safely call external tools and make real-world impact!
