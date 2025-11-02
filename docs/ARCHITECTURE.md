# AI-Trader Architecture & Code Review

Complete technical documentation explaining how the AI-Trader system works from scratch, including FastMCP integration, service architecture, and trading logic.

**Table of Contents:**
1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [FastMCP Services](#fastmcp-services)
4. [Trading Agent Logic](#trading-agent-logic)
5. [Configuration System](#configuration-system)
6. [Data Flow](#data-flow)
7. [Docker Containerization](#docker-containerization)
8. [GitHub Actions Automation](#github-actions-automation)

---

## System Overview

### What is AI-Trader?

AI-Trader is an **intelligent automated trading system** that:
- Uses Large Language Models (LLMs) to make trading decisions
- Fetches real-time stock and cryptocurrency prices
- Executes trades based on AI analysis
- Runs 24/7 on GitHub Actions with hourly trading cycles
- Supports multiple AI providers (OpenAI, Anthropic, DeepSeek)
- Tracks portfolio performance and positions

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│         GitHub Actions Hourly Trigger                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Docker Compose         │
        │  (4 MCP Services)       │
        └─────────┬──────┬────────┘
                  │      │
        ┌─────────▼──┐  └──────────────────┐
        │  MCP      │                      │
        │  Services │        Trading Agent │
        │           │        (main.py)     │
        └────┬──────┘                      │
             │          (connects via HTTP)│
   ┌─────────┼─────────────────────────────▼──────┐
   │         │                                      │
   ▼         ▼                                      ▼
 Math     Search    Trade      Prices      BaseAgent
 (8000)   (8001)   (8002)     (8003)      - Reasoning
                                          - Decision
                                          - Execution
             │
             └──────────────────┬─────────────────┐
                               │                  │
                            Logs            Position
                          (JSONL)           Tracking
```

---

## Architecture Layers

### Layer 1: Entry Point (`main.py`)

**File:** `/Users/krish/code/github/AI-Trader/main.py`

**Purpose:** Application orchestrator that:
1. Loads configuration files
2. Dynamically instantiates agent classes
3. Manages multiple LLM models
4. Orchestrates trading sessions

**Key Functions:**

```python
def load_config(config_path=None):
    """
    Load JSON configuration file
    - Reads configs/default_config.json or custom config
    - Returns dict with agent, model, and trading parameters
    """

def get_agent_class(agent_type):
    """
    Dynamic class loading using agent registry
    - Supports extensible agent types
    - Currently implements: BaseAgent
    - Pattern allows adding new agents without modifying main.py
    """

async def main(config_path=None):
    """
    Main orchestration loop:
    1. Load config and models
    2. For each enabled model:
       - Create agent instance
       - Initialize MCP connections
       - Run trading session
       - Log results
    """
```

**Configuration Example:**

```json
{
  "agent_type": "BaseAgent",
  "date_range": {
    "init_date": "2025-10-28",
    "end_date": "2025-11-02"
  },
  "models": [
    {
      "name": "gpt-4o-crypto",
      "basemodel": "gpt-4o",
      "signature": "gpt-4o-crypto-trader",
      "enabled": true
    }
  ],
  "agent_config": {
    "max_steps": 30,
    "initial_cash": 10000.0
  }
}
```

---

### Layer 2: Trading Agent (`BaseAgent`)

**File:** `/Users/krish/code/github/AI-Trader/agent/base_agent/base_agent.py` (595 lines)

**Purpose:** Core intelligent trading agent that uses LLMs to:
1. Analyze stock/crypto prices
2. Make buy/sell decisions
3. Manage portfolio positions
4. Track trading history

#### Agent Initialization

```python
class BaseAgent:
    def __init__(
        self,
        signature: str,           # Agent identifier
        basemodel: str,           # LLM model name
        stock_symbols: list,      # Trading universe
        log_path: str,            # Where to save logs
        max_steps: int = 10,      # Max decisions per session
        initial_cash: float = 10000.0
    ):
        """
        Initialize agent with:
        - LLM connection (OpenAI, Anthropic, DeepSeek)
        - MCP service connections
        - Trading state tracking
        - Portfolio management
        """
```

#### MCP Service Integration

```python
def _init_mcp_services(self):
    """
    Connect to 4 FastMCP services:

    1. Math Service (http://localhost:8000)
       - Calculations, analysis functions

    2. Search Service (http://localhost:8001)
       - Web search via Jina API
       - Market research

    3. Trade Service (http://localhost:8002)
       - Execute buy/sell orders
       - Position tracking

    4. Prices Service (http://localhost:8003)
       - Fetch OHLCV data
       - Price lookups
    """
```

#### Trading Decision Loop

```python
async def run_trading_session(self):
    """
    Main trading loop (max_steps iterations):

    Step 1: System Prompt
    ├─ Initialize agent with market context
    ├─ Define decision-making rules
    └─ Set portfolio constraints

    Step 2: Market Analysis
    ├─ Fetch current prices
    ├─ Calculate technical indicators
    └─ Search for market news

    Step 3: LLM Decision
    ├─ Send market data to LLM
    ├─ Ask: "Should we buy/sell?"
    └─ Receive structured action

    Step 4: Action Execution
    ├─ Call Trade Service
    ├─ Update portfolio
    └─ Log transaction

    Step 5: Result Analysis
    ├─ Calculate P&L
    ├─ Update position tracking
    └─ Decide: Continue or Stop?

    Step 6: Exit Condition
    └─ Stop if max_steps reached or agent says "done"
    """
```

#### LLM Model Support

```python
def _init_llm_model(self):
    """
    Dynamic LLM initialization supporting:

    OpenAI Models:
    - gpt-4-turbo
    - gpt-4o
    - gpt-4-mini

    Anthropic Models:
    - claude-3.5-sonnet
    - claude-3-opus

    DeepSeek Models:
    - deepseek-chat-v3.1

    Custom Models:
    - Support via openai_base_url parameter
    """
```

---

### Layer 3: FastMCP Services

**What is FastMCP?**

FastMCP is a lightweight framework for building Model Context Protocol (MCP) services using HTTP. It allows:
- LLMs to call external tools via REST APIs
- Tool discovery and validation
- Structured input/output handling
- Error handling and retries

#### Service Architecture

```
Client (BaseAgent)
    │
    ├─── HTTP POST to localhost:8000 ───→ Math Service
    │                                      - Vector operations
    │                                      - Statistics
    │                                      - Time series analysis
    │
    ├─── HTTP POST to localhost:8001 ───→ Search Service
    │                                      - Web search (Jina API)
    │                                      - News retrieval
    │                                      - Market research
    │
    ├─── HTTP POST to localhost:8002 ───→ Trade Service
    │                                      - Execute trades
    │                                      - Position tracking
    │                                      - P&L calculation
    │
    └─── HTTP POST to localhost:8003 ───→ Prices Service
                                           - Historical OHLCV
                                           - Real-time quotes
                                           - Price lookups
```

#### Service 1: Math Service (`tool_math.py`)

**Port:** 8000
**Framework:** FastMCP
**Purpose:** Numeric calculations

```python
# Example FastMCP tool definition
@mcp.tool()
def calculate_sma(prices: list, period: int) -> float:
    """
    Calculate Simple Moving Average

    Args:
        prices: List of closing prices
        period: Number of periods

    Returns:
        Simple moving average
    """
    return sum(prices[-period:]) / period
```

**Running:**
```bash
# Inside Docker container
python agent_tools/tool_math.py

# Outputs:
# ✅ FastMCP Math Service running on http://0.0.0.0:8000/mcp
```

#### Service 2: Search Service (`tool_jina_search.py`)

**Port:** 8001
**Framework:** FastMCP
**Purpose:** Market research via web search

```python
@mcp.tool()
def search_market_news(query: str, limit: int = 5) -> dict:
    """
    Search for market news using Jina API

    Args:
        query: Search query (e.g., "Apple earnings")
        limit: Number of results

    Returns:
        {"results": [{"title": "...", "url": "...", "snippet": "..."}]}
    """
    # Uses environment variable: JINA_API_KEY
    response = requests.get(
        "https://api.jina.ai/search",
        headers={"Authorization": f"Bearer {JINA_API_KEY}"},
        params={"q": query, "limit": limit}
    )
    return response.json()
```

#### Service 3: Trade Service (`tool_trade.py`)

**Port:** 8002
**Framework:** FastMCP
**Purpose:** Execute trades and manage portfolio

```python
@mcp.tool()
def execute_trade(
    symbol: str,
    action: str,  # "buy" or "sell"
    quantity: int,
    price: float
) -> dict:
    """
    Execute buy/sell order

    Returns:
    {
        "success": true,
        "order_id": "ORD_12345",
        "symbol": "AAPL",
        "action": "buy",
        "quantity": 10,
        "price": 150.25,
        "total": 1502.50,
        "timestamp": "2025-11-02T13:30:00Z"
    }
    """
    # Updates internal position tracking
    # Calls TradeTools class methods
```

```python
@mcp.tool()
def get_portfolio_status() -> dict:
    """
    Get current portfolio state

    Returns:
    {
        "cash": 8500.00,
        "positions": {
            "AAPL": {"quantity": 10, "avg_cost": 150.25},
            "MSFT": {"quantity": 5, "avg_cost": 350.00}
        },
        "total_value": 20000.00,
        "p_l": 2000.00
    }
    """
```

#### Service 4: Prices Service (`tool_get_price_local.py`)

**Port:** 8003
**Framework:** FastMCP
**Purpose:** Price lookups

```python
@mcp.tool()
def get_price(symbol: str, date: str = None) -> dict:
    """
    Get OHLCV data for symbol

    Returns:
    {
        "symbol": "AAPL",
        "date": "2025-11-02",
        "open": 150.10,
        "high": 151.50,
        "low": 149.80,
        "close": 150.25,
        "volume": 50000000
    }
    """
    # Reads from merged.jsonl file (stock + crypto prices)
```

#### FastMCP Request/Response Flow

```python
# Inside BaseAgent
from langchain.agents import AgentExecutor, create_openai_functions_agent

# MCP tools are exposed as LLM-callable functions
tools = [
    get_price_tool,
    search_market_news_tool,
    execute_trade_tool,
    calculate_sma_tool
]

# Agent can call tools via HTTP
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True
)

# When agent decides to "search for Apple news":
# 1. Agent sends: {"action": "search_market_news", "query": "Apple earnings"}
# 2. Framework calls: HTTP POST localhost:8001/mcp
# 3. Service processes: search_market_news(query="Apple earnings")
# 4. Response returned: {"results": [...]}
# 5. Agent receives and analyzes results
```

---

### Layer 4: Configuration System

**Files:**
- `configs/default_config.json` - Stock trading config
- `configs/crypto_config.json` - Cryptocurrency trading config
- `tools/general_tools.py` - Runtime config management

#### Configuration Hierarchy

```
┌──────────────────────────────────┐
│ 1. Static Config Files (.json)   │
│    - Models list                 │
│    - Date ranges                 │
│    - Initial portfolio values    │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ 2. Runtime Configuration         │
│    (written to .runtime_env.json)│
│    - Current signature           │
│    - Today's date                │
│    - Trading status              │
└────────────────┬─────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ 3. Environment Variables         │
│    (override all others)         │
│    - INIT_DATE                   │
│    - END_DATE                    │
│    - OPENAI_API_KEY              │
└──────────────────────────────────┘
```

#### Config File Structure

```json
{
  "agent_type": "BaseAgent",

  "date_range": {
    "init_date": "2025-10-28",
    "end_date": "2025-11-02"
  },

  "models": [
    {
      "name": "gpt-4-turbo",
      "basemodel": "gpt-4-turbo",
      "signature": "gpt-4-turbo",
      "enabled": true,
      "openai_api_key": null,  // Uses env var if null
      "openai_base_url": null
    }
  ],

  "agent_config": {
    "max_steps": 30,
    "max_retries": 3,
    "base_delay": 0.5,
    "initial_cash": 10000.0
  },

  "log_config": {
    "log_path": "./data/agent_data",
    "log_prefix": "trading"
  }
}
```

---

## Trading Agent Logic

### Complete Trading Session Flow

```
TRADING SESSION (1 hour)
│
├─ PHASE 1: Initialization
│  ├─ Load configuration
│  ├─ Initialize LLM model
│  ├─ Connect to MCP services
│  └─ Set initial portfolio (cash: $10,000)
│
├─ PHASE 2: Market Data Fetch
│  ├─ Get price history (last 60 days)
│  ├─ Calculate technical indicators
│  │  ├─ SMA (Simple Moving Average)
│  │  ├─ RSI (Relative Strength Index)
│  │  └─ MACD
│  ├─ Search market news
│  └─ Prepare market context
│
├─ PHASE 3: LLM Decision Making (max 30 steps)
│  │
│  ├─ Step N:
│  │  ├─ Send market analysis to LLM
│  │  ├─ LLM thinks: "Given this data, what should I do?"
│  │  ├─ LLM response: "Buy 10 shares of AAPL at $150"
│  │  ├─ Validate order
│  │  └─ Execute trade (if valid)
│  │
│  ├─ Check exit condition
│  │  ├─ Max steps reached? → EXIT
│  │  ├─ LLM says done? → EXIT
│  │  └─ Cash depleted? → EXIT
│  │
│  └─ Loop back to Step N+1
│
├─ PHASE 4: Results Analysis
│  ├─ Calculate total P&L
│  ├─ Calculate return on investment
│  ├─ Create trading summary
│  └─ Log all transactions
│
└─ PHASE 5: Persistence
   ├─ Save agent data to JSONL
   ├─ Save position tracking
   ├─ Save trading logs
   └─ Ready for next hour
```

### System Prompt Example

```python
TRADING_SYSTEM_PROMPT = """
You are an expert AI trading assistant with access to:
- Real-time price data via get_price() tool
- Technical analysis via calculate_sma() tool
- Market news via search_market_news() tool
- Trading execution via execute_trade() tool
- Portfolio status via get_portfolio_status() tool

Your objective: Maximize portfolio value while managing risk.

Rules:
1. Only trade NASDAQ 100 stocks (list provided)
2. Maximum position size: 5% of portfolio
3. Daily loss limit: -10% of initial capital
4. Minimum RSI > 30 before buying
5. Sell if price drops >5% from entry

Available actions:
- get_price(symbol, date) → Get OHLCV data
- calculate_sma(prices, period) → Calculate 50-day average
- search_market_news(query) → Search news
- execute_trade(symbol, "buy"/"sell", quantity, price)
- get_portfolio_status() → Check positions
- done() → End trading session

Respond with action format:
{"action": "...", "args": {...}, "reason": "..."}
"""
```

---

## Data Flow

### Complete Data Journey

```
1. DATA FETCHING
   ├─ Stock prices
   │  └─ data/get_daily_price.py
   │     └─ Fetches from Alpha Vantage API
   │        └─ Stores in data/daily_price_*.json
   │
   ├─ Crypto prices
   │  └─ data/get_crypto_prices.py
   │     └─ Fetches from CoinGecko API (free, no auth)
   │        └─ Stores in data/crypto_prices_*.json
   │
   └─ Merging
      └─ data/merge_jsonl.py
         ├─ Reads all daily_price_*.json
         ├─ Reads all crypto_prices_*.json
         └─ Writes to data/merged.jsonl (103 lines)

2. TRADING EXECUTION (BaseAgent)
   ├─ Reads from merged.jsonl
   ├─ Calls MCP services
   ├─ Makes decisions
   ├─ Executes trades
   └─ Writes to data/agent_data/*.jsonl

3. RESULTS AGGREGATION
   ├─ Position tracking
   │  └─ data/agent_data/{model}/position/position.jsonl
   │
   ├─ Trading logs
   │  └─ data/agent_data/{model}/log/{date}/log.jsonl
   │
   └─ Dashboard data
      └─ docs/data/ (symlink to ../data/)
         └─ portfolio.html reads this data

4. DASHBOARD DISPLAY
   └─ https://pkrishnath.github.io/AI-Trader/
      ├─ Reads merged.jsonl
      ├─ Reads position.jsonl
      └─ Visualizes portfolio
```

### JSONL File Format

**merged.jsonl** (Price data for all symbols):
```json
{
  "Meta Data": {
    "1. Information": "Daily Prices (buy price, high, low, sell price) and Volumes",
    "2. Symbol": "AAPL"
  },
  "Time Series (Daily)": {
    "2025-11-02": {"1. buy price": "150.25"},
    "2025-11-01": {"1. buy price": "149.80", "2. high": "151.50", ...}
  }
}
```

**position.jsonl** (Portfolio positions):
```json
{
  "timestamp": "2025-11-02T13:30:00Z",
  "symbol": "AAPL",
  "quantity": 10,
  "avg_cost": 150.25,
  "current_price": 151.50,
  "position_value": 1515.00,
  "unrealized_pnl": 12.50
}
```

---

## Docker Containerization

### Why Docker?

**Problem:** MCP services failing to start in GitHub Actions as background processes.

**Solution:** Docker containers provide:
- Isolated environments
- Automatic restart on failure
- Health checks
- Network isolation
- Consistent behavior across platforms

### Docker Architecture

```
docker-compose.yml (Orchestrator)
│
├─ math-service (Port 8000)
│  ├─ Image: Python 3.11-slim
│  ├─ Dockerfile: agent_tools/Dockerfile.math
│  ├─ Health Check: GET /health every 5s
│  └─ Starts: python agent_tools/tool_math.py
│
├─ search-service (Port 8001)
│  ├─ Dockerfile: agent_tools/Dockerfile.search
│  ├─ Env: PYTHONPATH=/app, JINA_API_KEY=${JINA_API_KEY}
│  └─ Starts: python agent_tools/tool_jina_search.py
│
├─ trade-service (Port 8002)
│  ├─ Dockerfile: agent_tools/Dockerfile.trade
│  ├─ Volumes: ./data:/app/data, ./configs:/app/configs
│  └─ Starts: python agent_tools/tool_trade.py
│
└─ prices-service (Port 8003)
   ├─ Dockerfile: agent_tools/Dockerfile.prices
   ├─ Volumes: ./data:/app/data
   └─ Starts: python agent_tools/tool_get_price_local.py

Network: mcp-network (bridge)
└─ All services communicate via internal Docker DNS
```

### Dockerfile Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY agent_tools/ /app/agent_tools/
COPY tools/ /app/tools/

# Set Python path for imports
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/health')"

# Run service
CMD ["python", "agent_tools/tool_trade.py"]
```

### Running Docker Services

```bash
# Build images
docker compose -f docker-compose.yml build

# Start services (detached)
docker compose -f docker-compose.yml up -d

# Check status
docker compose -f docker-compose.yml ps

# View logs
docker compose -f docker-compose.yml logs -f math-service

# Stop services
docker compose -f docker-compose.yml down
```

---

## GitHub Actions Automation

### Hourly Trading Workflow

**File:** `.github/workflows/hourly-trading.yml`

```yaml
name: Hourly AI Trading Run

on:
  schedule:
    - cron: '0 * * * *'  # Every hour
  workflow_dispatch      # Manual trigger

jobs:
  trading-run:
    runs-on: ubuntu-latest

    steps:
      # 1. Checkout code
      - uses: actions/checkout@v4

      # 2. Setup Python
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      # 3. Install dependencies
      - run: pip install -r requirements.txt

      # 4. Fetch price data
      - run: |
          cd data
          python get_daily_price.py      # Stock prices
          python get_crypto_prices.py    # Crypto prices
          python merge_jsonl.py          # Merge all
          cd ..

      # 5. Start Docker services
      - uses: docker/setup-buildx-action@v3
      - run: |
          docker compose -f docker-compose.yml build
          docker compose -f docker-compose.yml up -d
          sleep 30  # Wait for startup

      # 6. Run trading simulation
      - run: python main.py configs/crypto_config.json
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          JINA_API_KEY: ${{ secrets.JINA_API_KEY }}

      # 7. Upload results
      - uses: actions/upload-artifact@v4
        with:
          name: trading-results
          path: data/agent_data/

      # 8. Stop Docker
      - run: docker compose -f docker-compose.yml down
```

### Workflow Execution Timeline

```
+00:00 - Trigger (top of hour)
  ├─ Checkout code
  ├─ Setup Python (30s)
  ├─ Install dependencies (60s)
  ├─ Fetch price data (30s)
  │  ├─ Alpha Vantage API calls
  │  ├─ CoinGecko API calls
  │  └─ Merge results
  │
+02:30 - Build and start Docker (60s)
  ├─ Build 4 images
  ├─ Start containers
  └─ Health check
  │
+03:30 - Trading simulation (60s)
  ├─ Connect to MCP services
  ├─ Fetch market data
  ├─ 30 trading steps
  │  ├─ LLM analysis
  │  └─ Trade execution
  └─ Save results
  │
+04:30 - Upload artifacts (30s)
  ├─ Upload trading results
  ├─ Upload merged data
  └─ Create report
  │
+05:00 - Complete
  └─ Total duration: ~5 minutes
```

---

## Key Code Examples

### Example 1: Making a Trade Decision

```python
# In BaseAgent.run_trading_session()

# Step 1: Fetch market data
current_price = self.get_price("AAPL")  # Call Prices Service
news = self.search_market_news("Apple earnings")  # Call Search Service

# Step 2: Prepare context for LLM
market_context = f"""
Current AAPL price: ${current_price['close']}
50-day MA: ${calculate_sma(price_history, 50)}
Latest news: {news['results'][0]['title']}

Given this context, what should I do?
"""

# Step 3: Get LLM decision
response = await self.model.apredict(market_context)
# Response: "Buy 10 shares of AAPL because price is below MA"

# Step 4: Execute trade
trade_result = self.execute_trade("AAPL", "buy", 10, current_price['close'])

# Step 5: Update portfolio
self.portfolio.add_position("AAPL", 10, current_price['close'])
```

### Example 2: MCP Service Health Check

```python
# In BaseAgent._init_mcp_services()

import httpx

async def check_service_health(url: str, max_retries: int = 30):
    """Check if MCP service is healthy"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/health", timeout=3.0)
                if response.status_code == 200:
                    return True
        except httpx.RequestError:
            pass

        await asyncio.sleep(2)  # Wait 2 seconds before retry

    raise TimeoutError(f"Service {url} did not start within 60 seconds")

# Check all services
await check_service_health("http://localhost:8000")  # Math
await check_service_health("http://localhost:8001")  # Search
await check_service_health("http://localhost:8002")  # Trade
await check_service_health("http://localhost:8003")  # Prices
```

### Example 3: Configuration Override

```python
# In main.py

# 1. Load static config
config = load_config("configs/crypto_config.json")

# 2. Override with environment variables
if os.getenv("INIT_DATE"):
    config["date_range"]["init_date"] = os.getenv("INIT_DATE")

if os.getenv("OPENAI_API_KEY"):
    for model in config["models"]:
        model["openai_api_key"] = os.getenv("OPENAI_API_KEY")

# 3. Pass to agent
agent = BaseAgent(
    signature=config["models"][0]["signature"],
    basemodel=config["models"][0]["basemodel"],
    initial_cash=config["agent_config"]["initial_cash"]
)
```

---

## Summary

The AI-Trader architecture demonstrates:

1. **Modular Design:** Clear separation between agent logic, services, and orchestration
2. **Microservices:** FastMCP provides isolated, scalable services
3. **LLM Integration:** Seamless connection to multiple AI providers
4. **Automation:** GitHub Actions orchestrates hourly trading
5. **Containerization:** Docker ensures reliability and consistency
6. **Data Pipeline:** Clean flow from data fetching to dashboard display
7. **Extensibility:** Add new agents, models, or services without modifying core code

This architecture is production-ready and can handle:
- 24/7 automated trading
- Multiple LLM providers
- Both stocks and cryptocurrencies
- Portfolio tracking and reporting
- Comprehensive logging and error handling
