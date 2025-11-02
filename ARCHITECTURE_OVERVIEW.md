# AI-Trader Comprehensive Architecture & Technical Overview

## Executive Summary

AI-Trader is a sophisticated AI-powered automated trading system that simulates stock and cryptocurrency trading using Language Models (LLMs) orchestrated through Model Control Protocol (MCP) services. It supports multiple AI providers (OpenAI, Anthropic Claude, DeepSeek) and uses FastMCP-based microservices for tool execution.

**Key Statistics:**
- 22 Python files across 7 major modules
- 4 containerized MCP services (Math, Search, Trade, Prices)
- Multi-model support with configurable LLM selection
- Comprehensive GitHub Actions CI/CD automation
- Support for both stock and cryptocurrency trading

---

## 1. Project Structure & Directories

```
/Users/krish/code/github/AI-Trader/
├── agent/                           # AI Agent implementations
│   └── base_agent/
│       ├── __init__.py
│       └── base_agent.py           # Core agent class (595 lines)
│
├── agent_tools/                     # MCP service implementations
│   ├── Dockerfile.math              # Math service container
│   ├── Dockerfile.prices            # Price service container
│   ├── Dockerfile.search            # Search service container
│   ├── Dockerfile.trade             # Trade service container
│   ├── start_mcp_services.py       # MCP service launcher
│   ├── tool_math.py                 # Math operations MCP service
│   ├── tool_jina_search.py          # Web search MCP service
│   ├── tool_trade.py                # Trade execution MCP service
│   └── tool_get_price_local.py      # Local price lookup MCP service
│
├── tools/                           # Utility tools & business logic
│   ├── __init__.py
│   ├── general_tools.py             # Config management, conversation parsing
│   ├── price_tools.py               # Stock price & position management
│   ├── result_tools.py              # Trade results aggregation
│   └── crypto_tools.py              # Cryptocurrency price tools
│
├── prompts/                         # System prompts for agents
│   ├── agent_prompt.py              # Stock trading agent prompts
│   └── crypto_agent_prompt.py       # Cryptocurrency trading prompts
│
├── configs/                         # Configuration files
│   ├── default_config.json          # Default trading configuration
│   └── crypto_config.json           # Cryptocurrency trading config
│
├── data/                            # Trading data
│   ├── daily_prices_*.json          # Stock price data (100+ files)
│   ├── crypto_prices_*.json         # Cryptocurrency price data
│   ├── merged.jsonl                 # Merged price data
│   └── agent_data/                  # Trading results
│       ├── gpt-4-turbo/
│       ├── claude-3.7-sonnet/
│       ├── deepseek-chat-v3.1/
│       ├── gemini-2.5-flash/
│       ├── gpt-5/
│       └── qwen3-max/               # Per-model trading results
│
├── .github/workflows/               # GitHub Actions CI/CD
│   ├── hourly-trading.yml           # Hourly automated trading
│   ├── tests.yml                    # Testing & validation
│   ├── claude.yml                   # Claude Code integration
│   ├── claude-code-review.yml       # Code review automation
│   └── deploy-github-pages.yml      # Documentation deployment
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── test_config.py               # Configuration validation tests
│   └── test_tools.py                # Tool functionality tests
│
├── main.py                          # Application entry point
├── docker-compose.yml               # Docker Compose configuration
├── requirements.txt                 # Python dependencies
├── .runtime_env.json                # Runtime configuration
├── .env.example                     # Environment template
└── [Documentation files]            # README, guides, etc.
```

---

## 2. Key Entry Points

### 2.1 Main Application Entry Point

**File:** `/Users/krish/code/github/AI-Trader/main.py`

**Purpose:** Primary orchestrator for trading simulations

**Key Functions:**

```python
get_agent_class(agent_type)
  - Dynamically imports and instantiates agent classes
  - Supports extensible agent architecture via AGENT_REGISTRY
  - Validates agent type against registry
  
load_config(config_path=None)
  - Loads JSON configuration files from configs/ directory
  - Validates config file exists and is valid JSON
  - Returns configuration dictionary
  
async main(config_path=None)
  - Loads configuration
  - Initializes agents based on config
  - Processes enabled models sequentially
  - Runs trading simulations across date ranges
  - Handles error reporting and logging
```

**Configuration Flow:**
1. Accept optional config file path via command line
2. Load default or specified config (JSON)
3. Validate date ranges and model configurations
4. Override INIT_DATE/END_DATE from environment if provided
5. For each enabled model:
   - Load model signature, basemodel, API keys
   - Create agent instance
   - Initialize MCP connections
   - Run trading session across date range

**Supported Models (from config):**
- gpt-4-turbo (basemodel: gpt-4-turbo)
- gpt-4o (basemodel: gpt-4o)
- claude-3.5-sonnet (basemodel: anthropic/claude-3.5-sonnet)
- deepseek-chat-v3.1 (basemodel: deepseek/deepseek-chat-v3.1)

