# GitHub Actions自动发布微信公众号完整方案

## 📁 仓库结构设计

```
your-blog-repo/
├── .github/
│   └── workflows/
│       └── publish-to-wechat.yml    # GitHub Actions工作流
├── articles/                        # 文章目录
│   ├── 2025/
│   │   ├── 01-first-article/
│   │   │   ├── index.md            # 文章内容
│   │   │   ├── thumb.jpg           # 缩略图
│   │   │   └── images/             # 文章图片
│   │   │       ├── image1.png
│   │   │       └── image2.jpg
│   │   └── 02-second-article/
│   │       ├── index.md
│   │       └── thumb.png
│   └── 2024/
│       └── ...
├── scripts/                         # 发布脚本
│   ├── wechat_publisher.py         # 微信发布核心脚本
│   ├── requirements.txt            # Python依赖
│   └── utils.py                    # 工具函数
├── config/
│   ├── published.json              # 已发布文章记录
│   └── settings.json               # 配置文件模板
├── README.md
└── .gitignore
```

## 🔧 核心配置文件

### 1. GitHub Actions工作流 (`.github/workflows/publish-to-wechat.yml`)

```yaml
name: Auto Publish to WeChat

on:
  push:
    branches: [ main ]
    paths: [ 'articles/**/*.md' ]
  workflow_dispatch:  # 手动触发
    inputs:
      force_publish:
        description: '强制发布所有文章'
        required: false
        default: 'false'
        type: boolean

jobs:
  detect-and-publish:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # 获取完整历史，用于检测变更
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r scripts/requirements.txt
    
    - name: Detect new or modified articles
      id: detect
      run: |
        python scripts/detect_changes.py
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Publish to WeChat
      if: steps.detect.outputs.has_changes == 'true'
      run: |
        python scripts/wechat_publisher.py
      env:
        WECHAT_APP_ID: ${{ secrets.WECHAT_APP_ID }}
        WECHAT_APP_SECRET: ${{ secrets.WECHAT_APP_SECRET }}
        AUTHOR_NAME: ${{ vars.AUTHOR_NAME }}
        SOURCE_URL: ${{ vars.SOURCE_URL }}
    
    - name: Update published record
      if: steps.detect.outputs.has_changes == 'true'
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add config/published.json
        git commit -m "Update published articles record [skip ci]" || exit 0
        git push
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Create summary
      run: |
        python scripts/create_summary.py >> $GITHUB_STEP_SUMMARY
```

## 📝 核心Python脚本

### 2. 变更检测脚本 (`scripts/detect_changes.py`)

```python
#!/usr/bin/env python3
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

def get_git_changes():
    """获取Git变更的文件列表"""
    # 获取最近一次提交的变更
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        # 如果是第一次提交，获取所有文件
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True, text=True
        )
    
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def load_published_record():
    """加载已发布记录"""
    published_file = Path('config/published.json')
    if published_file.exists():
        with open(published_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_published_record(record):
    """保存已发布记录"""
    published_file = Path('config/published.json')
    published_file.parent.mkdir(exist_ok=True)
    
    with open(published_file, 'w', encoding='utf-8') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

def get_article_info(md_file):
    """获取文章信息"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取元数据
    import re
    
    # 提取标题
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else Path(md_file).stem
    
    # 获取文件修改时间
    mtime = os.path.getmtime(md_file)
    
    return {
        'title': title,
        'file_path': str(md_file),
        'modified_time': mtime,
        'content_hash': hash(content)
    }

def main():
    # 强制发布模式
    force_publish = os.getenv('INPUT_FORCE_PUBLISH', 'false').lower() == 'true'
    
    # 获取变更文件
    changed_files = get_git_changes()
    
    # 过滤出markdown文件
    md_files = [f for f in changed_files if f.endswith('.md') and f.startswith('articles/')]
    
    if force_publish:
        # 强制模式：获取所有文章
        md_files = list(Path('articles').rglob('*.md'))
        md_files = [str(f) for f in md_files]
    
    # 加载已发布记录
    published_record = load_published_record()
    
    # 检测需要发布的文章
    to_publish = []
    
    for md_file in md_files:
        if not Path(md_file).exists():
            continue
            
        article_info = get_article_info(md_file)
        file_key = str(Path(md_file).relative_to('articles'))
        
        # 检查是否需要发布
        should_publish = False
        
        if force_publish:
            should_publish = True
        elif file_key not in published_record:
            should_publish = True
        elif published_record[file_key]['content_hash'] != article_info['content_hash']:
            should_publish = True
        
        if should_publish:
            to_publish.append(article_info)
    
    # 输出结果
    if to_publish:
        print(f"发现 {len(to_publish)} 篇需要发布的文章:")
        for article in to_publish:
            print(f"  - {article['title']} ({article['file_path']})")
        
        # 保存待发布列表
        with open('to_publish.json', 'w', encoding='utf-8') as f:
            json.dump(to_publish, f, indent=2, ensure_ascii=False)
        
        # 设置GitHub Actions输出
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write('has_changes=true\n')
    else:
        print("没有发现需要发布的文章")
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write('has_changes=false\n')

if __name__ == "__main__":
    main()
```

