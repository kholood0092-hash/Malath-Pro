import matplotlib.pyplot as plt
import matplotlib.patches as patches
import plotly.graph_objects as go

# ==========================================
# 🌟 دعم اللغة العربية المزدوج (2D & 3D) 🌟
# ==========================================

ARABIC_SUPPORT = False
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False

def fix_ar(text, for_plotly=False):
    """معالجة النص لتوافقه مع الرسم البياني بناءً على نوع المحرك البصري"""
    translations = {
        "المدخل": "المدخل", "الممر": "ممر الحركة", "الدرج": "الدرج",
        "ديوانية": "ديوانية", "حمام ديوانية": "حمام", "مغاسل ضيوف": "مغاسل", "صالة المعيشة": "صالة المعيشة", 
        "المطبخ": "المطبخ الرئيسي", "مطبخ تحضيري": "تحضيري", "غرفة غسيل": "غسيل", "غسيل علوي": "غسيل",
        "طعام": "طعام العائلة", "حمام عائلة": "حمام", "صالة علوية": "صالة علوية",
        "جناح الماستر": "جناح الماستر", "حمام الماستر": "حمام", "غرفة تبديل": "تبديل ملابس",
        "غرفة نوم 1": "نوم 1", "غرفة نوم 2": "نوم 2", "غرفة نوم 3": "نوم 3", 
        "صالة طعام ضيوف": "طعام ضيوف", "حمام مشترك": "حمام", "ممر داخلي": "ممر",
        "بلكونة الماستر": "بلكونة"
    }
    
    mapped_text = text
    for k, v in translations.items():
        if k in str(text):
            mapped_text = v
            break

    if for_plotly: return mapped_text

    if ARABIC_SUPPORT:
        try:
            reshaped_text = arabic_reshaper.reshape(mapped_text)
            return get_display(reshaped_text)
        except:
            return mapped_text
    return mapped_text
def generate_blueprint_figure(room_options, area, floor, is_green, prefs, climate=None):
    climate = climate or {}
    temp = climate.get('temp', 35)

    # تكيّف المخطط مع المناخ الحقيقي
    shade_depth  = 1.5 if temp > 40 else (1.0 if temp > 33 else 0.6)  # عمق الظلال
    window_ratio = 0.15 if temp > 38 else 0.25   # نسبة النوافذ: أصغر في الحر
    has_courtyard = temp > 36 and is_green        # فناء داخلي للتبريد الطبيعي
    wall_color   = '#D4A96A' if temp > 36 else '#B8C4D4'  # لون الواجهة حسب المناخ
  
# ==========================================
# 🌟 الهوية البصرية والخامات 🌟
# ==========================================
def get_theme_colors(prefs):
    cool = prefs.get('cool', False)
    wall_c = '#FFFFFF' if cool else '#FDFEFE' 
    floor_main = '#E5E8E8' if cool else '#FDF2E9' 
    floor_wet = '#D5DBDB' if cool else '#EAECEE'
    frame_c = '#B76E79' if prefs.get('rose_gold', False) else ('#2C3E50' if cool else '#8B4513')
    return wall_c, floor_main, floor_wet, frame_c

# ==========================================
# 🌟 محرك الأثاث المعماري الاحترافي 🌟
# ==========================================
def draw_furniture(ax, space_name, x, y, w, l, color='#BDC3C7'):
    """رسم عناصر الأثاث لتعزيز فهم التوزيع المكاني"""
    if "ديوانية" in space_name or "صالة المعيشة" in space_name or "علوية" in space_name:
        ax.add_patch(patches.Rectangle((x+0.8, y+0.8), w-1.6, 1.2, color=color, alpha=0.6))
        ax.add_patch(patches.Rectangle((x+0.8, y+0.8), 1.2, l-1.6, color=color, alpha=0.6))
        ax.add_patch(patches.Rectangle((x+w-2.0, y+0.8), 1.2, l-1.6, color=color, alpha=0.6))
        ax.add_patch(patches.Rectangle((x+w/2-1, y+l/2-1), 2, 2, fill=False, edgecolor='#7F8C8D', lw=1.5))
    elif "نوم" in space_name or "ماستر" in space_name:
        bx, by = x+w/2-1.5, y+l-3.5
        ax.add_patch(patches.Rectangle((bx, by), 3, 2.5, facecolor='#D5DBDB', edgecolor='#95A5A6', lw=1.5))
        ax.add_patch(patches.Rectangle((bx-0.8, by+1.8), 0.6, 0.6, facecolor=color, alpha=0.8))
        ax.add_patch(patches.Rectangle((bx+3.2, by+1.8), 0.6, 0.6, facecolor=color, alpha=0.8))
    elif "طعام" in space_name:
        ax.add_patch(patches.Rectangle((x+w/2-1.5, y+l/2-2.5), 3, 5, facecolor='#D35400', alpha=0.2, edgecolor='#D35400', lw=2))
    elif "مطبخ" in space_name:
        ax.add_patch(patches.Rectangle((x, y), 1.5, l, color='#7F8C8D', alpha=0.3))
        ax.add_patch(patches.Rectangle((x, y+l-1.5), w, 1.5, color='#7F8C8D', alpha=0.3))
    elif "الدرج" in space_name:
        for i in range(1, int(l)):
            ax.plot([x, x+w], [y+i, y+i], color='#95A5A6', lw=1)

