# DeepSeek Pricing: 100 Trading Runs Per Day

## Input: Your Pricing Model

```
MODEL: deepseek-chat (DeepSeek-V3.2-Exp)

PRICING:
- Input (cache hit):   $0.028 per 1M tokens
- Input (no cache):    $0.28 per 1M tokens
- Output:              $0.42 per 1M tokens

CONTEXT: 128K
MAX OUTPUT: 8K
```

---

## Calculation: 100 Runs Per Day

### Token Breakdown Per Run
```
Average per trading session: ~4,500 tokens
├─ Input tokens (80%):  3,600 tokens
└─ Output tokens (20%): 900 tokens
```

### Daily Total (100 runs)
```
Total tokens:  100 × 4,500 = 450,000 tokens/day
├─ Input:      360,000 tokens
└─ Output:     90,000 tokens
```

---

## Cost Scenarios

### Scenario A: No Caching (First Day - Worst Case)

```
Input cost:    360,000 tokens × ($0.28 / 1,000,000) = $0.1008
Output cost:   90,000 tokens × ($0.42 / 1,000,000) = $0.0378
─────────────────────────────────────────────────────
Daily Total:                                         $0.1386
Monthly (30 days):                                   $4.16
```

### Scenario B: With Cache Hits (Realistic - After Day 1)

After the first trading session, DeepSeek caches the system prompt and context. Subsequent runs benefit from cache hits.

**Assumption: 75% of input tokens hit cache**

```
Cached input:     270,000 × ($0.028 / 1,000,000) = $0.00756
Non-cached input: 90,000 × ($0.28 / 1,000,000) = $0.0252
Output tokens:    90,000 × ($0.42 / 1,000,000) = $0.0378
─────────────────────────────────────────────────────
Daily Total:                                     $0.07056
Monthly (30 days):                              $2.12
```

### Scenario C: Maximum Caching (90% Cache Hit Rate)

If most of the system prompt and trading logic is cached:

```
Cached input:     324,000 × ($0.028 / 1,000,000) = $0.009072
Non-cached input: 36,000 × ($0.28 / 1,000,000) = $0.010080
Output tokens:    90,000 × ($0.42 / 1,000,000) = $0.037800
─────────────────────────────────────────────────────
Daily Total:                                     $0.056952
Monthly (30 days):                              $1.71
```

---

## Summary Table: 100 Runs Per Day

| Scenario | Cache Hit % | Daily Cost | Monthly Cost | Notes |
|----------|------------|-----------|--------------|-------|
| **A: No Cache** | 0% | $0.139 | **$4.16** | First day, no optimization |
| **B: Realistic** | 75% | $0.071 | **$2.12** | After cache builds up |
| **C: Optimized** | 90% | $0.057 | **$1.71** | Maximum caching |
| **D: Your current usage** (24 runs/day) | 75% | $0.017 | **$0.51** | Current system |

---

## Real-World Estimate

**For 100 runs per day, expect to pay: $1.50 - $2.50/month**

### Why the Range?

1. **First few days:** Higher cost ($4+/day) until cache builds
2. **After a week:** Cache stabilizes at ~75% hit rate ($2/month)
3. **After 30 days:** Potentially 85-90% cache hit ($1.50/month)

### Cost Drivers

```
High Cache Hit = Low Cost:
- System prompt is cached after first run
- Trading logic is cached
- Market context is reused

Low Cache Hit = Higher Cost:
- New market conditions require new tokens
- System prompt changes
- Different trading strategies
```

---

## Comparison: 100 Runs/Day with Other Providers

| Provider | Model | Daily Cost | Monthly Cost | Rate Limits | Viability |
|----------|-------|-----------|--------------|------------|-----------|
| **DeepSeek** | deepseek-chat | $0.06-0.14 | **$1.50-4.16** | UNLIMITED | ✅ EXCELLENT |
| **OpenAI** | gpt-4o | ~$1.50 | ~$45 | 3,500 RPM | ⚠️ OK |
| **OpenAI** | gpt-4 | ~$3.00 | ~$90 | 500 RPM | ⚠️ RISKY |
| **Groq** | llama-3.3-70b | $0 | $0 | 100K/day | ❌ TOO LOW |
| **Claude** | 3.5-sonnet | ~$1.25 | ~$37.50 | 50 RPM | ⚠️ BOTTLENECK |
| **Ollama** | Local | $0 | $0 (infra) | UNLIMITED | ✅ FREE |

