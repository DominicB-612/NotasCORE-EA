import streamlit as st
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Consulta de Rúbrica",
    page_icon="📋",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f7f9fc; }
    .card {
        background: white;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.07);
        margin-top: 1.5rem;
    }
    label { font-weight: 600 !important; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
EXCEL_FILE = "datos.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(EXCEL_FILE, header=None, dtype=str)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error(f"⚠️ No se encontró el archivo **{EXCEL_FILE}**.")
    st.stop()

# ── Parse structure ───────────────────────────────────────────────────────────
ROW_RUTS       = 0
ROW_DATA_START = 6
COL_COMMON     = [0, 1, 2]
COL_DATA_START = 3
COL_DATA_END   = 25

rut_row = df.iloc[ROW_RUTS, COL_DATA_START:COL_DATA_END]

label_df = df.iloc[ROW_DATA_START:, COL_COMMON].reset_index(drop=True)
label_df.columns = ["Criterio", "Descripción", "Puntaje"]

# ── UI ────────────────────────────────────────────────────────────────────────
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
        personal_data = df.iloc[ROW_DATA_START:, match_col].reset_index(drop=True)

        result = label_df.copy()
        result["Tu Evaluación"] = personal_data

        # Limpiar "nan" y "None" que vienen del dtype=str
        result = result.replace("nan", "").replace("None", "")

        # Eliminar filas donde TODAS las columnas estén vacías
        result = result[~(result == "").all(axis=1)]

        st.success("✅ RUT encontrado. Aquí está tu evaluación:")

        def df_to_html(dataframe):
            rows = ""
            for _, row in dataframe.iterrows():
                cells = "".join(
                    f"<td style='padding:10px 14px; border-bottom:1px solid #e0e0e0; "
                    f"vertical-align:top; white-space:normal; word-wrap:break-word;'>"
                    f"{row[col]}</td>"
                    for col in dataframe.columns
                )
                rows += f"<tr>{cells}</tr>"
            headers = "".join(
                f"<th style='padding:10px 14px; background:#2d6a9f; color:white; "
                f"text-align:left; white-space:nowrap;'>{col}</th>"
                for col in dataframe.columns
            )
            return (
                f"<table style='width:100%; border-collapse:collapse; font-size:14px;'>"
                f"<thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"
            )

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(df_to_html(result), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👆 Ingresa tu RUT para comenzar.")
