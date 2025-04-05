import streamlit as st
import pandas as pd
import openai
import os

# Configuración de página
st.set_page_config(page_title="Chat Gerencial - Ventas", layout="wide")
st.title("📊 Chat Gerencial - Análisis de Ventas")

# Leer la API key desde el entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

# Subir archivo
archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

if archivo is not None:
    df = pd.read_excel(archivo)

    st.subheader("Vista general de los datos")
    st.dataframe(df.head(50), use_container_width=True)

    # Opcional: Mostrar resumen general
    st.subheader("Resumen estadístico")
    st.write(df.describe())

    # Entrada para pregunta o análisis
    st.subheader("🤖 Asistente Gerencial")
    pregunta = st.text_area("¿Qué deseas analizar o preguntar?", placeholder="Ej: ¿Qué sucursales no están cumpliendo las metas?")

    if st.button("Generar análisis con IA"):
        with st.spinner("Generando análisis..."):

            resumen_texto = ""
            for index, row in df.iterrows():
                resumen_texto += f"Sucursal {row['sucursal']}: Ventas = {row['ventas_reales']}, Meta = {row['meta_sucursal']}. Cumple: {row['cumple_meta_sucursal']}\n"

            prompt = f"""
Eres un asesor de negocios. Analiza los siguientes datos de desempeño comercial y responde a la siguiente pregunta del usuario de forma ejecutiva.

Datos:
{resumen_texto}

Pregunta: {pregunta}

Entrega un resumen con conclusiones claras y recomendaciones.
"""

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=800
                )

                respuesta = response.choices[0].message["content"]
                st.markdown("### 🧠 Respuesta del Asistente")
                st.write(respuesta)

            except Exception as e:
                st.error(f"Ocurrió un error al consultar la IA: {e}")