---

### 2.2 BaseAgent - Core Trading Agent

**File:** `/Users/krish/code/github/AI-Trader/agent/base_agent/base_agent.py` (595 lines)

**Purpose:** Core intelligent agent orchestrating trading decisions

**Class: BaseAgent**

**Initialization Parameters:**
```python
signature: str              # Agent identifier (e.g., "gpt-4-turbo")
basemodel: str              # Model name (e.g., "gpt-4-turbo")
stock_symbols: List[str]    # Tradeable assets (defaults to NASDAQ 100)
mcp_config: Dict            # MCP service endpoints
log_path: str               # Trading results directory
max_steps: int              # Max reasoning steps per session (default: 10)
max_retries: int            # Retry attempts on failure (default: 3)
base_delay: float           # Base retry delay in seconds
openai_base_url: str        # Custom OpenAI API endpoint
openai_api_key: str         # API authentication key
initial_cash: float         # Starting portfolio value ($10,000)
init_date: str              # Initialization date (YYYY-MM-DD)
```

**Core Components:**

```
1. MCP Client Management
   - MultiServerMCPClient handles 4 MCP services
   - Dynamically loads tools from services
   - Supports HTTP-based tool communication
   
2. AI Model Integration
   - ChatAnthropic for Claude models
   - ChatOpenAI for GPT/custom models
   - Configurable API base URLs and keys
   
3. Agent Workflow
   - create_agent() from langchain
   - System prompt generation per trading session
   - Tool invocation loop with max_steps limit
   - STOP_SIGNAL detection for session termination
   
4. Trading Session Execution
   - Per-date trading logic
   - Logging to JSONL files
   - Position tracking and validation
   - Error handling with retries
```

**Default MCP Configuration:**
```json
{
  "math": "http://localhost:8000/mcp",
  "stock_local": "http://localhost:8003/mcp",
  "search": "http://localhost:8001/mcp",
  "trade": "http://localhost:8002/mcp"
}
```

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `async initialize()` | Initialize MCP client, load tools, create AI model |
| `async run_trading_session(today_date)` | Execute trading for single day |
| `async _ainvoke_with_retry(message)` | Agent invocation with exponential backoff |
| `register_agent()` | Create initial position file |
| `get_trading_dates(init_date, end_date)` | Generate trading date list (weekdays only) |
| `async run_date_range(init_date, end_date)` | Process all trading days |
| `get_position_summary()` | Retrieve final portfolio positions |

**Default Stock Universe (NASDAQ 100):**
100 tech/growth stocks: NVDA, MSFT, AAPL, GOOG, GOOGL, AMZN, META, AVGO, TSLA, NFLX, PLTR, COST, ASML, AMD, CSCO, AZN, TMUS, MU, LIN, PEP, SHOP, APP, INTU, AMAT, LRCX, PDD, QCOM, ARM, INTC, BKNG, AMGN, TXN, ISRG, GILD, KLAC, PANW, ADBE, HON, CRWD, CEG, ADI, ADP, DASH, CMCSA, VRTX, MELI, SBUX, CDNS, ORLY, SNPS, MSTR, MDLZ, ABNB, MRVL, CTAS, TRI, MAR, MNST, CSX, ADSK, PYPL, FTNT, AEP, WDAY, REGN, ROP, NXPI, DDOG, AXON, ROST, IDXX, EA, PCAR, FAST, EXC, TTWO, XEL, ZS, PAYX, WBD, BKR, CPRT, CCEP, FANG, TEAM, CHTR, KDP, MCHP, GEHC, VRSK, CTSH, CSGP, KHC, ODFL, DXCM, TTD, ON, BIIB, LULU, CDW, GFS

---

## 3. MCP Services Architecture (FastMCP)

### 3.1 Overview

Model Control Protocol (MCP) services provide isolated, containerized tools accessed by agents via HTTP. Each service is a FastMCP application exposing trading-related functions.

**Service Communication Flow:**
```
BaseAgent (LangChain) 
    ↓
MultiServerMCPClient (langchain_mcp_adapters)
    ↓ HTTP StreamableHTTP
    ├→ Math Service (port 8000)
    ├→ Search Service (port 8001)
    ├→ Trade Service (port 8002)
    └→ Price Service (port 8003)
```

### 3.2 MCP Service #1: Math Operations

**File:** `/Users/krish/code/github/AI-Trader/agent_tools/tool_math.py`

**Purpose:** Basic arithmetic operations for trading calculations

**Tools:**
```python
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers (supports int and float)"""
    return float(a) + float(b)

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers (supports int and float)"""
    return float(a) * float(b)
```

**Containerization:**
- **Dockerfile:** `agent_tools/Dockerfile.math`
- **Port:** 8000 (configurable via MATH_HTTP_PORT)
- **Transport:** streamable-http

