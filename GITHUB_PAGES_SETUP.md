# GitHub Pages Dashboard Setup

Your AI-Trader dashboard is automatically updated and deployed to GitHub Pages after every trading run!

## What's Automated

✅ **After every hourly trading run:**
1. Trading data is collected from `data/merged.jsonl` and `data/agent_data/`
2. Data is copied to the `docs/` folder
3. Dashboard is automatically deployed to GitHub Pages
4. Live at: `https://pkrishnath.github.io/AI-Trader/`

✅ **Dashboard updates automatically:**
- Performance charts refresh with latest trading data
- Leaderboard updates with new results
- Portfolio analysis shows current positions
- Everything synced with real-time trading

## Enable GitHub Pages

You only need to do this ONCE:

### Step 1: Go to Repository Settings
1. GitHub repo → **Settings** tab
2. Scroll down to **Pages** section (left sidebar)

### Step 2: Configure GitHub Pages
1. **Source**: Select **Deploy from a branch**
2. **Branch**: Select **main**
3. **Folder**: Select **/ (root)**
   - OR if you want docs folder: **/docs**
4. Click **Save**

### Step 3: Wait for Deployment
- GitHub will deploy your site
- Check the **Actions** tab for deployment status
- Once complete, you'll see a URL like:
  `https://pkrishnath.github.io/AI-Trader/`

## View Your Dashboard

**After GitHub Pages is enabled:**

- **Main Dashboard**: `https://pkrishnath.github.io/AI-Trader/`
- **Portfolio Analysis**: `https://pkrishnath.github.io/AI-Trader/portfolio.html`

These pages will automatically update after every trading run!

## How It Works

### Workflow Flow

```
Hourly Trading Run starts
        ↓
Trading simulation executes
        ↓
Results saved to data/agent_data/
        ↓
Trading data copied to docs/
        ↓
Deploy Dashboard workflow triggers
        ↓
Data is pushed to GitHub Pages
        ↓
Dashboard goes live (5-10 seconds)
```

### File Structure

```
docs/
├── index.html              (Main dashboard)
├── portfolio.html          (Portfolio page)
├── assets/
│   ├── css/styles.css      (Styling)
│   └── js/                 (JavaScript)
├── figs/                   (Brand logos)
└── data/                   (Auto-synced from data/)
    ├── merged.jsonl        (All trading data)
    └── agent_data/         (Agent results)
```

## Monitoring Dashboard Deployments

### Check Deployment Status
1. Go to **Actions** tab in GitHub
2. Look for **"Deploy Dashboard to GitHub Pages"** workflow
3. See deployment status and URL

### Check Deployment Logs
1. Actions → **Deploy Dashboard to GitHub Pages**
2. Click the specific run
3. View logs for any issues

## Troubleshooting

### Dashboard Not Updating

**Problem**: Traded data shows but dashboard looks old

**Solutions:**
1. Hard refresh your browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Check if trading run completed successfully
3. Verify data files in docs/ folder:
   - Go to: GitHub repo → docs folder
   - Should see `merged.jsonl` and `agent_data/`

### Pages Not Enabled

**Problem**: Dashboard URL returns 404

**Solutions:**
1. Follow "Enable GitHub Pages" section above
2. Make sure source is set to **main** branch, **docs** folder
3. Wait 1-2 minutes for initial deployment
4. Check Actions tab for deployment errors

### Data Not Syncing

**Problem**: Dashboard shows old data

**Solutions:**
1. Verify trading run completed (check Actions → Hourly AI Trading Run)
2. Check data files exist in data/ folder
3. Monitor "Deploy Dashboard to GitHub Pages" workflow
4. Check if workflow is being triggered

## Customization

### Change Dashboard Layout

Edit the HTML/CSS files in `docs/`:
- `docs/index.html` - Main page layout
- `docs/assets/css/styles.css` - Styling
- `docs/assets/js/*.js` - JavaScript logic

After editing, push changes and dashboard auto-updates!

### Add Custom Metrics

Edit `docs/assets/js/data-loader.js` to:
- Add new performance metrics
- Create custom charts
- Add filtering options

Changes deploy automatically!

## Real-Time Updates

Your dashboard now features:

📊 **Real-Time Performance**
- Updates every hour with new trading data
- Live leaderboard of AI models
- Current portfolio positions

📈 **Trading Charts**
- Performance over time
- Return comparisons
- Win/loss analysis

💼 **Portfolio Tracking**
- Current holdings
- Position history
- P&L per stock

🤖 **Agent Comparison**
- AI model performance
- Trading strategies effectiveness
- Risk metrics

## Performance Tips

- **Clear Cache**: For faster updates, hard refresh (`Ctrl+Shift+R`)
- **Use Chrome DevTools**: For debugging dashboard issues
- **Check GitHub Status**: If dashboard seems slow

## Support

For issues:
1. Check workflow logs in Actions tab
2. Verify data files in docs/ folder
3. Review browser console for JavaScript errors
4. Check GitHub Pages settings

---

**Your dashboard is now LIVE and auto-updating! 🎉**

Every hour your trading data syncs and the dashboard refreshes automatically.

Monitor trading performance in real-time at:
👉 `https://pkrishnath.github.io/AI-Trader/`
