import os
import signal
from gpiozero import Button

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# --- Environment Variables ---
agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")

# --- ElevenLabs ---
elevenlabs = ElevenLabs(api_key=api_key)

conversation = Conversation(
    # API client and agent ID.
    elevenlabs,
    agent_id,
    # Assume auth is required when API_KEY is set.
    requires_auth=bool(api_key),
    # Use the default audio interface.
    audio_interface=DefaultAudioInterface(),
    # Simple callbacks that print the conversation to the console.
    callback_agent_response=lambda response: print(f"Agent: {response}"),
    callback_agent_response_correction=lambda original, corrected: print(
        f"Agent: {original} -> {corrected}"
    ),
    callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
    # Uncomment if you want to see latency measurements.
    # callback_latency_measurement=lambda latency: print(f"Latency: {latency}ms"),
)

# from apa102_pi.driver import apa102
# from time import sleep

# --- Button Setup ---
# The button on the ReSpeaker 2-Mics HAT is connected to GPIO17.
button = Button(17)


def on_button_pressed():
    """
    This function will be executed when the button is pressed.
    """
    print("Button was pressed!")


button.when_pressed = on_button_pressed

print("Assistant is running. Waiting for button press...")

# --- LED Example (commented out) ---
# The ReSpeaker 2-Mics HAT has 3 APA102 RGB LEDs.
# You can control them using the 'apa102-pi' library.
# First, you would need to initialize the driver:
# num_leds = 3
# leds = apa102.APA102(num_led_or_strip=num_leds)

# Then you can set the color of each LED.
# For example, to set the first LED to red:
# leds.set_pixel(0, 255, 0, 0)
# leds.show()

# To turn them all off:
# leds.clear_strip()
# leds.cleanup()

# --- Main Loop ---
# The script will pause here and wait for events, like a button press.
# signal.pause()

conversation.start_session()

signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())

conversation_id = conversation.wait_for_session_end()
print(f"Conversation ID: {conversation_id}")
