#!/usr/bin/env python3
"""
生成开发者日报相关的图片
"""

from PIL import Image, ImageDraw, ImageFont
import os
import random
import colorsys

def generate_gradient_background(width, height, start_color, end_color):
    """生成渐变背景"""
    base = Image.new('RGB', (width, height), start_color)
    top = Image.new('RGB', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(255 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def get_random_tech_color():
    """获取随机的科技感颜色"""
    colors = [
        (46, 204, 113),   # 绿色
        (52, 152, 219),   # 蓝色
        (155, 89, 182),   # 紫色
        (230, 126, 34),   # 橙色
        (241, 196, 15),   # 黄色
        (231, 76, 60),    # 红色
        (26, 188, 156),   # 青色
        (142, 68, 173),   # 深紫色
    ]
    return random.choice(colors)

def create_tech_trend_chart(output_path):
    """创建技术趋势图表"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (15, 23, 42))
    draw = ImageDraw.Draw(img)
    
    # 绘制标题
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 36)
        label_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 16)
    except:
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
    
    draw.text((50, 30), "2025 技术趋势分析", fill=(255, 255, 255), font=title_font)
    
    # 绘制图表数据
    technologies = ["AI/ML", "Web3", "Cloud", "Mobile", "DevOps", "Security"]
    values = [85, 72, 68, 55, 63, 78]
    colors = [(46, 204, 113), (52, 152, 219), (155, 89, 182), 
              (230, 126, 34), (241, 196, 15), (231, 76, 60)]
    
    bar_width = 80
    bar_spacing = 100
    start_x = 100
    start_y = 500
    
    for i, (tech, value, color) in enumerate(zip(technologies, values, colors)):
        x = start_x + i * bar_spacing
        bar_height = value * 3
        
        # 绘制柱状图
        draw.rectangle([x, start_y - bar_height, x + bar_width, start_y], fill=color)
        
        # 绘制标签
        draw.text((x + 10, start_y + 10), tech, fill=(255, 255, 255), font=label_font)
        draw.text((x + 20, start_y - bar_height - 25), f"{value}%", fill=(255, 255, 255), font=label_font)
    
    img.save(output_path)

def create_ai_development_roadmap(output_path):
    """创建AI发展路线图"""
    width, height = 800, 600
    base_color = (20, 30, 48)
    accent_color = (64, 224, 208)
    
    img = generate_gradient_background(width, height, base_color, (30, 40, 60))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 32)
        text_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 14)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    draw.text((50, 30), "AI 发展路线图 2025", fill=(255, 255, 255), font=title_font)
    
    # 绘制时间线
    timeline_y = 150
    milestones = [
        ("Q1", "大模型优化", 150),
        ("Q2", "多模态融合", 300),
        ("Q3", "边缘计算AI", 450),
        ("Q4", "AGI突破", 600)
    ]
    
    # 绘制连接线
    draw.line([(100, timeline_y), (700, timeline_y)], fill=accent_color, width=3)
    
    for quarter, milestone, x in milestones:
        # 绘制节点
        draw.ellipse([x-15, timeline_y-15, x+15, timeline_y+15], fill=accent_color)
        
        # 绘制标签
        draw.text((x-20, timeline_y-50), quarter, fill=(255, 255, 255), font=title_font)
        draw.text((x-40, timeline_y+30), milestone, fill=(200, 200, 200), font=text_font)
    
    img.save(output_path)

def create_programming_languages_pie(output_path):
    """创建编程语言使用占比饼图"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (25, 25, 35))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 28)
        label_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 14)
    except:
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
    
    draw.text((200, 30), "编程语言流行度 2025", fill=(255, 255, 255), font=title_font)
    
    # 饼图数据
    languages = [
        ("Python", 28, (52, 152, 219)),
        ("JavaScript", 22, (46, 204, 113)),
        ("TypeScript", 18, (155, 89, 182)),
        ("Rust", 12, (230, 126, 34)),
        ("Go", 10, (241, 196, 15)),
        ("其他", 10, (231, 76, 60))
    ]
    
    center_x, center_y = 400, 350
    radius = 150
    start_angle = 0
    
    for lang, percentage, color in languages:
        end_angle = start_angle + (percentage * 360 / 100)
        
        # 绘制扇形
        draw.pieslice([center_x-radius, center_y-radius, center_x+radius, center_y+radius],
                     start_angle, end_angle, fill=color)
        
        # 计算标签位置
        mid_angle = start_angle + (end_angle - start_angle) / 2
        label_x = center_x + (radius + 50) * (1 if mid_angle % 360 < 180 else -1) * 0.7
        label_y = center_y + (radius + 30) * (1 if 90 < mid_angle % 360 < 270 else -1) * 0.3
        
        draw.text((label_x, label_y), f"{lang} {percentage}%", fill=(255, 255, 255), font=label_font)
        
        start_angle = end_angle
    
    img.save(output_path)

def create_dev_tools_comparison(output_path):
    """创建开发工具对比图"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (18, 18, 26))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 28)
        text_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 16)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    draw.text((200, 30), "开发工具生态对比", fill=(255, 255, 255), font=title_font)
    
    # 工具对比数据
    tools = [
        ("VS Code", 9.2, (0, 122, 204)),
        ("JetBrains", 8.5, (255, 215, 0)),
        ("Vim/Neovim", 7.8, (0, 150, 136)),
        ("Sublime", 6.9, (255, 69, 0)),
        ("Atom", 5.2, (102, 170, 85))
    ]
    
    y_start = 120
    for i, (tool, rating, color) in enumerate(tools):
        y = y_start + i * 80
        
        # 绘制工具名称
        draw.text((50, y), tool, fill=(255, 255, 255), font=text_font)
        
        # 绘制评分条
        bar_width = int(rating * 60)
        draw.rectangle([200, y, 200 + bar_width, y + 30], fill=color)
        
        # 绘制评分
        draw.text((200 + bar_width + 20, y + 5), f"{rating}/10", fill=(200, 200, 200), font=text_font)
    
    img.save(output_path)

def create_cloud_architecture(output_path):
    """创建云架构图"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (240, 248, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 28)
        text_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 14)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    draw.text((250, 30), "现代云架构设计", fill=(25, 25, 112), font=title_font)
    
    # 绘制架构组件
    components = [
        ("用户", 100, 150, (70, 130, 180)),
        ("CDN", 300, 100, (255, 140, 0)),
        ("负载均衡", 300, 200, (50, 205, 50)),
        ("API网关", 500, 150, (220, 20, 60)),
        ("微服务", 650, 100, (138, 43, 226)),
        ("数据库", 650, 200, (30, 144, 255))
    ]
    
    # 绘制连接线
    connections = [
        ((100, 150), (300, 100)),
        ((100, 150), (300, 200)),
        ((300, 100), (500, 150)),
        ((300, 200), (500, 150)),
        ((500, 150), (650, 100)),
        ((500, 150), (650, 200))
    ]
    
    for start, end in connections:
        draw.line([start, end], fill=(100, 100, 100), width=2)
    
    for name, x, y, color in components:
        # 绘制组件框
        draw.rectangle([x-40, y-20, x+40, y+20], fill=color, outline=(0, 0, 0))
        
        # 绘制组件名称
        bbox = draw.textbbox((0, 0), name, font=text_font)
        text_width = bbox[2] - bbox[0]
        draw.text((x - text_width//2, y - 8), name, fill=(255, 255, 255), font=text_font)
    
    img.save(output_path)

def create_api_performance_chart(output_path):
    """创建API性能监控图"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (32, 32, 40))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 24)
        text_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 12)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    draw.text((250, 30), "API 性能监控面板", fill=(255, 255, 255), font=title_font)
    
    # 绘制性能指标
    metrics = [
        ("响应时间", "125ms", (46, 204, 113)),
        ("吞吐量", "2.5K/s", (52, 152, 219)),
        ("错误率", "0.02%", (231, 76, 60)),
        ("可用性", "99.9%", (241, 196, 15))
    ]
    
    for i, (metric, value, color) in enumerate(metrics):
        x = 150 + (i % 2) * 300
        y = 150 + (i // 2) * 200
        
        # 绘制指标卡片
        draw.rectangle([x-80, y-60, x+80, y+60], fill=color, outline=color)
        
        # 绘制指标名称和值
        draw.text((x-60, y-30), metric, fill=(255, 255, 255), font=text_font)
        draw.text((x-40, y), value, fill=(255, 255, 255), font=title_font)
    
    # 绘制性能曲线
    curve_y = 450
    points = []
    for i in range(0, 700, 20):
        y_offset = 30 * (0.5 + 0.5 * (i / 700))
        points.append((100 + i, curve_y - y_offset))
    
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=(46, 204, 113), width=3)
    
    img.save(output_path)

def create_security_dashboard(output_path):
    """创建安全监控仪表板"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (20, 25, 30))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 28)
        text_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 14)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    draw.text((220, 30), "网络安全监控中心", fill=(255, 255, 255), font=title_font)
    
    # 绘制威胁等级
    threat_levels = [
        ("低风险", 180, 120, (46, 204, 113)),
        ("中风险", 295, 120, (241, 196, 15)),
        ("高风险", 410, 120, (231, 76, 60))
    ]
    
    for level, x, y, color in threat_levels:
        # 绘制威胁等级指示器
        draw.ellipse([x-25, y-25, x+25, y+25], fill=color)
        draw.text((x-30, y+40), level, fill=(255, 255, 255), font=text_font)
    
    # 绘制安全事件统计
    events = ["SQL注入尝试: 23", "暴力破解: 12", "异常访问: 5", "恶意文件: 2"]
    for i, event in enumerate(events):
        y = 250 + i * 40
        draw.text((100, y), f"• {event}", fill=(200, 200, 200), font=text_font)
    
    # 绘制安全状态圆环
    center_x, center_y = 600, 350
    radius = 80
    
    # 外圆环 (总体安全分数)
    draw.ellipse([center_x-radius, center_y-radius, center_x+radius, center_y+radius], 
                outline=(46, 204, 113), width=8)
    
    # 内圆环 (当前威胁等级)
    inner_radius = 60
    draw.ellipse([center_x-inner_radius, center_y-inner_radius, 
                 center_x+inner_radius, center_y+inner_radius], 
                outline=(241, 196, 15), width=6)
    
    # 安全分数
    draw.text((center_x-15, center_y-10), "87%", fill=(255, 255, 255), font=title_font)
    draw.text((center_x-25, center_y+20), "安全", fill=(200, 200, 200), font=text_font)
    
    img.save(output_path)

def create_mobile_development_trends(output_path):
    """创建移动开发趋势图"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (15, 20, 25))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 28)
        text_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 14)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    draw.text((200, 30), "移动开发技术趋势", fill=(255, 255, 255), font=title_font)
    
    # 技术趋势数据
    frameworks = [
        ("React Native", [60, 65, 70, 75, 80], (97, 218, 251)),
        ("Flutter", [40, 50, 62, 72, 78], (66, 165, 245)),
        ("Native iOS", [80, 78, 75, 72, 70], (255, 183, 77)),
        ("Native Android", [85, 82, 79, 76, 73], (129, 199, 132)),
        ("Xamarin", [45, 42, 38, 35, 30], (240, 98, 146))
    ]
    
    # 绘制趋势线
    chart_start_x, chart_start_y = 100, 150
    chart_width, chart_height = 600, 300
    
    # 绘制网格
    for i in range(6):
        y = chart_start_y + i * (chart_height // 5)
        draw.line([(chart_start_x, y), (chart_start_x + chart_width, y)], 
                 fill=(50, 50, 50), width=1)
    
    for i in range(6):
        x = chart_start_x + i * (chart_width // 5)
        draw.line([(x, chart_start_y), (x, chart_start_y + chart_height)], 
                 fill=(50, 50, 50), width=1)
    
    # 绘制趋势线
    for framework, values, color in frameworks:
        points = []
        for i, value in enumerate(values):
            x = chart_start_x + (i * chart_width // 4)
            y = chart_start_y + chart_height - (value * chart_height // 100)
            points.append((x, y))
        
        # 绘制线条
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=color, width=3)
        
        # 绘制点
        for point in points:
            draw.ellipse([point[0]-3, point[1]-3, point[0]+3, point[1]+3], fill=color)
    
    # 绘制图例
    legend_y = chart_start_y + chart_height + 50
    for i, (framework, _, color) in enumerate(frameworks):
        x = chart_start_x + i * 120
        draw.rectangle([x, legend_y, x+15, legend_y+15], fill=color)
        draw.text((x+20, legend_y), framework, fill=(255, 255, 255), font=text_font)
    
    img.save(output_path)

def create_devops_pipeline(output_path):
    """创建DevOps流水线图"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (248, 249, 250))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 28)
        text_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 12)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    draw.text((250, 30), "DevOps 持续集成流水线", fill=(33, 37, 41), font=title_font)
    
    # 流水线阶段
    stages = [
        ("代码提交", 100, 150, (40, 167, 69)),
        ("构建", 200, 150, (3, 102, 214)),
        ("测试", 300, 150, (255, 193, 7)),
        ("部署", 400, 150, (220, 53, 69)),
        ("监控", 500, 150, (111, 66, 193))
    ]
    
    # 绘制流水线连接
    for i in range(len(stages) - 1):
        start_x = stages[i][1] + 40
        end_x = stages[i+1][1] - 40
        y = stages[i][2]
        
        # 绘制箭头
        draw.line([(start_x, y), (end_x, y)], fill=(108, 117, 125), width=3)
        draw.polygon([(end_x, y), (end_x-10, y-5), (end_x-10, y+5)], 
                    fill=(108, 117, 125))
    
    # 绘制各个阶段
    for stage, x, y, color in stages:
        # 绘制圆形节点
        draw.ellipse([x-30, y-30, x+30, y+30], fill=color)
        
        # 绘制阶段名称
        bbox = draw.textbbox((0, 0), stage, font=text_font)
        text_width = bbox[2] - bbox[0]
        draw.text((x - text_width//2, y - 6), stage, fill=(255, 255, 255), font=text_font)
        
        # 绘制状态指示
        status_texts = ["✓ 完成", "✓ 完成", "⟳ 进行中", "⏸ 等待", "○ 准备"]
        draw.text((x - 25, y + 50), status_texts[stages.index((stage, x, y, color))], 
                 fill=(108, 117, 125), font=text_font)
    
    # 绘制统计信息
    stats_y = 300
    stats = [
        ("构建成功率", "94.2%", (40, 167, 69)),
        ("平均构建时间", "3.2分钟", (3, 102, 214)),
        ("部署频率", "12次/天", (220, 53, 69))
    ]
    
    for i, (metric, value, color) in enumerate(stats):
        x = 150 + i * 180
        # 绘制统计卡片
        draw.rectangle([x-60, stats_y-40, x+60, stats_y+40], 
                      fill=color, outline=color)
        
        # 绘制统计信息
        draw.text((x-50, stats_y-20), metric, fill=(255, 255, 255), font=text_font)
        draw.text((x-30, stats_y), value, fill=(255, 255, 255), font=title_font)
    
    img.save(output_path)

def create_database_performance(output_path):
    """创建数据库性能监控图"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (25, 30, 35))
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 28)
        text_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 14)
        small_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 10)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    draw.text((220, 30), "数据库性能监控", fill=(255, 255, 255), font=title_font)
    
    # 性能指标仪表盘
    gauges = [
        ("CPU使用率", 67, 200, 120, (231, 76, 60)),
        ("内存使用", 45, 400, 120, (241, 196, 15)),
        ("磁盘I/O", 23, 600, 120, (46, 204, 113))
    ]
    
    for metric, value, center_x, center_y, color in gauges:
        # 绘制仪表盘背景
        draw.arc([center_x-50, center_y-50, center_x+50, center_y+50], 
                start=180, end=0, fill=(60, 60, 60), width=8)
        
        # 绘制当前值弧线
        end_angle = 180 - (value * 180 / 100)
        draw.arc([center_x-50, center_y-50, center_x+50, center_y+50], 
                start=180, end=end_angle, fill=color, width=8)
        
        # 绘制指标名称
        bbox = draw.textbbox((0, 0), metric, font=text_font)
        text_width = bbox[2] - bbox[0]
        draw.text((center_x - text_width//2, center_y + 20), metric, 
                 fill=(255, 255, 255), font=text_font)
        
        # 绘制数值
        value_text = f"{value}%"
        bbox = draw.textbbox((0, 0), value_text, font=title_font)
        text_width = bbox[2] - bbox[0]
        draw.text((center_x - text_width//2, center_y - 10), value_text, 
                 fill=(255, 255, 255), font=title_font)
    
    # 绘制查询性能图表
    chart_y = 300
    draw.text((50, chart_y), "慢查询分析", fill=(255, 255, 255), font=text_font)
    
    # 模拟慢查询数据
    queries = [
        ("SELECT * FROM users WHERE...", 1250, (231, 76, 60)),
        ("UPDATE orders SET status...", 890, (241, 196, 15)),
        ("JOIN products p ON...", 567, (155, 89, 182)),
        ("DELETE FROM logs WHERE...", 234, (46, 204, 113))
    ]
    
    max_time = max(query[1] for query in queries)
    
    for i, (query, time_ms, color) in enumerate(queries):
        y = chart_y + 50 + i * 40
        bar_width = int((time_ms / max_time) * 400)
        
        # 绘制查询条
        draw.rectangle([180, y, 180 + bar_width, y + 20], fill=color)
        
        # 绘制查询文本
        query_short = query[:30] + "..." if len(query) > 30 else query
        draw.text((50, y + 3), query_short, fill=(200, 200, 200), font=small_font)
        
        # 绘制执行时间
        draw.text((180 + bar_width + 10, y + 3), f"{time_ms}ms", 
                 fill=(255, 255, 255), font=small_font)
    
    img.save(output_path)

def main():
    """主函数：生成所有图片"""
    output_dir = "/Users/lin/hime/HelloWe/articles/2025/03-developer-daily/image"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成所有图片
    image_generators = [
        ("tech_trends.png", create_tech_trend_chart),
        ("ai_roadmap.png", create_ai_development_roadmap),
        ("language_pie.png", create_programming_languages_pie),
        ("dev_tools.png", create_dev_tools_comparison),
        ("cloud_arch.png", create_cloud_architecture),
        ("api_performance.png", create_api_performance_chart),
        ("security_dashboard.png", create_security_dashboard),
        ("mobile_trends.png", create_mobile_development_trends),
        ("devops_pipeline.png", create_devops_pipeline),
        ("database_performance.png", create_database_performance)
    ]
    
    print("开始生成开发者日报图片...")
    
    for filename, generator_func in image_generators:
        output_path = os.path.join(output_dir, filename)
        try:
            generator_func(output_path)
            print(f"✓ 生成成功: {filename}")
        except Exception as e:
            print(f"✗ 生成失败: {filename} - {e}")
    
    print(f"\n所有图片已生成完成，保存在: {output_dir}")

if __name__ == "__main__":
    main()