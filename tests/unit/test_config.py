"""
Unit tests for configuration module.
"""

import pytest
import os
from unittest.mock import patch, mock_open
from jarvis.core.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_creation(self):
        """Test creating a config with valid values."""
        config = Config(
            agent_id="test-agent",
            api_key="test-key",
            sample_rate=16000,
            input_frames_per_buffer=2048,
            output_frames_per_buffer=1024,
        )

        assert config.agent_id == "test-agent"
        assert config.api_key == "test-key"
        assert config.sample_rate == 16000
        assert config.input_frames_per_buffer == 2048
        assert config.output_frames_per_buffer == 1024

    def test_config_defaults(self):
        """Test config creation with default values."""
        config = Config(agent_id="test-agent", api_key="test-key")

        assert config.sample_rate == 16000
        assert config.input_frames_per_buffer == 4000
        assert config.output_frames_per_buffer == 1000

    def test_config_validation_valid(self):
        """Test config validation with valid values."""
        config = Config(agent_id="test-agent", api_key="test-key")
        config.validate()  # Should not raise

    def test_config_validation_empty_agent_id(self):
        """Test config validation with empty agent_id."""
        config = Config(agent_id="", api_key="test-key")
        with pytest.raises(ValueError, match="agent_id cannot be empty"):
            config.validate()

    def test_config_validation_empty_api_key(self):
        """Test config validation with empty api_key."""
        config = Config(agent_id="test-agent", api_key="")
        with pytest.raises(ValueError, match="api_key cannot be empty"):
            config.validate()

    def test_config_validation_invalid_sample_rate(self):
        """Test config validation with invalid sample rate."""
        config = Config(agent_id="test-agent", api_key="test-key", sample_rate=0)
        with pytest.raises(ValueError, match="sample_rate must be positive"):
            config.validate()

    def test_config_validation_invalid_input_frames(self):
        """Test config validation with invalid input frames."""
        config = Config(
            agent_id="test-agent", api_key="test-key", input_frames_per_buffer=0
        )
        with pytest.raises(
            ValueError, match="input_frames_per_buffer must be positive"
        ):
            config.validate()

    def test_config_validation_invalid_output_frames(self):
        """Test config validation with invalid output frames."""
        config = Config(
            agent_id="test-agent", api_key="test-key", output_frames_per_buffer=0
        )
        with pytest.raises(
            ValueError, match="output_frames_per_buffer must be positive"
        ):
            config.validate()

    @patch.dict(os.environ, {"AGENT_ID": "env-agent", "ELEVENLABS_API_KEY": "env-key"})
    def test_from_env_success(self):
        """Test creating config from environment variables."""
        config = Config.from_env()

        assert config.agent_id == "env-agent"
        assert config.api_key == "env-key"

    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_missing_agent_id(self):
        """Test from_env with missing AGENT_ID."""
        with pytest.raises(
            ValueError, match="AGENT_ID environment variable is required"
        ):
            Config.from_env()

    @patch.dict(os.environ, {"AGENT_ID": "test-agent"}, clear=True)
    def test_from_env_missing_api_key(self):
        """Test from_env with missing ELEVENLABS_API_KEY."""
        with pytest.raises(
            ValueError, match="ELEVENLABS_API_KEY environment variable is required"
        ):
            Config.from_env()

    @patch.dict(os.environ, {"AGENT_ID": "env-agent", "ELEVENLABS_API_KEY": "env-key"})
    @patch("dotenv.load_dotenv")
    def test_from_env_with_dotenv(self, mock_load_dotenv):
        """Test from_env with .env file loading."""
        config = Config.from_env(".env.local")

        mock_load_dotenv.assert_called_once_with(".env.local")
        assert config.agent_id == "env-agent"
        assert config.api_key == "env-key"

    @patch.dict(os.environ, {"AGENT_ID": "env-agent", "ELEVENLABS_API_KEY": "env-key"})
    @patch("dotenv.load_dotenv", side_effect=ImportError)
    def test_from_env_dotenv_import_error(self, mock_load_dotenv):
        """Test from_env when python-dotenv is not available."""
        config = Config.from_env(".env.local")

        # Should continue with system environment variables
        assert config.agent_id == "env-agent"
        assert config.api_key == "env-key"
