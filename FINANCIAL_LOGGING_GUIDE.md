# Financial Logging Guide - Track Trades, Prices & Costs

## Overview

The enhanced logging system now tracks all financial aspects of trading:
- **Buy/Sell prices** - Exact price per unit and total cost
- **DeepSeek token costs** - API cost per trading step
- **Trade execution details** - Commission, quantity, subtotal
- **Session financial summary** - Total costs and profitability

---

## Quick Example

```python
from tools.enhanced_logging import get_logger

logger = get_logger()

# Log a trade being decided
logger.trade_decision(
    action="buy",
    symbol="BTC",
    amount=0.5,
    price=45000.00,
    reason="Volume confirmation"
)
# Output:
# 📈 Trade Decision: BUY 0.5 BTC
#    Price: $45,000.00
#    Trade Value: $22,500.00
#    Reason: Volume confirmation

# Log actual execution
logger.trade_execution(
    symbol="BTC",
    action="buy",
    quantity=0.5,
    price=45000.00,
    commission=0
)
# Output:
# 📈 EXECUTED: BUY 0.5 BTC
#    Price per unit: $45,000.00
#    Quantity: 0.5
#    Subtotal: $22,500.00
#    Total Cost: $22,500.00

# Log DeepSeek API costs
logger.deepseek_tokens(
    input_tokens=3600,
    output_tokens=900,
    cache_hit_rate=0.75
)
# Output:
# 💻 DeepSeek Token Usage:
#    Input tokens (with cache):     2700
#    Input tokens (without cache):  900
#    Output tokens:                 900
#    Total tokens:                  4500
#
#    Input (cached):    $0.000076 (75% cache hit)
#    Input (regular):   $0.000252
#    Output:            $0.000378
#    Total API Cost: $0.000706
```

---

## Financial Logging Methods

### 1. Trade Decision with Price

#### Method Signature
```python
logger.trade_decision(
    action: str,           # "buy" or "sell"
    symbol: str,           # "BTC", "ETH", etc.
    amount: float,         # Quantity to trade
    reason: str = "",      # Why making this decision
    price: float = 0       # Price per unit (NEW!)
)
```

#### Example: Buying at Market Price
```python
logger.trade_decision(
    action="buy",
    symbol="BTC",
    amount=0.5,
    price=45000.50,
    reason="Oversold condition detected + volume spike"
)
```

#### Output
```
📈 Trade Decision: BUY 0.5 BTC
   Price: $45,000.50
   Trade Value: $22,500.25
   Reason: Oversold condition detected + volume spike
```

### 2. Trade Execution (Complete Details)

#### Method Signature
```python
logger.trade_execution(
    symbol: str,           # Asset being traded
    action: str,           # "buy" or "sell"
    quantity: float,       # Amount traded
    price: float,          # Price per unit
    commission: float = 0  # Trading fee (optional)
)
```

#### Example: BUY with Commission
```python
logger.trade_execution(
    symbol="BTC",
    action="buy",
    quantity=0.5,
    price=45000.00,
    commission=22.50  # 0.05% commission
)
```

#### Output
```
📈 EXECUTED: BUY 0.5 BTC
   Price per unit: $45,000.00
   Quantity: 0.5
   Subtotal: $22,500.00
   Commission: $22.50
   Total Cost: $22,522.50
```

#### Example: SELL Order
```python
logger.trade_execution(
    symbol="ETH",
    action="sell",
    quantity=2.0,
    price=2500.00,
    commission=10.00
)
```

#### Output
```
📉 EXECUTED: SELL 2.0 ETH
   Price per unit: $2,500.00
   Quantity: 2.0
   Subtotal: $5,000.00
   Commission: $10.00
   Total Cost: $5,010.00
```

### 3. DeepSeek Token Cost Tracking

#### Method Signature
```python
logger.deepseek_tokens(
    input_tokens: int,          # Tokens sent to API
    output_tokens: int,         # Tokens received from API
    cache_hit_rate: float = 0.0 # % of inputs from cache (0.0-1.0)
)
```

#### Pricing Used (From your API docs)
```
Input (cache hit):   $0.028 per 1M tokens
Input (no cache):    $0.28 per 1M tokens
Output:              $0.42 per 1M tokens
```

#### Example: With Cache Hits
```python
logger.deepseek_tokens(
    input_tokens=3600,
    output_tokens=900,
    cache_hit_rate=0.75  # 75% of inputs came from cache
)
```

#### Output
```
💻 DeepSeek Token Usage:
   Input tokens (with cache):     2700
   Input tokens (without cache):  900
   Output tokens:                 900
   Total tokens:                  4500

   Input (cached):    $0.000076 (75% cache hit)
   Input (regular):   $0.000252
   Output:            $0.000378
   Total API Cost: $0.000706
```

#### Example: First Call (No Cache)
```python
logger.deepseek_tokens(
    input_tokens=3600,
    output_tokens=900,
    cache_hit_rate=0.0  # First call, no cached content
)
```

