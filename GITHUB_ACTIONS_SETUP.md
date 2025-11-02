# GitHub Actions Setup Guide for AI-Trader

Complete guide to set up automated hourly trading runs with GitHub Actions.

## Quick Start (5 minutes)

### Step 1: Add GitHub Secrets (2 minutes)

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add these 3 secrets:

| Secret Name | Description | Where to Get |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI/LLM API key | https://platform.openai.com/api-keys |
| `ALPHAADVANTAGE_API_KEY` | Stock price data API | https://www.alphavantage.co/api/ |
| `JINA_API_KEY` | Market research API | https://jina.ai/ |

**Example:** Adding OPENAI_API_KEY
```
Secret name: OPENAI_API_KEY
Secret value: sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 2: Verify Workflows Are Enabled (1 minute)

1. Go to **Actions** tab in your GitHub repo
2. You should see 2 workflows:
   - ✅ "Hourly AI Trading Run"
   - ✅ "Tests & Validation"
3. Both should be enabled (green checkmarks)

### Step 3: Trigger First Run (2 minutes)

1. Go to **Actions** tab
2. Click **"Hourly AI Trading Run"**
3. Click **"Run workflow"** button
4. Click **"Run workflow"** to confirm
5. Watch the run in real-time!

## What Happens Next

### Every Hour (Automatic)
- ⏰ AI-Trader runs automatically every hour
- 📊 Trading simulation executes
- 💾 Results saved as artifacts
- 📈 Leaderboard updated

### Every Push (Automatic)
- ✅ Code quality checks run
- 🧪 Unit tests execute
- 🔒 Security scanning runs
- 📋 Configuration validated

## Monitoring Your Workflows

### View Results
1. Go to **Actions** tab
2. See all workflow runs
3. Click any run for details

### Check Artifacts
1. Click completed workflow run
2. Scroll to "Artifacts" section
3. Download trading results and data

### View Logs
1. Click workflow run
2. Click job name (e.g., "trading-run")
3. See real-time execution logs

## Cost & Free Tier

### GitHub Actions Free Tier
- **Public repos**: ∞ (unlimited)
- **Private repos**: 2,000 minutes/month

### Your Usage (Hourly Trading)
- Estimated: **10-15 minutes per run**
- Monthly estimate: **~7,200-10,800 minutes**
- ⚠️ **Will exceed free tier if private repo**

### Solutions for Private Repos
**Option A: Use GitHub Pro** (~$4/month)
- Includes 3,000 minutes/month

**Option B: Run less frequently**
- Change schedule from hourly to every 6 hours:
  ```yaml
  cron: '0 */6 * * *'  # Every 6 hours
  ```
  - Monthly usage: ~1,440-2,160 minutes ✓ (within free tier)

**Option C: Use self-hosted runner**
- Run on your own machine
- No GitHub Actions minutes consumed
- Requires setup

## Advanced Configuration

### Change Hourly Schedule

Edit `.github/workflows/hourly-trading.yml`:

```yaml
on:
  schedule:
    - cron: '0 * * * *'  # Every hour
```

Common schedules:
```yaml
# Every 6 hours
- cron: '0 */6 * * *'

# Every 4 hours
- cron: '0 */4 * * *'

# Daily at 9 AM UTC
- cron: '0 9 * * *'

# Every weekday at 10 AM
- cron: '0 10 * * 1-5'

# Every Monday at 8 AM
- cron: '0 8 * * 1'
```

### Add Slack Notifications

If you want trading updates in Slack:

1. **Create Slack webhook:**
   - Go to your Slack workspace
   - Apps → "Incoming Webhooks"
   - Create new webhook
   - Copy webhook URL

2. **Add as GitHub secret:**
   - Settings → Secrets → New secret
   - Name: `SLACK_WEBHOOK`
   - Value: `https://hooks.slack.com/services/...`

3. **That's it!** Workflow already configured to use it

### Customize Test Suite

Edit `.github/workflows/tests.yml` to add more checks:

```yaml
- name: Run custom validation
  run: |
    python your_custom_test.py
```

## Troubleshooting

### Workflow Not Running on Schedule
**Cause**: Scheduled workflows need at least one commit in the last 60 days
**Fix**: Make a commit to the repository

### API Keys Failing
**Cause**: Wrong secret names or expired keys
**Fix**:
1. Verify secret names match exactly
2. Test keys locally first
3. Check API rate limits
4. Verify key permissions

### Tests Failing
**Cause**: Environment or dependency issue
**Fix**:
1. Run tests locally: `pytest tests/ -v`
2. Check Python version: `python --version` (needs 3.11+)
3. Install dependencies: `pip install -r requirements.txt`
4. Review test logs in GitHub Actions

### Workflow Timeout
**Cause**: Taking too long to run
**Fix**:
1. Check MCP services startup time
2. Increase timeout: change `timeout-minutes: 30` to larger value
3. Optimize data fetching

### Out of Free Tier Minutes
**Cause**: Running too frequently
**Fix**:
1. See "Solutions for Private Repos" above
2. Reduce schedule frequency
3. Or upgrade to GitHub Pro

## Testing Locally Before Pushing

### Option 1: Using `act` (Recommended)

Install:
```bash
brew install act  # macOS
# or: choco install act  (Windows)
# or: Download from https://github.com/nektos/act
```

Run:
```bash
# Test trading workflow
act -j trading-run --secret-files .env

# Test all workflows
act --secret-files .env

# Test with custom event
act push
```

### Option 2: Manual Testing

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio black flake8 isort

# Run tests
pytest tests/ -v

# Run linting
black --check .
flake8 .
isort --check-only .

# Test data preparation
cd data
python get_daily_price.py
python merge_jsonl.py
cd ..

# Test main script locally
python main.py
```

## File Structure Created

```
.github/
└── workflows/
    ├── hourly-trading.yml      # Hourly trading run
    ├── tests.yml               # Code quality & tests
    └── README.md               # Detailed workflow docs

tests/
├── __init__.py
├── test_config.py              # Config validation tests
└── test_tools.py               # Tool tests

pytest.ini                       # Pytest configuration

GITHUB_ACTIONS_SETUP.md          # This file
```

## Next Steps

### Immediate (Today)
- [ ] Add 3 API key secrets to GitHub
- [ ] Verify workflows enabled
- [ ] Trigger first manual run
- [ ] Check results in Actions tab

### Short Term (This Week)
- [ ] Monitor first few hourly runs
- [ ] Check artifacts for trading data
- [ ] Review logs for errors
- [ ] Optimize if needed

### Long Term (Optional)
- [ ] Add Slack notifications
- [ ] Implement custom tests
- [ ] Set up data export
- [ ] Create dashboards
- [ ] Monitor costs monthly

## Getting Help

### Check Workflow Logs
1. Go to Actions tab
2. Click failed workflow
3. Click job name to see error messages
4. Search error message in documentation

### GitHub Actions Documentation
- Main docs: https://docs.github.com/en/actions
- Workflow syntax: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- Scheduled workflows: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#scheduled-events

### API Documentation
- OpenAI: https://platform.openai.com/docs
- Alpha Vantage: https://www.alphavantage.co/documentation/
- Jina: https://jina.ai/documentation/

## Summary

You now have:
- ✅ Automatic hourly trading runs
- ✅ Continuous testing on every push
- ✅ Code quality checks
- ✅ Security scanning
- ✅ Full logging and monitoring
- ✅ Artifact storage for 30 days

**Your AI-Trader is now running on autopilot!** 🚀

Monitor progress in the Actions tab anytime.
