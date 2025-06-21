#!/usr/bin/env python3
"""
Test script to verify the interrupt functionality.
This script simulates the audio interface without requiring the full ElevenLabs setup.
"""

import threading
import time
import pyaudio
import io
import numpy as np
from interruptible_audio_interface import InterruptibleAudioInterface


class TestInterruptibleAudioInterface(InterruptibleAudioInterface):
    """
    Test version of the interruptible audio interface for testing purposes.
    """

    def play_test_tone(self, duration_seconds=5):
        """
        Play a test tone for the specified duration.
        """
        with self.audio_lock:
            # Stop any currently playing audio
            self.should_stop = True
            if self.current_audio_thread and self.current_audio_thread.is_alive():
                self.current_audio_thread.join(timeout=0.1)

            # Reset stop flag and start new audio
            self.should_stop = False
            self.current_audio_thread = threading.Thread(
                target=self._play_test_tone, args=(duration_seconds,)
            )
            self.current_audio_thread.start()

    def _play_test_tone(self, duration_seconds):
        """
        Play a test tone that can be interrupted.
        """
        try:
            # Generate a simple sine wave tone
            sample_rate = 44100
            frequency = 440  # A4 note
            samples = int(sample_rate * duration_seconds)

            # Generate sine wave
            t = np.linspace(0, duration_seconds, samples, False)
            tone = np.sin(2 * np.pi * frequency * t)

            # Convert to 16-bit PCM
            audio_data = (tone * 32767).astype(np.int16).tobytes()

            # Play using pyaudio
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16, channels=1, rate=sample_rate, output=True
            )

            # Play in chunks
            chunk_size = 1024
            audio_io = io.BytesIO(audio_data)

            print(f"Playing test tone for {duration_seconds} seconds...")

            while not self.should_stop:
                chunk = audio_io.read(chunk_size)
                if not chunk:
                    break

                if self.should_stop:
                    print("Audio interrupted!")
                    break

                stream.write(chunk)

            if not self.should_stop:
                print("Test tone completed.")

            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()

        except Exception as e:
            print(f"Audio playback error: {e}")


def test_interrupt_functionality():
    """
    Test the interrupt functionality.
    """
    print("Testing interruptible audio interface...")
    print("Press Ctrl+C to interrupt the audio.")

    audio_interface = TestInterruptibleAudioInterface()

    try:
        # Start playing a 10-second tone
        audio_interface.play_test_tone(duration_seconds=10)

        # Wait for 3 seconds, then interrupt
        time.sleep(3)
        print("Interrupting audio...")
        audio_interface.stop_audio()

        # Wait a bit, then play another tone
        time.sleep(1)
        print("Playing another tone...")
        audio_interface.play_test_tone(duration_seconds=5)

        # Let this one complete
        time.sleep(6)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        audio_interface.stop_audio()

    print("Test completed.")


if __name__ == "__main__":
    test_interrupt_functionality()
