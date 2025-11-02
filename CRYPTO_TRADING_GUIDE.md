# Cryptocurrency Trading Guide for AI-Trader

Your AI-Trader now supports **native Bitcoin (BTC) and Ethereum (ETH) trading**!

## What's New

✅ **Crypto Price Data**: Uses CoinGecko API (free, no authentication required)
✅ **BTC & ETH Support**: Trade Bitcoin and Ethereum directly
✅ **Fractional Trading**: Buy/sell in decimal amounts (e.g., 0.5 BTC, 2.3 ETH)
✅ **Real-time Prices**: Fetches latest market data hourly
✅ **Full Integration**: Works with existing GitHub Actions automation

## Quick Start - Run Crypto Trading

### Step 1: Fetch Crypto Price Data

```bash
# Download 60 days of BTC and ETH price history
python data/get_crypto_prices.py
```

This will create:
- `data/crypto_prices_BTC.json` - Bitcoin price history
- `data/crypto_prices_ETH.json` - Ethereum price history

### Step 2: Run Crypto Trading with Custom Config

```bash
# Use crypto config instead of default stock config
python main.py configs/crypto_config.json
```

The AI will now trade only BTC and ETH!

### Step 3: View Results

Trading results will be saved to:
- `data/agent_data/` - Trading logs and decisions
- `data/merged.jsonl` - Combined trading records

## Configuration

### Crypto Config File: `configs/crypto_config.json`

```json
{
  "agent_type": "BaseAgent",
  "crypto_mode": true,
  "trading_universe": ["BTC", "ETH"],
  "agent_config": {
    "initial_cash": 10000.0,
    "crypto_trading": true
  }
}
```

Key settings:
- `crypto_mode`: Enable crypto trading
- `trading_universe`: ["BTC", "ETH"] for cryptocurrencies only
- `initial_cash`: Starting capital (default $10,000)

## How to Use Crypto Trading

### Fetch Fresh Price Data

```bash
# Get latest 60 days of data for BTC and ETH
python data/get_crypto_prices.py

# Or fetch different time periods
python -c "
from data.get_crypto_prices import fetch_all_crypto_data
fetch_all_crypto_data(symbols=['BTC', 'ETH'], days=90)
"
```

### Run Trading Simulation

```bash
# Run with crypto config
python main.py configs/crypto_config.json

# Run with different dates
INIT_DATE=2025-09-01 END_DATE=2025-10-31 python main.py configs/crypto_config.json
```

### Check Crypto Price Data

```bash
# View available crypto data
python -c "
from tools.crypto_tools import get_crypto_price_summary
print(get_crypto_price_summary())
"
```

## Crypto Trading Tools

The following tools are available in `tools/crypto_tools.py`:

### Get Price on Specific Date
```python
from tools.crypto_tools import get_crypto_price_on_date

price = get_crypto_price_on_date("BTC", "2025-10-15", price_type="close")
print(f"BTC price on Oct 15: ${price:,.2f}")
```

### Get Price Range
```python
from tools.crypto_tools import get_crypto_prices_range

prices = get_crypto_prices_range("ETH", "2025-10-01", "2025-10-21")
for date, data in prices.items():
    print(f"{date}: ${data['close']:,.2f}")
```

### Calculate Returns
```python
from tools.crypto_tools import calculate_crypto_returns

returns = calculate_crypto_returns(
    crypto_symbol="BTC",
    purchase_date="2025-10-01",
    purchase_price=40000,
    sale_date="2025-10-21"
)
print(f"Return: {returns['return_percentage']:.2f}%")
```

## Switching Between Stock and Crypto Trading

### Use Stock Config (Default)
```bash
python main.py configs/default_config.json
# Trades NASDAQ 100 stocks
```

### Use Crypto Config (BTC & ETH Only)
```bash
python main.py configs/crypto_config.json
# Trades Bitcoin and Ethereum only
```

### Create Hybrid Config (Optional)
To trade both stocks and cryptos, edit the config to include both:

```json
{
  "trading_universe": ["AAPL", "MSFT", "BTC", "ETH"]
}
```

Then create corresponding data for mixed trading.

## Automate Crypto Trading with GitHub Actions

### Option 1: Add Crypto Workflow

Create `.github/workflows/crypto-trading.yml`:

