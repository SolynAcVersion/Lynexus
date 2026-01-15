# [file name]: utils/config_manager.py
"""
Configuration Manager
Handles saving and loading of configuration files with relative paths.
"""
import os
import json
import pickle

class ConfigManager:
    """Manages configuration files with relative path handling."""
    
    def __init__(self):
        self.configs_dir = "configs"
        self.ignore_file = ".confignore"
        self.conversations_dir = "conversations"
        self.history_dir = "chathistory"
        
        # Create directories if they don't exist
        os.makedirs(self.configs_dir, exist_ok=True)
        os.makedirs(self.conversations_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)
    
    def get_conversation_config_path(self, conversation_name):
        """Get config file path for a conversation (sanitized name)."""
        # Sanitize conversation name for filename
        safe_name = "".join(c for c in conversation_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return os.path.join(self.conversations_dir, f"{safe_name}.json")
    
    def load_conversation_config(self, conversation_name):
        """Load configuration for a conversation with path conversion."""
        config_path = self.get_conversation_config_path(conversation_name)
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # Convert relative MCP paths to absolute paths
                    if 'mcp_paths' in config:
                        config['mcp_paths'] = [
                            os.path.abspath(path) if not os.path.isabs(path) else path
                            for path in config['mcp_paths']
                        ]
                    
                    return config
            except Exception as e:
                print(f"Error loading config for {conversation_name}: {e}")
        return None
    
    def save_conversation_config(self, conversation_name, config):
        """Save conversation configuration with relative paths."""
        config_path = self.get_conversation_config_path(conversation_name)
        safe_config = config.copy()
        
        # Remove sensitive information
        if 'api_key' in safe_config:
            del safe_config['api_key']
        if 'ai_config' in safe_config and 'api_key' in safe_config['ai_config']:
            del safe_config['ai_config']['api_key']
        
        # Convert absolute MCP paths to relative paths if they are in the current directory tree
        if 'mcp_paths' in safe_config:
            safe_config['mcp_paths'] = [
                self._make_path_relative(path) for path in safe_config['mcp_paths']
            ]
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(safe_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config for {conversation_name}: {e}")
            return False
    
    def _make_path_relative(self, path):
        """Convert absolute path to relative if possible."""
        if not os.path.isabs(path):
            return path
        
        # Try to make path relative to current directory
        try:
            rel_path = os.path.relpath(path)
            # Only use relative path if it doesn't go up too many directories
            if not rel_path.startswith('..' + os.sep + '..'):
                return rel_path
        except ValueError:
            pass
        
        # Return absolute path if relative conversion fails or goes too far up
        return path
    
    def load_api_key(self):
        """Load API key from .confignore file or environment variables."""
        # Try .confignore file first
        ignore_path = self.ignore_file
        if os.path.exists(ignore_path):
            try:
                with open(ignore_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    lines = content.split('\n')
                    for line in lines:
                        if '=' in line:
                            key, value = line.split('=', 1)
                            if key.strip() == 'api_key':
                                return value.strip()
            except:
                pass
        
        # Check environment variables
        env_keys = ['DEEPSEEK_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
        for key in env_keys:
            value = os.environ.get(key)
            if value:
                return value
        
        return None
    
    def save_api_key(self, api_key):
        """Save API key to .confignore file."""
        try:
            with open(self.ignore_file, 'w', encoding='utf-8') as f:
                f.write(f"api_key={api_key}")
            return True
        except:
            return False
    
    def save_chat_history(self, chat_records):
        """Save chat history to pickle files."""
        for chat, messages in chat_records.items():
            file_path = os.path.join(self.history_dir, f"{chat}.his")
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(messages, f)
            except Exception as e:
                print(f"Error saving chat history: {e}")
    
    def load_chat_history(self):
        """Load chat history from pickle files."""
        chat_records = {}
        for file_name in os.listdir(self.history_dir):
            if file_name.endswith('.his'):
                chat_name = file_name[:-4]
                file_path = os.path.join(self.history_dir, file_name)
                try:
                    with open(file_path, 'rb') as f:
                        chat_records[chat_name] = pickle.load(f)
                except Exception as e:
                    print(f"Error loading chat history: {e}")
        return chat_records