### 3.3 MCP Service #2: Web Search (Jina)

**File:** `/Users/krish/code/github/AI-Trader/agent_tools/tool_jina_search.py`

**Purpose:** Web search and market news retrieval

**Key Features:**
- Uses Jina API for web scraping
- Date format parsing (handles relative dates like "4 hours ago")
- HTML to Markdown conversion
- Supports ISO 8601, relative time, and natural language dates

**Helper Functions:**
```python
parse_date_to_standard(date_str) -> str
  - Converts various date formats to YYYY-MM-DD HH:MM:SS
  - Handles: "4 hours ago", "May 31, 2025", ISO 8601, etc.
```

**Containerization:**
- **Dockerfile:** `agent_tools/Dockerfile.search`
- **Port:** 8001 (SEARCH_HTTP_PORT)
- **Environment:** JINA_API_KEY required

### 3.4 MCP Service #3: Trade Execution

**File:** `/Users/krish/code/github/AI-Trader/agent_tools/tool_trade.py`

**Purpose:** Stock buying and selling with position tracking

**Key Tools:**

```python
@mcp.tool()
def buy(symbol: str, amount: int) -> Dict[str, Any]:
    """
    Buy stock function
    
    Steps:
    1. Get current position and operation ID
    2. Get stock opening price for the day
    3. Validate buy conditions (sufficient cash)
    4. Update position (increase stock quantity, decrease cash)
    5. Record transaction to position.jsonl file
    
    Returns:
        New position dict or error dict
    """
    
def sell(symbol: str, amount: int) -> Dict[str, Any]:
    """
    Sell stock function
    
    Similar to buy but:
    - Checks stock quantity availability
    - Increases cash balance
    - Records sell transaction
    """
```

**Data Flow:**
1. Read signature (agent identifier) from runtime config
2. Fetch current position from `{data_path}/{signature}/position/position.jsonl`
3. Get opening price for symbol from price service
4. Validate transaction (sufficient cash for buy, sufficient shares for sell)
5. Update position dictionary
6. Append new transaction to JSONL position file

**Position File Format:**
```jsonl
{"date": "2025-10-28", "id": 0, "positions": {"AAPL": 0, "MSFT": 0, "CASH": 10000.0, ...}}
{"date": "2025-10-28", "id": 1, "positions": {"AAPL": 10, "MSFT": 0, "CASH": 9900.0, ...}}
```

**Containerization:**
- **Dockerfile:** `agent_tools/Dockerfile.trade`
- **Port:** 8002 (TRADE_HTTP_PORT)
- **Volumes:** ./data, ./configs (required for position tracking)

### 3.5 MCP Service #4: Local Price Data

**File:** `/Users/krish/code/github/AI-Trader/agent_tools/tool_get_price_local.py`

**Purpose:** Query OHLCV data from local JSON files

**Tool:**
```python
@mcp.tool()
def get_price_local(symbol: str, date: str) -> Dict[str, Any]:
    """
    Read OHLCV data for specified stock and date
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'MSFT')
        date: Date in YYYY-MM-DD format
        
    Returns:
        {
            "symbol": "AAPL",
            "date": "2025-10-28",
            "ohlcv": {
                "open": 234.50,
                "high": 236.20,
                "low": 233.10,
                "close": 235.80,
                "volume": 45000000
            }
        }
    """
```

**Data Source:**
- Primary: `data/merged.jsonl` (combined JSONL format)
- Fallback: `data/daily_prices_{SYMBOL}.json` (individual stock files)
- Cryptocurrency: `data/crypto_prices_{BTC|ETH}.json`

**Data Format (JSONL):**
```json
{
  "Meta Data": {"2. Symbol": "AAPL"},
  "Time Series (Daily)": {
    "2025-10-28": {
      "1. buy price": "234.50",
      "2. high": "236.20",
      "3. low": "233.10",
      "4. sell price": "235.80",
      "5. volume": "45000000"
    }
  }
}
```

**Containerization:**
- **Dockerfile:** `agent_tools/Dockerfile.prices`
- **Port:** 8003 (GETPRICE_HTTP_PORT)
- **Volumes:** ./data (read-only for price data)

### 3.6 MCP Service Manager

**File:** `/Users/krish/code/github/AI-Trader/agent_tools/start_mcp_services.py`

**Purpose:** Initialize and manage lifecycle of all 4 MCP services

**Class: MCPServiceManager**

**Features:**
```python
- Loads port configuration from environment variables
- Starts all services as subprocess instances
- Monitors service health via port connectivity checks
- Implements graceful shutdown with signal handlers
- Creates individual log files per service
- Provides status reporting
```

**Usage:**
```bash
# Start all services
python agent_tools/start_mcp_services.py

# Check service status
python agent_tools/start_mcp_services.py status
```

**Port Configuration (Environment Variables):**
- MATH_HTTP_PORT=8000
- SEARCH_HTTP_PORT=8001
- TRADE_HTTP_PORT=8002
- GETPRICE_HTTP_PORT=8003

---

## 4. Configuration System

### 4.1 Configuration Hierarchy

```
Environment Variables (.env)
    ↓
Runtime Config (.runtime_env.json)
    ↓
Trading Config (configs/*.json)
```

### 4.2 Runtime Configuration

**File:** `/Users/krish/code/github/AI-Trader/.runtime_env.json`

**Purpose:** Persistent runtime state during trading sessions

**Typical Contents:**
```json
{
  "SIGNATURE": "gpt-4-turbo",
  "TODAY_DATE": "2025-11-02",
  "IF_TRADE": false,
  "MATH_HTTP_PORT": 8000,
  "SEARCH_HTTP_PORT": 8001,
  "TRADE_HTTP_PORT": 8002,
  "GETPRICE_HTTP_PORT": 8003
}
```

**Management Functions:**

```python
# tools/general_tools.py

def get_config_value(key: str, default=None):
    """Get config value from runtime or environment"""
    _RUNTIME_ENV = _load_runtime_env()
    if key in _RUNTIME_ENV:
        return _RUNTIME_ENV[key]
    return os.getenv(key, default)

def write_config_value(key: str, value: Any):
    """Persist config value to runtime file"""
    _RUNTIME_ENV = _load_runtime_env()
    _RUNTIME_ENV[key] = value
    # Write to .runtime_env.json
```

### 4.3 Trading Configuration Files

**File:** `/Users/krish/code/github/AI-Trader/configs/default_config.json`

**Structure:**
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
      "openai_base_url": null,
      "openai_api_key": null
    }
  ],
  "agent_config": {
    "max_steps": 30,
    "max_retries": 3,
    "base_delay": 1.0,
    "initial_cash": 10000.0
  },
  "log_config": {
    "log_path": "./data/agent_data"
  }
}
```

**Cryptocurrency Configuration:**

**File:** `/Users/krish/code/github/AI-Trader/configs/crypto_config.json`

```json
{
  "agent_type": "BaseAgent",
  "crypto_mode": true,
  "trading_universe": ["BTC", "ETH"],
  "models": [
    {
      "name": "gpt-4o",
      "basemodel": "gpt-4o",
      "signature": "gpt-4o-crypto-trader",
      "enabled": true
    }
  ],
  "agent_config": {
    "crypto_trading": true,
    "description": "Cryptocurrency trading with Bitcoin (BTC) and Ethereum (ETH)"
  }
}
```

---

## 5. Data Flow and Trading Logic

### 5.1 Complete Trading Session Flow

```
1. INITIALIZATION
   ├─ Load configuration (JSON)
   ├─ Select enabled models
   ├─ Validate API keys
   └─ Create BaseAgent instances

2. MCP SERVICE STARTUP
   ├─ Start 4 FastMCP services (ports 8000-8003)
   ├─ Health check all services
   └─ Verify tool availability

3. AGENT INITIALIZATION (per model)
   ├─ Create MultiServerMCPClient
   ├─ Load tools from all 4 services
   ├─ Initialize ChatOpenAI/ChatAnthropic model
   └─ Create LangChain agent

4. TRADING DATE RANGE PROCESSING
   ├─ Parse init_date and end_date
   ├─ Generate weekday-only trading dates
   └─ For each trading date:
      
      5. DAILY TRADING SESSION
         ├─ Setup logging (JSONL)
         ├─ Generate system prompt with:
         │  ├─ Current date
         │  ├─ Position from yesterday
         │  ├─ Yesterday's prices
         │  └─ Today's opening prices
         ├─ Create agent with system prompt
         ├─ User Query: "Analyze today's positions"
         │
         ├─ AGENT LOOP (max_steps times)
         │  ├─ Agent reasoning
         │  ├─ Tool invocation (buy/sell/search/prices)
         │  ├─ Receive tool results
         │  ├─ Log conversation
         │  └─ Check for STOP_SIGNAL
         │
         └─ Save results to position.jsonl

5. POSITION TRACKING
   ├─ Store daily positions in JSONL
   ├─ Maintain position history
   └─ Track portfolio value

6. RESULTS AGGREGATION
   ├─ Generate position summary
   ├─ Calculate performance metrics
   └─ Export reports
