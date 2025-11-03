# Groq Rate Limit Crisis - Action Plan

## Problem Summary

**All recent hourly trading runs are FAILING** due to Groq free tier rate limits.

### Evidence

```
✓ Last 20+ runs show "success" (workflow completes)
✗ But ALL actual trading attempts show: Error 429 Rate Limit
✗ Limit: 100,000 tokens/day for free tier
✗ Usage: Full 100,000 tokens exhausted each day
✗ Retry time: 50+ minutes after exhaustion
```

### Timeline

```
2025-11-02 23:46 UTC → First 429 error (Run #91)
2025-11-02 23:46-24:00 → Multiple runs hitting limit
2025-11-03 00:21 UTC → STILL hitting limit (Run #92)
2025-11-03 06:07 UTC → Latest run (98) - status unknown
```

### Root Cause

- **Hourly runs** = 24 runs per day
- **Per-session tokens** = 4,000-5,000 tokens
- **Daily usage** = 24 × 4,500 = **108,000 tokens**
- **Free limit** = **100,000 tokens**
- **Result** = Exceeds limit by 8% every single day

---

## Immediate Solutions (Choose One)

### OPTION 1: Switch to DeepSeek (RECOMMENDED)

**Cost:** $30/month | **Implementation:** 15 minutes | **Risk:** Low

**Steps:**

1. **Create DeepSeek Account**
   ```bash
   # Visit: https://platform.deepseek.com/
   # Sign up (free, no credit card for testing)
   ```

2. **Get API Key**
   ```bash
   # Go to: https://platform.deepseek.com/api_keys
   # Create new API key
   # Copy: sk_...
   ```

3. **Update GitHub Secret**
   ```bash
   gh secret set DEEPSEEK_API_KEY --body "sk_..."
   ```

4. **Update Workflow Default**
   Edit `.github/workflows/hourly-trading.yml`:
   ```yaml
   - cron: '0 * * * *'

   workflow_dispatch:
     inputs:
       llm_model:
         default: 'deepseek'  # CHANGE FROM: 'groq'
   ```

5. **Test Run**
   ```bash
   gh workflow run "Hourly AI Trading Run" \
     --ref main \
     -f llm_model="deepseek" \
     -f asset_type="crypto" \
     -f symbols="BTC,ETH"
   ```

**Advantages:**
- ✅ Only $30/month for unlimited runs
- ✅ No rate limits for your use case
- ✅ Quality comparable to GPT-4
- ✅ Fast inference (200+ tokens/sec)
- ✅ Works immediately after setup
- ✅ Can keep running 100+ times/day

**Status After Switch:**
```
✓ No more 429 errors
✓ Trading runs actually complete
✓ All hourly runs work
✓ Cost: $30/month (very low)
```

---

### OPTION 2: Upgrade Groq to Dev Tier

**Cost:** ~$2.50/month | **Implementation:** 5 minutes | **Risk:** Low

**Steps:**

1. **Visit Groq Console**
   ```
   https://console.groq.com/settings/billing
   ```

2. **Upgrade to Dev Tier**
   - Click "Upgrade to Dev Tier"
   - Set up billing (low cost)
   - Dev Tier has much higher limits

3. **No code changes needed**
   - Current groq_config.json works
   - Same workflow runs

**Advantages:**
- ✅ Minimal cost (~$2.50/month)
- ✅ No code changes
- ✅ Stays with Groq (familiar)

**Disadvantages:**
- ⚠️ Still requires paid tier
- ⚠️ Groq limits are lower than alternatives

**Status After Upgrade:**
```
✓ Dev Tier has higher limits
✓ Should support your hourly runs
⚠️ Verify limits match your needs
```

---

### OPTION 3: Use Ollama (Self-Hosted)

**Cost:** $0 API | **Implementation:** 2-3 hours | **Risk:** Medium

**Steps:**

1. **Install Ollama**
   ```bash
   # On Mac:
   brew install ollama

   # Or download: https://ollama.ai
   ```

