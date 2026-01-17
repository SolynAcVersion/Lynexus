# [file name]: aiclass.py
"""
Lynexus AI Assistant - Complete version with proper history management
保持所有原始功能，包括：
1. 系统提示集成
2. 完整的对话历史上下文
3. 流式和非流式处理
4. 命令执行迭代
5. MCP工具加载
"""

from datetime import datetime
import os
import sys
import importlib.util
import json
from typing import List, Dict, Generator, Optional
from openai import OpenAI
from mcp_utils import MCPServerManager, load_mcp_conf


class AI:
    """
    完整的AI助手类，支持流式、命令执行和完整历史管理
    """
    
    def __init__(self,
                # 基本配置
                mcp_paths=None,
                api_key=None,
                api_base=None,
                model=None,

                # 系统提示
                system_prompt=None,

                # 模型参数
                temperature=1.0,
                max_tokens=2048,
                top_p=1.0,
                stop=None,
                stream=True,  # 默认流式
                presence_penalty=0.0,
                frequency_penalty=0.0,

                # 命令解析
                command_start="YLDEXECUTE:",
                command_separator="￥|",

                # 命令执行
                max_iterations=15,

                # 自定义提示词（可从设置对话框配置）
                command_execution_prompt=None,
                command_retry_prompt=None,
                final_summary_prompt=None,
                max_execution_iterations=3):

        # 工具配置
        self.mcp_paths = mcp_paths or []
        self.funcs = {}

        # API配置
        self.api_key = api_key
        self.api_base = api_base or 'https://api.deepseek.com'
        self.model = model or 'deepseek-chat'
        self.client = None

        # 命令配置
        self.command_start = command_start
        self.command_separator = command_separator
        self.max_iterations = max_iterations

        # 自定义提示词（从配置或使用默认值）
        self.command_execution_prompt = command_execution_prompt or (
            "Execution result: {result}\n\n"
            "CRITICAL INSTRUCTION: If the task is COMPLETE, provide a FINAL SUMMARY in Chinese and then STOP - "
            "do NOT execute any more commands. Only execute another command if this result shows the task is incomplete "
            "and you have a clear next step."
        )

        self.command_retry_prompt = command_retry_prompt or (
            "Execution failed: {error}\n\n"
            "Please analyze the error and retry with a corrected command, or provide an alternative solution."
        )

        self.final_summary_prompt = final_summary_prompt or (
            "Based on all the execution results, please provide a FINAL SUMMARY in Chinese of what was found or accomplished. "
            "This is the FINAL request - after this summary, do NOT execute any more commands. "
            "Just provide the summary and stop."
        )

        self.max_execution_iterations = max_execution_iterations

        # 模型参数
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stop = stop
        self.stream = stream  # 存储流式参数
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty

        # 系统提示 - 使用完整的系统提示
        self.system_prompt = system_prompt or self.get_complete_system_prompt()
        
        # 内部对话历史 - 由外部管理，但这里保留用于处理
        self.conv_his = []
        
        # 执行状态跟踪
        self.execution_status = {
            "status": "idle",
            "tool_name": None,
            "tool_args": None,
            "start_time": None
        }
        
        # 停止标志
        self._stop_flag = False
        
        # 初始化AI客户端
        self.init_ai_client()
        
        # 加载MCP工具
        self.load_mcp_tools()
        
        # 重置对话历史（添加系统提示）
        self.reset_conversation()
        
        print(f"[AI] 初始化完成，加载了 {len(self.funcs)} 个工具，stream={self.stream}")
    
    def get_complete_system_prompt(self):
        """返回完整的系统提示"""
        return f"""
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
    
    # === MCP工具加载 ===
    
    def load_mcp_mod(self, mcp_path):
        """加载一个MCP文件(*.json或*.py)"""
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
                # Python文件
                module_name = os.path.basename(mcp_path).replace('.py', '')
                spec = importlib.util.spec_from_file_location(module_name, mcp_path)
                if spec is None:
                    raise ImportError(f"Cannot load module from {mcp_path}")
                
                mcp_module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mcp_module
                spec.loader.exec_module(mcp_module)
                
                funcs = {}
                for attr_name in dir(mcp_module):
                    attr = getattr(mcp_module, attr_name)
                    if callable(attr) and not attr_name.startswith('_'):
                        funcs[attr_name] = attr
                        
                return mcp_module, funcs
            
        except Exception as e:
            print(f"[Warning] Load failed: {e}")
            return None, {}
    
    def load_mcp_tools(self):
        """从路径加载MCP工具"""
        if not self.mcp_paths:
            print("[Info] No MCP paths provided, skipping tool loading")
            return
        
        # 检查默认工具
        default_tools = []
        ocr_path = "./tools/ocr.py"
        mcp_config_path = "./tools/mcp_config.json"
        
        for tool_path in [ocr_path, mcp_config_path]:
            if os.path.exists(tool_path) and tool_path not in self.mcp_paths:
                self.mcp_paths.append(tool_path)
                print(f"[Info] Added default tool: {tool_path}")
        
        # 验证路径
        valid_paths = []
        for path in self.mcp_paths:
            # 尝试解析相对路径
            if not os.path.isabs(path) and not os.path.exists(path):
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
        
        # 加载有效的MCP文件
        _, self.funcs = self.load_mult_mcp_mod(valid_paths)
        
        # 生成工具描述并更新系统提示
        if self.funcs:
            tools_desc = self.gen_tools_desc()
            current_prompt = self.system_prompt
            
            # 将工具描述添加到系统提示开头
            self.system_prompt = tools_desc + '\n\n' + current_prompt
            self.update_system_prompt(self.system_prompt)
            print("[Info] Updated system prompt with tool descriptions")
    
    def load_mult_mcp_mod(self, mcp_paths):
        """加载多个MCP文件"""
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
    
    def gen_tools_desc(self):
        """生成工具描述"""
        if not self.funcs:
            return ""
        
        desc = "You can use the following tools:\n"
        for func_name, func in self.funcs.items():
            doc = func.__doc__ or "No description"
            # 截断长描述
            if len(doc) > 150:
                doc = doc[:150] + "..."
            desc += f"- {func_name}: {doc}\n"
        
        # 添加使用示例
        desc += f"\nUsage example: {self.command_start} tool_name {self.command_separator} param1 {self.command_separator} param2\n"
        return desc
    
    # === 核心方法 ===
    
    def init_ai_client(self):
        """初始化AI客户端"""
        if not self.api_key:
            # 尝试各种环境变量
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
    
    def set_stop_flag(self, value: bool):
        """设置停止标志"""
        self._stop_flag = value
        if value:
            self.execution_status = {
                "status": "idle",
                "tool_name": None,
                "tool_args": None,
                "start_time": None
            }
            print(f"[Info] Stop flag set to True, execution interrupted")
    
    def get_stop_flag(self):
        """获取当前停止标志值"""
        return self._stop_flag
    
    def exec_func(self, func_name, *args):
        """执行函数，带状态跟踪和停止标志支持"""
        if self.get_stop_flag():
            return "Execution interrupted by user"
        
        if func_name not in self.funcs:
            return f"Error: Function '{func_name}' does not exist"
        
        try:
            # 更新执行状态
            self.execution_status = {
                "status": "executing_tool",
                "tool_name": func_name,
                "tool_args": args,
                "start_time": datetime.now().isoformat()
            }
            
            print(f"[Debug] Executing function: {func_name} with args: {args}")
            
            # 检查停止标志
            if self.get_stop_flag():
                self.execution_status = {
                    "status": "stopped",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                return "Execution interrupted by user before execution"
            
            # 处理MCP函数
            if func_name.startswith('mcp_'):
                kwargs = {}
                for arg in args:
                    if '=' in arg:
                        key, value = arg.split('=', 1)
                        kwargs[key.strip()] = value.strip()
                    elif arg.strip():
                        kwargs['value'] = arg.strip()
                
                print(f"[Debug] Calling MCP function with kwargs: {kwargs}")
                
                # 检查停止标志
                if self.get_stop_flag():
                    self.execution_status = {
                        "status": "stopped",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    return "Execution interrupted by user before MCP execution"
                
                res = self.funcs[func_name](**kwargs)
            else:
                print(f"[Debug] Calling regular function with args: {args}")
                
                # 检查停止标志
                if self.get_stop_flag():
                    self.execution_status = {
                        "status": "stopped",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    return "Execution interrupted by user before function execution"
                
                # 尝试执行函数，如果参数错误，提供更多信息
                try:
                    res = self.funcs[func_name](*args)
                except TypeError as e:
                    # 获取函数签名
                    import inspect
                    func = self.funcs[func_name]
                    sig = inspect.signature(func)
                    expected_args = list(sig.parameters.keys())
                    
                    error_msg = f"Parameter error: {e}\nExpected parameters: {expected_args}"
                    print(f"[Error] {error_msg}")
                    return f"Execution failed: {error_msg}"
            
            print(f"[Debug] Function execution result: {res[:100]}..." if len(str(res)) > 100 else f"[Debug] Function execution result: {res}")
            
            # 重置执行状态
            self.execution_status = {
                "status": "idle",
                "tool_name": None,
                "tool_args": None,
                "start_time": None
            }
            
            return f"Execution successful: {res}"
        
        except Exception as e:
            print(f"[Error] Function execution failed: {e}")
            
            # 重置执行状态
            self.execution_status = {
                "status": "idle",
                "tool_name": None,
                "tool_args": None,
                "start_time": None
            }
            
            return f"Execution failed: {e}"
            
    def process_user_input_with_history(self, user_input: str, external_history: List[Dict] = None) -> str:
        """
        Process user input with external history
        Returns AI's complete response with proper command execution handling
        
        Args:
            user_input: The user's input message
            external_history: External conversation history (optional)
        
        Returns:
            str: AI's complete response
        """
        # Use external history if provided, otherwise use internal history
        if external_history:
            current_history = external_history.copy()
        else:
            current_history = self.conv_his.copy()
        
        # Ensure system prompt is at the beginning
        if not current_history or current_history[0].get("role") != "system":
            current_history.insert(0, {"role": "system", "content": self.system_prompt})
        
        # Add user input to history
        current_history.append({"role": "user", "content": user_input})
        
        iteration = 0
        full_response = ""
        
        print(f"[AI] Processing with history (length: {len(current_history)}), iteration limit: {self.max_iterations}")
        
        while iteration < self.max_iterations:
            if self.get_stop_flag():
                self.set_stop_flag(False)
                self.execution_status = {
                    "status": "idle",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                return "**Execution stopped**\nProcessing was interrupted by user."
            
            try:
                # Prepare API parameters
                api_params = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": current_history,
                    "stream": False  # Non-streaming for internal processing
                }
                
                # Add optional parameters
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
                
                print(f"[AI] Sending request to API with {len(current_history)} messages (iteration {iteration + 1})")
                
                # Execute API call
                response = self.client.chat.completions.create(**api_params)
                get_reply = response.choices[0].message.content
                full_response += get_reply
                
                print(f"[AI] Received reply: {get_reply[:100]}..." if len(get_reply) > 100 else f"[AI] Received reply: {get_reply}")
                
                # Check if AI wants to execute a command
                if get_reply.startswith(self.command_start):
                    print(f"\n[AI][Iteration {iteration + 1}] Command detected: {get_reply}")
                    
                    # Add AI reply to history
                    current_history.append({"role": "assistant", "content": get_reply})
                    
                    # Parse command - extract ONLY the first command
                    # Sometimes AI outputs multiple commands in one response
                    command_line = get_reply
                    
                    # If there are multiple commands, take only the first one
                    if '\n' in get_reply:
                        lines = get_reply.split('\n')
                        for line in lines:
                            if line.startswith(self.command_start):
                                command_line = line
                                break
                    
                    # Parse the command
                    tokens = command_line.replace(self.command_start, "").strip().split(self.command_separator)
                    tokens = [t.strip() for t in tokens if t.strip()]
                    
                    if len(tokens) < 1:
                        res = "Error: Command format is incorrect. Please use: {command_start} tool_name {command_separator} param1 {command_separator} param2"
                    else:
                        func_name = tokens[0]
                        args = tokens[1:] if len(tokens) > 1 else []
                        
                        print(f"[AI] Executing command: {func_name} with args: {args}")
                        
                        # Execute function
                        res = self.exec_func(func_name, *args)
                    
                    print(f"[AI] Command execution result: {res[:200]}...")
                    
                    # Check if command exists
                    if "does not exist" in res or "Error: Function" in res:
                        # Command doesn't exist - add feedback and let AI try again
                        error_feedback = f"Tool '{func_name}' is not available. Please use only available tools from the list provided in the system prompt."
                        current_history.append({
                            "role": "user",
                            "content": error_feedback
                        })
                        
                        # Add a small delay to prevent rapid retries
                        import time
                        time.sleep(0.5)
                        
                        iteration += 1
                        continue
                    
                    # Add execution result to history with guidance
                    current_history.append({
                        "role": "user",
                        "content": f"Execution result: {res}\n\nBased on this result, please decide the next step. If the task is complete or the command failed, provide a final summary in Chinese of what was accomplished or found."
                    })
                    
                    iteration += 1
                    
                else:
                    # No command, processing is complete
                    current_history.append({"role": "assistant", "content": get_reply})
                    self.execution_status = {
                        "status": "idle",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    
                    return full_response
                    
            except Exception as e:
                print(f"[AI] Error processing user input: {e}")
                
                # Reset execution status
                self.execution_status = {
                    "status": "idle",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                
                return f"Error occurred during processing: {e}"
        
        # Reached maximum iterations
        self.execution_status = {
            "status": "idle",
            "tool_name": None,
            "tool_args": None,
            "start_time": None
        }
        
        return f"{full_response}\n\n[Note: Reached maximum execution steps ({self.max_iterations}), task may not be fully completed]"


    def _process_with_history(self, user_input: str, history: List[Dict]) -> str:
        """使用指定历史处理用户输入"""
        if self.get_stop_flag():
            self.set_stop_flag(False)
            return "**Execution stopped**\nProcessing was interrupted by user."
        
        # 设置处理状态
        self.execution_status = {
            "status": "processing",
            "tool_name": None,
            "tool_args": None,
            "start_time": datetime.now().isoformat()
        }
        
        # 添加用户输入到历史
        history.append({"role": "user", "content": user_input})
        
        iteration = 0
        full_response = ""
        
        while iteration < self.max_iterations:
            if self.get_stop_flag():
                print(f"[Info] Stop flag detected, stopping execution at iteration {iteration}")
                self.execution_status = {
                    "status": "idle",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                self.set_stop_flag(False)
                return "**Execution stopped**\nProcessing was interrupted by user."
            
            try:
                # 准备API参数
                api_params = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": history,
                    "stream": False  # 非流式用于内部处理
                }
                
                # 添加可选参数
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
                
                print(f"[Debug] Sending request to API with {len(history)} messages (iteration {iteration + 1})")
                
                # 执行API调用
                response = self.client.chat.completions.create(**api_params)
                get_reply = response.choices[0].message.content
                full_response += get_reply
                
                print(f"[Debug] Received reply: {get_reply[:100]}..." if len(get_reply) > 100 else f"[Debug] Received reply: {get_reply}")
                
                if self.get_stop_flag():
                    self.execution_status = {
                        "status": "idle",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    self.set_stop_flag(False)
                    return "**Execution stopped**\nProcessing was interrupted by user."
                
                if get_reply.startswith(self.command_start):
                    print(f"\n[Iteration {iteration + 1}][AI requested execution] {get_reply}")
                    
                    # 添加AI回复到历史
                    history.append({"role": "assistant", "content": get_reply})
                    
                    # 解析命令
                    tokens = get_reply.replace(self.command_start, "").strip().split(self.command_separator)
                    tokens = [t.strip() for t in tokens]
                    
                    if len(tokens) < 1:
                        res = "Error! Your command format is incorrect"
                    else:
                        func_name = tokens[0]
                        args = tokens[1:] if len(tokens) > 1 else []
                        
                        if self.get_stop_flag():
                            self.execution_status = {
                                "status": "idle",
                                "tool_name": None,
                                "tool_args": None,
                                "start_time": None
                            }
                            self.set_stop_flag(False)
                            return "**Execution stopped**\nProcessing was interrupted by user."
                        
                        # 执行函数
                        res = self.exec_func(func_name, *args)
                    
                    print(f"[Info] AI execution result: {res}")
                    
                    if self.get_stop_flag():
                        self.execution_status = {
                            "status": "idle",
                            "tool_name": None,
                            "tool_args": None,
                            "start_time": None
                        }
                        self.set_stop_flag(False)
                        return "**Execution stopped**\nProcessing was interrupted by user."
                    
                    # 添加执行结果到历史
                    history.append({
                        "role": "user", 
                        "content": f"Execution result: {res}\nPlease decide the next operation based on this result. If the task is complete, please summarize and tell me the result."
                    })
                    
                    iteration += 1
                    
                else:
                    # 没有命令，完成处理
                    history.append({"role": "assistant", "content": get_reply})
                    self.execution_status = {
                        "status": "idle",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    
                    return full_response
                    
            except Exception as e:
                print(f"[Error] Error processing user input: {e}")
                
                if self.get_stop_flag():
                    self.set_stop_flag(False)
                    self.execution_status = {
                        "status": "idle",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    return "**Execution stopped**\nProcessing was interrupted by user."
                
                self.execution_status = {
                    "status": "idle",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                
                return f"Error occurred during processing: {e}"
        
        # 达到最大迭代次数
        self.execution_status = {
            "status": "idle",
            "tool_name": None,
            "tool_args": None,
            "start_time": None
        }
        
        return f"{full_response}\n\n[Note: Reached maximum execution steps ({self.max_iterations}), task may not be fully completed]"
    
    # === 流式处理 ===
    def process_user_input_stream(self, user_input: str, conversation_history: List[Dict], callback=None):
        """流式处理用户输入 - 修复版本，支持命令执行"""
        print(f"[AI] Starting stream processing for: {user_input[:50]}...")
        
        if self.get_stop_flag():
            self.set_stop_flag(False)
            if callback:
                callback("**Execution stopped**\nProcessing was interrupted by user.")
            else:
                yield "**Execution stopped**\nProcessing was interrupted by user."
            return
        
        # 设置处理状态
        self.execution_status = {
            "status": "processing",
            "tool_name": None,
            "tool_args": None,
            "start_time": datetime.now().isoformat()
        }
        
        # 创建历史副本
        history = conversation_history.copy()
        
        # 确保系统提示
        if not history or history[0].get("role") != "system":
            history.insert(0, {"role": "system", "content": self.system_prompt})
        
        # 添加用户输入
        history.append({"role": "user", "content": user_input})

        iteration = 0
        full_response = ""
        summary_requested = False  # Flag to track if we've already requested a summary

        while iteration < self.max_iterations:
            if self.get_stop_flag():
                self.execution_status = {
                    "status": "idle",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                self.set_stop_flag(False)
                if callback:
                    callback("**Execution stopped**\nProcessing was interrupted by user.")
                else:
                    yield "**Execution stopped**\nProcessing was interrupted by user."
                return
            
            try:
                # 准备API参数
                api_params = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": history,
                    "stream": True,  # 关键：启用流式
                    "max_tokens": self.max_tokens or 2048
                }
                
                print(f"[AI] Sending stream request with {len(history)} messages (iteration {iteration + 1})")
                
                # 调用流式API
                response = self.client.chat.completions.create(**api_params)
                
                # 处理流式响应
                current_response = ""
                for chunk in response:
                    if self.get_stop_flag():
                        break
                    
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        current_response += content
                        full_response += content
                        
                        # 发送内容
                        if callback:
                            callback(content)
                        else:
                            yield content
                
                print(f"[AI] Stream iteration {iteration + 1} complete: {current_response[:100]}...")
                
                # 检查是否AI想要执行命令
                if current_response.startswith(self.command_start):
                    print(f"[AI] Command detected in response: {current_response}")
                    
                    # 添加AI回复到历史
                    history.append({"role": "assistant", "content": current_response})
                    
                    # 解析命令
                    tokens = current_response.replace(self.command_start, "").strip().split(self.command_separator)
                    tokens = [t.strip() for t in tokens]
                    
                    if len(tokens) < 1:
                        res = "Error! Your command format is incorrect"
                    else:
                        func_name = tokens[0]
                        args = tokens[1:] if len(tokens) > 1 else []
                        
                        # 执行函数
                        res = self.exec_func(func_name, *args)
                    
                    print(f"[AI] Command execution result: {res}")

                    # 添加执行结果到历史（使用自定义提示词）
                    history.append({
                        "role": "user",
                        "content": self.command_execution_prompt.format(result=res)
                    })

                    iteration += 1

                    # 如果执行失败，AI应该重新尝试（使用自定义重试提示词）
                    if ("Execution failed" in res or "Error" in res) and iteration < 2:
                        print("[AI] Command execution failed, removing failed command from history")
                        # Remove the failed command and execution prompt from history
                        if len(history) >= 2:
                            history.pop()  # Remove execution prompt
                            history.pop()  # Remove command response
                            print(f"[AI] Removed failed command, history size now: {len(history)}")

                        history.append({
                            "role": "user",
                            "content": self.command_retry_prompt.format(error=res)
                        })
                        continue

                    # 如果执行成功，让AI决定是否需要继续
                    if "Execution successful" in res:
                        # 继续下一个迭代，但AI应该主动停止
                        print("[AI] Command executed successfully, AI will decide next step")
                        # 给AI一次机会决定是否继续，但限制总迭代次数
                        if iteration >= self.max_execution_iterations:  # 使用配置的迭代次数
                            print(f"[AI] Reached safety limit ({self.max_execution_iterations}), requesting final summary")
                            history.append({
                                "role": "user",
                                "content": self.final_summary_prompt
                            })
                            summary_requested = True  # Mark that we've requested summary
                            continue
                        else:
                            continue
                    else:
                        # 不是明确成功，直接请求总结（不要再继续了）
                        print("[AI] Command execution did not succeed, requesting summary")
                        history.append({
                            "role": "user",
                            "content": self.final_summary_prompt
                        })
                        summary_requested = True
                        iteration += 1
                        continue
                        
                else:
                    # 没有命令执行，完成处理
                    history.append({"role": "assistant", "content": current_response})

                    # 检查是否需要总结（只在第一次请求）
                    if iteration > 0 and not summary_requested:
                        # 如果已经执行过命令，让AI总结结果（使用自定义总结提示词）
                        print("[AI] Requesting final summary...")
                        history.append({
                            "role": "user",
                            "content": self.final_summary_prompt
                        })

                        summary_requested = True  # Mark that we've requested summary
                        iteration += 1
                        continue  # 最后一次迭代获取总结
                    else:
                        # 已经请求过总结，或没有执行过命令，直接结束
                        if summary_requested:
                            print("[AI] Summary provided, completing task")
                        break
                        
            except Exception as e:
                print(f"[AI] Stream API error: {e}")
                error_msg = f"Error in stream processing: {str(e)}"
                
                if callback:
                    callback(error_msg)
                else:
                    yield error_msg
                break
        
        # 重置状态
        self.execution_status = {
            "status": "idle",
            "tool_name": None,
            "tool_args": None,
            "start_time": None
        }

        # CRITICAL: 将处理后的历史保存回 self.conv_his
        # 这样下次对话时才能记住上下文
        self.conv_his = history.copy()
        print(f"[AI] Updated conv_his with {len(self.conv_his)} messages")

        # 确保生成器正确结束（无论是否使用callback）
        yield ""  # 确保生成器结束


    def _process_user_inp_stream_internal(self, user_input: str, history: List[Dict], callback=None):
        """内部流式处理方法 - 保持原始逻辑"""
        if not user_input:
            yield ""
            return

        max_iter = self.max_iterations
        
        # 检查停止标志
        if self.get_stop_flag():
            self.set_stop_flag(False)
            self.execution_status = {
                "status": "idle",
                "tool_name": None,
                "tool_args": None,
                "start_time": None
            }
            yield "**Execution stopped**\nProcessing was interrupted by user."
            return
        
        # 设置执行状态
        self.execution_status = {
            "status": "processing",
            "tool_name": None,
            "tool_args": None,
            "start_time": datetime.now().isoformat()
        }
        
        iteration = 0
        while iteration < max_iter:
            # 检查停止标志
            if self.get_stop_flag():
                print(f"[Info] Stop flag detected, stopping execution at iteration {iteration}")
                self.execution_status = {
                    "status": "idle",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                self.set_stop_flag(False)
                yield "**Execution stopped**\nProcessing was interrupted by user."
                return
            
            try:
                # 准备API参数
                api_params = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": history,
                    "stream": True
                }
                
                # 添加可选参数
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
                
                print(f"[Debug] Sending stream request to API with {len(history)} messages (iteration {iteration + 1})")
                
                # 执行流式API调用
                response = self.client.chat.completions.create(**api_params)
                
                # 收集响应
                collected_chunks = []
                collected_messages = []
                
                # 处理流式响应
                for chunk in response:
                    # 检查停止标志
                    if self.get_stop_flag():
                        self.execution_status = {
                            "status": "idle",
                            "tool_name": None,
                            "tool_args": None,
                            "start_time": None
                        }
                        self.set_stop_flag(False)
                        yield "**Execution stopped**\nProcessing was interrupted by user."
                        return
                    
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        collected_chunks.append(chunk)
                        collected_messages.append(content)
                        
                        # 发送实时内容
                        if callback:
                            callback(content)
                        else:
                            yield content
                
                # 合并收集的消息
                full_reply = ''.join(collected_messages)
                print(f"[Debug] Full reply received (iteration {iteration + 1}): {full_reply[:100]}..." if len(full_reply) > 100 else f"[Debug] Full reply received: {full_reply}")
                
                # 检查是否AI想要执行命令
                if self.command_start in full_reply:
                    print(f"\n[Iteration {iteration + 1}][AI requested execution] {full_reply}")
                    
                    # 提取命令部分
                    if full_reply.startswith(self.command_start):
                        command_line = full_reply
                    else:
                        # 从回复中提取命令
                        start_idx = full_reply.find(self.command_start)
                        command_line = full_reply[start_idx:].split('\n')[0].strip()
                    
                    # 解析命令
                    command_text = command_line.replace(self.command_start, "").strip()
                    tokens = command_text.split(self.command_separator)
                    tokens = [t.strip() for t in tokens]
                    
                    if len(tokens) < 1:
                        res = "Error! Your command format is incorrect"
                    else:
                        func_name = tokens[0]
                        args = tokens[1:] if len(tokens) > 1 else []
                        
                        # 检查停止标志
                        if self.get_stop_flag():
                            self.execution_status = {
                                "status": "idle",
                                "tool_name": None,
                                "tool_args": None,
                                "start_time": None
                            }
                            self.set_stop_flag(False)
                            yield "**Execution stopped**\nProcessing was interrupted by user."
                            return
                        
                        # 执行函数
                        res = self.exec_func(func_name, *args)
                    
                    print(f"[Info] AI execution result: {res}")
                    
                    # 检查停止标志
                    if self.get_stop_flag():
                        self.execution_status = {
                            "status": "idle",
                            "tool_name": None,
                            "tool_args": None,
                            "start_time": None
                        }
                        self.set_stop_flag(False)
                        yield "**Execution stopped**\nProcessing was interrupted by user."
                        return
                    
                    # 添加回复和结果到对话历史
                    history.append({"role": "assistant", "content": full_reply})
                    history.append({
                        "role": "user", 
                        "content": f"Execution result: {res}\nPlease decide the next operation based on this result. If the task is complete, please summarize and tell me the result."
                    })
                    
                    # 流式命令执行结果
                    result_message = f"\n\n**Command Execution Result**\n```\n{res}\n```"
                    
                    # 发送结果
                    if callback:
                        callback(result_message)
                    else:
                        yield result_message
                    
                    iteration += 1
                    
                    # 如果执行成功，继续下一个迭代
                    if "Execution successful" in res:
                        print(f"[Info] Command executed successfully, continuing to next iteration")
                        continue
                    else:
                        # 如果执行失败，AI应该重新尝试
                        print(f"[Info] Command execution failed, AI should retry")
                        continue
                    
                else:
                    # 没有命令执行，完成处理
                    history.append({"role": "assistant", "content": full_reply})
                    self.execution_status = {
                        "status": "idle",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    return
                    
            except Exception as e:
                print(f"[Error] Error processing user input: {e}")
                
                # 检查是否是stop导致的错误
                if self.get_stop_flag():
                    self.set_stop_flag(False)
                    self.execution_status = {
                        "status": "idle",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    yield "**Execution stopped**\nProcessing was interrupted by user."
                    return
                
                # 重置执行状态
                self.execution_status = {
                    "status": "idle",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                
                yield f"Error occurred during processing: {e}"
                return
        
        # 达到最大迭代次数
        self.execution_status = {
            "status": "idle",
            "tool_name": None,
            "tool_args": None,
            "start_time": None
        }
        
        yield f"Reached maximum execution steps ({max_iter}), task may not be fully completed"
    
    # === 兼容性方法 ===
    
    def process_user_inp(self, user_inp, max_iter=None):
        """兼容性方法 - 处理用户输入"""
        if self.stream:
            # 流式处理 - 返回生成器
            return self._process_user_inp_stream_internal(user_inp, self.conv_his)
        else:
            # 非流式处理 - 返回元组
            return self._process_user_inp_non_stream(user_inp, max_iter)
    
    def _process_user_inp_non_stream(self, user_inp, max_iter=None):
        """非流式处理用户输入 - 保持原始逻辑"""
        if not user_inp:
            return "", False

        max_iter = max_iter or self.max_iterations
        
        # 检查停止标志
        if self.get_stop_flag():
            self.set_stop_flag(False)
            self.execution_status = {
                "status": "idle",
                "tool_name": None,
                "tool_args": None,
                "start_time": None
            }
            return "**Execution stopped**\nProcessing was interrupted by user.", True
        
        self.execution_status = {
            "status": "processing",
            "tool_name": None,
            "tool_args": None,
            "start_time": datetime.now().isoformat()
        }
        
        self.conv_his.append({"role": "user", "content": user_inp})
        
        for step in range(max_iter):
            if self.get_stop_flag():
                print(f"[Info] Stop flag detected, stopping execution at step {step+1}")
                self.execution_status = {
                    "status": "idle",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                self.set_stop_flag(False)
                return "**Execution stopped**\nProcessing was interrupted by user.", True
            
            try:
                api_params = {
                    "model": self.model,
                    "temperature": self.temperature,
                    "messages": self.conv_his,
                    "stream": False  # 非流式
                }
                
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
                
                print(f"[Debug] Sending non-stream request to API with {len(self.conv_his)} messages")
                
                response = self.client.chat.completions.create(**api_params)
                get_reply = response.choices[0].message.content
                print(f"[Debug] Received reply: {get_reply[:100]}..." if len(get_reply) > 100 else f"[Debug] Received reply: {get_reply}")
                
                if self.get_stop_flag():
                    self.execution_status = {
                        "status": "idle",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    self.set_stop_flag(False)
                    return "**Execution stopped**\nProcessing was interrupted by user.", True
                
                if get_reply.startswith(self.command_start):
                    print(f"\n[Step {step + 1}][AI requested execution] {get_reply}")
                    
                    tokens = get_reply.replace(self.command_start, "").strip().split(self.command_separator)
                    tokens = [t.strip() for t in tokens]
                    
                    if len(tokens) < 1:
                        res = "Error! Your command format is incorrect"
                    else:
                        func_name = tokens[0]
                        args = tokens[1:] if len(tokens) > 1 else []
                        
                        if self.get_stop_flag():
                            self.execution_status = {
                                "status": "idle",
                                "tool_name": None,
                                "tool_args": None,
                                "start_time": None
                            }
                            self.set_stop_flag(False)
                            return "**Execution stopped**\nProcessing was interrupted by user.", True
                        
                        res = self.exec_func(func_name, *args)
                    
                    print(f"[Info] AI execution result: {res}")
                    
                    if self.get_stop_flag():
                        self.execution_status = {
                            "status": "idle",
                            "tool_name": None,
                            "tool_args": None,
                            "start_time": None
                        }
                        self.set_stop_flag(False)
                        return "**Execution stopped**\nProcessing was interrupted by user.", True
                    
                    self.conv_his.append({"role": "assistant", "content": get_reply})
                    self.conv_his.append({
                        "role": "user", 
                        "content": f"Execution result: {res}\nPlease decide the next operation based on this result. If the task is complete, please summarize and tell me the result."
                    })
                    
                else:
                    self.conv_his.append({"role": "assistant", "content": get_reply})
                    
                    self.execution_status = {
                        "status": "idle",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    
                    return get_reply, True
                    
            except Exception as e:
                print(f"[Error] Error processing user input: {e}")
                
                if self.get_stop_flag():
                    self.set_stop_flag(False)
                    self.execution_status = {
                        "status": "idle",
                        "tool_name": None,
                        "tool_args": None,
                        "start_time": None
                    }
                    return "**Execution stopped**\nProcessing was interrupted by user.", True
                
                self.execution_status = {
                    "status": "idle",
                    "tool_name": None,
                    "tool_args": None,
                    "start_time": None
                }
                
                return f"Error occurred during processing: {e}", True
        
        self.execution_status = {
            "status": "idle",
            "tool_name": None,
            "tool_args": None,
            "start_time": None
        }
        
        return f"Reached maximum execution steps ({max_iter}), task may not be fully completed", False
    
    # === 历史管理 ===
    
    def reset_conversation(self):
        """重置对话历史"""
        self.conv_his = [{"role": "system", "content": self.system_prompt}]
        print("[AI] Conversation history reset")
    
    def load_conversation_history(self, history_messages: List[Dict]):
        """加载对话历史到AI上下文"""
        print(f"[AI] Loading {len(history_messages)} conversation history messages")
        
        # 重置对话
        self.reset_conversation()
        
        # 添加历史消息到对话
        for msg in history_messages:
            role = "user" if msg.get("is_sender", False) else "assistant"
            content = msg.get("text", "")
            
            # 跳过空消息
            if content and content.strip():
                self.conv_his.append({"role": role, "content": content})
        
        print(f"[AI] Conversation history loaded. Total messages: {len(self.conv_his)}")
    
    def get_current_history(self) -> List[Dict]:
        """获取当前对话历史"""
        return self.conv_his.copy()
    
    def set_current_history(self, history: List[Dict]):
        """设置当前对话历史"""
        self.conv_his = history.copy()
        print(f"[AI] History set with {len(self.conv_his)} messages")
    
    # === 配置方法 ===
    
    def update_system_prompt(self, new_prompt: str):
        """更新系统提示"""
        self.system_prompt = new_prompt
        for i, msg in enumerate(self.conv_his):
            if msg.get("role") == "system":
                self.conv_his[i]["content"] = new_prompt
                break
        else:
            self.conv_his.insert(0, {"role": "system", "content": new_prompt})
    
    def update_config(self, config_dict: Dict):
        """从字典更新配置，不创建新实例"""
        print(f"[AI] Updating AI configuration for existing instance")
        
        # 更新API配置
        if 'api_key' in config_dict and config_dict['api_key']:
            self.api_key = config_dict['api_key']
        
        if 'api_base' in config_dict and config_dict['api_base']:
            self.api_base = config_dict['api_base']
        
        if 'model' in config_dict and config_dict['model']:
            self.model = config_dict['model']
            
        # 重新初始化客户端
        if any(key in config_dict for key in ['api_key', 'api_base', 'model']):
            self.init_ai_client()
        
        # 更新模型参数
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
            print(f"[AI] Stream mode updated to: {self.stream}")
        
        if 'presence_penalty' in config_dict:
            self.presence_penalty = config_dict['presence_penalty']
        
        if 'frequency_penalty' in config_dict:
            self.frequency_penalty = config_dict['frequency_penalty']
        
        # 更新命令配置
        if 'command_start' in config_dict:
            self.command_start = config_dict['command_start']
        
        if 'command_separator' in config_dict:
            self.command_separator = config_dict['command_separator']
        
        if 'max_iterations' in config_dict:
            self.max_iterations = config_dict['max_iterations']
        
        # 更新系统提示
        if 'system_prompt' in config_dict and config_dict['system_prompt']:
            self.system_prompt = config_dict['system_prompt']
            self.update_system_prompt(self.system_prompt)
        
        # 更新MCP路径并重新加载工具
        if 'mcp_paths' in config_dict:
            new_paths = config_dict['mcp_paths']
            if set(new_paths) != set(self.mcp_paths):
                print(f"[AI] MCP paths changed, reloading tools")
                self.mcp_paths = new_paths
                self.load_mcp_tools()

        # 更新自定义提示词
        if 'command_execution_prompt' in config_dict and config_dict['command_execution_prompt']:
            self.command_execution_prompt = config_dict['command_execution_prompt']

        if 'command_retry_prompt' in config_dict and config_dict['command_retry_prompt']:
            self.command_retry_prompt = config_dict['command_retry_prompt']

        if 'final_summary_prompt' in config_dict and config_dict['final_summary_prompt']:
            self.final_summary_prompt = config_dict['final_summary_prompt']

        if 'max_execution_iterations' in config_dict:
            self.max_execution_iterations = config_dict['max_execution_iterations']
            print(f"[AI] Max execution iterations updated to: {self.max_execution_iterations}")

        print(f"[AI] Configuration updated successfully, stream={self.stream}")
    
    def get_config(self) -> Dict:
        """获取当前配置字典"""
        return {
            # API配置
            "api_base": self.api_base,
            "model": self.model,
            
            # 提示配置
            "system_prompt": self.system_prompt,
            
            # 模型参数
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stop": self.stop,
            "stream": self.stream,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            
            # 命令执行配置
            "command_start": self.command_start,
            "command_separator": self.command_separator,
            "max_iterations": self.max_iterations,
            
            # 工具配置
            "mcp_paths": self.mcp_paths.copy(),
            "available_tools": list(self.funcs.keys())
        }
    
    def get_execution_status(self) -> Dict:
        """获取当前执行状态用于状态栏显示"""
        return self.execution_status.copy()
    
    def get_available_tools(self) -> List[Dict]:
        """获取可用工具列表"""
        tools = []
        for func_name, func in self.funcs.items():
            doc = func.__doc__ or "No description"
            tools.append({"name": func_name, "description": doc})
        return tools
    
    def print_tools_list(self):
        """打印可用工具列表"""
        print("\nAvailable tools:")
        tools = self.get_available_tools()
        for i, tool in enumerate(tools, 1):
            print(f"{i:2}. {tool['name']}: {tool['description'][:60]}...")


# 配置文件加载函数
def load_config_from_file(config_path: str) -> Optional[Dict]:
    """从文件加载配置(JSON或YAML)"""
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


def create_ai_from_config(config_path: str) -> Optional[AI]:
    """从配置文件创建AI实例"""
    config = load_config_from_file(config_path)
    if not config:
        return None
    
    # 提取配置参数
    mcp_paths = config.get("mcp_paths", [])
    api_key = config.get("api_key")
    
    # 创建AI实例
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
        stream=config.get("stream", True),
        presence_penalty=config.get("presence_penalty", 0.0),
        frequency_penalty=config.get("frequency_penalty", 0.0),
        command_start=config.get("command_start", "YLDEXECUTE:"),
        command_separator=config.get("command_separator", "￥|"),
        max_iterations=config.get("max_iterations", 15)
    )
    
    return ai


def save_config_to_file(ai_instance: AI, config_path: str) -> bool:
    """将AI实例配置保存到文件"""
    config = ai_instance.get_config()
    config["api_key"] = ai_instance.api_key  # 警告：保存API密钥需谨慎
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"[Info] Configuration saved to {config_path}")
        return True
    except Exception as e:
        print(f"[Error] Failed to save configuration: {e}")
        return False


if __name__ == "__main__":
    """主控制台界面"""
    print("Lynexus AI Assistant - Console Interface")
    
    # 简单测试
    ai = AI(stream=True)
    
    print(f"\nAI initialized with {len(ai.funcs)} tools")
    print("Type 'exit' to quit, 'tools' to list tools, 'clear' to clear history")
    
    while True:
        try:
            user_input = input("\n>> ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye', '退出', '再见']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            if user_input.lower() in ['clear', '清空']:
                ai.reset_conversation()
                print("Conversation history cleared")
                continue
            
            if user_input.lower() == 'tools':
                ai.print_tools_list()
                continue
            
            if user_input.lower() == 'config':
                config = ai.get_config()
                print("\nCurrent configuration:")
                for key, value in config.items():
                    print(f"  {key}: {value}")
                continue
            
            if ai.stream:
                # 流式模式
                print("\n[AI] ", end="", flush=True)
                for chunk in ai.process_user_inp(user_input):
                    if chunk:
                        print(chunk, end="", flush=True)
                print()
            else:
                # 非流式模式
                response, completed = ai.process_user_inp(user_input)
                if response:
                    print(f"\n[AI] {response}")
            
        except KeyboardInterrupt:
            print("\n[Info] Operation interrupted")
            break
        except Exception as e:
            print(f"\n[Error] Error: {e}")
            continue