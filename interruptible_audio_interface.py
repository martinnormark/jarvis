"""
Interruptible Audio Interface for ElevenLabs Conversational AI

This module provides a custom audio interface that can be interrupted
by external events (like button presses) while keeping the conversation
state intact.
"""

import threading
import queue
from typing import Callable
from elevenlabs.conversational_ai.conversation import AudioInterface


class InterruptibleAudioInterface(AudioInterface):
    """
    Custom audio interface that can be interrupted by button press.

    This class extends ElevenLabs' AudioInterface to provide the ability
    to stop audio playback immediately while preserving conversation state.
    """

    INPUT_FRAMES_PER_BUFFER = 4000  # 250ms @ 16kHz
    OUTPUT_FRAMES_PER_BUFFER = 1000  # 62.5ms @ 16kHz

    def __init__(self):
        """Initialize the interruptible audio interface."""
        try:
            import pyaudio
        except ImportError:
            raise ImportError(
                "To use InterruptibleAudioInterface you must install pyaudio."
            )
        self.pyaudio = pyaudio

    def start(self, input_callback: Callable[[bytes], None]):
        """
        Starts the audio interface.

        Args:
            input_callback: Callback function to handle input audio chunks
        """
        # Audio input is using callbacks from pyaudio which we simply pass through.
        self.input_callback = input_callback

        # Audio output is buffered so we can handle interruptions.
        # Start a separate thread to handle writing to the output stream.
        self.output_queue: queue.Queue[bytes] = queue.Queue()
        self.should_stop = threading.Event()
        self.output_thread = threading.Thread(target=self._output_thread)

        self.p = self.pyaudio.PyAudio()
        self.in_stream = self.p.open(
            format=self.pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            stream_callback=self._input_callback,
            frames_per_buffer=self.INPUT_FRAMES_PER_BUFFER,
            start=True,
        )
        self.out_stream = self.p.open(
            format=self.pyaudio.paInt16,
            channels=1,
            rate=16000,
            output=True,
            frames_per_buffer=self.OUTPUT_FRAMES_PER_BUFFER,
            start=True,
        )

        self.output_thread.start()

    def stop(self):
        """
        Stops the audio interface and cleans up resources.
        """
        self.should_stop.set()
        self.output_thread.join()
        self.in_stream.stop_stream()
        self.in_stream.close()
        self.out_stream.close()
        self.p.terminate()

    def output(self, audio: bytes):
        """
        Output audio to the user.

        Args:
            audio: Audio data in 16-bit PCM mono format at 16kHz
        """
        self.output_queue.put(audio)

    def interrupt(self):
        """
        Interruption signal to stop any audio output.

        Clears the output queue to stop any audio that is currently playing.
        """
        # Clear the output queue to stop any audio that is currently playing.
        # Note: We can't atomically clear the whole queue, but we are doing
        # it from the message handling thread so no new audio will be added
        # while we are clearing.
        try:
            while True:
                _ = self.output_queue.get(block=False)
        except queue.Empty:
            pass

    def _output_thread(self):
        """
        Output thread that handles writing audio data to the output stream.
        """
        while not self.should_stop.is_set():
            try:
                audio = self.output_queue.get(timeout=0.25)
                self.out_stream.write(audio)
            except queue.Empty:
                pass

    def _input_callback(self, in_data, frame_count, time_info, status):
        """
        Callback for input audio stream.
        """
        if self.input_callback:
            self.input_callback(in_data)
        return (None, self.pyaudio.paContinue)

    # Additional methods for external interruption control
    def force_interrupt(self):
        """
        Force an immediate interruption of audio output.

        This method can be called from any thread (e.g., button press handler)
        to immediately stop audio playback.
        """
        self.interrupt()

    def is_playing(self) -> bool:
        """
        Check if audio is currently playing.

        Returns:
            True if audio is playing (queue has items), False otherwise
        """
        return not self.output_queue.empty()

    def clear_audio_buffer(self):
        """
        Clear all buffered audio without stopping the interface.

        Useful for immediate interruption while keeping the conversation active.
        """
        self.interrupt()
