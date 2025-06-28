#!/bin/bash

# Claude Code + Gemini AI Project Setup Script
set -e

echo "Setting up Claude Code + Gemini AI project..."

# Check if Python 3.10+ is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "Error: Python 3.10+ is required. Found version: $python_version"
    exit 1
fi

echo "✓ Python $python_version detected"

# Check if Node.js is available (required for Claude Code)
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required for Claude Code but not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✓ Node.js $(node --version) detected"

# Check if Claude Code CLI is installed
if ! command -v claude &> /dev/null; then
    echo "Installing Claude Code CLI globally..."
    npm install -g @anthropic-ai/claude-code
else
    echo "✓ Claude Code CLI already installed"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To get started:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Set your API keys:"
echo "   export ANTHROPIC_API_KEY='your-anthropic-api-key'"
echo "   export GEMINI_API_KEY='your-gemini-api-key'"
echo "3. Run the demo: python main.py"
echo ""
echo "Make sure you have valid API keys from:"
echo "- Anthropic Console: https://console.anthropic.com/"
echo "- Google AI Studio: https://aistudio.google.com/apikey"