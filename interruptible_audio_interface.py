"""
Interruptible Audio Interface for ElevenLabs Conversational AI

This module provides a custom audio interface that can be interrupted
by external events (like button presses) while keeping the conversation
state intact.
"""

import threading
import pyaudio
import io
from elevenlabs.conversational_ai.audio_interface import AudioInterface


class InterruptibleAudioInterface(AudioInterface):
    """
    Custom audio interface that can be interrupted by button press.

    This class extends ElevenLabs' AudioInterface to provide the ability
    to stop audio playback immediately while preserving conversation state.
    """

    def __init__(self):
        """Initialize the interruptible audio interface."""
        self.current_audio_thread = None
        self.should_stop = False
        self.audio_lock = threading.Lock()

    def play_audio(self, audio_data: bytes) -> None:
        """
        Play audio data with the ability to interrupt it.

        Args:
            audio_data: Raw audio bytes to play
        """
        with self.audio_lock:
            # Stop any currently playing audio
            self.should_stop = True
            if self.current_audio_thread and self.current_audio_thread.is_alive():
                self.current_audio_thread.join(timeout=0.1)

            # Reset stop flag and start new audio
            self.should_stop = False
            self.current_audio_thread = threading.Thread(
                target=self._play_audio_thread, args=(audio_data,)
            )
            self.current_audio_thread.start()

    def _play_audio_thread(self, audio_data: bytes):
        """
        Play audio in a separate thread so it can be interrupted.

        Args:
            audio_data: Raw audio bytes to play
        """
        try:
            # Use pyaudio to play the audio with interrupt capability
            p = pyaudio.PyAudio()

            # Open stream
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)

            # Convert audio data to chunks and play
            chunk_size = 1024
            audio_io = io.BytesIO(audio_data)

            while not self.should_stop:
                chunk = audio_io.read(chunk_size)
                if not chunk:
                    break

                if self.should_stop:
                    break

                stream.write(chunk)

            # Clean up
            stream.stop_stream()
            stream.close()
            p.terminate()

        except Exception as e:
            print(f"Audio playback error: {e}")

    def stop_audio(self):
        """
        Stop the currently playing audio.

        This method can be called from any thread to interrupt
        the current audio playback.
        """
        with self.audio_lock:
            self.should_stop = True
            if self.current_audio_thread and self.current_audio_thread.is_alive():
                self.current_audio_thread.join(timeout=0.1)

    def is_playing(self) -> bool:
        """
        Check if audio is currently playing.

        Returns:
            True if audio is playing, False otherwise
        """
        return (
            self.current_audio_thread is not None
            and self.current_audio_thread.is_alive()
            and not self.should_stop
        )
