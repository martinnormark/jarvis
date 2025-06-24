# Jarvis - Voice Assistant with Intelligent Audio Interfaces

A voice assistant built with ElevenLabs Conversational AI that supports multiple intelligent audio interruption methods. Works on both macOS and Raspberry Pi with platform-specific input methods.

## Features

- 🎤 **Real-time Voice Interaction**: Seamless conversation with ElevenLabs AI agents
- 🤖 **Multiple Audio Interfaces**: Choose from manual interruption, volume reduction, or automatic VAD
- 🔊 **Volume-Reducing Interruption**: Reduces agent audio volume instead of stopping it completely
- 🎵 **Smooth Audio Transitions**: Configurable fade duration for natural audio experience
- 🎯 **Automatic Voice Detection**: Silero VAD automatically detects when you're speaking
- 🖥️ **Cross-Platform**: Works on macOS (spacebar) and Raspberry Pi (GPIO button)
- 🔧 **Modern Development**: Uses `uv` for fast Python package management
- 🎯 **Platform Detection**: Automatically detects and configures for your platform
- 🔐 **Secure Configuration**: Environment variables loaded from `.env.local` on Mac
- 🧪 **Comprehensive Testing**: Full test suite with unit and integration tests
- 📦 **Clean Architecture**: Well-structured, maintainable codebase

## Audio Interface Comparison

### InterruptibleAudioInterface ❌

- Manual interruption required (button press)
- Clears audio buffer completely when interrupted
- Agent stops speaking immediately
- User loses context of what agent was saying
- Abrupt interruption experience

### VolumeReducingAudioInterface ✅

- Manual interruption required (button press)
- Reduces volume to 30% (configurable) when interrupted
- Agent continues speaking at lower volume
- User can still hear and understand the agent
- Smooth fade transition (150ms configurable)
- Volume automatically restores when user speaks
- Maintains conversation context

### SileroVADAudioInterface 🚀

- **Automatic voice activity detection** - no manual interruption needed
- Uses local Silero VAD model for real-time speech detection
- Reduces volume when user speaks, restores when they stop
- Works with 6000+ languages
- Real-time processing (<1ms per chunk)
- Configurable sensitivity and timing parameters
- Most natural conversation experience

## Quick Start

### Prerequisites

1. **Install uv** (fast Python package manager):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up environment variables**:

   **On macOS**: The setup script will create a `.env.local` file for you to edit:

   ```bash
   # Edit .env.local with your credentials
   AGENT_ID=your-elevenlabs-agent-id
   ELEVENLABS_API_KEY=your-elevenlabs-api-key
   ```

   **On Raspberry Pi**: Set environment variables in your shell:

   ```bash
   export AGENT_ID="your-elevenlabs-agent-id"
   export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
   ```

### Installation

1. **Clone the repository**:

   ```bash
   git clone <your-repo-url>
   cd jarvis
   ```

2. **Run the setup script**:

   ```bash
   make setup
   ```

   This will automatically:

   - Detect your platform (macOS or Raspberry Pi)
   - Install the appropriate dependencies
   - Set up the virtual environment
   - Create `.env.local` template on macOS

3. **Configure your credentials** (macOS only):
   ```bash
   # Edit the .env.local file with your actual credentials
   nano .env.local
   ```

### Running Jarvis

```bash
# Run with make (recommended)
make run

# Or run directly
uv run python run.py

# Or use the CLI
uv run jarvis
```

### Testing the Audio Interfaces

```bash
# Test the volume reducing audio interface
python demo_volume_reducing_audio.py

# Test the Silero VAD audio interface
python demo_silero_vad_audio.py

# Run the test scripts
python tests/test_volume_reducing_audio.py
python tests/test_silero_vad_audio.py
```

## Platform-Specific Features

### macOS

- **Input Method**: Press **SPACEBAR** to reduce agent audio volume
- **Dependencies**: Automatically installs `keyboard` and `python-dotenv` libraries
- **Configuration**: Uses `.env.local` file for secure credential storage

### Raspberry Pi

- **Input Method**: Press **GPIO17 button** to reduce agent audio volume
- **Dependencies**: Automatically installs `gpiozero`, `RPi.GPIO`, and `apa102-pi`
- **Hardware**: Compatible with ReSpeaker 2-Mics HAT

## Development

### Project Structure