# ==========================================
# 🌟 خوارزمية التوزيع المكاني (BIM Engine) 🌟
# ==========================================
# --- [Data Visualization: BIM Layout Algorithm] ---
def layout_ground_floor(opts):
    return [
        {'space': 'المدخل', 'x': 8, 'y': 0, 'w': 4, 'l': 4, 'zone': 'Corridor'},
        {'space': 'الممر', 'x': 8, 'y': 4, 'w': 4, 'l': 12, 'zone': 'Corridor'},
        {'space': 'الدرج', 'x': 8, 'y': 16, 'w': 4, 'l': 4, 'zone': 'Stairs'},
        {'space': 'صالة المعيشة', 'x': 0, 'y': 0, 'w': 8, 'l': 8, 'zone': 'Living'},
        {'space': 'طعام', 'x': 0, 'y': 8, 'w': 8, 'l': 5, 'zone': 'Living'},
        {'space': 'المطبخ', 'x': 0, 'y': 13, 'w': 8, 'l': 7, 'zone': 'Service'},
        {'space': 'ديوانية', 'x': 12, 'y': 0, 'w': 8, 'l': 7, 'zone': 'Guest'},
        {'space': 'مغاسل ضيوف', 'x': 12, 'y': 7, 'w': 4, 'l': 2, 'zone': 'Service'},
        {'space': 'حمام ديوانية', 'x': 16, 'y': 7, 'w': 4, 'l': 2, 'zone': 'Service'},
        {'space': 'صالة طعام ضيوف', 'x': 12, 'y': 9, 'w': 8, 'l': 6, 'zone': 'Guest'},
        {'space': 'حمام عائلة', 'x': 12, 'y': 15, 'w': 4, 'l': 5, 'zone': 'Service'},
        {'space': 'غرفة غسيل', 'x': 16, 'y': 15, 'w': 4, 'l': 5, 'zone': 'Service'}
    ]

def layout_first_floor(opts):
    return [
        {'space': 'صالة علوية', 'x': 8, 'y': 0, 'w': 4, 'l': 16, 'zone': 'Living'},
        {'space': 'الدرج', 'x': 8, 'y': 16, 'w': 4, 'l': 4, 'zone': 'Stairs'},
        {'space': 'غرفة نوم 1', 'x': 0, 'y': 0, 'w': 8, 'l': 6, 'zone': 'Private'},
        {'space': 'حمام 1', 'x': 0, 'y': 6, 'w': 4, 'l': 4, 'zone': 'Service'},
        {'space': 'ممر داخلي', 'x': 4, 'y': 6, 'w': 4, 'l': 4, 'zone': 'Corridor'},
        {'space': 'غرفة نوم 2', 'x': 0, 'y': 10, 'w': 8, 'l': 6, 'zone': 'Private'},
        {'space': 'حمام مشترك', 'x': 0, 'y': 16, 'w': 4, 'l': 4, 'zone': 'Service'},
        {'space': 'غسيل علوي', 'x': 4, 'y': 16, 'w': 4, 'l': 4, 'zone': 'Service'},
        {'space': 'بلكونة الماستر', 'x': 12, 'y': -2, 'w': 8, 'l': 2, 'zone': 'Balcony'},
        {'space': 'جناح الماستر', 'x': 12, 'y': 0, 'w': 8, 'l': 8, 'zone': 'Master'},
        {'space': 'غرفة تبديل', 'x': 12, 'y': 8, 'w': 8, 'l': 4, 'zone': 'Master'},
        {'space': 'حمام الماستر', 'x': 12, 'y': 12, 'w': 8, 'l': 3, 'zone': 'Service'},
        {'space': 'غرفة نوم 3', 'x': 12, 'y': 15, 'w': 8, 'l': 5, 'zone': 'Private'}
    ]

