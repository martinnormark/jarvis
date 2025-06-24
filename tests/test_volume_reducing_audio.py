#!/usr/bin/env python3
"""
Test script for VolumeReducingAudioInterface.

This script tests the new volume reducing audio interface to ensure
it properly reduces volume instead of clearing the buffer when interrupted.
"""

import os
import sys
import signal
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")

if not agent_id or not api_key:
    print("Error: AGENT_ID and ELEVENLABS_API_KEY are required")
    sys.exit(1)

print("Testing VolumeReducingAudioInterface...")
print("=" * 60)

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs.conversational_ai.conversation import Conversation
    from jarvis.audio.interface import VolumeReducingAudioInterface

    # Initialize ElevenLabs client
    elevenlabs = ElevenLabs(api_key=api_key)
    print("✓ ElevenLabs client initialized")

    # Create volume reducing audio interface
    audio_interface = VolumeReducingAudioInterface(
        volume_reduction_factor=0.3,  # Reduce to 30% volume
        fade_duration_ms=150,  # 150ms fade duration
    )
    print("✓ VolumeReducingAudioInterface created")

    # Create conversation with volume reducing audio interface
    conversation = Conversation(
        elevenlabs,
        agent_id,
        requires_auth=bool(api_key),
        audio_interface=audio_interface,
        callback_agent_response=lambda response: print(f"Agent: {response}"),
        callback_agent_response_correction=lambda original, corrected: print(
            f"Agent: {original} -> {corrected}"
        ),
        callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
    )
    print("✓ Conversation with VolumeReducingAudioInterface created")

    def cleanup_handler(sig, frame):
        """Cleanup handler for graceful shutdown."""
        print("\nShutting down gracefully...")
        try:
            conversation.end_session()
            audio_interface.stop()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_handler)

    print("Starting conversation session with volume reducing audio interface...")
    print("Press Ctrl+C to stop")
    print(
        "The audio interface will reduce volume instead of clearing buffer when interrupted"
    )
    print("-" * 60)

    # Start the session
    conversation.start_session()
    print("✓ Session started successfully")

    # Wait for session to end
    conversation_id = conversation.wait_for_session_end()
    print(f"✓ Session ended. Conversation ID: {conversation_id}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
