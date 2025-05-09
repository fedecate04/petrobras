# LTS LAB ANALYZER COMPLETO - Mejora estructural y visual
import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import os
import base64
from pathlib import Path

# --------------------------- CONFIGURACIÓN GENERAL --------------------------- #

st.set_page_config(page_title="LTS Lab Analyzer", layout="wide")
LOGO_PATH = "logopetrogas.png"

# --------------------------- FUNCIONES UTILITARIAS --------------------------- #

def limpiar_pdf_texto(texto):
    """Reemplaza caracteres incompatibles con codificación PDF Latin-1"""
    reemplazos = {
        "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
        "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
        "⁰": "0", "¹": "1", "²": "2", "³": "3",
        "°": " grados ", "º": "", "“": '"', "”": '"',
        "‘": "'", "’": "'", "–": "-", "—": "-", "•": "-",
        "→": "->", "←": "<-", "⇒": "=>", "≠": "!=", "≥": ">=", "≤": "<=",
        "✓": "OK", "✅": "OK", "❌": "NO"
    }
    for k, v in reemplazos.items():
        texto = texto.replace(k, v)
    return texto

# --------------------------- ESTILO VISUAL CUSTOM --------------------------- #

st.markdown("""
    <style>
        .stApp { background-color: #1e1e1e; color: white; }
        .stButton>button, .stDownloadButton>button {
            background-color: #0d6efd;
            color: white;
            border-radius: 8px;
            border: none;
        }
        input, textarea, .stTextInput, .stTextArea, .stNumberInput input {
            background-color: #2e2e2e !important;
            color: white !important;
            border: 1px solid #555 !important;
        }
        .stSelectbox div {
            background-color: #2e2e2e !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# --------------------------- LOGO EMPRESARIAL --------------------------- #

if Path(LOGO_PATH).exists():
    with open(LOGO_PATH, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(f"""
        <div style='text-align:center;'>
            <img src='data:image/png;base64,{logo_base64}' width='200'/>
        </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ No se encontró el logo 'logopetrogas.png'")

st.markdown("<h2 style='text-align:center;'>🧪 LTS Lab Analyzer</h2>", unsafe_allow_html=True)

# --------------------------- CLASE PDF PERSONALIZADA --------------------------- #

class PDF(FPDF):
    def header(self):
        if os.path.exists(LOGO_PATH):
            self.image(LOGO_PATH, 10, 8, 33)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "INFORME DE ANÁLISIS DE LABORATORIO", 0, 1, "C")
        self.set_font("Arial", "", 10)
        self.cell(0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "R")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Confidencial - Uso interno PETROGAS", 0, 0, "C")

    def add_section(self, title, content):
        self.set_font("Arial", "B", 11)
        self.cell(0, 10, title, 0, 1)
        self.set_font("Arial", "", 10)
        if isinstance(content, dict):
            for k, v in content.items():
                self.cell(0, 8, f"{k}: {v}", 0, 1)
        else:
            self.multi_cell(0, 8, str(content))
        self.ln(2)

# --------------------------- FUNCIÓN DE EXPORTACIÓN PDF --------------------------- #

def exportar_pdf(nombre, operador, explicacion, resultados, observaciones, muestreo_en, muestra_por):
    """Genera el informe PDF con todos los campos requeridos"""
    pdf = PDF()
    pdf.add_page()
    pdf.add_section("Operador", limpiar_pdf_texto(operador))
    pdf.add_section("Muestreo en", limpiar_pdf_texto(muestreo_en))
    pdf.add_section("Muestra tomada por", limpiar_pdf_texto(muestra_por))
    pdf.add_section("Explicación técnica", limpiar_pdf_texto(explicacion))
    pdf.add_section("Resultados", {k: limpiar_pdf_texto(str(v)) for k, v in resultados.items()})
    pdf.add_section("Observaciones", limpiar_pdf_texto(observaciones or "Sin observaciones."))
    output = pdf.output(dest='S').encode('latin-1', errors='ignore')
    st.download_button("⬇️ Descargar informe PDF", data=BytesIO(output), file_name=nombre, mime="application/pdf")

