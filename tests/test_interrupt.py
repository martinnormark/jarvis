#!/usr/bin/env python3
"""
Test script using the InterruptibleAudioInterface in the same context as the working minimal test.
"""

import os
import sys
import signal
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")

if not agent_id or not api_key:
    print("Error: AGENT_ID and ELEVENLABS_API_KEY are required")
    sys.exit(1)

print("Testing with InterruptibleAudioInterface...")
print("=" * 60)

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs.conversational_ai.conversation import Conversation
    from interruptible_audio_interface import InterruptibleAudioInterface

    # Initialize ElevenLabs client
    elevenlabs = ElevenLabs(api_key=api_key)
    print("✓ ElevenLabs client initialized")

    # Create interruptible audio interface
    audio_interface = InterruptibleAudioInterface()
    print("✓ InterruptibleAudioInterface created")

    # Create conversation with interruptible audio interface
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
    print("✓ Conversation with InterruptibleAudioInterface created")

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

    print("Starting conversation session with InterruptibleAudioInterface...")
    print("Press Ctrl+C to stop")
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
