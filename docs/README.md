# Lynexus AI Assistant - Complete User Guide

## 1. Normal Usage

### 1.1 Launching the Application

#### From Source Code:
```bash
# Make sure you have Python 3.8+ installed
python main.py
```

#### From Executable (Windows):
- Download the latest release from GitHub
- Extract the ZIP file
- Run `Lynexus.exe`

### 1.2 Initial Setup

When you first launch Lynexus, you'll see the initialization dialog:

1. **Select API Provider**: Choose from DeepSeek, OpenAI, Anthropic, Local, or Custom
2. **Enter API Key**: Input your API key (you can also load from a config file)
3. **Configure Model Settings**:
   - API Base URL: Usually provided by your API provider
   - Model: Select the model you want to use
4. **Add MCP Tools (Optional)**: Click "Select MCP Files" to add custom tools
5. **Click "Start Lynexus"** to begin

### 1.3 Basic Chat Interface

The main interface has three sections:

**Left Sidebar**:
- **New Chat**: Create a new conversation
- **Conversations List**: Switch between different chat sessions
- **Action Buttons**: Settings, Tools, Export, etc.

**Main Chat Area**:
- **Message Display**: Shows chat history with modern bubble design
- **Input Box**: Type your messages here
- **Send Button**: Submit your message (Ctrl+Enter shortcut)

**Status Bar**:
- Shows connection status, model info, and tool count
- Displays execution status when AI is running commands

### 1.4 Sending Messages

1. Type your message in the input box
2. Press Enter or click the Send button
3. The AI will process your request and respond
4. If the AI needs to execute commands, you'll see real-time status updates

### 1.5 Managing Conversations

**Create New Chat**:
- Click "New Chat" in the sidebar
- Enter a name for the conversation
- The new chat will appear in your conversations list

**Switch Between Chats**:
- Click any conversation in the sidebar
- Each chat maintains its own history and AI configuration

**Export Chat History**:
- Click "Export Chat" in the sidebar
- Choose format (TXT, JSON, or Markdown)
- Select save location (defaults to Desktop)

**Clear Current Chat**:
- Click "Clear Chat" in the sidebar
- Confirm to delete all messages in the current conversation

## 2. How to Set Up Presets

### 2.1 What Are Presets?

Presets are complete AI configurations that include:
- API settings (base URL, model)
- Model parameters (temperature, max tokens, etc.)
- System prompt
- Command execution settings
- MCP tool configurations

### 2.2 Creating Your First Preset

#### Method 1: Through Settings Dialog

1. Click "Settings" in the sidebar
2. Configure all desired parameters:
   - **API Configuration**: Provider, API Key, Model
   - **Model Parameters**: Temperature, Max Tokens, Top P, etc.
   - **Command Configuration**: Command markers and separators
   - **System Prompt**: Custom instructions for the AI
   - **MCP Tools**: Add custom tool files
3. Click "Save Settings" to apply to current conversation
4. Click "Save As Config" to export as a preset file

#### Method 2: Direct Configuration via AI Class

For advanced users, you can create presets programmatically:

```python
from aiclass import AI

# Create AI instance with custom configuration
my_preset = AI(
    api_key="your_api_key_here",
    api_base="https://api.deepseek.com",
    model="deepseek-chat",
    temperature=0.7,
    max_tokens=4096,
    system_prompt="You are a helpful coding assistant...",
    command_start="EXECUTE:",
    command_separator="|",
    mcp_paths=["./tools/my_tool.py", "./tools/mcp_config.json"]
)
```

### 2.3 Saving Presets to Files

1. In Settings dialog, click "Save As Config"
2. Choose save location and filename
3. Select format (JSON recommended)
4. The preset will be saved without your API key for security

**Example JSON Preset Structure**:
```json
{
    "name": "My Coding Assistant",
    "version": "1.0.0",
    "api_base": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "temperature": 0.7,
    "max_tokens": 4096,
    "top_p": 1.0,
    "presence_penalty": 0.0,
    "frequency_penalty": 0.0,
    "command_start": "EXECUTE:",
    "command_separator": "|",
    "max_iterations": 15,
    "system_prompt": "You are an expert Python programmer...",
    "mcp_paths": [
        "./tools/code_analyzer.py",
        "./tools/file_manager.json"
    ]
}
```

### 2.4 Best Practices for Preset Creation

