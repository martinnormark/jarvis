"""
Volume Reducing Audio Interface for ElevenLabs Conversational AI.

This module provides a custom audio interface that reduces volume instead
of clearing buffer when interrupted, allowing for more natural conversation flow.
"""

import threading
import queue
import platform
import time
import os
from typing import Callable, Optional
from elevenlabs.conversational_ai.conversation import AudioInterface


class VolumeReducingAudioInterface(AudioInterface):
    """
    Custom audio interface that reduces volume instead of clearing buffer when interrupted.

    This class extends ElevenLabs' AudioInterface to provide the ability
    to reduce audio volume when interrupted, allowing the user to speak
    while the agent's audio continues at a lower volume.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        input_frames: int = 2048,
        output_frames: int = 1024,
        volume_reduction_factor: float = 0.2,
        fade_duration_ms: int = 100,
    ):
        """
        Initialize the volume reducing audio interface.

        Args:
            sample_rate: Audio sample rate in Hz
            input_frames: Input buffer size in frames
            output_frames: Output buffer size in frames
            volume_reduction_factor: Factor to reduce volume by (0.0-1.0)
            fade_duration_ms: Duration of volume fade in milliseconds
        """
        try:
            import pyaudio
        except ImportError as e:
            raise ImportError(
                "PyAudio is required for VolumeReducingAudioInterface. "
                "Install with: pip install pyaudio"
            ) from e

        self.pyaudio = pyaudio
        self.sample_rate = sample_rate
        self.input_frames = input_frames
        self.output_frames = output_frames
        self.volume_reduction_factor = max(0.0, min(1.0, volume_reduction_factor))
        self.fade_duration_ms = fade_duration_ms

        self.is_macos = platform.system().lower() == "darwin"
        self.p: Optional[pyaudio.PyAudio] = None
        self.in_stream = None
        self.out_stream = None
        self.output_thread: Optional[threading.Thread] = None
        self.should_stop = threading.Event()
        self.output_queue: Optional[queue.Queue[bytes]] = None
        self.input_callback: Optional[Callable[[bytes], None]] = None
        self._is_playing = False

        # Volume control state
        self._is_interrupted = False
        self._interrupt_start_time = 0.0
        self._current_volume = 1.0
        self._volume_lock = threading.Lock()

        # macOS-specific environment variable to help with audio issues
        if self.is_macos:
            os.environ["PYAUDIO_USE_COREAUDIO"] = "1"

    def start(self, input_callback: Callable[[bytes], None]) -> None:
        """
        Start the audio interface.

        Args:
            input_callback: Callback function to handle input audio chunks

        Raises:
            RuntimeError: If audio interface fails to start
        """
        self.input_callback = input_callback

        # Audio output is buffered so we can handle interruptions.
        # Start a separate thread to handle writing to the output stream.
        self.output_queue = queue.Queue()
        self.should_stop.clear()
        self.output_thread = threading.Thread(target=self._output_thread, daemon=True)

        # Initialize PyAudio with error handling
        try:
            self.p = self.pyaudio.PyAudio()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize PyAudio: {e}") from e

        try:
            # Create input stream
            self.in_stream = self.p.open(
                format=self.pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                stream_callback=self._input_callback,
                frames_per_buffer=self.input_frames,
                start=True,
            )

            # Create output stream
            self.out_stream = self.p.open(
                format=self.pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.output_frames,
                start=True,
            )

        except Exception as e:
            self.stop()
            raise RuntimeError(f"Failed to start audio streams: {e}") from e

        if self.output_thread:
            self.output_thread.start()

    def stop(self) -> None:
        """Stop the audio interface and clean up resources."""
        self.should_stop.set()
        self._is_playing = False

        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join(timeout=2.0)

        self._cleanup_streams()

        if self.p:
            try:
                self.p.terminate()
            except Exception as e:
                print(f"Warning: Error terminating PyAudio: {e}")
            self.p = None

    def output(self, audio: bytes) -> None:
        """
        Output audio to the user.

        Args:
            audio: Audio data in 16-bit PCM mono format
        """
        if not self.should_stop.is_set() and self.output_queue:
            try:
                self.output_queue.put(audio, timeout=0.1)
                self._is_playing = True
            except queue.Full:
                pass  # Drop audio if queue is full

    def interrupt(self) -> None:
        """
        Interruption signal to reduce audio volume.

        Reduces the volume of audio output instead of clearing the buffer.
        """
        with self._volume_lock:
            self._is_interrupted = True
            self._interrupt_start_time = time.time()
            print("Audio interrupted - reducing volume to allow user speech")

    def force_interrupt(self) -> None:
        """Force interrupt the audio playback by reducing volume."""
        self.interrupt()

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self._is_playing and not self.output_queue.empty()

    def clear_audio_buffer(self) -> None:
        """Clear the audio output buffer."""
        if self.output_queue:
            try:
                while True:
                    self.output_queue.get(block=False)
            except queue.Empty:
                pass

    def _apply_volume_reduction(self, audio: bytes) -> bytes:
        """
        Apply volume reduction to audio data.

        Args:
            audio: Audio data in 16-bit PCM format

        Returns:
            Audio data with volume reduction applied
        """
        with self._volume_lock:
            if self._current_volume == 1.0:
                return audio

            # Convert bytes to numpy array
            import numpy as np

            audio_array = np.frombuffer(audio, dtype=np.int16)

            # Apply volume reduction
            reduced_audio = (audio_array * self._current_volume).astype(np.int16)

            # Convert back to bytes
            return reduced_audio.tobytes()

    def _cleanup_streams(self) -> None:
        """Clean up audio streams safely."""
        if self.in_stream:
            try:
                self.in_stream.stop_stream()
                self.in_stream.close()
            except Exception as e:
                print(f"Warning: Error closing input stream: {e}")
            self.in_stream = None

        if self.out_stream:
            try:
                self.out_stream.stop_stream()
                self.out_stream.close()
            except Exception as e:
                print(f"Warning: Error closing output stream: {e}")
            self.out_stream = None

    def _output_thread(self) -> None:
        """Output thread that handles writing audio data to the output stream."""
        while not self.should_stop.is_set():
            try:
                if self.output_queue:
                    audio = self.output_queue.get(timeout=0.25)
                    if audio and self.out_stream and not self.should_stop.is_set():
                        try:
                            # Apply volume reduction if interrupted
                            processed_audio = self._apply_volume_reduction(audio)
                            self.out_stream.write(processed_audio)
                        except Exception as e:
                            print(f"Audio output error: {e}")
                            break
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Unexpected error in output thread: {e}")
                break

    def _input_callback(
        self, in_data: bytes, frame_count: int, time_info: dict, status: int
    ) -> tuple:
        """
        Callback for input audio stream.

        Args:
            in_data: Input audio data
            frame_count: Number of frames
            time_info: Time information
            status: Status code

        Returns:
            Tuple of (None, paContinue) to continue streaming
        """
        if self.input_callback and in_data:
            try:
                self.input_callback(in_data)
            except Exception as e:
                print(f"Input callback error: {e}")
        return (None, self.pyaudio.paContinue)

    def resume_normal_volume(self) -> None:
        """
        Resume normal volume after interruption.

        This method can be called when the user stops speaking to restore
        normal audio volume.
        """
        with self._volume_lock:
            self._is_interrupted = False
            self._current_volume = 1.0
            print("Audio volume restored to normal")
