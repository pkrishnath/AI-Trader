"""
Test that all tool scripts can be imported without syntax or import errors.
This is a simple way to catch basic errors that would cause a container to fail on startup.
"""

import pytest

def test_import_tool_trade():
    """Test that tool_trade.py can be imported."""
    try:
        from agent_tools import tool_trade
    except Exception as e:
        pytest.fail(f"Failed to import tool_trade: {e}")

def test_import_tool_crypto_trade():
    """Test that tool_crypto_trade.py can be imported."""
    try:
        from agent_tools import tool_crypto_trade
    except Exception as e:
        pytest.fail(f"Failed to import tool_crypto_trade: {e}")

def test_import_tool_futures_trade():
    """Test that tool_futures_trade.py can be imported."""
    try:
        from agent_tools import tool_futures_trade
    except Exception as e:
        pytest.fail(f"Failed to import tool_futures_trade: {e}")

def test_import_tool_get_price_local():
    """Test that tool_get_price_local.py can be imported."""
    try:
        from agent_tools import tool_get_price_local
    except Exception as e:
        pytest.fail(f"Failed to import tool_get_price_local: {e}")

def test_import_tool_jina_search():
    """Test that tool_jina_search.py can be imported."""
    try:
        from agent_tools import tool_jina_search
    except Exception as e:
        pytest.fail(f"Failed to import tool_jina_search: {e}")

def test_import_tool_math():
    """Test that tool_math.py can be imported."""
    try:
        from agent_tools import tool_math
    except Exception as e:
        pytest.fail(f"Failed to import tool_math: {e}")