```yaml
name: Crypto Trading Run

on:
  schedule:
    - cron: '0 * * * *'  # Every hour

jobs:
  crypto-trading:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Fetch crypto prices
        run: python data/get_crypto_prices.py

      - name: Run crypto trading
        run: python main.py configs/crypto_config.json
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ALPHAADVANTAGE_API_KEY: ${{ secrets.ALPHAADVANTAGE_API_KEY }}
          JINA_API_KEY: ${{ secrets.JINA_API_KEY }}
```

### Option 2: Modify Existing Hourly Workflow

Edit `.github/workflows/hourly-trading.yml` to use crypto config:

```yaml
- name: Run trading simulation
  run: |
    python main.py configs/crypto_config.json
```

## Data Files

### Crypto Price Data Files

After running `python data/get_crypto_prices.py`:

```
data/
├── crypto_prices_BTC.json     # Bitcoin historical prices
├── crypto_prices_ETH.json     # Ethereum historical prices
├── crypto_prices_merged.json  # Combined data (optional)
└── agent_data/
    └── crypto_*.jsonl          # Trading records
```

### File Format

Each crypto price file contains:

```json
{
  "2025-10-01": {
    "date": "2025-10-01",
    "open": 43250.50,
    "high": 43500.00,
    "low": 42800.00,
    "close": 43400.00,
    "volume": 0
  }
}
```

## FAQ

### Q: Can I trade more cryptocurrencies?

A: Yes! Edit `tools/crypto_tools.py` and `data/get_crypto_prices.py`:

```python
CRYPTO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",      # Add more
    "DOGE": "dogecoin"
}
```

Then update `SUPPORTED_CRYPTOS` and `CRYPTO_SYMBOLS`.

### Q: How often are prices updated?

A: After each trading run, fresh prices are fetched from CoinGecko (free API).
- For GitHub Actions: Every hour (configurable)
- For local runs: Each time you execute

### Q: What's the minimum trade size?

A: Cryptocurrencies support fractional amounts:
- BTC: Can trade 0.00000001 BTC minimum
- ETH: Can trade 0.000001 ETH minimum
- Agent decides optimal amounts based on strategy

### Q: Does CoinGecko API have rate limits?

A: Free CoinGecko API:
- Limit: 50 calls/minute
- Your hourly jobs: ~2-3 calls/hour = well under limit
- No authentication required
- No API key needed

### Q: Can I use a different price API?

A: Yes! CoinGecko is recommended but you can:
1. Use Binance API (free, high volume)
2. Use Kraken API (professional data)
3. Use Yahoo Finance (some cryptos)
4. Use custom sources

Edit `data/get_crypto_prices.py` to integrate your preferred API.

### Q: How do I backtest crypto strategies?

```bash
# Test with historical data
INIT_DATE=2025-01-01 END_DATE=2025-10-21 python main.py configs/crypto_config.json
```

## Performance Monitoring

### View Crypto Trading Results

```bash
# Check latest trading data
tail -n 20 data/agent_data/crypto_*.jsonl

# View merged results
cat data/merged.jsonl | grep -i "btc\|eth"
```

### Check Dashboard Updates

After GitHub Pages is enabled, your dashboard automatically shows:
- BTC and ETH price charts
- Trading performance
- Portfolio allocation
- Return analysis

Visit: `https://pkrishnath.github.io/AI-Trader/`

## Troubleshooting

### No price data for cryptos

**Problem**: "No data available for BTC/ETH"

**Solution**:
```bash
python data/get_crypto_prices.py
```

### CoinGecko API rate limit

**Problem**: Requests failing with 429 error

**Solution**:
- Add delay between requests
- Use retry logic (built-in)
- Switch to paid CoinGecko API

### Crypto prices not updating

**Problem**: Dashboard shows old prices

**Solution**:
1. Verify `get_crypto_prices.py` ran successfully
2. Check `data/crypto_prices_*.json` files exist
3. Hard refresh dashboard (Cmd+Shift+R)

## Next Steps

1. ✅ Run `python data/get_crypto_prices.py` to fetch data
2. ✅ Test locally: `python main.py configs/crypto_config.json`
3. ✅ Monitor trading results in `data/agent_data/`
4. ✅ Deploy via GitHub Actions (same hourly automation)
5. ✅ Watch live dashboard updates

## Support

For issues:
- Check `crypto_tools.py` for available functions
- Review `crypto_agent_prompt.py` for prompt structure
- Monitor `data/agent_data/` logs for trading decisions
- Check GitHub Actions logs for automation issues

---

Your AI is now ready to trade cryptocurrencies 24/7! 🚀🪙
