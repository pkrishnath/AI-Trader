# Enhanced Logging Guide

## Overview

The `tools/enhanced_logging.py` module provides detailed, colorized logging for the trading agent. This allows you to:

1. **See what the AI is thinking** - Agent reasoning and thought process
2. **Track tool execution** - Function calls, parameters, and results
3. **Monitor market analysis** - Data being analyzed and decisions made
4. **Debug issues** - Detailed error context and diagnostics
5. **Understand decisions** - Rationale behind trading actions

---

## Quick Start

### Using the Logger

```python
from tools.enhanced_logging import get_logger, log_detailed_step

logger = get_logger()

# Log a section header
logger.header("Trading Session Started")

# Log AI thinking
logger.thinking("BTC is up 5% today, ETH is down 2%. Should increase BTC position.")

# Log tool calls
logger.tool_call("buy", {"symbol": "BTC", "amount": 0.5})

# Log tool results
logger.tool_result("buy", {"status": "success", "price": 45000})

# Log market data
logger.market_data("BTC", {
    "price": 45000,
    "change": "+5%",
    "volume": "2.3B"
})

# Log trade decisions
logger.trade_decision("buy", "BTC", 0.5, "Market uptrend detected")

# Log portfolio performance
logger.performance(
    portfolio_value=12500,
    cash=5000,
    p_and_l=2500
)
```

---

## Logger Methods

### Formatting Methods

#### `header(title: str)`
Print a major section header
```python
logger.header("TRADING SESSION")
# Output:
# ======================================================================
#                         TRADING SESSION
# ======================================================================
```

#### `subheader(title: str)`
Print a subsection header
```python
logger.subheader("Market Analysis")
# Output:
# ▶ Market Analysis
```

#### `step(step_num: int, total_steps: int, message: str = "")`
Log an agent step
```python
logger.step(1, 30, "Analyzing current positions")
# Output:
# 🔄 Step 1/30: Analyzing current positions
```

---

### Content Logging Methods

#### `thinking(thought: str)`
Log AI reasoning
```python
logger.thinking("""
Looking at the data:
- BTC momentum is strong
- Volume is increasing
- Moving average shows uptrend
Decision: Increase position
""")
# Output with purple background:
# 💭 AI Thinking:
#    Looking at the data:
#    - BTC momentum is strong
#    ...
```

#### `tool_call(tool_name: str, args: Dict[str, Any])`
Log a function call
```python
logger.tool_call("buy", {
    "symbol": "BTC",
    "amount": 0.5,
    "limit_price": 45000
})
# Output with blue formatting:
# 🔧 Calling tool: buy
#    {
#      "symbol": "BTC",
#      "amount": 0.5,
#      "limit_price": 45000
#    }
```

#### `tool_result(tool_name: str, result: Any, success: bool = True)`
Log tool result
```python
logger.tool_result("buy", {
    "status": "success",
    "price": 45000,
    "shares": 0.5,
    "total": 22500
}, success=True)
# Output with green check:
# ✅ Tool result from buy:
#    {
#      "status": "success",
#      ...
#    }
```

#### `market_data(symbol: str, data: Dict[str, Any])`
Log market information
```python
logger.market_data("BTC", {
    "price": 45000.50,
    "high": 46000,
    "low": 44500,
    "volume": 2300000000,
    "change_percent": "+5.2%"
})
# Output:
# 📊 Market Data for BTC:
#    price: 45000.50
#    high: 46000
#    ...
```

#### `position(symbol: str, quantity: float, price: float, value: float)`
Log position details
```python
logger.position("BTC", 1.5, 45000, 67500)
# Output with green formatting:
# 📈 Position: BTC
#    Quantity: 1.5
#    Price: $45000.00
#    Value: $67500.00
```

#### `trade_decision(action: str, symbol: str, amount: float, reason: str = "")`
Log trading decision
```python
logger.trade_decision("buy", "BTC", 0.5,
    "Strong uptrend detected + oversold conditions")
# Output:
# 📈 Trade Decision: BUY 0.5 BTC
#    Reason: Strong uptrend detected + oversold conditions
```

#### `performance(portfolio_value: float, cash: float, p_and_l: float)`
Log portfolio metrics
```python
logger.performance(
    portfolio_value=12500,
    cash=5000,
    p_and_l=2500
)
# Output:
# 💰 Portfolio Status:
#    Total Value: $12500.00
#    Cash: $5000.00
#    P&L: $+2500.00 (green if positive)
```

---

### Status Methods

#### `success(message: str)`
Log successful action
```python
logger.success("Trade executed successfully")
# Output in green:
# ✅ Trade executed successfully
```

#### `error(error_msg: str, error_type: str = "Error")`
Log error with emphasis
```python
logger.error("Insufficient funds for trade", "InsufficientFundsError")
# Output in red:
# ❌ InsufficientFundsError: Insufficient funds for trade
```

#### `warning(warning_msg: str)`
Log warning
```python
logger.warning("API response slower than expected")
# Output in yellow:
# ⚠️  WARNING: API response slower than expected
```

#### `info(message: str)`
Log informational message
```python
logger.info("Waiting for next market update")
# Output in cyan:
# ℹ️  Waiting for next market update
```

---

### Complex Operations

#### `execution_summary(date: str, status: str, trades_made: int, p_and_l: float)`
Log session summary
```python
logger.execution_summary(
    date="2025-11-03",
    status="success",
    trades_made=5,
    p_and_l=1250.50
)
# Output:
# ======================================================================
# EXECUTION SUMMARY - 2025-11-03
# ======================================================================
# Status: success
# Trades Made: 5
# P&L: $+1250.50
# ======================================================================
```

