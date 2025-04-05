import streamlit as st
import pandas as pd
from asistente import generar_respuesta

st.set_page_config(page_title="Chat Gerencial - Ventas", layout="wide")

st.title("📊 Chat Gerencial - Análisis de Ventas")

# Subir archivo
archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

if archivo is not None:
    df = pd.read_excel(archivo)

    st.subheader("Vista general de los datos")
    st.dataframe(df.head(50), use_container_width=True)

    # Reglas de negocio simples
    st.subheader("🔍 Evaluación de metas")
    df['cumple_meta_producto'] = df['ventas_reales'] >= df['meta_producto']

    resumen_sucursal = df.groupby('sucursal').agg({
        'ventas_reales': 'sum',
        'meta_sucursal': 'mean'
    }).reset_index()

    resumen_sucursal['cumple_meta_sucursal'] = resumen_sucursal['ventas_reales'] >= resumen_sucursal['meta_sucursal']

    st.write("✅ Cumplimiento por sucursal:")
    st.dataframe(resumen_sucursal, use_container_width=True)

    st.write("🔔 Alertas:")
    for _, row in resumen_sucursal.iterrows():
        if not row['cumple_meta_sucursal']:
            st.warning(f"La sucursal {row['sucursal']} no cumplió la meta. Ventas: {row['ventas_reales']} / Meta: {row['meta_sucursal']}")

    # Asistente Gerencial
    st.subheader("🤖 Asistente Gerencial")
    resumen_texto = ""
    for _, row in resumen_sucursal.iterrows():
       resumen_texto += f"Sucursal {row['sucursal']}: Ventas = {row['ventas_reales']}, Meta = {row['meta_sucursal']}. Cumple: {row['cumple_meta_sucursal']}"


    if st.button("Generar recomendaciones"):
        respuesta = generar_respuesta(resumen_texto)
        st.success(respuesta)

else:
    st.info("Por favor, carga un archivo Excel con los datos de ventas.")
