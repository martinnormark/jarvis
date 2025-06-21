#!/usr/bin/env python3
"""
Minimal test to isolate CFData assertion error.
This script tests ElevenLabs initialization without our custom audio interface.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")

if not agent_id or not api_key:
    print("Error: AGENT_ID and ELEVENLABS_API_KEY are required")
    sys.exit(1)

print("Testing ElevenLabs client initialization...")
try:
    from elevenlabs.client import ElevenLabs

    elevenlabs = ElevenLabs(api_key=api_key)
    print("✓ ElevenLabs client created successfully")
except Exception as e:
    print(f"✗ ElevenLabs client creation failed: {e}")
    sys.exit(1)

print("\nTesting conversation with default audio interface...")
try:
    from elevenlabs.conversational_ai.conversation import Conversation
    from elevenlabs.conversational_ai.conversation import AudioInterface

    # Create a minimal audio interface for testing
    class MinimalAudioInterface(AudioInterface):
        def start(self, input_callback):
            print("Minimal audio interface started")

        def stop(self):
            print("Minimal audio interface stopped")

        def output(self, audio):
            pass

        def interrupt(self):
            pass

    minimal_audio = MinimalAudioInterface()
    conversation_with_default = Conversation(
        elevenlabs,
        agent_id,
        requires_auth=bool(api_key),
        audio_interface=minimal_audio,
    )
    print("✓ Conversation with minimal audio interface created successfully")
except Exception as e:
    print(f"✗ Conversation with minimal audio interface failed: {e}")
    sys.exit(1)

print("\nTesting our custom audio interface creation...")
try:
    from interruptible_audio_interface import InterruptibleAudioInterface

    audio_interface = InterruptibleAudioInterface()
    print("✓ Custom audio interface created successfully")
except Exception as e:
    print(f"✗ Custom audio interface creation failed: {e}")
    sys.exit(1)

print("\nTesting conversation with our custom audio interface...")
try:
    conversation_with_custom_audio = Conversation(
        elevenlabs,
        agent_id,
        requires_auth=bool(api_key),
        audio_interface=audio_interface,
    )
    print("✓ Conversation with custom audio interface created successfully")
except Exception as e:
    print(f"✗ Conversation with custom audio interface failed: {e}")
    sys.exit(1)

print(
    "\nAll tests passed! The issue might be in the conversation session initialization."
)
print("Let's test starting a session with minimal audio interface...")

try:
    print("Starting conversation session with minimal audio...")
    conversation_with_default.start_session()
    print("✓ Session with minimal audio started successfully")

    # End the session immediately
    conversation_with_default.end_session()
    print("✓ Session with minimal audio ended successfully")

except Exception as e:
    print(f"✗ Session with minimal audio failed: {e}")
    sys.exit(1)

print("\nNow testing session with our custom audio interface...")

try:
    print("Starting conversation session with custom audio...")
    conversation_with_custom_audio.start_session()
    print("✓ Session with custom audio started successfully")

    # End the session immediately
    conversation_with_custom_audio.end_session()
    print("✓ Session with custom audio ended successfully")

except Exception as e:
    print(f"✗ Session with custom audio failed: {e}")
    sys.exit(1)

print("\n✓ All tests completed successfully!")
print("The CFData error might be intermittent or related to specific audio conditions.")
