# LLM Cost Analysis: Running 100 Trading Sessions/Day

## Executive Summary

For **100 trading sessions per day**, costs vary dramatically by provider:

| Provider | Daily Cost | Monthly Cost | Status |
|----------|-----------|--------------|--------|
| **Groq** | $0 | $0 | **FREE** (within free tier limits) |
| **DeepSeek** | ~$0.30-0.60 | ~$9-18 | 💰 **CHEAPEST** |
| **Ollama (Local)** | $0 | $0 | **FREE** (open-source, self-hosted) |
| **OpenAI GPT-4** | ~$100-150 | ~$3,000-4,500 | ❌ **EXPENSIVE** |
| **OpenAI GPT-4o** | ~$30-50 | ~$900-1,500 | ⚠️ **MODERATE-HIGH** |
| **Claude 3.5 Sonnet** | ~$60-90 | ~$1,800-2,700 | ⚠️ **HIGH** |

---

## Token Usage Calculation

### Current Configuration Analysis

**From last pipeline run errors:**
- Per-step token usage: **4,049 - 4,273 tokens**
- Configuration: **max_steps = 10** (Groq) or **max_steps = 30** (DeepSeek)
- Retries: **max_retries = 3**

### Scenarios for 100 Runs/Day

#### Scenario A: Conservative (Groq, 10 steps, no errors)
```
Tokens per session:  4,200 tokens × 10 steps = 42,000 tokens
100 sessions/day:    42,000 × 100 = 4,200,000 tokens/day
Monthly (30 days):   4,200,000 × 30 = 126,000,000 tokens/month
```

#### Scenario B: Standard (DeepSeek, 30 steps, occasional errors)
```
Tokens per session:  4,200 tokens × 30 steps × 1.2 (errors) = 151,200 tokens
100 sessions/day:    151,200 × 100 = 15,120,000 tokens/day
Monthly (30 days):   15,120,000 × 30 = 453,600,000 tokens/month
```

#### Scenario C: Worst-case (GPT-4, 30 steps, max retries)
```
Tokens per session:  4,200 tokens × 30 steps × 1.5 (retries) = 189,000 tokens
100 sessions/day:    189,000 × 100 = 18,900,000 tokens/day
Monthly (30 days):   18,900,000 × 30 = 567,000,000 tokens/month
```

---

## Detailed Provider Pricing

### 1. Groq (RECOMMENDED FOR FREE TIER)

**Pricing Model:**
- Free tier: **100,000 tokens/day** + **12,000 tokens/minute**
- Dev Tier: Paid option with higher limits

**For 100 Runs/Day (4.2M tokens):**

| Tier | Status | Cost |
|------|--------|------|
| Free | ❌ EXCEEDS | Not viable |
| Dev Tier | ✅ VIABLE | ~$0.02/1M tokens |

**Dev Tier Calculation:**
```
4.2M tokens × $0.02 = $0.084/day
$0.084 × 30 = $2.52/month
```

**Limitations:**
- Free tier: Maxes out after ~1-2 runs
- Dev Tier: Affordable but requires signup

**Status:** 🟡 Free tier insufficient; Dev Tier ~$2.50/month

---

### 2. DeepSeek (BEST COST-EFFECTIVE)

**Pricing Model:**
- Cache hit: **$0.014 per 1M input tokens**
- Cache write: **$0.14 per 1M input tokens**
- Output: **$0.28 per 1M output tokens**
- No rate limits (very generous)

**For 100 Runs/Day (15.1M tokens):**

```
Input (80%):   15.1M × 0.80 × $0.014 = $0.169/day
Output (20%):  15.1M × 0.20 × $0.28  = $0.846/day
Total:         $1.015/day ≈ $30/month
```

**Advantages:**
- ✅ Cheapest option for high-frequency use
- ✅ No rate limits (perfect for 100x/day)
- ✅ Fast inference
- ✅ Good quality

**Status:** 🟢 **BEST OPTION - ~$30/month for 100x/day**

---

### 3. Ollama (FREE, SELF-HOSTED)

**Pricing Model:**
- **FREE** - Open source, runs on your machine
- No API costs
- Only infrastructure costs (electricity, compute)

