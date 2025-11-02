# Free LLM Testing Guide - No Credit Card Required

Testing the AI-Trader without spending money? Yes! Here are several completely free options.

---

## 🆓 Free LLM Options (2024-2025)

### 1. **Groq** (Recommended for Speed)
- **Cost**: Completely FREE
- **Speed**: 300+ tokens/second (fastest free option)
- **Models Available**:
  - Llama 3.3 70B (fastest, best free option)
  - Mixtral 8x7B
  - Llama 3 8B
- **Sign-up**: https://console.groq.com

#### Setup for Groq:
```bash
# 1. Create free account at https://console.groq.com
# 2. Get API key from dashboard
# 3. Set environment variable
export GROQ_API_KEY="your-api-key-here"

# 4. Update config
```

**Config for Groq** (configs/groq_config.json):
```json
{
  "agent_type": "BaseAgent",
  "crypto_mode": true,
  "trading_universe": ["BTC", "ETH"],
  "date_range": {
    "init_date": "2025-10-28",
    "end_date": "2025-11-02"
  },
  "models": [
    {
      "name": "groq-llama3.3",
      "basemodel": "groq/llama-3.3-70b-versatile",
      "signature": "groq-crypto-trader",
      "enabled": true,
      "openai_base_url": "https://api.groq.com/openai/v1",
      "openai_api_key": null
    }
  ]
}
```

---

### 2. **Google AI Studio (Gemini)**
- **Cost**: Completely FREE
- **Tokens**: Up to 1,000,000 tokens/minute
- **Models**: Google Gemini 2.5 Flash (very capable)
- **Sign-up**: https://aistudio.google.com/app/apikeys

#### Setup for Google Gemini:
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

**Config for Google Gemini**:
```json
{
  "name": "google-gemini",
  "basemodel": "google/gemini-2.5-flash",
  "signature": "gemini-crypto-trader",
  "enabled": true,
  "openai_base_url": "https://api.google.com/v1",
  "openai_api_key": null
}
```

---

### 3. **Ollama** (Local, 100% FREE)
- **Cost**: FREE (runs locally)
- **Speed**: Depends on your machine
- **Models Available**: Llama 2, DeepSeek, Mistral, etc.
- **Download**: https://ollama.ai

#### Setup Ollama Locally:

```bash
# 1. Install Ollama from https://ollama.ai
# 2. Start Ollama service
ollama serve

# 3. In another terminal, pull a model
ollama pull llama2        # 3.8B parameters, ~2GB
# OR faster/smaller
ollama pull mistral       # 7B parameters, ~4GB
# OR very capable
ollama pull neural-chat   # 7B, optimized for chat

# 4. Test the API
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

**Config for Ollama**:
```json
{
  "name": "ollama-llama2",
  "basemodel": "ollama/llama2",
  "signature": "ollama-crypto-trader",
  "enabled": true,
  "openai_base_url": "http://localhost:11434/api",
  "openai_api_key": ""
}
```

---

### 4. **HuggingFace Inference API**
- **Cost**: FREE tier available
- **Models**: 300+ models
- **Sign-up**: https://huggingface.co

#### Setup HuggingFace:
```bash
export HUGGINGFACE_API_KEY="hf_xxxxx"
```

**Config for HuggingFace**:
```json
{
  "name": "huggingface-mistral",
  "basemodel": "mistralai/Mistral-7B-Instruct-v0.1",
  "signature": "hf-crypto-trader",
  "enabled": true,
  "openai_base_url": "https://api-inference.huggingface.co/models",
  "openai_api_key": null
}
```

---

### 5. **Replicate**
- **Cost**: $5 free credits (valid 14 days)
- **Models**: Many open-source models
- **Sign-up**: https://replicate.com

---

## 🎯 QUICKSTART: Free Testing in 5 Minutes

### Option A: Use Groq (Recommended - Fastest)

```bash
# 1. Sign up (free): https://console.groq.com
# 2. Copy API key from dashboard
# 3. Set environment variable
export GROQ_API_KEY="gsk_xxxxxxxxxxxxx"
export GROQ_API_BASE="https://api.groq.com/openai/v1"

# 4. Update .env.example
GROQ_API_KEY="gsk_xxxxxxxxxxxxx"
GROQ_API_BASE="https://api.groq.com/openai/v1"

# 5. Run with Groq config
python main.py configs/groq_config.json
```

### Option B: Use Ollama (Local, No API Key)

```bash
# 1. Install Ollama: https://ollama.ai
# 2. Start service
ollama serve

# 3. In another terminal, pull a model
ollama pull mistral

# 4. Set environment (optional, localhost is default)
export OLLAMA_API_BASE="http://localhost:11434/api"

# 5. Run with Ollama config
python main.py configs/ollama_config.json
```

### Option C: Use Google Gemini

```bash
# 1. Get free API key: https://aistudio.google.com/app/apikeys
# 2. Set environment variable
export GOOGLE_API_KEY="AIzaSyDxxxxxxxxxx"

# 3. Update .env.example
GOOGLE_API_KEY="AIzaSyDxxxxxxxxxx"

