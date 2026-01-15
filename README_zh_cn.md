# Lynexus - 社区驱动的AI智能体平台

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.46-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MPL 2.0-green" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10&#43;-yellow" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey" alt="Platform">
</p>

<div align="center">
  <strong>用社区驱动的智能，赋能您的AI开发</strong>
</div>

<div align="center">
  <a href = "https://github.com/SolynAcVersion/LyNexus/blob/main/README.md">English</a>
</div>

## 🌟 Lynexus是什么？

Lynexus是一个**社区驱动的AI智能体平台**，使开发者能够创建、定制和分享具有可配置提示词、工具和行为参数的智能体。该平台以灵活性和协作为核心理念打造，将AI开发转变为共享的体验。

🎯 **核心理念**：一次创造，处处分享。向他人学习，加速构建。

## ✨ 功能特性

### 🤖 **灵活的AI配置**
- **模型无关**：连接不同的AI模型（DeepSeek、OpenAI等）
- **参数自定义**：精确调节温度、tokens数、惩罚项等参数
- **自定义系统提示**：根据需要量身定制AI行为
- **MCP集成**：无缝集成模型上下文协议工具

### 🔄 **社区驱动的生态系统**
- **一键导出**：打包整个配置用于分享
- **一键导入**：立即使用他人优化的配置
- **论坛集成**：在社区论坛分享和发现配置
- **站在巨人肩膀上**：基于经过社区测试的配置构建

### 🎨 **现代化界面**
- **Windows 11风格UI**：清晰、暗色调界面
- **对话管理**：支持多个聊天会话，每个都有独立的AI实例
- **实时执行**：观看AI执行命令并实时状态更新
- **导出格式**：将聊天保存为TXT、JSON或Markdown格式

### ⚡ **高级工具**
- **命令执行**：AI可以执行shell命令（可配置）
- **工具集成**：通过MCP连接各种API和服务
- **执行控制**：随时停止长时间运行的操作
- **历史管理**：保留和加载对话历史

## 🚀 快速开始

#### 环境要求
- Python 3.8 或更高版本
- AI API密钥（DeepSeek、OpenAI等）

#### 安装

```bash
# 克隆仓库
git clone https://github.com/SolynAcVersion/LyNexus.git
cd lynexus

# 安装依赖
uv pip install -r requirements.txt
```

#### 启动选项
**选项1：从源代码运行**
```bash
uv run python ./main.py
```

**选项2：下载发行版（即将推出）**
- 从[发布页面](https://github.com/SolynAcVersion/LyNexus/releases/new)下载最新发行版
- 解压并运行 Lynexus.exe

## 🛠️ 配置
Lynexus让您完全掌控AI智能体：

**模型配置**
```python
# 完整的参数自定义
mcp_paths=None, 
api_key=None,
api_base=None,
model=None,
system_prompt=None,
temperature=1.0,
max_tokens=None,
top_p=1.0,
stop=None,
stream=False,
presence_penalty=0.0,
frequency_penalty=0.0,
command_start="YLDEXECUTE:",
command_separator=￥|,
max_iterations=15
```

#### 对话管理
- **多个聊天会话**：每个会话都有独立的AI实例
- **持久化历史**：聊天内容会被保存并可导出
- **上下文保持**：AI会记住对话历史
- **导出/导入**：分享您完整的聊天配置

## 📦 一键分享工作流

#### 导出您的配置
1. 完美地配置您的AI智能体
2. 点击“导出配置”
3. 在我们的论坛上分享`.json`文件
4. 帮助他人从您的工作中获益
5. **请勿泄露您的 `.confignore` 文件**

#### 导入他人的配置
1. 浏览社区论坛
2. 下载吸引您的配置文件
3. 点击“导入配置”
4. 立即使用优化过的设置

## 🤝 社区与贡献

#### 加入我们的社区
- **论坛**：分享配置并获得帮助
- **Discord**：实时讨论
- **GitHub问题**：报告错误和请求功能
- **展示区**：分享您的优秀AI智能体

#### 贡献方式

欢迎贡献！您可以通过以下方式帮助我们：

1. **分享配置**：将您的最佳配置上传到论坛
2. **报告错误**：帮助我们提高稳定性
3. **建议功能**：什么能让Lynexus变得更好？
4. **改进文档**：帮助他人快速上手
5. **代码贡献**：提交Pull Request

有关详情，请查看我们的[贡献指南]()。

## 📁 项目结构
```text
lynexus/
├── main.py              # 应用程序入口点
├── aiclass.py           # 核心AI功能
├── ui/                  # 用户界面组件
│   ├── chat_box.py      # 主聊天界面
│   ├── init_dialog.py   # 初始化对话框
│   └── settings_dialog.py # 设置界面
├── config/              # 配置管理
└── utils/               # 实用工具函数

```

## 🔧 高级用法

#### 自定义MCP服务器/文件

1. 将MCP服务器放在`.json`文件中
2. 准备好MCP `.py`文件
3. 在设置中配置文件路径
4. AI将自动发现并使用可用的工具

#### 系统集成

- **API密钥管理**：安全存储密钥
- **环境变量**：使用 DEEPSEEK_API_KEY 或 OPENAI_API_KEY
- **桌面集成**：将导出保存到桌面以便快速访问




## 📄 许可证
本项目采用MPL 2.0许可证 - 有关详细信息，请参阅[许可证](https://github.com/SolynAcVersion/Lym/blob/main/LICENSE)文件。

## 🙏 致谢
- **AI社区**：感谢分享知识和配置的社区
- **开源项目**：使本平台成为可能
- **贡献者**：每位帮助改进Lynexus的人
- **用户**：感谢信任我们的AI开发需求

<div align="center"> <p> <strong>由AI社区🫶为AI社区打造</strong> </p> <p> <a href="https://forum.lynexus.ai">论坛</a> • <a href="https://solynacversion.github.io/LyNexus">文档</a> • <a href="https://github.com/SolynAcVersion/LyNexus/issues">问题反馈</a> • <a href="https://github.com/SolynAcVersion/LyNexus/discussions">讨论区</a> </p> </div>
<p align="center"></p>
<div align="center"> <i>如果觉得这个项目有用，请给它一个⭐吧！</i> </div>