# ==========================================
# 🌟 1. رسم المخطط 2D 🌟
# ==========================================
def generate_blueprint_figure(rooms_data, total_area, floor_type='ground', is_green=False, prefs=None):
    if prefs is None: prefs = {}
    wall_col, floor_main, floor_wet, frame_col = get_theme_colors(prefs)
    mapped = layout_ground_floor(rooms_data) if floor_type == 'ground' else layout_first_floor(rooms_data)
    
    fig, ax = plt.subplots(figsize=(14, 12))
    ax.set_facecolor('#F8F9F9') 

    for r in mapped:
        x, y, w, l = r['x'], r['y'], r['w'], r['l']
        room_floor = floor_wet if r['zone'] in ['Service', 'Stairs'] else floor_main
        if r['zone'] == 'Balcony': room_floor = '#E8F6F3'

        ax.add_patch(patches.Rectangle((x, y), w, l, facecolor=room_floor, edgecolor='#333', lw=3.5))
        draw_furniture(ax, r['space'], x, y, w, l)

        if r['zone'] not in ['Corridor', 'Stairs', 'Balcony']:
            if x == 0:
                ax.plot([x, x], [y+l/2-1.5, y+l/2+1.5], color='#3498DB', lw=6)
            if x+w == 20:
                ax.plot([x+w, x+w], [y+l/2-1.5, y+l/2+1.5], color='#3498DB', lw=6)

        ax.text(x+w/2, y+l/2, fix_ar(r['space']), ha='center', va='center', fontweight='bold', fontsize=12, color='#111')

    doors = [([9, 11], [0, 0]), ([8, 8], [3, 5]), ([12, 12], [2, 4])]
    for dx, dy in doors:
        ax.plot(dx, dy, color=floor_main, lw=5)
        
    ax.arrow(24, 2, 0, 3, head_width=0.8, fc='#E74C3C', ec='#E74C3C', width=0.15)
    ax.text(24, 1, fix_ar("الشمال"), ha='center', color='#E74C3C', fontweight='bold', fontsize=12)

    ax.set_xlim(-2, 28); ax.set_ylim(-3, 22); ax.axis('off')
    return fig

# ==========================================
# 🌟 2. المحرك البصري 3D 🌟
# ==========================================
def create_box_plotly(x, y, z, w, l, h, color, opacity=1.0):
    x_pts = [x, x+w, x+w, x, x, x+w, x+w, x]; y_pts = [y, y, y+l, y+l, y, y, y+l, y+l]; z_pts = [z, z, z, z, z+h, z+h, z+h, z+h]
    i = [0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1]; j = [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 2, 6]; k = [2, 3, 6, 7, 5, 4, 6, 7, 7, 4, 6, 5]
    mesh = go.Mesh3d(x=x_pts, y=y_pts, z=z_pts, i=i, j=j, k=k, color=color, opacity=opacity, flatshading=True, hoverinfo='skip')
    ex = [x, x+w, x+w, x, x, None, x, x+w, x+w, x, x, None, x, x, None, x+w, x+w, None, x+w, x+w, None, x, x]; ey = [y, y, y+l, y+l, y, None, y, y, y+l, y+l, y, None, y, y, None, y, y, None, y+l, y+l, None, y+l, y+l]; ez = [z, z, z, z, z, None, z+h, z+h, z+h, z+h, z+h, None, z, z+h, None, z, z+h, None, z, z+h, None, z, z+h]
    lines = go.Scatter3d(x=ex, y=ey, z=ez, mode='lines', line=dict(color='#BDC3C7', width=1.5), showlegend=False, hoverinfo='skip')
    return [mesh, lines]

def generate_3d_model(rooms_data, floor_type='all', is_green=False, prefs=None):
    if prefs is None: prefs = {}
    wall_col, floor_main, floor_wet, frame_col = get_theme_colors(prefs)
    fig = go.Figure()
    
    fig.add_trace(create_box_plotly(-2, -4, -0.4, 24, 26, 0.4, '#FDFEFE', 1.0)[0])
    
    floors_to_draw = []
    if floor_type in ['all', 'ground']: floors_to_draw.append(('ground', 0.0))
    if floor_type in ['all', 'first']:  floors_to_draw.append(('first', 3.6))

    room_counter = 1
    room_legend = {} 

    for f_name, z_offset in floors_to_draw:
        mapped = layout_ground_floor(rooms_data) if f_name == 'ground' else layout_first_floor(rooms_data)
        h = 3.4
        for r in mapped:
            x, y, w, l = r['x'], r['y'], r['w'], r['l']
            blk = create_box_plotly(x, y, z_offset, w, l, h, wall_col, 0.95)
            fig.add_trace(blk[0]); fig.add_trace(blk[1])
            
            room_name = fix_ar(r['space'], for_plotly=True)
            fig.add_trace(go.Scatter3d(
                x=[x + w/2], y=[y + l/2], z=[z_offset + h + 0.8],
                mode='markers+text', text=[str(room_counter)],
                marker=dict(size=22, color='#2C3E50', symbol='circle'), 
                hoverinfo='text', hovertext=[room_name], showlegend=False
            ))
            room_legend[room_counter] = room_name
            room_counter += 1

    annotations = [dict(x=1.1, y=0.95, xref='paper', yref='paper', text="<b>دليل الفراغات</b>", showarrow=False, xanchor='right', font=dict(size=14))]
    y_pos = 0.90
    for num, name in room_legend.items():
        annotations.append(dict(x=1.1, y=y_pos, xref='paper', yref='paper', text=f"<b>{num}</b> - {name}", showarrow=False, xanchor='right'))
        y_pos -= 0.05 

    fig.update_layout(showlegend=False, annotations=annotations, scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode='data'), paper_bgcolor='#FFFFFF')
    return fig
