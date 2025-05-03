
import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import io
from datetime import datetime

PM = {
    'CH4': 16.04, 'C2H6': 30.07, 'C3H8': 44.10,
    'i-C4H10': 58.12, 'n-C4H10': 58.12, 'i-C5H12': 72.15, 'n-C5H12': 72.15,
    'C6+': 86.00, 'N2': 28.01, 'CO2': 44.01, 'H2S': 34.08, 'O2': 32.00
}
HHV = {
    'CH4': 39.82, 'C2H6': 70.6, 'C3H8': 101.0,
    'i-C4H10': 131.6, 'n-C4H10': 131.6,
    'i-C5H12': 161.0, 'n-C5H12': 161.0,
    'C6+': 190.0
}
R = 8.314
PM_aire = 28.96
T_std = 288.15
P_std = 101325

def analizar_composicion(composicion):
    composicion = {k: float(v) for k, v in composicion.items() if k in PM}
    total = sum(composicion.values())
    fracciones = {k: v / total for k, v in composicion.items()}
    pm_muestra = sum(fracciones[k] * PM[k] for k in fracciones)
    densidad = (pm_muestra * P_std) / (R * T_std)
    hhv_total = sum(fracciones.get(k, 0) * HHV.get(k, 0) for k in HHV)
    gamma = PM_aire / pm_muestra
    wobbe = hhv_total / np.sqrt(pm_muestra / PM_aire)
    dew_point = -30 if fracciones.get('C6+', 0) > 0.01 else -60
    api_h2s_ppm = composicion.get('H2S', 0) * 1e4
    carga_h2s = (api_h2s_ppm * PM['H2S'] / 1e6) / (pm_muestra * 1e3)
    ingreso = hhv_total * 2.25
    validacion = {
        'CO2 (%)': (composicion.get('CO2', 0), ('<', 2, '% molar')),
        'Inertes totales': (sum(composicion.get(k, 0) for k in ['N2', 'CO2', 'O2']), ('<', 4, '% molar')),
        'O2 (%)': (composicion.get('O2', 0), ('<', 0.2, '% molar')),
        'H2S (ppm)': (api_h2s_ppm, ('<', 2, 'ppm')),
        'PCS (kcal/m3)': (hhv_total * 239.006, ('>=', (8850, 12200), 'Kcal/Sm³'))
    }
    return {
        'PM': pm_muestra,
        'PCS (MJ/m3)': hhv_total,
        'PCS (kcal/m3)': hhv_total * 239.006,
        'Gamma': gamma,
        'Wobbe': wobbe,
        'Densidad (kg/m3)': densidad,
        'Dew Point estimado (°C)': dew_point,
        'CO2 (%)': composicion.get('CO2', 0),
        'H2S ppm': api_h2s_ppm,
        'Carga H2S (kg/kg)': carga_h2s,
        'Ingreso estimado (USD/m3)': ingreso,
        'Validación': validacion
    }

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Informe de Análisis de Gas Natural', 0, 1, 'C')
        self.ln(5)
    def add_sample(self, nombre, resultados):
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f"Muestra: {nombre}", 0, 1)
        for k, v in resultados.items():
            if k != 'Validación':
                self.cell(0, 8, f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}", 0, 1)
        self.ln(3)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, 'Validación de parámetros:', 0, 1)
        self.set_font('Arial', '', 10)
        for param, (valor, (op, ref, unidad)) in resultados['Validación'].items():
            if op == '<':
                cumple = valor < ref
                espec = f"< {ref} {unidad}"
            else:
                cumple = ref[0] <= valor <= ref[1]
                espec = f"{ref[0]}–{ref[1]} {unidad}"
            estado = 'CUMPLE' if cumple else 'NO CUMPLE'
            self.cell(0, 8, f"{estado} {param}: {valor:.2f} ({espec})", 0, 1)
        self.ln(5)

st.title("Analizador de Gas Natural")
archivo = st.file_uploader("Subí un archivo CSV con una muestra", type="csv")

if archivo:
    df = pd.read_csv(archivo)
    fila = df.iloc[0]
    composicion = {k: fila[k] for k in PM if k in fila}
    resultados = analizar_composicion(composicion)
    st.subheader("Resultados del análisis")
    st.dataframe(pd.DataFrame.from_dict(resultados, orient='index', columns=['Valor']))

    pdf = PDF()
    pdf.add_page()
    pdf.add_sample("Muestra", resultados)
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    st.download_button(
        label="Descargar informe PDF",
        data=buffer,
        file_name=f"Informe_Gas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )
