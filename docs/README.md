# Lynexus AI Assistant - Complete User Guide

[简体中文](./zh-cn/README.md)

Welcome to Lynexus! This guide is organized into two tracks to help you get started quickly, whether you're a beginner or an advanced user.

---

## 📚 Choose Your Track

- **🌱 Beginner Track** - Perfect if you're new to AI assistants or just want to use Lynexus without technical details
- **⚡ Advanced Track** - For developers and users who want customization, programming, and integration

---

# 🌱 BEGINNER TRACK

## Quick Start Guide

### What is Lynexus?

Lynexus is an AI assistant that can:
- 💬 Chat with you naturally
- 🛠️ Execute commands on your computer (when you allow it)
- 📁 Manage files and folders
- 🔍 Search the web
- 🤖 Use various tools to help you work faster

Think of it as ChatGPT, but with the ability to actually **do things** on your computer!

---

## Getting Started

### Step 1: Download and Install

**Option A: Download the ready-to-use version (Recommended)**
1. Go to [GitHub Releases](https://github.com/SolynAcVersion/LyNexus/releases)
2. Download the latest `.zip` file
3. Extract it to any folder
4. Double-click `Lynexus.exe` to start

**Option B: Install from source**
1. Make sure you have Python 3.10+ installed
2. Download and unzip the source code
3. Install dependencies (follow the instructions in README.md)
4. Run `python main.py`

---

### Step 2: First-Time Setup

When you first open Lynexus, you'll see a setup window. Don't worry - it's simple!

**1. Get an API Key**
   - You need an API key to use AI
   - Popular options:
     - **DeepSeek**: Affordable and powerful ([Get key here](https://platform.deepseek.com))
     - **OpenAI**: The original ChatGPT ([Get key here](https://platform.openai.com))
   - Copy your API key (it looks like: `sk-xxxxxxxxxxxxxx`)

**2. Fill in the Setup Form**
   - **API Provider**: Choose your provider (e.g., DeepSeek, OpenAI)
   - **API Key**: Paste your key
   - **Model**: Use the default suggested model
   - **MCP Tools**: Leave empty for now (we'll explain later)

**3. Click "Start Lynexus"**

That's it! You're ready to chat!

---

### Step 3: Basic Chatting

**The Interface**
- **Left sidebar**: Your chat conversations
- **Center**: Chat area where you see messages
- **Bottom**: Input box to type your message

**How to Chat**
1. Click in the input box at the bottom
2. Type your message
3. Press Ctrl+Enter or click the send button
4. The AI will respond!

**Example conversations:**
- "Help me write an email to my boss"
- "Explain quantum physics like I'm 5 years old"
- "What's the difference between Python and JavaScript?"

---

### Step 4: Managing Conversations

**Create a New Chat**
- Click "New Chat" in the left sidebar
- Give it a name like "Work" or "Learning Python"

**Switch Between Chats**
- Click on any conversation in the left sidebar
- Each chat remembers its own history

**Save Your Chat**
- Click "Export Chat" in the sidebar
- Choose where to save it (Desktop is recommended)
- Select format:
  - **TXT**: Simple text file
  - **JSON**: For developers
  - **Markdown**: Nice formatting for documents

---

### Step 5: AI Commands (The Magic Part!)

Lynexus can execute commands on your computer! Here's how:

**⚠️ Important**: By default, the AI can only chat. To enable file operations, web search, and other advanced features, you need to use the **Beginner Tools Package**.

---

### 🎁 Quick Start with File Operations (Recommended)

We've prepared a special package for beginners that includes ready-to-use tools!

**What's in the package:**
- 📁 **File Operations**: Read, write, copy, move, delete files
- 🔍 **Web Search**: Search Baidu and read web pages
- 👁️ **OCR**: Extract text from images and PDFs
- 🌐 **Network Tools**: Download documents, test connections

**How to use it (Super Easy!):**

1. **Download the tools package** from [GitHub Releases](https://github.com/SolynAcVersion/LyNexus/releases)
   - Look for `lynexus_tools.zip`

2. **Extract the package** - You'll see:
   - A `tools/` folder
   - A `prefab_file_operator.json` configuration file

3. **Place the `tools/` folder** in your Lynexus directory:
   - **If using `.exe`**: Put it in the same folder as `Lynexus.exe`
   - **If using source code**: Put it in the project root directory

4. **Load the configuration**:
   - Method 1: When starting Lynexus, click "Load Config File" and select `prefab_file_operator.json`
   - Method 2: In the main window, click "Import Config" and select `prefab_file_operator.json`

5. **That's it!** Now you can:
   - Read files: "Read config.txt"
   - Create files: "Create a notes.txt file with my meeting notes"
   - Search the web: "Search for Python tutorials"
   - Extract text from images: "Extract text from screenshot.png"

**Example conversations after setup:**
```
You: "Create a file called hello.txt with the text 'Hello World'"
AI: YLDEXECUTE:write_to_file￥|Hello World￥|hello.txt

You: "What files are in the current directory?"
AI: YLDEXECUTE:ls￥|.

You: "Read the hello.txt file"
AI: YLDEXECUTE:cat￥|hello.txt
```

---

**Without the tools package:**
The AI will only be able to chat with you. It won't be able to execute commands until you set up the tools or create your own (see Advanced Track for details).

**⚠️ Safety First:**
- The AI will only execute commands you request
- You can always stop it by clicking the "Stop" button
- Be careful with delete commands - they can't be undone!
- The `rm` tool deletes files permanently

---

## Common Tasks

### Task 1: Get Help with Coding

**Prompt:**
```
I'm learning Python. Can you write a simple function that adds two numbers?
```

The AI will explain the code and provide examples!

### Task 2: File Management (Requires Tools Package)

**Prompt:**
```
Create a text file called notes.txt with my meeting notes from today
```

The AI will:
1. Create the file using the `write_to_file` tool
2. Add your content
3. Confirm when it's done

**Note**: This requires the [Beginner Tools Package](#step-5-ai-commands-the-magic-part) to be installed.

### Task 3: Research and Summarize (Requires Tools Package)

**Prompt:**
```
Search for information about climate change and summarize the key points
```

The AI will:
1. Use the `search_baidu` tool
2. Read the results
3. Give you a clear summary

**Note**: This requires the [Beginner Tools Package](#step-5-ai-commands-the-magic-part) to be installed.

### Task 4: Extract Text from Images (Requires Tools Package)

**Prompt:**
```
Extract text from the screenshot.png file on my desktop
```

The AI will:
1. Use the `ocr_process_pictures` tool
2. Extract all text from the image
3. Display the results

**Note**: This requires the [Beginner Tools Package](#step-5-ai-commands-the-magic-part) to be installed.

---

## Troubleshooting (Beginner FAQ)

### Problem: "API Key Error"
**Solution:**
- Check that you copied the entire API key
- Make sure there are no extra spaces
- Verify your key hasn't expired

### Problem: "AI Won't Respond"
**Solution:**
- Check your internet connection
- Make sure you have API credits left
- Try clicking "Clear Chat" and start fresh

### Problem: "Commands Don't Work"
**Solution:**
- Go to Settings
- Check if MCP tools are configured
- Some features require additional setup (see Advanced Track)

### Problem: "Where Did My Chat Go?"
**Solution:**
- Chats are saved automatically
- Look in the left sidebar
- Click "Export Chat" to save a copy

---

## Tips for Beginners

✅ **Start Simple**: Just chat normally at first
✅ **Be Specific**: The more details you give, the better the response
✅ **Experiment**: Try different types of requests
✅ **Save Good Conversations**: Export chats you want to keep
✅ **Use Multiple Chats**: Create separate chats for different topics

❌ **Don't Worry About**: Technical settings for now (explore later in Advanced Track)
❌ **Don't Share**: Never share your API key with others
❌ **Don't Delete**: Be careful with file delete commands

---

## Next Steps

Once you're comfortable with basic chatting:

1. **🎁 Download the Tools Package** - Give your AI superpowers!
   - Get it from [GitHub Releases](https://github.com/SolynAcVersion/LyNexus/releases)
   - Look for `lynexus_tools.zip`
   - Follow the installation guide in [Step 5](#step-5-ai-commands-the-magic-part)

2. **📦 Explore Presets** - Try different AI personalities
   - Import the `prefab_file_operator.json` for file operations
   - Look for community presets on the forum

3. **🔧 Customize Your Experience** - Fine-tune the AI
   - Adjust settings in the Settings menu
   - Create your own presets
   - Share your favorites with friends

4. **📚 Learn Advanced Features** - Unlock full potential
   - Read the [Advanced Track](#-advanced-track) below
   - Learn to create your own tools
   - Integrate with your workflow

---

# ⚡ ADVANCED TRACK

## Advanced Configuration & Customization

### Understanding Presets

**What is a Preset?**
A preset is a complete configuration package that includes:
- API settings (which AI model to use)
- Behavior parameters (how creative or precise the AI should be)
- Custom instructions (system prompts)
- Tool configurations (what the AI can do)
- Command settings (how the AI executes commands)

**Why Use Presets?**
- 🎯 Quickly switch between different AI personalities
- 📦 Share your perfect setup with others
- 🔥 Use community-tested configurations
- ⚡ Skip repetitive setup

---

### Creating Your First Preset

#### Method 1: Visual Configuration (Recommended)

1. Click **Settings** in the sidebar
2. Configure each section:

**API Configuration**
```
Provider: DeepSeek / OpenAI / Anthropic / Local / Custom
API Key: Your secret key
Base URL: Auto-filled based on provider
Model: Select from available models
```

**Model Parameters** (What do these mean?)

**Temperature** (0.0 - 2.0)
- `0.0 - 0.3`: Precise, factual, consistent (good for coding)
- `0.4 - 0.7`: Balanced, natural (good for general use)
- `0.8 - 1.2`: Creative, varied (good for brainstorming)
- `1.3 - 2.0`: Very random, experimental

**Max Tokens** (Response length)
- `512 - 1024`: Short, concise answers
- `2048`: Standard length (default)
- `4096+`: Long, detailed explanations

**Top P** (0.0 - 1.0)
- Controls diversity via probability
- Lower = more focused, Higher = more diverse

**Presence & Frequency Penalty** (-2.0 to 2.0)
- Controls repetition in responses
- Positive values: Avoid repetition
- Negative values: Encourage repetition
- `0.0`: Neutral (default)

**Command Configuration**
```
Command Start: YLDEXECUTE: (default)
Command Separator: ￥| (default)
Max Iterations: 15 (how many commands AI can execute in a row)
```

**System Prompt** (Custom Instructions)
This is where you define the AI's personality and behavior. Examples:

**Simple Assistant:**
```
You are a helpful assistant. Answer clearly and concisely.
```

**Expert Python Developer:**
```
You are an expert Python developer with 10 years of experience.
Follow PEP 8 guidelines. Write clean, documented code.
Explain complex concepts with examples.
Focus on best practices and performance optimization.
```

**Creative Writing Coach:**
```
You are a creative writing coach specializing in fiction.
Help users develop compelling characters and plots.
Use vivid descriptions and imaginative ideas.
Encourage experimentation while maintaining narrative coherence.
```

**MCP Tools** (Add Superpowers)
- Click "Select MCP Files"
- Choose `.py` or `.json` tool files
- Tools extend what the AI can do

3. Click **Save Settings** to apply to current chat
4. Click **Save As Config** to export as a preset file

---

#### Method 2: Programmatic Configuration

For developers who want full control:

```python
from aiclass import AI

# Create AI instance with custom configuration
my_preset = AI(
    # API Configuration
    api_key="your_api_key_here",
    api_base="https://api.deepseek.com",
    model="deepseek-chat",

    # Model Parameters
    temperature=0.7,
    max_tokens=4096,
    top_p=1.0,
    presence_penalty=0.0,
    frequency_penalty=0.0,

    # Command Configuration
    command_start="EXECUTE:",
    command_separator="|",
    max_iterations=15,

    # Behavior
    system_prompt="You are an expert Python programmer...",

    # Tools
    mcp_paths=["./tools/my_tool.py", "./tools/mcp_config.json"]
)
```

**Preset JSON Structure:**
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

---

### Preset Best Practices

#### For Coding Assistants
```python
AI(
    temperature=0.3,  # Low for consistent code
    max_tokens=2048,
    system_prompt="Expert Python programmer. Follow PEP 8. Write clean, documented code.",
    mcp_paths=["./tools/file_ops.py", "./tools/code_runner.py"]
)
```

#### For Creative Writing
```python
AI(
    temperature=1.1,  # High for creativity
    max_tokens=4096,
    presence_penalty=-0.5,  # Encourage thematic repetition
    system_prompt="Creative writing coach. Vivid descriptions, imaginative ideas.",
    mcp_paths=["./tools/research.py", "./tools/thesaurus.py"]
)
```

#### For Research & Analysis
```python
AI(
    temperature=0.5,  # Balanced
    max_tokens=4096,
    system_prompt="Research assistant. Accurate, thorough, with citations.",
    mcp_paths=["./tools/web_search.py", "./tools/data_analyzer.py"]
)
```

#### For Automation/Scripting
```python
AI(
    temperature=0.1,  # Very low for predictability
    max_tokens=512,
    command_start="CMD:",
    command_separator="||",
    max_iterations=10,
    system_prompt="Execute commands precisely. Output ONLY command syntax when action needed.",
)
```

---

### Importing & Exporting Presets

**Export Your Configuration:**
1. Settings → Save As Config
2. Choose location (Desktop recommended)
3. Save as `.json` file
4. **⚠️ Important**: Never share your `.confignore` file (contains API keys!)

**Import a Configuration:**
1. Click "Import Config" in sidebar
2. Select `.json` preset file
3. Settings are applied automatically
4. Add your own API key in Settings

**Import During Setup:**
1. In initialization dialog, click "Load Config File"
2. Select your preset
3. All settings auto-populate
4. Add API key
5. Click "Start Lynexus"

---

### Community Preset Ecosystem

**Find Presets:**
- Browse the [community forum](https://forum.lynexus.ai)
- Filter by category (coding, writing, research, etc.)
- Read reviews and ratings
- Download configurations that match your needs

**Share Presets:**
1. Create and test your configuration
2. Export as JSON (Settings → Save As Config)
3. Write a description:
   - What it's optimized for
   - Key features
   - How to use it
   - Example prompts
4. Upload to community forum
5. **⚠️ REMEMBER**: Remove your API key before sharing!

**Rate & Review:**
- Help others by rating presets you use
- Leave constructive feedback
- Share your success stories

---

## MCP Tools Development

### What Are MCP Tools?

MCP (Model Context Protocol) tools extend what the AI can do. Think of them as plugins or extensions.

**Examples:**
- 📁 File operations (read, write, list)
- 🔍 Web search
- 🧮 Calculator
- 📊 Data analysis
- 🗄️ Database queries
- 🌐 API integrations

---

### Creating Python MCP Tools

**Simple Tool:**

```python
# ./tools/calculator.py

def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers together.

    Parameters:
    a: First number
    b: Second number

    Returns:
    Sum of a and b
    """
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Parameters:
    a: First number
    b: Second number

    Returns:
    Product of a and b
    """
    return a * b
```

**Advanced Tool with Error Handling:**

```python
# ./tools/file_manager.py

import os
import json

def read_file(filepath: str) -> str:
    """
    Read the contents of a file.

    Parameters:
    filepath: Path to the file to read

    Returns:
    File contents as string
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """
    Write content to a file.

    Parameters:
    filepath: Path to the file
    content: Content to write

    Returns:
    Success message
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to '{filepath}'"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_files(directory: str = ".") -> str:
    """
    List files in a directory.

    Parameters:
    directory: Directory path (default: current directory)

    Returns:
    JSON list of files and directories
    """
    try:
        items = os.listdir(directory)
        return json.dumps(items, indent=2)
    except Exception as e:
        return f"Error listing directory: {str(e)}"
```

**Tool Discovery:**
- Place `.py` files in your tools directory
- Functions with docstrings are automatically discovered
- The AI can see function names, parameters, and descriptions

---

### Creating JSON MCP Configurations

For external MCP servers or complex tools:

```json
{
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
        },
        "web-search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-web-search"]
        }
    }
}
```

**Configure in Lynexus:**
1. Create the JSON file
2. Settings → MCP Tools → Add JSON path
3. Tools are loaded automatically

---

## Advanced System Prompts

### Prompt Engineering Best Practices

**1. Be Explicit and Clear**
```text
GOOD:
You are a Python coding assistant. When writing code:
- Always include docstrings
- Follow PEP 8 guidelines
- Add type hints
- Provide usage examples
- Explain complex logic in comments

BAD:
You help with coding.
```

**2. Provide Examples**
```text
You are a command executor. When the user requests an action:

User: "Read config.txt"
You: YLDEXECUTE:file_read￥|config.txt

User: "Create a folder"
You: YLDEXECUTE:mkdir￥|new_folder

Rules:
- Output ONLY the command, no explanations
- Validate parameters before execution
- Ask for clarification if unsure
```

**3. Define Constraints**
```text
You are a precise technical writer. Follow these rules:
- Maximum 3 sentences per paragraph
- Use bullet points for lists
- Avoid jargon unless necessary
- Define technical terms on first use
- Include examples for complex concepts
```

**4. Specify Output Format**
```text
When providing code examples, use this format:

## Language
```python
# Code here
```

**Explanation:** Brief explanation

**Usage:** How to use it

---

## Multi-Conversation Management

### Independent AI Instances

Each conversation maintains its own:
- AI configuration
- Chat history
- Tool access
- Context memory

**Use Cases:**
- **Work Chat**: Coding assistant with file tools
- **Personal Chat**: Creative writing with research tools
- **Learning Chat**: Tutor mode with educational tools

### Sharing Configuration Between Chats

**Method 1: Export/Import**
1. Configure Chat A perfectly
2. Export configuration (Settings → Save As Config)
3. In Chat B, import the config
4. All settings copied!

**Method 2: Preset System**
1. Save common configurations as presets
2. Quick-load into any new chat
3. Build a library of specialized setups

---

## Command Line Interface

### Running from Terminal

**Interactive Console:**
```bash
python aiclass.py
```

**One-Liner Commands:**
```bash
python -c "
from aiclass import create_ai_from_config
ai = create_ai_from_config('config.json')
response = ai.process_user_inp('Explain quantum computing')
print(response)
"
```

**Batch Processing:**
```python
from aiclass import AI

# Initialize AI
ai = AI(
    api_key="your_key",
    model="deepseek-chat",
    temperature=0.7
)

# Process multiple inputs
inputs = [
    "Summarize this article",
    "Extract key points",
    "Generate a conclusion"
]

for i, inp in enumerate(inputs, 1):
    print(f"\n=== Task {i} ===")
    print(f"Input: {inp}\n")

    response, completed = ai.process_user_inp(inp)
    print(response)

    if i < len(inputs):
        ai.reset_conversation()  # Clear for next task
```

---

## Integration & Automation

### Webhook Integration

Create a simple Flask API wrapper:

```python
from flask import Flask, request, jsonify
from aiclass import AI

app = Flask(__name__)
ai = AI(api_key="your_key", model="deepseek-chat")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')

    response, completed = ai.process_user_inp(message)

    return jsonify({
        'response': response,
        'completed': completed
    })

if __name__ == '__main__':
    app.run(port=5000)
```

**Use it:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, Lynexus!"}'
```

### Automation Scripts

**Scheduled Tasks:**
```python
import schedule
import time
from aiclass import AI

def daily_report():
    ai = AI(api_key="your_key", model="deepseek-chat")

    # Generate report
    report, _ = ai.process_user_inp(
        "Analyze today's logs and summarize issues"
    )

    # Save to file
    with open('daily_report.txt', 'w') as f:
        f.write(report)

    print("Daily report generated!")

# Run every day at 9 AM
schedule.every().day.at("09:00").do(daily_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Development Workflow Integration

**Pre-commit Hook for Code Review:**
```python
#!/usr/bin/env python3
# .git/hooks/pre-commit

import sys
from aiclass import AI

def review_staged_files():
    ai = AI(
        api_key="your_key",
        model="deepseek-chat",
        system_prompt="You are a code reviewer. Check for bugs, style issues, and improvements."
    )

    # Get staged files (simplified)
    files = ["main.py", "aiclass.py"]

    for file in files:
        with open(file, 'r') as f:
            code = f.read()

        review, _ = ai.process_user_inp(
            f"Review this code:\n\n{code}\n\nProvide brief feedback."
        )

        print(f"\n=== Review for {file} ===")
        print(review)

if __name__ == "__main__":
    review_staged_files()
    sys.exit(0)
```

---

## Troubleshooting (Advanced)

### API Connection Issues

**Debug Mode:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from aiclass import AI
ai = AI(api_key="your_key", model="deepseek-chat")
```

**Common Problems:**

1. **Timeout Errors**
   - Increase `timeout` parameter
   - Check network connectivity
   - Verify API status

2. **Rate Limiting**
   - Implement exponential backoff
   - Use multiple API keys in rotation
   - Reduce request frequency

3. **Invalid Responses**
   - Check `max_tokens` isn't truncating
   - Verify `temperature` settings
   - Review system prompt clarity

### MCP Tool Errors

**Debug Tool Loading:**
```python
from aiclass import AI

ai = AI(mcp_paths=["./tools/my_tool.py"])

# Check loaded tools
print("Available tools:", ai.tools)
```

**Common Tool Issues:**

1. **Import Errors**
   - Ensure all dependencies installed
   - Use absolute imports
   - Check Python path

2. **Function Signature Mismatch**
   - Verify parameter types match docstring
   - Check for required vs optional parameters
   - Test functions independently

3. **Execution Failures**
   - Add try-except blocks in tools
   - Validate inputs before processing
   - Return informative error messages

### Performance Optimization

**Reduce Latency:**
```python
ai = AI(
    api_base="https://api.deepseek.com",  # Use nearest server
    max_tokens=1024,  # Reduce response size
    stream=False  # Disable streaming for faster complete response
)
```

**Memory Management:**
```python
# For long conversations
ai.reset_conversation()  # Clear history periodically

# For batch processing
for task in tasks:
    response = ai.process_user_inp(task)
    ai.reset_conversation()  # Fresh context for each task
```

---

## Complete Parameter Reference

<details>
<summary><strong>📖 Click to expand full parameter reference</strong></summary>

### API Configuration

#### `api_key`
- **Type**: String
- **Default**: None
- **Example**: `"sk-1234567890abcdef..."`
- **Note**: Can also use environment variable `DEEPSEEK_API_KEY` or `OPENAI_API_KEY`

#### `api_base`
- **Type**: String (URL)
- **Default**: `"https://api.deepseek.com"`
- **Examples**:
  - DeepSeek: `"https://api.deepseek.com"`
  - OpenAI: `"https://api.openai.com/v1"`
  - Local Ollama: `"http://localhost:11434"`

#### `model`
- **Type**: String
- **Default**: `"deepseek-chat"`
- **Examples**:
  - `"deepseek-chat"` (DeepSeek V3)
  - `"gpt-4-turbo"` (OpenAI)
  - `"claude-3-opus-20240229"` (Anthropic)

### Model Behavior

#### `temperature`
- **Range**: 0.0 - 2.0
- **Default**: 1.0
- **Effects**:
  - 0.0: Deterministic, same output for same input
  - 0.5: Consistent with slight variation
  - 1.0: Natural, varied responses
  - 1.5+: Creative, unpredictable
- **Use Cases**:
  - Low (0.0-0.3): Coding, factual answers
  - Medium (0.4-0.7): General conversation
  - High (0.8-1.2): Brainstorming, creative writing

#### `max_tokens`
- **Range**: 1 - 8192+ (depends on API)
- **Default**: 2048
- **Effects**:
  - 512: Short responses
  - 2048: Standard length
  - 4096+: Long, detailed content
  - 0/None: No limit (uses API max)

#### `top_p`
- **Range**: 0.0 - 1.0
- **Default**: 1.0
- **Effects**: Controls diversity via nucleus sampling
  - 0.1: Very focused, only probable tokens
  - 0.5: Balanced sampling
  - 0.9: Diverse choices
  - 1.0: No filtering

#### `presence_penalty`
- **Range**: -2.0 - 2.0
- **Default**: 0.0
- **Effects**:
  - Negative: Encourages repetition
  - 0.0: Neutral
  - Positive: Avoids repetition

#### `frequency_penalty`
- **Range**: -2.0 - 2.0
- **Default**: 0.0
- **Effects**:
  - Negative: Favors common words
  - 0.0: Natural frequency
  - Positive: Favors rare words

### Command Execution

#### `command_start`
- **Type**: String
- **Default**: `"YLDEXECUTE:"`
- **Purpose**: Marker that indicates AI wants to execute a command
- **Recommendation**: Use unique strings unlikely in normal text

#### `command_separator`
- **Type**: String
- **Default**: `"￥|"`
- **Purpose**: Separates command parts
- **Examples**: `"|"`, `"::"`, `"||"`

#### `max_iterations`
- **Range**: 1 - 100
- **Default**: 15
- **Purpose**: Maximum command execution loops before stopping
- **Use Cases**:
  - 5-10: Simple tasks
  - 15-20: Standard usage
  - 30+: Complex automation

### Tool Configuration

#### `mcp_paths`
- **Type**: List of strings
- **Default**: []
- **Purpose**: Paths to MCP tool files (.py, .json, .yaml)
- **Examples**:
  - `[]`: No tools
  - `["./tools/file_ops.py"]`: Single tool
  - `["./tools/tool1.py", "./tools/tool2.json"]`: Multiple tools

#### `system_prompt`
- **Type**: String
- **Default**: Auto-generated
- **Length**: 100 - 10,000+ characters
- **Purpose**: Defines AI behavior, personality, and capabilities

### Advanced

#### `stream`
- **Type**: Boolean
- **Default**: False
- **Purpose**: Stream responses token-by-token
- **Use**: Faster perceived response time for long outputs

#### `stop`
- **Type**: List of strings or None
- **Default**: None
- **Purpose**: Sequences where AI stops generating
- **Examples**:
  - `["\n\n", "###"]`: Stop at double newline or marker
  - `["User:", "Assistant:"]`: Stop before new turn

</details>

---

## Parameter Optimization Guide

### Systematic Tuning Process

1. **Start with defaults** - Establish baseline behavior
2. **Identify issues** - Note what needs improvement
3. **Adjust ONE parameter** - Change only one at a time
4. **Test consistently** - Use same test prompts
5. **Document changes** - Keep a tuning log
6. **Iterate** - Repeat until satisfied
7. **Save preset** - Export final configuration

### Quick Reference Table

| Symptom | Solution |
|---------|----------|
| Too repetitive | Increase `presence_penalty` (0.5-1.5) |
| Too random | Lower `temperature` (0.3-0.7) |
| Too short | Increase `max_tokens` (2048-4096) |
| Commands failing | Check `command_start`/`command_separator` |
| Ignores instructions | Make system prompt more explicit |
| Too wordy | Lower `max_tokens`, add "be concise" to prompt |
| Too creative | Lower `temperature`, increase `top_p` |
| Too boring | Raise `temperature`, lower `presence_penalty` |

### Example Optimization Process

```
Initial Setup:
temperature=1.0 → Responses too random

Test 1: temperature=0.7
Result: Better but still some randomness

Test 2: temperature=0.5
Result: Good balance, retains creativity

Test 3: Add top_p=0.9
Result: Further focuses responses

Test 4: Add presence_penalty=0.3
Result: Reduces repetitive phrases

Final Configuration:
temperature=0.5, top_p=0.9, presence_penalty=0.3
```

---

## Community & Resources

**Get Help:**
- [Documentation](https://solynacversion.github.io/LyNexus)
- [Community Forum](https://forum.lynexus.ai)
- [GitHub Issues](https://github.com/SolynAcVersion/LyNexus/issues)
- [Discord Server](https://discord.gg/lynexus)

**Contribute:**
- Share your presets
- Report bugs
- Suggest features
- Improve documentation
- Submit pull requests

**Learn More:**
- [Contributing Guidelines](https://github.com/SolynAcVersion/LyNexus/blob/main/CONTRIBUTING.md)
- [Code of Conduct](https://github.com/SolynAcVersion/LyNexus/blob/main/CODE_OF_CONDUCT.md)
- [Project Roadmap](https://github.com/SolynAcVersion/LyNexus/blob/main/ROADMAP.md)

---

## License

This project is licensed under the Mozilla Public License 2.0. See [LICENSE](https://github.com/SolynAcVersion/LyNexus/blob/main/LICENSE) for details.

---

**Built with ❤️ by the AI community, for the AI community**
