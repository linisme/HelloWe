# GitHub Actions 自动发布微信公众号 🚀

[![Auto Publish to WeChat](https://github.com/yourusername/your-repo/workflows/Auto%20Publish%20to%20WeChat/badge.svg)](https://github.com/yourusername/your-repo/actions)

一个完全自动化的微信公众号发布解决方案，支持 Markdown 文章自动发布到微信公众号。

## ✨ 特性

- 🔄 **自动化发布** - 提交文章自动发布到微信公众号
- 📝 **Markdown支持** - 完整的Markdown语法支持
- 🖼️ **图片自动上传** - 本地图片自动上传到微信服务器
- 🎨 **美观样式** - 专为微信公众号优化的样式
- 📊 **发布记录** - 自动跟踪已发布文章，避免重复发布
- 🔍 **智能检测** - 仅发布新增或修改的文章
- 📈 **发布摘要** - GitHub Actions 中显示详细发布报告

## 📁 项目结构

```
HelloWe/
├── .github/
│   └── workflows/
│       └── publish-to-wechat.yml    # GitHub Actions工作流
├── articles/                        # 文章目录
│   └── 2025/
│       └── 01-hello-world/
│           ├── index.md            # 文章内容
│           ├── thumb.jpg           # 缩略图(可选)
│           └── images/             # 文章图片
├── scripts/                         # 发布脚本
│   ├── detect_changes.py           # 变更检测脚本
│   ├── wechat_publisher.py         # 微信发布核心脚本
│   └── create_summary.py           # 摘要生成脚本
├── pyproject.toml                   # UV项目配置文件
├── config/
│   ├── published.json              # 已发布文章记录
│   └── settings.json               # 配置文件模板
└── README.md
```

## 🚀 快速开始

### 1. 环境准备

确保已安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 克隆项目

```bash
git clone https://github.com/yourusername/HelloWe.git
cd HelloWe
```

### 3. 安装依赖

```bash
uv sync
```

### 4. 配置微信公众号

1. 登录微信公众平台，获取 `AppID` 和 `AppSecret`
2. 在 GitHub 仓库的 Settings → Secrets and variables → Actions 中添加：

**Secrets:**
- `WECHAT_APP_ID`: 你的微信公众号AppID
- `WECHAT_APP_SECRET`: 你的微信公众号AppSecret

**Variables:**
- `AUTHOR_NAME`: 作者名称
- `SOURCE_URL`: 原文链接域名

### 5. 创建第一篇文章

```bash
# 创建文章目录
mkdir -p articles/2025/01-my-first-article/images

# 创建文章
cat > articles/2025/01-my-first-article/index.md << 'EOF'
# 我的第一篇文章

这是一篇测试文章！

## 功能特点

- ✅ 支持Markdown语法
- ✅ 自动发布到微信公众号
- ✅ 图片自动上传

![示例图片](./images/example.png)

很棒吧！
EOF

# 添加缩略图（可选）
cp your-image.jpg articles/2025/01-my-first-article/thumb.jpg
```

### 6. 提交并自动发布

```bash
git add .
git commit -m "添加第一篇文章"
git push origin main
```

文章将自动发布到你的微信公众号！

## 🛠️ 本地开发

### 使用 uv 运行脚本

```bash
# 检测文章变更
uv run python scripts/detect_changes.py

# 发布文章到微信
uv run python scripts/wechat_publisher.py

# 生成发布摘要
uv run python scripts/create_summary.py
```

### 添加新依赖

```bash
# 添加生产依赖
uv add requests

# 添加开发依赖
uv add --dev pytest
```

## 📖 使用说明

### 文章格式

- 文章必须放在 `articles/` 目录下
- 文件名必须是 `index.md`
- 支持标准 Markdown 语法
- 图片使用相对路径引用

### 缩略图

支持以下文件名作为缩略图：
- `thumb.jpg`
- `thumb.jpeg` 
- `thumb.png`
- `cover.jpg`
- `cover.png`

### 目录结构建议

```
articles/
├── 2025/
│   ├── 01-article-name/
│   │   ├── index.md
│   │   ├── thumb.jpg
│   │   └── images/
│   │       └── image1.png
│   └── 02-another-article/
│       └── index.md
└── 2024/
    └── ...
```

## 🔧 高级功能

### 手动触发发布

在 GitHub 仓库的 Actions 页面，可以手动运行工作流：
- 选择 "Auto Publish to WeChat" 工作流
- 点击 "Run workflow"
- 可选择"强制发布所有文章"

### 定时发布

可以在工作流中添加定时触发：

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # 每天上午9点检查
```

### 多环境支持

可以设置不同分支对应不同环境：

```yaml
on:
  push:
    branches: [ main, staging ]
```

## 🛠️ 故障排除

### 常见问题

1. **发布失败** - 检查微信公众号配置和网络连接
2. **图片上传失败** - 确保图片格式正确且大小不超过限制
3. **权限问题** - 确保 GitHub Secrets 配置正确

### 调试方法

查看 GitHub Actions 日志了解详细错误信息：
1. 进入仓库的 Actions 页面
2. 点击失败的工作流运行
3. 查看各步骤的日志输出

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请提交 Issue 或联系作者。

---

⭐ 如果这个项目对你有帮助，请给个星标支持一下！