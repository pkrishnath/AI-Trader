# GitHub Actions Workflows for AI-Trader

This document explains the automated workflows configured for the AI-Trader project.

## Workflows Overview

### 1. **Hourly Trading Run** (`hourly-trading.yml`)

Automatically runs the AI trading simulation every hour.

#### Schedule
- **Trigger**: Every hour at minute 0 (00:00, 01:00, 02:00, etc. UTC)
- **Can be triggered manually** via GitHub Actions UI using "Workflow dispatch"
- **Also runs** when pushing to main branch with changes to trading-related files

#### What it does:
1. Checks out the latest code
2. Sets up Python 3.11 environment
3. Installs project dependencies from `requirements.txt`
4. Configures environment variables from GitHub secrets
5. Fetches and prepares stock price data
6. Starts MCP (Model Context Protocol) services
7. Runs the trading simulation (`python main.py`)
8. Uploads results as artifacts
9. Generates a trading report
10. Sends optional Slack notification

#### Required Secrets
You need to add these secrets in GitHub:
- `OPENAI_API_KEY` - Your OpenAI/LLM API key
- `ALPHAADVANTAGE_API_KEY` - Alpha Vantage API key for stock data
- `JINA_API_KEY` - Jina API key for market research
- `SLACK_WEBHOOK` (optional) - Slack webhook URL for notifications

#### How to add secrets:
1. Go to: **GitHub repo → Settings → Secrets and variables → Actions**
2. Click "New repository secret"
3. Add each secret with its corresponding value

#### Outputs
- **Artifacts**: Trading results and merged data (retained for 30 days)
- **Logs**: Check the "Actions" tab to view full execution logs
- **Slack notification** (if configured): Alerts on success or failure

#### Manual Trigger
To run immediately without waiting for the schedule:
1. Go to **Actions** tab in your GitHub repo
2. Click **"Hourly AI Trading Run"**
3. Click **"Run workflow"** → **"Run workflow"**

---

### 2. **Tests & Validation** (`tests.yml`)

Runs on every push/PR to main branch. Validates code quality, runs tests, and checks security.

#### Triggers
- Push to `main` or `develop` branch
- Pull requests targeting `main` or `develop`

#### What it does:

**A. Linting & Code Quality**
- Checks code style with `flake8`
- Validates formatting with `black`
- Checks import ordering with `isort`

**B. Unit Tests**
- Runs pytest on all tests in `tests/` directory
- Generates coverage reports
- Uploads to Codecov for tracking

**C. Configuration Validation**
- Validates all JSON config files
- Checks environment variable templates

**D. Security Scanning**
- Runs Bandit for security issues
- Checks for hardcoded secrets
- Audits dependencies for vulnerabilities

**E. Dependency Audit**
- Checks for outdated packages
- Audits for known vulnerabilities

#### View Test Results
1. Go to **Actions** tab
2. Click the workflow run
3. Check each job for details

---

## GitHub Actions Setup Instructions

### Step 1: Add Required Secrets

1. Go to your GitHub repo
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:

```
OPENAI_API_KEY = [your-key]
ALPHAADVANTAGE_API_KEY = [your-key]
JINA_API_KEY = [your-key]
SLACK_WEBHOOK = [optional: your-slack-webhook-url]
```

### Step 2: Verify Workflows Are Enabled

1. Go to **Actions** tab
2. You should see two workflows:
   - "Hourly AI Trading Run"
   - "Tests & Validation"
3. If they're disabled, click "Enable workflow"

### Step 3: Check Workflow Status

1. Click on any workflow
2. View recent runs
3. Click a run to see detailed logs

### Step 4: (Optional) Configure Slack Notifications

If you want Slack alerts:

1. Create a Slack webhook:
   - Go to your Slack workspace
   - Create an incoming webhook
   - Copy the webhook URL

2. Add to GitHub secrets as `SLACK_WEBHOOK`

3. Workflow will automatically post notifications

