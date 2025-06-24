#!/usr/bin/env python3
"""
Test script for SileroVADAudioInterface.

This script tests the new Silero VAD audio interface to ensure
it properly detects voice activity and reduces volume accordingly.
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

print("Testing SileroVADAudioInterface...")
print("=" * 60)


# Voice activity callback to log when user speaks
def voice_activity_callback(is_speaking: bool):
    """Callback function to log voice activity detection."""
    timestamp = time.strftime("%H:%M:%S")
    if is_speaking:
        print(f"🎤 [{timestamp}] User started speaking - Volume reduced")
    else:
        print(f"🔇 [{timestamp}] User stopped speaking - Volume restored")


try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs.conversational_ai.conversation import Conversation
    from jarvis.audio.interface import SileroVADAudioInterface

    # Initialize ElevenLabs client
    elevenlabs = ElevenLabs(api_key=api_key)
    print("✓ ElevenLabs client initialized")

    # Create Silero VAD audio interface
    audio_interface = SileroVADAudioInterface(
        sample_rate=16000,  # Silero VAD supports 8000 or 16000 Hz
        volume_reduction_factor=0.3,  # Reduce to 30% volume
        vad_threshold=0.5,  # VAD sensitivity
        min_speech_duration_ms=250,  # Minimum speech duration
        min_silence_duration_ms=100,  # Minimum silence duration
        voice_activity_callback=voice_activity_callback,  # Log voice activity
    )
    print("✓ SileroVADAudioInterface created with voice activity logging")

    # Create conversation with Silero VAD audio interface
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
    print("✓ Conversation with SileroVADAudioInterface created")

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

    print("Starting conversation session with Silero VAD audio interface...")
    print("Press Ctrl+C to stop")
    print("The audio interface will automatically detect when you're speaking")
    print("and reduce the agent's volume accordingly.")
    print("Voice activity will be logged with timestamps.")
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
