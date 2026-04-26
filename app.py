import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

st.set_page_config(page_title="Consulta de Rúbrica", page_icon="📋", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f7f9fc; }
    label { font-weight: 600 !important; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

EXCEL_FILE = "datos.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_FILE, header=None, dtype=str)

try:
    df = load_data()
except FileNotFoundError:
    st.error(f"⚠️ No se encontró el archivo **{EXCEL_FILE}**.")
    st.stop()

ROW_RUTS     = 0
ROW_NOTA     = 4
ROW_PUNTAJE  = 5
RUBRIC_START = 6
RUBRIC_END   = 63
COL_DATA_START = 3

rut_row = df.iloc[ROW_RUTS, COL_DATA_START:25]

# Group rows by criterion: [{name, rows: [{desc, ptje_max, row_idx}]}]
def build_criteria():
    criteria = []
    current = None
    for i in range(RUBRIC_START, RUBRIC_END):
        a = str(df.iloc[i, 0]).strip()
        b = str(df.iloc[i, 1]).strip()
        c = str(df.iloc[i, 2]).strip()
        if a not in ("nan", "") :
            current = {"name": a, "rows": []}
            criteria.append(current)
        if current is not None:
            desc     = "" if b == "nan" else b
            ptje_max = "" if c == "nan" else c
            current["rows"].append({"desc": desc, "ptje_max": ptje_max, "row_idx": i})
    return criteria

criteria = build_criteria()

st.markdown("## 📋 Consulta de Rúbrica de Evaluación")
st.markdown("Ingresa tu RUT para ver tu evaluación.")

rut_input = st.text_input(
    "RUT (sin puntos, con guion — ej: 12345678-9)",
    placeholder="12345678-9",
    max_chars=12,
).strip()

if rut_input:
    rut_clean = rut_input.replace(".", "").upper()

    match_col = None
    for idx, val in rut_row.items():
        if str(val).replace(".", "").upper().strip() == rut_clean:
            match_col = idx
            break

    if match_col is None:
        st.error("❌ RUT no encontrado. Verifica que esté bien escrito.")
    else:
        nota    = str(df.iloc[ROW_NOTA, match_col]).strip()
        puntaje = str(df.iloc[ROW_PUNTAJE, match_col]).strip()
        if nota    == "nan": nota    = "—"
        if puntaje == "nan": puntaje = "—"

        st.success("✅ RUT encontrado. Aquí está tu evaluación:")

        table_rows = ""
        for crit in criteria:
            # Student score is in the first row of each criterion
            first_row_idx = crit["rows"][0]["row_idx"]
            ptje_est = str(df.iloc[first_row_idx, match_col]).strip()
            if ptje_est == "nan": ptje_est = ""

            n_subrows = len(crit["rows"])

            for i, row in enumerate(crit["rows"]):
                desc     = row["desc"]
                ptje_max = row["ptje_max"]

                # Highlight the row whose puntaje_max matches the student's score
                is_match = (ptje_est != "" and ptje_max == ptje_est)
                row_bg   = "#d4edda" if is_match else ("white" if i % 2 == 0 else "#f7f9fc")
                row_style = f"background:{row_bg};"
                if is_match:
                    row_style += "font-weight:bold;"

                # First sub-row: show criterion name with rowspan
                if i == 0:
                    table_rows += f"""
                    <tr style="{row_style}">
                        <td rowspan="{n_subrows}" style="font-weight:bold; padding:10px 14px;
                            border-bottom:2px solid #2d6a9f; vertical-align:middle;
                            background:#eef4fb; text-align:center;">{crit['name']}</td>
                        <td style="padding:10px 14px; border-bottom:1px solid #dde3ed;
                            vertical-align:top; word-wrap:break-word; {row_style}">{desc}</td>
                        <td style="padding:10px 14px; border-bottom:1px solid #dde3ed;
                            text-align:center; vertical-align:top; {row_style}">{ptje_max}</td>
                        <td rowspan="{n_subrows}" style="padding:10px 14px;
                            border-bottom:2px solid #2d6a9f; text-align:center;
                            vertical-align:middle; font-weight:bold; font-size:16px;
                            background:#eef4fb;">{ptje_est}</td>
                    </tr>"""
                else:
                    table_rows += f"""
                    <tr style="{row_style}">
                        <td style="padding:10px 14px; border-bottom:1px solid #dde3ed;
                            vertical-align:top; word-wrap:break-word;">{desc}</td>
                        <td style="padding:10px 14px; border-bottom:1px solid #dde3ed;
                            text-align:center; vertical-align:top;">{ptje_max}</td>
                    </tr>"""

        html = f"""
        <div style="font-family: sans-serif;">
            <div style="background:#2d6a9f; color:white; border-radius:12px; padding:14px 24px;
                        display:inline-block; font-size:1.3rem; font-weight:bold; margin-bottom:20px;">
                🎓 Nota: {nota} &nbsp;|&nbsp; Puntaje total: {puntaje}
            </div>
            <div style="background:white; border-radius:16px; padding:24px 32px;
                        box-shadow:0 4px 20px rgba(0,0,0,0.07); overflow-x:auto;">
                <table style="width:100%; border-collapse:collapse; font-size:14px;">
                    <thead>
                        <tr>
                            <th style="background:#2d6a9f; color:white; padding:10px 14px;
                                text-align:center; width:13%;">Criterio</th>
                            <th style="background:#2d6a9f; color:white; padding:10px 14px;
                                text-align:left; width:62%;">Descripción</th>
                            <th style="background:#2d6a9f; color:white; padding:10px 14px;
                                text-align:center; width:10%;">Ptje. máx.</th>
                            <th style="background:#2d6a9f; color:white; padding:10px 14px;
                                text-align:center; width:15%;">Tu puntaje</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>
        """

        components.html(html, height=1200, scrolling=True)

else:
    st.info("👆 Ingresa tu RUT para comenzar.")
