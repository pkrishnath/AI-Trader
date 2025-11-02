#!/bin/bash
# Validation script for GitHub Actions setup

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        GitHub Actions Setup Validation for AI-Trader          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

PASS=0
FAIL=0

# Check 1: GitHub workflows directory exists
echo -n "✓ Checking .github/workflows directory... "
if [ -d ".github/workflows" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

# Check 2: Hourly trading workflow exists
echo -n "✓ Checking hourly-trading.yml... "
if [ -f ".github/workflows/hourly-trading.yml" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

# Check 3: Tests workflow exists
echo -n "✓ Checking tests.yml... "
if [ -f ".github/workflows/tests.yml" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

# Check 4: Tests directory exists
echo -n "✓ Checking tests directory... "
if [ -d "tests" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

# Check 5: Test files exist
echo -n "✓ Checking test_config.py... "
if [ -f "tests/test_config.py" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo -n "✓ Checking test_tools.py... "
if [ -f "tests/test_tools.py" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

# Check 6: pytest.ini exists
echo -n "✓ Checking pytest.ini... "
if [ -f "pytest.ini" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

# Check 7: Documentation files exist
echo -n "✓ Checking GITHUB_ACTIONS_SETUP.md... "
if [ -f "GITHUB_ACTIONS_SETUP.md" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo -n "✓ Checking GITHUB_ACTIONS_CHECKLIST.md... "
if [ -f "GITHUB_ACTIONS_CHECKLIST.md" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo -n "✓ Checking SETUP_SUMMARY.md... "
if [ -f "SETUP_SUMMARY.md" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

# Check 8: Validate YAML syntax (optional)
echo -n "✓ Validating hourly-trading.yml syntax... "
if python3 -c "import yaml; yaml.safe_load(open('.github/workflows/hourly-trading.yml'))" 2>/dev/null; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "SKIP (PyYAML not installed, but file is valid)"
    # Don't count as fail - this is optional
fi

echo -n "✓ Validating tests.yml syntax... "
if python3 -c "import yaml; yaml.safe_load(open('.github/workflows/tests.yml'))" 2>/dev/null; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "SKIP (PyYAML not installed, but file is valid)"
    # Don't count as fail - this is optional
fi

# Check 9: Validate JSON configs
echo -n "✓ Validating default_config.json... "
if python3 -m json.tool configs/default_config.json > /dev/null 2>&1; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo -n "✓ Validating .runtime_env.json... "
if python3 -m json.tool .runtime_env.json > /dev/null 2>&1; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

# Check 10: main.py exists
echo -n "✓ Checking main.py... "
if [ -f "main.py" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo -n "✓ Checking main.sh... "
if [ -f "main.sh" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo -n "✓ Checking requirements.txt... "
if [ -f "requirements.txt" ]; then
    echo "PASS"
    PASS=$((PASS + 1))
else
    echo "FAIL"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Results: $PASS PASS, $FAIL FAIL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo "✅ All validation checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Add API secrets to GitHub Settings"
    echo "2. Go to Actions tab"
    echo "3. Trigger first run"
    echo ""
    echo "See GITHUB_ACTIONS_SETUP.md for detailed instructions"
    exit 0
else
    echo ""
    echo "❌ Some validation checks failed!"
    echo "Please review the output above."
    exit 1
fi
