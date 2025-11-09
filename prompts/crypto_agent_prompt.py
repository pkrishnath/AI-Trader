"""
Cryptocurrency Trading Agent Prompt
This file now uses the generic IctPromptGenerator.
"""
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.ict_prompt_generator import IctPromptGenerator
from tools.general_tools import get_config_value

# Cryptocurrency symbols
CRYPTO_SYMBOLS = ["BTC", "ETH"]

def get_crypto_agent_system_prompt(today_date: str, signature: str) -> str:
    """
    Generate system prompt for the crypto trading agent using the generic ICT generator.
    """
    # Instantiate the generator for the 'crypto' asset type
    prompt_generator = IctPromptGenerator(asset_type='crypto', symbols=CRYPTO_SYMBOLS)
    
    # Generate and return the prompt
    return prompt_generator.generate_prompt(today_date, signature)


if __name__ == "__main__":
    # Test the crypto prompt generation
    today_date = "2025-11-09"
    signature = "deepseek-crypto-trader"

    print("\n" + "=" * 60)
    print("CRYPTO AGENT SYSTEM PROMPT (via Generic ICT Generator)")
    print("=" * 60 + "\n")
    prompt = get_crypto_agent_system_prompt(today_date, signature)
    print(prompt)
