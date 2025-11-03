"""
Enhanced logging system for AI Trading Agent
Provides detailed visibility into agent reasoning and execution
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Standard colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


class TradeLogger:
    """Enhanced logger for trading agent with detailed formatting"""

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.step_counter = 0

    def header(self, title: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}")
        print(f"{title.center(70)}")
        print(f"{'='*70}{Colors.RESET}\n")

    def subheader(self, title: str):
        """Print subsection header"""
        print(f"{Colors.BOLD}{Colors.BLUE}▶ {title}{Colors.RESET}")

    def step(self, step_num: int, total_steps: int, message: str = ""):
        """Log agent step"""
        self.step_counter = step_num
        step_str = f"Step {step_num}/{total_steps}"
        if message:
            print(f"{Colors.BRIGHT_CYAN}🔄 {step_str}: {message}{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_CYAN}🔄 {step_str}{Colors.RESET}")

    def thinking(self, thought: str):
        """Log AI thinking/reasoning"""
        print(f"{Colors.MAGENTA}💭 AI Thinking:{Colors.RESET}")
        for line in thought.split('\n'):
            if line.strip():
                print(f"   {line}")

    def tool_call(self, tool_name: str, args: Dict[str, Any]):
        """Log tool function call"""
        args_str = json.dumps(args, indent=2)
        print(f"{Colors.BRIGHT_BLUE}🔧 Calling tool: {tool_name}{Colors.RESET}")
        for line in args_str.split('\n'):
            print(f"   {line}")

    def tool_result(self, tool_name: str, result: Any, success: bool = True):
        """Log tool result"""
        status_icon = "✅" if success else "❌"
        status_color = Colors.GREEN if success else Colors.RED

        print(f"{status_color}{status_icon} Tool result from {tool_name}:{Colors.RESET}")

        if isinstance(result, dict):
            result_str = json.dumps(result, indent=2)
        else:
            result_str = str(result)

        lines = result_str.split('\n')
        for line in lines[:20]:  # Limit output
            print(f"   {line}")

        if len(lines) > 20:
            remaining = len(lines) - 20
            print(f"   ... ({remaining} more lines)")

    def error(self, error_msg: str, error_type: str = "Error"):
        """Log error with emphasis"""
        print(f"{Colors.BRIGHT_RED}❌ {error_type}: {error_msg}{Colors.RESET}")

    def warning(self, warning_msg: str):
        """Log warning"""
        print(f"{Colors.BRIGHT_YELLOW}⚠️  WARNING: {warning_msg}{Colors.RESET}")

    def success(self, message: str):
        """Log successful action"""
        print(f"{Colors.BRIGHT_GREEN}✅ {message}{Colors.RESET}")

    def info(self, message: str):
        """Log info message"""
        print(f"{Colors.CYAN}ℹ️  {message}{Colors.RESET}")

    def market_data(self, symbol: str, data: Dict[str, Any]):
        """Log market data"""
        print(f"{Colors.BRIGHT_CYAN}📊 Market Data for {symbol}:{Colors.RESET}")
        for key, value in data.items():
            print(f"   {key}: {value}")

    def position(self, symbol: str, quantity: float, price: float, value: float):
        """Log position information"""
        print(f"{Colors.BRIGHT_GREEN}📈 Position: {symbol}{Colors.RESET}")
        print(f"   Quantity: {quantity}")
        print(f"   Price: ${price:.2f}")
        print(f"   Value: ${value:.2f}")

    def trade_decision(self, action: str, symbol: str, amount: float, reason: str = "", price: float = 0):
        """Log trade decision with price and cost"""
        action_icon = "📈" if action.lower() == "buy" else "📉"
        action_color = Colors.GREEN if action.lower() == "buy" else Colors.RED

        trade_value = amount * price if price > 0 else 0

        print(f"{action_color}{action_icon} Trade Decision: {action.upper()} {amount} {symbol}{Colors.RESET}")
        if price > 0:
            print(f"   Price: ${price:,.2f}")
            print(f"   Trade Value: ${trade_value:,.2f}")
        if reason:
            print(f"   Reason: {reason}")

    def performance(self, portfolio_value: float, cash: float, p_and_l: float):
        """Log portfolio performance"""
        p_and_l_color = Colors.GREEN if p_and_l >= 0 else Colors.RED
        print(f"{Colors.BRIGHT_CYAN}💰 Portfolio Status:{Colors.RESET}")
        print(f"   Total Value: ${portfolio_value:.2f}")
        print(f"   Cash: ${cash:.2f}")
        print(f"{p_and_l_color}   P&L: ${p_and_l:+.2f}{Colors.RESET}")

    def trade_execution(self, symbol: str, action: str, quantity: float,
                        price: float, commission: float = 0):
        """Log executed trade with details"""
        action_icon = "📈" if action.lower() == "buy" else "📉"
        action_color = Colors.GREEN if action.lower() == "buy" else Colors.RED

        total_cost = (quantity * price) + commission

        print(f"{action_color}{action_icon} EXECUTED: {action.upper()} {quantity} {symbol}{Colors.RESET}")
        print(f"   Price per unit: ${price:,.2f}")
        print(f"   Quantity: {quantity}")
        print(f"   Subtotal: ${quantity * price:,.2f}")
        if commission > 0:
            print(f"   Commission: ${commission:,.2f}")
        print(f"   Total Cost: ${total_cost:,.2f}")

    def deepseek_tokens(self, input_tokens: int, output_tokens: int,
                       cache_hit_rate: float = 0.0):
        """Log DeepSeek token usage and costs"""
        # DeepSeek pricing
        input_cache_cost = (input_tokens * cache_hit_rate) * (0.028 / 1_000_000)
        input_regular_cost = (input_tokens * (1 - cache_hit_rate)) * (0.28 / 1_000_000)
        output_cost = output_tokens * (0.42 / 1_000_000)
        total_cost = input_cache_cost + input_regular_cost + output_cost

        print(f"{Colors.BRIGHT_BLUE}💻 DeepSeek Token Usage:{Colors.RESET}")
        print(f"   Input tokens (with cache):     {int(input_tokens * cache_hit_rate):,}")
        print(f"   Input tokens (without cache): {int(input_tokens * (1 - cache_hit_rate)):,}")
        print(f"   Output tokens:                {output_tokens:,}")
        print(f"   Total tokens:                 {input_tokens + output_tokens:,}")
        print(f"\n   Input (cached):    ${input_cache_cost:.6f} ({cache_hit_rate*100:.0f}% cache hit)")
        print(f"   Input (regular):   ${input_regular_cost:.6f}")
        print(f"   Output:            ${output_cost:.6f}")
        print(f"   {Colors.BRIGHT_CYAN}Total API Cost: ${total_cost:.6f}{Colors.RESET}")

    def session_costs(self, total_trades: int, total_trade_value: float,
                     total_api_cost: float, total_commission: float = 0):
        """Log session financial summary"""
        total_cost = total_api_cost + total_commission
        cost_per_trade = total_cost / total_trades if total_trades > 0 else 0

        print(f"\n{Colors.BRIGHT_YELLOW}💰 SESSION FINANCIAL SUMMARY:{Colors.RESET}")
        print(f"   Trades executed:       {total_trades}")
        print(f"   Total trade value:     ${total_trade_value:,.2f}")
        print(f"   API cost (DeepSeek):   ${total_api_cost:,.6f}")
        if total_commission > 0:
            print(f"   Commission:            ${total_commission:,.2f}")
        print(f"   {Colors.BRIGHT_CYAN}Total cost:            ${total_cost:,.6f}{Colors.RESET}")
        print(f"   Cost per trade:        ${cost_per_trade:,.6f}")

    def execution_summary(self, date: str, status: str, trades_made: int, p_and_l: float,
                         total_cost: float = 0, total_tokens: int = 0):
        """Log execution summary with financial details"""
        status_color = Colors.GREEN if status.lower() == "success" else Colors.RED

        print(f"\n{Colors.BOLD}{status_color}{'='*70}")
        print(f"EXECUTION SUMMARY - {date}")
        print(f"{'='*70}{Colors.RESET}")
        print(f"Status: {status}")
        print(f"Trades Made: {trades_made}")
        print(f"P&L: ${p_and_l:+.2f}")
        if total_cost > 0:
            print(f"API Cost: ${total_cost:,.6f}")
        if total_tokens > 0:
            print(f"Total Tokens: {total_tokens:,}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")


# Singleton logger instance
_logger = None

def get_logger() -> TradeLogger:
    """Get or create logger instance"""
    global _logger
    if _logger is None:
        _logger = TradeLogger()
    return _logger


def log_agent_message(message: str, message_type: str = "info"):
    """Log agent message"""
    logger = get_logger()

    if message_type == "thinking":
        logger.thinking(message)
    elif message_type == "error":
        logger.error(message)
    elif message_type == "warning":
        logger.warning(message)
    elif message_type == "success":
        logger.success(message)
    elif message_type == "tool_call":
        logger.tool_call(message, {})
    else:
        logger.info(message)


def log_detailed_step(
    step_num: int,
    total_steps: int,
    agent_message: str,
    tool_calls: Optional[List[Dict[str, Any]]] = None,
    tool_results: Optional[List[Dict[str, Any]]] = None,
):
    """Log a complete agent step with all details"""
    logger = get_logger()

    logger.step(step_num, total_steps)

    if agent_message:
        logger.thinking(agent_message)

    if tool_calls:
        print(f"{Colors.BRIGHT_BLUE}{'─'*70}{Colors.RESET}")
        for tool_call in tool_calls:
            logger.tool_call(
                tool_call.get("name", "unknown"),
                tool_call.get("args", {})
            )

    if tool_results:
        print(f"{Colors.BRIGHT_BLUE}{'─'*70}{Colors.RESET}")
        for result in tool_results:
            logger.tool_result(
                result.get("name", "unknown"),
                result.get("result", ""),
                result.get("success", True)
            )
