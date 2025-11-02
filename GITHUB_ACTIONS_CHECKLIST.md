# GitHub Actions Setup Checklist ✓

Complete this checklist to activate your automated AI-Trader system.

## Pre-Setup (Knowledge)
- [ ] Read `GITHUB_ACTIONS_SETUP.md` (5 min read)
- [ ] Understand what workflows do (2 min)
- [ ] Know your API key sources (1 min)

## Setup Phase 1: GitHub Secrets (2 minutes)

### Get Your API Keys
- [ ] **OPENAI_API_KEY**
  - [ ] Go to https://platform.openai.com/api-keys
  - [ ] Create new API key
  - [ ] Copy the key (long string starting with `sk-`)

- [ ] **ALPHAADVANTAGE_API_KEY**
  - [ ] Go to https://www.alphavantage.co/api/
  - [ ] Request free API key
  - [ ] Copy the key (uppercase alphanumeric string)

- [ ] **JINA_API_KEY**
  - [ ] Go to https://jina.ai/
  - [ ] Sign up / Login
  - [ ] Find API keys section
  - [ ] Copy the key

### Add Secrets to GitHub
1. [ ] Go to your GitHub repository
2. [ ] Click **Settings**
3. [ ] Click **Secrets and variables**
4. [ ] Click **Actions**
5. [ ] Click **New repository secret**

For each API key:
- [ ] Add OPENAI_API_KEY
  - [ ] Name: `OPENAI_API_KEY`
  - [ ] Value: [Your OpenAI API key]
  - [ ] Click "Add secret"

- [ ] Add ALPHAADVANTAGE_API_KEY
  - [ ] Name: `ALPHAADVANTAGE_API_KEY`
  - [ ] Value: [Your Alpha Vantage API key]
  - [ ] Click "Add secret"

- [ ] Add JINA_API_KEY
  - [ ] Name: `JINA_API_KEY`
  - [ ] Value: [Your Jina API key]
  - [ ] Click "Add secret"

### Verify Secrets Added
- [ ] Go back to Secrets page
- [ ] See all 3 secrets listed (values hidden)
- [ ] Secret names match exactly (case-sensitive!)

## Setup Phase 2: Verify Workflows (30 seconds)

- [ ] Go to GitHub repository
- [ ] Click **Actions** tab
- [ ] See "Hourly AI Trading Run" workflow
- [ ] See "Tests & Validation" workflow
- [ ] Both workflows have green "enabled" status
- [ ] No red "disabled" badges

## Setup Phase 3: Decision - Choose Your Schedule (2 minutes)

### For PUBLIC Repositories
- [ ] You can run hourly (no cost)
- [ ] Schedule: `cron: '0 * * * *'` (already set)
- [ ] No action needed ✓

### For PRIVATE Repositories
Choose ONE option:

**Option A: Save Money - Run Every 6 Hours**
- [ ] Stay within free 2,000 minute/month quota
- [ ] Estimated cost: $0/month
- [ ] To activate:
  1. [ ] Edit `.github/workflows/hourly-trading.yml`
  2. [ ] Find line: `cron: '0 * * * *'`
  3. [ ] Change to: `cron: '0 */6 * * *'`
  4. [ ] Push to GitHub

**Option B: Pay - Hourly Runs**
- [ ] Exceeds free tier (need ~200+ min/month)
- [ ] Cost: ~$4/month for GitHub Pro
- [ ] To activate:
  1. [ ] Go to Settings → Billing and plan
  2. [ ] Upgrade to GitHub Pro
  3. [ ] No code changes needed ✓

**Option C: DIY - Self-Hosted Runner**
- [ ] Advanced setup required
- [ ] Runs on your machine
- [ ] Cost: $0/month (electricity only)
- [ ] To activate:
  1. [ ] Follow GitHub self-hosted runner setup
  2. [ ] Add runner to repo
  3. [ ] Update workflow to use your runner

## Setup Phase 4: Trigger First Run (1 minute)

- [ ] Go to **Actions** tab
- [ ] Click **"Hourly AI Trading Run"**
- [ ] Click **"Run workflow"** dropdown
- [ ] Click **"Run workflow"** button
- [ ] Green checkmark appears on workflow run
- [ ] Watch live execution logs (click the running item)

## Setup Phase 5: Verify It Works (5 minutes)

### Check Workflow Execution
- [ ] Workflow shows "in progress" (spinning icon)
- [ ] Job names appear:
  - [ ] "trading-run"
  - [ ] "notify-slack" (optional)
  - [ ] Wait 5-15 minutes for completion

### Check Results
- [ ] Workflow shows green checkmark (success)
- [ ] Scroll down to **Artifacts** section
- [ ] See files:
  - [ ] `trading-results-[ID]`
  - [ ] `merged-data-[ID]`
- [ ] Click to download and verify

### Check Logs (if there's an issue)
- [ ] Click "trading-run" job name
- [ ] Review log output
- [ ] Look for errors (usually clear error messages)