---

## Local Development with Workflows

To test workflows locally before pushing:

### Option A: Using Act (Recommended)

Install `act` to run GitHub Actions locally:

```bash
# Install act (macOS)
brew install act

# Run specific workflow
act -j trading-run  # Run the trading workflow
act -j lint         # Run linting only
act -j test-units   # Run unit tests

# Run all workflows
act
```

### Option B: Manual Testing

Run commands locally:

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 isort

# Run linting
flake8 . --max-line-length=127
black --check .
isort --check-only .

# Run tests
pytest tests/ -v --cov

# Prepare data and run trading
cd data && python get_daily_price.py && python merge_jsonl.py && cd ..
cd agent_tools && python start_mcp_services.py & cd ..
python main.py
```

---

## Monitoring & Debugging

### View Workflow Logs
1. Go to **Actions** tab
2. Click the workflow
3. Click the specific run
4. Click the job name to see logs

### Common Issues

**Issue: Workflow times out**
- Solution: Check if MCP services are starting properly
- Increase timeout in the workflow file if needed

**Issue: API keys not working**
- Solution: Verify secrets are added correctly
- Check that keys have required permissions
- Make sure secrets names match exactly in workflow

**Issue: Tests failing**
- Solution: Run tests locally first
- Check Python version compatibility
- Ensure all dependencies installed

**Issue: Price data fetch failing**
- Solution: Check Alpha Vantage API limits
- Verify API key permissions
- Check internet connectivity

---

## Scheduling

### Current Schedule
- **Hourly Trading**: Every hour at :00 minutes
- **Tests**: On every push/PR to main/develop

### Change Schedule

To change the hourly trading schedule, edit `.github/workflows/hourly-trading.yml`:

```yaml
on:
  schedule:
    - cron: '0 * * * *'  # Current: every hour
    # Change to:
    # - cron: '0 9 * * *'    # Daily at 9 AM UTC
    # - cron: '0 */6 * * *'  # Every 6 hours
    # - cron: '0 0 * * 0'    # Weekly on Sunday at midnight
```

### Cron Syntax
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

---

## Cost Considerations

**GitHub Actions Free Tier:**
- Public repos: Unlimited
- Private repos: 2,000 minutes/month free

**Hourly trading workflow:**
- Estimated: ~10-15 minutes per run
- Monthly: ~7,200-10,800 minutes
- Status: **Will exceed free tier if private**

**Recommendations:**
1. If repo is private, consider changing schedule:
   - Run every 6 hours instead of hourly
   - Change: `cron: '0 */6 * * *'`

2. Or use GitHub Pro for more minutes

3. Monitor usage:
   - Go to: Settings → Billing and plan
   - View "Actions" section

---

## Best Practices

1. **Keep secrets secure**
   - Never commit `.env` files
   - Rotate API keys regularly
   - Use minimal permission scopes

2. **Monitor costs**
   - Check Actions billing monthly
   - Adjust schedule if needed

3. **Review logs regularly**
   - Check for errors in workflow runs
   - Monitor trading results
   - Watch for API failures

4. **Test before production**
   - Test workflows locally with `act`
   - Review in PR before merging
   - Monitor first few runs closely

5. **Maintain dependencies**
   - Keep requirements.txt updated
   - Audit for security issues
   - Update Python version periodically

---

## Troubleshooting Checklist

- [ ] All secrets added to GitHub
- [ ] Secrets names match workflow exactly
- [ ] API keys are valid and have correct permissions
- [ ] Workflow file syntax is correct (check for indentation)
- [ ] Python version compatible (3.11+)
- [ ] All required files exist (`main.py`, configs, data/)
- [ ] MCP services can start successfully
- [ ] Tests pass locally
- [ ] No hardcoded secrets in code

---

## Support

For issues:
1. Check workflow logs for error details
2. Run commands locally to reproduce
3. Review this README
4. Check GitHub Actions documentation: https://docs.github.com/actions
