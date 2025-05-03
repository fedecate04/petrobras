import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import io
from datetime import datetime

st.title("Sistema de Análisis de Calidad - Planta LTS")
modulo = st.selectbox("🧪 Elegí el tipo de análisis:", ["Gas Natural", "Gasolina Estabilizada"])

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

# --- GAS NATURAL ---
if modulo == "Gas Natural":
    st.header("📄 Módulo de Gas Natural")
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

    valor_dolar = st.number_input("💲 Ingresá el valor estimado en USD por MJ de PCS", value=2.25, step=0.01)
    archivo = st.file_uploader("Subí un archivo CSV con una muestra", type="csv")

    def analizar_composicion(composicion, valor_dolar):
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
        ingreso = hhv_total * valor_dolar
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
            'Ingreso estimado (USD/m3)': ingreso,
            'Validación': validacion
        }

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Informe de Gas Natural', 0, 1, 'C')
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
                    espec = f"{ref[0]}-{ref[1]} {unidad}"
                estado = 'CUMPLE' if cumple else 'NO CUMPLE'
                self.cell(0, 8, f"{estado} {param}: {valor:.2f} ({espec})", 0, 1)
            self.ln(5)

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
            label="📥 Descargar informe PDF",
            data=buffer,
            file_name=f"Informe_Gas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )

# --- GASOLINA ESTABILIZADA ---
if modulo == "Gasolina Estabilizada":
    st.header("📄 Módulo de Gasolina Estabilizada")
    st.markdown("""
    Este módulo permite ingresar manualmente los parámetros de una muestra de gasolina estabilizada.  
    Se evalúan los siguientes indicadores contra especificaciones típicas:

    - **TVR (psi a 38.7 °C)**: Presión medida del vapor recuperado. Refleja volatilidad y seguridad.
    - **Sales (mg/L)**: Medida de contaminantes inorgánicos. Valores altos pueden corroer equipos.
    - **Color (ASTM)**: Indicador visual relacionado con el proceso de estabilización. Texto de observación.
    - **Densidad (kg/m³)**: Parámetro físico importante para compatibilidad y rendimiento.

    Ingresá los valores según el análisis de laboratorio y generá un informe en PDF con validación automática.
    """)

    tvr = st.number_input("TVR (psi a 38.7 °C)", min_value=0.0, max_value=100.0, value=7.0)
    sales = st.number_input("Concentración de Sales (mg/L)", min_value=0.0, max_value=10.0, value=2.0)
    color = st.text_input("Color ASTM / Observación", value="Color dentro de especificación")
    densidad = st.number_input("Densidad a 15 °C (kg/m³)", min_value=600.0, max_value=800.0, value=730.0)

    if st.button("Generar informe de gasolina"):
        resultados = {
            "TVR (psi a 38.7 °C)": tvr,
            "Sales (mg/L)": sales,
            "Color ASTM": color,
            "Densidad (kg/m³)": densidad
        }
        especificaciones = {
            "TVR (psi a 38.7 °C)": (5, 10),
            "Sales (mg/L)": (0, 3),
            "Densidad (kg/m³)": (700, 740)
        }

        validacion = {}
        for k in resultados:
            if k == "Color ASTM":
                validacion[k] = (resultados[k], "Observación", True)
            else:
                valor = resultados[k]
                min_, max_ = especificaciones[k]
                cumple = min_ <= valor <= max_
                validacion[k] = (valor, (min_, max_), cumple)

        st.subheader("📊 Resultados del análisis de gasolina")
        tabla = []
        for k, val in validacion.items():
            if k == "Color ASTM":
                tabla.append({"Parámetro": k, "Valor": val[0], "Especificación": val[1], "Cumple": "Observación"})
            else:
                valor, (min_, max_), cumple = val
                tabla.append({"Parámetro": k, "Valor": valor, "Especificación": f"{min_}–{max_}", "Cumple": "✅" if cumple else "❌"})
        df_val = pd.DataFrame(tabla)
        st.dataframe(df_val)

        class PDFGasolina(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'Informe de Gasolina Estabilizada', 0, 1, 'C')
                self.ln(10)

            def add_resultados(self, resultados, validacion):
                self.set_font('Arial', '', 10)
                for param in resultados:
                    valor = resultados[param]
                    if param == "Color ASTM":
                        self.cell(0, 8, f"{param}: {valor} (Observación)", 0, 1)
                    else:
                        min_, max_ = validacion[param][1]
                        cumple = validacion[param][2]
                        estado = 'CUMPLE' if cumple else 'NO CUMPLE'
                        self.cell(0, 8, f"{param}: {valor} ({estado}, espec: {min_}–{max_})", 0, 1)

        pdf = PDFGasolina()
        pdf.add_page()
        pdf.add_resultados(resultados, validacion)

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        buffer = io.BytesIO(pdf_bytes)

        st.download_button(
            label="📥 Descargar informe PDF de Gasolina",
            data=buffer,
            file_name=f"Informe_Gasolina_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )


