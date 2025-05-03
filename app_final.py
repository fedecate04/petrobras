
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
    valor_dolar = st.number_input("💲 Ingresá el valor estimado en USD por MJ de PCS", value=2.25, step=0.01)
    validacion = {
        'CO2 (%)': (composicion.get('CO2', 0), ('<', 2, '% molar')),
        'Inertes totales': (sum(composicion.get(k, 0) for k in ['N2', 'CO2', 'O2']), ('<', 4, '% molar')),
        'O2 (%)': (composicion.get('O2', 0), ('<', 0.2, '% molar')),
        'H2S (ppm)': (api_h2s_ppm, ('<', 2, 'ppm')),
        'PCS (kcal/m3)': (hhv_total * 239.006, ('>=', (8850, 12200), 'Kcal/Sm3'))
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
        resultados = analizar_composicion(composicion, valor_dolar)
        'Validación': validacion
    }

class PDF(FPDF):
    def header(self):
        try:
            self.image("LOGO PETROGAS.png", x=10, y=8, w=30)  # Ajustá nombre si es distinto
        except:
            pass  # Si el logo no se encuentra, no rompe el PDF
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Informe de Analisis de Gas Natural', 0, 1, 'C')
        self.ln(15)

    def add_sample(self, nombre, resultados):
        self.set_font('Arial', '', 10)
        self.cell(0, 10, f"Muestra: {nombre}", 0, 1)
        for k, v in resultados.items():
            if k != 'Validación':
                self.cell(0, 8, f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}", 0, 1)
        self.ln(3)
        self.set_font('Arial', 'B', 10)
        self.cell(0, 8, 'Validacion de parametros:', 0, 1)
        self.set_font('Arial', '', 10)
        for param, (valor, (op, ref, unidad)) in resultados['Validación'].items():
            if op == '<':
                cumple = valor < ref
                espec = f"< {ref} {unidad}"
            else:
                cumple = ref[0] <= valor <= ref[1]
                espec = f"{ref[0]}-{ref[1]} {unidad}"
            estado = 'CUMPLE' if cumple else 'NO CUMPLE'
            self.cell(0, 8, f"{estado} {param}: {valor:.2f} ({espec})", 0, 1)
        self.ln(5)

st.title("Analizador de Gas Natural")
st.markdown("""
### 🧾 Descripción del sistema

Este sistema permite analizar la composición de una muestra de gas natural a partir de un archivo `.csv` con los porcentajes molares de sus componentes.  
A partir de esa información, calcula parámetros clave para la evaluación del gas y genera un informe técnico en formato PDF.

---

### 📂 ¿Qué debe contener el archivo CSV?

El archivo debe contener **una fila con los siguientes nombres de columnas** (en cualquier orden, pero con estos encabezados exactos):

- `CH4`, `C2H6`, `C3H8`, `i-C4H10`, `n-C4H10`, `i-C5H12`, `n-C5H12`, `C6+`
- `N2`, `CO2`, `H2S`, `O2`

Los valores deben estar expresados en **% molar**. Solo se analiza la **primera fila** del archivo.

---

### 📊 ¿Qué cálculos realiza?

El sistema calcula:

- **PM**: Peso molecular promedio del gas
- **PCS**: Poder Calorífico Superior en MJ/m³ y kcal/m³
- **Gamma**: Relación de PM aire / PM gas
- **Índice de Wobbe**: Importante para el rendimiento energético
- **Densidad** a condiciones estándar
- **Dew Point estimado**: Según presencia de componentes pesados
- **Carga de H₂S** y concentración en ppm
- **Ingreso estimado (USD/m³)**: En base al PCS
- **Validación de parámetros críticos**: Contra especificaciones típicas del gas comercial

---

Una vez subido el archivo, podrás visualizar los resultados y descargar un informe PDF automático.
""")

archivo = st.file_uploader("Subi un archivo CSV con una muestra", type="csv")

if archivo:
    df = pd.read_csv(archivo)
    fila = df.iloc[0]
    composicion = {k: fila[k] for k in PM if k in fila}
    resultados = analizar_composicion(composicion, valor_dolar)
    st.subheader("Resultados del análisis")
    st.dataframe(pd.DataFrame.from_dict(resultados, orient='index', columns=['Valor']))


    pdf = PDF()
    pdf.add_page()
    pdf.add_sample("Muestra", resultados)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer = io.BytesIO(pdf_bytes)

    st.download_button(
        label="Descargar informe PDF",
        data=buffer,
        file_name=f"Informe_Gas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )
