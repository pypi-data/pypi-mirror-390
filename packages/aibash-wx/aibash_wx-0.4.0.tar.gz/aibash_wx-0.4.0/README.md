# AIBash

AI 驱动的 Shell 命令生成工具

## 简介

AIBash 是一个智能命令行工具，能够根据自然语言描述生成对应的 Shell 命令。支持 OpenAI API 和本地 Ollama 模型。

**注意**: 命令行内的所有提示信息均为英文，以避免字符编码问题。文档提供中英文两种版本。

## 功能特性

- 🤖 **AI 命令生成**: 根据自然语言描述生成 Shell 命令
- 🔄 **交互式选择**: 支持执行、修改或放弃生成的命令
- 📝 **历史记录**: 保存命令执行历史和输出，提供上下文支持
- ⚙️ **灵活配置**: 支持多种配置选项（模型、密钥、系统信息等）
- 🌐 **多平台支持**: 支持 macOS、Windows、Linux
- 🔌 **多模型支持**: 支持 OpenAI API 和 Ollama 本地模型
- 🧠 **自动化任务**: 通过 `-a` 自动规划多步命令，逐步执行完成复杂任务
- 🪟 **新终端执行**: 通过 `-new` 在新的终端窗口中运行命令，保持当前窗口清爽
- 🌏 **双语界面**: 命令行提示支持英文/中文两种语言，可随时切换

## 安装

### 从源码安装

```bash
git clone https://github.com/W1412X/aibash.git
cd aibash
pip install -e .
```

### 使用 pip 安装

```bash
pip install aibash-wx
```

## 快速开始

### 1. 配置

首次使用前需要配置模型连接信息。配置文件位于 `~/.aibash/config.yaml`。

#### OpenAI API 配置示例

```yaml
model:
  provider: openai
  api_base: https://api.openai.com/v1
  api_key: your-api-key-here
  model_name: gpt-3.5-turbo

history:
  enabled: true
  max_records: 50
  include_output: true

system_info: "Linux 5.15.0 (x86_64)"
use_default_prompt: true
```

#### Ollama 配置示例

```yaml
model:
  provider: ollama
  api_base: http://localhost:11434
  api_key: ""  # Ollama 不需要密钥
  model_name: llama2

history:
  enabled: true
  max_records: 50
  include_output: true

system_info: "Linux 5.15.0 (x86_64)"
use_default_prompt: true
```

### 2. 使用

```bash
# 基本用法
aibash -l "列出当前目录下的所有文件"

# 指定配置文件
aibash --config /path/to/config.yaml -l "查找包含test的文件"

# 自动模式示例（逐步完成任务并逐条确认）
aibash -a "查看当前项目依赖并生成 requirements.txt"

# 自动/分析模式从文件读取任务描述（需与 -a 或 --analyze 搭配）
aibash -a "" -p /path/to/task_description.txt
aibash --analyze "进行代码审查" -p /path/to/task_description.txt

# 在新的终端窗口中执行命令
aibash -new -l "运行当前目录下的测试用例"

# 项目分析模式（生成项目摘要后再执行）
aibash --analyze "梳理项目模块并输出重构建议"

# 查看帮助
aibash -h

# 初始化配置（首次使用）
aibash --init

# 查看命令历史
aibash --history

# 清空命令历史
aibash --clear-history

# 测试 AI 连接
aibash --test
```

- `-l, --lang QUERY`: 自然语言描述，用于生成 shell 命令
- `-a, --auto QUERY`: 自动模式，根据自然语言目标规划并执行多步操作（默认最多 30 步，不生成项目摘要）
- `--analyze QUERY`: 项目分析模式，在执行步骤前自动生成项目摘要，适合大型工程
- `-p, --plan-file PATH`: 指定文件作为任务描述输入，需与 `-a/--auto` 或 `-A/--analyze` 搭配使用
- `--auto-approve-all`: 自动模式下自动批准所有动作（无确认）
- `--auto-approve-commands`: 自动模式下自动批准命令执行
- `--auto-approve-files`: 自动模式下自动批准文件读取
- `--auto-approve-web`: 自动模式下自动批准网络请求
- `--auto-max-steps N`: 自动模式下限制最多执行的步骤数量（默认 30）
- `--ui-language {en,zh}`: 临时切换界面语言（默认从配置读取，未设置时为英文）
- `--config PATH`: 指定配置文件路径（默认: ~/.aibash/config.yaml）
- `-new, --new-terminal`: 将命令在新的终端窗口中执行（未指定时默认在当前终端执行）
- `--init`: 交互式初始化配置文件
- `--history`: 查看命令执行历史
- `--clear-history`: 清空命令执行历史
- `--test`: 测试 AI 连接
- `-h, --help`: 显示帮助信息
- `-v, --version`: 显示版本信息