**For Coding Assistants**:
- Lower temperature (0.3-0.7) for more deterministic code
- Include MCP tools for file operations
- Add system prompt with coding guidelines

**For Creative Writing**:
- Higher temperature (0.8-1.2) for more varied output
- Include tools for research and reference
- System prompt with style guidelines

**For Research Assistants**:
- Balanced temperature (0.5-0.8)
- Include web search and data analysis tools
- System prompt emphasizing accuracy and citation

## 3. How to Import Presets

### 3.1 Importing from File

1. Click "Import Config" in the sidebar
2. Select a preset file (.json or .yaml format)
3. The configuration will be applied to your current conversation
4. MCP tools will be automatically loaded

### 3.2 Importing During Initialization

1. In the initialization dialog, click "Load Config File"
2. Select your preset file
3. All settings will be populated automatically
4. Adjust any settings if needed
5. Click "Start Lynexus"

### 3.3 Sharing Presets with Others

**To Share Your Preset**:
1. Export your configuration (Settings → Save As Config)
2. Share the JSON/YAML file
3. **Important**: Never share your `.confignore` file or files containing API keys

**To Use Shared Presets**:
1. Download the preset file from the source
2. Import it using the methods above
3. Add your own API key in Settings

### 3.4 Community Preset Repository

Lynexus supports a community-driven preset system. You can:
1. Browse presets on the community forum
2. Download presets that match your needs
3. Import and use them instantly
4. Rate and review presets to help others

## 4. Troubleshooting Common Errors

### 4.1 API Connection Errors

**Error: "No API key provided"**
- **Solution**: 
  1. Check if API key is set in Settings
  2. Verify environment variables (DEEPSEEK_API_KEY, OPENAI_API_KEY)
  3. Try re-entering your API key

**Error: "Failed to connect to API"**
- **Solution**:
  1. Check your internet connection
  2. Verify API base URL is correct
  3. Ensure API key has sufficient credits/permissions
  4. Try a different model or provider

### 4.2 MCP Tool Errors

**Error: "MCP file not found"**
- **Solution**:
  1. Verify file paths in configuration
  2. Check if files exist at specified locations
  3. Use absolute paths or relative paths from the application directory

**Error: "Function execution failed"**
- **Solution**:
  1. Check tool dependencies are installed
  2. Verify tool parameters are correct
  3. Check tool permissions (for file operations)

### 4.3 Command Execution Errors

**Error: "Maximum execution steps reached"**
- **Solution**:
  1. Increase max_iterations in Settings
  2. Simplify your request into smaller steps
  3. Use "continue" command for multi-step operations

**Error: "Command syntax incorrect"**
- **Solution**:
  1. Check command_start and command_separator settings
  2. Ensure AI is using the correct format
  3. Review system prompt for command guidelines

### 4.4 UI/Application Errors

**Error: "Failed to load conversation history"**
- **Solution**:
  1. Check file permissions
  2. Verify config directory exists
  3. Try resetting configuration (backup first)

**Error: "Application crashes on startup"**
- **Solution**:
  1. Check Python version (requires 3.8+)
  2. Install all dependencies: ```pip install -r requirements.txt```
  3. Check for conflicting Python installations

## 5. Advanced Usage

### 5.1 Custom MCP Tool Development

**Creating Python MCP Tools**:
1. Create a Python file in the tools directory
2. Define functions with proper docstrings
3. Functions will be automatically discovered

```python
# Example: ./tools/calculator.py
def add_numbers(a: float, b: float) -> float:
    ```
    Add two numbers together.
    
    Parameters:
    a: First number
    b: Second number
    
    Returns:
    Sum of a and b
    ```
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    ```
    Multiply two numbers.
    
    Parameters:
    a: First number
    b: Second number
    
    Returns:
    Product of a and b
    ```
    return a * b
```

**Creating JSON MCP Configurations**:
1. Create a JSON file defining MCP servers
2. Follow MCP specification format
3. Place in tools directory or any accessible location

### 5.2 Custom System Prompts

**Advanced Prompt Engineering**:
- Use the system prompt to define AI behavior
- Include examples of correct command usage
- Set constraints and guidelines
- Define response formats