```

### 5.2 Position File Structure

**Location:** `data/agent_data/{SIGNATURE}/position/position.jsonl`

**Format (one position per line):**
```json
{
  "date": "2025-10-28",
  "id": 0,
  "positions": {
    "AAPL": 10,
    "MSFT": 5,
    "GOOGL": 0,
    "TSLA": 0,
    "CASH": 7500.25,
    [... 95 more stocks ...]
  }
}
```

**ID Semantics:**
- Incremented per transaction within a day
- Identifies transaction ordering
- Helps reconstruct decision sequence

### 5.3 Logging Structure

**Location:** `data/agent_data/{SIGNATURE}/log/{DATE}/log.jsonl`

**Format:**
```json
{
  "timestamp": "2025-11-02T14:30:45.123456",
  "signature": "gpt-4-turbo",
  "new_messages": [
    {
      "role": "user",
      "content": "Please analyze today's positions."
    }
  ]
}
```

---

## 6. Docker Containerization

### 6.1 Docker Compose Architecture

**File:** `/Users/krish/code/github/AI-Trader/docker-compose.yml`

**Network Topology:**
```
            mcp-network (bridge)
                    ↓
        ┌───────────┬───────────┬───────────┬───────────┐
        ↓           ↓           ↓           ↓           ↓
    math-service  search-service trade-service prices-service
    (port 8000)   (port 8001)   (port 8002)   (port 8003)
```

### 6.2 Service Definitions

**All Services:**
- Base Image: `python:3.11-slim`
- Health Check: HTTP endpoint on service port
- Interval: 5s, Timeout: 3s, Retries: 5, Start Period: 5s

### Service #1: Math Service

```yaml
math-service:
  build:
    context: .
    dockerfile: agent_tools/Dockerfile.math
  ports:
    - "8000:8000"
  environment:
    - MATH_HTTP_PORT=8000
  networks:
    - mcp-network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
```

### Service #2: Search Service

```yaml
search-service:
  build:
    context: .
    dockerfile: agent_tools/Dockerfile.search
  ports:
    - "8001:8001"
  environment:
    - SEARCH_HTTP_PORT=8001
    - JINA_API_KEY=${JINA_API_KEY}
    - PYTHONPATH=/app
  networks:
    - mcp-network
```

### Service #3: Trade Service

```yaml
trade-service:
  build:
    context: .
    dockerfile: agent_tools/Dockerfile.trade
  ports:
    - "8002:8002"
  environment:
    - TRADE_HTTP_PORT=8002
    - PYTHONPATH=/app
  networks:
    - mcp-network
  volumes:
    - ./data:/app/data          # Position files
    - ./configs:/app/configs    # Config files
```

### Service #4: Prices Service

```yaml
prices-service:
  build:
    context: .
    dockerfile: agent_tools/Dockerfile.prices
  ports:
    - "8003:8003"
  environment:
    - GETPRICE_HTTP_PORT=8003
    - PYTHONPATH=/app
  networks:
    - mcp-network
  volumes:
    - ./data:/app/data          # Price data files
```

### 6.3 Individual Dockerfiles

**Pattern (all services):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent_tools/ /app/agent_tools/
COPY tools/ /app/tools/
COPY data/ /app/data/              # (Trade & Prices only)
COPY configs/ /app/configs/         # (Trade only)

EXPOSE {PORT}

HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:{PORT}/health')" || exit 1

CMD ["python", "agent_tools/tool_{SERVICE}.py"]
```

---

## 7. GitHub Actions Workflows

### 7.1 Hourly Trading Workflow

**File:** `.github/workflows/hourly-trading.yml`

**Trigger:** 
- `0 * * * *` (Every hour at minute 0)
- Manual trigger via `workflow_dispatch`
- Push to main with changes to configs/, agent/, main.py

**Execution Steps:**

```yaml
1. Checkout Repository
   └─ Get latest code (depth: 1)

2. Setup Python 3.11
   └─ Cache pip dependencies

3. Install Dependencies
   └─ pip install -r requirements.txt

4. Configure Environment
   └─ Copy .env.example → .env
   └─ Add API keys from GitHub Secrets:
      • OPENAI_API_KEY
      • ALPHAADVANTAGE_API_KEY
      • JINA_API_KEY

5. Fetch & Prepare Price Data
   └─ python data/get_daily_price.py      (Stock prices)
   └─ python data/get_crypto_prices.py    (BTC/ETH prices)
   └─ python data/merge_jsonl.py          (Combine all data)

6. Setup Docker Buildx
   └─ Enable multi-platform builds

7. Start MCP Services
   ├─ docker compose -f docker-compose.yml build
   ├─ docker compose -f docker-compose.yml up -d
   ├─ Wait 30 seconds for startup
   └─ Verify all containers running

8. Run Trading Simulation
   ├─ python main.py configs/crypto_config.json
   ├─ Timeout: 30 minutes
   ├─ Environment: API keys, PYTHONUNBUFFERED
   └─ Exit on completion

9. Upload Trading Results
   ├─ Artifact: trading-results-${RUN_ID}
   ├─ Path: data/agent_data/
   └─ Retention: 30 days

10. Upload Merged Data
    ├─ Artifact: merged-data-${RUN_ID}
    ├─ Path: data/merged.jsonl
    └─ Retention: 30 days

11. Verify Data Accessibility
    └─ Check symlink: docs/data → ../data

12. Stop Docker Containers
    └─ docker compose -f docker-compose.yml down

13. Generate Trading Report
    └─ Create trading_report.md summary

14. Slack Notification (if webhook configured)
    └─ Send status to Slack channel
```

