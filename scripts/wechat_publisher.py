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
        """添加微信公众号样式 - 简化版以符合20000字符限制"""
        styles = """<style>
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",Arial;font-size:16px;line-height:1.6;color:#333;margin:0;padding:20px}
h1{font-size:1.8em;font-weight:bold;color:#2c3e50;border-bottom:3px solid #3498db;padding-bottom:0.3em;margin:1.5em 0 1em 0}
h2{font-size:1.5em;font-weight:bold;color:#2c3e50;border-left:4px solid #3498db;padding-left:0.5em;margin:1.3em 0 0.8em 0}
h3{font-size:1.3em;font-weight:bold;color:#e74c3c;margin:1.2em 0 0.6em 0}
p{margin:1em 0;text-align:justify;line-height:1.8}
code{background-color:#f8f9fa;padding:2px 6px;border-radius:4px;color:#e74c3c;font-size:0.9em}
pre{background-color:#f8f9fa;padding:1.2em;border-radius:8px;overflow-x:auto;border-left:4px solid #3498db;margin:1.5em 0}
blockquote{border-left:4px solid #3498db;margin:1.5em 0;padding:0.5em 1.2em;background-color:#f8f9fa;font-style:italic;color:#666}
ul,ol{margin:1em 0;padding-left:2em}
li{margin:0.5em 0;line-height:1.6}
table{border-collapse:collapse;width:100%;margin:1.5em 0;font-size:0.9em}
th,td{border:1px solid #ddd;padding:10px 12px;text-align:left}
th{background-color:#3498db;color:white;font-weight:bold}
tr:nth-child(even){background-color:#f2f2f2}
img{max-width:100%;height:auto;border-radius:8px;margin:1em 0}
a{color:#3498db;text-decoration:none}
hr{border:none;height:1px;background-color:#ddd;margin:2em 0}
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