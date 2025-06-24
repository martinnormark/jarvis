#!/usr/bin/env python3
"""
Simple demo script for SileroVADAudioInterface voice activity callback.

This script demonstrates the voice activity callback functionality
without requiring ElevenLabs credentials.
"""

import time
import threading


def demo_voice_activity_callback():
    """Demonstrate the voice activity callback functionality."""
    print("🎤 SileroVADAudioInterface Voice Activity Callback Demo")
    print("=" * 60)
    print("This demo shows how the voice activity callback works.")
    print("The callback will be triggered when the VAD detects speech.")
    print("Press Ctrl+C to stop the demo.")
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
        from jarvis.audio.interface import SileroVADAudioInterface

        # Create Silero VAD audio interface with voice activity callback
        audio_interface = SileroVADAudioInterface(
            sample_rate=16000,  # Silero VAD supports 8000 or 16000 Hz
            volume_reduction_factor=0.2,  # Reduce to 20% volume when user speaks
            vad_threshold=0.5,  # VAD sensitivity (0.0-1.0)
            min_speech_duration_ms=250,  # Minimum speech duration to trigger volume reduction
            min_silence_duration_ms=100,  # Minimum silence duration to restore volume
            voice_activity_callback=voice_activity_callback,  # Log voice activity
        )
        print("✓ SileroVADAudioInterface created with voice activity logging")

        # Simple input callback that just passes through
        def input_callback(audio_data: bytes):
            """Simple input callback that does nothing."""
            pass

        print("\n🎤 Starting voice activity detection...")
        print("💡 Try speaking into your microphone!")
        print("   The callback will log when you start and stop speaking.")
        print("   This simulates what happens in the full conversation demo.")
        print("-" * 50)

        # Start the audio interface
        audio_interface.start(input_callback)
        print("✓ Audio interface started")

        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Demo stopped by user")

        # Stop the audio interface
        audio_interface.stop()
        print("✓ Audio interface stopped")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


def show_callback_example():
    """Show an example of how to use the voice activity callback."""
    print("\n📝 Voice Activity Callback Example")
    print("=" * 50)
    print("Here's how to use the voice activity callback:")
    print()

    example_code = '''
def voice_activity_callback(is_speaking: bool):
    """Callback function to log voice activity detection."""
    timestamp = time.strftime("%H:%M:%S")
    if is_speaking:
        print(f"🎤 [{timestamp}] User started speaking - Volume reduced")
    else:
        print(f"🔇 [{timestamp}] User stopped speaking - Volume restored")

audio_interface = SileroVADAudioInterface(
    sample_rate=16000,
    volume_reduction_factor=0.2,
    vad_threshold=0.5,
    min_speech_duration_ms=250,
    min_silence_duration_ms=100,
    voice_activity_callback=voice_activity_callback,  # Add the callback here
)
'''
    print(example_code)
    print("The callback receives a boolean parameter:")
    print("  - True: User started speaking (volume reduced)")
    print("  - False: User stopped speaking (volume restored)")


if __name__ == "__main__":
    show_callback_example()

    response = input(
        "\nWould you like to try the voice activity callback demo? (y/n): "
    )
    if response.lower() in ["y", "yes"]:
        demo_voice_activity_callback()
    else:
        print(
            "Demo skipped. You can run it later with: python demo_silero_vad_callback.py"
        )