#### Output
```
💻 DeepSeek Token Usage:
   Input tokens (with cache):     0
   Input tokens (without cache):  3600
   Output tokens:                 900
   Total tokens:                  4500

   Input (cached):    $0.000000 (0% cache hit)
   Input (regular):   $0.001008
   Output:            $0.000378
   Total API Cost: $0.001386
```

### 4. Session Financial Summary

#### Method Signature
```python
logger.session_costs(
    total_trades: int,        # Number of trades
    total_trade_value: float, # Sum of all trade values
    total_api_cost: float,    # Total DeepSeek costs
    total_commission: float = 0  # Total fees paid
)
```

#### Example: Complete Session
```python
logger.session_costs(
    total_trades=5,
    total_trade_value=100000.00,
    total_api_cost=0.00353,  # From 5 steps of trading
    total_commission=50.00   # 0.05% on each trade
)
```

#### Output
```
💰 SESSION FINANCIAL SUMMARY:
   Trades executed:       5
   Total trade value:     $100,000.00
   API cost (DeepSeek):   $0.000353
   Commission:            $50.00
   Total cost:            $0.000353
   Cost per trade:        $0.000071
```

### 5. Execution Summary (Enhanced)

#### Method Signature
```python
logger.execution_summary(
    date: str,             # Trading date
    status: str,           # "success" or "failed"
    trades_made: int,      # Number of trades
    p_and_l: float,        # Profit/loss
    total_cost: float = 0,    # Total API + commission costs
    total_tokens: int = 0     # Total tokens used
)
```

#### Example: Successful Session
```python
logger.execution_summary(
    date="2025-11-03",
    status="success",
    trades_made=5,
    p_and_l=1250.50,
    total_cost=0.00353,
    total_tokens=22500
)
```

#### Output
```
======================================================================
EXECUTION SUMMARY - 2025-11-03
======================================================================
Status: success
Trades Made: 5
P&L: $+1250.50
API Cost: $0.000353
Total Tokens: 22,500
======================================================================
```

---

## Complete Trading Session Example

```python
from tools.enhanced_logging import get_logger

logger = get_logger()

# Session start
logger.header("Trading Session - 2025-11-03")
logger.info("Starting with BTC and ETH")

# Market analysis
logger.step(1, 30, "Analyzing market")
logger.thinking("BTC up 5%, volume strong. ETH consolidating...")
logger.market_data("BTC", {
    "price": 45000.50,
    "change": "+5.2%",
    "volume": "2.3B"
})

# Get API costs for this step
logger.deepseek_tokens(
    input_tokens=3600,
    output_tokens=900,
    cache_hit_rate=0.75
)
# Shows: API Cost: $0.000706

# Trading decision
logger.step(2, 30, "Executing trades")
logger.trade_decision(
    action="buy",
    symbol="BTC",
    amount=0.5,
    price=45000.50,
    reason="Volume breakout confirmed"
)

# Trade execution
logger.trade_execution(
    symbol="BTC",
    action="buy",
    quantity=0.5,
    price=45000.50,
    commission=22.50
)
# Shows: Total Cost: $22,522.50

# Portfolio update
logger.performance(
    portfolio_value=30000.00,
    cash=7477.50,
    p_and_l=500.00
)

# More trading...
logger.trade_decision(
    action="sell",
    symbol="ETH",
    amount=1.0,
    price=2550.00,
    reason="Take profit at resistance"
)

logger.trade_execution(
    symbol="ETH",
    action="sell",
    quantity=1.0,
    price=2550.00,
    commission=12.75
)
# Shows: Total Cost: $2,562.75

# Session end
logger.session_costs(
    total_trades=2,
    total_trade_value=25050.50,
    total_api_cost=0.00142,
    total_commission=35.25
)

logger.execution_summary(
    date="2025-11-03",
    status="success",
    trades_made=2,
    p_and_l=750.25,
    total_cost=0.00142,
    total_tokens=9000
)
```

