"""
Configuration management for Jarvis.

Handles environment variables, platform-specific settings, and validation.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for Jarvis voice assistant."""

    agent_id: str
    api_key: str
    sample_rate: int = 16000
    input_frames_per_buffer: int = 4000  # 250ms @ 16kHz
    output_frames_per_buffer: int = 1000  # 62.5ms @ 16kHz

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> "Config":
        """
        Create configuration from environment variables.

        Args:
            env_file: Optional path to .env file to load

        Returns:
            Config instance with validated settings

        Raises:
            ValueError: If required environment variables are missing
        """
        # Load .env file if specified
        if env_file and os.path.exists(env_file):
            try:
                from dotenv import load_dotenv

                load_dotenv(env_file)
            except ImportError:
                pass  # python-dotenv not available, continue with system env

        # Get required environment variables
        agent_id = os.getenv("AGENT_ID")
        api_key = os.getenv("ELEVENLABS_API_KEY")

        # Validate required variables
        if not agent_id:
            raise ValueError(
                "AGENT_ID environment variable is required. "
                "Set it in your .env.local file or environment."
            )

        if not api_key:
            raise ValueError(
                "ELEVENLABS_API_KEY environment variable is required. "
                "Set it in your .env.local file or environment."
            )

        return cls(
            agent_id=agent_id,
            api_key=api_key,
        )

    def validate(self) -> None:
        """Validate configuration values."""
        if not self.agent_id.strip():
            raise ValueError("agent_id cannot be empty")

        if not self.api_key.strip():
            raise ValueError("api_key cannot be empty")

        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")

        if self.input_frames_per_buffer <= 0:
            raise ValueError("input_frames_per_buffer must be positive")

        if self.output_frames_per_buffer <= 0:
            raise ValueError("output_frames_per_buffer must be positive")
