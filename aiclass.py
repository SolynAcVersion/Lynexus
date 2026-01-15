# [file name]: aiclass.py
"""
Lynexus AI Assistant - Main AI class with enhanced features:
- Execution status tracking for status bar display
- Direct configuration updates without creating new instances
- Conversation history loading into AI context
- All MCP paths remain as relative paths
"""

from datetime import datetime 
import os 
import sys
import importlib.util
from openai import OpenAI  
import json
from mcp_utils import MCPServerManager, load_mcp_conf, exec_mcp_tools


# Main class of AI, encapsulated from ./console.py on 10/01/26
# Enhanced on 15/01/26 with status tracking and config updates
class AI:
    def __init__(self, 
                # Basic configuration for the model
                mcp_paths=None, 
                api_key=None,
                api_base=None,
                model=None,
                
                # System prompt
                system_prompt=None,
                
                # Model parameters
                temperature=1.0,
                max_tokens=None,
                top_p=1.0,
                stop=None,
                stream=False,
                presence_penalty=0.0,
                frequency_penalty=0.0,
                
                # Command parsing
                command_start="YLDEXECUTE:",
                command_separator="￥|",
                
                # Command execution
                max_iterations=15):
        """Initialize AI agent with enhanced features"""
        
        # Tool configuration - store relative paths
        self.mcp_paths = mcp_paths or []
        self.funcs = {}
        
        # API configuration
        self.api_key = api_key
        self.api_base = api_base or 'https://api.deepseek.com'
        self.model = model or 'deepseek-chat'
        self.client = None
        
        # Command configuration
        self.command_start = command_start
        self.command_separator = command_separator
        self.max_iterations = max_iterations
        
        # Model parameters
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stop = stop
        self.stream = stream
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        
        # System prompt - command_start and command_separator are now initialized
        self.system_prompt = system_prompt or self.get_default_system_prompt()
        
        # Conversation history
        self.conv_his = []
        
        # Execution status tracking for status bar display
        self.execution_status = {
            "status": "idle",  # idle, executing_tool, processing
            "tool_name": None,
            "tool_args": None,
            "start_time": None
        }
        
        # Initialize AI client first
        self.init_ai_client()
        
        # Load MCP tools (default tools will be added in load_mcp_tools if needed)
        self.load_mcp_tools()
        
        # Reset conversation history
        self.reset_conversation()
        
        print(f"[Info] AI initialized with {len(self.funcs)} tools")
    
    def get_default_system_prompt(self):
        """Return default system prompt"""
        default_prompt = f"""
You are an AI assistant that can directly execute commands and call available tools.

【Core Principles】
1. **Strict Response Mode**:
- When the user explicitly requests an operation (query, search, file operations, etc.), **only output one line {self.command_start} instruction**, without any other text
- When the user requests content creation, answers questions, or normal conversation, **directly output the content itself**, without any additional explanations
- When the user says "continue", only output the next {self.command_start} instruction, without any explanation

2. **Accurate Understanding of Intent**:
- User states facts (e.g., "I'm from Jinan") → Respond directly to the fact, do not call tools
- User explicitly requests operations (e.g., "save file to desktop") → Call the corresponding tool

3. **Use Correct Tools and Syntax**:
- Only use actually available tools
- Ensure command syntax is correct, especially for file operations

Before executing MCP tools, please check:
1. Are all required parameters provided in the correct format?
2. Are parameter value types correct (numbers/strings/booleans)?
3. Are there additional optional parameters that can be provided?
4. If there's an error, try multiple parameter formats, such as 2, peoplecount=2, etc.

If unsure, ask the user what parameters are needed.

【Call Format】
- `{self.command_start} tool_name {self.command_separator} param1 {self.command_separator} param2 {self.command_separator} ...`
- Or direct system command: `{self.command_start} command {self.command_separator} param1 {self.command_separator} param2 {self.command_separator} ...`

【Strictly Prohibited】
1. Do not add explanatory text before or after any {self.command_start} instruction
2. Do not actively plan multi-step operations when not explicitly requested by user
3. Do not use incorrect command syntax (especially for file operations)
4. Do not output words like "I'll", "let me", "try", "now", "then", etc.
5. Do not provide alternative suggestions or explain reasons when operations fail
6. Do not combine multiple operations into one instruction without explicit user request

【Error Examples】
User: I'm from Jinan
Wrong: {self.command_start} weather {self.command_separator} Jinan # (User is just stating, not requesting query)

User: continue
Wrong: [AI] Now getting current date... # (Should only output {self.command_start} instruction, no explanation)

User: save file
Wrong: {self.command_start} echo {self.command_separator} content {self.command_separator} 2 {self.command_separator} file_path # (Incorrect redirection syntax)

【Multi-step Operation Rules】
1. Only execute multiple steps when user explicitly requests multiple operations
2. Execute only one step at a time, wait for user to say "continue" before next step
3. Output only one {self.command_start} instruction per step, without any other text
4. Do not decompose tasks on your own if user doesn't explicitly request multiple steps

【Error Handling】
- If execution fails, directly reply "Operation failed" (non-{self.command_start} situation) or wait for further user instructions
- Do not explain reasons, do not provide alternatives

Please strictly follow these rules to ensure responses are concise, accurate, and meet actual user needs.
"""
        return default_prompt

    def load_mcp_mod(self, mcp_path):
        """Load one MCP file (*.json or *.py)"""
        try:
            if mcp_path.endswith('.json'):
                mcp_manager = MCPServerManager()
                tool_names = load_mcp_conf(mcp_path, mcp_manager)
                
                if not tool_names:
                    return None, {}
                
                funcs = {}
                
                for ser_name in mcp_manager.servers.keys():
                    for tool in mcp_manager.tools.get(ser_name, []):
                        tool_name = tool.get('name', '')
                        if tool_name:
                            func_name = f"mcp_{ser_name}_{tool_name}"
                            def make_tool_func(name_ser, name_tool, desc):
                                def tool_func(**kwargs):
                                    res = mcp_manager.call_tool(name_ser, name_tool, kwargs)
                                    return json.dumps(res, ensure_ascii=False, indent=2)
                                tool_func.__name__ = name_tool
                                tool_func.__doc__ = tool.get('description', desc)
                                return tool_func
                            funcs[func_name] = make_tool_func(ser_name, tool_name, tool.get('description', 'No description'))
                
                class MCPModule:
                    def __init__(self):
                        self.manager = mcp_manager
                return MCPModule(), funcs             
                        
            else:
                # Python file
                module_name = os.path.basename(mcp_path).replace('.py', '')
                spec = importlib.util.spec_from_file_location(module_name, mcp_path)
                if spec is None:
                    raise ImportError(f"[Warning] Cannot load module from {mcp_path}")
                
                mcp_module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mcp_module
                spec.loader.exec_module(mcp_module)  
                print(f"[Info] Successfully loaded {module_name}")
                
                funcs = {}
                for attr_name in dir(mcp_module):
                    attr = getattr(mcp_module, attr_name)
                    if callable(attr) and not attr_name.startswith('_'):
                        funcs[attr_name] = attr
                        
                return mcp_module, funcs
            
        except Exception as e:
            print(f"[Warning] Load failed: {e}")
            return None, {}

    def load_mult_mcp_mod(self, mcp_paths):
        """Load multiple MCP files"""
        all_funcs = {}
        all_mods = []
        
        for path in mcp_paths:
            mod, funcs = self.load_mcp_mod(path)
            if mod:
                all_mods.append(mod)
            if funcs:
                for func_name, func in funcs.items():
                    if func_name in all_funcs:
                        print(f"[Warning] Function '{func_name}' exists in multiple MCP files, will use the last loaded version")
                    all_funcs[func_name] = func
        return all_mods, all_funcs
    
    def load_mcp_tools(self):
        """Load MCP tools from paths"""
        if not self.mcp_paths:
            print("[Info] No MCP paths provided, skipping tool loading")
            return
        
        # Check if default tools exist and add them
        default_tools = []
        
        # Check for OCR tool - using relative path
        ocr_path = "./tools/ocr.py"
        if os.path.exists(ocr_path):
            default_tools.append(ocr_path)
        else:
            print(f"[Warning] OCR tool not found at {ocr_path}")
            
        # Check for MCP config - using relative path
        mcp_config_path = "./tools/mcp_config.json"
        if os.path.exists(mcp_config_path):
            default_tools.append(mcp_config_path)
        else:
            print(f"[Warning] MCP config not found at {mcp_config_path}")
            
        # Add default tools to paths if not already present
        for tool_path in default_tools:
            if tool_path not in self.mcp_paths:
                self.mcp_paths.append(tool_path)
                print(f"[Info] Added default tool: {tool_path}")
        
        # Verify paths exist - all paths remain as provided (relative or absolute)
        valid_paths = []
        for path in self.mcp_paths:
            # Try to resolve relative path
            if not os.path.isabs(path) and not os.path.exists(path):
                # Try relative to current directory
                resolved_path = os.path.join(os.getcwd(), path)
                if os.path.exists(resolved_path):
                    valid_paths.append(resolved_path)
                else:
                    print(f"[Warning] File does not exist: {path}")
            elif os.path.exists(path):
                valid_paths.append(path)
            else:
                print(f"[Warning] File does not exist: {path}")
        
        if not valid_paths:
            print("[Warning] No valid MCP file paths found")
            return
        
        print(f"[Info] Will load {len(valid_paths)} MCP files")
        
        # Load valid MCP files
        _, self.funcs = self.load_mult_mcp_mod(valid_paths)
        
        # Debug information
        print(f"[Debug] Loaded {len(self.funcs)} functions")
        if self.funcs:
            print(f"[Debug] Function list: {list(self.funcs.keys())}")
        
        # Generate tool descriptions and update system prompt
        if self.funcs:
            tools_desc = self.gen_tools_desc()
            current_prompt = self.system_prompt
            
            # Add tools description to the beginning of system prompt
            self.system_prompt = tools_desc + '\n\n' + current_prompt
            self.update_system_prompt(self.system_prompt)
            print("[Info] Updated system prompt with tool descriptions")
    
    def add_mcp_mods(self, valid_paths):
        """Add additional MCP files to the AI agent"""
        _, funcs = self.load_mult_mcp_mod(valid_paths)
        self.funcs.update(funcs)
        
        if funcs:
            tools_desc = "You can use the following tools to operate files:\n"
            for func_name, func in funcs.items():
                doc = func.__doc__ or "No description"
                tools_desc += f"- {func_name}: {doc}\n"
            
            # Update system prompt with new tools
            current_prompt = self.system_prompt
            self.system_prompt = tools_desc + '\n\n' + current_prompt
            self.update_system_prompt(self.system_prompt)
    
    def gen_tools_desc(self):
        """Generate tools description"""
        if not self.funcs:
            return ""
        
        desc = "You can use the following tools:\n"
        for func_name, func in self.funcs.items():
            doc = func.__doc__ or "No description"
            # Truncate long descriptions
            if len(doc) > 150:
                doc = doc[:150] + "..."
            desc += f"- {func_name}: {doc}\n"
        
        # Add usage example
        desc += f"\nUsage example: {self.command_start} tool_name {self.command_separator} param1 {self.command_separator} param2\n"
        return desc
    
    def init_ai_client(self):
        """Initialize AI client"""
        if not self.api_key:
            # Try various environment variables
            self.api_key = os.environ.get("DEEPSEEK_API_KEY") or \
                          os.environ.get("OPENAI_API_KEY") or \
                          os.environ.get("ANTHROPIC_API_KEY")
            
            if not self.api_key:
                raise ValueError("No API key provided and no API key found in environment variables")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base
        )
        print(f"[Info] API client initialized with model: {self.model}")
    
    # ============ Configuration Update Methods ============
    
    def update_system_prompt(self, new_prompt):
        """Update system prompt"""
        self.system_prompt = new_prompt
        for i, msg in enumerate(self.conv_his):
            if msg.get("role") == "system":
                self.conv_his[i]["content"] = new_prompt
                break
        else:
            self.conv_his.insert(0, {"role": "system", "content": new_prompt})
    
    def update_temperature(self, temperature):
        """Update temperature parameter (0.0-2.0)"""
        self.temperature = temperature
    
    def update_model_params(self, **kwargs):
        """Batch update model parameters"""
        valid_params = ['max_tokens', 'top_p', 'stop', 'stream', 
                       'presence_penalty', 'frequency_penalty']
        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)
            else:
                print(f"[Warning] Invalid parameter: {key}")
    
    def update_api_config(self, api_key=None, api_base=None, model=None):
        """Update API configuration"""
        if api_key:
            self.api_key = api_key
        if api_base:
            self.api_base = api_base
        if model:
            self.model = model
        self.init_ai_client()
    
    def update_command_config(self, command_start=None, command_separator=None):
        """Update command execution configuration"""
        if command_start:
            self.command_start = command_start
        if command_separator:
            self.command_separator = command_separator
        
        # Re-generate system prompt with new command config
        self.system_prompt = self.get_default_system_prompt()
        self.update_system_prompt(self.system_prompt)
    
    def update_max_iterations(self, max_iterations):
        """Update maximum execution iterations"""
        self.max_iterations = max_iterations
    
    def update_config(self, config_dict):
        """Update configuration from dictionary without creating new instance"""
        print(f"[Info] Updating AI configuration for existing instance")
        
        # Update API configuration if provided
        if 'api_key' in config_dict and config_dict['api_key']:
            self.api_key = config_dict['api_key']
        
        if 'api_base' in config_dict and config_dict['api_base']:
            self.api_base = config_dict['api_base']
        
        if 'model' in config_dict and config_dict['model']:
            self.model = config_dict['model']
            
        # Reinitialize client if API config changed
        if any(key in config_dict for key in ['api_key', 'api_base', 'model']):
            self.init_ai_client()
        
        # Update model parameters
        if 'temperature' in config_dict:
            self.temperature = config_dict['temperature']
        
        if 'max_tokens' in config_dict:
            self.max_tokens = config_dict['max_tokens']
        
        if 'top_p' in config_dict:
            self.top_p = config_dict['top_p']
        
        if 'stop' in config_dict:
            self.stop = config_dict['stop']
        
        if 'stream' in config_dict:
            self.stream = config_dict['stream']
        
        if 'presence_penalty' in config_dict:
            self.presence_penalty = config_dict['presence_penalty']
        
        if 'frequency_penalty' in config_dict:
            self.frequency_penalty = config_dict['frequency_penalty']
        
        # Update command configuration
        if 'command_start' in config_dict:
            self.command_start = config_dict['command_start']
        
        if 'command_separator' in config_dict:
            self.command_separator = config_dict['command_separator']
        
        if 'max_iterations' in config_dict:
            self.max_iterations = config_dict['max_iterations']
        
        # Update system prompt
        if 'system_prompt' in config_dict and config_dict['system_prompt']:
            self.system_prompt = config_dict['system_prompt']
            self.update_system_prompt(self.system_prompt)
        
        # Update MCP paths and reload tools if changed
        if 'mcp_paths' in config_dict:
            new_paths = config_dict['mcp_paths']
            if set(new_paths) != set(self.mcp_paths):
                print(f"[Info] MCP paths changed, reloading tools")
                self.mcp_paths = new_paths
                self.load_mcp_tools()
        
        print(f"[Info] Configuration updated successfully")
    
    # ============ Configuration Get Methods ============
    
    def get_config(self):
        """Get current configuration dictionary"""
        return {
            # API config
            "api_base": self.api_base,
            "model": self.model,
            
            # Prompt config
            "system_prompt": self.system_prompt,
            
            # Model parameters
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stop": self.stop,
            "stream": self.stream,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            
            # Command execution config
            "command_start": self.command_start,
            "command_separator": self.command_separator,
            "max_iterations": self.max_iterations,
            
            # Tool config
            "mcp_paths": self.mcp_paths.copy(),
            "available_tools": list(self.funcs.keys())
        }
    
    def get_execution_status(self):
        """Get current execution status for status bar display"""
        return self.execution_status.copy()

    def reset_conversation(self):
        """Clear conversation history"""
        self.conv_his = [{"role": "system", "content": self.system_prompt}]
    
    def load_conversation_history(self, history_messages):
        """Load conversation history into AI context"""
        print(f"[Info] Loading {len(history_messages)} conversation history messages")
        
        # Reset conversation first
        self.reset_conversation()
        
        # Add history messages to conversation
        for msg in history_messages:
            role = "user" if msg.get("is_sender", False) else "assistant"
            content = msg.get("text", "")
            
            # Skip empty messages
            if content and content.strip():
                self.conv_his.append({"role": role, "content": content})
        
        print(f"[Info] Conversation history loaded. Total messages: {len(self.conv_his)}")
    
    def exec_func(self, func_name, *args):
        """Execute functions called by AI agents with status tracking"""
        if func_name not in self.funcs:
            return f"Error: Function '{func_name}' does not exist"
        
        try:
            # Update execution status for status bar display
            self.execution_status = {
                "status": "executing_tool",
                "tool_name": func_name,
                "tool_args": args,
                "start_time": datetime.now().isoformat()
            }
            
            print(f"[Debug] Executing function: {func_name} with args: {args}")
            
            if func_name.startswith('mcp_'):
                kwargs = {}
                for arg in args:
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        kwargs[key.strip()] = value.strip()
                    elif arg.strip():
                        kwargs['value'] = arg.strip()
                
                print(f"[Debug] Calling MCP function with kwargs: {kwargs}")
                res = self.funcs[func_name](**kwargs)
            else:
                print(f"[Debug] Calling regular function with args: {args}")
                res = self.funcs[func_name](*args)
            
            print(f"[Debug] Function execution result: {res[:100]}..." if len(str(res)) > 100 else f"[Debug] Function execution result: {res}")
            
            # Reset execution status
            self.execution_status = {
                "status": "idle",
                "tool_name": None,
                "tool_args": None,
                "start_time": None
            }
            
            return f"Execution successful: {res}"
        except Exception as e:
            print(f"[Error] Function execution failed: {e}")
            
            # Reset execution status even on error
            self.execution_status = {
                "status": "idle",
                "tool_name": None,
                "tool_args": None,
                "start_time": None
            }
            
            return f"Execution failed: {e}"
    
    def process_user_inp(self, user_inp, max_iter=None):
        """Process user input with execution status tracking"""
        if not user_inp:
            return "", False

        max_iter = max_iter or self.max_iterations
        
        # Update execution status to processing
        self.execution_status = {
            "status": "processing",
            "tool_name": None,
            "tool_args": None,
            "start_time": datetime.now().isoformat()
        }
        
        # Add user input to conversation history
        self.conv_his.append({"role": "user", "content": user_inp})
        
        for step in range(max_iter):
            try:
                # Prepare API call parameters
                api_params = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": self.conv_his,
                    "stream": self.stream
                }
                
                # Add optional parameters if not None
                optional_params = {
                    "max_tokens": self.max_tokens,
                    "top_p": self.top_p,
                    "stop": self.stop,
                    "presence_penalty": self.presence_penalty,
                    "frequency_penalty": self.frequency_penalty
                }
                
                for param, value in optional_params.items():
                    if value is not None:
                        api_params[param] = value
                
                print(f"[Debug] Sending request to API with {len(self.conv_his)} messages")
                response = self.client.chat.completions.create(**api_params)
                get_reply = response.choices[0].message.content
                print(f"[Debug] Received reply: {get_reply[:100]}..." if len(get_reply) > 100 else f"[Debug] Received reply: {get_reply}")
                
                # Check if AI wants to execute commands
                if get_reply.startswith(self.command_start):
                    print(f"\n[Step {step + 1}][AI requested execution] {get_reply}")
                    
                    # Parse command
                    tokens = get_reply.replace(self.command_start, "").strip().split(self.command_separator)
                    tokens = [t.strip() for t in tokens]
                    print(f"[Debug] Parsed tokens: {tokens}")
                    
                    if len(tokens) < 1:
                        res = "Error! Your command format is incorrect"
                    else:
                        func_name = tokens[0]
                        args = tokens[1:] if len(tokens) > 1 else []
                        res = self.exec_func(func_name, *args)
                    
                    print(f"[Info] AI execution result: {res}")
                    
                    self.conv_his.append({"role": "assistant", "content": get_reply})
                    self.conv_his.append({"role": "user", "content": f"Execution result: {res}\nPlease decide the next operation based on this result. If the task is complete, please summarize and tell me the result."})
                    
                else:
                    # No execution needed
                    self.conv_his.append({"role": "assistant", "content": get_reply})
                    
                    # Reset execution status
                    self.execution_status = {
                        "status": "idle",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    
                    return get_reply, True
                    
            except Exception as e:
                print(f"[Error] Error processing user input: {e}")
                
                # Reset execution status
                self.execution_status = {
                    "status": "idle",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                
                return f"Error occurred during processing: {e}", True
        
        # Reset execution status
        self.execution_status = {
            "status": "idle",
            "tool_name": None,
            "tool_args": None,
            "start_time": None
        }
        
        return f"Reached maximum execution steps ({max_iter}), task may not be fully completed", False
    
    def get_available_tools(self):
        """Get available tools list"""
        tools = []
        for func_name, func in self.funcs.items():
            doc = func.__doc__ or "No description"
            tools.append({"name": func_name, "description": doc})
        return tools
    
    def print_tools_list(self):
        """Print available tools list"""
        print("\nAvailable tools:")
        tools = self.get_available_tools()
        for i, tool in enumerate(tools, 1):
            print(f"{i:2}. {tool['name']}: {tool['description'][:60]}...")


# Configuration file loading functions
def load_config_from_file(config_path):
    """Load configuration from file (JSON or YAML)"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.endswith('.json'):
                config = json.load(f)
            elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                try:
                    import yaml
                    config = yaml.safe_load(f)
                except ImportError:
                    print("[Warning] PyYAML not installed. Install with: pip install pyyaml")
                    return None
            else:
                raise ValueError("Unsupported config file format, supports JSON or YAML")
        return config
    except Exception as e:
        print(f"[Error] Failed to load config file: {e}")
        return None


def create_ai_from_config(config_path):
    """Create AI instance from config file"""
    config = load_config_from_file(config_path)
    if not config:
        return None
    
    # Extract configuration parameters
    mcp_paths = config.get("mcp_paths", [])
    api_key = config.get("api_key")
    
    # Create AI instance
    ai = AI(
        mcp_paths=mcp_paths,
        api_key=api_key,
        api_base=config.get("api_base"),
        model=config.get("model"),
        system_prompt=config.get("system_prompt"),
        temperature=config.get("temperature", 1.0),
        max_tokens=config.get("max_tokens"),
        top_p=config.get("top_p", 1.0),
        stop=config.get("stop"),
        stream=config.get("stream", False),
        presence_penalty=config.get("presence_penalty", 0.0),
        frequency_penalty=config.get("frequency_penalty", 0.0),
        command_start=config.get("command_start", "YLDEXECUTE:"),
        command_separator=config.get("command_separator", "￥|"),
        max_iterations=config.get("max_iterations", 15)
    )
    
    return ai


def save_config_to_file(ai_instance, config_path):
    """Save AI instance configuration to file"""
    config = ai_instance.get_config()
    config["api_key"] = ai_instance.api_key  # Warning: saving API key needs caution
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"[Info] Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"[Error] Failed to save configuration: {e}")
        return False


def main():
    """Main console interface"""
    config_type = input("Select configuration method (1: Manual, 2: Config file): ").strip()
    
    if config_type == "2":
        config_path = input("Enter config file path: ").strip()
        ai = create_ai_from_config(config_path)
        if not ai:
            print("Failed to load config file, using default configuration")
            ai = AI()
    else:
        MCP_PATH = input("MCP file directory (supports .py or .json) (multiple files separated by spaces): ").strip()
        mcp_paths = [p.strip() for p in MCP_PATH.split() if p.strip()]
        
        use_custom = input("Use custom configuration? (y/N): ").strip().lower()
        
        if use_custom == 'y':
            temperature = float(input(f"Temperature (default 1.0): ") or "1.0")
            command_start = input(f"Command start identifier (default YLDEXECUTE:): ") or "YLDEXECUTE:"
            command_separator = input(f"Command separator (default ￥|): ") or "￥|"
            
            ai = AI(
                mcp_paths=mcp_paths,
                temperature=temperature,
                command_start=command_start,
                command_separator=command_separator
            )
        else:
            ai = AI(mcp_paths=mcp_paths)
    
    while True:
        try:
            user_inp = input("\n>> ").strip()
            if user_inp.lower() in ['exit', 'quit', 'bye', '退出', '再见']:
                print("Goodbye!")
                break
            if not user_inp:
                continue
            
            if user_inp.lower() in ['clear', '清空']:
                ai.reset_conversation()
                print("Conversation history cleared")
                continue
            
            if user_inp.lower() == 'config':
                config = ai.get_config()
                print("\nCurrent configuration:")
                for key, value in config.items():
                    print(f"  {key}: {value}")
                continue
                
            if user_inp.lower() == 'tools':
                ai.print_tools_list()
                continue
                
            if user_inp.lower().startswith('update '):
                parts = user_inp[7:].split('=', 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    print(f"Update configuration: {key} = {value}")
                continue
            
            response, completed = ai.process_user_inp(user_inp)
            if response:
                print(f"\n[AI] {response}")
            
        except KeyboardInterrupt:
            print("\n[Error] Operation interrupted, goodbye!")
            break
        except Exception as e:
            print(f"\n[Error] Error: {e}")
            continue

if __name__ == "__main__":
    main()