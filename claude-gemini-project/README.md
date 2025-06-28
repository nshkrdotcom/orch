# Claude Code + Gemini AI Collaboration Demo

This project demonstrates how to orchestrate a collaborative workflow between Claude Code and Google's Gemini AI for iterative code development and improvement.

## Features

- 🤖 **Dual AI Collaboration**: Claude Code generates code, Gemini reviews and suggests improvements
- 🔄 **2-Round Trip Workflow**: Initial solution → Review → Improved solution → Final assessment
- 📋 **Session Management**: Uses proper Claude Code session management for multi-turn conversations
- 🛠️ **Modern Python**: Virtual environments and clean package management
- 💾 **Result Logging**: Saves the complete collaboration session with session IDs

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js (required for Claude Code CLI)
- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`
- API Keys:
  - Claude subscription (or [Anthropic API Key](https://console.anthropic.com/))
  - [Google AI Studio API Key](https://aistudio.google.com/apikey)

### Setup

1. **Run the automated setup:**
   ```bash
   ./setup.sh
   ```

2. **Set your Gemini API key:**
   ```bash
   export GEMINI_API_KEY='your-gemini-api-key'
   ```

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Run the collaboration demo:**
   ```bash
   python main.py
   ```

## How It Works

The demo orchestrates a 2-round collaboration:

1. **Round 1:**
   - Claude Code generates a Python email validation function
   - Gemini reviews the code and suggests improvements

2. **Round 2:**
   - Claude Code incorporates Gemini's feedback using session continuity
   - Gemini provides a final assessment and rating (1-10)

### Technical Approach

- Uses `claude -p --output-format json` for structured responses
- Captures session IDs for multi-turn conversations
- Uses `--resume session_id` for conversation continuity
- Maintains context across rounds for coherent collaboration

## Project Structure

```
claude-gemini-project/
├── setup.sh              # Automated setup script
├── requirements.txt       # Python dependencies (google-genai)
├── main.py               # Main collaboration script
├── README.md             # This documentation
├── venv/                 # Virtual environment (created by setup)
└── collaboration_results.json # Generated session results
```

## Configuration

### Claude Code
- Uses subscription-based authentication (no API key needed)
- JSON output format for structured session management
- Session-based multi-turn conversations

### Gemini AI
- Model: `gemini-2.5-flash-lite-preview-06-17`
- Thinking disabled for faster responses
- Environment variable: `GEMINI_API_KEY`

## Example Output

```
🚀 Claude + Gemini Collaboration Demo (Proper Multi-turn)
🔄 Round 1: Claude creates solution
📋 Session ID: 38fc1006-474d-49a7-a0ab-d1a9bae44e33
🔄 Round 2: Claude improves (continuing session)
🎉 Collaboration Complete!
📊 Final Assessment: Rating: 7/10
💾 Saved to collaboration_results.json
```

## Troubleshooting

- **Claude authentication**: Ensure you're logged into Claude Code CLI
- **Missing Gemini API key**: Set `GEMINI_API_KEY` environment variable
- **Python version**: Requires Python 3.10+
- **Node.js**: Required for Claude Code CLI

## Dependencies

- `google-genai`: Google's Gemini AI SDK
- Claude Code CLI (npm package)
- Python 3.10+ with venv support