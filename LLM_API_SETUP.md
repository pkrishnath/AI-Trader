# LLM API Setup & Configuration Guide

## Overview

This document explains how the AI-Trader manages multiple LLM providers with separate API credentials, avoiding key collisions and providing clean provider separation.

---

## 🔧 Environment Variables Setup

### LLM Provider API Keys

Each LLM provider has its own dedicated API key environment variable:

```bash
# OpenAI Models (GPT-4o, GPT-4-Turbo)
OPENAI_API_KEY="sk-..."

# DeepSeek Models (deepseek-chat-v3.1)
DEEPSEEK_API_KEY="sk-..."

# Anthropic Models (Claude 3.5-Sonnet)
ANTHROPIC_API_KEY="sk-..."
```

### API Base URLs

```bash
# OpenAI API endpoint
OPENAI_API_BASE="https://api.openai.com/v1"

# DeepSeek API endpoint (OpenAI-compatible)
DEEPSEEK_API_BASE="https://api.deepseek.com/v1"
```

### Configuration File

```bash
# Third-party APIs
ALPHAADVANTAGE_API_KEY="..."
JINA_API_KEY="..."

# MCP Service Ports
MATH_HTTP_PORT=8000
SEARCH_HTTP_PORT=8001
TRADE_HTTP_PORT=8002
GETPRICE_HTTP_PORT=8003

# Agent Configuration
AGENT_MAX_STEP=30
RUNTIME_ENV_PATH=""
```

---

## 🤖 How Model Selection Works

### 1. GitHub Workflow Input

When triggering the workflow manually, select which LLM to use:

```yaml
llm_model:
  type: choice
  default: 'deepseek'
  options:
    - deepseek          # Default for cost efficiency
    - gpt-4o            # OpenAI's latest model
    - gpt-4-turbo       # OpenAI's powerful model
    - claude-3.5-sonnet # Anthropic's latest model
```

### 2. Config File Specifies Model Details

The `configs/crypto_config.json` defines which model to use:

```json
{
  "models": [
    {
      "name": "deepseek-chat-v3.1",
      "basemodel": "deepseek-chat-v3.1",
      "signature": "deepseek-crypto-trader",
      "enabled": true,
      "openai_base_url": "https://api.deepseek.com/v1",
      "openai_api_key": null  // Uses env var
    }
  ]
}
```

### 3. BaseAgent Intelligent Selection

In `agent/base_agent/base_agent.py`, the BaseAgent class automatically:

1. **Selects the correct API key** based on model name:
   ```python
   if "deepseek" in basemodel.lower():
       self.openai_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
       # Tries DEEPSEEK_API_KEY first, falls back to OPENAI_API_KEY
   ```

2. **Selects the correct API base URL**:
   ```python
   if "deepseek" in basemodel.lower():
       self.openai_base_url = os.getenv("DEEPSEEK_API_BASE") or "https://api.deepseek.com/v1"
   ```

3. **Creates the appropriate LLM client**:
   ```python
   if "claude" in self.basemodel.lower():
       self.model = ChatAnthropic(...)  # Uses Anthropic SDK
   else:
       self.model = ChatOpenAI(
           model="deepseek-chat-v3.1",
           base_url="https://api.deepseek.com/v1",  # Correct endpoint
           api_key=api_key_from_env,
       )
   ```

---

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────┐
│ GitHub Actions Workflow Dispatch    │
│ Select: llm_model = "deepseek"      │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Workflow: Set Environment Variables │
│ • DEEPSEEK_API_KEY=***              │
│ • DEEPSEEK_API_BASE=https://...     │
│ • OPENAI_API_KEY=***                │
│ • ANTHROPIC_API_KEY=***             │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ Docker Container Started            │
│ All env vars passed via -e flags    │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ main.py Loads crypto_config.json    │
│ • basemodel: "deepseek-chat-v3.1"   │
│ • openai_base_url: "https://..."    │
│ • openai_api_key: null              │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ BaseAgent.__init__()                │
│ Detects "deepseek" in model name    │
│ • Selects DEEPSEEK_API_KEY env var  │
│ • Selects DEEPSEEK_API_BASE env var │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ BaseAgent.initialize()              │
│ Creates ChatOpenAI client with:      │
│ • model: "deepseek-chat-v3.1"       │
│ • base_url: "https://api.deepseek..." │
│ • api_key: <DEEPSEEK_API_KEY value> │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│ ✅ Ready to Make API Calls           │
│ Trading agent starts...             │
└─────────────────────────────────────┘
```

---

## 📋 Provider-Specific Configuration

### DeepSeek (Default)

```json
{
  "name": "deepseek-chat-v3.1",
  "basemodel": "deepseek-chat-v3.1",
  "signature": "deepseek-crypto-trader",
  "enabled": true,
  "openai_base_url": "https://api.deepseek.com/v1",
  "openai_api_key": null
}
```

**Environment Variables:**
- `DEEPSEEK_API_KEY`: Your DeepSeek API key
- `DEEPSEEK_API_BASE`: API endpoint (defaults to `https://api.deepseek.com/v1`)

**Cost Benefit:** Most cost-effective option (cheaper than OpenAI)

---

### OpenAI (GPT-4o / GPT-4-Turbo)

```json
{
  "name": "gpt-4o",
  "basemodel": "gpt-4o",
  "signature": "gpt-4o-crypto-trader",
  "enabled": false,
  "openai_base_url": "https://api.openai.com/v1",
  "openai_api_key": null
}
```

**Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_API_BASE`: API endpoint (defaults to `https://api.openai.com/v1`)

**Cost Benefit:** Higher performance, higher cost

---

### Claude 3.5-Sonnet

```json
{
  "name": "claude-3.5-sonnet",
  "basemodel": "anthropic/claude-3.5-sonnet",
  "signature": "claude-crypto-trader",
  "enabled": false,
  "openai_base_url": null,
  "openai_api_key": null
}
```

**Environment Variables:**
- `ANTHROPIC_API_KEY`: Your Anthropic API key

**Note:** Claude uses a different SDK (ChatAnthropic) instead of ChatOpenAI

**Cost Benefit:** Very capable, middle-ground pricing

---

## 🚀 GitHub Actions Secrets Setup

To use different providers, set these secrets in your GitHub repository:

1. Go to **Settings → Secrets and variables → Actions**

2. Create secrets:

| Secret Name | Example Value | Required |
|-------------|---------------|----------|
| `OPENAI_API_KEY` | `sk-proj-...` | For GPT models |
| `DEEPSEEK_API_KEY` | `sk-...` | For DeepSeek models |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | For Claude models |
| `ALPHAADVANTAGE_API_KEY` | `...` | For stock data |
| `JINA_API_KEY` | `jina_...` | For web search |

---

## 🧪 Testing Different Models

### Via GitHub UI

1. Go to **Actions → Hourly AI Trading Run**
2. Click **Run workflow**
3. Select your LLM model from the dropdown
4. Click **Run workflow**

### Via Command Line

```bash
# Test with DeepSeek (default)
gh workflow run "Hourly AI Trading Run" --ref main

# Test with GPT-4o
gh workflow run "Hourly AI Trading Run" --ref main \
  -f llm_model="gpt-4o"

# Test with Claude
gh workflow run "Hourly AI Trading Run" --ref main \
  -f llm_model="claude-3.5-sonnet"
```

---

## 🔍 Debugging API Issues

### Check which API key is being used:

Look for these log messages in the workflow:

```
🔑 Using DeepSeek API key         # Correct for deepseek-chat-v3.1
🔑 Using OpenAI API key          # Correct for gpt-4o models
```

### Verify API endpoints:

Check in the logs:
```
OPENAI_API_BASE=https://api.openai.com/v1
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
```

### Common Issues:

| Issue | Solution |
|-------|----------|
| 404 - Model not found | Check model name matches provider (e.g., `deepseek-chat-v3.1`) |
| 401 - Unauthorized | Verify API key is correct and not expired |
| API endpoint mismatch | Ensure API base URL matches the provider |
| Missing API key | Check GitHub secrets are configured correctly |

---

## 💡 Best Practices

1. **Separate API Keys**: Always use provider-specific API keys to avoid confusion
2. **Default to DeepSeek**: For cost efficiency, use DeepSeek as default
3. **Test Before Production**: Test workflow manually with each model before scheduling
4. **Monitor Costs**: Each provider has different pricing; monitor usage
5. **Keep Secrets Secure**: Never commit API keys; use GitHub secrets
6. **Document Changes**: When switching providers, update the config file accordingly

---

## 📚 Related Files

- **Workflow Definition**: `.github/workflows/hourly-trading.yml`
- **Configuration**: `configs/crypto_config.json`
- **Agent Implementation**: `agent/base_agent/base_agent.py`
- **Environment Template**: `.env.example`

---

**Last Updated:** 2025-11-02
