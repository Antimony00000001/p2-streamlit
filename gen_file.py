import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# 获取脚本所在目录
script_dir = os.path.dirname(__file__)
font_dir = os.path.join(script_dir, 'font')

# =========== 1. 全局配置 (Global Configuration) ===========
# 图片尺寸
IMG_WIDTH = 1200
IMG_HEIGHT = 1800
PADDING = 50

# 布局尺寸
HEADER_HEIGHT = 80
LEFT_AXIS_WIDTH = 60

# 时间表定义
DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
TIME_SLOTS = [f"{i}:00" for i in range(8, 22)]  # 时间范围：早8点至晚9点

# --- Requirement 4: 风格可选 ---
# 你可以在这里选择一种预设的风格: 'modern', 'cute', 'cool', 'fresh'
STYLES = {
    'modern': {
        'bg_colors': ('#F0F2F5', '#E6E9EE'),
        'line_color': '#D8DCE3',
        'font_color': '#333740',
        'text_on_course_color': '#2D3436',
        'palette': ['#D4E2F4', '#F4D9D4', '#D4F4E2', '#F4F1D4', '#E2D4F4', '#D4F4F1'],
        'font_path': os.path.join(font_dir, 'MaShanZheng-Regular.ttf'),
        'font_bold_path': os.path.join(font_dir, 'MaShanZheng-Regular.ttf'),
    },
    'cute': {
        'bg_colors': ('#FFF0F5', '#F8E9EE'),
        'line_color': '#F5E3E8',
        'font_color': '#D66D93',
        'text_on_course_color': '#6B2D3F',
        'palette': ['#FFC3D9', '#C3E1FF', '#C3FFD9', '#FFFDC3', '#E1C3FF', '#C3F8FF'],
        'font_path': os.path.join(font_dir, 'MaShanZheng-Regular.ttf'),
        'font_bold_path': os.path.join(font_dir, 'MaShanZheng-Regular.ttf'),
    },
    'cool': {
        'bg_colors': ('#282C34', '#21252B'),
        'line_color': '#3E444F',
        'font_color': '#ABB2BF',
        'text_on_course_color': '#FFFFFF',
        'palette': ['#61AFEF', '#E06C75', '#98C379', '#E5C07B', '#C678DD', '#56B6C2'],
        'font_path': os.path.join(font_dir, 'MaShanZheng-Regular.ttf'),
        'font_bold_path': os.path.join(font_dir, 'MaShanZheng-Regular.ttf'),
    },
    'fresh': {
        'bg_colors': ('#F3F9FB', '#E8F3F6'),
        'line_color': '#DAE6EB',
        'font_color': '#3E667A',
        'text_on_course_color': '#0B4F6C',
        'palette': ['#A8DADC', '#F191A2', '#83D4A3', '#FADF98', '#B3B8E3', '#98DFF0'],
        'font_path': os.path.join(font_dir, 'MaShanZheng-Regular.ttf'),
        'font_bold_path': os.path.join(font_dir, 'MaShanZheng-Regular.ttf'),
    }
}

# =========== 3. 示例数据 (Sample Data) ===========
# Requirement 5: 提供一份课程示例数据，用于直接生成课表。
sample_courses = [
    ("高等数学", 1, "8:00", "9:40", "教A-101", 0),
    ("Python编程实践", 1, "14:00", "16:30", "实验楼302", 0),
    ("大学英语", 2, "10:00", "11:40", "文科楼203", 0),
    ("线性代数", 3, "8:00", "9:40", "教A-101", 0),
    ("数据结构与算法", 3, "14:00", "16:30", "实验楼304", 0),
    ("体育（网球）", 4, "15:00", "16:40", "体育馆", 0),
    ("操作系统原理", 5, "10:00", "12:30", "实验楼501", 0),
    ("电影鉴赏", 5, "19:00", "20:40", "艺术楼放映厅", 0),
    ("周末自习", 6, "9:00", "17:00", "图书馆", 0),
]


# =========== 4. 辅助绘图函数 (Helper Functions) ===========

def create_background(width, height, colors):
    """Requirement 1: 创建一个细腻的渐变背景，不喧宾夺主。"""
    base = Image.new('RGB', (width, height), colors[0])
    top = Image.new('RGB', (width, height), colors[1])
    mask = Image.new('L', (width, height))
    mask_data = [int(255 * (y / height)) for y in range(height) for _ in range(width)]
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base


def draw_3d_effect_shadow(base_image, xy, radius):
    """Requirement 6: 通过绘制一个柔和模糊的阴影来增加立体效果。"""
    x1, y1, x2, y2 = [int(v) for v in xy]
    offset = 10
    blur_radius = 8  # 阴影模糊度
    shadow_color = (0, 0, 0, 40)  # 使用半透明黑色作为通用阴影色

    # 在一个独立的透明图层上绘制阴影，以进行模糊处理
    shadow_canvas = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_canvas)
    shadow_draw.rounded_rectangle((x1, y1 + offset, x2, y2 + offset), radius=radius, fill=shadow_color)

    # 使用高斯模糊创建柔和的阴影边缘
    shadow_canvas = shadow_canvas.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # 将模糊后的阴影合成到主图片上
    base_image.paste(shadow_canvas, (0, 0), shadow_canvas)


