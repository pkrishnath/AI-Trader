"""
Unit tests for the trade tool (tool_trade.py).
"""

import json
import os
from unittest.mock import patch, mock_open

import pytest

from agent_tools import tool_trade

# --- Test Setup ---

@pytest.fixture
def mock_env_and_positions():
    """Pytest fixture to mock environment variables and position data."""
    with patch('os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key, default=None: {
            "SIGNATURE": "test_agent",
            "TODAY_DATE": "2025-11-10"
        }.get(key, default)

        initial_positions = {"AAPL": 10, "CASH": 10000.0}
        with patch('agent_tools.tool_trade.get_latest_position', return_value=(initial_positions, 0)):
            yield

# --- Tests for buy() ---

@patch('agent_tools.tool_trade.get_open_prices', return_value={"AAPL_price": 150.0})
def test_buy_successful(mock_get_prices, mock_env_and_positions):
    """Test a successful buy operation."""
    with patch("builtins.open", mock_open()) as mock_file:
        result = tool_trade.buy_logic(symbol="AAPL", amount=5)

        assert result["AAPL"] == 15
        assert result["CASH"] == 10000.0 - (150.0 * 5)
        
        mock_file.assert_called_with(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "agent_data", "test_agent", "position", "position.jsonl"),
            "a"
        )
        
        written_content = mock_file().write.call_args[0][0]
        log_data = json.loads(written_content.strip())
        
        assert log_data["this_action"]["action"] == "buy"
        assert log_data["positions"]["AAPL"] == 15

@patch('agent_tools.tool_trade.get_open_prices', return_value={"AAPL_price": 150.0})
def test_buy_insufficient_cash(mock_get_prices, mock_env_and_positions):
    """Test a buy operation that fails due to insufficient cash."""
    result = tool_trade.buy_logic(symbol="AAPL", amount=100)
    
    assert "error" in result
    assert "Insufficient cash" in result["error"]

@patch('agent_tools.tool_trade.get_open_prices', return_value={})
def test_buy_price_not_found(mock_get_prices, mock_env_and_positions):
    """Test a buy operation that fails because the price for the symbol is not found."""
    result = tool_trade.buy_logic(symbol="GOOG", amount=10)
    
    assert "error" in result
    assert "not found" in result["error"]

# --- Tests for sell() ---

@patch('agent_tools.tool_trade.get_open_prices', return_value={"AAPL_price": 200.0})
def test_sell_successful(mock_get_prices, mock_env_and_positions):
    """Test a successful sell operation."""
    with patch("builtins.open", mock_open()) as mock_file:
        result = tool_trade.sell_logic(symbol="AAPL", amount=5)

        assert result["AAPL"] == 5
        assert result["CASH"] == 10000.0 + (200.0 * 5)

        mock_file.assert_called_with(
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "agent_data", "test_agent", "position", "position.jsonl"),
            "a"
        )
        
        written_content = mock_file().write.call_args[0][0]
        log_data = json.loads(written_content.strip())
        
        assert log_data["this_action"]["action"] == "sell"
        assert log_data["positions"]["AAPL"] == 5

@patch('agent_tools.tool_trade.get_open_prices', return_value={"AAPL_price": 200.0})
def test_sell_insufficient_shares(mock_get_prices, mock_env_and_positions):
    """Test a sell operation that fails due to insufficient shares."""
    result = tool_trade.sell_logic(symbol="AAPL", amount=20)
    
    assert "error" in result
    assert "Insufficient shares" in result["error"]

@patch('agent_tools.tool_trade.get_open_prices', return_value={"MSFT_price": 300.0})
def test_sell_stock_not_owned(mock_get_prices, mock_env_and_positions):
    """Test a sell operation for a stock that is not in the portfolio."""
    result = tool_trade.sell_logic(symbol="MSFT", amount=5)
    
    assert "error" in result
    assert "No position" in result["error"]