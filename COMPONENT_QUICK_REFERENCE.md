# AI-Trader Component Quick Reference

## File Locations Summary

### Core Application
- **Main Entry Point**: `main.py` - Orchestrates trading simulations
- **Base Agent**: `agent/base_agent/base_agent.py` (595 lines) - Core intelligent agent

### Agent Services (MCP - Model Control Protocol)
| Service | File | Port | Purpose |
|---------|------|------|---------|
| Math | `agent_tools/tool_math.py` | 8000 | Arithmetic (add, multiply) |
| Search | `agent_tools/tool_jina_search.py` | 8001 | Web search, market news |
| Trade | `agent_tools/tool_trade.py` | 8002 | Buy/sell execution |
| Prices | `agent_tools/tool_get_price_local.py` | 8003 | OHLCV price lookup |
| Manager | `agent_tools/start_mcp_services.py` | - | Service lifecycle mgmt |

### Docker Configuration
- **Compose**: `docker-compose.yml` - 4-service orchestration
- **Dockerfiles**: 
  - `agent_tools/Dockerfile.math`
  - `agent_tools/Dockerfile.search`
  - `agent_tools/Dockerfile.trade`
  - `agent_tools/Dockerfile.prices`

### Utility Tools
- **General**: `tools/general_tools.py` - Config management, conversation parsing
- **Prices**: `tools/price_tools.py` - Stock prices, positions, P&L
- **Crypto**: `tools/crypto_tools.py` - BTC/ETH price data
- **Results**: `tools/result_tools.py` - Trade aggregation & analysis

### System Prompts
- **Stock Trading**: `prompts/agent_prompt.py` - NASDAQ 100 trading
- **Crypto Trading**: `prompts/crypto_agent_prompt.py` - BTC/ETH trading

### Configuration Files
- **Stock Config**: `configs/default_config.json` - Default trading settings
- **Crypto Config**: `configs/crypto_config.json` - Cryptocurrency settings
- **Runtime Config**: `.runtime_env.json` - Transient state
- **Template**: `.env.example` - Environment variables

### Data
- **Stock Prices**: `data/daily_prices_*.json` (100+ files)
- **Crypto Prices**: `data/crypto_prices_{BTC|ETH}.json`
- **Merged Data**: `data/merged.jsonl` - Combined price data
- **Trading Results**: `data/agent_data/{MODEL}/{position|log}/`

### GitHub Actions CI/CD
- **Hourly Trading**: `.github/workflows/hourly-trading.yml`
- **Tests**: `.github/workflows/tests.yml`
- **Claude Integration**: `.github/workflows/claude.yml`
- **Code Review**: `.github/workflows/claude-code-review.yml`
- **Deployment**: `.github/workflows/deploy-github-pages.yml`

### Testing
- **Config Tests**: `tests/test_config.py`
- **Tool Tests**: `tests/test_tools.py`
- **Pytest Config**: `pytest.ini`

---

## Quick Command Reference

### Run Trading (Local)
```bash
# Stock trading
python main.py

# Cryptocurrency trading
python main.py configs/crypto_config.json

# Custom config
python main.py configs/my_config.json
```

### Start MCP Services
```bash
# Start all services
python agent_tools/start_mcp_services.py

# Check service status
python agent_tools/start_mcp_services.py status

# Or use Docker Compose
docker compose up -d
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_config.py

# With coverage
pytest --cov=.

# Verbose output
pytest -v
```

### Code Quality
```bash
# Format check
black --check .

# Linting
flake8 .

# Import sorting
isort --check-only .

# Security
bandit -r .
```

### Data Management
```bash
# Fetch stock prices
python data/get_daily_price.py

# Fetch crypto prices
python data/get_crypto_prices.py

# Merge all data
python data/merge_jsonl.py
```

---

## Architecture Layers

```
Application Layer
    ├─ main.py (Orchestration)
    └─ agent/base_agent/ (Intelligent Decision Making)

Integration Layer
    ├─ langchain_mcp_adapters (MCP Communication)
    └─ langchain (Agent Framework)

Service Layer (4 Microservices via MCP)
    ├─ Math (Calculations)
    ├─ Search (News/Web)
    ├─ Trade (Execution)
    └─ Prices (Data)

Tools & Utilities Layer
    ├─ general_tools (Config)
    ├─ price_tools (Stock Data)
    ├─ crypto_tools (Crypto Data)
    └─ result_tools (Analysis)

Data Layer
    ├─ Positions (JSONL)
    ├─ Logs (JSONL)
    └─ Price Data (JSON/JSONL)
```

---

## Configuration Key Parameters

### Agent Config
```json
{
  "max_steps": 30,           # Max reasoning steps per session
  "max_retries": 3,          # Retry attempts on failure
  "base_delay": 1.0,         # Retry delay in seconds
  "initial_cash": 10000.0    # Starting portfolio value
}
```

### Date Range
```json
{
  "init_date": "2025-10-28",
  "end_date": "2025-11-02"
}
```

