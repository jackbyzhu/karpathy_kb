# Karpathy Knowledge Base

一个基于 LangChain 和通义千问的智能知识库系统，支持文档编译、知识管理和智能问答。

## ✨ 特性

- 📚 **多格式支持**：支持 PDF、Markdown、TXT、图片等多种格式文档
- 🤖 **AI 驱动**：使用通义千问（Qwen）大模型进行知识提取和问答
- 🔗 **双向链接**：自动生成概念间的关联，形成知识网络
- 💬 **智能对话**：支持流式输出的智能问答系统
- 📊 **Token 统计**：实时显示和累计 Token 使用情况
- 🗂️ **增量编译**：支持增量和全量两种编译模式
- 🎯 **细粒度拆分**：自动将知识拆分为独立的概念文件

## 📋 目录结构

```
karpathy-kb/
├── raw/                    # 原始资料目录
│   ├── notes/             # 文本笔记
│   └── papers/            # 论文 PDF
├── wiki/                  # 生成的知识库
│   ├── concepts/          # 概念文件
│   ├── people/            # 人物文件
│   └── index/             # 索引文件
├── output/                # 输出目录
│   └── sessions/          # 对话历史
├── src/                   # 源代码
│   ├── compiler.py        # 编译器
│   ├── ingest.py          # 文档加载
│   ├── llm.py             # LLM 封装
│   ├── query_engine.py    # 查询引擎
│   ├── config.py          # 配置
│   └── linter.py          # 代码检查
├── app.py                 # 主程序
├── main.py                # 测试入口
├── requirements.txt       # 依赖包
└── README.md              # 说明文档
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- 通义千问 API Key

### 2. 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd karpathy-kb

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 API Key

编辑 `src/config.py` 文件：

```python
MODEL_NAME = "qwen-turbo"  # 使用 qwen-turbo 模型（速度快）
API_KEY = "your-api-key-here"  # 替换为你的通义千问 API Key
TEMPERATURE = 0.1  # 模型温度，越低越稳定
```

**获取 API Key：**
1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册/登录账号
3. 创建 API Key
4. 复制到配置文件中

### 4. 准备资料

将你的资料放入 `raw/` 目录：

```bash
raw/
├── notes/              # 放置 .txt, .md 文件
│   ├── 笔记 1.txt
│   └── 笔记 2.md
└── papers/             # 放置 .pdf 文件
    └── 论文.pdf
```

**支持格式：**
- 📄 `.txt` - 纯文本文件
- 📝 `.md` - Markdown 文件
- 📕 `.pdf` - PDF 文档
- 🖼️ `.jpg`, `.jpeg`, `.png`, `.gif` - 图片文件（OCR 识别）

### 5. 编译知识库

```bash
# 运行编译
python app.py
```

编译过程：
1. 自动读取 `raw/` 目录下的所有文件
2. 使用 LLM 提取知识点
3. 生成结构化的 Markdown 文件到 `wiki/` 目录
4. 创建索引和双向链接

**编译模式：**

```python
# 增量编译（默认，只处理新文件）
compile(incremental=True)

# 全量编译（重新处理所有文件）
compile(incremental=False)

# 指定文件编译
compile(raw_files=["笔记 1.txt", "笔记 2.md"])
```

### 6. 开始问答

编译完成后，程序会自动进入问答模式：

```
=== Testing query system ===
Enter your questions (type 'exit' to quit):

You: 漩涡鸣人是谁？
Processing...

漩涡鸣人是火之国木叶隐村的忍者，四代火影波风水门与漩涡玖辛奈之子...

✅ 本次 Tokens 使用：
   - 输入：14
   - 输出：50
   - 总计：64

📊 累计 Tokens 使用：64

You: exit
```

**特性：**
- 💬 流式输出（文字逐个显示）
- 📊 实时 Token 统计
- 💾 自动保存对话历史
- 🔄 支持多会话管理

## 📖 详细使用

### LLM 模块使用

#### 基本调用

```python
from src.llm import LLM

llm = LLM(model_name="qwen-turbo", api_key="your-key")

# 普通调用
result = llm.chat_invoke("你好", system_prompt="你是一个助手")
print(result['response'])
print(f"Tokens: {result['usage']['total_tokens']}")

# 流式调用
for chunk in llm.chat_stream("讲故事"):
    print(chunk['content'], end='')

# 获取 tokens 信息
usage = llm.get_usage()
print(f"Total: {usage['total_tokens']}")
```

#### 直接使用底层模型

```python
model = llm.get_llm()
messages = [{"role": "user", "content": "你好"}]
response = model.invoke(messages)
print(response.content)
```

### 查询引擎使用

```python
from src.query_engine import query

# 非流式
answer, usage = query(
    question="什么是查克拉？",
    session_id="session1",
    stream=False
)

# 流式
generator = query(
    question="什么是查克拉？",
    session_id="session1",
    stream=True
)
answer, usage = generator()
```

### 编译器使用

```python
from src.compiler import compile_knowledge, compile