### 3. 微信发布脚本 (`scripts/wechat_publisher.py`)

```python
#!/usr/bin/env python3
import os
import json
import requests
import markdown
import re
import time
from pathlib import Path
from datetime import datetime

class WeChatPublisher:
    def __init__(self):
        self.app_id = os.getenv('WECHAT_APP_ID')
        self.app_secret = os.getenv('WECHAT_APP_SECRET')
        self.author = os.getenv('AUTHOR_NAME', '')
        self.source_url = os.getenv('SOURCE_URL', '')
        self.access_token = None
        self.access_token_expires = 0
        
        if not self.app_id or not self.app_secret:
            raise ValueError("未设置微信公众号配置")
    
    def get_access_token(self):
        """获取access_token"""
        if self.access_token and time.time() < self.access_token_expires:
            return self.access_token
            
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        response = requests.get(url)
        result = response.json()
        
        if 'access_token' in result:
            self.access_token = result['access_token']
            self.access_token_expires = time.time() + result['expires_in'] - 600
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {result}")
    
    def upload_image(self, image_path):
        """上传图片到微信服务器"""
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"
        
        with open(image_path, 'rb') as f:
            files = {'media': (os.path.basename(image_path), f, 'image/jpeg')}
            response = requests.post(url, files=files)
            result = response.json()
            
        if result.get('errcode') == 0:
            return result['url']
        else:
            raise Exception(f"图片上传失败: {result}")
    
    def upload_thumb_media(self, image_path):
        """上传缩略图素材"""
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=thumb"
        
        with open(image_path, 'rb') as f:
            files = {'media': (os.path.basename(image_path), f, 'image/jpeg')}
            response = requests.post(url, files=files)
            result = response.json()
            
        if result.get('errcode') == 0:
            return result['media_id']
        else:
            raise Exception(f"缩略图上传失败: {result}")
    
    def process_markdown_content(self, markdown_content, article_dir):
        """处理Markdown内容，上传图片并转换HTML"""
        
        def replace_images(match):
            img_alt = match.group(1)
            img_path = match.group(2)
            
            # 处理相对路径
            if not img_path.startswith(('http://', 'https://')):
                full_path = Path(article_dir) / img_path
                if full_path.exists():
                    try:
                        wx_url = self.upload_image(str(full_path))
                        return f'<img src="{wx_url}" alt="{img_alt}" style="width: 100%; height: auto;">'
                    except Exception as e:
                        print(f"⚠️  图片上传失败 {img_path}: {e}")
                        return f'<p>[图片上传失败: {img_alt}]</p>'
            
            return f'<img src="{img_path}" alt="{img_alt}" style="width: 100%; height: auto;">'
        
        # 替换图片
        markdown_content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_images, markdown_content)
        
        # 转换为HTML
        html = markdown.markdown(
            markdown_content,
            extensions=['codehilite', 'tables', 'toc', 'fenced_code'],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True
                }
            }
        )
        
        return self.add_wechat_styles(html)
    
    def add_wechat_styles(self, html):
        """添加微信公众号样式"""
        styles = """
        <style>
        /* 基础样式 */
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif; 
            font-size: 16px; 
            line-height: 1.6; 
            color: #333; 
            margin: 0; 
            padding: 20px;
        }
        
        /* 标题样式 */
        h1 { 
            font-size: 1.8em; 
            font-weight: bold; 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            padding-bottom: 0.3em; 
            margin: 1.5em 0 1em 0;
        }
        
        h2 { 
            font-size: 1.5em; 
            font-weight: bold; 
            color: #2c3e50; 
            border-left: 4px solid #3498db; 
            padding-left: 0.5em; 
            margin: 1.3em 0 0.8em 0;
        }
        
        h3 { 
            font-size: 1.3em; 
            font-weight: bold; 
            color: #e74c3c; 
            margin: 1.2em 0 0.6em 0;
        }
        
        /* 段落样式 */
        p { 
            margin: 1em 0; 
            text-align: justify; 
            line-height: 1.8;
        }
        
        /* 代码样式 */
        code { 
            background-color: #f8f9fa; 
            padding: 2px 6px; 
            border-radius: 4px; 
            font-family: 'Fira Code', Consolas, Monaco, monospace; 
            color: #e74c3c; 
            font-size: 0.9em;
        }
        
        pre { 
            background-color: #f8f9fa; 
            padding: 1.2em; 
            border-radius: 8px; 
            overflow-x: auto; 
            border-left: 4px solid #3498db; 
            margin: 1.5em 0;
            line-height: 1.4;
        }
        
        pre code { 
            background-color: transparent; 
            padding: 0; 
            color: #333; 
            font-size: 0.9em;
        }
        
        /* 引用样式 */
        blockquote { 
            border-left: 4px solid #3498db; 
            margin: 1.5em 0; 
            padding: 0.5em 1.2em; 
            background-color: #f8f9fa; 
            font-style: italic; 
            color: #666;
        }
        
        /* 列表样式 */
        ul, ol { 
            margin: 1em 0; 
            padding-left: 2em; 
        }
        
        li { 
            margin: 0.5em 0; 
            line-height: 1.6;
        }
        
        /* 表格样式 */
        table { 
            border-collapse: collapse; 
            width: 100%; 
            margin: 1.5em 0; 
            font-size: 0.9em;
        }
        
        th, td { 
            border: 1px solid #ddd; 
            padding: 10px 12px; 
            text-align: left; 
        }
        
        th { 
            background-color: #3498db; 
            color: white; 
            font-weight: bold; 
        }
        
        tr:nth-child(even) { 
            background-color: #f2f2f2; 
        }
        
        /* 图片样式 */
        img { 
            max-width: 100%; 
            height: auto; 
            border-radius: 8px; 
            margin: 1em 0; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* 链接样式 */
        a { 
            color: #3498db; 
            text-decoration: none; 
        }
        
        a:hover { 
            text-decoration: underline; 
        }
        
        /* 分割线 */
        hr { 
            border: none; 
            height: 1px; 
            background-color: #ddd; 
            margin: 2em 0; 
        }
        </style>
        """
        
        return styles + html
    
    def create_draft(self, title, content, author, digest, thumb_media_id, source_url):
        """创建草稿"""
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        
        data = {
            "articles": [{
                "title": title,
                "author": author,
                "digest": digest,
                "content": content,
                "content_source_url": source_url,
                "thumb_media_id": thumb_media_id,
                "need_open_comment": 1,
                "only_fans_can_comment": 0
            }]
        }
        
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('errcode') == 0:
            return result['media_id']
        else:
            raise Exception(f"创建草稿失败: {result}")
    
    def publish_draft(self, media_id):
        """发布草稿"""
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
        
        data = {"media_id": media_id}
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('errcode') == 0:
            return result.get('publish_id')
        else:
            raise Exception(f"发布失败: {result}")
    
    def publish_article(self, article_info):
        """发布单篇文章"""
        file_path = Path(article_info['file_path'])
        article_dir = file_path.parent
        
        # 读取文章内容
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 处理内容
        html_content = self.process_markdown_content(markdown_content, article_dir)
        
        # 生成摘要
        content_text = re.sub(r'[#*`\[\]()]', '', markdown_content)
        digest = content_text[:100].strip() + "..." if len(content_text) > 100 else content_text
        
        # 查找缩略图
        thumb_media_id = ""
        for thumb_name in ['thumb.jpg', 'thumb.jpeg', 'thumb.png', 'cover.jpg', 'cover.png']:
            thumb_path = article_dir / thumb_name
            if thumb_path.exists():
                thumb_media_id = self.upload_thumb_media(str(thumb_path))
                break
        
        # 创建草稿
        media_id = self.create_draft(
            title=article_info['title'],
            content=html_content,
            author=self.author,
            digest=digest,
            thumb_media_id=thumb_media_id,
            source_url=self.source_url
        )
        
        # 发布草稿
        publish_id = self.publish_draft(media_id)
        
        return {
            'media_id': media_id,
            'publish_id': publish_id,
            'published_time': datetime.now().isoformat()
        }