**Environment Variables:**
```bash
AGENT_MAX_STEP=30
PYTHONUNBUFFERED=1
OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
ALPHAADVANTAGE_API_KEY=${{ secrets.ALPHAADVANTAGE_API_KEY }}
JINA_API_KEY=${{ secrets.JINA_API_KEY }}
```

### 7.2 Tests & Validation Workflow

**File:** `.github/workflows/tests.yml`

**Trigger:** Push/PR to main or develop

**Jobs:**

1. **Linting (flake8, black, isort)**
   - Code quality checks
   - Formatting validation
   - Import sorting

2. **Unit Tests (pytest)**
   - Run: `pytest tests/ -v --cov=. --cov-report=xml`
   - Coverage upload to Codecov
   - Parallelizable test execution

3. **Configuration Validation**
   - JSON schema validation
   - Environment template check
   - Required fields verification

4. **Security Scanning (bandit)**
   - Detect security vulnerabilities
   - Check for hardcoded secrets
   - Generate JSON report

5. **Dependency Audit**
   - Safety check for known vulnerabilities
   - Pip-audit for dependency analysis
   - Continue-on-error to not block

### 7.3 Claude Code Integration

**File:** `.github/workflows/claude.yml`

**Trigger:**
- `@claude` mention in issue comments
- `@claude` mention in PR review comments
- `@claude` in issue/PR title or body

**Capabilities:**
- Automated code review
- PR description updates
- Issue triage
- Code suggestions

### 7.4 Secrets Required

```
OPENAI_API_KEY              (Required for trading)
ALPHAADVANTAGE_API_KEY      (Optional, for stock data)
JINA_API_KEY                (Required for web search)
CLAUDE_CODE_OAUTH_TOKEN     (Optional, for Claude integration)
SLACK_WEBHOOK               (Optional, for notifications)
```

---

## 8. Supporting Tools and Utilities

### 8.1 General Tools

**File:** `/Users/krish/code/github/AI-Trader/tools/general_tools.py`

**Functions:**

```python
def get_config_value(key: str, default=None):
    """Get config from runtime or environment"""

def write_config_value(key: str, value: Any):
    """Persist config value to .runtime_env.json"""

def extract_conversation(conversation: dict, output_type: str):
    """
    Extract from LangChain conversation object
    output_type: 'final' (last message) or 'all' (all messages)
    """

def extract_tool_messages(conversation: dict):
    """Extract ToolMessage objects from conversation"""

def extract_first_tool_message_content(conversation: dict):
    """Get content of first tool message"""
```

### 8.2 Price Tools

**File:** `/Users/krish/code/github/AI-Trader/tools/price_tools.py`

**Functions:**

```python
def get_open_prices(date: str, symbols: List[str]) -> Dict:
    """Get opening prices for symbols on date"""

def get_latest_position(date: str, signature: str) -> Tuple:
    """Get most recent position for agent"""

def get_today_init_position(signature: str) -> Dict:
    """Get initial position at trading session start"""

def get_yesterday_date(today: str) -> str:
    """Get previous trading day (handles weekends)"""

def get_yesterday_open_and_close_price(symbol: str, today: str) -> Tuple:
    """Get yesterday's OHLC data"""

def get_yesterday_profit(symbol: str, signature: str) -> float:
    """Calculate previous day's profit/loss"""

def add_no_trade_record(date: str, signature: str):
    """Record no-trade decision in position file"""
```

### 8.3 Crypto Tools

**File:** `/Users/krish/code/github/AI-Trader/tools/crypto_tools.py`

**Supported Assets:** BTC, ETH

**Functions:**

```python
def load_crypto_price_data(crypto_symbol: str) -> Dict:
    """Load price data from crypto_prices_*.json"""

def get_crypto_price_on_date(symbol: str, date: str, 
                            price_type: str = "close") -> Optional[float]:
    """Get specific price (open/close/high/low)"""

def get_crypto_prices_range(symbol: str, start_date: str, 
                           end_date: str) -> Dict:
    """Get prices for date range"""

def get_crypto_latest_price(symbol: str) -> Optional[float]:
    """Get latest available price"""

def format_crypto_price_data(prices: Dict, symbol: str) -> str:
    """Format prices for display in prompts"""
```

### 8.4 Result Tools

**File:** `/Users/krish/code/github/AI-Trader/tools/result_tools.py` (27,107 bytes)

**Purpose:** Trade results aggregation and analysis

**Functions:**
```python
def calculate_portfolio_value(positions: Dict, prices: Dict, 
                             cash: float = 0.0) -> float:
    """Calculate total portfolio value"""

def get_available_date_range(modelname: str) -> Tuple[str, str]:
    """Get earliest and latest trading dates for model"""

def [Additional analysis functions...]
```

### 8.5 Agent Prompts

**Stock Trading Prompt:**

**File:** `/Users/krish/code/github/AI-Trader/prompts/agent_prompt.py`

```python
STOP_SIGNAL = "<FINISH_SIGNAL>"

system_prompt = """
You are a stock trading assistant for NASDAQ 100 companies.

Your goals are:
- Analyze market trends
- Make informed trading decisions
- Maximize portfolio returns

Thinking standards:
- Show key intermediate steps
- Read current positions and cash
- Analyze today's prices
- Decide buy/sell actions
- Execute via tools

Notes:
- You can execute directly
- Implement via tools only
- Available tools: price checking, order execution, position tracking

[... followed by runtime data: date, positions, prices ...]

When complete, output: <FINISH_SIGNAL>
"""
```

**Cryptocurrency Trading Prompt:**

**File:** `/Users/krish/code/github/AI-Trader/prompts/crypto_agent_prompt.py`

```python
crypto_system_prompt = """
You are a cryptocurrency trading assistant for BTC and ETH.

Your goals are:
- Analyze crypto market trends
- Make informed trading decisions
- Maximize portfolio returns
- Use available tools to gather data

[... structured similarly to stock prompt ...]

Trading universe: BTC (Bitcoin), ETH (Ethereum)
Each crypto supports fractional amounts.

[... date, positions, prices ...]

When complete, output: <FINISH_SIGNAL>
"""
```

---

## 9. Testing Infrastructure

### 9.1 Test Configuration

**File:** `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### 9.2 Configuration Tests

**File:** `/Users/krish/code/github/AI-Trader/tests/test_config.py`

**Test Classes:**

1. **TestConfigLoading**
   - Default config file exists
   - Valid JSON format
   - Required fields present
   - Initial cash configuration
   - Runtime env file exists and is valid
   - .env.example exists with required variables

2. **TestConfigValidation**
   - Date range format validation
   - Models list not empty
   - Model has required fields (name, basemodel)

### 9.3 Tool Tests

**File:** `/Users/krish/code/github/AI-Trader/tests/test_tools.py`

Tests for:
- Price data retrieval
- Position file operations
- Configuration persistence
- Cryptographic trading tools

---

## 10. Dependencies

**File:** `requirements.txt`

```
langchain==1.0.2
langchain-openai==1.0.1
langchain-anthropic>=0.1.0
langchain-mcp-adapters>=0.1.0
fastmcp==2.12.5
```

**Additional (from GitHub Actions):**
- pytest, pytest-cov, pytest-asyncio (testing)
- flake8, black, isort (linting)
- bandit, safety (security)
- Docker, Docker Compose (containerization)

---

## 11. Data Storage & Management

### 11.1 Stock Price Data

**Location:** `data/daily_prices_*.json`

**Files:** 100+ files (one per stock symbol)

**Format:**
```json
{
  "Meta Data": {
    "1. Information": "Daily Prices",
    "2. Symbol": "AAPL",
    "3. Last Refreshed": "2025-11-02",
    "4. Time Zone": "US/Eastern"
  },
  "Time Series (Daily)": {
    "2025-11-02": {
      "1. buy price": "234.50",
      "2. high": "236.20",
      "3. low": "233.10",
      "4. sell price": "235.80",
      "5. volume": "45000000"
    }
  }
}
```

### 11.2 Cryptocurrency Price Data

**Location:** `data/crypto_prices_{BTC|ETH}.json`

**Format:** Similar to stock prices with OHLCV data

### 11.3 Merged Data File

**Location:** `data/merged.jsonl`

**Purpose:** Combined JSONL for efficient price lookup

**Creation:** `python data/merge_jsonl.py`

### 11.4 Trading Results Directory

**Location:** `data/agent_data/{SIGNATURE}/`

**Structure:**
```
data/agent_data/
├── gpt-4-turbo/
│   ├── position/
│   │   └── position.jsonl     (Position history)
│   └── log/
│       ├── 2025-10-28/
│       │   └── log.jsonl      (Trading session log)
│       ├── 2025-10-29/
│       └── ...
├── claude-3.5-sonnet/
└── ...
```

---

## 12. Environment Configuration

**File:** `.env.example`

```bash
# API Keys
OPENAI_API_KEY=sk-...
ALPHAADVANTAGE_API_KEY=...
JINA_API_KEY=...

# Optional: Custom OpenAI endpoint
OPENAI_API_BASE=https://api.openai.com/v1

# MCP Service Ports
MATH_HTTP_PORT=8000
SEARCH_HTTP_PORT=8001
TRADE_HTTP_PORT=8002
GETPRICE_HTTP_PORT=8003

# Runtime Configuration
RUNTIME_ENV_PATH=.runtime_env.json

