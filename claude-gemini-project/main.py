#!/usr/bin/env python3
"""
Claude Code + Gemini AI Integration Demo

Demonstrates a 2-round trip collaboration between Claude Code and Gemini AI
to iteratively develop and improve a Python email validation function.

Uses proper Claude Code session management for multi-turn conversations.
"""

import os
import json
import subprocess
from google import genai
from google.genai import types


class AICollaborationDemo:
    def __init__(self):
        self.setup_clients()
        self.session_id = None
        
    def setup_clients(self):
        """Initialize clients"""
        # Gemini client
        self.gemini_client = genai.Client()
        
    def validate_environment(self):
        """Check that required components are available"""
        if not os.getenv('GEMINI_API_KEY'):
            raise ValueError("Missing GEMINI_API_KEY")
    
    def claude_with_session(self, prompt: str, continue_session: bool = False) -> tuple[str, str]:
        """
        Call Claude with proper session management
        Returns: (response, session_id)
        """
        print(f"🤖 Asking Claude: {prompt[:100]}...")
        
        try:
            cmd = ["claude", "-p", "--output-format", "json"]
            
            if continue_session and self.session_id:
                cmd.extend(["--resume", self.session_id])
            
            cmd.append(prompt)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                
                # Extract session ID for future use
                self.session_id = response_data.get('session_id')
                
                # Get the actual response
                response_text = response_data.get('result', '')
                
                print(f"📝 Claude responds ({len(response_text)} chars): {response_text[:200]}...")
                return response_text, self.session_id
            else:
                error_msg = result.stderr.strip() if result.stderr else f"Exit code: {result.returncode}"
                print(f"❌ Claude error: {error_msg}")
                return f"Error from Claude: {error_msg}", None
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Claude JSON response: {e}")
            return f"JSON decode error: {e}", None
        except subprocess.TimeoutExpired:
            return "Claude request timed out", None
        except Exception as e:
            print(f"❌ Error calling Claude: {e}")
            return f"Error calling Claude: {e}", None
    
    def ask_gemini(self, prompt: str) -> str:
        """Send a prompt to Gemini and return the response"""
        print(f"✨ Asking Gemini: {prompt[:100]}...")
        
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite-preview-06-17",
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)
                )
            )
            result = response.text
            print(f"💫 Gemini responds: {result[:200]}...")
            return result
        except Exception as e:
            return f"Error from Gemini: {str(e)}"
    
    def run_collaboration_demo(self):
        """Run the collaboration demo with proper session management"""
        print("🚀 Claude + Gemini Collaboration Demo (Proper Multi-turn)")
        print("=" * 65)
        
        try:
            self.validate_environment()
        except ValueError as e:
            print(f"❌ {e}")
            return
        
        # Initial problem - start new session
        problem = """PROVIDE ACTUAL PYTHON CODE - do not describe what you will do.

Start your response with: import re

Then provide the validate_email(email) function that:
- Uses regex for email validation
- Returns True/False
- Has a docstring
- Include 3 example function calls

BEGIN CODE NOW:"""
        
        print(f"\n🎯 Problem: {problem}")
        print("\n" + "=" * 65)
        
        # Round 1: Claude creates solution (new session)
        print("\n🔄 Round 1: Claude creates solution")
        claude_response_1, session_id = self.claude_with_session(problem, continue_session=False)
        
        if not session_id or "Error" in claude_response_1:
            print("❌ Failed to get response from Claude, stopping demo")
            return
        
        print(f"📋 Session ID: {session_id}")
        
        # Round 1: Gemini reviews
        gemini_prompt_1 = f"""Review this Python email validation code:

{claude_response_1}

Focus on: regex pattern accuracy, edge cases, code quality. Provide specific suggestions."""
        
        gemini_response_1 = self.ask_gemini(gemini_prompt_1)
        
        print("\n" + "=" * 65)
        
        # Round 2: Claude improves based on feedback (continue session)
        print("\n🔄 Round 2: Claude improves (continuing session)")
        claude_prompt_2 = f"""Based on this review feedback, improve the email validation function:

{gemini_response_1}

Provide the complete improved Python code that addresses these points."""
        
        claude_response_2, _ = self.claude_with_session(claude_prompt_2, continue_session=True)
        
        # Round 2: Gemini final assessment
        gemini_prompt_2 = f"""Rate this improved email validation function (1-10) and summarize its strengths:

{claude_response_2}"""
        
        gemini_response_2 = self.ask_gemini(gemini_prompt_2)
        
        print("\n" + "=" * 65)
        print("\n🎉 Collaboration Complete!")
        print(f"\n📊 Final Assessment:\n{gemini_response_2}")
        
        # Save results
        results = {
            "session_id": session_id,
            "problem": problem,
            "round_1": {
                "claude_solution": claude_response_1,
                "gemini_review": gemini_response_1
            },
            "round_2": {
                "claude_improved": claude_response_2,
                "gemini_assessment": gemini_response_2
            }
        }
        
        with open("collaboration_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Saved to collaboration_results.json")
        print(f"📋 Session ID for future reference: {session_id}")


def main():
    demo = AICollaborationDemo()
    demo.run_collaboration_demo()


if __name__ == "__main__":
    main()