# 4. Run with Google config
python main.py configs/google_config.json
```

---

## 📊 Free LLM Comparison Table

| Provider | Model | Speed | Quality | Setup Difficulty | Cost |
|----------|-------|-------|---------|-----------------|------|
| **Groq** | Llama 3.3 70B | ⚡⚡⚡⚡⚡ Fastest | ⭐⭐⭐⭐ Good | Easy | 🆓 Free |
| **Google** | Gemini 2.5 Flash | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ Excellent | Easy | 🆓 Free |
| **Ollama** | Mistral 7B | ⚡⚡ Medium | ⭐⭐⭐ Fair | Easy | 🆓 Local |
| **HuggingFace** | Mistral 7B | ⚡ Slow | ⭐⭐⭐ Fair | Medium | 🆓 Free |
| **Replicate** | Various | ⚡⚡ Medium | ⭐⭐⭐⭐ Good | Easy | 💰 $5 credit |
| **DeepSeek** | V3 Chat | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ Excellent | Easy | 💰 Paid (cheap) |
| **OpenAI** | GPT-4o | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ Excellent | Easy | 💰 Paid (expensive) |

---

## 🛠️ Implementation: Add Free Provider Support

### Step 1: Update BaseAgent to support free providers

File: `agent/base_agent/base_agent.py`

```python
# Add after the existing Claude/OpenAI detection
if "groq" in basemodel.lower():
    print(f"🤖 Using Groq model: {basemodel}")
    self.model = ChatOpenAI(
        model=basemodel.replace("groq/", ""),
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY"),
        max_retries=3,
        timeout=30,
    )
elif "ollama" in basemodel.lower():
    print(f"🤖 Using Ollama model: {basemodel}")
    self.model = ChatOpenAI(
        model=basemodel.replace("ollama/", ""),
        base_url="http://localhost:11434/api/v1",
        api_key="dummy",  # Ollama doesn't need API key
        max_retries=3,
        timeout=30,
    )
```

### Step 2: Create config for free providers

Create `configs/free_testing_config.json`:

```json
{
  "agent_type": "BaseAgent",
  "crypto_mode": true,
  "trading_universe": ["BTC", "ETH"],
  "date_range": {
    "init_date": "2025-10-28",
    "end_date": "2025-11-02"
  },
  "models": [
    {
      "comment": "Groq - Fastest free option, completely FREE",
      "name": "groq-llama3.3",
      "basemodel": "groq/llama-3.3-70b-versatile",
      "signature": "groq-crypto-trader",
      "enabled": true,
      "openai_base_url": "https://api.groq.com/openai/v1",
      "openai_api_key": null
    }
  ],
  "agent_config": {
    "max_steps": 10,
    "max_retries": 3,
    "base_delay": 1.0,
    "initial_cash": 10000.0
  },
  "log_config": {
    "log_path": "./data/agent_data"
  }
}
```

### Step 3: Update .env.example

```bash
# Free LLM Provider API Keys (no credit card required)
GROQ_API_KEY=""                    # From https://console.groq.com
GOOGLE_API_KEY=""                  # From https://aistudio.google.com/app/apikeys
OLLAMA_API_BASE="http://localhost:11434/api/v1"

# Paid LLM Provider API Keys
OPENAI_API_KEY=""
DEEPSEEK_API_KEY=""
ANTHROPIC_API_KEY=""
```

---

## 🧪 Testing Without Spending Money

### Local Testing (Offline)

```bash
# 1. Install Ollama
# 2. Pull a small model
ollama pull neural-chat  # ~5GB, very capable

# 3. Run locally (completely FREE, no internet required)
python main.py configs/ollama_config.json

# 4. Test everything locally
# No API calls, no costs!
```

### Free Tier Testing (Online)

```bash
# 1. Sign up for Groq (completely free)
# 2. Get API key
# 3. Test for free with unlimited calls
python main.py configs/groq_config.json

# Still free! Groq has NO rate limits for free tier
```

### Mock/Dummy Testing (For CI/CD)

For GitHub Actions, you might want a dummy LLM for quick testing:

```python
class MockLLM:
    def __init__(self):
        self.model = "mock-llm"

    def invoke(self, messages):
        # Return mock trading decisions
        return {
            "content": "HOLD BTC ETH"  # Dummy response
        }
```

---

## 📋 Step-by-Step: Test with Groq Now

```bash
# 1. Go to https://console.groq.com
# 2. Click "Sign Up" (completely free, no credit card)
# 3. Verify email
# 4. Go to API Keys section
# 5. Copy your API key
# 6. Set it locally
export GROQ_API_KEY="gsk_xxxxxxxxxxxxx"

# 7. Create groq_config.json based on template above
cp configs/crypto_config.json configs/groq_config.json
# Edit groq_config.json and update to use Groq model

# 8. Run it!
python main.py configs/groq_config.json

# Test passed? You can trade for free with Groq!
```

---

## ⚠️ Free Tier Limitations

| Provider | Limit | How Often |
|----------|-------|-----------|
| Groq | None | Unlimited (free forever) |
| Google Gemini | 1M tokens/min | Per minute |
| Ollama | None | Unlimited (local) |
| HuggingFace | Rate limited | Slow |
| Replicate | $5 | One-time (14 days) |

---

## 💡 Recommendation for FREE Testing

**Best Option**: Use **Groq**
- ✅ Completely FREE
- ✅ Super FAST (300+ tokens/sec)
- ✅ No credit card needed
- ✅ No rate limits
- ✅ High quality model (Llama 3.3 70B)
- ✅ Easy setup (5 minutes)

**Runner-up**: Use **Ollama** locally
- ✅ Completely FREE
- ✅ No internet required after setup
- ✅ No API key needed
- ✅ Good quality models available

---

## 🚀 Next Steps

1. **Choose your free provider** (Groq recommended)
2. **Sign up** (takes 2 minutes)
3. **Get API key**
4. **Create config file** (copy from templates above)
5. **Run the trading agent** `python main.py configs/groq_config.json`
6. **Test everything** completely FREE!

---

**Remember**: No credit card required for any of these options! 🎉

**Last Updated**: 2025-11-02
