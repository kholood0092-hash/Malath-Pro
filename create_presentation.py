"""
create_presentation.py — Malath PRO
Root cause fix: arabic_reshaper outputs FE70-FEFF presentation forms.
GeezaPro has NO FE70-FEFF glyphs → all Arabic = black boxes.
Arial Unicode MS has FE70-FEFF + ASCII digits + Latin → everything works.
"""
import os, re
from io import BytesIO

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

# ──────────────────────────────────────────────────────────────
# 🔑 WHY GeezaPro FAILS WITH arabic_reshaper
#
#  arabic_reshaper converts Arabic letters to Unicode Presentation
#  Forms (U+FE70–FEFF).  GeezaPro uses OpenType GSUB shaping —
#  it has NO pre-built FE70-FEFF glyphs → every Arabic char = ■
#
#  Arial Unicode MS has EXPLICIT FE70-FEFF glyphs AND ASCII
#  digits/Latin → arabic_reshaper output renders perfectly.
# ──────────────────────────────────────────────────────────────

# python-bidi inserts invisible directional control characters
# (U+202A LTR EMBED, U+202B RTL EMBED, U+202C POP …) around Latin
# runs inside Arabic text.  Fonts have NO glyphs for these → □ .
# Visual reordering is already done so stripping is safe.
_BIDI_STRIP = frozenset(
    '\u200e\u200f'           # LRM / RLM
    '\u202a\u202b\u202c'     # LRE / RLE / PDF
    '\u202d\u202e'            # LRO / RLO
    '\u2066\u2067\u2068\u2069'  # LRI / RLI / FSI / PDI
)


def fix_text(text):
    """Reshape Arabic + bidi reorder + strip invisible control chars."""
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(str(text))
    displayed = get_display(reshaped)
    return "".join(c for c in displayed if c not in _BIDI_STRIP)


# ──────────────────────────────────────────────────────────────
# Font resolver — Arial Unicode MS first (has FE70-FEFF + digits)
# ──────────────────────────────────────────────────────────────

def _find_font():
    """
    Returns (regular_path, bold_path).
    Tries fonts that have BOTH Arabic presentation forms AND Latin/digits.
    GeezaPro is intentionally excluded — it lacks FE70-FEFF glyphs.
    """
    candidates = [
        # macOS — Arial Unicode MS covers everything
        ("/Library/Fonts/Arial Unicode MS.ttf",                     None),
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf",    None),
        ("/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf", None),
        ("/System/Library/Assets/com_apple_MobileAsset_Font7/"
         "Arial Unicode MS.ttf",                                     None),
        # Common user-installed location
        (os.path.expanduser("~/Library/Fonts/Arial Unicode MS.ttf"), None),
        # Linux
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/opentype/unifont/unifont.otf",            None),
    ]
    for reg, bold in candidates:
        if os.path.exists(reg):
            b = bold if (bold and os.path.exists(bold)) else reg
            return reg, b
    return None, None


_REG_PATH, _BOLD_PATH = _find_font()

if _REG_PATH:
    pdfmetrics.registerFont(TTFont('AR',  _REG_PATH))
    pdfmetrics.registerFont(TTFont('ARB', _BOLD_PATH))
    _RL, _RLB = 'AR', 'ARB'
    print(f"[Malath] Font: {os.path.basename(_REG_PATH)}")
else:
    # Hard fallback — Helvetica has no Arabic but won't crash
    _RL, _RLB = 'Helvetica', 'Helvetica-Bold'
    print("[Malath] WARNING: No Arabic font found. Install Arial Unicode MS.")

_FP      = fm.FontProperties(fname=_REG_PATH)  if _REG_PATH  else fm.FontProperties()
_FP_BOLD = fm.FontProperties(fname=_BOLD_PATH) if _BOLD_PATH else fm.FontProperties()

# ──────────────────────────────────────────────────────────────
# Colours
# ──────────────────────────────────────────────────────────────
C_GREEN  = colors.HexColor('#1a6b3a')
C_LIGHT  = colors.HexColor('#e8f5e9')
C_DARK   = colors.HexColor('#1a1a2e')
C_GREY   = colors.HexColor('#7f8c8d')
C_ORANGE = colors.HexColor('#f39c12')
C_WHITE  = colors.white
C_BLACK  = colors.black

M_RED    = '#e74c3c'
M_BLUE   = '#3498db'
M_GREEN  = '#27ae60'
M_ORANGE = '#f39c12'

# ──────────────────────────────────────────────────────────────
# Paragraph styles
# Since Arial Unicode MS has digits + Latin, ALL cells can use _RL.
# Helvetica kept as 'num' for explicit pure-number formatting.
# ──────────────────────────────────────────────────────────────

def _ps(name, font, size, col, align=2, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size,
                          textColor=col, alignment=align, **kw)

S = {
    'h1':   _ps('h1',  _RLB,            16, C_GREEN, spaceBefore=10, spaceAfter=5),
    'body': _ps('bd',  _RL,             10, C_DARK,  spaceAfter=4, leading=16),
    'cell': _ps('cl',  _RL,              9, C_BLACK, wordWrap='RTL'),
    'cb':   _ps('cb',  _RLB,             9, C_DARK,  wordWrap='RTL'),
    'num':  _ps('num', 'Helvetica-Bold', 9, C_DARK),   # pure ASCII backup
}


def _TS():
    return TableStyle([
        ('BACKGROUND',     (0,0), (-1, 0), C_GREEN),
        ('TEXTCOLOR',      (0,0), (-1, 0), C_WHITE),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [C_WHITE, C_LIGHT]),
        ('BOX',            (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('INNERGRID',      (0,0), (-1,-1), 0.3, colors.lightgrey),
        ('ALIGN',          (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',     (0,0), (-1,-1), 5),
        ('BOTTOMPADDING',  (0,0), (-1,-1), 5),
    ])


def P(text, style=None):
    """Arabic Paragraph — reshapes and strips control chars."""
    return Paragraph(fix_text(str(text)), style or S['cell'])


def N(text):
    """Number/Latin Paragraph — Helvetica-Bold, no reshaping."""
    return Paragraph(str(text), S['num'])


def M(text):
    """Mixed Arabic+number Paragraph — uses full-Unicode AR font."""
    return Paragraph(fix_text(str(text)), S['cell'])


# ──────────────────────────────────────────────────────────────
# Charts
# ──────────────────────────────────────────────────────────────

def _buf(fig):
    b = BytesIO()
    fig.savefig(b, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    b.seek(0)
    return b


def _chart_kpi(temp, humidity, score, wind_speed=0):
    kpis = [
        (fix_text('معدل الاستدامة'),   f'{float(score):.0f}/100',      M_GREEN),
        (fix_text('درجة الحرارة'),     f'{float(temp):.1f}\u00b0C',    M_RED),
        (fix_text('الرطوبة النسبية'),  f'{float(humidity):.0f}%',       M_BLUE),
    ]
    if wind_speed:
        kpis.append((fix_text('سرعة الرياح'),
                     f'{float(wind_speed):.1f} m/s', M_ORANGE))
    n = len(kpis)
    fig, axes = plt.subplots(1, n, figsize=(n * 2.9, 2.4), facecolor='white')
    if n == 1: axes = [axes]
    for ax, (lbl, val, col) in zip(axes, kpis):
        ax.set_facecolor(col)
        ax.text(0.5, 0.60, val,   ha='center', va='center', fontsize=26,
                fontweight='bold', color='white', transform=ax.transAxes)
        ax.text(0.5, 0.18, lbl,   ha='center', va='center', fontsize=11,
                color='white', transform=ax.transAxes, fontproperties=_FP)
        ax.axis('off')
    fig.tight_layout(pad=0.3)
    return _buf(fig)


def _chart_energy():
    months = ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov']
    trad   = [150, 240, 390, 480, 410, 200]
    sust   = [50,   85, 140, 180, 150,  70]
    x, w   = np.arange(6), 0.35
    fig, ax = plt.subplots(figsize=(8, 3.5), facecolor='white')
    ax.bar(x-w/2, trad, w, label=fix_text('تقليدي'),        color=M_RED,   alpha=0.85)
    ax.bar(x+w/2, sust, w, label=fix_text('مستدام (ملاذ)'), color=M_GREEN, alpha=0.85)
    ax.set_xticks(x); ax.set_xticklabels(months, fontsize=10)
    ax.set_ylabel('kWh', fontsize=10)
    ax.set_title(fix_text('محاكاة استهلاك الطاقة السنوي (kWh)'),
                 fontproperties=_FP, fontsize=12, pad=10)
    ax.legend(prop=_FP, fontsize=9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.annotate(fix_text('توفير 63%'), xy=(3,180), xytext=(3.8,330),
                fontproperties=_FP, fontsize=9, color=M_GREEN,
                arrowprops=dict(arrowstyle='->', color=M_GREEN))
    fig.tight_layout()
    return _buf(fig)


def _chart_radar(score):
    cats  = [fix_text(c) for c in ['الطاقة','المياه','المواد','الموقع','جودة الهواء']]
    vals  = [float(score)*f/100 for f in (0.90,0.85,0.80,0.95,0.88)]
    N_    = len(cats)
    angles = [n/N_*2*np.pi for n in range(N_)] + [0]
    vals  += vals[:1]
    fig, ax = plt.subplots(figsize=(4.2,4.2), subplot_kw=dict(polar=True), facecolor='white')
    ax.plot(angles, vals, 'o-', linewidth=2, color=M_GREEN)
    ax.fill(angles, vals, alpha=0.20, color=M_GREEN)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(cats, fontproperties=_FP, fontsize=9)
    ax.set_ylim(0,1); ax.set_yticks([0.25,0.5,0.75,1.0])
    ax.set_yticklabels(['25','50','75','100'], fontsize=7, color='grey')
    ax.set_title(fix_text('مؤشرات الاستدامة الفرعية'),
                 fontproperties=_FP, fontsize=11, pad=18)
    ax.grid(color='gray', alpha=0.3)
    return _buf(fig)


def _chart_co2(pct):
    fig, ax = plt.subplots(figsize=(7,1.6), facecolor='white')
    ax.barh(0,100, height=0.5, color='#ecf0f1', edgecolor='none')
    ax.barh(0,pct, height=0.5, color=M_GREEN if pct>=70 else M_ORANGE, edgecolor='none')
    ax.set_xlim(0,100); ax.axis('off')
    ax.text(pct/2, 0, f'{pct}%', ha='center', va='center',
            fontsize=14, fontweight='bold', color='white')
    ax.set_title(fix_text('تقليل انبعاثات ثاني اكسيد الكربون'),
                 fontproperties=_FP, fontsize=11, pad=8)
    return _buf(fig)


# ──────────────────────────────────────────────────────────────
# Page decoration
# ──────────────────────────────────────────────────────────────

def _on_page(cv, doc):
    pw, ph = A4
    cv.setFillColor(C_GREEN)
    cv.rect(0, ph-90, pw, 90, fill=1, stroke=0)
    cv.setStrokeColor(C_ORANGE); cv.setLineWidth(2)
    cv.line(0, ph-92, pw, ph-92)
    cv.setFont(_RLB, 22); cv.setFillColor(C_WHITE)
    cv.drawRightString(pw-30, ph-42, fix_text('MALATH PRO | ملاذ'))
    cv.setFont(_RL, 11)
    cv.drawRightString(pw-30, ph-65,
                       fix_text('تقرير الاستدامة والمحاكاة المناخية اللحظية'))
    cv.setFont('Helvetica', 7); cv.setFillColor(C_GREY)
    cv.drawString(30, 18, 'MALATH PRO — Sustainable Architecture Engine')
    cv.setFont(_RL, 7)
    cv.drawRightString(pw-30, 18, fix_text('ملاذ | تقرير سري'))


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def create_pdf_report(data: dict,
                      output_path: str = 'Malath_PRO_Report.pdf'):
    if data is None: data = {}

    temp       = float(data.get('temp',       36.5))
    humidity   = float(data.get('humidity',   24))
    score      = float(data.get('score',      90))
    wind_speed = float(data.get('wind_speed', 0))
    lat        = float(data.get('lat',        29.38))
    lon        = float(data.get('lon',        47.98))
    energy_kwh = round(500 * 145 * 0.35)

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=100, bottomMargin=45,
        leftMargin=30, rightMargin=30,
    )
    W = A4[0] - 60
    story = []

    # 1 – KPI cards
    story.append(P('المؤشرات البيئية اللحظية', S['h1']))
    story.append(HRFlowable(width=W, thickness=1, color=C_LIGHT, spaceAfter=6))
    story.append(Image(_chart_kpi(temp, humidity, score, wind_speed),
                       width=W, height=W*0.24))
    story.append(Spacer(1, 10))

    # 2 – Data table  (numbers via N(), Arabic labels via P())
    rows = [
        [P('القيمة', S['cb']),           P('البيان', S['cb'])],
        [N(f'{lat:.4f} N'),              P('خط العرض',        S['cell'])],
        [N(f'{lon:.4f} E'),              P('خط الطول',        S['cell'])],
        [N(f'{temp:.1f} \u00b0C'),       P('درجة الحرارة',    S['cell'])],
        [N(f'{humidity:.0f}%'),          P('الرطوبة النسبية', S['cell'])],
        [N(f'{wind_speed:.1f} m/s'),     P('سرعة الرياح',     S['cell'])],
    ]
    t = Table(rows, colWidths=[W*0.38, W*0.62]); t.setStyle(_TS())
    story.append(t)
    story.append(Spacer(1, 14))

    # 3 – Energy + Radar
    story.append(P('تحليل الطاقة والاستدامة', S['h1']))
    story.append(HRFlowable(width=W, thickness=1, color=C_LIGHT, spaceAfter=6))
    twin = Table(
        [[Image(_chart_energy(),     width=W*0.60, height=W*0.27),
          Image(_chart_radar(score), width=W*0.37, height=W*0.27)]],
        colWidths=[W*0.62, W*0.38]
    )
    twin.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),
                               ('LEFTPADDING',(0,0),(-1,-1),0),
                               ('RIGHTPADDING',(0,0),(-1,-1),4)]))
    story.append(twin)
    story.append(Spacer(1, 8))
    story.append(Image(_chart_co2(75), width=W*0.68, height=W*0.09))
    story.append(Spacer(1, 12))

    # 4 – Performance table
    story.append(P('ملخص الاداء المعماري', S['h1']))
    story.append(HRFlowable(width=W, thickness=1, color=C_LIGHT, spaceAfter=6))
    rating = 'ممتاز' if score >= 85 else 'جيد جداً'
    perf = [
        [P('النتيجة',S['cb']),    P('مؤشر الاداء',S['cb']),                    P('التصنيف',S['cb'])],
        [N(f'{score:.0f}/100'),   M('درجة الاستدامة الاجمالية LEED'),          P(rating,S['cell'])],
        [N('65%'),                P('توفير الطاقة مقارنة بالتصميم التقليدي',S['cell']), P('ممتاز',S['cell'])],
        [N('75%'),                P('تقليل انبعاثات ثاني اكسيد الكربون',S['cell']),     P('ممتاز',S['cell'])],
        [N(f'{energy_kwh:,} kWh'),M('الاستهلاك السنوي التقديري 500 م2'),       N('—')],
        [N('LEED Gold+'),         P('شهادة الاستدامة المتوقعة',S['cell']),     P('مستهدف',S['cell'])],
    ]
    tp = Table(perf, colWidths=[W*0.22, W*0.55, W*0.23]); tp.setStyle(_TS())
    story.append(tp)
    story.append(Spacer(1, 14))

    # 5 – Recommendations
    story.append(P('التوصيات والحلول الذكية', S['h1']))
    story.append(HRFlowable(width=W, thickness=1, color=C_LIGHT, spaceAfter=6))
    recs = []
    if temp > 38:
        recs.append(('نظام التبريد التبخيري',
                     f'درجة الحرارة {temp:.1f} درجة تستوجب التبريد التبخيري (IEC).'))
    if humidity < 30:
        recs.append(('واجهات بيوميمتيك',
                     f'الرطوبة المنخفضة ({humidity:.0f}%) تستدعي واجهات محاكية لجلد الصبار.'))
    if score >= 85:
        recs.append(('شهادة LEED Gold',
                     'الاداء المرتفع يؤهل المشروع للحصول على شهادة LEED Gold.'))
    recs.append(('الالواح الشمسية',
                 'تركيب الواح شمسية 30 kW يغطي 40% من الاحتياج الكهربائي السنوي.'))
    recs.append(('اعادة تدوير المياه',
                 'نظام المياه الرمادية يوفر 35% من استهلاك مياه الري الخارجي.'))

    rec_rows = [[P('التفاصيل',S['cb']), P('التوصية',S['cb'])]]
    for ttl, dsc in recs:
        rec_rows.append([M(dsc), P(ttl, S['cb'])])   # M() for mixed Arabic+numbers
    tr = Table(rec_rows, colWidths=[W*0.70, W*0.30]); tr.setStyle(_TS())
    story.append(tr)
    story.append(Spacer(1, 12))

    # 6 – Vision
    story.append(P('رؤية المشروع', S['h1']))
    story.append(HRFlowable(width=W, thickness=1, color=C_LIGHT, spaceAfter=6))
    story.append(P(
        'تكامل الذكاء الاصطناعي مع معايير البناء المستدام لتحقيق اقصى كفاءة '
        'طاقة ممكنة مع مراعاة الهوية المعمارية الخليجية المحلية.', S['body']))

    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    print(f'[Malath] PDF saved → {output_path}')
    return output_path
