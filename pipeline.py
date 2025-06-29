#!/usr/bin/env python3
"""
Pipeline Orchestration System
- Gemini = BRAIN: All decision-making, planning, evaluation
- Claude = MUSCLE: Pure execution of coding/file tasks, no decisions
"""

import yaml
import json
import asyncio
import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import time

try:
    import google.generativeai as genai
    from google.generativeai.types import FunctionDeclaration, Tool
    from google.generativeai import GenerationConfig
except ImportError:
    print("Error: google-generativeai not installed")
    print("Please run: pip install google-generativeai")
    sys.exit(1)

@dataclass
class StepResult:
    step_name: str
    result: Any
    timestamp: datetime
    model_used: str
    
class PipelineOrchestrator:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.results: Dict[str, StepResult] = {}
        self.checkpoint_dir = Path(self.config['workflow'].get('checkpoint_dir', './checkpoints'))
        self.output_dir = Path(self.config['workflow']['defaults'].get('output_dir', './outputs'))
        self.workspace_dir = Path(self.config['workflow'].get('workspace_dir', './workspace'))
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create workspace directory if specified
        if 'workspace_dir' in self.config['workflow']:
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created workspace directory: {self.workspace_dir}")
            
        # Create debug log file
        self.debug_log_path = self.output_dir / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self._log_debug(f"Pipeline started: {self.config['workflow']['name']}")
        self._log_debug(f"Config: {config_path}")
        
        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("Error: GEMINI_API_KEY environment variable not set")
            print("Please run: export GEMINI_API_KEY=your_api_key")
            sys.exit(1)
        genai.configure(api_key=api_key)
        print(f"✅ Debug: Gemini API configured successfully")
        
    def _load_config(self, path: str) -> dict:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
            
    def _build_prompt(self, prompt_config: List[Dict], context: Dict[str, Any]) -> str:
        """Build prompt from template configuration"""
        prompt_parts = []
        
        for part in prompt_config:
            if part['type'] == 'static':
                prompt_parts.append(part['content'])
            elif part['type'] == 'file':
                with open(part['path'], 'r') as f:
                    prompt_parts.append(f.read())
            elif part['type'] == 'previous_response':
                step_name = part['step']
                if step_name in self.results:
                    result = self.results[step_name].result
                    if 'extract' in part:
                        # Extract specific field from result
                        result = result.get(part['extract'], result)
                    prompt_parts.append(str(result))
                    
        return '\n'.join(prompt_parts)
        
    def _save_to_file(self, filename: str, data: Any):
        """Save results to output file"""
        filepath = self.output_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            if isinstance(data, dict) or isinstance(data, list):
                json.dump(data, f, indent=2)
            else:
                f.write(str(data))
        print(f"📁 Saved output to: {filepath}")
        
    def _log_debug(self, message: str):
        """Append message to debug log file"""
        timestamp = datetime.now().isoformat()
        with open(self.debug_log_path, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
        
    def _make_gemini_call(self, model, prompt):
        """Helper method to make actual Gemini API call with detailed logging"""
        # print(f"🔍 Debug: Inside _make_gemini_call at {datetime.now().isoformat()}")
        # print(f"🔍 Debug: About to call model.generate_content...")
        # print(f"🔍 Debug: Model object: {model}")
        # print(f"🔍 Debug: Model type: {type(model)}")
        
        # Show prompt preview
        prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
        print(f"📝 Prompt preview: {prompt_preview}")
        
        try:
            # print(f"🔍 Debug: Executing model.generate_content() NOW...")
            start_time = time.time()
            response = model.generate_content(prompt)
            elapsed_time = time.time() - start_time
            # print(f"🔍 Debug: model.generate_content() returned successfully")
            # print(f"🔍 Debug: Response type: {type(response)}")
            
            # Show raw response
            print(f"📤 Raw Gemini response (took {elapsed_time:.2f}s):")
            if hasattr(response, 'candidates') and response.candidates:
                for i, candidate in enumerate(response.candidates):
                    finish_reason_map = {
                        1: "STOP (normal completion)",
                        2: "MAX_TOKENS (hit token limit)",
                        3: "SAFETY",
                        4: "RECITATION",
                        5: "OTHER"
                    }
                    reason_text = finish_reason_map.get(candidate.finish_reason, f"UNKNOWN ({candidate.finish_reason})")
                    print(f"  Candidate {i}: finish_reason={reason_text}")
                    if hasattr(candidate.content, 'parts'):
                        for j, part in enumerate(candidate.content.parts):
                            if hasattr(part, 'text'):
                                print(f"    Part {j} (text): {part.text[:100]}..." if len(part.text) > 100 else f"    Part {j} (text): {part.text}")
                            elif hasattr(part, 'function_call'):
                                print(f"    Part {j} (function_call): name={part.function_call.name}, args={part.function_call.args}")
            else:
                print(f"  Response object: {response}")
            
            return response
        except Exception as e:
            print(f"❌ Debug: Exception in _make_gemini_call: {e}")
            print(f"❌ Debug: Exception type in helper: {type(e)}")
            raise
        
    async def _run_gemini_step(self, step: Dict) -> Any:
        """Execute Gemini BRAIN step - all decision making"""
        print(f"🧠 Gemini Brain processing: {step.get('role', 'decision')}")
        # print(f"🔍 Debug: Step config: {step}")
        
        model_name = step.get('model', self.config['workflow']['defaults']['gemini_model'])
        # print(f"🔍 Debug: Using model: {model_name}")
        
        # Get token budget configuration
        token_budget = {}
        # First check for default token budget
        if 'gemini_token_budget' in self.config['workflow']['defaults']:
            token_budget = self.config['workflow']['defaults']['gemini_token_budget'].copy()
        # Then override with step-specific token budget if present
        if 'token_budget' in step:
            token_budget.update(step['token_budget'])
        
        # Prepare generation config from token budget
        generation_config = {}
        if 'max_output_tokens' in token_budget:
            generation_config['max_output_tokens'] = token_budget['max_output_tokens']
        if 'temperature' in token_budget:
            generation_config['temperature'] = token_budget['temperature']
        if 'top_p' in token_budget:
            generation_config['top_p'] = token_budget['top_p']
        if 'top_k' in token_budget:
            generation_config['top_k'] = token_budget['top_k']
        
        if generation_config:
            print(f"📊 Token budget: max_output_tokens={generation_config.get('max_output_tokens', 'default')}, "
                  f"temperature={generation_config.get('temperature', 'default')}")
        
        try:
            model = genai.GenerativeModel(
                model_name,
                generation_config=genai.GenerationConfig(**generation_config) if generation_config else None
            )
            # print(f"🔍 Debug: Model initialized successfully")
        except Exception as e:
            print(f"❌ Debug: Model initialization failed: {e}")
            raise
        
        # Build prompt
        # print(f"🔍 Debug: Building prompt...")
        prompt = self._build_prompt(step['prompt'], self.results)
        print(f"🖓 Input context length: {len(prompt)} characters")
        # print(f"🔍 Debug: Prompt built, length: {len(prompt)} chars")
        # print(f"🔍 Debug: Prompt preview: {prompt[:200]}...")
        
        # Add function calling if specified
        # print(f"🔍 Debug: Checking for functions in step...")
        # print(f"🔍 Debug: Step keys: {list(step.keys())}")
        # print(f"🔍 Debug: 'functions' in step: {'functions' in step}")
        
        if 'functions' in step:
            print(f"🔍 Debug: Found functions: {step['functions']}")
            tools = []
            for func_name in step['functions']:
                if func_name in self.config['workflow'].get('gemini_functions', {}):
                    func_def = self.config['workflow']['gemini_functions'][func_name]
                    print(f"🔍 Debug: Adding function: {func_name}")
                    func_decl = FunctionDeclaration(
                        name=func_name,
                        description=func_def.get('description', ''),
                        parameters=func_def.get('parameters', {})
                    )
                    tools.append(Tool(function_declarations=[func_decl]))
            
            print(f"🔍 Debug: Calling Gemini with {len(tools)} tools...")
            print(f"🔍 Debug: LLM call type: SYNCHRONOUS")
            max_tokens = generation_config.get('max_output_tokens', 'default') if generation_config else 'default'
            print(f"🚀 Debug: Starting LLM call to Gemini ({model_name}, max_tokens: {max_tokens}) with tools NOW at {datetime.now().isoformat()}")
            
            # Show prompt preview
            prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
            print(f"📝 Prompt preview: {prompt_preview}")
            self._log_debug(f"Gemini prompt (with tools):\n{prompt}\n")
            
            try:
                start_time = time.time()
                response = model.generate_content(
                    prompt,
                    tools=tools if tools else None
                )
                elapsed_time = time.time() - start_time
                print(f"🔍 Debug: Gemini response received with tools at {datetime.now().isoformat()}")
                
                # Show raw response
                print(f"📤 Raw Gemini response (took {elapsed_time:.2f}s):")
                self._log_debug(f"Gemini response with tools (took {elapsed_time:.2f}s):")
                if hasattr(response, 'candidates') and response.candidates:
                    for i, candidate in enumerate(response.candidates):
                        finish_reason_map = {
                            1: "STOP (normal completion)",
                            2: "MAX_TOKENS (hit token limit)",
                            3: "SAFETY",
                            4: "RECITATION",
                            5: "OTHER"
                        }
                        reason_text = finish_reason_map.get(candidate.finish_reason, f"UNKNOWN ({candidate.finish_reason})")
                        print(f"  Candidate {i}: finish_reason={reason_text}")
                        if hasattr(candidate.content, 'parts'):
                            for j, part in enumerate(candidate.content.parts):
                                if hasattr(part, 'text'):
                                    print(f"    Part {j} (text): {part.text[:100]}..." if len(part.text) > 100 else f"    Part {j} (text): {part.text}")
                                    self._log_debug(f"Response text:\n{part.text}\n")
                                elif hasattr(part, 'function_call'):
                                    print(f"    Part {j} (function_call): name={part.function_call.name}, args={part.function_call.args}")
                                    self._log_debug(f"Function call: {part.function_call.name}, args: {part.function_call.args}")
                else:
                    print(f"  Response object: {response}")
                    self._log_debug(f"Response object: {response}")
            except Exception as e:
                print(f"❌ Debug: Gemini call with tools failed at {datetime.now().isoformat()}: {e}")
                print(f"❌ Debug: Exception type: {type(e)}")
                print(f"❌ Debug: Full exception details: {repr(e)}")
                import traceback
                print(f"❌ Debug: Traceback:\n{traceback.format_exc()}")
                raise
        else:
            print(f"🔍 Debug: Calling Gemini without tools...")
            print(f"🔍 Debug: LLM call type: SYNCHRONOUS (wrapped in async executor)")
            max_tokens = generation_config.get('max_output_tokens', 'default') if generation_config else 'default'
            start_time = time.time()
            print(f"🚀 Debug: Starting LLM call to Gemini ({model_name}, max_tokens: {max_tokens}) NOW at {datetime.now().isoformat()}")
            try:
                # Add timeout protection
                # print(f"🔍 Debug: Creating executor task...")
                response = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: self._make_gemini_call(model, prompt)
                    ),
                    timeout=30.0  # 30 second timeout
                )
                elapsed_time = time.time() - start_time
                # print(f"🔍 Debug: Gemini response received without tools at {datetime.now().isoformat()}")
            except asyncio.TimeoutError:
                print(f"❌ Debug: Gemini call timed out after 30 seconds at {datetime.now().isoformat()}")
                raise Exception("Gemini API call timed out")
            except Exception as e:
                print(f"❌ Debug: Gemini call failed at {datetime.now().isoformat()}: {e}")
                print(f"❌ Debug: Exception type: {type(e)}")
                print(f"❌ Debug: Full exception details: {repr(e)}")
                import traceback
                print(f"❌ Debug: Traceback:\n{traceback.format_exc()}")
                raise
            
        # Parse function calls if present
        result = {}
        # print(f"🔍 Debug: Parsing response...")
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        print(f"🔍 Debug: Found function call: {part.function_call.name}")
                        print(f"🔍 Debug: Function args type: {type(part.function_call.args)}")
                        print(f"🔍 Debug: Function args value: {part.function_call.args}")
                        
                        # Handle None args case
                        args = {}
                        if part.function_call.args is not None:
                            args = dict(part.function_call.args)
                        
                        result = {
                            'function_call': part.function_call.name,
                            'args': args,
                            'text': response.text if hasattr(response, 'text') else ''
                        }
                        break
                        
        if not result:
            # Try to get text from response
            try:
                result = {'text': response.text}
            except Exception as e:
                print(f"⚠️ Debug: Could not get text from response: {e}")
                # Fallback: try to extract text from parts
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate.content, 'parts'):
                        text_parts = []
                        for part in candidate.content.parts:
                            if hasattr(part, 'text'):
                                text_parts.append(part.text)
                        result = {'text': ' '.join(text_parts)}
                    else:
                        result = {'text': 'No text content available'}
                else:
                    result = {'text': 'No response content'}
        
        # Check if we got an empty response due to token limit
        if result.get('text') == 'No text content available':
            print(f"⚠️ Warning: Empty response - token limit may be too low for this task")
            
        # Save to file if specified
        if 'output_to_file' in step:
            self._save_to_file(step['output_to_file'], result)
            
        return result
        
    async def _run_claude_step(self, step: Dict) -> Any:
        """Execute Claude MUSCLE step - pure code/file execution, no decisions"""
        print(f"💪 Claude Muscle executing: {step.get('name', 'task')}")
        print(f"🔍 Debug: LLM call type: ASYNCHRONOUS (subprocess)")
        
        # Build Claude command
        cmd = ['claude']
        
        # Add CLI options
        claude_opts = step.get('claude_options', {})
        
        # Handle working directory
        if 'cwd' in claude_opts:
            # Resolve cwd relative to the project root
            cwd_path = Path(claude_opts['cwd']).resolve()
            cwd_path.mkdir(parents=True, exist_ok=True)
            # We'll need to use the cwd in the subprocess call
        
        if claude_opts.get('print', True):
            cmd.append('-p')
            
        if 'output_format' in claude_opts:
            cmd.extend(['--output-format', claude_opts['output_format']])
        else:
            cmd.extend(['--output-format', self.config['workflow']['defaults'].get('claude_output_format', 'json')])
            
        if 'max_turns' in claude_opts:
            cmd.extend(['--max-turns', str(claude_opts['max_turns'])])
            
        if claude_opts.get('verbose'):
            cmd.append('--verbose')
            
        if 'allowed_tools' in claude_opts:
            cmd.extend(['--allowedTools', ' '.join(claude_opts['allowed_tools'])])
            
        if 'append_system_prompt' in claude_opts:
            cmd.extend(['--append-system-prompt', claude_opts['append_system_prompt']])
            
        # Add cwd option if specified
        cwd_for_subprocess = None
        if 'cwd' in claude_opts:
            cwd_path = Path(claude_opts['cwd']).resolve()
            cwd_for_subprocess = str(cwd_path)
            
        # Build and add prompt
        prompt = self._build_prompt(step['prompt'], self.results)
        # print(f"🔍 Debug: Claude prompt built, length: {len(prompt)} chars")
        
        # Show prompt preview
        prompt_preview = prompt[:200] + "..." if len(prompt) > 200 else prompt
        print(f"📝 Prompt preview: {prompt_preview}")
        self._log_debug(f"Claude prompt:\n{prompt}\n")
        
        # Run Claude
        start_time = time.time()
        print(f"🚀 Debug: Starting LLM call to Claude NOW at {datetime.now().isoformat()}")
        if cwd_for_subprocess:
            print(f"📁 Working directory: {cwd_for_subprocess}")
        # print(f"🔍 Debug: Claude command: {' '.join(cmd)}")
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd_for_subprocess
        )
        # print(f"🔍 Debug: Claude subprocess created, communicating...")
        
        stdout, stderr = await process.communicate(prompt.encode())
        elapsed_time = time.time() - start_time
        # print(f"🔍 Debug: Claude subprocess completed at {datetime.now().isoformat()}")
        
        # Show raw response
        print(f"📤 Raw Claude response (took {elapsed_time:.2f}s):")
        if stdout:
            response_preview = stdout.decode()[:200] + "..." if len(stdout.decode()) > 200 else stdout.decode()
            print(f"  {response_preview}")
            self._log_debug(f"Claude response (took {elapsed_time:.2f}s):\n{stdout.decode()}\n")
        
        if process.returncode != 0:
            raise RuntimeError(f"Claude failed: {stderr.decode()}")
            
        # Parse output based on format
        output = stdout.decode()
        if claude_opts.get('output_format') == 'json' or self.config['workflow']['defaults'].get('claude_output_format') == 'json':
            result = json.loads(output)
        else:
            result = {'text': output}
            
        # Save to file if specified
        if 'output_to_file' in step:
            self._save_to_file(step['output_to_file'], result)
            
        return result
            
    async def _run_parallel_claude(self, step: Dict) -> Any:
        """Run multiple Claude MUSCLE tasks in parallel"""
        print(f"💪💪 Running {len(step['parallel_tasks'])} Claude tasks in parallel")
        print(f"🔍 Debug: LLM call type: ASYNCHRONOUS PARALLEL (multiple subprocesses)")
        print(f"🚀 Debug: Starting {len(step['parallel_tasks'])} parallel LLM calls to Claude NOW at {datetime.now().isoformat()}")
        
        tasks = []
        for task in step['parallel_tasks']:
            # Create a step-like structure for each parallel task
            claude_step = {
                'name': task['id'],
                'claude_options': task.get('claude_options', {}),
                'prompt': task['prompt'],
                'output_to_file': task.get('output_to_file')
            }
            tasks.append(self._run_claude_step(claude_step))
            
        results = await asyncio.gather(*tasks)
        
        # Combine results with markers
        combined = []
        for i, (task, result) in enumerate(zip(step['parallel_tasks'], results)):
            combined.append(f"\n===[{task['id']}]===\n")
            combined.append(str(result))
            
        combined_result = {
            'combined_results': '\n'.join(combined), 
            'individual_results': dict(zip([t['id'] for t in step['parallel_tasks']], results))
        }
        
        # Save combined results if specified
        if 'output_to_file' in step:
            self._save_to_file(step['output_to_file'], combined_result)
            
        return combined_result
        
    def _check_condition(self, condition: str) -> bool:
        """Check if a condition is met based on previous results"""
        if not condition:
            return True
            
        # Parse condition like "step_name.field_name"
        parts = condition.split('.')
        if len(parts) != 2:
            return True
            
        step_name, field_name = parts
        if step_name not in self.results:
            return False
            
        result = self.results[step_name].result
        if isinstance(result, dict):
            return bool(result.get(field_name, False))
        return False
        
    async def run(self):
        """Execute the pipeline"""
        steps = self.config['workflow']['steps']
        print(f"\n🚀 Starting pipeline: {self.config['workflow']['name']}")
        print(f"📊 Total steps: {len(steps)}")
        
        for i, step in enumerate(steps, 1):
            # Check condition if present
            if 'condition' in step and not self._check_condition(step['condition']):
                print(f"\n⏭️  Skipping step {i}/{len(steps)}: {step['name']} (condition not met)")
                continue
                
            print(f"\n🔄 Executing step {i}/{len(steps)}: {step['name']}")
            
            try:
                if step['type'] == 'gemini':
                    result = await self._run_gemini_step(step)
                elif step['type'] == 'claude':
                    result = await self._run_claude_step(step)
                elif step['type'] == 'parallel_claude':
                    result = await self._run_parallel_claude(step)
                else:
                    raise ValueError(f"Unknown step type: {step['type']}")
                    
                # Store result
                self.results[step['name']] = StepResult(
                    step_name=step['name'],
                    result=result,
                    timestamp=datetime.now(),
                    model_used=step.get('model', step['type'])
                )
                
                # Checkpoint if enabled
                if self.config['workflow'].get('checkpoint_enabled'):
                    self._save_checkpoint()
                    
                print(f"✅ Step {step['name']} completed")
                
            except Exception as e:
                print(f"❌ Step {step['name']} failed: {str(e)}")
                raise
                
        print(f"\n🎉 Pipeline completed successfully!")
        print(f"📋 Debug log: {self.debug_log_path}")
        print(f"💡 Tip: Run './view_debug.py' to see the full debug log and outputs")
                
    def _save_checkpoint(self):
        """Save current state for resume capability"""
        self.checkpoint_dir.mkdir(exist_ok=True)
        checkpoint_file = self.checkpoint_dir / f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        checkpoint_data = {
            'results': {
                name: {
                    'result': result.result,
                    'timestamp': result.timestamp.isoformat(),
                    'model_used': result.model_used
                }
                for name, result in self.results.items()
            }
        }
        
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
            
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python pipeline.py <config.yaml>")
        sys.exit(1)
        
    orchestrator = PipelineOrchestrator(sys.argv[1])
    asyncio.run(orchestrator.run())