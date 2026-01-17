# Lynexus AI助手 - 完整用户指南

[English](./../README.md)

欢迎使用 Lynexus！本指南分为两个轨道，帮助您快速上手，无论您是初学者还是高级用户。

---

## 📚 选择您的轨道

- **🌱 初学者轨道** - 适合AI助手新手或只想使用Lynexus而不想了解技术细节的用户
- **⚡ 高级轨道** - 适合开发者以及想要定制、编程和集成的用户

---

# 🌱 初学者轨道

## 快速入门指南

### Lynexus是什么？

Lynexus是一个AI助手，它可以：
- 💬 与您自然聊天
- 🛠️ 在您的计算机上执行命令（经您允许）
- 📁 管理文件和文件夹
- 🔍 搜索网络
- 🤖 使用各种工具帮您更快地工作

把它想象成ChatGPT，但具有实际**在您的计算机上执行操作**的能力！

---

## 入门指南

### 第1步：下载和安装

**选项A：下载即用版本（推荐）**
1. 访问 [GitHub Releases](https://github.com/SolynAcVersion/LyNexus/releases)
2. 下载最新的 `.zip` 文件
3. 解压到任意文件夹
4. 双击 `Lynexus.exe` 启动

**选项B：从源代码安装**
1. 确保已安装 Python 3.10+
2. 下载并解压源代码
3. 安装依赖（按照 README.md 中的说明）
4. 运行 `python main.py`

---

### 第2步：首次设置

首次打开Lynexus时，您会看到设置窗口。别担心 - 很简单！

**1. 获取API密钥**
   - 您需要API密钥才能使用AI
   - 热门选择：
     - **DeepSeek**: 价格实惠且功能强大 ([在此获取密钥](https://platform.deepseek.com))
     - **OpenAI**: 原创ChatGPT ([在此获取密钥](https://platform.openai.com))
   - 复制您的API密钥（看起来像：`sk-xxxxxxxxxxxxxx`）

**2. 填写设置表单**
   - **API提供商**：选择您的提供商（如DeepSeek、OpenAI）
   - **API密钥**：粘贴您的密钥
   - **模型**：使用默认建议的模型
   - **MCP工具**：暂时留空（我们稍后会解释）

**3. 点击"开始使用Lynexus"**

就这样！您可以开始聊天了！

---

### 第3步：基本聊天

**界面介绍**
- **左侧边栏**：您的聊天对话
- **中央区域**：显示消息的聊天区域
- **底部**：输入消息的输入框

**如何聊天**
1. 点击底部的输入框
2. 输入您的消息
3. 按Ctrl+Enter键或点击发送按钮
4. AI将回复您！

**对话示例：**
- "帮我写一封给老板的邮件"
- "像对5岁孩子一样解释量子物理"
- "Python和JavaScript有什么区别？"

---

### 第4步：管理对话

**创建新对话**
- 点击左侧边栏中的"新建聊天"
- 给它起个名字，比如"工作"或"学习Python"

**切换对话**
- 点击左侧边栏中的任意对话
- 每个对话都记住自己的历史记录

**保存对话**
- 点击边栏中的"导出聊天"
- 选择保存位置（建议保存到桌面）
- 选择格式：
  - **TXT**：简单文本文件
  - **JSON**：适合开发者
  - **Markdown**：文档格式良好

---

### 第5步：AI命令（神奇的部分！）

Lynexus可以在您的计算机上执行命令！方法如下：

**⚠️ 重要提示**：默认情况下，AI只能聊天。要启用文件操作、网络搜索和其他高级功能，您需要使用**初学者工具包**。

---

### 🎁 快速开始文件操作（推荐）

我们为初学者准备了一个特殊的包，包含现成的工具！

**包里有什么：**
- 📁 **文件操作**：读取、写入、复制、移动、删除文件
- 🔍 **网络搜索**：百度搜索、阅读网页
- 👁️ **OCR功能**：从图片和PDF中提取文本
- 🌐 **网络工具**：下载文档、测试连接

**如何使用（超简单！）：**

1. **下载工具包**，从 [GitHub Releases](https://github.com/SolynAcVersion/LyNexus/releases)
   - 查找 `lynexus_tools.zip`

2. **解压包** - 您会看到：
   - 一个 `tools/` 文件夹
   - 一个 `prefab_file_operator.json` 配置文件

3. **将 `tools/` 文件夹**放在Lynexus目录中：
   - **如果使用 `.exe`**：放在与 `Lynexus.exe` 相同的文件夹中
   - **如果使用源代码**：放在项目根目录中

4. **加载配置**：
   - 方法1：启动Lynexus时，点击"加载配置文件"并选择 `prefab_file_operator.json`
   - 方法2：在主窗口中，点击"导入配置"并选择 `prefab_file_operator.json`

5. **就这样！** 现在您可以：
   - 读取文件："读取 config.txt"
   - 创建文件："创建一个包含我的会议记录的 notes.txt 文件"
   - 搜索网络："搜索Python教程"
   - 从图片提取文本："从 screenshot.png 提取文本"

**设置后的对话示例：**
```
您："创建一个名为 hello.txt 的文件，内容为'Hello World'"
AI：YLDEXECUTE:write_to_file￥|Hello World￥|hello.txt

您："当前目录有什么文件？"
AI：YLDEXECUTE:ls￥|.

您："读取 hello.txt 文件"
AI：YLDEXECUTE:cat￥|hello.txt
```

---

**没有工具包的情况下：**
AI只能与您聊天。在您设置工具或创建自己的工具之前，它将无法执行命令（详情请参见高级轨道）。

**⚠️ 安全第一：**
- AI只执行您请求的命令
- 您可以随时点击"停止"按钮来停止它
- 删除命令要小心 - 它们无法撤销！
- `rm` 工具会永久删除文件

---

## 常见任务

### 任务1：获取编程帮助

**提示：**
```
我正在学习Python。你能编写一个简单的函数来将两个数字相加吗？
```

AI将解释代码并提供示例！

### 任务2：文件管理（需要工具包）

**提示：**
```
创建一个名为notes.txt的文本文件，包含我今天的会议记录
```

AI将：
1. 使用 `write_to_file` 工具创建文件
2. 添加您的内容
3. 完成后确认

**注意**：这需要安装[初学者工具包](#第5步ai命令神奇的部分)

### 任务3：研究和总结（需要工具包）

**提示：**
```
搜索关于气候变化的信息并总结要点
```

AI将：
1. 使用 `search_baidu` 工具
2. 阅读结果
3. 给您清晰的总结

**注意**：这需要安装[初学者工具包](#第5步ai命令神奇的部分)

### 任务4：从图片提取文本（需要工具包）

**提示：**
```
从我桌面上的 screenshot.png 文件中提取文本
```

AI将：
1. 使用 `ocr_process_pictures` 工具
2. 从图片中提取所有文本
3. 显示结果

**注意**：这需要安装[初学者工具包](#第5步ai命令神奇的部分)

---

## 故障排除（初学者常见问题）

### 问题："API密钥错误"
**解决方案：**
- 检查是否复制了完整的API密钥
- 确保没有多余的空格
- 验证您的密钥未过期

### 问题："AI不响应"
**解决方案：**
- 检查您的网络连接
- 确保还有API额度
- 尝试点击"清空聊天"并重新开始

### 问题："命令不起作用"
**解决方案：**
- 进入设置
- 检查是否配置了MCP工具
- 某些功能需要额外设置（参见高级轨道）

### 问题："我的聊天去哪了？"
**解决方案：**
- 聊天会自动保存
- 查看左侧边栏
- 点击"导出聊天"保存副本

---

## 初学者技巧

✅ **从简单开始**：起初只是正常聊天
✅ **具体明确**：您给出的细节越多，响应越好
✅ **实验尝试**：尝试不同类型的请求
✅ **保存好对话**：导出您想保留的聊天
✅ **使用多个对话**：为不同主题创建单独的聊天

❌ **不用担心**：暂时不用担心技术设置（稍后在高级轨道中探索）
❌ **不要分享**：永远不要与他人分享您的API密钥
❌ **不要删除**：对文件删除命令要小心

---

## 下一步

一旦您熟悉了基本聊天：

1. **🎁 下载工具包** - 给您的AI超能力！
   - 从 [GitHub Releases](https://github.com/SolynAcVersion/LyNexus/releases) 获取
   - 查找 `lynexus_tools.zip`
   - 按照[第5步](#第5步ai命令神奇的部分)中的安装指南操作

2. **📦 探索预设** - 尝试不同的AI个性
   - 导入 `prefab_file_operator.json` 进行文件操作
   - 在论坛上查找社区预设

3. **🔧 定制您的体验** - 微调AI
   - 在设置菜单中调整设置
   - 创建您自己的预设
   - 与朋友分享您的最爱

4. **📚 学习高级功能** - 解锁全部潜力
   - 阅读下面的[高级轨道](#-高级轨道)
   - 学习创建自己的工具
   - 集成到您的工作流程中

---

# ⚡ 高级轨道

## 高级配置与定制

### 理解预设

**什么是预设？**
预设是一个完整的配置包，包括：
- API设置（使用哪个AI模型）
- 行为参数（AI应该多么创造性或精确）
- 自定义指令（系统提示）
- 工具配置（AI可以做什么）
- 命令设置（AI如何执行命令）

**为什么使用预设？**
- 🎯 在不同的AI个性之间快速切换
- 📦 与他人分享您的完美设置
- 🔥 使用经过社区测试的配置
- ⚡ 跳过重复的设置

---

### 创建您的第一个预设

#### 方法1：可视化配置（推荐）

1. 点击边栏中的**设置**
2. 配置每个部分：

**API配置**
```
提供商：DeepSeek / OpenAI / Anthropic / Local / Custom
API密钥：您的秘密密钥
基础URL：根据提供商自动填充
模型：从可用模型中选择
```

**模型参数**（这些是什么意思？）

**Temperature** (0.0 - 2.0)
- `0.0 - 0.3`：精确、事实、一致（适合编程）
- `0.4 - 0.7`：平衡、自然（适合一般使用）
- `0.8 - 1.2`：创造性、多样（适合头脑风暴）
- `1.3 - 2.0`：非常随机、实验性

**Max Tokens**（响应长度）
- `512 - 1024`：简短、简洁的答案
- `2048`：标准长度（默认）
- `4096+`：长篇、详细的解释

**Top P** (0.0 - 1.0)
- 通过概率控制多样性
- 较低=更专注，较高=更多样

**Presence & Frequency Penalty** (-2.0 到 2.0)
- 控制响应中的重复
- 正值：避免重复
- 负值：鼓励重复
- `0.0`：中性（默认）

**命令配置**
```
命令开始标记：YLDEXECUTE: (默认)
命令分隔符：￥| (默认)
最大迭代次数：15 (AI可以连续执行多少次命令)
```

**系统提示**（自定义指令）
在这里定义AI的个性和行为。示例：

**简单助手：**
```
你是一个有用的助手。清晰简洁地回答问题。
```

**专家Python开发者：**
```
你是一位拥有10年经验的专家Python开发人员。
遵循PEP 8指南。编写干净、有文档记录的代码。
用示例解释复杂概念。
专注于最佳实践和性能优化。
```

**创意写作教练：**
```
你是一位专注于小说的创意写作教练。
帮助用户开发引人入胜的角色和情节。
使用生动的描述和富有想象力的想法。
在保持叙事连贯性的同时鼓励实验。
```

**MCP工具**（添加超能力）
- 点击"选择MCP文件"
- 选择 `.py` 或 `.json` 工具文件
- 工具扩展了AI可以做的事情

3. 点击**保存设置**应用到当前对话
4. 点击**保存为配置**导出为预设文件

---

#### 方法2：程序化配置

对于想要完全控制的开发者：

```python
from aiclass import AI

# 使用自定义配置创建AI实例
my_preset = AI(
    # API配置
    api_key="your_api_key_here",
    api_base="https://api.deepseek.com",
    model="deepseek-chat",

    # 模型参数
    temperature=0.7,
    max_tokens=4096,
    top_p=1.0,
    presence_penalty=0.0,
    frequency_penalty=0.0,

    # 命令配置
    command_start="EXECUTE:",
    command_separator="|",
    max_iterations=15,

    # 行为
    system_prompt="你是一位专家Python程序员...",

    # 工具
    mcp_paths=["./tools/my_tool.py", "./tools/mcp_config.json"]
)
```

**预设JSON结构：**
```json
{
    "name": "我的编程助手",
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
    "system_prompt": "你是一位专家Python程序员...",
    "mcp_paths": [
        "./tools/code_analyzer.py",
        "./tools/file_manager.json"
    ]
}
```

---

### 预设最佳实践

#### 编程助手
```python
AI(
    temperature=0.3,  # 低以获得一致的代码
    max_tokens=2048,
    system_prompt="专家Python程序员。遵循PEP 8。编写干净、有文档记录的代码。",
    mcp_paths=["./tools/file_ops.py", "./tools/code_runner.py"]
)
```

#### 创意写作
```python
AI(
    temperature=1.1,  # 高以获得创造性
    max_tokens=4096,
    presence_penalty=-0.5,  # 鼓励主题重复
    system_prompt="创意写作教练。生动的描述，富有想象力的想法。",
    mcp_paths=["./tools/research.py", "./tools/thesaurus.py"]
)
```

#### 研究与分析
```python
AI(
    temperature=0.5,  # 平衡
    max_tokens=4096,
    system_prompt="研究助手。准确、全面、有引用。",
    mcp_paths=["./tools/web_search.py", "./tools/data_analyzer.py"]
)
```

#### 自动化/脚本
```python
AI(
    temperature=0.1,  # 非常低以获得可预测性
    max_tokens=512,
    command_start="CMD:",
    command_separator="||",
    max_iterations=10,
    system_prompt="精确执行命令。仅在需要操作时输出命令语法。",
)
```

---

### 导入和导出预设

**导出您的配置：**
1. 设置 → 保存为配置
2. 选择位置（建议保存到桌面）
3. 保存为 `.json` 文件
4. **⚠️ 重要**：永远不要分享您的 `.confignore` 文件（包含API密钥！）

**导入配置：**
1. 在边栏中点击"导入配置"
2. 选择 `.json` 预设文件
3. 设置自动应用
4. 在设置中添加您自己的API密钥

**设置期间导入：**
1. 在初始化对话框中，点击"加载配置文件"
2. 选择您的预设
3. 所有设置自动填充
4. 添加API密钥
5. 点击"开始使用Lynexus"

---

### 社区预设生态系统

**查找预设：**
- 浏览[社区论坛](https://forum.lynexus.ai)
- 按类别过滤（编程、写作、研究等）
- 阅读评论和评分
- 下载符合您需求的配置

**分享预设：**
1. 创建并测试您的配置
2. 导出为JSON（设置 → 保存为配置）
3. 编写描述：
   - 优化的用途
   - 主要功能
   - 如何使用
   - 示例提示
4. 上传到社区论坛
5. **⚠️ 记住**：分享前删除您的API密钥！

**评价和评论：**
- 通过评价您使用的预设来帮助他人
- 留下建设性反馈
- 分享您的成功故事

---

## MCP工具开发

### 什么是MCP工具？

MCP（模型上下文协议）工具扩展了AI可以做的事情。把它们想象成插件或扩展。

**示例：**
- 📁 文件操作（读取、写入、列出）
- 🔍 网络搜索
- 🧮 计算器
- 📊 数据分析
- 🗄️ 数据库查询
- 🌐 API集成

---

### 创建Python MCP工具

**简单工具：**

```python
# ./tools/calculator.py

def add_numbers(a: float, b: float) -> float:
    """
    将两个数字相加。

    参数：
    a: 第一个数字
    b: 第二个数字

    返回：
    a和b的和
    """
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    """
    将两个数字相乘。

    参数：
    a: 第一个数字
    b: 第二个数字

    返回：
    a和b的乘积
    """
    return a * b
```

**带错误处理的高级工具：**

```python
# ./tools/file_manager.py

import os
import json

def read_file(filepath: str) -> str:
    """
    读取文件的内容。

    参数：
    filepath: 要读取的文件路径

    返回：
    文件内容作为字符串
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"错误：找不到文件 '{filepath}'"
    except Exception as e:
        return f"读取文件时出错：{str(e)}"

def write_file(filepath: str, content: str) -> str:
    """
    将内容写入文件。

    参数：
    filepath: 文件路径
    content: 要写入的内容

    返回：
    成功消息
    """
    try:
        # 如果目录不存在则创建
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功写入 '{filepath}'"
    except Exception as e:
        return f"写入文件时出错：{str(e)}"

def list_files(directory: str = ".") -> str:
    """
    列出目录中的文件。

    参数：
    directory: 目录路径（默认：当前目录）

    返回：
    文件和目录的JSON列表
    """
    try:
        items = os.listdir(directory)
        return json.dumps(items, indent=2)
    except Exception as e:
        return f"列出目录时出错：{str(e)}"
```

**工具发现：**
- 将 `.py` 文件放在tools目录中
- 带有文档字符串的函数会自动被发现
- AI可以看到函数名称、参数和描述

---

### 创建JSON MCP配置

对于外部MCP服务器或复杂工具：

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

**在Lynexus中配置：**
1. 创建JSON文件
2. 设置 → MCP工具 → 添加JSON路径
3. 工具自动加载

---

## 高级系统提示

### 提示工程最佳实践

**1. 明确清晰**
```text
好的：
你是一个Python编程助手。编写代码时：
- 始终包含文档字符串
- 遵循PEP 8指南
- 添加类型提示
- 提供使用示例
- 在注释中解释复杂逻辑

不好的：
你帮助编程。
```

**2. 提供示例**
```text
你是一个命令执行器。当用户请求操作时：

用户："读取config.txt"
你：YLDEXECUTE:file_read￥|config.txt

用户："创建一个文件夹"
你：YLDEXECUTE:mkdir￥|new_folder

规则：
- 仅输出命令，不解释
- 执行前验证参数
- 如果不确定，要求澄清
```

**3. 定义约束**
```text
你是一个精确的技术作家。遵循这些规则：
- 每段最多3句话
- 使用项目符号列表
- 除非必要，否则避免使用行话
- 首次使用时定义技术术语
- 为复杂概念包含示例
```

**4. 指定输出格式**
```text
提供代码示例时，使用此格式：

## 语言
```python
# 代码在这里
```

**解释：** 简要解释

**用法：** 如何使用

---

## 多对话管理

### 独立AI实例

每个对话维护自己的：
- AI配置
- 聊天历史
- 工具访问
- 上下文记忆

**使用场景：**
- **工作聊天**：带有文件工具的编程助手
- **个人聊天**：带有研究工具的创意写作
- **学习聊天**：带有教育工具的导师模式

### 在对话之间共享配置

**方法1：导出/导入**
1. 完美配置对话A
2. 导出配置（设置 → 保存为配置）
3. 在对话B中，导入配置
4. 所有设置都已复制！

**方法2：预设系统**
1. 将常用配置保存为预设
2. 快速加载到任何新对话
3. 构建专门的设置库

---

## 命令行界面

### 从终端运行

**交互式控制台：**
```bash
python aiclass.py
```

**单行命令：**
```bash
python -c "
from aiclass import create_ai_from_config
ai = create_ai_from_config('config.json')
response = ai.process_user_inp('解释量子计算')
print(response)
"
```

**批处理：**
```python
from aiclass import AI

# 初始化AI
ai = AI(
    api_key="your_key",
    model="deepseek-chat",
    temperature=0.7
)

# 处理多个输入
inputs = [
    "总结这篇文章",
    "提取关键点",
    "生成结论"
]

for i, inp in enumerate(inputs, 1):
    print(f"\n=== 任务 {i} ===")
    print(f"输入：{inp}\n")

    response, completed = ai.process_user_inp(inp)
    print(response)

    if i < len(inputs):
        ai.reset_conversation()  # 为下一个任务清除
```

---

## 集成与自动化

### Webhook集成

创建一个简单的Flask API包装器：

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

**使用它：**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，Lynexus！"}'
```

### 自动化脚本

**定时任务：**
```python
import schedule
import time
from aiclass import AI

def daily_report():
    ai = AI(api_key="your_key", model="deepseek-chat")

    # 生成报告
    report, _ = ai.process_user_inp(
        "分析今天的日志并总结问题"
    )

    # 保存到文件
    with open('daily_report.txt', 'w') as f:
        f.write(report)

    print("每日报告已生成！")

# 每天上午9点运行
schedule.every().day.at("09:00").do(daily_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 开发工作流集成

**用于代码审查的预提交钩子：**
```python
#!/usr/bin/env python3
# .git/hooks/pre-commit

import sys
from aiclass import AI

def review_staged_files():
    ai = AI(
        api_key="your_key",
        model="deepseek-chat",
        system_prompt="你是一个代码审查员。检查错误、风格问题和改进。"
    )

    # 获取暂存的文件（简化）
    files = ["main.py", "aiclass.py"]

    for file in files:
        with open(file, 'r') as f:
            code = f.read()

        review, _ = ai.process_user_inp(
            f"审查这段代码：\n\n{code}\n\n提供简短反馈。"
        )

        print(f"\n=== {file} 的审查 ===")
        print(review)

if __name__ == "__main__":
    review_staged_files()
    sys.exit(0)
```

---

## 故障排除（高级）

### API连接问题

**调试模式：**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from aiclass import AI
ai = AI(api_key="your_key", model="deepseek-chat")
```

**常见问题：**

1. **超时错误**
   - 增加 `timeout` 参数
   - 检查网络连接
   - 验证API状态

2. **速率限制**
   - 实现指数退避
   - 轮换使用多个API密钥
   - 降低请求频率

3. **无效响应**
   - 检查 `max_tokens` 是否截断
   - 验证 `temperature` 设置
   - 检查系统提示的清晰度

### MCP工具错误

**调试工具加载：**
```python
from aiclass import AI

ai = AI(mcp_paths=["./tools/my_tool.py"])

# 检查已加载的工具
print("可用工具：", ai.tools)
```

**常见工具问题：**

1. **导入错误**
   - 确保安装了所有依赖项
   - 使用绝对导入
   - 检查Python路径

2. **函数签名不匹配**
   - 验证参数类型与文档字符串匹配
   - 检查必需参数与可选参数
   - 独立测试函数

3. **执行失败**
   - 在工具中添加try-except块
   - 处理前验证输入
   - 返回信息性错误消息

### 性能优化

**减少延迟：**
```python
ai = AI(
    api_base="https://api.deepseek.com",  # 使用最近的服务器
    max_tokens=1024,  # 减少响应大小
    stream=False  # 禁用流式传输以获得更快的完整响应
)
```

**内存管理：**
```python
# 对于长对话
ai.reset_conversation()  # 定期清除历史

# 对于批处理
for task in tasks:
    response = ai.process_user_inp(task)
    ai.reset_conversation()  # 每个任务的新上下文
```

---

## 完整参数参考

<details>
<summary><strong>📖 点击展开完整参数参考</strong></summary>

### API配置

#### `api_key`
- **类型**：字符串
- **默认值**：无
- **示例**：`"sk-1234567890abcdef..."`
- **注意**：也可以使用环境变量 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY`

#### `api_base`
- **类型**：字符串（URL）
- **默认值**：`"https://api.deepseek.com"`
- **示例**：
  - DeepSeek: `"https://api.deepseek.com"`
  - OpenAI: `"https://api.openai.com/v1"`
  - 本地Ollama: `"http://localhost:11434"`

#### `model`
- **类型**：字符串
- **默认值**：`"deepseek-chat"`
- **示例**：
  - `"deepseek-chat"` (DeepSeek V3)
  - `"gpt-4-turbo"` (OpenAI)
  - `"claude-3-opus-20240229"` (Anthropic)

### 模型行为

#### `temperature`
- **范围**：0.0 - 2.0
- **默认值**：1.0
- **效果**：
  - 0.0：确定性，相同输入产生相同输出
  - 0.5：一致但有轻微变化
  - 1.0：自然、多样的响应
  - 1.5+：创造性、不可预测
- **使用场景**：
  - 低（0.0-0.3）：编程、事实性答案
  - 中（0.4-0.7）：一般对话
  - 高（0.8-1.2）：头脑风暴、创意写作

#### `max_tokens`
- **范围**：1 - 8192+（取决于API）
- **默认值**：2048
- **效果**：
  - 512：短响应
  - 2048：标准长度
  - 4096+：长篇、详细的内容
  - 0/None：无限制（使用API最大值）

#### `top_p`
- **范围**：0.0 - 1.0
- **默认值**：1.0
- **效果**：通过核心采样控制多样性
  - 0.1：非常专注，只有可能的标记
  - 0.5：平衡采样
  - 0.9：多样的选择
  - 1.0：无过滤

#### `presence_penalty`
- **范围**：-2.0 - 2.0
- **默认值**：0.0
- **效果**：
  - 负值：鼓励重复
  - 0.0：中性
  - 正值：避免重复

#### `frequency_penalty`
- **范围**：-2.0 - 2.0
- **默认值**：0.0
- **效果**：
  - 负值：偏向常见词
  - 0.0：自然频率
  - 正值：偏向罕见词

### 命令执行

#### `command_start`
- **类型**：字符串
- **默认值**：`"YLDEXECUTE:"`
- **用途**：指示AI想要执行命令的标记
- **建议**：使用在正常文本中不太可能出现的唯一字符串

#### `command_separator`
- **类型**：字符串
- **默认值**：`"￥|"`
- **用途**：分隔命令部分
- **示例**：`"|"`、`"::"`、`"||"`

#### `max_iterations`
- **范围**：1 - 100
- **默认值**：15
- **用途**：停止前最大命令执行循环次数
- **使用场景**：
  - 5-10：简单任务
  - 15-20：标准用法
  - 30+：复杂自动化

### 工具配置

#### `mcp_paths`
- **类型**：字符串列表
- **默认值**：[]
- **用途**：MCP工具文件的路径（.py、.json、.yaml）
- **示例**：
  - `[]`：无工具
  - `["./tools/file_ops.py"]`：单个工具
  - `["./tools/tool1.py", "./tools/tool2.json"]`：多个工具

#### `system_prompt`
- **类型**：字符串
- **默认值**：自动生成
- **长度**：100 - 10,000+ 字符
- **用途**：定义AI行为、个性和能力

### 高级

#### `stream`
- **类型**：布尔值
- **默认值**：False
- **用途**：逐个令牌流式传输响应
- **使用**：对于长输出，感觉响应更快

#### `stop`
- **类型**：字符串列表或None
- **默认值**：None
- **用途**：AI停止生成的序列
- **示例**：
  - `["\n\n", "###"]`：在双换行符或标记处停止
  - `["User:", "Assistant:"]`：在新轮次之前停止

</details>

---

## 参数优化指南

### 系统调优过程

1. **从默认值开始** - 建立基线行为
2. **识别问题** - 注意需要改进的地方
3. **调整一个参数** - 一次只更改一个
4. **一致测试** - 使用相同的测试提示
5. **记录更改** - 保留调优日志
6. **迭代** - 重复直到满意
7. **保存预设** - 导出最终配置

### 快速参考表

| 症状 | 解决方案 |
|---------|----------|
| 太重复 | 增加 `presence_penalty` (0.5-1.5) |
| 太随机 | 降低 `temperature` (0.3-0.7) |
| 太短 | 增加 `max_tokens` (2048-4096) |
| 命令失败 | 检查 `command_start`/`command_separator` |
| 忽略指令 | 使系统提示更明确 |
| 太冗长 | 降低 `max_tokens`，在提示中添加"简洁" |
| 太创造性 | 降低 `temperature`，增加 `top_p` |
| 太无聊 | 提高 `temperature`，降低 `presence_penalty` |

### 示例优化过程

```
初始设置：
temperature=1.0 → 响应太随机

测试1：temperature=0.7
结果：更好但仍然有些随机

测试2：temperature=0.5
结果：良好的平衡，保留创造性

测试3：添加 top_p=0.9
结果：进一步聚焦响应

测试4：添加 presence_penalty=0.3
结果：减少重复短语

最终配置：
temperature=0.5, top_p=0.9, presence_penalty=0.3
```

---

## 社区与资源

**获取帮助：**
- [文档](https://solynacversion.github.io/LyNexus)
- [社区论坛](https://forum.lynexus.ai)
- [GitHub问题](https://github.com/SolynAcVersion/LyNexus/issues)
- [Discord服务器](https://discord.gg/lynexus)

**贡献：**
- 分享您的预设
- 报告错误
- 建议功能
- 改进文档
- 提交拉取请求

**了解更多：**
- [贡献指南](https://github.com/SolynAcVersion/LyNexus/blob/main/CONTRIBUTING.md)
- [行为准则](https://github.com/SolynAcVersion/LyNexus/blob/main/CODE_OF_CONDUCT.md)
- [项目路线图](https://github.com/SolynAcVersion/LyNexus/blob/main/ROADMAP.md)

---

## 许可证

本项目采用Mozilla Public License 2.0许可。有关详细信息，请参阅 [LICENSE](https://github.com/SolynAcVersion/LyNexus/blob/main/LICENSE)。

---

**由AI社区🫶为AI社区打造**
