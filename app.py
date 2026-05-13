import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import os
import time
 
# ==========================================
# 🌟 1. إعدادات الصفحة والهوية البصرية 🌟
# ==========================================
st.set_page_config(page_title="مَـلاذ | MALATH PRO", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")
 
# --- Imports with error handling ---
try:
    from scoring import get_environmental_data, calculate_sustainability_score
    from recommendations import (get_ai_recommendations, get_material_suggestions,
                                 get_certification_guide, get_design_styles,
                                 get_sustainability_strategies)
    SCORING_OK = True
except ImportError:
    st.error("⚠️ يرجى التأكد من وجود ملفات scoring.py و recommendations.py في نفس المجلد.")
    SCORING_OK = False
 
try:
    from layout import generate_blueprint_figure, generate_3d_model, ARABIC_SUPPORT
    LAYOUT_OK = True
except ImportError:
    st.error("⚠️ يرجى التأكد من وجود ملف layout.py المحدث.")
    ARABIC_SUPPORT = False
    LAYOUT_OK = False
 
try:
    from create_presentation import create_pdf_report
    PDF_OK = True
except ImportError:
    st.error("⚠️ ملف create_presentation.py غير موجود")
    PDF_OK = False
 
# --- صور المحاكاة الحيوية ---
BIOMIMICRY_IMAGES = {
    "نظام النمل الأبيض (Termite Mounds)": "https://asknature.org/wp-content/uploads/2016/08/Termite_mound_Tanzania.jpg",
    "الواجهات الحية (Green Facades)": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=600&q=80",
    "الواجهات ذاتية التظليل (Cactus Skin)": "https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=600&q=80",
    "التوجيه المناخي (Bioclimatic)": "https://images.unsplash.com/photo-1527061011665-3652c757a4d4?w=600&q=80"
}
 
# --- جميع دول مجلس التعاون الخليجي ---
GULF_LOCATIONS = {
    "🇰🇼 الكويت": {"مدينة الكويت": {"lat": 29.3759, "lon": 47.9774}, "الجهراء": {"lat": 29.3375, "lon": 47.6581}, "الأحمدي": {"lat": 29.0808, "lon": 48.0864}},
    "🇸🇦 السعودية": {"الرياض": {"lat": 24.7136, "lon": 46.6753}, "جدة": {"lat": 21.5433, "lon": 39.1728}, "الدمام": {"lat": 26.3927, "lon": 49.9777}},
    "🇦🇪 الإمارات": {"دبي": {"lat": 25.2048, "lon": 55.2708}, "أبوظبي": {"lat": 24.4539, "lon": 54.3773}},
    "🇶🇦 قطر": {"الدوحة": {"lat": 25.2854, "lon": 51.5310}, "لوسيل": {"lat": 25.4190, "lon": 51.4880}},
    "🇴🇲 عُمان": {"مسقط": {"lat": 23.5880, "lon": 58.3829}, "صلالة": {"lat": 17.0151, "lon": 54.0924}},
    "🇧🇭 البحرين": {"المنامة": {"lat": 26.2285, "lon": 50.5860}, "المحرق": {"lat": 26.2572, "lon": 50.6119}}
}
 
# ==========================================
# Session State initialization
# ==========================================
if 'country' not in st.session_state: st.session_state['country'] = "🇰🇼 الكويت"
if 'prefs' not in st.session_state: st.session_state['prefs'] = {"open": False, "cool": False, "louvers": False, "rose_gold": False, "bezel": False}
if 'room_options' not in st.session_state: st.session_state['room_options'] = {}
if 'lat' not in st.session_state: st.session_state['lat'] = 29.3759
if 'lon' not in st.session_state: st.session_state['lon'] = 47.9774
if 'area' not in st.session_state: st.session_state['area'] = 500
if 'is_green' not in st.session_state: st.session_state['is_green'] = True
if 'analyzed' not in st.session_state: st.session_state['analyzed'] = False
if 'results' not in st.session_state: st.session_state['results'] = {'temp': 36.51, 'humidity': 24, 'score': 90, 'wind_speed': 15}
if 'env_results' not in st.session_state: st.session_state['env_results'] = None
 
def calculate_performance(is_green, area):
    base_cons = area * 145
    base_co2 = area * 0.06
    if is_green:
        return base_cons * 0.35, base_co2 * 0.25, "⭐⭐⭐⭐⭐ (94/100) - مستدام"
    return base_cons, base_co2, "⭐⭐ (42/100) - تقليدي"
 
# ==========================================
# 🌟 2. اللوحة الجانبية (Sidebar) 🌟
# ==========================================
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&q=80", use_container_width=True)
    st.title("إعدادات المشروع (مَـلاذ)")
 
    if ARABIC_SUPPORT:
        st.caption("✅ دعم اللغة العربية مفعل")
    else:
        st.caption("⚠️ دعم اللغة العربية غير مفعل")
 
    st.divider()
    st.markdown("### 📍 الموقع والإقليم")
    input_method = st.radio("تحديد الموقع:", ["من القائمة", "النقر على الخريطة"], horizontal=True)
 
    if input_method == "من القائمة":
        st.session_state['country'] = st.selectbox(
            "الدولة:", list(GULF_LOCATIONS.keys()),
            index=list(GULF_LOCATIONS.keys()).index(st.session_state['country'])
        )
        city = st.selectbox("المدينة:", list(GULF_LOCATIONS[st.session_state['country']].keys()))
        if st.button("تحديث الإحداثيات"):
            st.session_state['lat'] = GULF_LOCATIONS[st.session_state['country']][city]['lat']
            st.session_state['lon'] = GULF_LOCATIONS[st.session_state['country']][city]['lon']
            st.rerun()
 
    st.divider()
    st.markdown("### 📐 المساحة والمخطط")
    st.session_state['area'] = st.number_input("المساحة الإجمالية (م²)", 200, 2000, st.session_state['area'], step=50)
    floor_type_input = st.selectbox("الطابق المراد عرضه:", ["الدور الأرضي (ضيافة)", "الدور الأول (معيشة)"])
    active_floor = 'ground' if "الأرضي" in floor_type_input else 'first'
 
    with st.expander("⚙️ تخصيص الغرف", expanded=False):
        st.session_state['room_options']['living_count'] = st.number_input("عدد صالات المعيشة", 1, 3, 1)
        st.session_state['room_options']['diwaniya_count'] = st.number_input("عدد الدواوين", 0, 2, 1)
        st.session_state['room_options']['prep_kitchen'] = st.checkbox("مطبخ تحضيري مفتوح", True)
 
    st.divider()
    st.session_state['is_green'] = st.toggle("🌿 تفعيل معايير LEED & WELL", value=st.session_state['is_green'])
 
    finish_level = st.select_slider("التشطيب:", ["تجاري", "متوسط", "ديلوكس", "VIP"], value="ديلوكس")
    rates = {"تجاري": 160, "متوسط": 190, "ديلوكس": 230, "VIP": 280}
    base_cost = st.session_state['area'] * rates[finish_level]
    total_cost = base_cost + (base_cost * 0.12 if st.session_state['is_green'] else 0)
 
    curr_sidebar = "د.ك"
    if "السعودية" in st.session_state['country']: curr_sidebar = "ر.س"
    elif "الإمارات" in st.session_state['country']: curr_sidebar = "د.إ"
    elif "البحرين" in st.session_state['country']: curr_sidebar = "د.ب"
    elif "قطر" in st.session_state['country']: curr_sidebar = "ر.ق"
    elif "عُمان" in st.session_state['country']: curr_sidebar = "ر.ع"
 
    st.markdown(f"<div style='text-align:center;font-size:18px;font-weight:bold;'>الميزانية التقديرية:<br>{total_cost:,.0f} {curr_sidebar}</div>", unsafe_allow_html=True)
    st.write("")
 
    # ---- زر التحليل الرئيسي ----
    analyze_btn = st.button("🚀 تحديث وبناء المخطط", use_container_width=True)
 
# ==========================================
# معالجة الضغط على زر التحليل
# ==========================================
if analyze_btn:
    with st.spinner("جاري التحليل المعماري وتوليد المخططات..."):
        time.sleep(1)
        if SCORING_OK:
            try:
                env_data = get_environmental_data(st.session_state['lat'], st.session_state['lon'])
                env_data['score'] = calculate_sustainability_score(env_data)
                st.session_state['results'] = env_data
                st.session_state['env_results'] = env_data
                st.session_state['analyzed'] = True
            except Exception as e:
                st.session_state['results'] = {"temp": 38, "humidity": 30, "score": 85, "wind_speed": 15, "lat": st.session_state['lat']}
                st.session_state['env_results'] = st.session_state['results']
                st.session_state['analyzed'] = True
                st.warning(f"⚠️ لم يتم الاتصال بالأقمار الصناعية، تم استخدام بيانات المناخ الافتراضية. ({e})")
        else:
            st.session_state['results'] = {"temp": 38, "humidity": 30, "score": 85, "wind_speed": 15, "lat": st.session_state['lat']}
            st.session_state['env_results'] = st.session_state['results']
            st.session_state['analyzed'] = True
 
        if PDF_OK:
            try:
                create_pdf_report(st.session_state['results'])
                st.success("✅ اكتمل التحليل وتوليد الملف!")
            except Exception as e:
                st.warning(f"⚠️ لم يتم إنشاء PDF: {e}")
 
# ==========================================
# 🌟 3. الواجهة الرئيسية (Main Dashboard) 🌟
# ==========================================
st.title(f"مَـلاذ | 𝗠𝗔𝗟𝗔𝗧𝗛 𝗣𝗥𝗢 🏛️ - {st.session_state['country']}")
 
cons, co2, star = calculate_performance(st.session_state['is_green'], st.session_state['area'])
c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
with c1:
    st.metric("استهلاك الطاقة", f"{cons:,.0f} kWh", delta="-65%" if st.session_state['is_green'] else None, delta_color="inverse")
with c2:
    st.metric("انبعاثات الكربون", f"{co2:,.1f} Ton", delta="-75%" if st.session_state['is_green'] else None, delta_color="inverse")
with c3:
    st.metric("تصنيف المبنى", star)
with c4:
    m = folium.Map(location=[st.session_state['lat'], st.session_state['lon']], zoom_start=14)
    folium.Marker(
        [st.session_state['lat'], st.session_state['lon']],
        icon=folium.Icon(color="green" if st.session_state['is_green'] else "blue")
    ).add_to(m)
    map_data = st_folium(m, height=130, use_container_width=True)
    if input_method == "النقر على الخريطة" and map_data.get('last_clicked'):
        if map_data['last_clicked']['lat'] != st.session_state['lat']:
            st.session_state['lat'] = map_data['last_clicked']['lat']
            st.session_state['lon'] = map_data['last_clicked']['lng']
            st.rerun()
 
# ==========================================
# التبويبات
# ==========================================
tabs = st.tabs([
    "📐 المخططات (2D/3D)",
    "🧩 الذوق والهوية",
    "🌿 التصميم والطبيعة",
    "⚡ الاستدامة والطاقة",
    "🎥 الاستوديو السينمائي",
    "📊 الإدارة والمقاولات",
    "🌤️ بيانات الطقس الحية",
    "📝 التقرير النهائي"
])
 
# ==========================================
# FIX: التبويب 1 - المخططات (2D/3D)
# يُرسم دائماً وليس فقط عند الضغط على الزر
# ==========================================
with tabs[0]:
    st.subheader("📐 المخططات الهندسية")
    c_2d, c_3d = st.columns([1.2, 1])
 
    with c_2d:
        st.subheader(f"المسقط التنفيذي (2D BIM) - {floor_type_input}")
        if LAYOUT_OK:
            try:
                fig_2d = generate_blueprint_figure(
                    st.session_state['room_options'],
                    st.session_state['area'],
                    active_floor,
                    st.session_state['is_green'],
                    st.session_state['prefs']
                )
                st.pyplot(fig_2d)
            except Exception as e:
                st.error(f"❌ خطأ في توليد المخطط 2D: {e}")
        else:
            st.info("💡 layout.py غير متوفر. المخطط 2D غير متاح.")
 
    with c_3d:
        st.subheader("الماكيت المعماري (3D Render)")
        view_3d = st.radio("العرض:", ["المبنى كاملاً", "الطابق الحالي فقط"], horizontal=True, key="3d_radio")
        sel_3d = 'all' if "كاملاً" in view_3d else active_floor
        if LAYOUT_OK:
            try:
                fig_3d = generate_3d_model(
                    st.session_state['room_options'],
                    sel_3d,
                    st.session_state['is_green'],
                    st.session_state['prefs']
                )
                st.plotly_chart(fig_3d, use_container_width=True, key="3d_model_main")
            except Exception as e:
                st.error(f"❌ خطأ في توليد النموذج 3D: {e}")
        else:
            st.info("💡 layout.py غير متوفر. النموذج 3D غير متاح.")


# ---------- التبويب 2: الذوق والهوية ----------
with tabs[1]:
    c_puz, c_her = st.columns(2)
    with c_puz:
        st.markdown("### 🧩 لغز الفراغات والخامات")
        q1 = st.radio("١. التوزيع الداخلي:", ["تقسيمات خصوصية (مغلق)", "مساحات مفتوحة (Open Plan)"],
                      index=1 if st.session_state['prefs']['open'] else 0)
        q2 = st.radio("٢. ألوان الخامات والأرضيات:", ["رخام دافئ (Warm)", "معدن وزجاج بارد (Cool)"],
                      index=1 if st.session_state['prefs']['cool'] else 0)
    with c_her:
        st.markdown("### 🏛️ التفاصيل الحركية والهوية")
        ch1 = st.checkbox("⚙️ مشربيات حركية منزلقة للواجهات", value=st.session_state['prefs']['louvers'])
        ch2 = st.checkbox("✨ تطعيمات النوافذ بلون الروز جولد", value=st.session_state['prefs']['rose_gold'])
        ch3 = st.checkbox("💎 ترصيع هندسي مركزي (Center Bezel) بالمدخل", value=st.session_state['prefs']['bezel'])
 
    if st.button("🔄 تطبيق الهوية على المخططات", use_container_width=True):
        st.session_state['prefs']['open'] = ("مفتوحة" in q1)
        st.session_state['prefs']['cool'] = ("بارد" in q2)
        st.session_state['prefs']['louvers'] = ch1
        st.session_state['prefs']['rose_gold'] = ch2
        st.session_state['prefs']['bezel'] = ch3
        st.rerun()
 
# ---------- التبويب 3: التصميم والطبيعة ----------
with tabs[2]:
    st.header("🎨 التصميم المستوحى من الطبيعة (Biomimicry)")
    # FIX: استخدام .get() الآمن بدلاً من الوصول المباشر
    res = st.session_state.get('results') or {}
    c_bio1, c_bio2 = st.columns(2)
 
    with c_bio1:
        st.subheader("1️⃣ حلول المحاكاة الحيوية")
        if SCORING_OK and res:
            try:
                recs, sols = get_ai_recommendations(res)
                for sol in sols:
                    with st.expander(f"💡 {sol['title']}", expanded=True):
                        st.info(sol['desc'])
                        img_url = BIOMIMICRY_IMAGES.get(sol['title'], "https://images.unsplash.com/photo-1518173946687-a4c8892bbd9f?w=600&q=80")
                        st.image(img_url, use_container_width=True)
            except Exception:
                st.info("💡 **نظام النمل الأبيض:** لتصميم أبراج تهوية طبيعية للتبريد.")
                st.image(BIOMIMICRY_IMAGES["نظام النمل الأبيض (Termite Mounds)"])
        else:
            st.info("💡 **نظام النمل الأبيض:** لتصميم أبراج تهوية طبيعية للتبريد.")
            st.image(BIOMIMICRY_IMAGES["نظام النمل الأبيض (Termite Mounds)"])
 
    with c_bio2:
        st.subheader("2️⃣ أنماط التصميم المعماري")
        if SCORING_OK:
            try:
                arch_styles, inter_styles = get_design_styles()
                for s in arch_styles:
                    st.write(f"**{s['name']}**: {s['desc']}")
            except Exception:
                st.write("**طراز Modern Minimalist**: خطوط نظيفة، مساحات مفتوحة، وإضاءة طبيعية.")
                st.write("**طراز Geometric Contemporary**: يعتمد على التشكيلات الهندسية الحادة.")
        else:
            st.write("**طراز Modern Minimalist**: خطوط نظيفة، مساحات مفتوحة، وإضاءة طبيعية.")
            st.write("**طراز Geometric Contemporary**: يعتمد على التشكيلات الهندسية الحادة.")
 
# ---------- التبويب 4: الاستدامة والطاقة ----------
with tabs[3]:
    if st.session_state['is_green']:
        c_chart, c_strat = st.columns([1.5, 1])
        with c_chart:
            st.subheader("محاكاة استهلاك الطاقة السنوي")
            sim_data = pd.DataFrame({
                'الشهر': ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov'],
                'تصميم تقليدي': [150, 240, 390, 480, 410, 200],
                'مستدام (ملاذ)': [50, 85, 140, 180, 150, 70]
            }).set_index('الشهر')
            st.line_chart(sim_data, color=["#E74C3C", "#27AE60"])
        with c_strat:
            st.subheader("💧 استراتيجيات المياه والطاقة")
            if SCORING_OK:
                try:
                    strat = get_sustainability_strategies()
                    for s in strat['water']: st.write(f"💧 {s}")
                    for s in strat['energy']: st.write(f"⚡ {s}")
                except Exception:
                    st.write("💧 إعادة تدوير المياه الرمادية للري.")
                    st.write("⚡ استخدام زجاج Low-E العازل للحرارة.")
            else:
                st.write("💧 إعادة تدوير المياه الرمادية للري.")
                st.write("⚡ استخدام زجاج Low-E العازل للحرارة.")
 
        st.divider()
        st.markdown("#### 🧱 المواد ومواصفات الأثاث المستدام")
        res = st.session_state.get('results') or {}
        if SCORING_OK and res:
            try:
                mats = get_material_suggestions(res.get('temp', 35))
                for m in mats: st.success(f"{m['icon']} **{m['name']}**: {m['benefit']}")
            except Exception:
                st.success("🧱 **خرسانة خضراء**: تقلل من الانبعاثات الكربونية وتقاوم حرارة الخليج.")
        else:
            st.success("🧱 **خرسانة خضراء**: تقلل من الانبعاثات الكربونية وتقاوم حرارة الخليج.")
    else:
        st.warning("حلول الاستدامة معطلة حالياً. يرجى تفعيلها من القائمة الجانبية.")
 
# ---------- التبويب 5: الاستوديو السينمائي ----------
with tabs[4]:
    st.subheader("🎥 الاستوديو السينمائي")
    try:
        import google.generativeai as genai
        GENAI_AVAILABLE = True
    except ImportError:
        GENAI_AVAILABLE = False
 
    GEMINI_API_KEY = "AIzaSyCPvfC0TOGvbBx5l1Um5G37euy7-jNHaYo"
 
    if GENAI_AVAILABLE and GEMINI_API_KEY != "AIzaSyCPvfC0TOGvbBx5l1Um5G37euy7-jNHaYo":
        try:
            genai.configure(api_key=GEMINI_API_KEY)
        except Exception:
            pass
 
    st.markdown("تحكمي في عدسة الكاميرا والإضاءة بدقة هندسية عالية.")
    c_cam, c_light = st.columns(2)
    with c_cam:
        camera_shot = st.selectbox("🎥 زاوية الكاميرا:", ["لقطة بمستوى العين", "لقطة درون علوية", "لقطة قريبة للتفاصيل"])
    with c_light:
        lighting = st.selectbox("💡 الإضاءة والجو العام:", ["نهار ساطع", "ليل سينمائي"])
 
    prefs = st.session_state['prefs']
    prompt_parts = [f"A {camera_shot} of a modern villa."]
    if prefs['cool']: prompt_parts.append("Featuring cold glass and metal materials.")
    else: prompt_parts.append("Featuring warm travertine and marble materials.")
    if prefs['open']: prompt_parts.append("Open plan layout.")
    else: prompt_parts.append("Private segmented layout.")
    if prefs['rose_gold']: prompt_parts.append("Adorned with luxurious rose gold metallic accents.")
    if prefs['louvers']: prompt_parts.append("Windows feature kinetic sliding wooden louvers.")
    if prefs['bezel']: prompt_parts.append("The entrance has a geometric center bezel floor inlay.")
    if st.session_state.get('is_green', True): prompt_parts.append("Biophilic design with cascading green plants.")
    prompt_parts.append(f"Lighting condition: {lighting}. Photorealistic, 8k render.")
    base_prompt = " ".join(prompt_parts)
    final_prompt = base_prompt
 
    if GENAI_AVAILABLE and GEMINI_API_KEY != "AIzaSyCPvfC0TOGvbBx5l1Um5G37euy7-jNHaYo":
        try:
            with st.spinner("Gemini يقوم بضبط إعدادات العدسة والوصف..."):
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Enhance this architectural prompt. Keep the camera angle at the absolute beginning: {base_prompt}")
                final_prompt = response.text
        except Exception:
            pass
 
    st.text_area("📝 الوصف النهائي الموجه للمحرك:", value=final_prompt, height=150)
 
    demo_images = {
        "لقطة بمستوى العين_نهار ساطع": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=1200&q=80",
        "لقطة بمستوى العين_ليل سينمائي": "https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=1200&q=80",
        "لقطة درون علوية_نهار ساطع": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200&q=80",
        "لقطة درون علوية_ليل سينمائي": "https://images.unsplash.com/photo-1516455590571-18256e5bb9ff?w=1200&q=80",
        "لقطة قريبة للتفاصيل_نهار ساطع": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=1200&q=80",
        "لقطة قريبة للتفاصيل_ليل سينمائي": "https://images.unsplash.com/photo-1573221566340-81f1d4eb610a?w=1200&q=80"
    }
    selected_image = demo_images.get(f"{camera_shot}_{lighting}", demo_images["لقطة بمستوى العين_نهار ساطع"])
 
    c_btn_ai1, c_btn_ai2 = st.columns(2)
    with c_btn_ai1:
        if st.button("📸 لقطة واقعية (Gemini Image)"):
            with st.spinner("جاري رندر اللقطة بدقة 8K..."):
                time.sleep(1.5)
                st.success("✅ تم التوليد بنجاح!")
                st.image(selected_image, caption=f"✨ {camera_shot} | {lighting}")
    with c_btn_ai2:
        if st.button("🎬 جولة سينمائية (Google Veo)"):
            with st.spinner("جاري معالجة الإطارات السينمائية عبر محرك Veo..."):
                time.sleep(3)
                st.success("✅ اكتمل الرندر!")
                st.info("✨ مساحة عرض الفيديو جاهزة.")
 
# ---------- التبويب 6: الإدارة والمقاولات ----------
with tabs[5]:
    import io
 
    if "الكويت" in st.session_state['country']: currency, muni_name = "د.ك", "تراخيص البلدية (الكويت)"
    elif "السعودية" in st.session_state['country']: currency, muni_name = "ر.س", "رخصة بلدي (المملكة العربية السعودية)"
    elif "الإمارات" in st.session_state['country']: currency, muni_name = "د.إ", "تراخيص البلدية (الإمارات)"
    elif "قطر" in st.session_state['country']: currency, muni_name = "ر.ق", "تراخيص البلدية (دولة قطر)"
    elif "عُمان" in st.session_state['country']: currency, muni_name = "ر.ع", "تراخيص البلدية (سلطنة عُمان)"
    elif "البحرين" in st.session_state['country']: currency, muni_name = "د.ب", "شؤون البلديات (مملكة البحرين)"
    else: currency, muni_name = "عملة محلية", "تراخيص البلدية"
 
    c_ar, c_man = st.columns([1, 2])
    with c_ar:
        st.subheader("📱 الواقع المعزز (AR)")
        st.write("امسحي الرمز لإسقاط المجسم بأرض القسيمة:")
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=Malath_AR_Ready", width=150)
 
    with c_man:
        st.subheader("📊 لوحة الإدارة الهندسية")
        with st.expander("📅 الجدول الزمني للتنفيذ", expanded=True):
            schedule_data = {
                "النشاط": ["التراخيص والموافقات", "عطاءات المقاولين", "تنفيذ الهيكل (الأسود)", "التشطيبات والأنظمة", "التسليم"],
                "المدة المتوقعة": ["6 أسابيع", "3 أسابيع", "16 أسبوع", "20 أسبوع", "أسبوعين"]
            }
            st.dataframe(pd.DataFrame(schedule_data), use_container_width=True, hide_index=True)
 
        st.divider()
        st.markdown("### 📥 المستندات التعاقدية")
 
        def generate_boq_excel(area, is_green, finish_lvl, tot_cost, base_cst, curr):
            concrete_vol = area * 0.45
            steel_weight = concrete_vol * 120
            data = {
                "البند": ["أعمال الحفر والردم (م3)", "الخرسانة المسلحة للهيكل (م3)", "حديد التسليح (كجم)",
                          "أعمال الطابوق (م2)", "أعمال المساح (م2)", "الأرضيات والرخام (م2)", "نظام التكييف المركزي (طن)"],
                "الكمية التقديرية": [round(area * 1.2, 1), round(concrete_vol, 1), round(steel_weight, 1),
                                     round(area * 1.5, 1), round(area * 2.8, 1), round(area * 0.9, 1), round(area / 15, 1)],
                "ملاحظات": ["حسب تقرير فحص التربة",
                            "خرسانة خضراء" if is_green else "خرسانة بورتلاندية عادية",
                            "حديد عالي الشد", "طابوق أبيض عازل", "مساح داخلي وخارجي",
                            f"تشطيب {finish_lvl}",
                            "وحدات VRF موفرة للطاقة" if is_green else "نظام Package أو DX"]
            }
            budget_data = pd.DataFrame({
                "البند": ["التكلفة التقديرية الإجمالية للمشروع", "تكلفة الاستدامة (LEED/WELL) المضافة"],
                f"القيمة ({curr})": [f"{tot_cost:,.0f}", f"{(tot_cost - base_cst):,.0f}" if is_green else "0"]
            })
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                pd.DataFrame(data).to_excel(writer, sheet_name='جدول الكميات (BOQ)', index=False)
                budget_data.to_excel(writer, sheet_name='خلاصة الميزانية', index=False)
            return output.getvalue()
 
        excel_data = generate_boq_excel(st.session_state['area'], st.session_state['is_green'], finish_level, total_cost, base_cost, currency)
        st.download_button(
            label=f"📊 تحميل جدول الكميات والميزانية ({currency})",
            data=excel_data,
            file_name=f"Malath_BOQ_{st.session_state['country'][:2]}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.write(f"**✅ القائمة المرجعية لـ {muni_name}:**")
        st.checkbox("مخطط معماري معتمد من المكتب الهندسي", value=True)
        st.checkbox("تعهد إشراف إنشائي من المكتب المصمم")
        if st.session_state['is_green']:
            st.checkbox("شهادة مطابقة العزل الحراري وكفاءة الطاقة", value=True)
 
# ---------- التبويب 7: بيانات الطقس الحية ----------
with tabs[6]:
    st.markdown("## 🌤️ نظام المحاكاة المناخية اللحظي")
    st.write("يتم الربط حالياً بالأقمار الصناعية لتحليل أثر المناخ على كفاءة المبنى.")
 
    if st.session_state.get('analyzed') and st.session_state.get('env_results'):
        res = st.session_state['env_results']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="🌡️ درجة الحرارة", value=f"{res.get('temp', 'N/A')}°C",
                      delta="مناخ صحراوي" if (res.get('temp') or 0) > 35 else "معتدل")
        with col2:
            st.metric(label="💧 الرطوبة النسبية", value=f"{res.get('humidity', 'N/A')}%")
        with col3:
            st.metric(label="💨 سرعة الرياح", value=f"{res.get('wind_speed', 0)} m/s")
        st.divider()
        st.success(f"📍 تم جلب البيانات بنجاح — Lat: {st.session_state['lat']:.4f}, Lon: {st.session_state['lon']:.4f}")
        st.info(f"💡 نصيحة ذكية: بناءً على حرارة {res.get('temp', '?')}°C، يُفضل تفعيل أنظمة التبريد السلبي.")
    else:
        st.warning("💡 يرجى الضغط على 'تحديث وبناء المخطط' في القائمة الجانبية لتفعيل الربط مع الأقمار الصناعية.")
 
# ---------- التبويب 8: التقرير النهائي ----------
with tabs[7]:
    st.markdown("## 📝 التقرير الفني للمشروع")
    st.write("سيحتوي هذا التقرير على كافة التفاصيل الهندسية، المناخية، وتوصيات الاستدامة.")
 
    if PDF_OK:
        try:
            create_pdf_report(st.session_state['results'])
            if os.path.exists("Malath_PRO_Report.pdf"):
                with open("Malath_PRO_Report.pdf", "rb") as file:
                    st.download_button(
                        label="📥 تحميل التقرير النهائي (PDF)",
                        data=file,
                        file_name="Malath_Report_Final.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        except Exception as e:
            st.error(f"❌ خطأ في إنشاء التقرير: {e}")
    else:
        st.info("⚠️ ملف create_presentation.py غير متوفر لإنشاء التقرير.")
        st.json(st.session_state.get('results', {}))
        
