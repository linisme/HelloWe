#!/usr/bin/env python3
"""
生成测试图片的脚本
使用PIL库创建各种类型的测试图片
"""

import os
from PIL import Image, ImageDraw, ImageFont
import random
import math

def create_basic_chart(width=800, height=600):
    """创建基础图表"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 绘制柱状图
    bars = [120, 200, 150, 300, 250, 180]
    bar_width = width // (len(bars) + 1)
    max_height = max(bars)
    
    for i, bar_height in enumerate(bars):
        x = (i + 1) * bar_width - bar_width // 4
        y = height - 50
        bar_h = int((bar_height / max_height) * (height - 100))
        
        # 随机颜色
        color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        draw.rectangle([x, y - bar_h, x + bar_width // 2, y], fill=color)
        
        # 添加数值标签
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        draw.text((x + 10, y - bar_h - 30), str(bar_height), fill='black', font=font)
    
    # 添加标题
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        title_font = ImageFont.load_default()
    draw.text((width//2 - 80, 20), "数据分析图表", fill='black', font=title_font)
    
    return img

def create_pie_chart(width=600, height=600):
    """创建饼图"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 饼图数据
    data = [30, 25, 20, 15, 10]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 3
    
    start_angle = 0
    for i, (value, color) in enumerate(zip(data, colors)):
        angle = (value / sum(data)) * 360
        end_angle = start_angle + angle
        
        # 绘制扇形
        draw.pieslice([center_x - radius, center_y - radius, 
                      center_x + radius, center_y + radius], 
                     start_angle, end_angle, fill=color)
        
        start_angle = end_angle
    
    # 添加标题
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    draw.text((width//2 - 60, 30), "市场份额分析", fill='black', font=font)
    
    return img

def create_timeline(width=800, height=400):
    """创建时间线图"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 时间线数据
    events = [
        ("2023-01", "项目启动"),
        ("2023-03", "需求分析"),
        ("2023-06", "开发阶段"),
        ("2023-09", "测试阶段"),
        ("2023-12", "上线部署")
    ]
    
    # 绘制主线
    y_line = height // 2
    draw.line([(50, y_line), (width - 50, y_line)], fill='#333', width=3)
    
    # 绘制事件点
    x_step = (width - 100) // (len(events) - 1)
    for i, (date, event) in enumerate(events):
        x = 50 + i * x_step
        
        # 绘制圆点
        draw.ellipse([x-8, y_line-8, x+8, y_line+8], fill='#FF6B6B')
        
        # 添加日期和事件
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        draw.text((x - 30, y_line - 40), date, fill='black', font=font)
        draw.text((x - 40, y_line + 20), event, fill='black', font=font)
    
    # 添加标题
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        title_font = ImageFont.load_default()
    draw.text((width//2 - 80, 30), "项目开发时间线", fill='black', font=title_font)
    
    return img

def create_flow_chart(width=800, height=600):
    """创建流程图"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 流程步骤
    steps = ["开始", "需求分析", "设计方案", "编码实现", "测试验证", "部署上线"]
    
    box_width, box_height = 120, 60
    y_step = (height - 100) // (len(steps) - 1)
    
    for i, step in enumerate(steps):
        y = 50 + i * y_step
        x = width // 2 - box_width // 2
        
        # 绘制矩形框
        if i == 0 or i == len(steps) - 1:
            # 开始和结束用椭圆
            draw.ellipse([x, y, x + box_width, y + box_height], 
                        fill='#96CEB4', outline='#333', width=2)
        else:
            # 中间步骤用矩形
            draw.rectangle([x, y, x + box_width, y + box_height], 
                          fill='#74B9FF', outline='#333', width=2)
        
        # 添加文字
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), step, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x + (box_width - text_width) // 2
        text_y = y + (box_height - text_height) // 2
        draw.text((text_x, text_y), step, fill='black', font=font)
        
        # 绘制箭头（除了最后一个）
        if i < len(steps) - 1:
            arrow_y = y + box_height + 10
            draw.line([(width//2, arrow_y), (width//2, arrow_y + 20)], fill='#333', width=2)
            # 箭头头部
            draw.polygon([(width//2-5, arrow_y + 15), (width//2+5, arrow_y + 15), 
                         (width//2, arrow_y + 20)], fill='#333')
    
    return img

def create_architecture_diagram(width=900, height=700):
    """创建系统架构图"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 系统层级
    layers = [
        ("前端界面", "#FFB6C1", 100),
        ("API网关", "#98FB98", 200),
        ("业务逻辑", "#87CEEB", 300),
        ("数据存储", "#F0E68C", 400)
    ]
    
    layer_height = 80
    
    for i, (name, color, y) in enumerate(layers):
        # 绘制层级矩形
        draw.rectangle([100, y, width-100, y + layer_height], 
                      fill=color, outline='#333', width=2)
        
        # 添加层级名称
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
        except:
            font = ImageFont.load_default()
        
        draw.text((width//2 - 40, y + 30), name, fill='black', font=font)
        
        # 绘制连接线（除了最后一层）
        if i < len(layers) - 1:
            arrow_y = y + layer_height + 10
            draw.line([(width//2, arrow_y), (width//2, arrow_y + 20)], fill='#333', width=2)
    
    # 添加标题
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        title_font = ImageFont.load_default()
    draw.text((width//2 - 80, 30), "系统架构图", fill='black', font=title_font)
    
    return img

def create_network_topology(width=800, height=600):
    """创建网络拓扑图"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 网络设备位置
    devices = [
        ("路由器", width//2, 100, "#FF6B6B"),
        ("交换机1", width//4, 300, "#4ECDC4"),
        ("交换机2", 3*width//4, 300, "#4ECDC4"),
        ("服务器1", width//6, 500, "#96CEB4"),
        ("服务器2", width//2, 500, "#96CEB4"),
        ("服务器3", 5*width//6, 500, "#96CEB4")
    ]
    
    # 连接关系
    connections = [
        (0, 1), (0, 2),  # 路由器连接交换机
        (1, 3), (1, 4),  # 交换机1连接服务器
        (2, 4), (2, 5)   # 交换机2连接服务器
    ]
    
    # 绘制连接线
    for start, end in connections:
        start_x, start_y = devices[start][1], devices[start][2]
        end_x, end_y = devices[end][1], devices[end][2]
        draw.line([(start_x, start_y), (end_x, end_y)], fill='#333', width=2)
    
    # 绘制设备
    for name, x, y, color in devices:
        # 绘制设备图标（圆形）
        radius = 30
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                    fill=color, outline='#333', width=2)
        
        # 添加设备名称
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        draw.text((x - text_width//2, y + radius + 10), name, fill='black', font=font)
    
    # 添加标题
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        title_font = ImageFont.load_default()
    draw.text((width//2 - 80, 30), "网络拓扑结构", fill='black', font=title_font)
    
    return img

def create_comparison_chart(width=800, height=500):
    """创建对比图表"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 对比数据
    categories = ["性能", "安全性", "易用性", "成本", "扩展性"]
    product_a = [85, 90, 75, 60, 80]
    product_b = [70, 85, 90, 80, 75]
    
    # 绘制雷达图背景
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 3
    
    # 绘制同心圆
    for r in range(20, radius, 20):
        draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], 
                    outline='#DDD', width=1)
    
    # 绘制分类轴线
    angle_step = 360 / len(categories)
    for i, category in enumerate(categories):
        angle = math.radians(i * angle_step - 90)
        end_x = center_x + radius * math.cos(angle)
        end_y = center_y + radius * math.sin(angle)
        
        draw.line([(center_x, center_y), (end_x, end_y)], fill='#DDD', width=1)
        
        # 添加分类标签
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        label_x = center_x + (radius + 20) * math.cos(angle)
        label_y = center_y + (radius + 20) * math.sin(angle)
        draw.text((label_x - 20, label_y - 10), category, fill='black', font=font)
    
    # 绘制产品A数据
    points_a = []
    for i, value in enumerate(product_a):
        angle = math.radians(i * angle_step - 90)
        r = (value / 100) * radius
        x = center_x + r * math.cos(angle)
        y = center_y + r * math.sin(angle)
        points_a.append((x, y))
    
    draw.polygon(points_a, outline='#FF6B6B', width=2)
    
    # 绘制产品B数据
    points_b = []
    for i, value in enumerate(product_b):
        angle = math.radians(i * angle_step - 90)
        r = (value / 100) * radius
        x = center_x + r * math.cos(angle)
        y = center_y + r * math.sin(angle)
        points_b.append((x, y))
    
    draw.polygon(points_b, outline='#4ECDC4', width=2)
    
    # 添加图例
    draw.rectangle([50, height - 80, 70, height - 60], fill='#FF6B6B')
    draw.text((80, height - 75), "产品 A", fill='black')
    draw.rectangle([50, height - 50, 70, height - 30], fill='#4ECDC4')
    draw.text((80, height - 45), "产品 B", fill='black')
    
    # 添加标题
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        title_font = ImageFont.load_default()
    draw.text((width//2 - 80, 30), "产品对比分析", fill='black', font=title_font)
    
    return img

def create_mind_map(width=900, height=700):
    """创建思维导图"""
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # 中心节点
    center_x, center_y = width // 2, height // 2
    
    # 主要分支
    branches = [
        ("技术架构", [(45, "前端框架"), (135, "后端服务"), (225, "数据库"), (315, "缓存系统")]),
        ("开发流程", [(0, "需求分析"), (90, "设计开发"), (180, "测试部署"), (270, "运维监控")]),
        ("团队协作", [(60, "项目管理"), (120, "代码协作"), (240, "文档规范"), (300, "知识分享")])
    ]
    
    # 绘制中心节点
    draw.ellipse([center_x-50, center_y-30, center_x+50, center_y+30], 
                fill='#FFD93D', outline='#333', width=2)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
    except:
        font = ImageFont.load_default()
    draw.text((center_x-30, center_y-10), "项目管理", fill='black', font=font)
    
    # 绘制主分支
    main_radius = 150
    colors = ['#FF6B6B', '#4ECDC4', '#96CEB4']
    
    for i, (main_topic, sub_topics) in enumerate(branches):
        angle = math.radians(i * 120)
        main_x = center_x + main_radius * math.cos(angle)
        main_y = center_y + main_radius * math.sin(angle)
        
        # 连接线到主分支
        draw.line([(center_x, center_y), (main_x, main_y)], fill='#333', width=3)
        
        # 主分支节点
        draw.ellipse([main_x-40, main_y-20, main_x+40, main_y+20], 
                    fill=colors[i], outline='#333', width=2)
        draw.text((main_x-30, main_y-8), main_topic, fill='black', font=font)
        
        # 子分支
        for sub_angle, sub_topic in sub_topics:
            sub_radius = 80
            total_angle = math.radians(i * 120 + sub_angle)
            sub_x = main_x + sub_radius * math.cos(total_angle)
            sub_y = main_y + sub_radius * math.sin(total_angle)
            
            # 连接线到子分支
            draw.line([(main_x, main_y), (sub_x, sub_y)], fill='#666', width=2)
            
            # 子分支节点
            draw.ellipse([sub_x-25, sub_y-15, sub_x+25, sub_y+15], 
                        fill='white', outline=colors[i], width=2)
            
            try:
                small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 10)
            except:
                small_font = ImageFont.load_default()
            draw.text((sub_x-20, sub_y-6), sub_topic, fill='black', font=small_font)
    
    return img

def create_dashboard(width=1000, height=800):
    """创建仪表板"""
    img = Image.new('RGB', (width, height), '#F8F9FA')
    draw = ImageDraw.Draw(img)
    
    # 标题栏
    draw.rectangle([0, 0, width, 80], fill='#2C3E50')
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        font = ImageFont.load_default()
    
    draw.text((20, 25), "系统监控仪表板", fill='white', font=title_font)
    draw.text((width-150, 30), "2025-01-28", fill='white', font=font)
    
    # KPI卡片
    kpis = [
        ("在线用户", "1,234", "#3498DB"),
        ("系统负载", "65%", "#E74C3C"),
        ("内存使用", "78%", "#F39C12"),
        ("响应时间", "120ms", "#27AE60")
    ]
    
    card_width = 200
    card_height = 100
    
    for i, (title, value, color) in enumerate(kpis):
        x = 50 + i * (card_width + 20)
        y = 120
        
        # 卡片背景
        draw.rectangle([x, y, x + card_width, y + card_height], 
                      fill='white', outline='#DDD', width=1)
        
        # 卡片顶部色条
        draw.rectangle([x, y, x + card_width, y + 5], fill=color)
        
        # 标题和数值
        draw.text((x + 10, y + 15), title, fill='#666', font=font)
        
        try:
            value_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            value_font = ImageFont.load_default()
        draw.text((x + 10, y + 40), value, fill=color, font=value_font)
    
    # 图表区域
    chart_y = 250
    
    # 趋势图
    trend_data = [45, 52, 48, 61, 55, 67, 59, 72, 68, 75]
    chart_width = 400
    chart_height = 200
    
    draw.rectangle([50, chart_y, 50 + chart_width, chart_y + chart_height], 
                  fill='white', outline='#DDD', width=1)
    draw.text((60, chart_y + 10), "访问量趋势", fill='#333', font=font)
    
    # 绘制趋势线
    points = []
    for i, value in enumerate(trend_data):
        x = 60 + i * (chart_width - 20) // (len(trend_data) - 1)
        y = chart_y + chart_height - 20 - (value / 100) * (chart_height - 60)
        points.append((x, y))
    
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill='#3498DB', width=2)
    
    # 状态指示器
    status_x = 500
    statuses = [
        ("数据库", "正常", "#27AE60"),
        ("API服务", "正常", "#27AE60"),
        ("缓存服务", "警告", "#F39C12"),
        ("文件存储", "正常", "#27AE60")
    ]
    
    draw.rectangle([status_x, chart_y, status_x + 350, chart_y + chart_height], 
                  fill='white', outline='#DDD', width=1)
    draw.text((status_x + 10, chart_y + 10), "服务状态", fill='#333', font=font)
    
    for i, (service, status, color) in enumerate(statuses):
        y = chart_y + 40 + i * 35
        
        # 状态指示灯
        draw.ellipse([status_x + 20, y, status_x + 35, y + 15], fill=color)
        
        # 服务名称和状态
        draw.text((status_x + 50, y), f"{service}: {status}", fill='#333', font=font)
    
    return img

def generate_all_images():
    """生成所有测试图片"""
    output_dir = "/Users/lin/hime/HelloWe/articles/2025/02-image-test"
    
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成各种图片
    images = [
        ("chart.png", create_basic_chart()),
        ("pie_chart.png", create_pie_chart()),
        ("timeline.png", create_timeline()),
        ("flowchart.png", create_flow_chart()),
        ("architecture.png", create_architecture_diagram()),
        ("network.png", create_network_topology()),
        ("comparison.png", create_comparison_chart()),
        ("mindmap.png", create_mind_map()),
        ("dashboard.png", create_dashboard()),
        ("cover.png", create_dashboard(800, 600))  # 封面图
    ]
    
    for filename, img in images:
        filepath = os.path.join(output_dir, filename)
        img.save(filepath, "PNG", quality=95)
        print(f"✅ 生成图片: {filename}")
    
    print(f"\n🎉 所有测试图片已生成完成！")
    print(f"📁 图片保存位置: {output_dir}")

if __name__ == "__main__":
    generate_all_images()