**For 100 Runs/Day:**
```
API Cost: $0/day = $0/month
Infrastructure: ~$1-3/day (electricity + hardware depreciation)
Total: ~$30-90/month (self-hosted)
```

**Advantages:**
- ✅ Zero API costs
- ✅ Unlimited inference
- ✅ Privacy (data stays local)
- ✅ Works offline

**Disadvantages:**
- Requires GPU ($500-2000 investment)
- Slower than cloud (unless high-end GPU)
- Maintenance burden

**Status:** 🟢 **FREE - Best for infrastructure investment**

---

### 4. OpenAI (GPT-4o, MODERATE COST)

**Pricing Model:**
- Input: **$0.005 per 1K tokens**
- Output: **$0.015 per 1K tokens**
- Rate limits: 3,500 RPM (fine for 100 runs)

**For 100 Runs/Day (18.9M tokens):**

```
Assumptions: 70% input, 30% output
Input (70%):   18.9M × 0.70 × $0.005 = $66.15/day
Output (30%):  18.9M × 0.30 × $0.015 = $85.05/day
Total:         $151.20/day = $4,536/month ❌ EXPENSIVE
```

**Status:** 🔴 **NOT RECOMMENDED - $4,536/month**

---

### 5. OpenAI (GPT-4 Turbo, VERY EXPENSIVE)

**Pricing Model:**
- Input: **$0.01 per 1K tokens**
- Output: **$0.03 per 1K tokens**

**For 100 Runs/Day (18.9M tokens):**

```
Input (70%):   18.9M × 0.70 × $0.01  = $132.30/day
Output (30%):  18.9M × 0.30 × $0.03  = $170.10/day
Total:         $302.40/day = $9,072/month ❌ EXTREMELY EXPENSIVE
```

**Status:** 🔴 **NOT VIABLE - $9,072/month**

---

### 6. Anthropic Claude 3.5 Sonnet

**Pricing Model:**
- Input: **$0.003 per 1K tokens**
- Output: **$0.015 per 1K tokens**
- Rate limits: 50 RPM (bottleneck for 100x/day)

**For 100 Runs/Day (18.9M tokens):**

```
Input (70%):   18.9M × 0.70 × $0.003 = $39.69/day
Output (30%):  18.9M × 0.30 × $0.015 = $85.05/day
Total:         $124.74/day = $3,742/month ❌ EXPENSIVE
```

**Additional Issue:** Rate limit of 50 RPM = max 3,000 requests/hour
- For 100 simultaneous runs: **Would need batching/queuing**

**Status:** 🔴 **NOT RECOMMENDED - $3,742/month + rate limiting**

---

## Cost Comparison Chart

### Daily Costs (100 runs, optimized)

```
Groq Free Tier       ║ ❌ Exceeded
Ollama Local         ║ ✅✅✅✅✅ $2-3/day
Groq Dev Tier        ║ ✅✅ $0.08/day
DeepSeek             ║ ✅✅✅ $1/day
OpenAI GPT-4o        ║ ❌❌❌❌❌ $150/day
Claude 3.5           ║ ❌❌❌❌ $125/day
OpenAI GPT-4 Turbo   ║ ❌❌❌❌❌ $300/day
```

### Monthly Costs (100 runs/day × 30 days)

```
Ollama Local        $60-90/month
Groq Dev Tier       $2.50/month
DeepSeek            $30/month
OpenAI GPT-4o       $4,536/month
Claude 3.5          $3,742/month
OpenAI GPT-4 Turbo  $9,072/month
```

---

## Recommendation Matrix

### Choose Based on Your Constraints

| Use Case | Recommendation | Cost | Config |
|----------|---|---|---|
| **Free, unlimited** | Ollama (local) | $0 API | `configs/ollama_config.json` |
| **Cheapest cloud** | DeepSeek | $30/month | `configs/crypto_config.json` (enabled) |
| **Quick free test** | Groq Free Tier | $0 | Only ~2 runs/day |
| **Unlimited free test** | Groq Dev Tier | $2.50/month | Upgrade free account |
| **Production quality** | DeepSeek | $30/month | Best price/quality ratio |
| **Premium (not cost-effective)** | Claude 3.5 | $3,742/month | Only if required |

