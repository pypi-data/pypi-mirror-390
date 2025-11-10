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

## 安装

### 从源码安装

```bash
git clone https://github.com/W1412X/aibash.git
cd aibash
pip install -e .
```

### 使用 pip 安装

```bash
pip install aibash
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

## 命令行选项

- `-l, --lang QUERY`: 自然语言描述，用于生成 shell 命令
- `--config PATH`: 指定配置文件路径（默认: ~/.aibash/config.yaml）
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
│   ├── config.py          # 配置管理
│   ├── ai_client.py       # AI 模型客户端
│   ├── history.py         # 历史记录管理
│   ├── interactive.py     # 交互式选择
│   ├── prompt.py          # Prompt 管理
│   └── main.py            # 主程序入口
├── setup.py
├── requirements.txt
└── README.md
```

## 开发

### 运行测试

```bash
python -m aibash.main -l "测试命令"
```

### 构建分发包

```bash
python setup.py sdist bdist_wheel
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

