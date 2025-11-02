# AI-Trader Documentation Index

Complete documentation has been generated for the AI-Trader codebase. This index helps you navigate all available resources.

## Primary Documentation Files

### 1. ARCHITECTURE_OVERVIEW.md (37 KB)
**Comprehensive technical reference covering all major components**

Location: `/Users/krish/code/github/AI-Trader/ARCHITECTURE_OVERVIEW.md`

Contents:
- Executive summary with key statistics
- Project structure and directory layout
- Key entry points (main.py, BaseAgent)
- Complete MCP services architecture (4 microservices)
- Configuration system (3-tier hierarchy)
- Data flow and trading logic diagrams
- Docker containerization details
- GitHub Actions workflow specifications
- Supporting tools and utilities documentation
- Testing infrastructure
- Dependencies and performance considerations

**Best for:** Complete understanding of system architecture and design

**Read time:** 30-45 minutes

**Audience:** All stakeholders (developers, DevOps, architects)

---

### 2. COMPONENT_QUICK_REFERENCE.md (8.4 KB)
**Quick lookup guide for developers and operators**

Location: `/Users/krish/code/github/AI-Trader/COMPONENT_QUICK_REFERENCE.md`

Contents:
- File locations summary table
- Quick command reference
- Architecture layers diagram
- Configuration key parameters
- Environment variables list
- Data structure examples (JSON)
- Supported models by provider
- Trading flow diagram
- Troubleshooting table with solutions
- Performance statistics
- Testing and deployment checklists

**Best for:** Quick lookups and command reference

**Read time:** 10-15 minutes

**Audience:** Developers and operators

---

## Existing Documentation

The following documentation files were already in the repository and complement these new guides:

### Setup & Getting Started
- **SETUP_SUMMARY.md** - GitHub Actions setup summary with 3-step quick start
- **GITHUB_ACTIONS_SETUP.md** - Comprehensive GitHub Actions configuration guide
- **CRYPTO_QUICK_START.md** - Quick start for cryptocurrency trading
- **DOCKER_SETUP.md** - Docker containerization guide

### Trading Guides
- **CRYPTO_TRADING_GUIDE.md** - Detailed cryptocurrency trading instructions
- **README_CN.md** - Chinese language documentation

### GitHub Integration
- **.github/workflows/README.md** - Workflow documentation
- **.github/workflows/QUICK_REFERENCE.txt** - Workflow quick reference

### Configuration Guides
- **configs/README.md** - Configuration file documentation
- **configs/README_zh.md** - Chinese configuration guide

---

## File Structure Reference

```
/Users/krish/code/github/AI-Trader/
│
├── ARCHITECTURE_OVERVIEW.md         ← START HERE for complete understanding
├── COMPONENT_QUICK_REFERENCE.md     ← START HERE for quick lookups
├── DOCUMENTATION_INDEX.md           ← You are here
│
├── main.py                          (Application entry point)
├── agent/base_agent/base_agent.py   (Core agent - 595 lines)
│
├── agent_tools/                     (4 MCP services)
│   ├── tool_math.py                 (Math operations)
│   ├── tool_jina_search.py          (Web search)
│   ├── tool_trade.py                (Buy/sell execution)
│   ├── tool_get_price_local.py      (Price lookups)
│   ├── start_mcp_services.py        (Service manager)
│   ├── Dockerfile.math
│   ├── Dockerfile.search
│   ├── Dockerfile.trade
│   └── Dockerfile.prices
│
├── tools/                           (Utilities)
│   ├── general_tools.py
│   ├── price_tools.py
│   ├── crypto_tools.py
│   └── result_tools.py
│
├── prompts/                         (System prompts)
│   ├── agent_prompt.py
│   └── crypto_agent_prompt.py
│
├── configs/                         (Configuration)
│   ├── default_config.json
│   └── crypto_config.json
│
├── .github/workflows/               (CI/CD)
│   ├── hourly-trading.yml
│   ├── tests.yml
│   ├── claude.yml
│   ├── claude-code-review.yml
│   └── deploy-github-pages.yml
│
├── tests/                           (Unit tests)
│   ├── test_config.py
│   └── test_tools.py
│
├── data/                            (Price data & results)
│   ├── daily_prices_*.json          (100+ stock files)
│   ├── crypto_prices_*.json         (BTC/ETH)
│   ├── merged.jsonl
│   └── agent_data/                  (Trading results)
│
├── docker-compose.yml               (Service orchestration)
├── requirements.txt                 (Python dependencies)
├── .runtime_env.json               (Runtime config)
└── .env.example                     (Environment template)
```

---

## Quick Start Guide

### For Different Roles

#### Software Developers
1. Read: COMPONENT_QUICK_REFERENCE.md (sections: Overview, Architecture Layers)
2. Read: ARCHITECTURE_OVERVIEW.md (sections: 1-3, 8)
3. Review: agent/base_agent/base_agent.py (core logic)
4. Check: agent_tools/ (service implementations)
5. Run: `pytest tests/` (unit tests)

#### DevOps/Infrastructure
1. Read: COMPONENT_QUICK_REFERENCE.md (entire document)
2. Read: ARCHITECTURE_OVERVIEW.md (sections: 6-7)
3. Review: docker-compose.yml
4. Check: .github/workflows/
5. Review: existing Docker/CI documentation