```
jarvis/
├── jarvis/                    # Main package
│   ├── __init__.py           # Package initialization
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   ├── assistant.py      # Main assistant class
│   │   └── config.py         # Configuration management
│   ├── audio/                # Audio interface
│   │   ├── __init__.py
│   │   └── interface.py      # Audio interfaces (VolumeReducing + Interruptible)
│   ├── platforms/            # Platform-specific code
│   │   ├── __init__.py
│   │   ├── detector.py       # Platform detection
│   │   └── handlers.py       # Input handlers
│   └── cli/                  # Command-line interface
│       ├── __init__.py
│       └── main.py           # CLI entry point
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest configuration
│   ├── unit/                 # Unit tests
│   │   └── test_volume_reducing_audio.py  # Volume reducing audio tests
│   └── integration/          # Integration tests
├── demo_volume_reducing_audio.py  # Demonstration script
├── pyproject.toml            # Project configuration
├── Makefile                  # Development tasks
├── run.py                    # Simple entry point
├── setup.sh                  # Automated setup script
├── env.local.example         # Example environment file
└── README.md                 # This file
```

### Development Commands

```bash
# Install development dependencies
make install-dev

# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Format code
make format

# Lint code
make lint

# Full development cycle (format + lint + test)
make dev

# Clean build artifacts
make clean

# Build package
make build

# Run the assistant
make run
```

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add platform-specific dependency
uv add --extra mac package-name    # macOS only
uv add --extra pi package-name     # Raspberry Pi only

# Add development dependency
uv add --dev package-name
```

## Configuration

### Environment Variables

The application looks for these environment variables:

- `AGENT_ID`: Your ElevenLabs agent ID
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key

### Platform-Specific Configuration

**macOS**:

- Environment variables are loaded from `.env.local` file
- The setup script creates a template for you to fill in
- File is automatically ignored by git for security

**Raspberry Pi**:

- Environment variables must be set in the shell session
- Use `export` commands or add to your shell profile

### Audio Settings

The audio interface is configured for:

- **Sample Rate**: 16kHz
- **Channels**: Mono
- **Format**: 16-bit PCM
- **Input Buffer**: 250ms (4000 frames)
- **Output Buffer**: 62.5ms (1000 frames)

### Volume Reducing Audio Interface Settings

The `VolumeReducingAudioInterface` can be customized with:

- **Volume Reduction Factor**: 0.0-1.0 (default: 0.2 = 20% volume)
- **Fade Duration**: Milliseconds for volume transition (default: 100ms)

Example configuration:

```python
audio_interface = VolumeReducingAudioInterface(
    volume_reduction_factor=0.3,  # Reduce to 30% volume
    fade_duration_ms=150,         # 150ms fade duration
)
```

### Silero VAD Audio Interface Settings

The `SileroVADAudioInterface` provides automatic voice activity detection with configurable parameters:

- **Volume Reduction Factor**: 0.0-1.0 (default: 0.2 = 20% volume when user speaks)
- **VAD Threshold**: 0.0-1.0 (default: 0.5 = speech detection sensitivity)
- **Min Speech Duration**: Milliseconds (default: 250ms = minimum speech to trigger reduction)
- **Min Silence Duration**: Milliseconds (default: 100ms = minimum silence to restore volume)
- **Sample Rate**: 8000 or 16000 Hz (default: 16000 Hz)
- **Voice Activity Callback**: Optional callback function called when user speaking state changes

Example configuration:

```python
def voice_activity_callback(is_speaking: bool):
    """Callback function to log voice activity detection."""
    timestamp = time.strftime("%H:%M:%S")
    if is_speaking:
        print(f"🎤 [{timestamp}] User started speaking - Volume reduced")
    else:
        print(f"🔇 [{timestamp}] User stopped speaking - Volume restored")

audio_interface = SileroVADAudioInterface(
    sample_rate=16000,              # Silero VAD supports 8000 or 16000 Hz
    volume_reduction_factor=0.2,    # Reduce to 20% volume when user speaks
    vad_threshold=0.5,              # VAD sensitivity (0.0-1.0)
    min_speech_duration_ms=250,     # Minimum speech duration to trigger reduction
    min_silence_duration_ms=100,    # Minimum silence duration to restore volume
    voice_activity_callback=voice_activity_callback,  # Log voice activity
)
```

**VAD Threshold Guidelines**:

- `0.0-0.3`: Very sensitive (may trigger on background noise)
- `0.3-0.7`: Balanced (recommended for most use cases)
- `0.7-1.0`: Less sensitive (requires louder speech)
