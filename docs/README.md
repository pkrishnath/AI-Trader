# AI-Trader Documentation

Complete technical documentation explaining the AI-Trader system architecture, implementation, and operations.

## 📚 Documentation Files

### 1. [ARCHITECTURE.md](./ARCHITECTURE.md) - System Architecture Overview
**Best for:** Understanding the complete system design

**Contents:**
- System overview and high-level architecture
- 7 architecture layers:
  1. Entry Point (main.py)
  2. Trading Agent (BaseAgent)
  3. FastMCP Services (4 services)
  4. Configuration System (3-tier hierarchy)
  5. Trading Agent Logic (complete trading flow)
  6. Data Flow (price data → trading → dashboard)
  7. Docker Containerization
- GitHub Actions automation
- Key code examples

**Reading time:** 30-45 minutes

---

### 2. [FASTMCP_GUIDE.md](./FASTMCP_GUIDE.md) - FastMCP Deep Dive
**Best for:** Understanding MCP services and tool definitions

**Contents:**
- What is FastMCP and why it's used
- Service architecture (4 services on ports 8000-8003)
- Tool definition structure and best practices
- Complete HTTP request/response cycle
- Detailed implementation of each service:
  - Math Service (calculations & indicators)
  - Search Service (market research)
  - Trade Service (execution & tracking)
  - Prices Service (data lookups)
- Error handling patterns
- Troubleshooting guide with debug checklist

**Reading time:** 25-35 minutes

---

## 🎯 Quick Start by Role

