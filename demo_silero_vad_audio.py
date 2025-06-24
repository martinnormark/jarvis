#!/usr/bin/env python3
"""
Demonstration script for SileroVADAudioInterface.

This script demonstrates the new Silero VAD audio interface that automatically
detects when the user is speaking and reduces the agent's audio volume accordingly.
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


def demo_silero_vad_interface():
    """Demonstrate the new Silero VAD audio interface."""
    print("🎤 SileroVADAudioInterface Demo")
    print("=" * 50)
    print(
        "This interface uses Silero VAD to automatically detect when you're speaking."
    )
    print("When you speak, the agent's audio volume automatically reduces to 20%.")
    print("When you stop speaking, the volume returns to normal.")
    print("No manual interruption needed - it's all automatic!")
    print()

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

        # Create Silero VAD audio interface with custom settings and voice activity callback
        audio_interface = SileroVADAudioInterface(
            sample_rate=16000,  # Silero VAD supports 8000 or 16000 Hz
            volume_reduction_factor=0.1,  # Reduce to 10% volume when user speaks (more dramatic)
            vad_threshold=0.2,  # VAD sensitivity (0.0-1.0) - lowered for better detection
            min_speech_duration_ms=100,  # Minimum speech duration to trigger volume reduction (faster)
            min_silence_duration_ms=50,  # Minimum silence duration to restore volume (faster)
            voice_activity_callback=voice_activity_callback,  # Log voice activity
        )
        print("✓ SileroVADAudioInterface created with voice activity logging")

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

        print("\n🎤 Starting conversation with automatic VAD...")
        print("💡 Try speaking while the agent is talking!")
        print("   The volume will automatically reduce when you speak.")
        print("   Voice activity will be logged with timestamps.")
        print("   No need to press any buttons - it's all automatic.")
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


def compare_vad_interfaces():
    """Compare the different audio interfaces."""
    print("\n📊 Audio Interface Comparison")
    print("=" * 50)
    print("InterruptibleAudioInterface:")
    print("  ❌ Manual interruption required")
    print("  ❌ Clears audio buffer completely")
    print("  ❌ Agent stops speaking immediately")
    print()
    print("VolumeReducingAudioInterface:")
    print("  ❌ Manual interruption required")
    print("  ✅ Reduces volume instead of clearing buffer")
    print("  ✅ Agent continues speaking at lower volume")
    print("  ✅ Smooth fade transition")
    print()
    print("SileroVADAudioInterface:")
    print("  ✅ Automatic voice activity detection")
    print("  ✅ No manual interruption needed")
    print("  ✅ Reduces volume when user speaks")
    print("  ✅ Restores volume when user stops")
    print("  ✅ Uses local Silero VAD model")
    print("  ✅ Works with 6000+ languages")
    print("  ✅ Real-time processing (<1ms per chunk)")
    print()


def show_vad_settings():
    """Show the configurable VAD settings."""
    print("\n⚙️  VAD Configuration Options")
    print("=" * 50)
    print("volume_reduction_factor: 0.1 (10% volume when user speaks)")
    print("vad_threshold: 0.2 (speech detection sensitivity)")
    print("min_speech_duration_ms: 100 (minimum speech to trigger reduction)")
    print("min_silence_duration_ms: 50 (minimum silence to restore volume)")
    print("sample_rate: 16000 (supports 8000 or 16000 Hz)")
    print()


if __name__ == "__main__":
    compare_vad_interfaces()
    show_vad_settings()

    response = input("Would you like to try the SileroVADAudioInterface demo? (y/n): ")
    if response.lower() in ["y", "yes"]:
        demo_silero_vad_interface()
    else:
        print(
            "Demo skipped. You can run it later with: python demo_silero_vad_audio.py"
        )
