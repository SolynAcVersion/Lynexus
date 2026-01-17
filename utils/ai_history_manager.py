# [file name]: utils/ai_history_manager.py
"""
AI Conversation History Manager - Independent from chat display history
Manages AI's conversation context, saves only valid conversations and command execution results
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class AIHistoryManager:
    """
    AI Conversation History Manager
    Manages AI's conv_his, completely separate from chat display history
    """
    
    def __init__(self, ai_conv_dir: str = "ai_conv"):
        self.ai_conv_dir = Path(ai_conv_dir)
        self.ai_conv_dir.mkdir(exist_ok=True, parents=True)
    
    def get_history_file(self, conversation_name: str) -> Path:
        """Get conversation history file path"""
        # Clean invalid characters from filename
        safe_name = "".join(c for c in conversation_name if c.isalnum() or c in (' ', '-', '_'))
        safe_name = safe_name.strip() or "default"
        return self.ai_conv_dir / f"{safe_name}_ai.json"
    
    def load_history(self, conversation_name: str, system_prompt: str = None) -> List[Dict]:
        """Load AI conversation history"""
        history_file = self.get_history_file(conversation_name)
        
        loaded_history = []
        
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    loaded_history = json.load(f)
                print(f"[AIHistory] Loaded {len(loaded_history)} messages from {history_file}")
            except Exception as e:
                print(f"[AIHistory] Failed to load history: {e}")
        
        # Ensure system prompt is at the beginning
        if system_prompt:
            # Remove any existing system prompts
            filtered_history = [msg for msg in loaded_history if msg.get("role") != "system"]
            # Add new system prompt at the beginning
            filtered_history.insert(0, {"role": "system", "content": system_prompt})
            return filtered_history
        elif loaded_history and loaded_history[0].get("role") == "system":
            return loaded_history
        else:
            # Return default system prompt
            return [
                {"role": "system", "content": "You are an AI assistant that can execute commands when requested."}
            ]
    
    def save_history(self, conversation_name: str, history: List[Dict]):
        """Save AI conversation history"""
        history_file = self.get_history_file(conversation_name)
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            print(f"[AIHistory] Saved {len(history)} messages to {history_file}")
        except Exception as e:
            print(f"[AIHistory] Failed to save history: {e}")
    
    def add_message_pair(self, conversation_name: str, user_input: str, assistant_response: str) -> List[Dict]:
        """Add user-assistant message pair to history"""
        history = self.load_history(conversation_name)
        
        # Add user message
        history.append({"role": "user", "content": user_input})
        
        # Add assistant message
        history.append({"role": "assistant", "content": assistant_response})
        
        self.save_history(conversation_name, history)
        return history
    
    def clear_history(self, conversation_name: str, system_prompt: str = None):
        """Clear conversation history, keep only system prompt"""
        if system_prompt:
            history = [{"role": "system", "content": system_prompt}]
        else:
            history = [
                {"role": "system", "content": "You are an AI assistant that can execute commands when requested."}
            ]

        self.save_history(conversation_name, history)
        print(f"[AIHistory] Cleared history for {conversation_name}")

    def delete_history(self, conversation_name: str):
        """Delete conversation history file"""
        history_file = self.get_history_file(conversation_name)

        if history_file.exists():
            try:
                history_file.unlink()
                print(f"[AIHistory] Deleted history file: {history_file}")
            except Exception as e:
                print(f"[AIHistory] Failed to delete history: {e}")
        else:
            print(f"[AIHistory] History file does not exist: {history_file}")