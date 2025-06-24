"""
Unit tests for VolumeReducingAudioInterface.
"""

import pytest
import struct
import time
from unittest.mock import Mock, patch
from jarvis.audio.interface import VolumeReducingAudioInterface


class TestVolumeReducingAudioInterface:
    """Test cases for VolumeReducingAudioInterface class."""

    def test_initialization(self):
        """Test creating a VolumeReducingAudioInterface with valid parameters."""
        with patch("pyaudio.PyAudio") as mock_pyaudio:
            interface = VolumeReducingAudioInterface(
                sample_rate=16000,
                input_frames=2048,
                output_frames=1024,
                volume_reduction_factor=0.3,
                fade_duration_ms=100,
            )

            assert interface.sample_rate == 16000
            assert interface.input_frames == 2048
            assert interface.output_frames == 1024
            assert interface.volume_reduction_factor == 0.3
            assert interface.fade_duration_ms == 100
            assert not interface._is_interrupted
            assert interface._current_volume == 1.0

    def test_volume_reduction_factor_clamping(self):
        """Test that volume reduction factor is clamped to valid range."""
        with patch("pyaudio.PyAudio") as mock_pyaudio:
            # Test values below 0.0
            interface = VolumeReducingAudioInterface(volume_reduction_factor=-0.5)
            assert interface.volume_reduction_factor == 0.0

            # Test values above 1.0
            interface = VolumeReducingAudioInterface(volume_reduction_factor=1.5)
            assert interface.volume_reduction_factor == 1.0

            # Test valid values
            interface = VolumeReducingAudioInterface(volume_reduction_factor=0.5)
            assert interface.volume_reduction_factor == 0.5

    def test_interrupt_sets_state(self):
        """Test that interrupt() sets the interrupted state."""
        with patch("pyaudio.PyAudio") as mock_pyaudio:
            interface = VolumeReducingAudioInterface()

            assert not interface._is_interrupted
            interface.interrupt()
            assert interface._is_interrupted
            assert interface._interrupt_start_time > 0

    def test_apply_volume_reduction_no_interrupt(self):
        """Test that volume reduction is not applied when not interrupted."""
        with patch("pyaudio.PyAudio") as mock_pyaudio:
            interface = VolumeReducingAudioInterface()

            # Create test audio data (16-bit PCM)
            original_audio = struct.pack("<4h", 1000, 2000, -1000, -2000)

            # Apply volume reduction when not interrupted
            result = interface._apply_volume_reduction(original_audio)

            # Should return original audio unchanged
            assert result == original_audio

    def test_apply_volume_reduction_with_interrupt(self):
        """Test that volume reduction is applied when interrupted."""
        with patch("pyaudio.PyAudio") as mock_pyaudio:
            interface = VolumeReducingAudioInterface(volume_reduction_factor=0.5)

            # Set interrupted state
            interface._is_interrupted = True
            interface._interrupt_start_time = time.time() - 0.2  # 200ms ago

            # Create test audio data (16-bit PCM)
            original_audio = struct.pack("<4h", 1000, 2000, -1000, -2000)

            # Apply volume reduction
            result = interface._apply_volume_reduction(original_audio)

            # Should return reduced volume audio
            assert result != original_audio

            # Unpack and verify values are reduced
            original_values = struct.unpack("<4h", original_audio)
            result_values = struct.unpack("<4h", result)

            for orig, reduced in zip(original_values, result_values):
                assert abs(reduced) <= abs(orig)
                assert abs(reduced) == abs(orig) * 0.5

    def test_apply_volume_reduction_fade_progress(self):
        """Test that volume reduction fades in over time."""
        with patch("pyaudio.PyAudio") as mock_pyaudio:
            interface = VolumeReducingAudioInterface(
                volume_reduction_factor=0.0,  # Complete silence
                fade_duration_ms=1000,  # 1 second fade
            )

            # Set interrupted state
            interface._is_interrupted = True
            interface._interrupt_start_time = (
                time.time() - 0.5
            )  # 500ms ago (50% through fade)

            # Create test audio data
            original_audio = struct.pack("<2h", 1000, -1000)

            # Apply volume reduction
            result = interface._apply_volume_reduction(original_audio)

            # Should be partially reduced (around 50% volume)
            original_values = struct.unpack("<2h", original_audio)
            result_values = struct.unpack("<2h", result)

            for orig, reduced in zip(original_values, result_values):
                # Should be reduced but not completely silent
                assert abs(reduced) < abs(orig)
                assert abs(reduced) > 0

    def test_resume_normal_volume(self):
        """Test that resume_normal_volume() restores normal state."""
        with patch("pyaudio.PyAudio") as mock_pyaudio:
            interface = VolumeReducingAudioInterface()

            # Set interrupted state
            interface._is_interrupted = True
            interface._current_volume = 0.5

            # Resume normal volume
            interface.resume_normal_volume()

            assert not interface._is_interrupted
            assert interface._current_volume == 1.0

    def test_force_interrupt_calls_interrupt(self):
        """Test that force_interrupt() calls interrupt()."""
        with patch("pyaudio.PyAudio") as mock_pyaudio:
            interface = VolumeReducingAudioInterface()

            # Mock the interrupt method
            interface.interrupt = Mock()

            # Call force_interrupt
            interface.force_interrupt()

            # Verify interrupt was called
            interface.interrupt.assert_called_once()

    def test_clear_audio_buffer(self):
        """Test that clear_audio_buffer() clears the output queue."""
        with patch("pyaudio.PyAudio") as mock_pyaudio:
            interface = VolumeReducingAudioInterface()

            # Mock the output queue
            mock_queue = Mock()
            interface.output_queue = mock_queue

            # Mock queue.get to raise Empty after first call
            from queue import Empty

            mock_queue.get.side_effect = [b"test", Empty()]

            # Call clear_audio_buffer
            interface.clear_audio_buffer()

            # Verify queue.get was called
            assert mock_queue.get.call_count >= 1