```text
Example Advanced System Prompt:

You are Lynexus AI, an assistant that can execute commands.

COMMAND FORMAT:
{command_start}tool_name{command_separator}param1{command_separator}param2

RULES:
1. When user asks for an operation, output ONLY the command line
2. When user asks a question, answer directly
3. Always validate parameters before execution
4. If unsure, ask for clarification

AVAILABLE TOOLS:
- file_read: Read file contents
- file_write: Write to file
- web_search: Search the web

EXAMPLES:
User: "What's the weather?"
AI: "I need to use a weather tool. Please add a weather MCP tool."

User: "Read config.txt"
AI: "{command_start}file_read{command_separator}config.txt"
```

### 5.3 Multi-Conversation Management

**Separate AI Instances per Conversation**:
- Each chat maintains independent AI configuration
- History is preserved separately
- Perfect for different projects or contexts

**Sharing Configuration Between Conversations**:
1. Export configuration from one conversation
2. Import into another conversation
3. All settings will be copied

### 5.4 Command Line Interface

**Running AI from Terminal**:
```bash
# Run the console interface
python aiclass.py

# Create AI from config file
python -c "
from aiclass import create_ai_from_config
ai = create_ai_from_config('my_config.json')
response = ai.process_user_inp('Hello, world!')
print(response)
"
```

**Batch Processing with AI**:
```python
from aiclass import AI

# Initialize AI
ai = AI(api_key="your_key", model="deepseek-chat")

# Process multiple inputs
inputs = ["First request", "Second request", "Third request"]
for inp in inputs:
    response, completed = ai.process_user_inp(inp)
    print(f"Input: {inp}")
    print(f"Response: {response}")
    print("-" * 50)
    ai.reset_conversation()  # Clear history for next request
```

### 5.5 Integration with Other Systems

**Webhook Integration**:
- Use Lynexus as an AI backend
- Create REST API wrapper around the AI class
- Process requests from web applications

**Automation Scripts**:
- Schedule regular AI tasks
- Process files and generate reports
- Monitor systems and alert on conditions

**Development Workflow Integration**:
- Code review assistance
- Automated testing suggestions
- Documentation generation

## 6. Complete Parameter Reference

### 6.1 API Configuration Parameters

#### api_key
**Purpose**: Authentication key for accessing AI API services
**Data Range**: String (typically 40-60 characters starting with "sk-")
**Default**: None (reads from environment variables if available)
**Examples & Effects**:
- Correct: `"sk-1234567890abcdef1234567890abcdef"`
  - Result: Successful API authentication
- Empty: `""`
  - Result: Error: "No API key provided and no API key found in environment variables"
- Invalid: `"invalid_key"`
  - Result: API returns 401 Unauthorized error

#### api_base
**Purpose**: Base URL for the AI API endpoint
**Data Range**: Valid URL string
**Default**: `"https://api.deepseek.com"`
**Examples & Effects**:
- DeepSeek: `"https://api.deepseek.com"`
  - Result: Connects to DeepSeek's official API
- OpenAI: `"https://api.openai.com/v1"`
  - Result: Connects to OpenAI's API
- Local: `"http://localhost:11434"`
  - Result: Connects to local Ollama server
- Invalid: `"not-a-url"`
  - Result: Connection failed, network error

#### model
**Purpose**: Specifies which AI model to use
**Data Range**: String, model name supported by the API
**Default**: `"deepseek-chat"`
**Examples & Effects**:
- DeepSeek: `"deepseek-chat"`
  - Result: Uses DeepSeek's standard chat model
- DeepSeek V3: `"deepseek-chat"`
  - Result: Uses latest DeepSeek V3 model
- OpenAI: `"gpt-4-turbo"`
  - Result: Uses GPT-4 Turbo model
- Anthropic: `"claude-3-opus-20240229"`
  - Result: Uses Claude 3 Opus model
- Invalid: `"nonexistent-model"`
  - Result: API returns model not found error

### 6.2 Model Behavior Parameters

#### temperature
**Purpose**: Controls randomness/creativity of responses
**Data Range**: 0.0 to 2.0 (float)
**Default**: 1.0
**Examples & Effects**:
- 0.0: Completely deterministic
  - Result: Always gives the same response for identical inputs
  - Use case: Code generation, factual answers
- 0.5: Balanced
  - Result: Consistent but with some variation
  - Use case: Technical writing, analysis
- 1.0: Default creativity
  - Result: Natural, varied responses
  - Use case: General conversation
- 1.5: High creativity
  - Result: More surprising, creative outputs
  - Use case: Creative writing, brainstorming