---

## Your Current Situation

### Current Config Analysis

**groq_config.json:**
- Model: llama-3.3-70b-versatile
- Max steps: 10
- Tokens/session: ~42,000
- Status: ✅ Working, but **free tier limits reached**

**crypto_config.json (DeepSeek enabled):**
- Model: deepseek-chat-v3.1
- Max steps: 30
- Tokens/session: ~126,000-151,000
- Status: ✅ Ready to use, **very affordable**

---

## Action Plan for 100 Runs/Day

### Option 1: DeepSeek (RECOMMENDED)
```bash
# Cost: ~$30/month

# 1. Create DeepSeek account
# https://platform.deepseek.com/

# 2. Get API key
# https://platform.deepseek.com/api_keys

# 3. Set up environment
export DEEPSEEK_API_KEY="sk_..."
export DEEPSEEK_API_BASE="https://api.deepseek.com/v1"

# 4. Run trading
python main.py configs/crypto_config.json

# 5. Scale to 100 runs
# Modify .github/workflows/hourly-trading.yml to:
# - Call main.py 100 times in parallel
# - Or trigger workflow 100 times/day
```

### Option 2: Groq Dev Tier (FREE ALTERNATIVE)
```bash
# Cost: ~$2.50/month (if Dev Tier required)

# 1. Upgrade free Groq account to Dev Tier
# https://console.groq.com/settings/billing

# 2. Run trading
python main.py configs/groq_config.json

# 3. Verify higher limits
# Should support 100 runs/day with Dev Tier
```

### Option 3: Ollama (SELF-HOSTED, NO API COST)
```bash
# Cost: $0 API + infrastructure

# 1. Install Ollama
# https://ollama.ai

# 2. Pull model
ollama pull mistral

# 3. Run locally
# Modify configs/ollama_config.json with local endpoint:
# "openai_base_url": "http://localhost:11434/v1"

# 4. Run trading
python main.py configs/ollama_config.json
```

---

## Cost Optimization Tips

### 1. **Reduce Tokens per Session**
```python
# In configs:
"max_steps": 5,  # Instead of 10-30 (reduces by 50-70%)
"max_retries": 1,  # Instead of 3 (reduces retries)
```

### 2. **Cache Results**
```python
# Don't re-fetch prices in same session
# Reuse previous analysis
```

### 3. **Batch Processing**
```python
# Run multiple analyses per API call
# Combine 5 trading decisions into 1 request
```

### 4. **Time-based Rate Limiting**
```bash
# Run 100 sessions across 10 hours (not all at once)
# Reduces rate limit pressure
# For every 6 minutes, run 1 session
```

---

## Summary Table

**For 100 Trading Runs Per Day:**

| Metric | Groq Free | Groq Dev | DeepSeek | Ollama | GPT-4o | GPT-4 |
|--------|-----------|----------|----------|--------|--------|--------|
| **Daily Cost** | ❌ Exceeded | $0.08 | $1 | $2-3 | $150 | $300 |
| **Monthly Cost** | ❌ Exceeded | $2.50 | $30 | $60-90 | $4,536 | $9,072 |
| **Setup Time** | 5 min | 10 min | 15 min | 2 hours | 10 min | 10 min |
| **Viability** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| **Recommended** | - | 🟡 OK | 🟢 BEST | 🟢 BEST | ❌ No | ❌ No |

---

## Conclusion

**For running 100 trading sessions per day:**

1. **Best Cost-Effective:** DeepSeek (~$30/month) ✅
2. **Cheapest (self-hosted):** Ollama (free API) ✅
3. **Free but limited:** Groq Dev Tier ($2.50/month if needed)
4. **Not recommended:** OpenAI GPT models ($3,700-9,000/month) ❌

**Immediate Action:**
- Enable DeepSeek in `configs/crypto_config.json`
- Add `DEEPSEEK_API_KEY` to GitHub secrets
- Run: `gh workflow run "Hourly AI Trading Run" -f llm_model="deepseek"`
- Cost: **~$30/month for unlimited runs**

---

*Analysis Date: November 2, 2025*
*Based on current pricing as of this date*
*Prices subject to change - verify with providers*
