# Pipeline Orchestration System

A powerful orchestration framework that combines Gemini AI (for planning and decision-making) with Claude AI (for code execution) to automate complex software development workflows.

## 🏗️ Architecture

- **Gemini = BRAIN** 🧠: All decision-making, planning, evaluation, and orchestration
- **Claude = MUSCLE** 💪: Pure execution of coding/file tasks with no decision-making

This separation of concerns ensures that each AI plays to its strengths: Gemini excels at high-level planning and analysis, while Claude excels at detailed code implementation.

## ✨ Key Features

1. **Single Config File**: Complete workflow definition in YAML
2. **Clear Separation**: Gemini decides what to do, Claude executes the work
3. **Sandboxed Execution**: Claude operates in an isolated workspace directory
4. **Parallel Execution**: Multiple Claude tasks can run concurrently
5. **File Output**: All results saved to files for inspection and debugging
6. **Conditional Steps**: Steps can be skipped based on previous results
7. **Checkpointing**: Save/resume workflow state
8. **Token Budget Management**: Fine-grained control over AI response lengths
9. **Debug Logging**: Comprehensive logging of all AI interactions
10. **File Tracking**: Monitor all files created during execution

## 🚀 Quick Start

```bash
# Set up environment
export GEMINI_API_KEY=your_api_key

# Install dependencies
pip install -r requirements.txt

# Run the example workflow
python pipeline.py example_workflow.yaml

# View results and debug information
python view_debug.py -w  # Show all created files with stats
```

## 📁 Project Structure

```
orch/
├── pipeline.py              # Main orchestration engine
├── view_debug.py           # Debug log and output viewer
├── requirements.txt        # Python dependencies
├── example_workflow.yaml   # Example: Calculator implementation
├── example_workflow_v2.yaml # Simplified calculator example
├── test_*.yaml            # Various test workflows
├── outputs/               # Pipeline outputs (auto-created)
├── workspace/             # Claude's sandboxed workspace (auto-created)
└── checkpoints/           # Workflow checkpoints (auto-created)
```

## 🔧 Configuration Structure

```yaml
workflow:
  name: "my_pipeline"
  checkpoint_enabled: true
  workspace_dir: "./workspace"  # Claude's sandboxed directory
  
  defaults:
    gemini_model: "gemini-2.5-flash"  # or gemini-2.5-pro, gemini-2.0-flash-lite
    gemini_token_budget:              # Default token budget for all Gemini steps
      max_output_tokens: 2048
      temperature: 0.7
      top_p: 0.95
      top_k: 40
    claude_output_format: "json"      # or "text", "stream-json"
    output_dir: "./outputs"
    
  steps:
    - name: "step_name"
      type: "gemini"  # or "claude", "parallel_claude"
      role: "brain"   # or "muscle"
      token_budget:   # Override defaults for this step
        max_output_tokens: 4096
        temperature: 0.5
      prompt:
        - type: "static"
          content: "Your prompt here"
        - type: "file"
          path: "input_file.txt"
        - type: "previous_response"
          step: "previous_step_name"
          extract: "optional_field"
      output_to_file: "output.json"
```

## 📝 Prompt Templates

Three types of prompt components can be combined:

- **`static`**: Fixed text content
- **`file`**: Load content from a file
- **`previous_response`**: Use output from a previous step (with optional field extraction)

Example:
```yaml
prompt:
  - type: "static"
    content: "Analyze this code:"
  - type: "file"
    path: "code.py"
  - type: "static"
    content: "\n\nBased on the analysis from step 1:"
  - type: "previous_response"
    step: "analysis_step"
    extract: "issues"  # Optional: extract specific field
```

## 🔨 Claude Options

All Claude CLI options are supported:

```yaml
claude_options:
  print: true                    # Non-interactive mode
  output_format: "json"          # Output format
  max_turns: 15                  # Limit conversation turns
  allowed_tools: ["Write", "Edit", "Read", "Bash"]  # Available tools
  verbose: true                  # Verbose logging
  append_system_prompt: "..."    # Additional system prompt
  cwd: "./workspace"            # Working directory (sandboxing)
```

## 💰 Token Budget Configuration

### Global Token Budget
Set default token limits for all Gemini steps:

```yaml
defaults:
  gemini_token_budget:
    max_output_tokens: 2048  # Maximum tokens in response
    temperature: 0.7         # Controls randomness (0.0-1.0)
    top_p: 0.95             # Nucleus sampling parameter
    top_k: 40               # Top-k sampling parameter
```

### Per-Step Token Budget
Override defaults for specific steps:

```yaml
steps:
  - name: "detailed_analysis"
    type: "gemini"
    token_budget:
      max_output_tokens: 8192  # Need more tokens for detailed output
      temperature: 0.3         # Lower temperature for focused analysis
```

### Token Budget Guidelines

