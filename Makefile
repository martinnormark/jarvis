# Jarvis Voice Assistant - Development Makefile
# John Carmack-style: minimal, efficient, and reliable

.PHONY: help install install-dev test test-unit test-integration lint format clean build run setup

# Default target
help:
	@echo "Jarvis Voice Assistant - Development Commands"
	@echo "============================================="
	@echo "install      - Install production dependencies"
	@echo "install-dev  - Install development dependencies"
	@echo "test         - Run all tests"
	@echo "test-unit    - Run unit tests only"
	@echo "test-integration - Run integration tests only"
	@echo "lint         - Run linting checks"
	@echo "format       - Format code with black"
	@echo "clean        - Clean build artifacts"
	@echo "build        - Build the package"
	@echo "run          - Run the assistant"
	@echo "setup        - Initial project setup"

# Installation
install:
	uv sync

install-dev:
	uv sync --dev

# Testing
test:
	uv run pytest tests/ -v --cov=jarvis --cov-report=term-missing

test-unit:
	uv run pytest tests/unit/ -v

test-integration:
	uv run pytest tests/integration/ -v

# Code quality
lint:
	uv run flake8 jarvis/ tests/
	uv run mypy jarvis/

format:
	uv run black jarvis/ tests/

# Build and run
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	uv build

run:
	uv run python run.py

# Development setup
setup: install-dev
	@echo "Setting up development environment..."
	@if [ ! -f .env.local ]; then \
		cp env.local.example .env.local; \
		echo "Created .env.local from template. Please edit with your credentials."; \
	fi
	@echo "Development environment ready!"
	@echo "Next steps:"
	@echo "1. Edit .env.local with your ElevenLabs credentials"
	@echo "2. Run 'make test' to verify everything works"
	@echo "3. Run 'make run' to start the assistant"

# Quick development cycle
dev: format lint test

# Release preparation
release: clean format lint test build
	@echo "Release preparation complete!" 