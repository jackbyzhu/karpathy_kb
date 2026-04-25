# GitHub 上传教程

本教程将指导你如何将 Karpathy Knowledge Base 项目上传到 GitHub。

## 📋 准备工作

### 1. 注册 GitHub 账号

如果没有 GitHub 账号，先访问 [github.com](https://github.com) 注册。

### 2. 安装 Git

**Windows 用户：**
- 下载：https://git-scm.com/download/win
- 安装后打开 Git Bash

**Mac 用户：**
```bash
# 使用 Homebrew 安装
brew install git
```

**Linux 用户：**
```bash
# Ubuntu/Debian
sudo apt-get install git

# CentOS/Fedora
sudo yum install git
```

### 3. 配置 Git

```bash
# 设置用户名
git config --global user.name "Your Name"

# 设置邮箱（使用 GitHub 注册邮箱）
git config --global user.email "your.email@example.com"

# 查看配置
git config --list
```

## 🚀 上传方法

### 方法一：使用命令行（推荐）

#### 步骤 1：初始化 Git 仓库

```bash
# 进入项目目录
cd c:\Users\94795\Desktop\karpathy\karpathy-kb

# 初始化 Git 仓库
git init
```

#### 步骤 2：创建 .gitignore 文件

创建 `.gitignore` 文件，忽略不需要上传的文件：

```bash
# 虚拟环境
venv/
env/
__pycache__/
*.pyc
*.pyo

# API Key 和敏感信息
src/config.py
.env
*.env

# 编译输出
wiki/
output/

# IDE 配置
.vscode/
.idea/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db

# 日志文件
*.log
```

**重要：** 将你的 API Key 从 config.py 中移除或添加到 .gitignore

#### 步骤 3：添加文件到暂存区

```bash
# 添加所有文件
git add .

# 或者添加特定文件
git add README.md
git add requirements.txt
git add src/
git add app.py
git add main.py

# 查看状态
git status
```

#### 步骤 4：提交到本地仓库

```bash
# 提交更改
git commit -m "Initial commit: Karpathy Knowledge Base

- 添加知识库编译功能
- 支持多格式文档处理
- 集成通义千问 LLM
- 实现智能问答系统
- 添加 Token 统计功能
- 完善文档和示例"
```

#### 步骤 5：创建 GitHub 仓库

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 填写信息：
   - **Repository name**: `karpathy-kb`（或其他名字）
   - **Description**: "A smart knowledge base system powered by LangChain and Qwen"
   - **Public/Private**: 选择公开或私有
   - **不要勾选** "Initialize this repository with a README"
4. 点击 "Create repository"

#### 步骤 6：关联远程仓库并推送

```bash
# 添加远程仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/karpathy-kb.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

如果提示需要认证，使用以下方式之一：

**使用 HTTPS（推荐新手）：**
- 输入 GitHub 用户名
- 输入 GitHub 密码（或个人访问令牌）

**使用 SSH（推荐）：**
```bash
# 生成 SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# 查看公钥
cat ~/.ssh/id_ed25519.pub

# 复制公钥内容，添加到 GitHub：
# Settings → SSH and GPG keys → New SSH key
```

### 方法二：使用 GitHub Desktop（图形界面）

#### 步骤 1：下载 GitHub Desktop

- Windows: https://central.github.com/deployments/desktop/desktop/latest/win32
- Mac: https://central.github.com/deployments/desktop/desktop/latest/darwin

#### 步骤 2：添加项目

1. 打开 GitHub Desktop
2. 登录 GitHub 账号
3. File → Add Local Repository
4. 选择项目目录：`c:\Users\94795\Desktop\karpathy\karpathy-kb`
5. 点击 "Create a repository"

#### 步骤 3：提交更改

1. 在 Changes 标签页查看修改的文件
2. 输入提交信息：`Initial commit`
3. 点击 "Commit to main"

#### 步骤 4：推送到 GitHub

1. 点击 "Publish repository"
2. 填写仓库信息
3. 点击 "Publish"

### 方法三：使用 VS Code

#### 步骤 1：初始化 Git

1. 打开 VS Code
2. 打开项目文件夹
3. 点击左侧 Git 图标
4. 点击 "Initialize Repository"

#### 步骤 2：提交更改

1. 在 Source Control 标签页
2. 输入提交信息
3. 点击 "+" 添加所有文件
4. 点击 "✓" 提交

#### 步骤 3：推送到 GitHub

1. 点击 "Publish Branch"
2. 选择 "Publish to GitHub"
3. 选择公开或私有
4. 完成！

## 📝 后续操作

### 更新代码到 GitHub

```bash
# 修改代码后

# 1. 查看变更
git status

# 2. 添加变更
git add .

# 3. 提交
git commit -m "添加新功能：xxx"

# 4. 推送
git push origin main
```

### 从 GitHub 拉取更新

```bash
# 拉取远程更新
git pull origin main
```

### 查看提交历史

```bash
# 查看历史
git log

# 简洁查看
git log --oneline
```

### 撤销更改

```bash
# 撤销工作区修改
git checkout -- filename

# 撤销暂存区修改
git reset HEAD filename

# 撤销最后一次提交
git reset --soft HEAD~1
```

## 🔒 安全注意事项

### 1. 不要上传 API Key

**错误做法：**
```python
# config.py 中直接写 API Key
API_KEY = "sk-1382b5d2ef7b4cbb89158ed7ceaf438d"  # ❌
```

**正确做法：**

方法 A：使用环境变量
```python
# config.py
import os
API_KEY = os.getenv("DASHSCOPE_API_KEY")
```

```bash
# 设置环境变量
# Windows
set DASHSCOPE_API_KEY=your-api-key

# Linux/Mac
export DASHSCOPE_API_KEY=your-api-key
```

方法 B：使用 .env 文件（加入 .gitignore）
```python
# config.py
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("DASHSCOPE_API_KEY")
```

```bash
# .env 文件
DASHSCOPE_API_KEY=your-api-key
```

### 2. 检查已上传的文件

```bash
# 查看已跟踪的文件
git ls-files

# 查看历史中是否有敏感文件
git log --all --full-history -- "src/config.py"
```

### 3. 如果不小心上传了 API Key

```bash
# 1. 立即删除 API Key
# 2. 修改 .gitignore
# 3. 清除 Git 历史（谨慎操作）
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch src/config.py" \
  --prune-empty --tag-name-filter cat -- --all

# 4. 强制推送
git push origin --force --all
```

**更简单的方法：** 直接删除仓库重新创建

## 📊 GitHub Pages（可选）

如果想让项目有在线页面：

### 步骤 1：创建 docs 目录

```bash
mkdir docs
```

### 步骤 2：添加 index.html

```html
<!DOCTYPE html>
<html>
<head>
    <title>Karpathy Knowledge Base</title>
</head>
<body>
    <h1>Karpathy Knowledge Base</h1>
    <p>一个智能知识库系统</p>
    <a href="https://github.com/YOUR_USERNAME/karpathy-kb">View on GitHub</a>
</body>
</html>
```

### 步骤 3：启用 GitHub Pages

1. Settings → Pages
2. Source: Deploy from branch
3. Branch: main /docs folder
4. Save

## 🎯 最佳实践

### 1. 提交信息规范

```bash
# 好的提交信息
git commit -m "feat: 添加流式输出功能"
git commit -m "fix: 修复 token 统计错误"
git commit -m "docs: 更新 README 文档"
git commit -m "refactor: 重构 LLM 模块"

# 格式：type: description
# type: feat, fix, docs, style, refactor, test, chore
```

### 2. 分支管理

```bash
# 创建新分支
git checkout -b feature/new-feature

# 切换分支
git checkout main

# 合并分支
git merge feature/new-feature

# 删除分支
git branch -d feature/new-feature
```

### 3. 定期同步上游

```bash
# 如果有 fork 其他项目
git remote add upstream https://github.com/original/repo.git
git fetch upstream
git merge upstream/main
```

## ❓ 常见问题

### 1. push 失败：权限被拒绝

**解决：**
- 检查是否已添加 SSH key
- 或使用 HTTPS 并输入正确的用户名密码

### 2. 冲突如何解决

```bash
# 拉取时冲突
git pull origin main

# 手动编辑冲突文件
# 找到 <<<<<<< 和 >>>>>>> 标记
# 选择保留的代码

# 解决后提交
git add .
git commit -m "解决冲突"
```

### 3. 文件太大无法上传

```bash
# 查看大文件
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)'

# 使用 Git LFS
git lfs install
git lfs track "*.pdf"
```

### 4. 如何删除已上传的文件

```bash
# 从 Git 历史删除（不推荐）
git rm --cached filename
git commit -m "删除敏感文件"
git push origin main
```

## 📚 相关资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 帮助](https://help.github.com/)
- [Git 教程 - 廖雪峰](https://www.liaoxuefeng.com/wiki/896043488029600)
- [GitHub 入门](https://docs.github.com/en/get-started)

---

**祝你上传顺利！🎉**