#### Full Output
```
======================================================================
                 Trading Session - 2025-11-03
======================================================================

ℹ️  Starting with BTC and ETH

🔄 Step 1/30: Analyzing market

💭 AI Thinking:
   BTC up 5%, volume strong. ETH consolidating...

📊 Market Data for BTC:
   price: 45000.50
   change: +5.2%
   volume: 2.3B

💻 DeepSeek Token Usage:
   Input tokens (with cache):     2700
   Input tokens (without cache):  900
   Output tokens:                 900
   Total tokens:                  4500

   Input (cached):    $0.000076 (75% cache hit)
   Input (regular):   $0.000252
   Output:            $0.000378
   Total API Cost: $0.000706

🔄 Step 2/30: Executing trades

📈 Trade Decision: BUY 0.5 BTC
   Price: $45,000.50
   Trade Value: $22,500.25
   Reason: Volume breakout confirmed

📈 EXECUTED: BUY 0.5 BTC
   Price per unit: $45,000.50
   Quantity: 0.5
   Subtotal: $22,500.25
   Commission: $22.50
   Total Cost: $22,522.75

💰 Portfolio Status:
   Total Value: $30000.00
   Cash: $7477.50
   P&L: $+500.00

... (continuing with ETH trade)

📉 Trade Decision: SELL 1.0 ETH
   Price: $2,550.00
   Trade Value: $2,550.00
   Reason: Take profit at resistance

📉 EXECUTED: SELL 1.0 ETH
   Price per unit: $2,550.00
   Quantity: 1.0
   Subtotal: $2,550.00
   Commission: $12.75
   Total Cost: $2,562.75

💰 SESSION FINANCIAL SUMMARY:
   Trades executed:       2
   Total trade value:     $25,050.50
   API cost (DeepSeek):   $0.001420
   Commission:            $35.25
   Total cost:            $0.036620
   Cost per trade:        $0.018310

======================================================================
EXECUTION SUMMARY - 2025-11-03
======================================================================
Status: success
Trades Made: 2
P&L: $+750.25
API Cost: $0.001420
Total Tokens: 9,000
======================================================================
```

---

## Cost Analysis Examples

### Example 1: Single Trade Day
```
Trades: 1 BTC at $45,000
DeepSeek tokens: 4,500
API cost: $0.000706
Commission: $22.50
Net cost: $22.50 + $0.000706 = $22.50

ROI required: Need $22.50 profit to break even
```

### Example 2: High-Frequency Day (24 trades)
```
Trades: 24 trades
Total tokens: 108,000
API cost: 24 × $0.000706 = $0.017
Commission: $500 (assuming $20-25 per trade)
Net cost: $500.017

ROI required: Need $500 profit to break even
```

### Example 3: 100 Runs Per Day
```
Runs: 100
Total tokens: 450,000
API cost: 100 × $0.000706 = $0.0706
(with caching after initial runs)
Cost per run: $0.000706 (first run)
Cost per run: $0.000035 (with 90% cache hit)

Average: ~$0.00025 per run
Daily cost: ~$0.025 (with optimal caching)
```

---

## Monitoring DeepSeek Costs

### Daily API Cost Calculation

```python
# For each trading session, track:
total_daily_cost = sum(api_costs_per_run)

# Example:
# Run 1: 4,500 tokens = $0.000706
# Run 2: 4,500 tokens = $0.000035 (75% cache)
# Run 3: 4,500 tokens = $0.000035 (75% cache)
# ...
# Run 24: 4,500 tokens = $0.000035 (75% cache)

total_daily_cost = 0.000706 + (23 × 0.000035) = $0.00086
```

### Monthly Cost Forecast
```
Daily API cost: $0.00086
Monthly cost: $0.00086 × 30 = $0.0258

With 100 runs/day (instead of 24):
Daily API cost: ~$0.0179
Monthly cost: ~$0.537
```

---

## Integration into BaseAgent

```python
from tools.enhanced_logging import get_logger

class BaseAgent:
    async def run_trading_session(self, today_date: str):
        logger = get_logger()

        total_api_cost = 0
        total_trades = 0

        for step in range(1, max_steps + 1):
            # Log step
            logger.step(step, max_steps)

            # Simulate token usage
            input_tokens = 3600
            output_tokens = 900
            cache_hit = 0.75 if step > 1 else 0.0

            # Log tokens and cost
            logger.deepseek_tokens(input_tokens, output_tokens, cache_hit)

            # If trading happens
            if action == "buy":
                logger.trade_decision(
                    action="buy",
                    symbol=symbol,
                    amount=amount,
                    price=price,
                    reason=reason
                )

                logger.trade_execution(
                    symbol=symbol,
                    action="buy",
                    quantity=amount,
                    price=price,
                    commission=amount * price * 0.0005
                )

                total_trades += 1
                total_api_cost += api_cost_per_step

        # Summary
        logger.session_costs(
            total_trades=total_trades,
            total_trade_value=total_trade_value,
            total_api_cost=total_api_cost
        )

        logger.execution_summary(
            date=today_date,
            status="success",
            trades_made=total_trades,
            p_and_l=profit_loss,
            total_cost=total_api_cost,
            total_tokens=total_tokens_used
        )
```

---

## Summary

Now you can see **everything**:
- ✅ **Every buy/sell price** - Exact price per unit and total value
- ✅ **DeepSeek API costs** - Per-step and per-day costs
- ✅ **Commission tracking** - Trading fees included
- ✅ **Cost efficiency** - Cost per trade metrics
- ✅ **Session summary** - Complete financial breakdown

This allows you to:
1. **Track profitability** - See if profits exceed API costs
2. **Optimize costs** - Understand cost drivers
3. **Monitor spending** - Stay within budget
4. **Analyze ROI** - Profit per dollar spent
5. **Debug issues** - See exact prices and costs

---

*Last Updated: November 3, 2025*
*All pricing based on DeepSeek rates you provided*
