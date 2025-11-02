#!/bin/bash
# Script to update Groq API key in GitHub secrets

echo "🔑 Groq API Key Update Tool"
echo "================================"
echo ""
echo "Follow these steps to get a fresh Groq API key:"
echo "1. Go to: https://console.groq.com/keys"
echo "2. Sign in to your Groq account"
echo "3. Copy a valid API key (should start with 'gsk_')"
echo "4. Paste it below"
echo ""

read -p "Enter your new Groq API key: " GROQ_KEY

# Validate format
if [[ ! $GROQ_KEY =~ ^gsk_ ]]; then
    echo "❌ Invalid format! API key should start with 'gsk_'"
    exit 1
fi

# Update the secret
echo "Updating GitHub secret..."
gh secret set GROQ_API_KEY --body "$GROQ_KEY"

if [ $? -eq 0 ]; then
    echo "✅ Groq API key updated successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Go to: https://github.com/pkrishnath/AI-Trader/actions"
    echo "2. Click 'Hourly AI Trading Run'"
    echo "3. Click 'Run workflow'"
    echo "4. Select 'groq' as LLM model"
    echo "5. Click 'Run workflow'"
    echo ""
    echo "Your new key will be used in the next run!"
else
    echo "❌ Failed to update API key"
    exit 1
fi
