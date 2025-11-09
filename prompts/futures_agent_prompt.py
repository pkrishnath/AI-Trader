"""
Futures Trading Agent Prompt
This file now uses the generic IctPromptGenerator.
"""
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tools.ict_prompt_generator import IctPromptGenerator
from tools.general_tools import get_config_value

# Futures symbols
FUTURES_SYMBOLS = ["NQ1"]

def get_futures_agent_system_prompt(today_date: str, signature: str, trade_style: str = "swing") -> str:
    """
    Generate system prompt for the futures trading agent using the generic ICT generator.
    """
    # The IctPromptGenerator can be extended to use the 'trade_style' if needed.
    # For now, it uses the same top-down analysis for all styles.
    prompt_generator = IctPromptGenerator(asset_type='futures', symbols=FUTURES_SYMBOLS)
    
    # Generate and return the prompt
    return prompt_generator.generate_prompt(today_date, signature)

if __name__ == "__main__":
    # Test the futures prompt generation
    today_date = "2025-11-03"
    signature = "deepseek-futures-trader"

    print("\n" + "=" * 60)
    print("FUTURES AGENT SYSTEM PROMPT (via Generic ICT Generator)")
    print("=" * 60 + "\n")
    prompt = get_futures_agent_system_prompt(today_date, signature)
    print(prompt)
