# recommendations.py

def get_ai_recommendations(env_data):
    temp = env_data.get('temp', 35) if env_data else 35
    humidity = env_data.get('humidity', 30) if env_data else 30
    recs, solutions = [], []

    if temp > 35 and humidity < 40:
        recs.append("⚠️ تنبيه حراري: المنطقة حارة وجافة، يُنصح بالعزل الحراري الفعال.")
        solutions.append({"title": "نظام النمل الأبيض (Termite Mounds)", "desc": "نظام تهوية طبيعي (Passive Cooling)."})
        solutions.append({"title": "الواجهات ذاتية التظليل (Cactus Skin)", "desc": "تكسية تظلل نفسها لتقليل اكتساب الحرارة."})
    elif humidity >= 40:
        recs.append("💧 تنبيه رطوبة: يُنصح بتوفير تهوية متقاطعة مستمرة لتجنب الرطوبة.")
        solutions.append({"title": "الواجهات الحية (Green Facades)", "desc": "نباتات متسلقة لتبريد الجدران وامتصاص الرطوبة."})
        solutions.append({"title": "التوجيه المناخي (Bioclimatic)", "desc": "اصطياد نسيم البحر لتجديد الهواء."})
    return recs, solutions

def get_design_styles():
    architecture_styles = [
        {"name": "التصميم البيوفيلي", "desc": "دمج الطبيعة بالإضاءة السماوية والفناء.", "image": "https://images.unsplash.com/photo-1600607686527-6fb886090705?w=600&q=80"},
        {"name": "العمارة الصحراوية الحديثة", "desc": "استلهام البيت الكويتي القديم بالحوش والليوان.", "image": "https://images.unsplash.com/photo-1512915922686-57c11dde9b6b?w=600&q=80"}
    ]
    interior_styles = [
        {"name": "أثاث الاستدامة", "desc": "أخشاب وأقمشة طبيعية خالية من الكيماويات.", "image": "https://images.unsplash.com/photo-1594026112284-02bb6f3352fe?w=600&q=80"},
        {"name": "التصميم الصحي", "desc": "مساحات تعزز الحركة والإضاءة الذكية.", "image": "https://images.unsplash.com/photo-1505693314120-0d443641f846?w=600&q=80"}
    ]
    return architecture_styles, interior_styles

def get_material_suggestions(temp):
    materials = [
        {"name": "الطابوق الجيري (AAC)", "benefit": "عزل حراري ممتاز وخفيف.", "icon": "🧱"},
        {"name": "الزجاج المزدوج (Low-E)", "benefit": "يقلل دخول الحرارة بنسبة 70%.", "icon": "🪟"}
    ]
    if temp > 35:
        materials.append({"name": "عزل الفوم (XPS)", "benefit": "ضروري جداً للأسقف والجدران.", "icon": "🛡️"})
    return materials

def get_sustainability_strategies(env_data=None):
    lat = env_data.get('lat', 29.0) if env_data else 29.0
    humidity = env_data.get('humidity', 30) if env_data else 30
    strat = {"water": ["مياه رمادية للري", "ري ذكي بالتنقيط"], "energy": ["استغلال الإضاءة الطبيعية"], "carbon": ["خرسانة خضراء"]}
    if 20 < lat < 30: strat["energy"].append("ألواح شمسية بزاوية ميلان مثالية.")
    if humidity > 40: strat["water"].append("تجميع مياه التكييف المتكثفة للري.")
    return strat

def get_certification_guide(score):
    if score >= 80: return "البلاتيني", ["طاقة شمسية كاملة", "نظام تدوير مياه متطور", "BMS ذكي"]
    elif score >= 60: return "الذهبي", ["سخانات شمسية", "عزل حراري مضاعف", "إضاءة LED ذكية"]
    else: return "الفضي", ["أجهزة موفرة للطاقة", "مرشدات استهلاك المياه", "زجاج مزدوج عازل"]

def get_room_dimensions(total_area, program, env_data=None, prefs=None):
    if prefs is None: prefs = {"open": False, "cool": False}
    is_open = prefs["open"]
    is_cool = prefs["cool"]
    
    scale = max(0.85, min(total_area / 400, 1.4))
    rooms = []
    
    # تحديد الألوان بناءً على الذوق
    c_guest = "#B0BEC5" if is_cool else "#D2B48C" 
    c_bath = "#90A4AE" if is_cool else "#A9A9A9"
    c_living = "#ECEFF1" if is_cool else "#F1FAEE" 
    c_service = "#E57373" if is_cool else "#E63946"
    c_annex = "#CFD8DC" if is_cool else "#FADBD8"
    c_master = "#546E7A" if is_cool else "#457B9D"
    c_private = "#78909C" if is_cool else "#1D3557"

    living_name = "معيشة مفتوحة" if is_open else "صالة المعيشة"
    reception_name = "استقبال مفتوح" if is_open else "استقبال"

    if program.get('floor_type') == 'ground':
        rooms.append({"space": "غرفة السائق", "w": 3.5*scale, "l": 3*scale, "zone": "Annex", "color": c_annex})
        rooms.append({"space": "حمام السائق", "w": 2*scale, "l": 1.5*scale, "zone": "Annex", "color": c_annex})
        rooms.append({"space": "مخزن خارجي", "w": 3*scale, "l": 4*scale, "zone": "Annex", "color": c_annex})

        rooms.append({"space": "ديوانية", "w": 7*scale, "l": 5*scale, "zone": "Guest", "color": c_guest})
        rooms.append({"space": "حمام ديوانية", "w": 2.5*scale, "l": 2*scale, "zone": "Guest", "color": c_bath})
        rooms.append({"space": reception_name, "w": 6*scale, "l": 5*scale, "zone": "Guest", "color": c_guest})
        rooms.append({"space": "حمام ضيوف", "w": 2.5*scale, "l": 2*scale, "zone": "Guest", "color": c_bath})

        rooms.append({"space": living_name, "w": 8*scale, "l": 6*scale, "zone": "Living", "color": c_living})
        rooms.append({"space": "المطبخ الرئيسي", "w": 5*scale, "l": 4*scale, "zone": "Service", "color": c_service})
    else:
        rooms.append({"space": "جناح الماستر", "w": 6*scale, "l": 5*scale, "zone": "Master", "color": c_master})
        rooms.append({"space": "ملابس وحمام", "w": 3*scale, "l": 5*scale, "zone": "Master", "color": c_master})
        for i in range(program.get('bedrooms', 3)):
            rooms.append({"space": f"غرفة نوم {i+1}", "w": 4.5*scale, "l": 4*scale, "zone": "Private", "color": c_private})

    return rooms
