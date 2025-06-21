#!/bin/bash

# Jarvis Setup Script
# This script sets up the Jarvis voice assistant with uv package management

set -e

echo "🚀 Setting up Jarvis Voice Assistant..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed"

# Detect platform
PLATFORM=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="mac"
    echo "🖥️  Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Check if we're on Raspberry Pi
    if [[ -f "/proc/device-tree/model" ]]; then
        MODEL=$(cat /proc/device-tree/model | tr '[:upper:]' '[:lower:]')
        if [[ "$MODEL" == *"raspberry pi"* ]]; then
            PLATFORM="pi"
            echo "🍓 Detected Raspberry Pi"
        else
            PLATFORM="linux"
            echo "🐧 Detected Linux"
        fi
    else
        PLATFORM="linux"
        echo "🐧 Detected Linux"
    fi
else
    echo "⚠️  Unknown platform: $OSTYPE"
    PLATFORM="unknown"
fi

# Create virtual environment and install dependencies
echo "📦 Creating virtual environment with uv..."

if [[ "$PLATFORM" == "mac" ]]; then
    echo "Installing dependencies for macOS..."
    uv sync --extra mac
elif [[ "$PLATFORM" == "pi" ]]; then
    echo "Installing dependencies for Raspberry Pi..."
    uv sync --extra pi
else
    echo "Installing base dependencies..."
    uv sync
fi

echo "✅ Dependencies installed successfully!"

# Setup environment file for Mac
if [[ "$PLATFORM" == "mac" ]]; then
    echo "🔧 Setting up environment configuration for macOS..."
    
    if [[ ! -f ".env.local" ]]; then
        if [[ -f "env.local.example" ]]; then
            echo "📝 Creating .env.local from template..."
            cp env.local.example .env.local
            echo "✅ Created .env.local - please edit it with your actual credentials"
        else
            echo "📝 Creating .env.local template..."
            cat > .env.local << EOF
# ElevenLabs Configuration
# Fill in your actual values below

# Your ElevenLabs Agent ID
AGENT_ID=your-agent-id-here

# Your ElevenLabs API Key
ELEVENLABS_API_KEY=your-api-key-here
EOF
            echo "✅ Created .env.local - please edit it with your actual credentials"
        fi
    else
        echo "✅ .env.local already exists"
    fi
fi

# Check for required environment variables
echo "🔧 Checking environment variables..."

if [[ -z "$AGENT_ID" ]]; then
    if [[ "$PLATFORM" == "mac" ]]; then
        echo "⚠️  AGENT_ID not set - please edit .env.local with your agent ID"
    else
        echo "⚠️  AGENT_ID environment variable is not set"
        echo "   You can set it with: export AGENT_ID='your-agent-id'"
    fi
fi

if [[ -z "$ELEVENLABS_API_KEY" ]]; then
    if [[ "$PLATFORM" == "mac" ]]; then
        echo "⚠️  ELEVENLABS_API_KEY not set - please edit .env.local with your API key"
    else
        echo "⚠️  ELEVENLABS_API_KEY environment variable is not set"
        echo "   You can set it with: export ELEVENLABS_API_KEY='your-api-key'"
    fi
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run Jarvis:"
echo "   uv run python main.py"
echo ""
echo "To activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "For development:"
echo "   uv run --dev python main.py" 