## Optional Enhancements

### Add Slack Notifications
- [ ] Create Slack incoming webhook
  1. [ ] Go to your Slack workspace
  2. [ ] Apps → "Incoming Webhooks"
  3. [ ] Create new webhook for a channel
  4. [ ] Copy webhook URL

- [ ] Add to GitHub secrets
  1. [ ] Go to Settings → Secrets
  2. [ ] New secret: `SLACK_WEBHOOK`
  3. [ ] Value: [Your webhook URL]
  4. [ ] Click "Add secret"

- [ ] Workflow will now post alerts automatically ✓

### Monitor Cost (for private repos)
- [ ] Go to **Settings → Billing and plan**
- [ ] Check **Actions** section monthly
- [ ] View minutes used vs. quota
- [ ] Adjust schedule if approaching limit

### Add Custom Tests
- [ ] Edit `tests/test_config.py` to add more checks
- [ ] Or create new test files: `tests/test_*.py`
- [ ] Tests run automatically on push

## Post-Setup Verification

### Daily (First Week)
- [ ] Check Actions tab daily
- [ ] Verify workflow runs complete
- [ ] Check for error messages
- [ ] Review trading results
- [ ] Monitor artifact generation

### Weekly
- [ ] Review recent workflow runs
- [ ] Check execution times
- [ ] Verify test passing rate
- [ ] Check GitHub Actions usage (if private)

### Monthly (Private Repos Only)
- [ ] Check Actions billing
- [ ] Confirm within quota
- [ ] Or adjust schedule if needed

## Troubleshooting Checklist

If workflows aren't running:

### Workflow Doesn't Appear
- [ ] Go to Actions tab and refresh
- [ ] Wait 60 seconds and refresh again
- [ ] Check if workflows are disabled
  - [ ] If disabled, click "Enable workflow"

### Workflow Fails on Schedule
- [ ] Make sure to push at least one commit
  - [ ] GitHub requires recent activity for scheduled workflows
  - [ ] Push any change to main branch

### API Keys Not Working
- [ ] Verify secret names are EXACTLY correct (case-sensitive)
- [ ] Check that values aren't truncated or have extra spaces
- [ ] Test keys locally before adding to GitHub
- [ ] Verify keys haven't expired
- [ ] Check API key rate limits

### Tests Failing
- [ ] Check test output in workflow logs
- [ ] Run tests locally: `pytest tests/ -v`
- [ ] Ensure Python 3.11+: `python --version`
- [ ] Install dependencies: `pip install -r requirements.txt`

### Data Fetch Failing
- [ ] Check Alpha Vantage API rate limits
- [ ] Verify internet connectivity
- [ ] Check API key permissions
- [ ] Review stock symbol list

### MCP Services Won't Start
- [ ] Increase timeout in workflow
- [ ] Check port availability
- [ ] Review service logs

## Success Criteria ✓

You've successfully set up GitHub Actions when:

- [ ] All 3 secrets added to GitHub
- [ ] Both workflows visible and enabled in Actions tab
- [ ] First manual trigger ran successfully
- [ ] Workflow logs show no errors
- [ ] Artifacts were generated and downloadable
- [ ] Next scheduled run completes successfully
- [ ] You can see trading data in artifacts

## Quick Reference Commands

```bash
# Test locally before pushing
pip install pytest pytest-cov black flake8 isort
pytest tests/ -v
black --check .
flake8 .

# View git status
git status

# Make changes and commit
git add .
git commit -m "Your message"
git push origin main
```

## Support & Help

### Documentation Files
1. **GITHUB_ACTIONS_SETUP.md** - Comprehensive guide
2. **.github/workflows/README.md** - Detailed workflow docs
3. **SETUP_SUMMARY.md** - Quick summary
4. **.github/workflows/QUICK_REFERENCE.txt** - Quick lookup

### Get Help
1. Read the relevant documentation file above
2. Check workflow logs for specific error messages
3. Search error message on GitHub/Stack Overflow
4. Review GitHub Actions docs: https://docs.github.com/en/actions

## Final Checklist

- [ ] All secrets added and verified
- [ ] Workflows enabled and visible
- [ ] First run triggered and completed
- [ ] Artifacts generated successfully
- [ ] No critical errors in logs
- [ ] Schedule chosen (hourly or custom)
- [ ] Understand cost implications (if private)
- [ ] Ready to monitor going forward

## Timeline

- **Setup time**: 3-5 minutes
- **First run**: 10-15 minutes
- **Subsequent runs**: Every hour (or custom schedule)
- **Total time to automation**: ~20 minutes from start to finish

---

## ✅ You're Done!

Your AI-Trader is now **fully automated**.

Check the **Actions** tab anytime to see:
- ✅ Trading results
- ✅ Test status
- ✅ Artifacts
- ✅ Execution logs

**Congratulations! Your AI is trading 24/7 on autopilot.** 🚀

---

**Created**: November 2024
**Last updated**: 2024-11-02