- 2.0: Maximum randomness
  - Result: Highly unpredictable responses
  - Use case: Idea generation, exploration

#### max_tokens
**Purpose**: Maximum number of tokens in the generated response
**Data Range**: 1 to 8192 (or API limit, 0 for no limit)
**Default**: 2048
**Examples & Effects**:
- 512: Very short responses
  - Result: Concise answers, may be cut off
  - Use case: Quick questions, summaries
- 2048: Standard length
  - Result: Complete paragraphs, typical conversation
  - Use case: Most general purposes
- 4096: Long responses
  - Result: Detailed explanations, essays
  - Use case: Complex analysis, documentation
- 8192: Maximum practical length
  - Result: Very detailed, comprehensive responses
  - Use case: Report generation, long-form content
- 0 or None: No limit
  - Result: Uses API's maximum limit
  - Use case: When you need complete answers regardless of length

#### top_p
**Purpose**: Nucleus sampling - controls diversity via probability mass
**Data Range**: 0.0 to 1.0 (float)
**Default**: 1.0
**Examples & Effects**:
- 0.1: Very focused
  - Result: Only considers most probable tokens
  - Use case: Factual, precise answers
- 0.5: Balanced sampling
  - Result: Considers likely tokens, excludes unlikely ones
  - Use case: General conversation
- 0.9: Broad sampling
  - Result: Includes more diverse token choices
  - Use case: Creative tasks
- 1.0: No filtering (default)
  - Result: All tokens considered
  - Use case: When you want maximum diversity

#### presence_penalty
**Purpose**: Penalizes tokens based on whether they appear in the text so far
**Data Range**: -2.0 to 2.0 (float)
**Default**: 0.0
**Examples & Effects**:
- -2.0: Strong repetition encouragement
  - Result: More likely to repeat words and phrases
  - Use case: Poetry, rhythmic writing
- -1.0: Mild repetition encouragement
  - Result: Slightly more repetitive
  - Use case: Technical documentation with consistent terminology
- 0.0: No penalty (default)
  - Result: Neutral behavior
  - Use case: General purposes
- 1.0: Mild repetition avoidance
  - Result: Tries to avoid repeating words
  - Use case: Creative writing, avoiding redundancy
- 2.0: Strong repetition avoidance
  - Result: Actively avoids any repetition
  - Use case: When variety is critical

#### frequency_penalty
**Purpose**: Penalizes tokens based on their frequency in the text so far
**Data Range**: -2.0 to 2.0 (float)
**Default**: 0.0
**Examples & Effects**:
- -2.0: Strong frequency encouragement
  - Result: Common words become even more common
  - Use case: Simplifying language for beginners
- -1.0: Mild frequency encouragement
  - Result: Slightly favors common words
  - Use case: Clear, simple explanations
- 0.0: No penalty (default)
  - Result: Natural word frequency
  - Use case: General conversation
- 1.0: Mild frequency avoidance
  - Result: Tries to use less common words
  - Use case: Sophisticated writing, academic papers
- 2.0: Strong frequency avoidance
  - Result: Actively avoids common words
  - Use case: Poetic or highly stylized writing

### 6.3 Command Execution Parameters

#### command_start
**Purpose**: Marker that indicates AI wants to execute a command
**Data Range**: Any string (recommend avoiding common words)
**Default**: `"YLDEXECUTE:"`
**Examples & Effects**:
- `"YLDEXECUTE:"`
  - Result: AI outputs "YLDEXECUTE:tool_name￥|param1￥|param2"
  - Advantage: Unique, unlikely to appear in normal text
- `"EXEC:"`
  - Result: AI outputs "EXEC:tool_name|param1|param2"
  - Advantage: Shorter, more readable
- `"RUN:"`
  - Result: AI outputs "RUN:tool_name|param1|param2"
  - Advantage: Intuitive, easy to understand
- `"CMD:"`
  - Result: AI outputs "CMD:tool_name|param1|param2"
  - Advantage: Clear meaning
- Problematic: `"Please:"`
  - Result: False positives when AI says "Please: explain this"
  - Disadvantage: Too common in normal conversation

#### command_separator
**Purpose**: Separates command name from parameters and between parameters
**Data Range**: Any string (recommend non-ASCII or unique characters)
**Default**: `"￥|"` (Japanese yen symbol + pipe)
**Examples & Effects**:
- `"￥|"` (default)
  - Result: `YLDEXECUTE:tool_name￥|param1￥|param2`
  - Advantage: Unique combination, unlikely in normal text
