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
criterion_rows = [
    i for i in range(RUBRIC_START, RUBRIC_END)
    if str(df.iloc[i, 0]).strip() not in ("nan", "")
]

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
        for r in criterion_rows:
            criterio    = str(df.iloc[r, 0]).strip()
            descripcion = str(df.iloc[r, 1]).strip()
            ptje_max    = str(df.iloc[r, 2]).strip()
            ptje_est    = str(df.iloc[r, match_col]).strip()

            if criterio    == "nan": criterio    = ""
            if descripcion == "nan": descripcion = ""
            if ptje_max    == "nan": ptje_max    = ""
            if ptje_est    == "nan": ptje_est    = "—"

            score_display = f"{ptje_est} / {ptje_max}" if ptje_max else ptje_est

            table_rows += f"""
            <tr>
                <td style="font-weight:bold; width:15%; padding:10px 14px; border-bottom:1px solid #dde3ed; vertical-align:top;">{criterio}</td>
                <td style="width:70%; padding:10px 14px; border-bottom:1px solid #dde3ed; vertical-align:top; white-space:normal; word-wrap:break-word;">{descripcion}</td>
                <td style="width:15%; padding:10px 14px; border-bottom:1px solid #dde3ed; vertical-align:top; text-align:center; font-weight:bold; font-size:15px;">{score_display}</td>
            </tr>"""

        html = f"""
        <div style="font-family: sans-serif;">
            <div style="background:#2d6a9f; color:white; border-radius:12px; padding:14px 24px;
                        display:inline-block; font-size:1.3rem; font-weight:bold; margin-bottom:20px;">
                🎓 Nota: {nota} &nbsp;|&nbsp; Puntaje total: {puntaje}
            </div>
            <div style="background:white; border-radius:16px; padding:24px 32px;
                        box-shadow:0 4px 20px rgba(0,0,0,0.07);">
                <table style="width:100%; border-collapse:collapse; font-size:14px;">
                    <thead>
                        <tr>
                            <th style="background:#2d6a9f; color:white; padding:10px 14px; text-align:left; width:15%;">Criterio</th>
                            <th style="background:#2d6a9f; color:white; padding:10px 14px; text-align:left; width:70%;">Descripción</th>
                            <th style="background:#2d6a9f; color:white; padding:10px 14px; text-align:center; width:15%;">Puntaje</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </div>
        """

        components.html(html, height=800, scrolling=True)

else:
    st.info("👆 Ingresa tu RUT para comenzar.")
