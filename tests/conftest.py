"""
Pytest configuration and common fixtures for Jarvis tests.
"""

import pytest
from unittest.mock import Mock, patch
from jarvis.core.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return Config(
        agent_id="test-agent-id",
        api_key="test-api-key",
        sample_rate=16000,
        input_frames_per_buffer=2048,
        output_frames_per_buffer=1024,
    )


@pytest.fixture
def mock_elevenlabs_client():
    """Create a mock ElevenLabs client."""
    return Mock()


@pytest.fixture
def mock_audio_interface():
    """Create a mock audio interface."""
    interface = Mock()
    interface.start = Mock()
    interface.stop = Mock()
    interface.output = Mock()
    interface.interrupt = Mock()
    interface.force_interrupt = Mock()
    interface.is_playing = Mock(return_value=False)
    return interface


@pytest.fixture
def mock_conversation():
    """Create a mock conversation object."""
    conversation = Mock()
    conversation.start_session = Mock()
    conversation.end_session = Mock()
    conversation.wait_for_session_end = Mock(return_value="test-conversation-id")
    conversation.send_user_message = Mock()
    return conversation


@pytest.fixture
def mock_platform_detector():
    """Create a mock platform detector."""
    detector = Mock()
    detector.get_platform = Mock(return_value="mac")
    detector.is_mac = Mock(return_value=True)
    detector.is_pi = Mock(return_value=False)
    detector.setup_input_handler = Mock()
    detector.cleanup = Mock()
    return detector
