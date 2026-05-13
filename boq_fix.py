

import io, pandas as pd

def generate_boq_excel(area, is_green, finish_lvl, tot_cost, base_cst, curr):
    concrete_vol = area * 0.45
    steel_weight = concrete_vol * 120

    boq_df = pd.DataFrame({
        "البند": [
            "أعمال الحفر والردم (م3)",
            "الخرسانة المسلحة للهيكل (م3)",
            "حديد التسليح (كجم)",
            "أعمال الطابوق (م2)",
            "أعمال المساح (م2)",
            "الأرضيات والرخام (م2)",
            "نظام التكييف المركزي (طن)",
        ],
        "الكمية التقديرية": [
            round(area * 1.2, 1),
            round(concrete_vol, 1),
            round(steel_weight, 1),
            round(area * 1.5, 1),
            round(area * 2.8, 1),
            round(area * 0.9, 1),
            round(area / 15, 1),
        ],
        "ملاحظات": [
            "حسب تقرير فحص التربة",
            "خرسانة خضراء" if is_green else "خرسانة بورتلاندية عادية",
            "حديد عالي الشد",
            "طابوق أبيض عازل",
            "مساح داخلي وخارجي",
            f"تشطيب {finish_lvl}",
            "وحدات VRF موفرة للطاقة" if is_green else "نظام Package أو DX",
        ],
    })

    budget_df = pd.DataFrame({
        "البند": [
            "التكلفة التقديرية الإجمالية",
            "تكلفة الاستدامة المضافة (LEED/WELL)",
        ],
        f"القيمة ({curr})": [
            f"{tot_cost:,.0f}",
            f"{(tot_cost - base_cst):,.0f}" if is_green else "0",
        ],
    })

    output = io.BytesIO()

   
    for engine in ("openpyxl", "xlsxwriter"):
        try:
            with pd.ExcelWriter(output, engine=engine) as writer:
                boq_df.to_excel(writer, sheet_name="جدول الكميات (BOQ)", index=False)
                budget_df.to_excel(writer, sheet_name="خلاصة الميزانية", index=False)
            output.seek(0)
            return output.getvalue(), "xlsx"
        except ImportError:
            output = io.BytesIO()  
            continue


    combined = pd.concat([boq_df, pd.DataFrame([{}]), budget_df], ignore_index=True)
    csv_bytes = combined.to_csv(index=False).encode("utf-8-sig")
    return csv_bytes, "csv"




"""
excel_data, fmt = generate_boq_excel(
    st.session_state['area'],
    st.session_state['is_green'],
    finish_level,
    total_cost,
    base_cost,
    currency
)

if fmt == "xlsx":
    st.download_button(
        label=f"📊 تحميل جدول الكميات والميزانية ({currency})",
        data=excel_data,
        file_name=f"Malath_BOQ.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
else:
    st.warning("⚠️ openpyxl و xlsxwriter غير متوفرَين — تحميل CSV بدلاً منه.")
    st.download_button(
        label=f"📄 تحميل جدول الكميات (CSV)",
        data=excel_data,
        file_name=f"Malath_BOQ.csv",
        mime="text/csv",
        use_container_width=True,
    )
"""
