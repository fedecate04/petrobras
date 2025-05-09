LTS LAB ANALYZER COMPLETO - Con campos adicionales "Muestreo en" y "Muestra tomada por"

import streamlit as st import pandas as pd from fpdf import FPDF from datetime import datetime from io import BytesIO import os import base64 from pathlib import Path

Función para limpiar caracteres incompatibles

def limpiar_pdf_texto(texto): reemplazos = { "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9", "⁰": "0", "¹": "1", "²": "2", "³": "3", "°": " grados ", "º": "", "“": '"', "”": '"', "‘": "'", "’": "'", "–": "-", "—": "-", "•": "-", "→": "->", "←": "<-", "⇒": "=>", "≠": "!=", "≥": ">=", "≤": "<=", "✓": "OK", "✅": "OK", "❌": "NO" } for k, v in reemplazos.items(): texto = texto.replace(k, v) return texto

Configuración general

st.set_page_config(page_title="LTS Lab Analyzer", layout="wide") LOGO_PATH = "logopetrogas.png"

Estilo visual

st.markdown(""" <style> .stApp { background-color: #1e1e1e; color: white; } .stButton>button, .stDownloadButton>button { background-color: #0d6efd; color: white; border-radius: 8px; border: none; } input, textarea, .stTextInput, .stTextArea, .stNumberInput input { background-color: #2e2e2e !important; color: white !important; border: 1px solid #555 !important; } .stSelectbox div { background-color: #2e2e2e !important; color: white !important; } </style> """, unsafe_allow_html=True)

Mostrar logo

if Path(LOGO_PATH).exists(): with open(LOGO_PATH, "rb") as f: logo_base64 = base64.b64encode(f.read()).decode("utf-8") st.markdown(f""" <div style='text-align:center;'> <img src='data:image/png;base64,{logo_base64}' width='200'/> </div> """, unsafe_allow_html=True) else: st.warning("⚠️ No se encontró el logo 'logopetrogas.png'")

st.markdown("<h2 style='text-align:center;'>🧪 LTS Lab Analyzer</h2>", unsafe_allow_html=True)

Clase PDF

class PDF(FPDF): def header(self): if os.path.exists(LOGO_PATH): self.image(LOGO_PATH, 10, 8, 33) self.set_font("Arial", "B", 12) self.cell(0, 10, "INFORME DE ANÁLISIS DE LABORATORIO", 0, 1, "C") self.set_font("Arial", "", 10) self.cell(0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "R") self.ln(5)

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

Función para exportar PDF con nuevos campos incluidos

def exportar_pdf(nombre, operador, explicacion, resultados, observaciones, muestreo_en, muestra_por): pdf = PDF() pdf.add_page() pdf.add_section("Operador", limpiar_pdf_texto(operador)) pdf.add_section("Muestreo en", limpiar_pdf_texto(muestreo_en)) pdf.add_section("Muestra tomada por", limpiar_pdf_texto(muestra_por)) pdf.add_section("Explicación técnica", limpiar_pdf_texto(explicacion)) pdf.add_section("Resultados", {k: limpiar_pdf_texto(str(v)) for k, v in resultados.items()}) pdf.add_section("Observaciones", limpiar_pdf_texto(observaciones or "Sin observaciones.")) output = pdf.output(dest='S').encode('latin-1', errors='ignore') st.download_button("⬇️ Descargar informe PDF", data=BytesIO(output), file_name=nombre, mime="application/pdf")