### For Developers
1. Start with [ARCHITECTURE.md](#architecturemd---system-architecture-overview)
2. Understand the BaseAgent in detail
3. Read [FASTMCP_GUIDE.md](#fastmcp_guidemd---fastmcp-deep-dive) for service integration
4. Review code examples in both documents
5. Run locally with Docker

### For DevOps Engineers
1. Focus on Docker sections in [ARCHITECTURE.md](#architecturemd---system-architecture-overview)
2. Review GitHub Actions workflows
3. Read Docker troubleshooting in [FASTMCP_GUIDE.md](#fastmcp_guidemd---fastmcp-deep-dive)
4. Monitor services using provided debugging checklist

### For Data Scientists / Traders
1. Read Trading Agent Logic section in [ARCHITECTURE.md](#architecturemd---system-architecture-overview)
2. Understand system prompt examples
3. Review configuration files structure
4. Check Data Flow section for output formats

### For System Architects
1. Start with System Overview in [ARCHITECTURE.md](#architecturemd---system-architecture-overview)
2. Review architecture layers and design decisions
3. Study service architecture in [FASTMCP_GUIDE.md](#fastmcp_guidemd---fastmcp-deep-dive)
4. Review Docker containerization approach

---

## 🏗️ Architecture Layers Overview

```
┌─────────────────────────────────────────────────┐
│ Layer 1: Entry Point (main.py)                  │
│ - Dynamic agent loading                         │
│ - Configuration management                      │
│ - Model orchestration                           │
└─────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────┐
│ Layer 2: Trading Agent (BaseAgent)              │
│ - LLM integration                               │
│ - Decision making                               │
│ - MCP service coordination                      │
└─────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────┐
│ Layer 3: FastMCP Services (4 services)          │
│ - Math (Port 8000)                              │
│ - Search (Port 8001)                            │
│ - Trade (Port 8002)                             │
│ - Prices (Port 8003)                            │
└─────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────┐
│ Layer 4: Configuration System                   │
│ - Static config files                           │
│ - Runtime configuration                         │
│ - Environment variables                         │
└─────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────┐
│ Layer 5-7: Data, Docker, Automation             │
│ - Price data fetching                           │
│ - Docker containerization                       │
│ - GitHub Actions workflows                      │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Trading Cycle (1 Hour)

```
1. TRIGGER (GitHub Actions)
   └─ Hourly schedule (0 * * * *)

2. DATA FETCH (30 seconds)
   ├─ Stock prices (Alpha Vantage API)
   ├─ Crypto prices (CoinGecko API)
   └─ Merge into unified format

3. SERVICE STARTUP (60 seconds)
   ├─ Build Docker images
   ├─ Start 4 MCP services
   └─ Verify health checks

4. TRADING SIMULATION (60 seconds)
   ├─ Initialize agent
   ├─ Connect to MCP services
   ├─ Fetch market data
   ├─ 30 trading steps max
   │  ├─ LLM analysis
   │  ├─ Decision
   │  └─ Trade execution
   └─ Save results

5. CLEANUP & REPORT (30 seconds)
   ├─ Stop Docker services
   ├─ Upload artifacts
   └─ Generate report

TOTAL: ~5 minutes per trading cycle
FREQUENCY: Every hour, 24/7
```

---

## 📊 Key Components

### Main Files

| File | Purpose | Lines | Language |
|------|---------|-------|----------|
| `main.py` | Application entry point | 250+ | Python |
| `agent/base_agent/base_agent.py` | Trading agent logic | 595 | Python |
| `agent_tools/tool_*.py` | MCP service tools | 300+ each | Python |
| `configs/*.json` | Configuration files | 50+ each | JSON |
| `.github/workflows/*.yml` | CI/CD pipelines | 150+ each | YAML |
| `docker-compose.yml` | Service orchestration | 85 | YAML |
| `agent_tools/Dockerfile.*` | Container definitions | 25 each | Dockerfile |

### Configuration Files

| File | Purpose |
|------|---------|
| `configs/default_config.json` | Stock trading config |
| `configs/crypto_config.json` | Crypto trading config |
| `.env.example` | Environment variable template |
| `.runtime_env.json` | Runtime state (generated) |

### Data Files

| Directory | Content |
|-----------|---------|
| `data/daily_price_*.json` | Stock price data (101 files) |
| `data/crypto_prices_*.json` | Crypto price data (2 files) |
| `data/merged.jsonl` | Combined price data |
| `data/agent_data/*/` | Trading results and logs |

---

## 🔧 Technology Stack

### Core Technologies
- **Language:** Python 3.11
- **LLM Framework:** LangChain
- **MCP Services:** FastMCP
- **HTTP Server:** FastAPI/Uvicorn
- **Container:** Docker, Docker Compose
- **CI/CD:** GitHub Actions
- **LLM Providers:** OpenAI, Anthropic, DeepSeek

### Key Libraries
```
langchain==1.0.2
langchain-openai==1.0.1
langchain-anthropic>=0.1.0
fastmcp==2.12.5
fastapi
uvicorn
python-dotenv
requests
httpx
```

---

## 🚀 Getting Started

### Local Development

1. **Clone Repository**
   ```bash
   git clone https://github.com/pkrishnath/AI-Trader.git
   cd AI-Trader
   ```

2. **Setup Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Services (Docker)**
   ```bash
   docker compose build
   docker compose up -d
   ```

5. **Run Trading Simulation**
   ```bash
   # Stock trading
   python main.py configs/default_config.json

   # Or crypto trading
   python main.py configs/crypto_config.json
   ```

6. **View Results**
   - Check `data/agent_data/` for results
   - Open `https://pkrishnath.github.io/AI-Trader/` for dashboard

---

## 📋 Service Health Checks

### Verify All Services Running

```bash
# Check service status
docker compose ps

# Should show:
# NAME              STATUS
# math-service      Up (healthy)
# search-service    Up (healthy)
# trade-service     Up (healthy)
# prices-service    Up (healthy)
```

### Manual Health Checks

```bash
# Math Service
curl http://localhost:8000/health

# Search Service
curl http://localhost:8001/health

# Trade Service
curl http://localhost:8002/health

# Prices Service
curl http://localhost:8003/health
```

---

## 🐛 Troubleshooting

### Service Won't Start

1. Check logs:
   ```bash
   docker compose logs service-name
   ```

2. Verify ports available:
   ```bash
   lsof -i :8000  # Check port 8000
   ```

3. Check environment variables:
   ```bash
   echo $JINA_API_KEY
   echo $OPENAI_API_KEY
   ```

### Agent Can't Connect to Services

1. Verify services are running:
   ```bash
   docker compose ps
   ```

2. Test connectivity:
   ```bash
   curl http://localhost:8000/health
   ```

3. Check network:
   ```bash
   docker network ls
   docker network inspect mcp-network
   ```

### Price Data Missing

1. Check merged.jsonl:
   ```bash
   wc -l data/merged.jsonl
   ```

2. Regenerate prices:
   ```bash
   cd data
   python get_daily_price.py
   python get_crypto_prices.py
   python merge_jsonl.py
   ```

---

## 🔑 Environment Variables

Required for operation:

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
JINA_API_KEY=jina_...
ALPHAADVANTAGE_API_KEY=...

# Optional
OPENAI_BASE_URL=https://api.openai.com/v1  # For custom endpoints
```

---

## 📈 Dashboard

**URL:** https://pkrishnath.github.io/AI-Trader/

**Displays:**
- Portfolio value over time
- Position tracking (stocks & crypto)
- Trading history
- Performance metrics
- P&L analysis

---

## 🎓 Learning Resources

### Understanding the System

1. **Start Here:** [ARCHITECTURE.md](./ARCHITECTURE.md) System Overview section
2. **Go Deeper:** Read Trading Agent Logic section
3. **Services:** [FASTMCP_GUIDE.md](./FASTMCP_GUIDE.md) Service Architecture
4. **Implementation:** Review code examples in both documents

### Running the Code

1. Setup local environment (see Getting Started)
2. Run with `python main.py`
3. Check results in `data/agent_data/`
4. Read logs to understand flow

### Extending the System

1. Add new tools to MCP services
2. Create new agent types
3. Support additional LLM providers
4. Add new trading strategies

---

## 📝 Code Review Summary

### Strengths
✅ **Modular Architecture:** Clear separation of concerns
✅ **Extensible Design:** Add agents, services, models without changing core
✅ **Error Handling:** Comprehensive validation and recovery
✅ **Production Ready:** Docker, CI/CD, logging, monitoring
✅ **Multiple LLMs:** Support for different AI providers
✅ **Asset Support:** Both stocks and cryptocurrencies

### Areas for Growth
💡 **Database Persistence:** Currently uses JSON files
💡 **State Management:** Could use Redis for distributed state
💡 **Monitoring:** Could add metrics/observability
💡 **Testing:** Could expand unit and integration tests
💡 **Rate Limiting:** Could add request throttling

---

## 📞 Support & Resources

### Documentation
- Architecture Overview: [ARCHITECTURE.md](./ARCHITECTURE.md)
- FastMCP Services: [FASTMCP_GUIDE.md](./FASTMCP_GUIDE.md)
- Configuration: See `configs/` directory
- Examples: Review code in `agent/` and `agent_tools/`

### Community
- GitHub Issues: [Report bugs](https://github.com/pkrishnath/AI-Trader/issues)
- Discussions: [Ask questions](https://github.com/pkrishnath/AI-Trader/discussions)

### External Resources
- [FastMCP Documentation](https://www.mcp.so/)
- [LangChain Documentation](https://python.langchain.com/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## 📄 License

See LICENSE file in repository

---

## ✍️ Contributors

- **Creator:** Krishnath
- **Documentation:** Claude Code
- **Last Updated:** November 2, 2025

---

**Ready to dive in?** Start with [ARCHITECTURE.md](./ARCHITECTURE.md) for a complete system overview!
