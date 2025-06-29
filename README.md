# Pipeline Orchestration System

## Architecture

- **Gemini = BRAIN**: All decision-making, planning, evaluation, and orchestration
- **Claude = MUSCLE**: Pure execution of coding/file tasks with no decision-making

## Key Features

1. **Single Config File**: Complete workflow definition in YAML
2. **Clear Separation**: Gemini decides what to do, Claude executes the work
3. **Parallel Execution**: Multiple Claude tasks can run in parallel
4. **File Output**: All results can be saved to files for inspection
5. **Conditional Steps**: Steps can be skipped based on previous results
6. **Checkpointing**: Save/resume workflow state
7. **Token Budget Management**: Configure token limits and generation parameters for Gemini models

## Configuration Structure

```yaml
workflow:
  name: "my_pipeline"
  checkpoint_enabled: true
  
  defaults:
    gemini_model: "gemini-2.5-flash"  # or gemini-2.5-pro, gemini-2.0-flash, gemini-2.5-flash-lite
    gemini_token_budget:              # Optional: Default token budget for all Gemini steps
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
      token_budget:   # Optional: Override token budget for this step
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

## Prompt Templates

Three types of prompt components:
- `static`: Fixed text content
- `file`: Load content from a file
- `previous_response`: Use output from a previous step

## Claude Options

All Claude CLI options are supported:
- `print`: Run in non-interactive mode
- `output_format`: json, text, or stream-json
- `max_turns`: Limit agentic turns
- `allowed_tools`: Specify allowed tools
- `verbose`: Enable verbose logging
- `append_system_prompt`: Add to system prompt

## Usage

```bash
# Set up environment
export GEMINI_API_KEY=your_api_key

# Install dependencies
pip install -r requirements.txt

# Run a workflow
python pipeline.py example_workflow.yaml
```

## Example Workflow

See `example_workflow.yaml` for a complete example that:
1. Gemini analyzes requirements and creates a plan
2. Gemini generates specific coding instructions
3. Claude executes the coding tasks
4. Gemini reviews the results

## Token Budget Configuration

### Global Token Budget
Set default token limits for all Gemini steps in the `defaults` section:

```yaml
defaults:
  gemini_token_budget:
    max_output_tokens: 2048  # Maximum tokens in response
    temperature: 0.7         # Controls randomness (0.0-1.0)
    top_p: 0.95             # Nucleus sampling parameter
    top_k: 40               # Top-k sampling parameter
```

### Per-Step Token Budget
Override the defaults for specific steps that need different settings:

```yaml
steps:
  - name: "detailed_analysis"
    type: "gemini"
    token_budget:
      max_output_tokens: 8192  # Need more tokens for detailed output
      temperature: 0.3         # Lower temperature for more focused analysis
```

### Use Cases
- **Short responses**: Use lower `max_output_tokens` (512-1024) for concise answers
- **Detailed analysis**: Use higher `max_output_tokens` (4096-8192) for comprehensive outputs
- **Creative tasks**: Use higher `temperature` (0.8-0.9) for more creative responses
- **Technical precision**: Use lower `temperature` (0.1-0.3) for deterministic outputs

See `test_token_budget.yaml` for a complete example demonstrating different token budget configurations.

## Output Structure

All outputs are saved to the configured output directory:
- JSON results from each step
- Combined results from parallel executions
- Checkpoint files for resume capability