生成命令后，你可以选择：

- `[e]` 执行命令 - 直接执行生成的命令
- `[c]` 复制到剪贴板 - 将命令复制到剪贴板
- `[m]` 修改命令 - 修改命令后再执行
- `[s]` 跳过/放弃 - 不执行命令
- `[h]` 显示帮助 - 显示帮助信息

当命令执行失败时，AIBash 会自动根据最新历史记录和错误输出请求 AI 生成新的命令建议，连同一条中文提示一起展示，帮助你快速迭代。

### 自动模式（-a）

自动模式让 AIBash 充当一个“执行代理”，根据你的自然语言描述分步规划并完成任务：

- 模型每次只会规划一个动作（运行命令、读取文件、访问网络、向你提问或结束）
- 每个命令、文件读取或网络访问都会先询问你是否确认执行
- 执行结果会反馈给模型，帮助其决定下一步操作
- 适合需要多步协作的任务，如“拉取最新代码、安装依赖并运行测试”等
- 可使用 `--auto-approve-*` 参数细粒度控制哪些操作无需确认，并可通过 `--auto-max-steps` 限制最多执行的步骤数
- 如某一步执行失败，自动模式会向模型反馈错误详情，并自动重新规划新的命令或策略
- 自动模式默认不会生成项目摘要，专注于执行用户任务；如需对项目结构进行深入分析，请使用 `--analyze`
- 项目分析模式会先对目录下的关键文件进行摘要（支持缓存与并发），帮助模型快速理解项目结构，再继续执行计划；摘要缓存保存在项目下 `.aibash_cache/summary_cache.json`
- 自动模式和项目分析模式均支持从配置文件预设是否自动确认命令/读文件/访问网络，以及是否静默展示读取/目录类输出（`automation.allow_silence`，默认开启）

可以与 `-new` 搭配，在新的终端窗口中执行实际命令，确保自动模式界面保持整洁。

## 配置说明

### 模型配置

- `provider`: 模型提供商 (`openai` 或 `ollama`)
- `api_base`: API 基础 URL
- `api_key`: API 密钥（Ollama 可为空）
- `model_name`: 模型名称

### 历史记录配置

- `enabled`: 是否启用历史记录
- `max_records`: 最大记录数
- `include_output`: 是否包含命令输出
- `history_file`: 历史记录文件路径（自动设置）

### 其他配置

- `system_info`: 系统信息（用于生成更准确的命令）
- `custom_prompt`: 自定义 prompt 模板
- `use_default_prompt`: 是否使用默认 prompt
- `ui.language`: 界面语言（`en` 或 `zh`，默认 `en`）
- `automation`: 自动模式默认行为配置（如自动确认、最大步骤、项目摘要并发等）

```yaml
automation:
  auto_confirm_all: false
  auto_confirm_commands: false
  auto_confirm_files: false
  auto_confirm_web: false
  max_steps: 30
  allow_silence: true
  enable_auto_summary: false
  summary_workers: 4

ui:
  enable_colors: true
  single_key_mode: true
  language: en
```

命令行中的 `--ui-language` 仅对当前会话生效，如需长期使用请在配置文件的 `ui.language` 中设置。

## 自定义 Prompt

你可以自定义 prompt 模板来更好地控制 AI 的行为。在配置文件中设置 `custom_prompt`，并使用以下占位符：

- `{system_info}`: 系统信息
- `{history_context}`: 历史上下文
- `{user_query}`: 用户查询

示例：

```yaml
custom_prompt: |
  你是一个专业的命令行助手。
  系统: {system_info}
  {history_context}
  用户需求: {user_query}
  请生成对应的shell命令：
use_default_prompt: false
```

## 项目结构

```
aibash/
├── aibash/
│   ├── __init__.py
│   ├── main.py            # 主程序入口
│   ├── automation.py      # 自动模式执行器
│   ├── agents/            # 不同模型的 Agent 实现
│   ├── config.py          # 配置加载与校验
│   ├── history.py         # 历史记录管理
│   ├── interactive.py     # 交互式命令选择
│   ├── prompt.py          # Prompt 模板与工具
│   └── utils/             # 终端、剪贴板等工具方法
├── pyproject.toml
├── requirements.txt
├── README.md
└── CONFIG_EXAMPLES.md
```

## 开发

### 运行测试

```bash
python -m aibash.main -l "测试命令"
```

### 构建分发包

```bash
pip install build
python -m build
```

## 文档

- [中文文档](README.md) - 本文档
- [English Documentation](README_EN.md) - English version

## 许可证

MIT License

## 作者

github/W1412X

## 贡献

欢迎提交 Issue 和 Pull Request！