| Use Case | max_output_tokens | temperature | Notes |
|----------|-------------------|-------------|-------|
| Concise summaries | 512-1024 | 0.5-0.7 | Quick responses |
| Detailed plans | 2048-4096 | 0.5-0.7 | Comprehensive analysis |
| Code generation | 4096-8192 | 0.3-0.5 | Precise output |
| Creative tasks | 2048-4096 | 0.8-0.9 | More variation |
| Technical docs | 2048-8192 | 0.1-0.3 | Deterministic |

## 🧪 Example Workflows

### 1. Calculator Implementation (`example_workflow.yaml`)
Full-featured calculator with comprehensive planning:
- Gemini creates detailed implementation plan
- Gemini generates specific coding instructions
- Claude implements all files (with workspace sandboxing)
- Gemini reviews the implementation

### 2. Simplified Calculator (`example_workflow_v2.yaml`)
Streamlined version with better integration:
- Concise planning phase (2048 tokens)
- More implementation turns (15 vs 10)
- Includes bash commands for verification
- Focused on working code

Key differences in v2:
- Shorter, more actionable plans
- Higher turn limit for Claude
- Includes file listing verification
- More pragmatic approach

### 3. Other Test Workflows
- `test_simple.yaml`: Basic Gemini-only workflow
- `test_timing.yaml`: Performance testing
- `test_token_budget.yaml`: Token limit experiments
- `test_gemini_only.yaml`: Gemini-specific features

## 🔍 Debugging and Monitoring

### View Debug Information
```bash
# Show full debug log and outputs
python view_debug.py

# Show only the debug log
python view_debug.py -l

# Show only output files
python view_debug.py -f

# Show workspace files with stats
python view_debug.py -w

# Show paths only (no content)
python view_debug.py -n
```

### Debug Output Includes:
- Complete prompts sent to each AI
- Full responses from both AIs
- Timing information for each call
- Token usage statistics
- File creation details (with -w flag)

## 📊 Output Structure

All outputs are saved to the configured output directory:

```
outputs/
└── calculator/
    ├── plan.json                    # Gemini's plan
    ├── coding_tasks.json            # Detailed instructions
    ├── implementation_result.json   # Claude's execution result
    ├── review_result.json          # Gemini's review
    └── debug_20250628_140606.log  # Complete debug log
```

Workspace files (Claude's sandbox):
```
workspace/
└── calculator/
    ├── __init__.py
    ├── calculator.py
    ├── operations.py
    ├── memory.py
    ├── ui.py
    └── main.py
```

## 🔒 Security & Sandboxing

- Claude operates in a sandboxed `workspace/` directory
- All file operations are restricted to this directory
- Prevents accidental modification of project files
- Configure with `workspace_dir` in workflow config
- Set with `cwd` in claude_options

## 🛠️ Advanced Features

### Parallel Claude Execution
Run multiple Claude instances simultaneously:

```yaml
- name: "parallel_implementation"
  type: "parallel_claude"
  parallel_tasks:
    - id: "backend"
      prompt:
        - type: "static"
          content: "Implement the backend API"
      output_to_file: "backend_result.json"
    - id: "frontend"
      prompt:
        - type: "static"
          content: "Implement the frontend UI"
      output_to_file: "frontend_result.json"
```

### Conditional Steps
Skip steps based on previous results:

```yaml
- name: "fix_errors"
  type: "claude"
  condition: "review_step.needs_fixes"  # Only run if review found issues
  prompt:
    - type: "static"
      content: "Fix the issues identified in the review"
```

### Function Calling (Gemini)
Define custom functions for Gemini to use:

```yaml
gemini_functions:
  evaluate_code:
    description: "Evaluate code quality"
    parameters:
      type: object
      properties:
        quality_score:
          type: number
          description: "Score from 1-10"
        issues:
          type: array
          items:
            type: string
```

## 📋 Requirements

- Python 3.8+
- Claude CLI (configured and authenticated)
- Gemini API key
- Dependencies in requirements.txt:
  - google-generativeai
  - pyyaml
  - asyncio (built-in)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Test with various workflows
4. Submit a pull request

## 📄 License

[Add your license here]

## 🚨 Troubleshooting

### Common Issues

1. **Claude hits turn limit**: Increase `max_turns` in claude_options
2. **Empty Gemini responses**: Increase `max_output_tokens` 
3. **Files created in wrong location**: Check `workspace_dir` and `cwd` settings
4. **Token limit errors**: Reduce prompt size or increase token budget

### Environment Variables
- `GEMINI_API_KEY`: Required for Gemini access
- `CLAUDE_*`: Any Claude CLI environment variables

## 📚 Additional Resources

- [Gemini API Documentation](https://ai.google.dev/)
- [Claude CLI Documentation](https://docs.anthropic.com/)
- [Example Workflows](./examples/)