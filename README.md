# jarvis

A voice assistant using ElevenLabs conversational AI with interruptible speech output.

## Features

- **Voice Assistant**: Uses ElevenLabs conversational AI for natural voice interactions
- **Interruptible Speech**: Press the button to interrupt the agent's speech output
- **ReSpeaker 2-Mics HAT Support**: Optimized for Raspberry Pi with ReSpeaker 2-Mics HAT
- **Conversation State Preservation**: Interrupting speech doesn't affect the conversation context
- **Modular Design**: Clean separation of concerns with dedicated audio interface module

## Project Structure

```
jarvis/
├── main.py                           # Main application entry point
├── interruptible_audio_interface.py  # Custom audio interface with interrupt capability
├── test_interrupt.py                 # Test script for interrupt functionality
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:

   ```bash
   export AGENT_ID="your_agent_id"
   export ELEVENLABS_API_KEY="your_api_key"
   ```

3. Run the assistant:
   ```bash
   python main.py
   ```

## Interrupt Functionality

The assistant includes a custom audio interface that allows you to interrupt the agent's speech output while keeping the conversation state intact.

### How it works:

1. **Custom Audio Interface**: The `InterruptibleAudioInterface` class (in `interruptible_audio_interface.py`) extends ElevenLabs' audio interface
2. **Threaded Audio Playback**: Audio is played in a separate thread to allow interruption
3. **Button Integration**: The ReSpeaker button (GPIO17) is connected to interrupt functionality
4. **State Preservation**: The conversation context remains intact when interrupting

### Usage:

- **Start Conversation**: The assistant will begin listening for voice input
- **Interrupt Speech**: Press the button while the agent is speaking to stop the audio output
- **Continue Conversation**: The conversation context is preserved, so you can continue naturally

### Testing:

You can test the interrupt functionality without the full ElevenLabs setup:

```bash
python test_interrupt.py
```

This will play a test tone that can be interrupted to verify the audio interface works correctly.

## Hardware Requirements

- Raspberry Pi (tested with Pi Zero 2 W)
- ReSpeaker 2-Mics Pi HAT
- Speaker or headphones connected to the ReSpeaker HAT

## Troubleshooting

- **Audio Issues**: Ensure your speaker is properly connected to the ReSpeaker HAT
- **Button Not Working**: Check that the ReSpeaker HAT is properly seated on the Raspberry Pi
- **API Errors**: Verify your ElevenLabs API key and agent ID are correctly set

## License

MIT License - see LICENSE file for details.
