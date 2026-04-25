# 快速开始指南

## 5 分钟快速上手

### 1️⃣ 安装依赖

**Windows 用户：**
```bash
# 双击运行
setup.bat
```

**或者手动安装：**
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 配置 API Key

编辑 `src/config.py`：

```python
MODEL_NAME = "qwen-turbo"
API_KEY = "sk-xxxxxxxxxxxxx"  # 替换为你的 API Key
TEMPERATURE = 0.1
```

**获取 API Key：**
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录
3. 创建 API Key
4. 复制到 config.py

### 3️⃣ 准备资料

将你的笔记、文档放入 `raw/` 目录：

```bash
raw/
├── notes/
│   ├── 笔记 1.txt
│   └── 笔记 2.md
└── papers/
    └── 文档.pdf
```

**支持格式：**
- ✅ .txt
- ✅ .md
- ✅ .pdf
- ✅ .jpg, .png（OCR 识别）

### 4️⃣ 运行

```bash
python app.py
```

程序会自动：
1. 编译知识库
2. 进入问答模式

**示例对话：**
```
You: 漩涡鸣人是谁？

漩涡鸣人是火之国木叶隐村的忍者...

✅ 本次 Tokens 使用：64
📊 累计 Tokens 使用：64
```

### 5️⃣ 上传到 GitHub

```bash
# 初始化 Git
git init

# 添加文件
git add .

# 提交
git commit -m "Initial commit"

# 创建 GitHub 仓库后推送
git remote add origin https://github.com/YOUR_USERNAME/karpathy-kb.git
git push -u origin main
```

详细教程：[GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md)

## 📚 更多文档

- **完整文档**：[README.md](README.md)
- **GitHub 上传教程**：[GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md)
- **使用示例**：[LLM_USAGE_EXAMPLE.md](LLM_USAGE_EXAMPLE.md)
- **Token 使用指南**：[STREAM_USAGE_GUIDE.md](STREAM_USAGE_GUIDE.md)

## ❓ 遇到问题？

### API Key 错误
```
检查 config.py 中的 API Key 是否正确
确认 API Key 已激活且有余额
```

### 依赖安装失败
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 其他问题
查看 [README.md](README.md) 的常见问题部分

## 🎉 开始使用吧！

现在你已经完成了所有设置，开始探索知识库的威力吧！

```bash
python app.py
```

---

**Happy Coding! 🚀**