------------ MÓDULOS DE ANÁLISIS ---------------------------

Crear pestañas para cada análisis

modulos = [ "Gas Natural", "Gasolina Estabilizada", "MEG", "TEG", "Agua Desmineralizada", "Aminas" ] tabs = st.tabs(modulos)

Gas Natural

with tabs[0]: st.subheader("🔥 Análisis de Gas Natural") h2s = st.number_input("H₂S (ppm)", 0.0, step=0.1) co2 = st.number_input("CO₂ (%)", 0.0, step=0.1) operador = st.text_input("👤 Operador") muestreo_en = st.text_input("📍 Muestreo en") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por") obs = st.text_area("📝 Observaciones") if st.button("📊 Analizar Gas"): resultados = { "H₂S (ppm)": f"{h2s} - {'✅' if h2s <= 2.1 else '❌'}", "CO₂ (%)": f"{co2} - {'✅' if co2 <= 2.0 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Gas_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Evaluación de H₂S y CO₂.", resultados, obs, muestreo_en, muestra_por)

Gasolina Estabilizada

with tabs[1]: st.subheader("⛽ Análisis de Gasolina Estabilizada") tvr = st.number_input("TVR (psia)", 0.0, step=0.1) sales = st.number_input("Sales (mg/m²)", 0.0, step=0.1) agua = st.number_input("Agua y sedimentos (%)", 0.0, step=0.1) operador = st.text_input("👤 Operador", key="op_gasolina") muestreo_en = st.text_input("📍 Muestreo en", key="m_gasolina") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_gasolina") obs = st.text_area("📝 Observaciones", key="obs_gasolina") if st.button("📊 Analizar Gasolina"): resultados = { "TVR (psia)": f"{tvr} - {'✅' if tvr <= 12 else '❌'}", "Sales (mg/m²)": f"{sales} - {'✅' if sales <= 100 else '❌'}", "Agua y sedimentos (%)": f"{agua} - {'✅' if agua <= 1 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Gasolina_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Parámetros críticos para evitar corrosión y sobrepresión.", resultados, obs, muestreo_en, muestra_por)

MEG

with tabs[2]: st.subheader("🧪 Análisis de MEG") ph = st.number_input("pH", 0.0, 14.0, step=0.1) conc = st.number_input("Concentración (%wt)", 0.0, 100.0, step=0.1) cl = st.number_input("Cloruros (ppm)", 0.0, step=0.1) operador = st.text_input("👤 Operador", key="op_meg") muestreo_en = st.text_input("📍 Muestreo en", key="m_meg") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_meg") obs = st.text_area("📝 Observaciones", key="obs_meg") if st.button("📊 Analizar MEG"): resultados = { "pH": f"{ph} - {'✅' if 6.5 <= ph <= 8 else '❌'}", "Concentración (%wt)": f"{conc} - {'✅' if 60 <= conc <= 84 else '❌'}", "Cloruros (ppm)": f"{cl} - {'✅' if cl <= 50 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"MEG_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Control del inhibidor de formación de hidratos.", resultados, obs, muestreo_en, muestra_por)

TEG

with tabs[3]: st.subheader("🧪 Análisis de TEG") ph = st.number_input("pH", 0.0, 14.0, step=0.1, key="ph_teg") conc = st.number_input("Concentración (%wt)", 0.0, 100.0, step=0.1, key="conc_teg") cl = st.number_input("Cloruros (ppm)", 0.0, step=0.1, key="cl_teg") operador = st.text_input("👤 Operador", key="op_teg") muestreo_en = st.text_input("📍 Muestreo en", key="m_teg") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_teg") obs = st.text_area("📝 Observaciones", key="obs_teg") if st.button("📊 Analizar TEG"): resultados = { "pH": f"{ph} - {'✅' if 6.5 <= ph <= 8.5 else '❌'}", "Concentración (%wt)": f"{conc} - {'✅' if conc >= 99 else '❌'}", "Cloruros (ppm)": f"{cl} - {'✅' if cl <= 50 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"TEG_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Análisis del glicol para deshidratación.", resultados, obs, muestreo_en, muestra_por)

Agua Desmineralizada

with tabs[4]: st.subheader("💧 Análisis de Agua Desmineralizada") cl = st.number_input("Cloruros (ppm)", 0.0, step=0.1) operador = st.text_input("👤 Operador", key="op_agua") muestreo_en = st.text_input("📍 Muestreo en", key="m_agua") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_agua") obs = st.text_area("📝 Observaciones", key="obs_agua") if st.button("📊 Analizar Agua"): resultados = { "Cloruros (ppm)": f"{cl} - {'✅' if cl <= 10 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Agua_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Control de cloruros en agua desmineralizada.", resultados, obs, muestreo_en, muestra_por)

Aminas

with tabs[5]: st.subheader("☠️ Análisis de Aminas") conc = st.number_input("Concentración (%wt)", 0.0, 100.0, step=0.1) cl_amina = st.number_input("Cloruros en amina (ppm)", 0.0, step=1.0) cl_caldera = st.number_input("Cloruros en caldera (ppm)", 0.0, step=0.1) carga_pobre = st.number_input("Carga ácida amina pobre (mol/mol)", 0.0, step=0.001) carga_rica = st.number_input("Carga ácida amina rica (mol/mol)", 0.0, step=0.01) operador = st.text_input("👤 Operador", key="op_aminas") muestreo_en = st.text_input("📍 Muestreo en", key="m_aminas") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_aminas") obs = st.text_area("📝 Observaciones", key="obs_aminas") if st.button("📊 Analizar Aminas"): resultados = { "Concentración (%wt)": f"{conc} - {'✅' if 48 <= conc <= 52 else '❌'}", "Cloruros en amina": f"{cl_amina} - {'✅' if cl_amina <= 1000 else '❌'}", "Cloruros en caldera": f"{cl_caldera} - {'✅' if cl_caldera <= 10 else '❌'}", "Carga ácida pobre": f"{carga_pobre} - {'✅' if carga_pobre <= 0.025 else '❌'}", "Carga ácida rica": f"{carga_rica} - {'✅' if carga_rica <= 0.45 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Aminas_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Evaluación de solvente amínico y cargas ácidas.", resultados, obs, muestreo_en, muestra_por)

[...]  # (El código base ya está incluido anteriormente)

--------------------------- MÓDULOS DE ANÁLISIS ---------------------------

Crear pestañas para cada análisis

modulos = [ "Gas Natural", "Gasolina Estabilizada", "MEG", "TEG", "Agua Desmineralizada", "Aminas" ] tabs = st.tabs(modulos)

Gas Natural

with tabs[0]: st.subheader("🔥 Análisis de Gas Natural") h2s = st.number_input("H₂S (ppm)", 0.0, step=0.1) co2 = st.number_input("CO₂ (%)", 0.0, step=0.1) operador = st.text_input("👤 Operador") muestreo_en = st.text_input("📍 Muestreo en") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por") obs = st.text_area("📝 Observaciones") if st.button("📊 Analizar Gas"): resultados = { "H₂S (ppm)": f"{h2s} - {'✅' if h2s <= 2.1 else '❌'}", "CO₂ (%)": f"{co2} - {'✅' if co2 <= 2.0 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Gas_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Evaluación de H₂S y CO₂.", resultados, obs, muestreo_en, muestra_por)

Gasolina Estabilizada

with tabs[1]: st.subheader("⛽ Análisis de Gasolina Estabilizada") tvr = st.number_input("TVR (psia)", 0.0, step=0.1) sales = st.number_input("Sales (mg/m²)", 0.0, step=0.1) agua = st.number_input("Agua y sedimentos (%)", 0.0, step=0.1) operador = st.text_input("👤 Operador", key="op_gasolina") muestreo_en = st.text_input("📍 Muestreo en", key="m_gasolina") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_gasolina") obs = st.text_area("📝 Observaciones", key="obs_gasolina") if st.button("📊 Analizar Gasolina"): resultados = { "TVR (psia)": f"{tvr} - {'✅' if tvr <= 12 else '❌'}", "Sales (mg/m²)": f"{sales} - {'✅' if sales <= 100 else '❌'}", "Agua y sedimentos (%)": f"{agua} - {'✅' if agua <= 1 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Gasolina_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Parámetros críticos para evitar corrosión y sobrepresión.", resultados, obs, muestreo_en, muestra_por)

MEG

with tabs[2]: st.subheader("🧪 Análisis de MEG") ph = st.number_input("pH", 0.0, 14.0, step=0.1) conc = st.number_input("Concentración (%wt)", 0.0, 100.0, step=0.1) cl = st.number_input("Cloruros (ppm)", 0.0, step=0.1) operador = st.text_input("👤 Operador", key="op_meg") muestreo_en = st.text_input("📍 Muestreo en", key="m_meg") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_meg") obs = st.text_area("📝 Observaciones", key="obs_meg") if st.button("📊 Analizar MEG"): resultados = { "pH": f"{ph} - {'✅' if 6.5 <= ph <= 8 else '❌'}", "Concentración (%wt)": f"{conc} - {'✅' if 60 <= conc <= 84 else '❌'}", "Cloruros (ppm)": f"{cl} - {'✅' if cl <= 50 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"MEG_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Control del inhibidor de formación de hidratos.", resultados, obs, muestreo_en, muestra_por)

TEG

with tabs[3]: st.subheader("🧪 Análisis de TEG") ph = st.number_input("pH", 0.0, 14.0, step=0.1, key="ph_teg") conc = st.number_input("Concentración (%wt)", 0.0, 100.0, step=0.1, key="conc_teg") cl = st.number_input("Cloruros (ppm)", 0.0, step=0.1, key="cl_teg") operador = st.text_input("👤 Operador", key="op_teg") muestreo_en = st.text_input("📍 Muestreo en", key="m_teg") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_teg") obs = st.text_area("📝 Observaciones", key="obs_teg") if st.button("📊 Analizar TEG"): resultados = { "pH": f"{ph} - {'✅' if 6.5 <= ph <= 8.5 else '❌'}", "Concentración (%wt)": f"{conc} - {'✅' if conc >= 99 else '❌'}", "Cloruros (ppm)": f"{cl} - {'✅' if cl <= 50 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"TEG_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Análisis del glicol para deshidratación.", resultados, obs, muestreo_en, muestra_por)

Agua Desmineralizada

with tabs[4]: st.subheader("💧 Análisis de Agua Desmineralizada") cl = st.number_input("Cloruros (ppm)", 0.0, step=0.1) operador = st.text_input("👤 Operador", key="op_agua") muestreo_en = st.text_input("📍 Muestreo en", key="m_agua") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_agua") obs = st.text_area("📝 Observaciones", key="obs_agua") if st.button("📊 Analizar Agua"): resultados = { "Cloruros (ppm)": f"{cl} - {'✅' if cl <= 10 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Agua_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Control de cloruros en agua desmineralizada.", resultados, obs, muestreo_en, muestra_por)

Aminas

with tabs[5]: st.subheader("☠️ Análisis de Aminas") conc = st.number_input("Concentración (%wt)", 0.0, 100.0, step=0.1) cl_amina = st.number_input("Cloruros en amina (ppm)", 0.0, step=1.0) cl_caldera = st.number_input("Cloruros en caldera (ppm)", 0.0, step=0.1) carga_pobre = st.number_input("Carga ácida amina pobre (mol/mol)", 0.0, step=0.001) carga_rica = st.number_input("Carga ácida amina rica (mol/mol)", 0.0, step=0.01) operador = st.text_input("👤 Operador", key="op_aminas") muestreo_en = st.text_input("📍 Muestreo en", key="m_aminas") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_aminas") obs = st.text_area("📝 Observaciones", key="obs_aminas") if st.button("📊 Analizar Aminas"): resultados = { "Concentración (%wt)": f"{conc} - {'✅' if 48 <= conc <= 52 else '❌'}", "Cloruros en amina": f"{cl_amina} - {'✅' if cl_amina <= 1000 else '❌'}", "Cloruros en caldera": f"{cl_caldera} - {'✅' if cl_caldera <= 10 else '❌'}", "Carga ácida pobre": f"{carga_pobre} - {'✅' if carga_pobre <= 0.025 else '❌'}", "Carga ácida rica": f"{carga_rica} - {'✅' if carga_rica <= 0.45 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Aminas_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Evaluación de solvente amínico y cargas ácidas.", resultados, obs, muestreo_en, muestra_por)

[...]  # (El código base ya está incluido anteriormente)

--------------------------- MÓDULOS DE ANÁLISIS ---------------------------

Crear pestañas para cada análisis

modulos = [ "Gas Natural", "Gasolina Estabilizada", "MEG", "TEG", "Agua Desmineralizada", "Aminas" ] tabs = st.tabs(modulos)

Gas Natural

with tabs[0]: st.subheader("🔥 Análisis de Gas Natural") h2s = st.number_input("H₂S (ppm)", 0.0, step=0.1) co2 = st.number_input("CO₂ (%)", 0.0, step=0.1) operador = st.text_input("👤 Operador") muestreo_en = st.text_input("📍 Muestreo en") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por") obs = st.text_area("📝 Observaciones") if st.button("📊 Analizar Gas"): resultados = { "H₂S (ppm)": f"{h2s} - {'✅' if h2s <= 2.1 else '❌'}", "CO₂ (%)": f"{co2} - {'✅' if co2 <= 2.0 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Gas_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Evaluación de H₂S y CO₂.", resultados, obs, muestreo_en, muestra_por)

Gasolina Estabilizada

with tabs[1]: st.subheader("⛽ Análisis de Gasolina Estabilizada") tvr = st.number_input("TVR (psia)", 0.0, step=0.1) sales = st.number_input("Sales (mg/m²)", 0.0, step=0.1) agua = st.number_input("Agua y sedimentos (%)", 0.0, step=0.1) operador = st.text_input("👤 Operador", key="op_gasolina") muestreo_en = st.text_input("📍 Muestreo en", key="m_gasolina") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_gasolina") obs = st.text_area("📝 Observaciones", key="obs_gasolina") if st.button("📊 Analizar Gasolina"): resultados = { "TVR (psia)": f"{tvr} - {'✅' if tvr <= 12 else '❌'}", "Sales (mg/m²)": f"{sales} - {'✅' if sales <= 100 else '❌'}", "Agua y sedimentos (%)": f"{agua} - {'✅' if agua <= 1 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Gasolina_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Parámetros críticos para evitar corrosión y sobrepresión.", resultados, obs, muestreo_en, muestra_por)

MEG

with tabs[2]: st.subheader("🧪 Análisis de MEG") ph = st.number_input("pH", 0.0, 14.0, step=0.1) conc = st.number_input("Concentración (%wt)", 0.0, 100.0, step=0.1) cl = st.number_input("Cloruros (ppm)", 0.0, step=0.1) operador = st.text_input("👤 Operador", key="op_meg") muestreo_en = st.text_input("📍 Muestreo en", key="m_meg") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_meg") obs = st.text_area("📝 Observaciones", key="obs_meg") if st.button("📊 Analizar MEG"): resultados = { "pH": f"{ph} - {'✅' if 6.5 <= ph <= 8 else '❌'}", "Concentración (%wt)": f"{conc} - {'✅' if 60 <= conc <= 84 else '❌'}", "Cloruros (ppm)": f"{cl} - {'✅' if cl <= 50 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"MEG_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Control del inhibidor de formación de hidratos.", resultados, obs, muestreo_en, muestra_por)

TEG

with tabs[3]: st.subheader("🧪 Análisis de TEG") ph = st.number_input("pH", 0.0, 14.0, step=0.1, key="ph_teg") conc = st.number_input("Concentración (%wt)", 0.0, 100.0, step=0.1, key="conc_teg") cl = st.number_input("Cloruros (ppm)", 0.0, step=0.1, key="cl_teg") operador = st.text_input("👤 Operador", key="op_teg") muestreo_en = st.text_input("📍 Muestreo en", key="m_teg") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_teg") obs = st.text_area("📝 Observaciones", key="obs_teg") if st.button("📊 Analizar TEG"): resultados = { "pH": f"{ph} - {'✅' if 6.5 <= ph <= 8.5 else '❌'}", "Concentración (%wt)": f"{conc} - {'✅' if conc >= 99 else '❌'}", "Cloruros (ppm)": f"{cl} - {'✅' if cl <= 50 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"TEG_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Análisis del glicol para deshidratación.", resultados, obs, muestreo_en, muestra_por)

Agua Desmineralizada

with tabs[4]: st.subheader("💧 Análisis de Agua Desmineralizada") cl = st.number_input("Cloruros (ppm)", 0.0, step=0.1) operador = st.text_input("👤 Operador", key="op_agua") muestreo_en = st.text_input("📍 Muestreo en", key="m_agua") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_agua") obs = st.text_area("📝 Observaciones", key="obs_agua") if st.button("📊 Analizar Agua"): resultados = { "Cloruros (ppm)": f"{cl} - {'✅' if cl <= 10 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Agua_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Control de cloruros en agua desmineralizada.", resultados, obs, muestreo_en, muestra_por)

Aminas

with tabs[5]: st.subheader("☠️ Análisis de Aminas") conc = st.number_input("Concentración (%wt)", 0.0, 100.0, step=0.1) cl_amina = st.number_input("Cloruros en amina (ppm)", 0.0, step=1.0) cl_caldera = st.number_input("Cloruros en caldera (ppm)", 0.0, step=0.1) carga_pobre = st.number_input("Carga ácida amina pobre (mol/mol)", 0.0, step=0.001) carga_rica = st.number_input("Carga ácida amina rica (mol/mol)", 0.0, step=0.01) operador = st.text_input("👤 Operador", key="op_aminas") muestreo_en = st.text_input("📍 Muestreo en", key="m_aminas") muestra_por = st.text_input("🧑‍🔬 Muestra tomada por", key="t_aminas") obs = st.text_area("📝 Observaciones", key="obs_aminas") if st.button("📊 Analizar Aminas"): resultados = { "Concentración (%wt)": f"{conc} - {'✅' if 48 <= conc <= 52 else '❌'}", "Cloruros en amina": f"{cl_amina} - {'✅' if cl_amina <= 1000 else '❌'}", "Cloruros en caldera": f"{cl_caldera} - {'✅' if cl_caldera <= 10 else '❌'}", "Carga ácida pobre": f"{carga_pobre} - {'✅' if carga_pobre <= 0.025 else '❌'}", "Carga ácida rica": f"{carga_rica} - {'✅' if carga_rica <= 0.45 else '❌'}" } st.dataframe(pd.DataFrame(resultados.items(), columns=["Parámetro", "Resultado"])) exportar_pdf(f"Aminas_{operador}{datetime.now().strftime('%Y%m%d%H%M')}.pdf", operador, "Evaluación de solvente amínico y cargas ácidas.", resultados, obs, muestreo_en, muestra_por)