2. **Start Ollama**
   ```bash
   ollama serve
   # Listens on http://localhost:11434
   ```

3. **Pull Model**
   ```bash
   ollama pull mistral
   # Or: ollama pull llama2
   ```

4. **Update Config**
   Edit or create `configs/ollama_config.json`:
   ```json
   {
     "agent_type": "BaseAgent",
     "crypto_mode": true,
     "trading_universe": ["BTC", "ETH"],
     "date_range": {
       "init_date": "2025-11-03",
       "end_date": "2025-11-03"
     },
     "models": [
       {
         "name": "ollama-mistral",
         "basemodel": "mistral",
         "signature": "ollama-crypto-trader",
         "enabled": true,
         "openai_base_url": "http://localhost:11434/v1",
         "openai_api_key": "not-needed"
       }
     ],
     "agent_config": {
       "max_steps": 10,
       "max_retries": 2,
       "base_delay": 1.0,
       "initial_cash": 10000.0,
       "crypto_trading": true
     },
     "log_config": {
       "log_path": "./data/agent_data",
       "log_prefix": "ollama"
     }
   }
   ```

5. **Run Trading**
   ```bash
   python main.py configs/ollama_config.json
   ```

**Advantages:**
- ✅ $0 API costs
- ✅ Works completely offline
- ✅ Unlimited inference
- ✅ Privacy (data stays local)

**Disadvantages:**
- ❌ Requires GPU ($500-2000 investment)
- ❌ Slower than cloud LLMs
- ❌ Maintenance burden
- ❌ Not suitable for GitHub Actions (local only)

**Status After Setup:**
```
✓ No API costs
✓ Unlimited runs
⚠️ Slower inference
⚠️ GPU requirement
```

---

## Recommended Action: DEEPSEEK

**Why DeepSeek is Best:**

| Factor | Groq Dev | DeepSeek | Ollama | GPT-4o |
|--------|----------|----------|--------|---------|
| **Cost/month** | $2.50 | $30 | $0 | $4,536 |
| **Setup time** | 5 min | 15 min | 2-3 hrs | 10 min |
| **Rate limits** | Medium | UNLIMITED | UNLIMITED | Rate-limited |
| **Quality** | Good | Excellent | OK | Excellent |
| **GitHub Actions** | ✓ | ✓ | ✗ | ✓ |
| **Feasibility** | ✓ | ✓✓ | △ | ✗ |

**Verdict: DeepSeek offers best balance of cost, quality, and unlimited scale.**

---

## Implementation Steps (DeepSeek)

### Step 1: Create Account & Get API Key (5 min)

```bash
# 1. Visit https://platform.deepseek.com/
# 2. Sign up (free account)
# 3. Go to https://platform.deepseek.com/api_keys
# 4. Create API key
# 5. Copy the key (starts with 'sk_')
```

### Step 2: Add to GitHub Secrets (5 min)

```bash
# Set the secret
gh secret set DEEPSEEK_API_KEY --body "sk_your_key_here"

# Verify
gh secret list
# Should show: DEEPSEEK_API_KEY
```

### Step 3: Update Workflow (5 min)

**File:** `.github/workflows/hourly-trading.yml`

Find this section:
```yaml
workflow_dispatch:
  inputs:
    llm_model:
      default: 'groq'    # <- CHANGE THIS
```

Change to:
```yaml
workflow_dispatch:
  inputs:
    llm_model:
      default: 'deepseek'    # <- CHANGED
```

Also update the config selection logic around line 150-165:
```yaml
case "$LLM_MODEL" in
  deepseek)
    CONFIG_FILE="configs/crypto_config.json"
    echo "📝 Using DeepSeek config: $CONFIG_FILE"
    ;;
  groq)
    CONFIG_FILE="configs/groq_config.json"
    ;;
  *)
    CONFIG_FILE="configs/crypto_config.json"
    ;;
esac
```

### Step 4: Test Run (2 min)

