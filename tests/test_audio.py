#!/usr/bin/env python3
"""
Simple audio test script to diagnose PyAudio issues on macOS.
This script tests basic audio input/output functionality without the ElevenLabs integration.
"""

import platform
import time
import sys


def test_pyaudio_installation():
    """Test if PyAudio is properly installed."""
    try:
        import pyaudio

        print("✓ PyAudio is installed")
        return pyaudio
    except ImportError as e:
        print(f"✗ PyAudio import failed: {e}")
        print("Install with: pip install pyaudio")
        return None


def test_audio_devices(pyaudio):
    """Test available audio devices."""
    try:
        p = pyaudio.PyAudio()

        print(f"\nAvailable audio devices:")
        print(f"{'Device ID':<10} {'Name':<30} {'Input':<8} {'Output':<8}")
        print("-" * 60)

        for i in range(p.get_device_count()):
            try:
                device_info = p.get_device_info_by_index(i)
                name = (
                    device_info["name"][:28] + "..."
                    if len(device_info["name"]) > 30
                    else device_info["name"]
                )
                inputs = device_info["maxInputChannels"]
                outputs = device_info["maxOutputChannels"]
                print(f"{i:<10} {name:<30} {inputs:<8} {outputs:<8}")
            except Exception as e:
                print(f"{i:<10} Error getting device info: {e}")

        p.terminate()
        return True
    except Exception as e:
        print(f"✗ Error testing audio devices: {e}")
        return False


def test_audio_streams(pyaudio):
    """Test basic audio input/output streams."""
    try:
        p = pyaudio.PyAudio()

        # Test input stream
        print("\nTesting input stream...")
        try:
            input_stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024,
                start=False,
            )
            print("✓ Input stream created successfully")
            input_stream.close()
        except Exception as e:
            print(f"✗ Input stream creation failed: {e}")
            return False

        # Test output stream
        print("Testing output stream...")
        try:
            output_stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                output=True,
                frames_per_buffer=1024,
                start=False,
            )
            print("✓ Output stream created successfully")
            output_stream.close()
        except Exception as e:
            print(f"✗ Output stream creation failed: {e}")
            return False

        p.terminate()
        return True
    except Exception as e:
        print(f"✗ Error testing audio streams: {e}")
        return False


def test_audio_permissions():
    """Test audio permissions on macOS."""
    if platform.system().lower() == "darwin":
        print("\nOn macOS, please ensure:")
        print("1. Terminal/your IDE has microphone permissions")
        print(
            "   - Go to System Preferences > Security & Privacy > Privacy > Microphone"
        )
        print("   - Add Terminal or your IDE to the list")
        print("2. Audio output is working")
        print("3. No other applications are using the microphone")

        # Try to get default devices
        try:
            import pyaudio

            p = pyaudio.PyAudio()

            default_input = p.get_default_input_device_info()
            default_output = p.get_default_output_device_info()

            print(f"\nDefault input device: {default_input['name']}")
            print(f"Default output device: {default_output['name']}")

            p.terminate()
        except Exception as e:
            print(f"Could not get default devices: {e}")


def main():
    """Main test function."""
    print("Audio Interface Test Script")
    print("=" * 40)
    print(f"Platform: {platform.system()} {platform.release()}")

    # Test PyAudio installation
    pyaudio = test_pyaudio_installation()
    if not pyaudio:
        sys.exit(1)

    # Test audio devices
    if not test_audio_devices(pyaudio):
        sys.exit(1)

    # Test audio streams
    if not test_audio_streams(pyaudio):
        sys.exit(1)

    # Test permissions (macOS specific)
    test_audio_permissions()

    print("\n✓ All basic audio tests passed!")
    print("If you're still having issues, try:")
    print("1. Restarting your terminal/IDE")
    print("2. Checking system audio settings")
    print("3. Running: brew install portaudio")
    print("4. Reinstalling PyAudio: pip uninstall pyaudio && pip install pyaudio")


if __name__ == "__main__":
    main()