- `"|"`
  - Result: `EXEC:tool_name|param1|param2`
  - Advantage: Standard pipe separator, clean looking
- `"::"`
  - Result: `EXEC:tool_name::param1::param2`
  - Advantage: Double colon, visually distinct
- `"||"`
  - Result: `EXEC:tool_name||param1||param2`
  - Advantage: Double pipe, very distinct
- Problematic: `","`
  - Result: Issues with parameters containing commas
  - Disadvantage: Common in data, causes parsing errors

#### max_iterations
**Purpose**: Maximum number of command execution loops before stopping
**Data Range**: 1 to 100 (integer)
**Default**: 15
**Examples & Effects**:
- 5: Very short execution chain
  - Result: Stops after 5 command executions
  - Use case: Simple, quick tasks
- 15: Standard (default)
  - Result: Allows moderate multi-step tasks
  - Use case: Most common use cases
- 30: Extended execution
  - Result: Allows complex multi-step workflows
  - Use case: Complex automation, research tasks
- 50: Maximum practical
  - Result: Very long execution chains possible
  - Use case: Complex analysis with many steps
- 100: Extreme
  - Result: May get stuck in loops
  - Warning: Use with caution, monitor execution

### 6.4 Tool Configuration Parameters

#### mcp_paths
**Purpose**: List of paths to MCP tool files (.py, .json, .yaml)
**Data Range**: Array of file path strings
**Default**: `[]` (empty list)
**Examples & Effects**:
- Empty: `[]`
  - Result: No tools available, AI can only converse
  - Use case: Pure chat mode
- Python tools: `["./tools/calculator.py", "./tools/file_ops.py"]`
  - Result: Functions from these files become available as tools
  - Use case: Custom Python functions as tools
- JSON configs: `["./tools/mcp_config.json"]`
  - Result: MCP servers and tools defined in JSON become available
  - Use case: External MCP server connections
- Mixed: `["./tools/local.py", "./tools/external.json"]`
  - Result: Both local Python functions and external MCP tools
  - Use case: Comprehensive toolset
- Invalid paths: `["./nonexistent.py"]`
  - Result: Warning message, tool not loaded
  - Solution: Check file existence and permissions

#### system_prompt
**Purpose**: Instructions that define AI's behavior and capabilities
**Data Range**: String (typically 100-10,000 characters)
**Default**: Generated automatically based on configuration
**Examples & Effects**:
**Minimal Prompt** (100 chars):
```text
You are a helpful assistant. Answer questions clearly and concisely.
```
Result: Basic helpful behavior, no special capabilities

**Standard Coding Assistant** (500 chars):
```text
You are an expert Python programmer. Help users write clean, efficient code.
Explain concepts clearly. When asked to write code, provide complete,
working examples with comments. Focus on best practices and PEP 8 guidelines.
```
Result: AI specializes in Python, gives detailed code examples

**Creative Writer** (800 chars):
```text
You are a creative writing assistant specializing in fiction and poetry.
Help users develop characters, plots, and settings. Provide vivid
descriptions and imaginative ideas. Use rich vocabulary and varied
sentence structures. Encourage creativity while maintaining coherence.
```
Result: AI focuses on creative writing, uses expressive language

**Strict Command Executor** (1200 chars):
```text
You are Lynexus AI. You can execute commands using this format:
YLDEXECUTE:tool_name￥|param1￥|param2

RULES:
1. Only output YLDEXECUTE: commands when user explicitly requests an action
2. For questions, answer directly without commands
3. Never explain your actions before or after commands
4. Use only available tools: file_read, file_write, web_search

Example:
User: "Read the config file"
You: "YLDEXECUTE:file_read￥|config.txt"
```
Result: AI strictly follows command protocol, no extraneous text

**Complex Multi-role** (2000+ chars):
```text
You are Lynexus AI with multiple capabilities. Your behavior depends on context:

1. When user asks technical questions: Act as expert with deep knowledge
2. When user requests file operations: Use appropriate tools efficiently
3. When user needs creative help: Be imaginative and supportive
4. When user gives vague requests: Ask clarifying questions

Available tools: [list of tools with descriptions]

Command format: [detailed command syntax]

Error handling: [specific error response guidelines]
```
Result: Context-aware behavior, handles diverse requests appropriately

### 6.5 Advanced Parameters