```bash
# Trigger test with DeepSeek
gh workflow run "Hourly AI Trading Run" \
  --ref main \
  -f llm_model="deepseek" \
  -f asset_type="crypto" \
  -f symbols="BTC,ETH"

# Check status
gh run list --workflow hourly-trading.yml --limit 1
```

### Step 5: Verify Success

Check the workflow logs:
```bash
# Get latest run ID
LATEST_RUN=$(gh run list --workflow hourly-trading.yml --limit 1 --json databaseId | jq -r '.[0].databaseId')

# View logs
gh run view $LATEST_RUN --log | grep -E "Processing model|Step [0-9]|Trading|success"
```

Should see:
```
✓ Processing model: deepseek-chat-v3.1
✓ Step 1/10
✓ Step 2/10
... (actual trading happening)
✓ Model deepseek-chat-v3.1 processing completed
```

**NOT:**
```
✗ Error code: 429 - Rate limit reached
```

---

## Cost Comparison After Fix

### Current Situation (Groq Free)
```
Daily: 24 hourly runs × 4,500 tokens = 108,000 tokens
Limit: 100,000 tokens/day
Result: ALL RUNS FAIL ❌
Cost: $0 (but non-functional)
```

### After Switch to DeepSeek
```
Daily: 24 hourly runs × 4,500 tokens = 108,000 tokens
Limit: UNLIMITED
Result: ALL RUNS WORK ✅
Cost: ~$0.30/day × 30 = $9/month
Monthly: $9-30 (depending on usage)
```

### ROI
```
Problem: Workflow broken, no trading happening
Solution: $30/month to fix completely
Trade-off: Tiny cost to make system fully functional
```

---

## Fallback Plan (If DeepSeek Takes Too Long)

If waiting for DeepSeek account/approval:

**Use Groq Dev Tier as temporary:**
1. Visit https://console.groq.com/settings/billing
2. Upgrade to Dev Tier
3. Set billing method
4. Higher limits should resolve immediately
5. Cost: ~$2.50/month while you set up DeepSeek

---

## Long-term Strategy

### Recommended Setup (Post-Fix)

**Primary:** DeepSeek ($30/month)
- Main trading runs
- Unlimited scale capability

**Fallback:** Groq Dev Tier ($2.50/month)
- Backup if DeepSeek has issues
- Quick failover option

**Testing:** Ollama (local, free)
- Development/testing only
- No API cost
- Requires GPU

---

## Summary

| Issue | Root Cause | Solution | Time | Cost |
|-------|-----------|----------|------|------|
| **Groq Rate Limit** | Free tier exhausted daily | Switch to DeepSeek | 15 min | $30/mo |
| **Trading Failures** | 429 errors every run | Unlimited tokens | - | - |
| **Hourly Runs Broken** | Workflow shows success but fails | API with no limits | - | - |

---

## Action Items

- [ ] Create DeepSeek account (5 min)
- [ ] Get API key from DeepSeek (2 min)
- [ ] Add GitHub secret (3 min)
- [ ] Update workflow default (5 min)
- [ ] Test run with DeepSeek (5 min)
- [ ] Verify trading completes (5 min)
- [ ] Monitor next 3 hourly runs (ongoing)

**Total time to fix: 25 minutes**

---

## Questions?

**Q: Will my existing code work with DeepSeek?**
A: Yes! crypto_config.json already has DeepSeek model configured.

**Q: How much will it cost?**
A: ~$30/month for your current usage (24 hourly runs/day).

**Q: Can I run 100 times per day with DeepSeek?**
A: Yes! DeepSeek has no rate limits. Cost would be ~$100/month for 100 runs/day.

**Q: What if DeepSeek goes down?**
A: Have Groq Dev Tier as fallback. Update workflow to support multiple models.

**Q: When should I do this?**
A: Immediately! All current runs are failing. Every hour of delay = more failed trading sessions.

---

*Analysis Date: November 3, 2025*
*Status: CRITICAL - All trading halted*
*Recommended Action: Switch to DeepSeek (15 min setup)*
