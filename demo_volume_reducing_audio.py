#!/usr/bin/env python3
"""
Demonstration script for VolumeReducingAudioInterface.

This script demonstrates the difference between the old InterruptibleAudioInterface
(which clears the buffer) and the new VolumeReducingAudioInterface (which reduces volume).
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")

if not agent_id or not api_key:
    print("Error: AGENT_ID and ELEVENLABS_API_KEY are required")
    print("Please set them in your .env.local file")
    sys.exit(1)


def demo_volume_reducing_interface():
    """Demonstrate the new volume reducing audio interface."""
    print("🎵 VolumeReducingAudioInterface Demo")
    print("=" * 50)
    print(
        "This interface reduces volume instead of clearing the buffer when interrupted."
    )
    print(
        "When you press the interrupt button, the agent's audio will fade to 30% volume."
    )
    print("This allows you to speak while still hearing the agent's response.")
    print()

    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs.conversational_ai.conversation import Conversation
        from jarvis.audio.interface import VolumeReducingAudioInterface

        # Initialize ElevenLabs client
        elevenlabs = ElevenLabs(api_key=api_key)
        print("✓ ElevenLabs client initialized")

        # Create volume reducing audio interface with custom settings
        audio_interface = VolumeReducingAudioInterface(
            volume_reduction_factor=0.3,  # Reduce to 30% volume
            fade_duration_ms=150,  # 150ms fade duration
        )
        print("✓ VolumeReducingAudioInterface created")

        # Create conversation
        conversation = Conversation(
            elevenlabs,
            agent_id,
            requires_auth=bool(api_key),
            audio_interface=audio_interface,
            callback_agent_response=lambda response: print(f"🤖 Agent: {response}"),
            callback_agent_response_correction=lambda original, corrected: print(
                f"🤖 Agent (corrected): {original} -> {corrected}"
            ),
            callback_user_transcript=lambda transcript: print(f"👤 User: {transcript}"),
        )
        print("✓ Conversation created")

        print("\n🎤 Starting conversation...")
        print("💡 Try interrupting the agent while it's speaking!")
        print("   The audio will fade to 30% volume instead of stopping completely.")
        print("   Press Ctrl+C to stop the demo.")
        print("-" * 50)

        # Start the session
        conversation.start_session()
        conversation_id = conversation.wait_for_session_end()
        print(f"\n✓ Conversation ended. ID: {conversation_id}")

    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


def compare_interfaces():
    """Compare the old and new audio interfaces."""
    print("\n📊 Interface Comparison")
    print("=" * 50)
    print("Old InterruptibleAudioInterface:")
    print("  ❌ Clears audio buffer completely")
    print("  ❌ Agent stops speaking immediately")
    print("  ❌ User loses context of what agent was saying")
    print()
    print("New VolumeReducingAudioInterface:")
    print("  ✅ Reduces volume to 30% (configurable)")
    print("  ✅ Agent continues speaking at lower volume")
    print("  ✅ User can still hear and understand the agent")
    print("  ✅ Smooth fade transition (150ms)")
    print("  ✅ Volume automatically restores when user speaks")
    print()


if __name__ == "__main__":
    compare_interfaces()

    response = input(
        "Would you like to try the VolumeReducingAudioInterface demo? (y/n): "
    )
    if response.lower() in ["y", "yes"]:
        demo_volume_reducing_interface()
    else:
        print(
            "Demo skipped. You can run it later with: python demo_volume_reducing_audio.py"
        )