### Models
```json
{
  "name": "gpt-4-turbo",
  "basemodel": "gpt-4-turbo",
  "signature": "gpt-4-turbo",
  "enabled": true
}
```

---

## Environment Variables

### API Keys (Required)
- `OPENAI_API_KEY` - For OpenAI models
- `JINA_API_KEY` - For web search

### Ports (Default: 8000-8003)
- `MATH_HTTP_PORT=8000`
- `SEARCH_HTTP_PORT=8001`
- `TRADE_HTTP_PORT=8002`
- `GETPRICE_HTTP_PORT=8003`

### Runtime
- `RUNTIME_ENV_PATH=.runtime_env.json`
- `PYTHONPATH=/app` (in Docker)

### Date Overrides
- `INIT_DATE=2025-10-28`
- `END_DATE=2025-11-02`

---

## Data Structures

### Position File (JSONL)
```json
{
  "date": "2025-10-28",
  "id": 0,
  "positions": {
    "AAPL": 10,
    "MSFT": 5,
    "CASH": 7500.25
  }
}
```

### OHLCV Price Data
```json
{
  "1. buy price": "234.50",
  "2. high": "236.20",
  "3. low": "233.10",
  "4. sell price": "235.80",
  "5. volume": "45000000"
}
```

### Log Entry (JSONL)
```json
{
  "timestamp": "2025-11-02T14:30:45.123456",
  "signature": "gpt-4-turbo",
  "new_messages": [
    {
      "role": "user",
      "content": "Analyze positions"
    }
  ]
}
```

---

## Supported Models

### By Provider

**OpenAI:**
- gpt-4-turbo
- gpt-4o

**Anthropic:**
- claude-3.5-sonnet
- claude-3-sonnet (with API key)

**DeepSeek:**
- deepseek-chat-v3.1

**Custom:**
- Any model accessible via OpenAI-compatible API

### Stock Universe
Default: NASDAQ 100 (100 symbols including NVDA, MSFT, AAPL, GOOG, etc.)

### Crypto Assets
- BTC (Bitcoin)
- ETH (Ethereum)
- Fractional amounts supported

---

## Trading Flow

```
1. Load Config
   ↓
2. Initialize Agents
   ↓
3. Start MCP Services
   ↓
4. For Each Date in Range:
   ├─ Generate System Prompt
   ├─ Load Yesterday's Position
   ├─ Fetch Today's Prices
   └─ Run Agent Loop:
      ├─ Agent Thinks
      ├─ Calls Tools (buy/sell/search/price)
      ├─ Receives Results
      ├─ Logs Conversation
      └─ Until STOP_SIGNAL or max_steps
   ↓
5. Save Results
   ├─ Position File (JSONL)
   └─ Log File (JSONL)
   ↓
6. Aggregate & Report
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "SIGNATURE not set" | Ensure main.py sets config value before tools call |
| "MCP tools not loading" | Check services running on correct ports |
| "Date range empty" | Verify date format (YYYY-MM-DD) and trading day logic |
| "Position file not found" | Check agent registration happened |
| "Insufficient cash" | Verify initial_cash is sufficient |
| "Symbol not found" | Check price data exists for symbol/date |
| "Docker compose fails" | Run `docker compose -f docker-compose.yml build` |
| "Workflow times out" | Increase timeout or reduce date range |

---

## Performance Stats

- **Agent Response Time**: ~1-5 seconds per step (depends on model)
- **Tool Execution**: <100ms (local prices) to 1-2s (web search)
- **Position File I/O**: <10ms (small files)
- **Docker Startup**: 30-60 seconds for all 4 services
- **Memory Usage**: ~500MB per service, ~2-4GB total

---

## Testing Checklist

- [ ] Config files are valid JSON
- [ ] Date ranges parse correctly
- [ ] MCP services start and respond
- [ ] Position files are created
- [ ] Buy/sell operations update positions correctly
- [ ] Price lookups return valid data
- [ ] Stop signal is recognized
- [ ] Error handling works (insufficient cash, missing symbols)
- [ ] GitHub Actions workflow succeeds
- [ ] Artifacts are uploaded correctly

---

## Deployment Checklist

- [ ] .env configured with API keys
- [ ] Docker and Docker Compose installed
- [ ] All requirements.txt dependencies installed
- [ ] Data files populated (prices)
- [ ] Config files created
- [ ] GitHub secrets set (if using Actions)
- [ ] MCP services can start
- [ ] Agent can initialize
- [ ] Trading simulation runs
- [ ] Results are saved and accessible

---

## Additional Resources

- **Comprehensive Docs**: `ARCHITECTURE_OVERVIEW.md`
- **Setup Guide**: `GITHUB_ACTIONS_SETUP.md`
- **Quick Start**: `CRYPTO_QUICK_START.md`
- **Trading Guide**: `CRYPTO_TRADING_GUIDE.md`
- **Docker Docs**: `DOCKER_SETUP.md`

---

*Last Updated: November 2, 2025*
