import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# Get script directory
script_dir = os.path.dirname(__file__)
font_dir = os.path.join(script_dir, 'font')

# =========== 1. Global Configuration ===========# Image dimensions
IMG_WIDTH = 1200
IMG_HEIGHT = 1800
PADDING = 50

# Layout dimensions
HEADER_HEIGHT = 80
LEFT_AXIS_WIDTH = 60

# Timetable definition
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TIME_SLOTS = [f"{i}:00" for i in range(8, 22)]  # Time range: 8 AM to 9 PM

# --- Requirement 4: Style Options ---
# You can choose a preset style here: 'modern', 'cute', 'cool', 'fresh'
STYLES = {
    'modern': {
        'bg_colors': ('#F0F2F5', '#E6E9EE'),
        'line_color': '#D8DCE3',
        'font_color': '#333740',
        'text_on_course_color': '#2D3436',
        'palette': ['#D4E2F4', '#F4D9D4', '#D4F4E2', '#F4F1D4', '#E2D4F4', '#D4F4F1'],
        'font_path': None,
        'font_bold_path': None,
    },
    'cute': {
        'bg_colors': ('#FFF0F5', '#F8E9EE'),
        'line_color': '#F5E3E8',
        'font_color': '#D66D93',
        'text_on_course_color': '#6B2D3F',
        'palette': ['#FFC3D9', '#C3E1FF', '#C3FFD9', '#FFFDC3', '#E1C3FF', '#C3F8FF'],
        'font_path': None,
        'font_bold_path': None,
    },
    'cool': {
        'bg_colors': ('#282C34', '#21252B'),
        'line_color': '#3E444F',
        'font_color': '#ABB2BF',
        'text_on_course_color': '#FFFFFF',
        'palette': ['#61AFEF', '#E06C75', '#98C379', '#E5C07B', '#C678DD', '#56B6C2'],
        'font_path': None,
        'font_bold_path': None,
    },
    'fresh': {
        'bg_colors': ('#F3F9FB', '#E8F3F6'),
        'line_color': '#DAE6EB',
        'font_color': '#3E667A',
        'text_on_course_color': '#0B4F6C',
        'palette': ['#A8DADC', '#F191A2', '#83D4A3', '#FADF98', '#B3B8E3', '#98DFF0'],
        'font_path': None,
        'font_bold_path': None,
    }
}

# =========== 3. Sample Data ===========# Requirement 5: Provide sample course data to directly generate the timetable.
sample_courses = [
    ("Advanced Mathematics", 1, "8:00", "9:40", "Classroom A-101", 0),
    ("Python Programming Practice", 1, "14:00", "16:30", "Lab Building 302", 0),
    ("College English", 2, "10:00", "11:40", "Liberal Arts Building 203", 0),
    ("Linear Algebra", 3, "8:00", "9:40", "Classroom A-101", 0),
    ("Data Structures and Algorithms", 3, "14:00", "16:30", "Lab Building 304", 0),
    ("Physical Education (Tennis)", 4, "15:00", "16:40", "Gymnasium", 0),
    ("Operating System Principles", 5, "10:00", "12:30", "Lab Building 501", 0),
    ("Film Appreciation", 5, "19:00", "20:40", "Art Building Screening Room", 0),
    ("Weekend Self-Study", 6, "9:00", "17:00", "Library", 0),
]


# =========== 4. Helper Functions ===========
def create_background(width, height, colors):
    """Requirement 1: Create a delicate gradient background that doesn't overpower the content."""
    base = Image.new('RGB', (width, height), colors[0])
    top = Image.new('RGB', (width, height), colors[1])
    mask = Image.new('L', (width, height))
    mask_data = [int(255 * (y / height)) for y in range(height) for _ in range(width)]
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base


def draw_3d_effect_shadow(base_image, xy, radius):
    """Requirement 6: Add a 3D effect by drawing a soft, blurred shadow."""
    x1, y1, x2, y2 = [int(v) for v in xy]
    offset = 10
    blur_radius = 8  # Shadow blur radius
    shadow_color = (0, 0, 0, 40)  # Use semi-transparent black as a general shadow color

    # Draw shadow on a separate transparent layer for blurring
    shadow_canvas = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_canvas)
    shadow_draw.rounded_rectangle((x1, y1 + offset, x2, y2 + offset), radius=radius, fill=shadow_color)

    # Use Gaussian blur to create soft shadow edges
    shadow_canvas = shadow_canvas.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # Composite the blurred shadow onto the main image
    base_image.paste(shadow_canvas, (0, 0), shadow_canvas)


def get_text_size(draw, text, font):
    """Helper function to accurately calculate text size."""
    if hasattr(draw, 'textbbox'):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:  # Compatible with older Pillow versions
        return draw.textsize(text, font=font)

def wrap_text(draw, text, font, max_width):
    """Helper function to wrap text based on max_width."""
    lines = []
    if not text: return lines

    # Handle Chinese characters: split by character if it's a single word that exceeds max_width
    # For simplicity, we'll assume words are separated by spaces for English, and for Chinese,
    # we'll try to fit as many characters as possible.
    words = text.split(' ')
    current_line = []

    for word in words:
        # Check if adding the next word (plus a space if it's not the first word) exceeds max_width
        test_line = ' '.join(current_line + [word])
        test_width, _ = get_text_size(draw, test_line, font)

        if test_width <= max_width:
            current_line.append(word)
        else:
            # If current_line is not empty, add it to lines and start a new line with the current word
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

            # If even a single word exceeds max_width, try to break it down (e.g., for long Chinese words or very long English words)
            word_width, _ = get_text_size(draw, word, font)
            if word_width > max_width:
                sub_word_line = []
                for char in word:
                    test_sub_word_line = ''.join(sub_word_line + [char])
                    test_sub_word_width, _ = get_text_size(draw, test_sub_word_line, font)
                    if test_sub_word_width <= max_width:
                        sub_word_line.append(char)
                    else:
                        if sub_word_line:
                            lines.append(''.join(sub_word_line))
                        sub_word_line = [char]
                if sub_word_line:
                    lines.append(''.join(sub_word_line))
                current_line = [] # Reset current_line as the word was fully processed

    if current_line:
        lines.append(' '.join(current_line))

    return lines


# =========== 5. Main Generator Function ===========
def generate_timetable_image(courses=sample_courses, selected_style='fresh', generate_png=True, generate_pdf=True, week_date_range=""):
    """Integrate all elements to generate the final timetable image."""
    style = STYLES[selected_style]
    # Step 1: Create background
    base_bg = create_background(IMG_WIDTH, IMG_HEIGHT, style['bg_colors'])
    img = base_bg.convert('RGBA')  # Convert to RGBA mode to handle shadows with transparency
    draw = ImageDraw.Draw(img)

    # Step 2: Load fonts
    font_regular = ImageFont.load_default()
    font_bold = ImageFont.load_default()
    font_course = ImageFont.load_default()
    font_course_bold = ImageFont.load_default()
    font_date_range = ImageFont.load_default()

    if style['font_path']:
        try:
            font_regular = ImageFont.truetype(style['font_path'], 28)
            font_course = ImageFont.truetype(style['font_path'], 24)
        except IOError:
            print(f"Tip: Font file not found! Please place font files like '{style['font_path']}' in the script directory. Default font will be used.")
    
    if style['font_bold_path']:
        try:
            font_bold = ImageFont.truetype(style['font_bold_path'], 40)
            font_course_bold = ImageFont.truetype(style['font_bold_path'], 30)
            font_date_range = ImageFont.truetype(style['font_bold_path'], 32) # New font for date range
        except IOError:
            print(f"Tip: Font file not found! Please place font files like '{style['font_bold_path']}' in the script directory. Default font will be used.")

    # Step 3: Draw timetable grid and axes
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

    # Step 4: Draw all courses
    course_colors = {}
    color_palette = style['palette']

    for course_data in courses:
        course_name, day_index, start_time, end_time, location, _ = course_data

        # Assign a color to each course
        if course_name not in course_colors:
            course_colors[course_name] = color_palette[len(course_colors) % len(color_palette)]

        # Calculate course block position and size
        day_col = day_index - 1
        start_h, start_m = map(int, start_time.split(':'))
        end_h, end_m = map(int, end_time.split(':'))
        start_row = (start_h - 8) + start_m / 60.0
        end_row = (end_h - 8) + end_m / 60.0
        x1, y1 = grid_x_start + day_col * col_width + 8, grid_y_start + start_row * row_height + 4
        x2, y2 = grid_x_start + (day_col + 1) * col_width - 8, grid_y_start + end_row * row_height - 4

        # Core drawing steps:
        # a. Draw shadow first for 3D effect (Requirement 6)
        draw_3d_effect_shadow(img, (x1, y1, x2, y2), radius=15)
        # b. Then draw rounded course blocks (Requirement 2 & 3)
        draw.rounded_rectangle((x1, y1, x2, y2), radius=15, fill=course_colors[course_name])
        # c. Finally, draw course text
        text_y_pos = y1 + 10
        text_color = style['text_on_course_color']
        max_text_width = int(x2 - x1 - 16) # 8 pixels padding on each side

        # Draw wrapped course name
        wrapped_course_name = wrap_text(draw, course_name, font_course_bold, max_text_width)
        for line in wrapped_course_name:
            text_w, text_h = get_text_size(draw, line, font_course_bold)
            draw.text((x1 + (max_text_width + 16 - text_w) / 2, text_y_pos), line, fill=text_color, font=font_course_bold)
            text_y_pos += text_h + 2 # Add a small line spacing

        # Draw wrapped location text
        location_text = f"@{location}" if location else ""
        wrapped_location_text = wrap_text(draw, location_text, font_course, max_text_width)
        for line in wrapped_location_text:
            text_w, text_h = get_text_size(draw, line, font_course)
            draw.text((x1 + (max_text_width + 16 - text_w) / 2, text_y_pos), line, fill=text_color, font=font_course)
            text_y_pos += text_h + 2 # Add a small line spacing

    final_img = img.convert('RGB')

    return final_img


# =========== 6. Script Entry Point ===========if __name__ == '__main__':
    generate_timetable_image()