# Agent Settings (can be overridden)
AGENT_MAX_STEP=30
```

---

## 13. Key Design Patterns

### 13.1 Agent Registry Pattern

```python
AGENT_REGISTRY = {
    "BaseAgent": {
        "module": "agent.base_agent.base_agent",
        "class": "BaseAgent"
    }
}
```

Allows dynamic agent instantiation and extensibility.

### 13.2 MCP Service Pattern

Each service:
- Isolated FastMCP application
- HTTP-based communication
- Independently deployable
- Containerized with health checks
- Auto-registers tools with MultiServerMCPClient

### 13.3 Configuration Hierarchy

1. **Static:** configs/*.json (trading logic)
2. **Runtime:** .runtime_env.json (transient state)
3. **Environment:** .env (secrets, ports)

### 13.4 JSONL Position Tracking

Append-only log format enables:
- Complete transaction history
- Point-in-time position recovery
- Audit trail for debugging

### 13.5 Date-Aware Trading

- Weekday-only trading simulation
- Automatic weekend/holiday skipping
- Logical date progression

---

## 14. Workflow Summary

```
┌─────────────────────────────────────────────────────────┐
│                 AI-Trader Workflow                      │
└─────────────────────────────────────────────────────────┘

main.py (Entry Point)
    ↓
load_config()
    ↓
create_agent_instances()
    ↓
start_mcp_services() [Docker]
    ├─ Math Service (8000)
    ├─ Search Service (8001)
    ├─ Trade Service (8002)
    └─ Prices Service (8003)
    ↓
for each date in range:
    ├─ generate_system_prompt(date)
    ├─ load_positions(date)
    ├─ fetch_prices(date)
    ├─ create_agent(system_prompt)
    │
    └─ agent_loop():
        ├─ user: "Analyze positions"
        ├─ agent reasoning
        ├─ call_tools():
        │   ├─ buy() / sell()
        │   ├─ get_price_local()
        │   ├─ search()
        │   └─ math()
        ├─ receive results
        ├─ log_conversation()
        └─ check_stop_signal()
    │
    ├─ save_positions(date)
    └─ log_results(date)
    ↓
upload_artifacts()
↓
notify_slack() [optional]
```

---

## 15. Quick Reference: File Locations

| Component | File Path |
|-----------|-----------|
| Main Entry | `/main.py` |
| Base Agent | `/agent/base_agent/base_agent.py` |
| Math Service | `/agent_tools/tool_math.py` |
| Search Service | `/agent_tools/tool_jina_search.py` |
| Trade Service | `/agent_tools/tool_trade.py` |
| Price Service | `/agent_tools/tool_get_price_local.py` |
| Service Manager | `/agent_tools/start_mcp_services.py` |
| General Tools | `/tools/general_tools.py` |
| Price Tools | `/tools/price_tools.py` |
| Crypto Tools | `/tools/crypto_tools.py` |
| Result Tools | `/tools/result_tools.py` |
| Stock Prompts | `/prompts/agent_prompt.py` |
| Crypto Prompts | `/prompts/crypto_agent_prompt.py` |
| Default Config | `/configs/default_config.json` |
| Crypto Config | `/configs/crypto_config.json` |
| Docker Compose | `/docker-compose.yml` |
| Hourly Workflow | `/.github/workflows/hourly-trading.yml` |
| Tests Workflow | `/.github/workflows/tests.yml` |
| Config Tests | `/tests/test_config.py` |
| Tool Tests | `/tests/test_tools.py` |

---

## 16. Performance & Scalability Considerations

### 16.1 Current Limitations
- Sequential model processing (one after another)
- Weekday-only trading (no 24/5 crypto)
- Single agent instance per model
- Local file-based state (not distributed)

### 16.2 Scalability Opportunities
- Parallel model processing via asyncio
- Kubernetes deployment for MCP services
- Distributed position tracking (database)
- Multi-agent coordination
- Real-time data feeds instead of daily snapshots

---

## 17. Conclusion

AI-Trader is a comprehensive, production-ready trading simulation framework with:

1. **Modular Architecture:** Agent, tools, services, configs separated
2. **Extensible Design:** Custom agents, models, tools easily added
3. **Cloud-Native:** Docker containerization, GitHub Actions CI/CD
4. **Multi-Provider:** OpenAI, Anthropic, DeepSeek, custom LLMs
5. **Asset Classes:** Stocks (100 NASDAQ symbols) and crypto (BTC/ETH)
6. **Instrumentation:** Complete logging, position tracking, performance metrics
7. **Testing:** Automated validation, security scanning, dependency auditing
8. **Documentation:** Comprehensive setup guides and configuration docs

The system is ready for both local development and production deployment on GitHub Actions, with clear separation of concerns and extensibility for adding new agents, tools, and trading strategies.

---

*Generated: 2025-11-02*
*Comprehensive overview of AI-Trader codebase architecture and operations.*