def get_text_size(draw, text, font):
    """精确计算文本尺寸的辅助函数。"""
    if hasattr(draw, 'textbbox'):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:  # 兼容旧版Pillow
        return draw.textsize(text, font=font)


# =========== 5. 主生成函数 (Main Generator Function) ===========

def generate_timetable_image(courses=sample_courses, selected_style='fresh', generate_png=True, generate_pdf=True, week_date_range=""):
    """整合所有元素，生成最终的课表图片。"""
    style = STYLES[selected_style]
    # 步骤 1: 创建背景
    base_bg = create_background(IMG_WIDTH, IMG_HEIGHT, style['bg_colors'])
    img = base_bg.convert('RGBA')  # 转换为RGBA模式以处理带透明度的阴影
    draw = ImageDraw.Draw(img)

    # 步骤 2: 加载字体
    try:
        font_regular = ImageFont.truetype(style['font_path'], 16)
        font_bold = ImageFont.truetype(style['font_bold_path'], 22)
        font_course = ImageFont.truetype(style['font_path'], 14)
        font_course_bold = ImageFont.truetype(style['font_bold_path'], 16)
        font_date_range = ImageFont.truetype(style['font_bold_path'], 18) # New font for date range
    except IOError:
        print(f"提示: 字体文件未找到! 请将 '{style['font_path']}' 等字体文件放置在脚本目录。将使用默认字体。")
        font_regular, font_bold, font_course, font_course_bold, font_date_range = [ImageFont.load_default()] * 5

    # 步骤 3: 绘制时间表网格和坐标轴
    grid_x_start = PADDING + LEFT_AXIS_WIDTH
    grid_y_start = PADDING + HEADER_HEIGHT
    grid_width = IMG_WIDTH - grid_x_start - PADDING
    grid_height = IMG_HEIGHT - grid_y_start - PADDING
    col_width = grid_width / len(DAYS)
    row_height = grid_height / len(TIME_SLOTS)

    # Draw week date range
    if week_date_range:
        text_w, text_h = get_text_size(draw, week_date_range, font_date_range)
        draw.text(((IMG_WIDTH - text_w) / 2, PADDING + 10), week_date_range, fill=style['font_color'], font=font_date_range)

    for i, day in enumerate(DAYS):
        text_w, text_h = get_text_size(draw, day, font_bold)
        x = grid_x_start + i * col_width + (col_width - text_w) / 2
        y = PADDING + (HEADER_HEIGHT - text_h) / 2 + 30 # Adjust Y to make space for date range
        draw.text((x, y), day, fill=style['font_color'], font=font_bold)

    for i, time in enumerate(TIME_SLOTS):
        y = grid_y_start + i * row_height
        text_w, _ = get_text_size(draw, time, font_regular)
        draw.text((grid_x_start - text_w - 15, y - 8), time, fill=style['font_color'], font=font_regular)
        draw.line([(grid_x_start - 5, y), (grid_x_start + grid_width, y)], fill=style['line_color'], width=1)

    # 步骤 4: 绘制所有课程
    course_colors = {}
    color_palette = style['palette']
    random.shuffle(color_palette)

    for course_data in courses:
        course_name, day_index, start_time, end_time, location, _ = course_data

        # 为每门课分配一个颜色
        if course_name not in course_colors:
            course_colors[course_name] = color_palette[len(course_colors) % len(color_palette)]

        # 计算课程块的位置和尺寸
        day_col = day_index - 1
        start_h, start_m = map(int, start_time.split(':'))
        end_h, end_m = map(int, end_time.split(':'))
        start_row = (start_h - 8) + start_m / 60.0
        end_row = (end_h - 8) + end_m / 60.0
        x1, y1 = grid_x_start + day_col * col_width + 8, grid_y_start + start_row * row_height + 4
        x2, y2 = grid_x_start + (day_col + 1) * col_width - 8, grid_y_start + end_row * row_height - 4

        # 核心绘制步骤:
        # a. 先画阴影，实现立体效果 (Requirement 6)
        draw_3d_effect_shadow(img, (x1, y1, x2, y2), radius=15)
        # b. 再画圆角课程块 (Requirement 2 & 3)
        draw.rounded_rectangle((x1, y1, x2, y2), radius=15, fill=course_colors[course_name])
        # c. 最后画上课程文字
        text_y_pos = y1 + 10
        text_color = style['text_on_course_color']

        text_w, text_h = get_text_size(draw, course_name, font_course_bold)
        draw.text((x1 + (x2 - x1 - text_w) / 2, text_y_pos), course_name, fill=text_color, font=font_course_bold)
        text_y_pos += text_h + 5

        location_text = f"@{location}"
        text_w, text_h = get_text_size(draw, location_text, font_course)
        draw.text((x1 + (x2 - x1 - text_w) / 2, text_y_pos), location_text, fill=text_color, font=font_course)

    final_img = img.convert('RGB')

    return final_img


# =========== 6. 脚本入口 (Script Entry Point) ===========
if __name__ == '__main__':
    generate_timetable_image()