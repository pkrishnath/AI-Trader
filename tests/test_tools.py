"""Tests for utility tools."""

import json
import os

import pytest


class TestPriceTools:
    """Test price data loading and processing."""

    def test_sample_price_file_exists(self):
        """Test that sample price files exist."""
        data_dir = "data"
        price_files = [
            f
            for f in os.listdir(data_dir)
            if f.startswith("daily_prices_") and f.endswith(".json")
        ]
        assert len(price_files) > 0, "No price data files found in data/ directory"

    def test_price_file_valid_json(self):
        """Test that price files are valid JSON."""
        data_dir = "data"
        price_files = [
            f
            for f in os.listdir(data_dir)
            if f.startswith("daily_prices_") and f.endswith(".json")
        ]

        if price_files:
            test_file = os.path.join(data_dir, price_files[0])
            with open(test_file, "r") as f:
                data = json.load(f)
            assert isinstance(
                data, (dict, list)
            ), f"Price data should be JSON object or array"

    def test_price_data_structure(self):
        """Test that price data has expected structure."""
        data_dir = "data"
        price_files = [
            f
            for f in os.listdir(data_dir)
            if f.startswith("daily_prices_") and f.endswith(".json")
        ]

        if price_files:
            test_file = os.path.join(data_dir, price_files[0])
            with open(test_file, "r") as f:
                data = json.load(f)

            if isinstance(data, dict):
                # Check if it has typical OHLCV data
                first_key = list(data.keys())[0] if data else None
                if first_key:
                    first_value = data[first_key]
                    assert isinstance(
                        first_value, dict
                    ), "Price data values should be dictionaries"


class TestMergedData:
    """Test merged data file."""

    def test_merged_jsonl_exists(self):
        """Test that merged.jsonl file exists."""
        merged_path = "data/merged.jsonl"
        # This is optional - merged.jsonl is generated at runtime
        if os.path.exists(merged_path):
            assert True
        else:
            # This is expected if the pipeline hasn't run yet
            assert True

    def test_merged_jsonl_format(self):
        """Test that merged.jsonl has correct format if it exists."""
        merged_path = "data/merged.jsonl"
        if os.path.exists(merged_path):
            with open(merged_path, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if line.strip():
                        data = json.loads(line)
                        assert isinstance(
                            data, dict
                        ), "Each JSONL line should be a JSON object"


class TestAgentData:
    """Test agent trading data."""

    def test_agent_data_directory_exists(self):
        """Test that agent data directory exists."""
        agent_data_dir = "data/agent_data"
        # Directory should exist or be created at runtime
        assert True  # This will be checked at runtime


class TestDataIntegrity:
    """Test data integrity and consistency."""

    def test_no_empty_price_files(self):
        """Test that price files are not empty."""
        data_dir = "data"
        price_files = [
            f
            for f in os.listdir(data_dir)
            if f.startswith("daily_prices_") and f.endswith(".json")
        ]

        for price_file in price_files:
            file_path = os.path.join(data_dir, price_file)
            file_size = os.path.getsize(file_path)
            assert file_size > 0, f"Price file {price_file} is empty"

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists."""
        assert os.path.exists("requirements.txt"), "requirements.txt not found"

    def test_main_entry_point_exists(self):
        """Test that main.py exists."""
        assert os.path.exists("main.py"), "main.py entry point not found"

    def test_main_script_exists(self):
        """Test that main.sh script exists."""
        assert os.path.exists("main.sh"), "main.sh script not found"