#### Data Scientists
1. Read: COMPONENT_QUICK_REFERENCE.md (section: Supported Models)
2. Read: ARCHITECTURE_OVERVIEW.md (sections: 5, 8.5)
3. Review: prompts/
4. Check: tools/result_tools.py
5. Study: configs/

#### Project Managers
1. Read: COMPONENT_QUICK_REFERENCE.md (Executive Summary sections)
2. Read: ARCHITECTURE_OVERVIEW.md (section: Executive Summary)
3. Review: Key files list above
4. Check: GitHub Actions workflows overview

---

## Key Concepts

### MCP (Model Control Protocol)
A protocol for isolated, containerized tools. AI-Trader uses 4 MCP services:
- Math, Search, Trade, Prices
- Each runs on dedicated port (8000-8003)
- Communicate via HTTP
- Independently scalable

### Configuration Hierarchy
```
.env (environment variables/secrets)
    ↓
.runtime_env.json (transient state)
    ↓
configs/*.json (trading logic)
```

### Trading Data Formats
- **Positions:** JSONL (date, id, holdings)
- **Logs:** JSONL (timestamp, messages)
- **Prices:** JSON/JSONL (OHLCV data)

### Supported Assets
- **Stocks:** NASDAQ 100 (100 symbols)
- **Crypto:** BTC, ETH (fractional amounts)

### Supported Models
- OpenAI: gpt-4-turbo, gpt-4o
- Anthropic: claude-3.5-sonnet
- DeepSeek: deepseek-chat-v3.1
- Custom: Any OpenAI-compatible API

---

## Common Tasks

### Running Trading Simulation
```bash
# Stock trading (default)
python main.py

# Cryptocurrency trading
python main.py configs/crypto_config.json

# Custom configuration
python main.py configs/custom_config.json
```

### Managing Services
```bash
# Start MCP services
docker compose up -d

# Check status
python agent_tools/start_mcp_services.py status

# Stop services
docker compose down
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_config.py -v
```

### Code Quality
```bash
# Format check
black --check .

# Linting
flake8 .

# Security scan
bandit -r .
```

---

## Troubleshooting Quick Links

### Common Issues
| Problem | Solution | File |
|---------|----------|------|
| Services won't start | Check ports 8000-8003 free | docker-compose.yml |
| Configuration error | Validate JSON format | configs/README.md |
| Tests failing | Check dependencies installed | requirements.txt |
| Position file missing | Register agent first | agent/base_agent/base_agent.py |
| Trading not executing | Check API keys set | .env.example |

For detailed troubleshooting, see COMPONENT_QUICK_REFERENCE.md (Troubleshooting section).

---

## Documentation Statistics

| Metric | Value |
|--------|-------|
| Total documentation | 45 KB |
| Main files | 2 new + 12+ existing |
| Code files documented | 22 Python files |
| Services documented | 4 MCP services |
| Workflows documented | 5 GitHub Actions |
| Data types explained | 5+ formats |
| Configuration options | 20+ parameters |
| Models supported | 4+ LLM providers |

---

## How to Use This Documentation

### Step 1: Orientation
Start with **COMPONENT_QUICK_REFERENCE.md** to understand overall structure.

### Step 2: Deep Dive
Read relevant sections from **ARCHITECTURE_OVERVIEW.md** based on your role.

### Step 3: Hands-On
Follow quick start commands in COMPONENT_QUICK_REFERENCE.md.

### Step 4: Reference
Use the quick reference tables and file locations for future lookups.

### Step 5: Existing Docs
Consult specific guides (SETUP_SUMMARY.md, CRYPTO_QUICK_START.md, etc.) as needed.

---

## Version Information

- **Documentation Generated:** November 2, 2025
- **AI-Trader Branch:** main
- **Python Version:** 3.11
- **Status:** Comprehensive (all components documented)

---

## Contributing to Documentation

To update or extend documentation:

1. **COMPONENT_QUICK_REFERENCE.md** - For quick lookups and summaries
2. **ARCHITECTURE_OVERVIEW.md** - For detailed technical specifications
3. Ensure absolute file paths (e.g., `/Users/krish/code/github/AI-Trader/...`)
4. Include code examples and JSON structures where applicable
5. Update this index if adding new documentation

---

## Additional Resources

- **Official MCP Documentation:** https://modelcontextprotocol.io
- **FastMCP Repository:** https://github.com/jlowin/fastmcp
- **LangChain Documentation:** https://python.langchain.com
- **Docker Documentation:** https://docs.docker.com
- **GitHub Actions:** https://docs.github.com/en/actions

---

## Support

For questions about:
- **Architecture:** See ARCHITECTURE_OVERVIEW.md
- **Commands:** See COMPONENT_QUICK_REFERENCE.md
- **Setup:** See existing SETUP_SUMMARY.md or GITHUB_ACTIONS_SETUP.md
- **Crypto Trading:** See CRYPTO_QUICK_START.md
- **Docker:** See DOCKER_SETUP.md

---

**Last Updated:** November 2, 2025
**Status:** Complete
**Audience:** All stakeholders

