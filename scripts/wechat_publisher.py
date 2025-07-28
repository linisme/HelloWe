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
            
        # 成功时没有errcode字段，失败时有errcode字段
        if 'errcode' not in result and 'url' in result:
            return result['url']
        else:
            raise Exception(f"图片上传失败: {result}")
    
    def upload_thumb_media(self, image_path):
        """上传缩略图素材"""
        print(f"🔍 开始上传缩略图: {image_path}")
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=thumb"
        print(f"🔍 上传URL: {url}")
        
        with open(image_path, 'rb') as f:
            files = {'media': (os.path.basename(image_path), f, 'image/jpeg')}
            print(f"🔍 文件信息: {os.path.basename(image_path)}, 大小: {os.path.getsize(image_path)} bytes")
            response = requests.post(url, files=files)
            result = response.json()
            print(f"🔍 上传响应: {result}")
            
        # 成功时没有errcode字段，失败时有errcode字段
        if 'errcode' not in result and 'media_id' in result:
            media_id = result['media_id']
            print(f"✅ 缩略图上传成功，media_id: {media_id}")
            return media_id
        else:
            print(f"❌ 缩略图上传失败: {result}")
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
                        return f'<div class="img-container"><img src="{wx_url}" alt="{img_alt}"><div class="img-caption">{img_alt}</div></div>'
                    except Exception as e:
                        print(f"⚠️  图片上传失败 {img_path}: {e}")
                        return f'<p>[图片上传失败: {img_alt}]</p>'
            
            return f'<div class="img-container"><img src="{img_path}" alt="{img_alt}"><div class="img-caption">{img_alt}</div></div>'
        
        # 预处理：添加特殊标记
        # 将 **文本** 转换为带高亮的strong标签
        markdown_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', markdown_content)
        
        # 将重要提示转换为特殊样式
        markdown_content = re.sub(r'(?:^|\n)> (.*?)(?=\n|$)', r'\n<blockquote>\1</blockquote>\n', markdown_content, flags=re.MULTILINE)
        
        # 替换图片
        markdown_content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_images, markdown_content)
        
        # 添加章节分隔符
        markdown_content = re.sub(r'\n---\n', '<div class="section-divider"><span>◆ ◆ ◆</span></div>', markdown_content)
        
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
        
        # 后处理：优化HTML结构
        # 包装内容
        html = f'<div class="content">{html}</div>'
        
        # 为表格添加容器
        html = re.sub(r'<table>', '<div class="table-container"><table>', html)
        html = re.sub(r'</table>', '</table></div>', html)
        
        return self.add_wechat_styles(html)
    
    def add_wechat_styles(self, html):
        """添加微信公众号样式 - 现代化设计版本"""
        styles = """<style>
/* 基础样式 */
body {
    font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Segoe UI", Roboto, Arial, sans-serif;
    font-size: 17px;
    line-height: 1.75;
    color: #2c3e50;
    margin: 0;
    padding: 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed;
}

.content {
    max-width: 100%;
    margin: 0 auto;
    background: #ffffff;
    border-radius: 16px;
    padding: 32px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    position: relative;
}

.content::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #f5576c);
    border-radius: 16px 16px 0 0;
}

/* 标题样式 */
h1 {
    font-size: 2.2em;
    font-weight: 800;
    color: #2c3e50;
    text-align: center;
    margin: 2em 0 1.5em;
    padding: 20px 0;
    position: relative;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

h1::after {
    content: "";
    position: absolute;
    bottom: -10px;
    left: 50%;
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 2px;
    transform: translateX(-50%);
}

h2 {
    font-size: 1.6em;
    font-weight: 700;
    color: #34495e;
    margin: 2.5em 0 1.2em;
    padding: 16px 24px;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    border-left: 5px solid #667eea;
    border-radius: 0 12px 12px 0;
    position: relative;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

h2::before {
    content: "✦";
    color: #667eea;
    font-size: 1.2em;
    margin-right: 8px;
}

h3 {
    font-size: 1.3em;
    font-weight: 600;
    color: #e74c3c;
    margin: 2em 0 1em;
    padding: 8px 16px;
    border-left: 3px solid #e74c3c;
    background: linear-gradient(90deg, #fef5f5 0%, transparent 100%);
    border-radius: 0 8px 8px 0;
}

/* 段落和文本样式 */
p {
    margin: 1.5em 0;
    text-align: justify;
    line-height: 1.8;
    font-size: 17px;
    color: #34495e;
    text-indent: 0;
}

strong {
    color: #2c3e50;
    font-weight: 700;
    background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
    padding: 3px 8px;
    border-radius: 6px;
    box-shadow: 0 2px 4px rgba(132, 250, 176, 0.3);
}

em {
    color: #e74c3c;
    font-style: normal;
    font-weight: 600;
    background: linear-gradient(120deg, #ffeaa7 0%, #fab1a0 100%);
    padding: 2px 6px;
    border-radius: 4px;
}

/* 代码样式 */
code {
    background: #f8fafc;
    padding: 4px 8px;
    border-radius: 6px;
    color: #e91e63;
    font-size: 0.9em;
    border: 1px solid #e2e8f0;
    font-family: "Fira Code", "JetBrains Mono", Consolas, monospace;
}

pre {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 24px;
    border-radius: 12px;
    overflow-x: auto;
    margin: 2em 0;
    position: relative;
    color: #ffffff;
    font-family: "Fira Code", "JetBrains Mono", Consolas, monospace;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

pre::before {
    content: "{ code }";
    position: absolute;
    top: 12px;
    right: 16px;
    color: rgba(255, 255, 255, 0.7);
    font-size: 12px;
    font-weight: 500;
}

pre code {
    background: transparent;
    border: none;
    color: inherit;
    padding: 0;
}

/* 引用样式 */
blockquote {
    border-left: 5px solid #667eea;
    margin: 2em 0;
    padding: 20px 24px;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    border-radius: 0 12px 12px 0;
    position: relative;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
}

blockquote::before {
    content: "💫";
    position: absolute;
    top: 16px;
    left: -16px;
    background: #ffffff;
    padding: 8px;
    border-radius: 50%;
    font-size: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 列表样式 */
ul, ol {
    margin: 1.5em 0;
    padding-left: 0;
    list-style: none;
}

ul li {
    position: relative;
    margin: 1em 0;
    padding-left: 2em;
    line-height: 1.7;
}

ul li::before {
    content: "▸";
    color: #667eea;
    font-weight: bold;
    font-size: 1.2em;
    position: absolute;
    left: 0;
    top: 0;
}

ol {
    counter-reset: item;
}

ol li {
    position: relative;
    margin: 1em 0;
    padding-left: 2.5em;
    line-height: 1.7;
    counter-increment: item;
}

ol li::before {
    content: counter(item);
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #ffffff;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    left: 0;
    top: 0;
    font-size: 13px;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* 图片样式 */
img {
    max-width: 100%;
    height: auto;
    border-radius: 16px;
    margin: 2em auto;
    display: block;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.img-container {
    text-align: center;
    margin: 2.5em 0;
    padding: 16px;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.img-caption {
    text-align: center;
    color: #64748b;
    font-size: 15px;
    margin-top: 12px;
    font-style: italic;
    padding: 8px 16px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 8px;
    display: inline-block;
}

/* 表格样式 */
.table-container {
    overflow-x: auto;
    margin: 2em 0;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    background: #ffffff;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 0;
    font-size: 0.95em;
    background: #ffffff;
}

th, td {
    border: 1px solid #e2e8f0;
    padding: 16px 20px;
    text-align: left;
}

th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #ffffff;
    font-weight: 700;
    border-bottom: 2px solid #5a67d8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.9em;
}

tr:nth-child(even) {
    background: #f8fafc;
}

tr:hover {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

/* 链接样式 */
a {
    color: #667eea;
    text-decoration: none;
    border-bottom: 2px solid transparent;
    transition: all 0.3s ease;
    font-weight: 500;
}

a:hover {
    border-bottom-color: #667eea;
    transform: translateY(-1px);
}

/* 分隔线样式 */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #667eea, transparent);
    margin: 3em 0;
    border-radius: 1px;
}

/* 高亮样式 */
.highlight {
    background: linear-gradient(120deg, #fff9c4 0%, #fff59d 100%);
    padding: 3px 8px;
    border-radius: 6px;
    color: #7c3aed;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(255, 245, 157, 0.4);
}

/* 章节分隔符 */
.section-divider {
    text-align: center;
    margin: 3em 0;
    position: relative;
}

.section-divider::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #667eea, transparent);
}

.section-divider span {
    background: #ffffff;
    padding: 0 24px;
    color: #667eea;
    font-size: 16px;
    font-weight: 600;
    position: relative;
    z-index: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
    body { padding: 16px; }
    .content { padding: 24px 20px; }
    h1 { font-size: 1.8em; }
    h2 { font-size: 1.4em; padding: 12px 16px; }
    h3 { font-size: 1.2em; }
    p { font-size: 16px; }
}
</style>"""
        
        return styles + html
    
    def create_draft(self, title, content, author, digest, thumb_media_id, source_url):
        """创建草稿"""
        print(f"🔍 创建草稿 - 标题: {title}")
        print(f"🔍 传入的thumb_media_id: '{thumb_media_id}', 类型: {type(thumb_media_id)}, 长度: {len(thumb_media_id) if thumb_media_id else 0}")
        
        # 调试各字段长度
        print(f"🔍 各字段长度检查:")
        print(f"   - title长度: {len(title)} 字符")
        print(f"   - author长度: {len(author)} 字符")  
        print(f"   - digest长度: {len(digest)} 字符")
        print(f"   - content长度: {len(content)} 字符")
        print(f"   - source_url长度: {len(source_url)} 字符")
        
        # 检查content长度是否超过微信API限制
        if len(content) > 20000:
            print(f"⚠️  content内容过长({len(content)}字符)，将被截断至20000字符")
            content = content[:20000]
        
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        
        article_data = {
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": source_url,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }
        
        # thumb_media_id 是必填字段，必须传递有效值
        if not thumb_media_id or not thumb_media_id.strip():
            raise Exception("缩略图 media_id 不能为空，这是微信草稿API的必填字段")
        
        print(f"✅ 添加缩略图到草稿: {thumb_media_id}")
        article_data["thumb_media_id"] = thumb_media_id
        
        data = {"articles": [article_data]}
        print(f"🔍 发送到微信API的数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 明确设置编码以避免中文乱码
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        response = requests.post(url, data=json_data, headers=headers)
        result = response.json()
        print(f"🔍 微信API响应: {result}")
        
        # 成功时没有errcode字段，失败时有errcode字段
        if 'errcode' not in result and 'media_id' in result:
            print(f"✅ 草稿创建成功，media_id: {result['media_id']}")
            return result['media_id']
        else:
            print(f"❌ 草稿创建失败: {result}")
            raise Exception(f"创建草稿失败: {result}")
    
    def publish_draft(self, media_id):
        """发布草稿"""
        access_token = self.get_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
        
        data = {"media_id": media_id}
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        response = requests.post(url, data=json_data, headers=headers)
        result = response.json()
        
        # 成功时没有errcode字段，失败时有errcode字段
        if 'errcode' not in result and 'publish_id' in result:
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
        
        # 生成摘要 - 微信公众号digest字段严格限制
        content_text = re.sub(r'[#*`\[\]()-]', '', markdown_content)
        content_text = re.sub(r'\n+', ' ', content_text)  # 将换行替换为空格
        content_text = re.sub(r'\s+', ' ', content_text)  # 多个空格合并为一个
        content_text = content_text.strip()
        # 严格限制在24个字符以内，为微信API digest字段预留安全边距
        if len(content_text) > 24:
            digest = content_text[:24]
        else:
            digest = content_text
        
        # 查找缩略图
        thumb_media_id = ""
        print(f"🔍 开始查找缩略图，目录: {article_dir}")
        
        for thumb_name in ['thumb.jpg', 'thumb.jpeg', 'thumb.png', 'cover.jpg', 'cover.png']:
            thumb_path = article_dir / thumb_name
            print(f"🔍 检查缩略图文件: {thumb_path}")
            if thumb_path.exists():
                print(f"📁 找到缩略图文件: {thumb_name}")
                try:
                    thumb_media_id = self.upload_thumb_media(str(thumb_path))
                    print(f"✅ 缩略图上传成功: {thumb_name}, media_id: {thumb_media_id}")
                    break
                except Exception as e:
                    print(f"⚠️  缩略图上传失败 {thumb_name}: {e}")
                    thumb_media_id = ""  # 确保失败时重置为空字符串
                    continue
        
        print(f"🔍 最终缩略图状态 - thumb_media_id: '{thumb_media_id}', 类型: {type(thumb_media_id)}, 布尔值: {bool(thumb_media_id)}")
        
        if not thumb_media_id:
            print("⚠️  未找到缩略图或上传失败，尝试使用默认缩略图")
            default_thumb_path = Path(__file__).parent.parent / 'config' / 'default_thumb.jpg'
            if default_thumb_path.exists():
                try:
                    thumb_media_id = self.upload_thumb_media(str(default_thumb_path))
                    print(f"✅ 默认缩略图上传成功，media_id: {thumb_media_id}")
                except Exception as e:
                    print(f"❌ 默认缩略图上传失败: {e}")
                    raise Exception(f"无法获取有效的缩略图 media_id，草稿创建需要缩略图: {e}")
            else:
                raise Exception(f"默认缩略图文件不存在: {default_thumb_path}")
        
        # 创建草稿
        media_id = self.create_draft(
            title=article_info['title'],
            content=html_content,
            author=self.author,
            digest=digest,
            thumb_media_id=thumb_media_id,
            source_url=self.source_url
        )
        
        # 尝试发布草稿（可能因权限限制失败）
        try:
            publish_id = self.publish_draft(media_id)
            print(f"✅ 草稿发布成功！publish_id: {publish_id}")
            return {
                'media_id': media_id,
                'publish_id': publish_id,
                'published_time': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️  自动发布失败: {e}")
            print(f"✅ 草稿已创建成功 (media_id: {media_id})，请手动在微信公众平台后台发布")
            return {
                'media_id': media_id,
                'publish_id': None,
                'published_time': datetime.now().isoformat(),
                'status': 'draft_created_manual_publish_required'
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