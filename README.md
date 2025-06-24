# Jarvis - Voice Assistant with Volume-Reducing Audio

A voice assistant built with ElevenLabs Conversational AI that supports intelligent audio interruption. Works on both macOS and Raspberry Pi with platform-specific input methods.

## Features

- 🎤 **Real-time Voice Interaction**: Seamless conversation with ElevenLabs AI agents
- 🔊 **Volume-Reducing Interruption**: Reduces agent audio volume instead of stopping it completely
- 🎵 **Smooth Audio Transitions**: Configurable fade duration for natural audio experience
- 🖥️ **Cross-Platform**: Works on macOS (spacebar) and Raspberry Pi (GPIO button)
- 🔧 **Modern Development**: Uses `uv` for fast Python package management
- 🎯 **Platform Detection**: Automatically detects and configures for your platform
- 🔐 **Secure Configuration**: Environment variables loaded from `.env.local` on Mac
- 🧪 **Comprehensive Testing**: Full test suite with unit and integration tests
- 📦 **Clean Architecture**: Well-structured, maintainable codebase

## Audio Interface Comparison

### Old InterruptibleAudioInterface ❌

- Clears audio buffer completely when interrupted
- Agent stops speaking immediately
- User loses context of what agent was saying
- Abrupt interruption experience

### New VolumeReducingAudioInterface ✅

- Reduces volume to 30% (configurable) when interrupted
- Agent continues speaking at lower volume
- User can still hear and understand the agent
- Smooth fade transition (150ms configurable)
- Volume automatically restores when user speaks
- Maintains conversation context

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

### Testing the New Audio Interface

```bash
# Run the demonstration script
python demo_volume_reducing_audio.py

# Run the test script
python tests/test_volume_reducing_audio.py
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

## Testing

The project includes a comprehensive test suite:

```bash
# Run all tests with coverage
make test

# Run specific test categories
make test-unit
make test-integration

# Run volume reducing audio tests specifically
python -m pytest tests/unit/test_volume_reducing_audio.py -v

# Run tests with specific markers
uv run pytest -m "not slow"
uv run pytest -m integration
```

## Code Quality

The project uses several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pre-commit**: Automated quality checks

```bash
# Run all quality checks
make lint

# Format code
make format

# Install pre-commit hooks
uv run pre-commit install
```

## Troubleshooting

### Common Issues

1. **"keyboard package not installed"** (macOS):

   ```bash
   make install-dev
   ```

2. **"gpiozero package not installed"** (Raspberry Pi):

   ```bash
   make install-dev
   ```

3. **Audio issues**:

   - Ensure your microphone and speakers are properly connected
   - Check system audio permissions
   - On macOS, grant microphone access to Terminal/your IDE

4. **Permission errors on Raspberry Pi**:

   ```bash
   sudo usermod -a -G gpio $USER
   # Then log out and back in
   ```

5. **Environment variables not loading** (macOS):

   - Check that `.env.local` exists and has the correct format
   - Ensure no spaces around the `=` sign in `.env.local`
   - Restart the application after editing `.env.local`

6. **Volume reduction not working**:
   - Check that you're using the `VolumeReducingAudioInterface`
   - Verify the volume reduction factor is between 0.0 and 1.0
   - Ensure the fade duration is reasonable (50-500ms recommended)

### Platform Detection

The system automatically detects your platform:

- **macOS**: Detected as "mac"
- **Raspberry Pi**: Detected as "pi" (checks `/proc/device-tree/model`)
- **Other Linux**: Detected as "linux"

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run quality checks: `make dev`
5. Submit a pull request

### Development Workflow

```bash
# 1. Setup development environment
make setup

# 2. Make your changes
# ... edit code ...

# 3. Run quality checks
make dev

# 4. Run tests
make test

# 5. Commit your changes
git add .
git commit -m "Your commit message"
```

## Security Notes

- The `.env.local` file is automatically added to `.gitignore`
- Never commit your actual API keys to version control
- The `env.local.example` file shows the required format without real credentials

## License

MIT License - see LICENSE file for details.
