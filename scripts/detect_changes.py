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