"""
Silero VAD Audio Interface for ElevenLabs Conversational AI.

This module provides a custom audio interface that uses Silero VAD for
voice activity detection, automatically adjusting volume based on user speech.
"""

import threading
import queue
import platform
import time
import os
from typing import Callable, Optional
from elevenlabs.conversational_ai.conversation import AudioInterface


class SileroVADAudioInterface(AudioInterface):
    """
    Audio interface that uses Silero VAD for voice activity detection.

    This interface automatically reduces volume when the user is speaking
    and restores it when they stop speaking, providing a more natural
    conversation experience.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        input_frames: int = 2048,
        output_frames: int = 1024,
        volume_reduction_factor: float = 0.2,
        fade_duration_ms: int = 100,
        vad_threshold: float = 0.5,
        min_speech_duration_ms: int = 250,
        min_silence_duration_ms: int = 100,
        voice_activity_callback: Optional[Callable[[bool], None]] = None,
    ):
        """
        Initialize the Silero VAD audio interface.

        Args:
            sample_rate: Audio sample rate in Hz (must be 8000 or 16000 for Silero VAD)
            input_frames: Input buffer size in frames
            output_frames: Output buffer size in frames
            volume_reduction_factor: Volume reduction factor when user is speaking (0.0-1.0)
            fade_duration_ms: Duration of volume fade transition in milliseconds
            vad_threshold: VAD threshold for speech detection (0.0-1.0)
            min_speech_duration_ms: Minimum speech duration to trigger volume reduction
            min_silence_duration_ms: Minimum silence duration to restore volume
            voice_activity_callback: Optional callback function called when user speaking state changes
                                    Callback receives a boolean: True when user starts speaking, False when they stop
        """
        try:
            import pyaudio
        except ImportError as e:
            raise ImportError(
                "PyAudio is required for SileroVADAudioInterface. "
                "Install with: pip install pyaudio"
            ) from e

        try:
            from silero_vad import load_silero_vad, get_speech_timestamps
        except ImportError as e:
            raise ImportError(
                "Silero VAD is required for SileroVADAudioInterface. "
                "Install with: pip install silero-vad"
            ) from e

        self.pyaudio = pyaudio
        self.sample_rate = sample_rate
        self.input_frames = input_frames
        self.output_frames = output_frames
        self.volume_reduction_factor = volume_reduction_factor
        self.fade_duration_ms = fade_duration_ms
        self.vad_threshold = vad_threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.min_silence_duration_ms = min_silence_duration_ms
        self.voice_activity_callback = voice_activity_callback

        # Validate sample rate for Silero VAD
        if sample_rate not in [8000, 16000]:
            raise ValueError(
                "Silero VAD only supports 8000 Hz or 16000 Hz sample rates"
            )

        self.is_macos = platform.system().lower() == "darwin"
        self.p: Optional[pyaudio.PyAudio] = None
        self.in_stream = None
        self.out_stream = None
        self.output_thread: Optional[threading.Thread] = None
        self.vad_thread: Optional[threading.Thread] = None
        self.should_stop = threading.Event()
        self.output_queue: Optional[queue.Queue[bytes]] = None
        self.input_queue: Optional[queue.Queue[bytes]] = None
        self.input_callback: Optional[Callable[[bytes], None]] = None
        self._is_playing = False
        self._user_speaking = False
        self._current_volume = 1.0
        self._target_volume = 1.0
        self._volume_lock = threading.Lock()

        # Initialize Silero VAD
        self.vad_model = load_silero_vad()
        self.get_speech_timestamps = get_speech_timestamps

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
        self.input_queue = queue.Queue()
        self.should_stop.clear()
        self.output_thread = threading.Thread(target=self._output_thread, daemon=True)
        self.vad_thread = threading.Thread(target=self._vad_thread, daemon=True)

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

        # Reset VAD model state for fresh start
        try:
            self.vad_model.reset_states()
            print("🎙️ VAD: Model state reset")
        except Exception as e:
            print(f"🎙️ VAD: Could not reset model state: {e}")

        if self.output_thread:
            self.output_thread.start()
        if self.vad_thread:
            self.vad_thread.start()

    def stop(self) -> None:
        """Stop the audio interface and clean up resources."""
        self.should_stop.set()
        self._is_playing = False

        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join(timeout=2.0)
        if self.vad_thread and self.vad_thread.is_alive():
            self.vad_thread.join(timeout=2.0)

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
        Interruption signal to stop any audio output.

        Clears the output queue to stop any audio that is currently playing.
        """
        self._is_playing = False
        if self.output_queue:
            try:
                while True:
                    self.output_queue.get(block=False)
            except queue.Empty:
                pass

    def force_interrupt(self) -> None:
        """Force interrupt the audio playback."""
        self.interrupt()

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self._is_playing and not self.output_queue.empty()

    def clear_audio_buffer(self) -> None:
        """Clear the audio output buffer."""
        self.interrupt()

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

    def _update_volume(self, user_speaking: bool) -> None:
        """
        Update volume based on user speech activity.

        Args:
            user_speaking: Whether the user is currently speaking
        """
        with self._volume_lock:
            if user_speaking != self._user_speaking:
                self._user_speaking = user_speaking
                self._target_volume = (
                    self.volume_reduction_factor if user_speaking else 1.0
                )
                # Actually update the current volume that's used for reduction
                self._current_volume = self._target_volume
                print(
                    f"🔊 Volume updated: {self._current_volume:.2f} (user_speaking={user_speaking})"
                )

                # Note: We don't clear the queue here as that would stop the agent entirely
                # Instead, we rely on the volume reduction being applied to each chunk
                # as it's processed in the output thread

        if self.voice_activity_callback:
            self.voice_activity_callback(user_speaking)

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
                    audio = self.output_queue.get(timeout=0.1)

                    # Apply volume reduction if needed
                    audio = self._apply_volume_reduction(audio)

                    if self.out_stream and not self.out_stream.is_stopped():
                        self.out_stream.write(audio)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Warning: Error in output thread: {e}")
                break

    def _vad_thread(self) -> None:
        """VAD thread that processes audio input for voice activity detection."""
        import numpy as np

        # Buffer for accumulating audio data for VAD processing
        audio_buffer = np.array([], dtype=np.float32)

        # Silero VAD requires specific chunk sizes:
        # 16kHz: 512 samples (~32ms)
        # 8kHz: 256 samples (~32ms)
        if self.sample_rate == 16000:
            vad_chunk_size = 512
        elif self.sample_rate == 8000:
            vad_chunk_size = 256
        else:
            raise ValueError(f"Unsupported sample rate: {self.sample_rate}")

        # Initialize timing with current time
        current_time = time.time() * 1000  # Convert to milliseconds
        last_speech_time = current_time
        last_silence_time = current_time

        print(
            f"🎙️ VAD: Starting with chunk size {vad_chunk_size} samples for {self.sample_rate}Hz"
        )

        while not self.should_stop.is_set():
            try:
                if self.input_queue:
                    # Collect audio data
                    audio_chunk = self.input_queue.get(timeout=0.1)

                    # Convert to float32 normalized to [-1, 1]
                    audio_array = (
                        np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32)
                        / 32768.0
                    )
                    audio_buffer = np.concatenate([audio_buffer, audio_array])

                    # Process in chunks of the required size
                    while len(audio_buffer) >= vad_chunk_size:
                        # Extract one chunk for VAD processing
                        vad_chunk = audio_buffer[:vad_chunk_size]
                        audio_buffer = audio_buffer[vad_chunk_size:]

                        # Convert to torch tensor
                        import torch

                        audio_tensor = torch.from_numpy(vad_chunk)

                        # Run VAD inference on single chunk
                        with torch.no_grad():
                            speech_prob = self.vad_model(
                                audio_tensor, self.sample_rate
                            ).item()

                        # Determine if user is speaking based on probability
                        current_time = time.time() * 1000  # Convert to milliseconds
                        is_speaking = speech_prob > self.vad_threshold

                        if is_speaking:
                            last_speech_time = current_time
                            # Check if speech duration meets minimum requirement
                            if (
                                current_time - last_silence_time
                                >= self.min_speech_duration_ms
                            ):
                                self._update_volume(True)
                        else:
                            last_silence_time = current_time
                            # Check if silence duration meets minimum requirement
                            if (
                                current_time - last_speech_time
                                >= self.min_silence_duration_ms
                            ):
                                self._update_volume(False)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Warning: Error in VAD thread: {e}")
                import traceback

                traceback.print_exc()
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
            Tuple of (None, pyaudio.paContinue)
        """
        if not self.should_stop.is_set():
            # Send to VAD processing
            if self.input_queue:
                try:
                    self.input_queue.put(in_data, timeout=0.1)
                except queue.Full:
                    pass  # Drop audio if queue is full

            # Send to input callback
            if self.input_callback:
                self.input_callback(in_data)

        return (None, self.pyaudio.paContinue)

    def resume_normal_volume(self) -> None:
        """Resume normal volume (for manual control)."""
        self._update_volume(False)