#### stream
**Purpose**: Whether to stream responses token by token
**Data Range**: Boolean (True/False)
**Default**: False
**Examples & Effects**:
- False: Complete response at once
  - Result: Waits for full response, then displays it
  - Advantage: Clean, complete responses
  - Use case: Most situations, better for command parsing
- True: Stream tokens as they arrive
  - Result: Shows response building character by character
  - Advantage: Feels more responsive
  - Use case: Long responses where waiting is noticeable

#### stop
**Purpose**: Sequences where the AI should stop generating
**Data Range**: Array of strings or None
**Default**: None
**Examples & Effects**:
- None: No special stop sequences
  - Result: AI generates until max_tokens or natural stop
- `["\n\n", "###", "END"]`: Multiple stop sequences
  - Result: Stops at double newline, "###", or "END"
  - Use case: Structured output, sections
- `["User:", "Assistant:"]`: Conversation markers
  - Result: Stops before starting a new turn
  - Use case: Multi-turn simulation
- `["</response>"]`: XML/HTML tags
  - Result: Stops at closing tag
  - Use case: Structured data generation

### 6.6 Parameter Combinations Examples

#### Example 1: Precise Technical Assistant
```python
AI(
    temperature=0.3,
    max_tokens=1024,
    top_p=0.9,
    presence_penalty=0.5,
    frequency_penalty=0.3,
    system_prompt="You are a precise technical assistant..."
)
```
**Result**: Concise, focused, avoids repetition, good for documentation

#### Example 2: Creative Brainstorming Partner
```python
AI(
    temperature=1.2,
    max_tokens=4096,
    top_p=0.95,
    presence_penalty=-0.5,
    frequency_penalty=-0.3,
    system_prompt="You are a creative brainstorming partner..."
)
```
**Result**: Expansive, imaginative, embraces repetition for emphasis

#### Example 3: Strict Command Executor
```python
AI(
    temperature=0.1,
    max_tokens=512,
    command_start="CMD:",
    command_separator="||",
    max_iterations=10,
    system_prompt="Output only CMD: commands when actions needed..."
)
```
**Result**: Highly predictable, minimal output, perfect for automation

#### Example 4: Balanced General Assistant
```python
AI(
    temperature=0.7,
    max_tokens=2048,
    top_p=1.0,
    presence_penalty=0.0,
    frequency_penalty=0.0,
    system_prompt="You are a helpful, balanced assistant..."
)
```
**Result**: Natural, versatile, good for everyday tasks

### 6.7 Parameter Adjustment Guidelines

**When responses are too repetitive**:
- Increase `presence_penalty` (0.5 to 1.5)
- Increase `frequency_penalty` (0.5 to 1.5)
- Lower `temperature` slightly

**When responses are too random**:
- Lower `temperature` (0.3 to 0.7)
- Lower `top_p` (0.7 to 0.9)
- Increase `presence_penalty` slightly

**When responses are too short**:
- Increase `max_tokens` (2048 to 4096)
- Check if `stop` sequences are triggering early

**When command execution fails**:
- Verify `command_start` and `command_separator` match system prompt
- Ensure tools are properly loaded in `mcp_paths`
- Check AI isn't being cut off by `max_tokens`

**When AI ignores system prompt**:
- Make prompt more explicit and detailed
- Include clear examples of desired behavior
- Consider lowering `temperature` for more adherence

### 6.8 Parameter Optimization Workflow

1. **Start with defaults**: Use all default parameters first
2. **Identify issues**: Note what's wrong with responses
3. **Adjust one parameter**: Change only one parameter at a time
4. **Test systematically**: Use the same test prompts each time
5. **Document changes**: Keep notes on what each change does
6. **Iterate**: Repeat until desired behavior is achieved
7. **Save preset**: Export your optimized configuration

**Example optimization process**:
```
Initial: temperature=1.0 → Responses too random
Test 1: temperature=0.7 → Better but still somewhat random
Test 2: temperature=0.5 → Good balance, retains creativity
Test 3: Add top_p=0.9 → Further focuses responses
Test 4: Add presence_penalty=0.3 → Reduces repetition
Final: temperature=0.5, top_p=0.9, presence_penalty=0.3
```

This comprehensive parameter reference should help you understand and optimize every aspect of your Lynexus AI assistant. Remember that optimal settings depend on your specific use case, so experiment and find what works best for your needs.