---

## Breaking Down the Cost

### Per-Run Cost (with cache)

```
Cost per 100 runs/day:  $0.071/day ÷ 100 = $0.00071 per run
Cost per 1,000 runs/month: $2.12 ÷ 30 × 1000 ÷ 100 = $0.707 per run
```

### Comparison to Coffee ☕

```
100 runs/day for 1 month: $2.12
Cost per day: $0.07
Equivalent to: 1 coffee every 14 days
```

---

## When 100 Runs/Day Makes Sense

### Use Cases

1. **High-frequency trading bot** ✅
   - Trading every 15 minutes
   - Multiple pairs simultaneously
   - Cost: $2/month is trivial

2. **Research & backtesting** ✅
   - Testing strategies
   - Optimization runs
   - Cost-effective analysis

3. **Multi-strategy trading** ✅
   - 4+ different trading agents
   - 25 runs each per day
   - Total 100 runs: only $2/month

4. **Portfolio management** ✅
   - Daily rebalancing
   - Multiple watchlists
   - Real-time analysis

---

## Cost Optimization Tips

### 1. Maximize Cache Hits
```
Same system prompt for all runs = better cache
Same trading pairs = cache reuse
```

### 2. Batch Similar Requests
```
Group similar market conditions
Reuse analysis from previous runs
```

### 3. Use Thinking Mode Selectively
```
deepseek-chat: Normal (cheaper)
deepseek-reasoner: Only when needed (more expensive)
```

### 4. Monitor Usage
```bash
# Check your current daily spend
# Use DeepSeek dashboard to monitor tokens used
# Adjust trading frequency based on ROI
```

---

## Monthly Cost Examples

### Different Trading Frequencies

| Frequency | Runs/Day | Daily Cost | Monthly Cost |
|-----------|----------|-----------|--------------|
| Hourly | 24 | $0.017 | $0.51 |
| Every 6 hours | 4 | $0.003 | $0.09 |
| Twice daily | 2 | $0.001 | $0.03 |
| **Every 15 min** | **96** | **$0.067** | **$2.01** |
| **Every 10 min** | **144** | **$0.101** | **$3.02** |
| **Every 5 min** | **288** | **$0.202** | **$6.05** |
| **Continuous** | **1,440** | **$1.010** | **$30.30** |

---

## Final Answer

### For 100 Trading Runs Per Day:

```
ESTIMATED COST: $1.50 - $2.50/month

Breakdown:
├─ First day (no cache):      ~$0.14/day
├─ Days 2-7 (cache building): ~$0.08/day
├─ Week 2+ (optimized):       ~$0.06/day
└─ Steady state (month 2+):   ~$0.05/day

Average monthly: $2.12
```

### Cost Comparison

```
Current (24 runs/day):  $0.51/month
100 runs/day:           $2.12/month
Additional cost:        $1.61/month (4x the runs, 4x the cost)

ROI perspective:
- If 100 runs generate $10+ profit/day = Break even in hours
- If used for optimization = Extremely cost-effective
```

---

## Decision Matrix

**Should you run 100 times per day?**

| Factor | Analysis |
|--------|----------|
| **Cost** | ✅ Trivial ($2/month) |
| **Token budget** | ✅ UNLIMITED |
| **Rate limits** | ✅ UNLIMITED |
| **Profit potential** | ✅ 4x more runs = 4x more opportunities |
| **Infrastructure** | ✅ GitHub Actions handles it |
| **Risk** | ✅ Very low cost to experiment |

**Verdict: YES, absolutely run 100 times/day if you want to!**

---

## Action Items

```bash
# 1. Monitor current costs
# Check DeepSeek dashboard regularly

# 2. Scale gradually
# Day 1: Keep at 24 runs/hour (current)
# Week 1: Increase to 50 runs/day if happy
# Month 1: Scale to 100+ if profitable

# 3. Optimize based on results
# Track ROI per run
# Adjust frequency based on profitability
```

---

*Analysis Date: November 3, 2025*
*Based on DeepSeek pricing you provided*
*Prices subject to change - verify with DeepSeek*