# 直接编译文本
raw_text = "原始资料内容..."
knowledge_base, usage, metadata = compile_knowledge(raw_text)

# 使用编译函数
compile(
    incremental=True,           # 增量编译
    raw_dir="raw",              # 原始资料目录
    output_dir="wiki"           # 输出目录
)
```

## ⚙️ 配置说明

### config.py 配置项

```python
# 模型配置
MODEL_NAME = "qwen-turbo"      # 模型名称
API_KEY = "your-key"           # API Key
TEMPERATURE = 0.1              # 温度（0-1）

# 目录配置
RAW_DIR = "raw"                # 原始资料目录
WIKI_DIR = "wiki"              # 知识库目录
OUTPUT_DIR = "output"          # 输出目录

# 编译配置
COMPILE_PROMPT = "..."         # 编译提示词模板
INCREMENTAL_PROMPT = "..."     # 增量编译提示词
```

### 模型选择

| 模型 | 速度 | 质量 | 价格 | 适用场景 |
|------|------|------|------|----------|
| qwen-turbo | ⚡⚡⚡ | ⭐⭐ | 💰 | 快速迭代、测试 |
| qwen-plus | ⚡⚡ | ⭐⭐⭐ | 💰💰 | 平衡性能 |
| qwen-max | ⚡ | ⭐⭐⭐⭐ | 💰💰💰 | 高质量要求 |

**推荐：** 开发测试使用 `qwen-turbo`，生产环境使用 `qwen-plus` 或 `qwen-max`

## 📊 Token 管理

### 查看 Token 使用

每次对话都会显示：
```
✅ 本次 Tokens 使用：
   - 输入：14
   - 输出：50
   - 总计：64
   - 缓存：0

📊 累计 Tokens 使用：1234
```

### 节省 Token 技巧

1. **使用增量编译**：只处理新文件
2. **合理设置 temperature**：越低越稳定，减少重复调用
3. **使用 qwen-turbo**：速度快，成本低
4. **优化提示词**：精简不必要的描述

## 🔧 高级功能

### 对话历史管理

对话历史保存在 `output/sessions/` 目录：

```python
# 加载历史对话
from src.query_engine import load_conversation

history = load_conversation("session1")

# 保存对话
from src.query_engine import save_conversation

save_conversation("session1", "user", "问题")
save_conversation("session1", "assistant", "回答")
```

### 知识库检查

```python
from src.linter import linter

# 检查知识库完整性
linter()
```

### 自定义提示词

编辑 `src/config.py` 中的 `COMPILATION_PROMPT` 和 `INCREMENTAL_COMPILATION_PROMPT`。

## 🐛 常见问题

### 1. API Key 错误

**错误信息：** `AuthenticationError: Invalid API key`

**解决方案：**
- 检查 API Key 是否正确
- 确认 API Key 已激活
- 检查是否有余额

### 2. 依赖安装失败

**错误信息：** `ERROR: Could not find a version that satisfies the requirement...`

**解决方案：**
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. PDF 无法读取

**解决方案：**
```bash
# 安装额外依赖
pip install pdfplumber
pip install pdf2image
```

### 4. Token 使用过快

**解决方案：**
- 使用 `qwen-turbo` 模型
- 减少单次编译文件数量
- 分批次编译

### 5. 知识库为空

**解决方案：**
- 确认 `raw/` 目录有文件
- 检查文件格式是否支持
- 查看编译日志是否有错误

## 📝 输出示例

### 生成的人物文件

```markdown
---
title: 漩涡鸣人
date: 2024-01-15
tags: [火影忍者，人物，木叶]
sources: [漩涡鸣人_人物介绍.txt]
---

# 漩涡鸣人

## 简介
漩涡鸣人是《火影忍者》的主角，火之国木叶隐村的忍者...

## 详细说明
### 基本信息
- 姓名：漩涡鸣人
- 生日：10 月 10 日
- 年龄：17 岁

### 能力
- 影分身之术
- 螺旋丸
- 九尾模式

## 相关链接
- [[宇智波佐助]] - 挚友
- [[旗木卡卡西]] - 老师
- [[九尾]] - 体内尾兽

## 待探索问题
- 鸣人如何成为七代火影？
- 鸣人与佐助的最终决战？
```

### 生成的索引文件

```markdown
---
title: README
date: 2024-01-15
---

# 知识库导航

## 人物
- [[漩涡鸣人]]
- [[宇智波佐助]]
- [[旗木卡卡西]]

## 概念
- [[查克拉]]
- [[写轮眼]]
- [[尾兽]]

## 组织
- [[晓组织]]
- [[第七班]]
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone <your-repo>
cd karpathy-kb

# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8

# 运行测试
pytest

# 代码格式化
black src/ app.py

# 代码检查
flake8 src/
```

## 📄 许可证

MIT License

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain)
- [通义千问](https://www.aliyun.com/product/dashscope)
- [火影忍者](https://www.naruto.com/)

## 📮 联系方式

如有问题，请提 Issue 或联系开发者。

---

**Made with ❤️ using LangChain and Qwen**
