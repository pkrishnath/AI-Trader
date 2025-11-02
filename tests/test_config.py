"""Tests for configuration loading and validation."""

import json
import os

import pytest


class TestConfigLoading:
    """Test configuration file loading."""

    def test_default_config_exists(self):
        """Test that default config file exists."""
        config_path = "configs/default_config.json"
        assert os.path.exists(config_path), f"Default config not found at {config_path}"

    def test_default_config_valid_json(self):
        """Test that default config is valid JSON."""
        config_path = "configs/default_config.json"
        with open(config_path, "r") as f:
            config = json.load(f)
        assert isinstance(config, dict), "Config should be a dictionary"

    def test_config_has_required_fields(self):
        """Test that config has required fields."""
        config_path = "configs/default_config.json"
        with open(config_path, "r") as f:
            config = json.load(f)

        required_fields = ["agent_type", "date_range", "models", "agent_config"]
        for field in required_fields:
            assert field in config, f"Config missing required field: {field}"

    def test_agent_config_has_initial_cash(self):
        """Test that agent config includes initial cash."""
        config_path = "configs/default_config.json"
        with open(config_path, "r") as f:
            config = json.load(f)

        assert (
            "initial_cash" in config["agent_config"]
        ), "Agent config should have initial_cash"
        assert (
            config["agent_config"]["initial_cash"] > 0
        ), "Initial cash should be positive"

    def test_runtime_env_exists(self):
        """Test that runtime environment file exists."""
        runtime_path = ".runtime_env.json"
        assert os.path.exists(
            runtime_path
        ), f"Runtime env file not found at {runtime_path}"

    def test_runtime_env_valid_json(self):
        """Test that runtime env is valid JSON."""
        runtime_path = ".runtime_env.json"
        with open(runtime_path, "r") as f:
            runtime_env = json.load(f)
        assert isinstance(runtime_env, dict), "Runtime env should be a dictionary"

    def test_env_example_exists(self):
        """Test that .env.example exists."""
        env_path = ".env.example"
        assert os.path.exists(env_path), ".env.example file not found"

    def test_env_example_has_required_variables(self):
        """Test that .env.example has required variables."""
        env_path = ".env.example"
        with open(env_path, "r") as f:
            content = f.read()

        required_vars = ["OPENAI_API_KEY", "ALPHAADVANTAGE_API_KEY", "JINA_API_KEY"]
        for var in required_vars:
            assert var in content, f"Missing {var} in .env.example"


class TestConfigValidation:
    """Test configuration validation logic."""

    def test_date_range_format(self):
        """Test that date range has valid format."""
        config_path = "configs/default_config.json"
        with open(config_path, "r") as f:
            config = json.load(f)

        date_range = config["date_range"]
        assert "init_date" in date_range, "date_range should have init_date"
        assert "end_date" in date_range, "date_range should have end_date"

    def test_models_list_not_empty(self):
        """Test that models list is not empty."""
        config_path = "configs/default_config.json"
        with open(config_path, "r") as f:
            config = json.load(f)

        assert len(config["models"]) > 0, "Models list should not be empty"

    def test_model_has_required_fields(self):
        """Test that each model has required fields."""
        config_path = "configs/default_config.json"
        with open(config_path, "r") as f:
            config = json.load(f)

        required_model_fields = ["name", "basemodel"]
        for model in config["models"]:
            for field in required_model_fields:
                assert field in model, f"Model missing field: {field}"
