"""
Unit tests for the BaseAgent class.
"""

import json
from unittest.mock import patch, mock_open
import pytest

from agent.base_agent.base_agent import BaseAgent

@pytest.fixture
def mock_agent():
    """Pytest fixture to create a BaseAgent instance with minimal setup."""
    agent = BaseAgent(
        signature="test_agent",
        basemodel="test_model",
        asset_type="stock",
        stock_symbols=["AAPL"],
        log_path="/tmp/test_logs"
    )
    return agent

def test_get_position_summary_success(mock_agent):
    """
    Test the get_position_summary method for a successful case.
    """
    # Mock the position file content
    position_data = [
        {"date": "2025-11-09", "id": 0, "positions": {"AAPL": 10, "CASH": 10000.0}},
        {"date": "2025-11-10", "id": 1, "positions": {"AAPL": 15, "CASH": 9250.0}},
    ]
    mock_file_content = "\n".join(json.dumps(p) for p in position_data)

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_file_content)) as mock_file:
            summary = mock_agent.get_position_summary()

            assert summary["signature"] == "test_agent"
            assert summary["latest_date"] == "2025-11-10"
            assert summary["total_records"] == 2
            assert summary["positions"]["AAPL"] == 15

def test_get_position_summary_no_file(mock_agent):
    """
    Test the get_position_summary method when the position file does not exist.
    """
    with patch("os.path.exists", return_value=False):
        summary = mock_agent.get_position_summary()
        assert "error" in summary
        assert "does not exist" in summary["error"]

def test_get_position_summary_empty_file(mock_agent):
    """
    Test the get_position_summary method when the position file is empty.
    """
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="")) as mock_file:
            summary = mock_agent.get_position_summary()
            assert "error" in summary
            assert "No position records" in summary["error"]
