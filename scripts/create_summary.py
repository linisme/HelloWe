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