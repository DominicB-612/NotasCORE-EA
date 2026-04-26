import streamlit as st
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Consulta de Rúbrica",
    page_icon="📋",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f7f9fc; }

    /* Card container */
    .card {
        background: white;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.07);
        margin-top: 1.5rem;
    }

    /* Table header */
    thead tr th {
        background-color: #2d6a9f !important;
        color: white !important;
        font-weight: 600;
    }

    /* Alternating rows */
    tbody tr:nth-child(even) td { background-color: #eef4fb; }
    tbody tr:nth-child(odd)  td { background-color: #ffffff; }

    /* Input label */
    label { font-weight: 600 !important; }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
EXCEL_FILE = "datos.xlsx"   # <-- pon aquí el nombre de tu archivo Excel

@st.cache_data
def load_data():
    # Read without headers so we control row indexing (0-based internally)
    df = pd.read_excel(EXCEL_FILE, header=None)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error(f"⚠️ No se encontró el archivo **{EXCEL_FILE}**. "
             "Asegúrate de que esté en la misma carpeta que esta app.")
    st.stop()

# ── Parse structure ───────────────────────────────────────────────────────────
# Excel row 4  → DataFrame row index 3  (0-based)
# Excel cols D–Y → pandas columns 3–24  (0-based: D=3, Y=24)

ROW_RUTS      = 0   # fila 1 de Excel (0-based)
ROW_DATA_START = 6  # fila 7 de Excel (0-based)
COL_COMMON     = [0, 1, 2]  # columnas A, B, C (0-based)
COL_DATA_START = 3           # D (0-based)
COL_DATA_END   = 25          # Y+1 (exclusive)

# RUT row: columns D to Y
rut_row = df.iloc[ROW_RUTS, COL_DATA_START:COL_DATA_END]

# Common columns from row 7 onward
label_df = df.iloc[ROW_DATA_START:, COL_COMMON].reset_index(drop=True)
label_df.columns = ["Criterio A", "Criterio B", "Criterio C"]

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("## 📋 Consulta de Rúbrica de Evaluación")
st.markdown("Ingresa tu RUT para ver tu evaluación.")

rut_input = st.text_input(
    "RUT (sin puntos, con guion — ej: 12345678-9)",
    placeholder="12345678-9",
    max_chars=12,
).strip()

if rut_input:
    # Normalise: remove dots, uppercase K
    rut_clean = rut_input.replace(".", "").upper()

    # Find matching column
    match_col = None
    for idx, val in rut_row.items():
        if str(val).replace(".", "").upper().strip() == rut_clean:
            match_col = idx
            break

    if match_col is None:
        st.error("❌ RUT no encontrado. Verifica que esté bien escrito.")
    else:
        # Personal data: rows from row 7 onward, same column
        personal_data = df.iloc[ROW_DATA_START:, match_col].reset_index(drop=True)

        # Build display table
        result = label_df.copy()
        result["Tu Evaluación"] = personal_data

        # Remove fully empty rows
        result = result.dropna(how="all")

        st.success(f"✅ RUT encontrado. Aquí está tu evaluación:")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👆 Ingresa tu RUT para comenzar.")