#### `log_detailed_step(step_num, total_steps, agent_message, tool_calls, tool_results)`
Log complete step with all details
```python
from tools.enhanced_logging import log_detailed_step

log_detailed_step(
    step_num=1,
    total_steps=30,
    agent_message="Analyzing market conditions...",
    tool_calls=[
        {"name": "get_price_local", "args": {"symbol": "BTC", "date": "2025-11-03"}}
    ],
    tool_results=[
        {"name": "get_price_local", "result": {...}, "success": True}
    ]
)
```

---

## Integration with BaseAgent

To integrate enhanced logging into the BaseAgent, add this to the trading session:

```python
from tools.enhanced_logging import get_logger, log_detailed_step

class BaseAgent:
    async def run_trading_session(self, today_date: str):
        logger = get_logger()

        # Log session header
        logger.header(f"Trading Session: {today_date}")
        logger.info(f"Trading {len(self.stock_symbols)} assets")

        current_step = 0
        for message_content in messages:
            current_step += 1
            logger.step(current_step, self.max_steps)

            # Log agent thinking
            logger.thinking(message_content)

            # Log tool calls
            if tool_calls:
                for tool_call in tool_calls:
                    logger.tool_call(
                        tool_call["name"],
                        tool_call.get("args", {})
                    )

            # Log tool results
            if tool_results:
                for result in tool_results:
                    logger.tool_result(
                        result["tool_name"],
                        result["content"],
                        success=True
                    )

            # Check stop signal
            if STOP_SIGNAL in agent_response:
                logger.success("Stop signal detected, ending session")
                break
```

---

## Color Reference

### Colors Used

| Color | Usage | Hex |
|-------|-------|-----|
| **Cyan** | Headers, info | #00FFFF |
| **Blue** | Tool calls | #0000FF |
| **Green** | Success, buy actions | #00FF00 |
| **Red** | Errors | #FF0000 |
| **Yellow** | Warnings | #FFFF00 |
| **Magenta** | AI thinking | #FF00FF |

### Terminal Output Examples

```
[CYAN]   📊 Market Data
[BLUE]   🔧 Tool Calls
[GREEN]  ✅ Success / 📈 Buy
[RED]    ❌ Errors
[YELLOW] ⚠️  Warnings
[MAGENTA] 💭 AI Thinking
```

---

## Output Examples

### Full Session Log

```
======================================================================
                    Trading Session: 2025-11-03
======================================================================

ℹ️  Trading 2 assets

🔄 Step 1/30: Initializing analysis

💭 AI Thinking:
   Current market analysis:
   - BTC: Strong uptrend, volume increasing
   - ETH: Consolidating, awaiting breakout

   Current positions:
   - BTC: 0.5 (value: $22,500)
   - ETH: 2.0 (value: $4,800)
   - Cash: $2,700

🔧 Calling tool: get_price_local
   {
     "symbol": "BTC",
     "date": "2025-11-03"
   }

─────────────────────────────────────────────────────────────────────

✅ Tool result from get_price_local:
   {
     "price": 45000.50,
     "high": 46000,
     "low": 44500,
     "volume": 2300000000
   }

📊 Market Data for BTC:
   price: 45000.50
   change: +5.2%
   volume: 2.3B

📈 Trade Decision: BUY 0.1 BTC
   Reason: Volume confirmation + uptrend strength

💰 Portfolio Status:
   Total Value: $30000.00
   Cash: $2700.00
   P&L: $+500.00

... (more steps)

======================================================================
EXECUTION SUMMARY - 2025-11-03
======================================================================
Status: success
Trades Made: 3
P&L: $+1250.50
======================================================================
```

---

## Environment Variable Fixes

The following environment variables are now properly set in the workflow:

```yaml
# In .github/workflows/hourly-trading.yml
-e RUNTIME_ENV_PATH="/app/.runtime_env.json"
```

This fixes:
- ✅ "RUNTIME_ENV_PATH not set" warnings
- ✅ Config values properly persisted
- ✅ SIGNATURE available to all tools
- ✅ Better error context for debugging

---

## Best Practices

### 1. Use Appropriate Log Levels
```python
# Use thinking() for AI reasoning
logger.thinking("Market conditions...")

# Use tool_call() for API calls
logger.tool_call("buy", {...})

# Use success()/error() for outcomes
logger.success("Trade executed")
logger.error("Insufficient funds")
```

### 2. Include Context
```python
# Good - includes reasoning
logger.trade_decision("buy", "BTC", 0.5,
    "MA50 > MA200 + RSI oversold")

# Less helpful
logger.trade_decision("buy", "BTC", 0.5)
```

### 3. Log Consistently
```python
# Log at predictable points
logger.step(step_num, total_steps)
logger.thinking(...)
logger.tool_call(...)
logger.tool_result(...)
```

---

## Troubleshooting

### Issue: Colors not showing
**Cause:** Terminal doesn't support ANSI colors
**Solution:** Add `PYTHONUNBUFFERED=1` to environment (already done in workflow)

### Issue: Output truncated
**Cause:** Large results being logged
**Solution:** Tool results are limited to 20 lines, which is by design

### Issue: Performance impact
**Cause:** Logging is synchronous
**Solution:** Logging overhead is minimal (~2-5ms per log statement)

---

## Next Steps

1. **Integration**: Add enhanced logging to BaseAgent
2. **Monitoring**: Check logs for insights into agent behavior
3. **Optimization**: Use logs to identify slow areas
4. **Analysis**: Track patterns in trading decisions

---

*Last Updated: November 3, 2025*
*Status: Ready for integration*