def main():
    """主函数"""
    # 检查是否有待发布文章
    to_publish_file = Path('to_publish.json')
    if not to_publish_file.exists():
        print("没有找到待发布文章列表")
        return
    
    with open(to_publish_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    if not articles:
        print("没有需要发布的文章")
        return
    
    # 初始化发布器
    publisher = WeChatPublisher()
    
    # 加载已发布记录
    published_record_file = Path('config/published.json')
    if published_record_file.exists():
        with open(published_record_file, 'r', encoding='utf-8') as f:
            published_record = json.load(f)
    else:
        published_record = {}
    
    # 发布文章
    success_count = 0
    for article in articles:
        try:
            print(f"\n📝 正在发布: {article['title']}")
            
            result = publisher.publish_article(article)
            
            # 更新发布记录
            file_key = str(Path(article['file_path']).relative_to('articles'))
            published_record[file_key] = {
                'title': article['title'],
                'content_hash': article['content_hash'],
                'published_time': result['published_time'],
                'media_id': result['media_id'],
                'publish_id': result['publish_id']
            }
            
            print(f"✅ 发布成功！publish_id: {result['publish_id']}")
            success_count += 1
            
            # 避免频率限制
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ 发布失败: {e}")
            continue
    
    # 保存发布记录
    published_record_file.parent.mkdir(exist_ok=True)
    with open(published_record_file, 'w', encoding='utf-8') as f:
        json.dump(published_record, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 发布完成！成功发布 {success_count}/{len(articles)} 篇文章")

if __name__ == "__main__":
    main()
```

### 4. 依赖文件 (`scripts/requirements.txt`)

```
requests>=2.31.0
markdown>=3.5.1
pygments>=2.16.1
```

### 5. 摘要生成脚本 (`scripts/create_summary.py`)

```python
#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

def main():
    """生成GitHub Actions摘要"""
    
    # 读取发布记录
    published_file = Path('config/published.json')
    if not published_file.exists():
        print("## 📋 发布摘要\n\n没有发布记录")
        return
    
    with open(published_file, 'r', encoding='utf-8') as f:
        published_record = json.load(f)
    
    # 读取本次发布的文章
    to_publish_file = Path('to_publish.json')
    if to_publish_file.exists():
        with open(to_publish_file, 'r', encoding='utf-8') as f:
            published_articles = json.load(f)
        
        print("## 📋 本次发布摘要\n")
        print(f"**发布时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"**发布数量**: {len(published_articles)} 篇\n")
        print("### 📄 发布文章列表\n")
        
        for article in published_articles:
            print(f"- ✅ **{article['title']}**")
            print(f"  - 文件: `{article['file_path']}`")
            print("")
    
    # 统计信息
    total_articles = len(published_record)
    print(f"\n### 📊 统计信息\n")
    print(f"- 总发布文章数: **{total_articles}** 篇")
    print(f"- 最近更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
```

## 🔐 安全配置

### GitHub Secrets 设置

在仓库的 Settings → Secrets and variables → Actions 中添加：

**Secrets**:
- `WECHAT_APP_ID`: 微信公众号AppID
- `WECHAT_APP_SECRET`: 微信公众号AppSecret

**Variables**:
- `AUTHOR_NAME`: 作者名称
- `SOURCE_URL`: 原文链接域名

## 🚀 使用方法

### 1. 创建仓库并设置配置

```bash
# 克隆或创建新仓库
git clone your-repo-url
cd your-repo

# 创建目录结构
mkdir -p .github/workflows scripts config articles/2025/01-first-article/images

# 复制上述文件到对应位置
```

### 2. 配置微信公众号

- 获取AppID和AppSecret
- 在GitHub仓库设置中添加Secrets

### 3. 编写第一篇文章

```bash
# 创建文章目录
mkdir articles/2025/01-hello-world

# 创建文章文件
cat > articles/2025/01-hello-world/index.md << 'EOF'
# Hello World

这是我的第一篇自动发布的文章！

## 特性

- ✅ 自动检测新文章
- ✅ 自动上传图片
- ✅ 自动发布到微信公众号
- ✅ 支持Markdown语法

![示例图片](./images/example.png)

## 代码示例

```python
def hello_world():
    print("Hello, WeChat!")
```

很棒吧！
EOF

# 添加缩略图
cp your-thumb-image.jpg articles/2025/01-hello-world/thumb.jpg
```

### 4. 提交并触发发布

```bash
git add .
git commit -m "添加第一篇文章"
git push origin main
```

## 🎯 高级功能

### 手动触发发布

在GitHub仓库的Actions页面，可以手动运行工作流，支持强制发布所有文章。

### 定时发布

可以添加cron触发器定时检查：

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

### 文章元数据支持

在markdown文件头部支持YAML frontmatter：

```markdown
---
title: "自定义标题"
author: "特定作者"
date: "2025-01-25"
tags: ["技术", "教程"]
---

# 文章内容
```

这个方案实现了完全自动化的发布流程，你只需要专注于写作，其他的交给GitHub Actions处理！
