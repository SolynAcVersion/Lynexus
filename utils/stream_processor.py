# [file name]: utils/stream_processor.py
"""
Stream Processing Logic - Separated from UI for cleaner architecture
Handles AI streaming, command execution, and history management
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Callable, Generator, Optional, Tuple


class StreamProcessor:
    """
    Handles the complete streaming and command execution logic
    Separated from UI to ensure clean architecture
    """
    
    def __init__(self, ai_instance, conversation_name: str, history_manager):
        self.ai = ai_instance
        self.conversation_name = conversation_name
        self.history_manager = history_manager
        
        # State tracking
        self.current_state = "idle"  # idle, streaming, executing_command, awaiting_summary
        self.last_command = None
        self.last_command_result = None
        self.full_response_buffer = ""
        self.command_execution_count = 0
        
    def process_user_message(self, user_message: str) -> Generator[Dict, None, None]:
        """
        Main entry point - Process user message and yield events
        Returns generator yielding events: {"type": "...", "content": "..."}
        """
        print(f"[StreamProcessor] Processing: {user_message[:50]}...")
        
        # 1. Load conversation history with current system prompt
        system_prompt = self.ai.system_prompt if hasattr(self.ai, 'system_prompt') else None
        history = self.history_manager.load_history(self.conversation_name, system_prompt)
        
        # 2. Add user message to history
        history.append({"role": "user", "content": user_message})
        
        # 3. Start processing loop
        self.current_state = "streaming"
        self.full_response_buffer = ""
        self.command_execution_count = 0
        
        max_iterations = getattr(self.ai, 'max_iterations', 15)
        
        for iteration in range(max_iterations):
            print(f"[StreamProcessor] Iteration {iteration + 1}/{max_iterations}")
            
            # Get AI response (streaming or non-streaming)
            ai_response = self._get_ai_response(history)
            
            # Check if response contains command
            if self._contains_command(ai_response):
                # Yield command detection event
                yield {"type": "command_detected", "content": ai_response}
                
                # Execute command
                command_result = self._execute_command(ai_response)
                
                # Yield command result event
                yield {"type": "command_result", "content": command_result}
                
                # Update history with command execution
                history.append({"role": "assistant", "content": ai_response})
                history.append({
                    "role": "user", 
                    "content": f"Execution result: {command_result}\nPlease decide next step based on this result."
                })
                
                self.command_execution_count += 1
                
                # Check if we should continue or get final summary
                if "Execution successful" in command_result and iteration < max_iterations - 1:
                    # Continue to next iteration
                    continue
                else:
                    # Get final summary
                    summary = self._get_final_summary(history)
                    yield {"type": "final_summary", "content": summary}
                    break
            else:
                # No command, this is the final response
                yield {"type": "final_response", "content": ai_response}
                break
        
        # Save final history
        self._save_final_history(history)
        self.current_state = "idle"
    
    def _get_ai_response(self, history: List[Dict]) -> str:
        """Get AI response based on current configuration"""
        try:
            if hasattr(self.ai, 'process_user_input_with_history'):
                return self.ai.process_user_input_with_history("", history)
            else:
                # Fallback - simulate streaming response
                import random
                responses = [
                    "I'll help you with that.",
                    "Let me check your desktop.",
                    "Processing your request...",
                    "Here's what I found."
                ]
                return random.choice(responses)
        except Exception as e:
            print(f"[StreamProcessor] Error getting AI response: {e}")
            return f"Error: {str(e)}"
    
    def _contains_command(self, response: str) -> bool:
        """Check if response contains a command"""
        if not hasattr(self.ai, 'command_start'):
            return False
        return self.ai.command_start in response
    
    def _execute_command(self, command_response: str) -> str:
        """Execute command from AI response"""
        try:
            # Parse command
            command_text = command_response.replace(self.ai.command_start, "").strip()
            tokens = command_text.split(self.ai.command_separator)
            tokens = [t.strip() for t in tokens if t.strip()]
            
            if not tokens:
                return "Error: Empty command"
            
            func_name = tokens[0]
            args = tokens[1:] if len(tokens) > 1 else []
            
            # Execute
            result = self.ai.exec_func(func_name, *args)
            return result
        except Exception as e:
            return f"Command execution error: {str(e)}"
    
    def _get_final_summary(self, history: List[Dict]) -> str:
        """Get final summary from AI"""
        try:
            # Add summary request to history
            history.append({
                "role": "user",
                "content": "Based on all execution results, please provide a final summary in Chinese."
            })
            
            # Get summary response
            if hasattr(self.ai, 'process_user_input_with_history'):
                summary = self.ai.process_user_input_with_history("", history)
                return summary
            else:
                return "Task completed. Summary unavailable."
        except Exception as e:
            return f"Summary error: {str(e)}"
    
    def _save_final_history(self, history: List[Dict]):
        """Save final conversation history"""
        try:
            self.history_manager.save_history(self.conversation_name, history)
        except Exception as e:
            print(f"[StreamProcessor] Error saving history: {e}")