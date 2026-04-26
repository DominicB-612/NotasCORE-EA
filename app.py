import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
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
    table { border-collapse: collapse; width: 100%; font-size: 14px; }
    thead th {
        background-color: #2d6a9f;
        color: white;
        padding: 10px 14px;
        text-align: left;
        white-space: nowrap;
    }
    tbody tr:nth-child(even) td { background-color: #eef4fb; }
    tbody tr:nth-child(odd)  td { background-color: #ffffff; }
    tbody td {
        padding: 10px 14px;
        border-bottom: 1px solid #e0e0e0;
        vertical-align: top;
        white-space: normal;
        word-wrap: break-word;
    }
    .score-cell {
        font-weight: bold;
        text-align: center;
        font-size: 15px;
    }
    .nota-box {
        background: #2d6a9f;
        color: white;
        border-radius: 12px;
        padding: 1rem 2rem;
        display: inline-block;
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
EXCEL_FILE = "datos.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(EXCEL_FILE, header=None, dtype=str)

try:
    df = load_data()
except FileNotFoundError:
    st.error(f"⚠️ No se encontró el archivo **{EXCEL_FILE}**.")
    st.stop()

# ── Parse structure ───────────────────────────────────────────────────────────
# Row 0 (fila 1): RUTs en columnas D-Y (índices 3-24)
# Row 4 (fila 5): NOTA final del estudiante
# Row 5 (fila 6): PUNTAJE total del estudiante
# Rows 6-62: Rúbrica. Filas con col A != nan son criterios principales.
# Cols: A=criterio, B=descripción, C=puntaje máximo, D-Y=puntaje estudiante

ROW_RUTS   = 0
ROW_NOTA   = 4
ROW_PUNTAJE = 5
RUBRIC_START = 6
RUBRIC_END   = 63
COL_DATA_START = 3
COL_DATA_END   = 25

rut_row = df.iloc[ROW_RUTS, COL_DATA_START:COL_DATA_END]

# Criterion rows: filas donde col A tiene contenido
criterion_rows = [
    i for i in range(RUBRIC_START, RUBRIC_END)
    if str(df.iloc[i, 0]).strip() not in ("nan", "")
]

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
        nota   = df.iloc[ROW_NOTA, match_col]
        puntaje = df.iloc[ROW_PUNTAJE, match_col]

        nota_str   = nota   if str(nota)   not in ("nan", "") else "—"
        puntaje_str = puntaje if str(puntaje) not in ("nan", "") else "—"

        st.success("✅ RUT encontrado. Aquí está tu evaluación:")

        st.markdown(
            f"<div class='nota-box'>🎓 Nota: {nota_str} &nbsp;|&nbsp; Puntaje total: {puntaje_str}</div>",
            unsafe_allow_html=True,
        )

        # Build table rows
        table_rows = ""
        for r in criterion_rows:
            criterio   = str(df.iloc[r, 0]).strip()
            descripcion = str(df.iloc[r, 1]).strip()
            ptje_max   = str(df.iloc[r, 2]).strip()
            ptje_est   = str(df.iloc[r, match_col]).strip()

            if criterio   == "nan": criterio   = ""
            if descripcion == "nan": descripcion = ""
            if ptje_max   == "nan": ptje_max   = ""
            if ptje_est   == "nan": ptje_est   = ""

            # Format score as X / MAX
            score_display = f"{ptje_est} / {ptje_max}" if ptje_est else f"— / {ptje_max}"

            table_rows += f"""
            <tr>
                <td><strong>{criterio}</strong></td>
                <td>{descripcion}</td>
                <td class='score-cell'>{score_display}</td>
            </tr>
            """

        html_table = f"""
        <table>
            <thead>
                <tr>
                    <th style='width:15%'>Criterio</th>
                    <th style='width:70%'>Descripción</th>
                    <th style='width:15%'>Puntaje</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        """

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(html_table, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("👆 Ingresa tu RUT para comenzar.")
