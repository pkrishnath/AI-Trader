# Crypto Trading Quick Start

## TL;DR - Run in 2 Commands

```bash
# 1. Fetch latest BTC and ETH prices
python data/get_crypto_prices.py

# 2. Run AI trading on crypto
python main.py configs/crypto_config.json
```

Done! Check results in `data/agent_data/`

---

## Files You Need to Know

| File | Purpose | Use When |
|------|---------|----------|
| `data/get_crypto_prices.py` | Fetch BTC/ETH prices | Starting a trading run |
| `configs/crypto_config.json` | Crypto trading settings | Running crypto trades |
| `prompts/crypto_agent_prompt.py` | AI instructions | Understanding how AI trades |
| `tools/crypto_tools.py` | Crypto utilities | Integrating with other code |
| `CRYPTO_TRADING_GUIDE.md` | Full documentation | Learning all features |

---

## Common Tasks

### Fetch Prices
```bash
python data/get_crypto_prices.py
```

### Run Trading
```bash
python main.py configs/crypto_config.json
```

### Check Latest Prices
```bash
python -c "
from tools.crypto_tools import get_crypto_price_summary
print(get_crypto_price_summary())
"
```

### Get Price on Specific Date
```bash
python -c "
from tools.crypto_tools import get_crypto_price_on_date
btc = get_crypto_price_on_date('BTC', '2025-10-15')
print(f'BTC on Oct 15: \${btc:,.2f}')
"
```

### View Trading Results
```bash
ls data/agent_data/
tail -n 50 data/agent_data/*.jsonl
```

---

## Configuration

Default crypto config: `configs/crypto_config.json`

Key settings:
- **Cryptos**: BTC, ETH
- **Starting capital**: $10,000
- **Trading enabled**: Yes
- **Log location**: `data/agent_data/`

---

## GitHub Actions Setup (Optional)

To automate hourly crypto trading:

Edit `.github/workflows/hourly-trading.yml`:

```yaml
- name: Run trading simulation
  run: |
    python data/get_crypto_prices.py
    python main.py configs/crypto_config.json
```

That's it! Crypto trading now runs hourly automatically.

---

## Troubleshooting

**Q: No price data?**
```bash
python data/get_crypto_prices.py
```

**Q: Check if data exists?**
```bash
ls -la data/crypto_prices_*.json
```

**Q: View available data?**
```bash
python -c "from tools.crypto_tools import get_crypto_price_summary; print(get_crypto_price_summary())"
```

**Q: Add more cryptos?**

Edit `data/get_crypto_prices.py`:
```python
CRYPTO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",  # Add this
}
```

**Q: Custom dates?**
```bash
INIT_DATE=2025-01-01 END_DATE=2025-10-31 python main.py configs/crypto_config.json
```

---

## API Info

- **Price Source**: CoinGecko (free, no auth needed)
- **Rate Limit**: 50 calls/minute
- **Your Usage**: ~2 calls/hour (well under limit)
- **Cost**: FREE ✓

---

## What's Trading?

Your AI trades:
- **BTC** (Bitcoin) - Digital gold
- **ETH** (Ethereum) - Smart contracts token

Starting with $10,000, maximizing returns.

---

## Next Steps

1. ✅ Run: `python data/get_crypto_prices.py`
2. ✅ Test: `python main.py configs/crypto_config.json`
3. ✅ Monitor: Check `data/agent_data/` for results
4. ✅ Deploy: Add to GitHub Actions for 24/7 trading

---

Need more info? See `CRYPTO_TRADING_GUIDE.md`
