#!/usr/bin/env python3
"""
Test script using a minimal audio interface similar to ElevenLabs default.
This will help determine if the CFData error is in our custom audio interface or upstream.
"""

import os
import sys
import signal
import threading
import queue
from dotenv import load_dotenv
from elevenlabs.conversational_ai.conversation import AudioInterface

# Load environment variables
load_dotenv(".env.local")

agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")

if not agent_id or not api_key:
    print("Error: AGENT_ID and ELEVENLABS_API_KEY are required")
    sys.exit(1)


# Create a minimal audio interface similar to ElevenLabs default
class MinimalAudioInterface(AudioInterface):
    """Minimal audio interface that mimics ElevenLabs default behavior."""

    def __init__(self):
        try:
            import pyaudio

            self.pyaudio = pyaudio
        except ImportError:
            raise ImportError("PyAudio is required")

        self.p = None
        self.in_stream = None
        self.out_stream = None
        self.input_callback = None
        self.output_thread = None
        self.should_stop = threading.Event()
        self.output_queue = queue.Queue()

    def start(self, input_callback):
        """Start the audio interface."""
        self.input_callback = input_callback

        # Start output thread
        self.output_thread = threading.Thread(target=self._output_thread, daemon=True)
        self.output_thread.start()

        # Initialize PyAudio
        self.p = self.pyaudio.PyAudio()

        # Use standard buffer sizes (not the small ones we were using)
        input_frames = 2048
        output_frames = 1024

        try:
            # Create input stream
            self.in_stream = self.p.open(
                format=self.pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                stream_callback=self._input_callback,
                frames_per_buffer=input_frames,
                start=True,
            )

            # Create output stream
            self.out_stream = self.p.open(
                format=self.pyaudio.paInt16,
                channels=1,
                rate=16000,
                output=True,
                frames_per_buffer=output_frames,
                start=True,
            )

            print("✓ Minimal audio interface started successfully")

        except Exception as e:
            print(f"✗ Error starting minimal audio interface: {e}")
            self.stop()
            raise

    def stop(self):
        """Stop the audio interface."""
        print("Stopping minimal audio interface...")
        self.should_stop.set()

        if self.output_thread and self.output_thread.is_alive():
            self.output_thread.join(timeout=2.0)

        if self.in_stream:
            try:
                self.in_stream.stop_stream()
                self.in_stream.close()
            except:
                pass
            self.in_stream = None

        if self.out_stream:
            try:
                self.out_stream.stop_stream()
                self.out_stream.close()
            except:
                pass
            self.out_stream = None

        if self.p:
            try:
                self.p.terminate()
            except:
                pass
            self.p = None

    def output(self, audio):
        """Output audio data."""
        if not self.should_stop.is_set():
            try:
                self.output_queue.put(audio, timeout=0.1)
            except queue.Full:
                pass  # Drop audio if queue is full

    def interrupt(self):
        """Interrupt audio output."""
        try:
            while True:
                self.output_queue.get(block=False)
        except queue.Empty:
            pass

    def _output_thread(self):
        """Output thread."""
        while not self.should_stop.is_set():
            try:
                audio = self.output_queue.get(timeout=0.25)
                if audio and self.out_stream and not self.should_stop.is_set():
                    try:
                        self.out_stream.write(audio)
                    except Exception as e:
                        print(f"Audio output error: {e}")
                        break
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Unexpected error in output thread: {e}")
                break

    def _input_callback(self, in_data, frame_count, time_info, status):
        """Input callback."""
        if self.input_callback and in_data:
            try:
                self.input_callback(in_data)
            except Exception as e:
                print(f"Input callback error: {e}")
        return (None, self.pyaudio.paContinue)


print("Testing with minimal audio interface...")
print("=" * 60)

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs.conversational_ai.conversation import Conversation

    # Initialize ElevenLabs client
    elevenlabs = ElevenLabs(api_key=api_key)
    print("✓ ElevenLabs client initialized")

    # Create minimal audio interface
    minimal_audio = MinimalAudioInterface()
    print("✓ Minimal audio interface created")

    # Create conversation with minimal audio interface
    conversation = Conversation(
        elevenlabs,
        agent_id,
        requires_auth=bool(api_key),
        audio_interface=minimal_audio,
        callback_agent_response=lambda response: print(f"Agent: {response}"),
        callback_agent_response_correction=lambda original, corrected: print(
            f"Agent: {original} -> {corrected}"
        ),
        callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
    )
    print("✓ Conversation with minimal audio interface created")

    def cleanup_handler(sig, frame):
        """Cleanup handler for graceful shutdown."""
        print("\nShutting down gracefully...")
        try:
            conversation.end_session()
            minimal_audio.stop()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_handler)

    print("Starting conversation session with minimal audio interface...")
    print("Press Ctrl+C to stop")
    print("-" * 60)

    # Start the session
    conversation.start_session()
    print("✓ Session started successfully")

    # Wait for session to end
    conversation_id = conversation.wait_for_session_end()
    print(f"✓ Session ended. Conversation ID: {conversation_id}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
