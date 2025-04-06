import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np
from openai import OpenAI
import io
from fpdf import FPDF
import base64

# Configura el cliente de OpenAI usando el secreto
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Chat Gerencial - Ventas", layout="wide")
st.title("🤖 Chat Gerencial - Análisis de Ventas")

# Subida de archivo
archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)

    st.subheader("📊 Vista general de los datos")
    st.dataframe(df)

    st.subheader("📈 Resumen estadístico")
    st.write(df.describe())

    # Mapa de calor de correlaciones
    st.subheader("🔥 Mapa de calor de correlaciones")
    fig, ax = plt.subplots()
    sns.heatmap(df.select_dtypes(include=np.number).corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # Clustering
    st.subheader("🧠 Segmentación por Clústeres (KMeans)")
    df_cluster = df.copy()
    numeric_cols = df_cluster.select_dtypes(include=np.number).columns
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_cluster[numeric_cols])

    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(df_scaled)
    df_cluster["Cluster"] = clusters

    st.write("### 📄 Datos con Clúster asignado")
    st.dataframe(df_cluster)

    # Gráfico de clúster en 2D
    if len(numeric_cols) >= 2:
        st.write("### 📌 Visualización de Clústeres")
        fig2, ax2 = plt.subplots()
        scatter = ax2.scatter(df_scaled[:, 0], df_scaled[:, 1], c=clusters, cmap="viridis")
        ax2.set_xlabel(numeric_cols[0])
        ax2.set_ylabel(numeric_cols[1])
        ax2.set_title("Distribución de clústeres")
        st.pyplot(fig2)

    # Descripción automática de clústeres usando OpenAI
    st.subheader("🧠 Descripción de Clústeres (IA)")
    try:
        resumen_cluster = df_cluster.groupby("Cluster")[numeric_cols].mean().reset_index()
        resumen_markdown = resumen_cluster.to_markdown(index=False)

        prompt = f"""
Eres un analista experto. Describe los siguientes clústeres en términos de su comportamiento y características. Proporciona recomendaciones para cada clúster. Usa un lenguaje claro y ejecutivo.

Resumen:
{resumen_markdown}
"""
        respuesta_chat = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
       {"role": "system", "content": "Eres un asesor gerencial experto en ventas y análisis de datos."},
       {"role": "user", "content": prompt_chat}
    ]
)
        descripcion = response.choices[0].message.content
        st.markdown(descripcion)
    except Exception as e:
        st.warning(f"⚠️ Error al generar descripción con IA: {e}")

    # Chat tipo conversación
    st.subheader("💬 Chat Gerencial Interactivo")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    col1, col2 = st.columns([4, 1])

    with col1:
        nueva_pregunta = st.text_input("Escribe tu pregunta:", key="input")
    with col2:
        borrar = st.button("🧹 Limpiar chat")

    if borrar:
        st.session_state.chat_history = []
        st.experimental_rerun()

    if st.button("Enviar pregunta") and nueva_pregunta:
        try:
            contexto = df.describe().to_string()
            prompt_chat = f"""
{contexto}

Basado en los datos anteriores, responde esta pregunta de forma ejecutiva:
{nueva_pregunta}
"""
            respuesta_chat = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asesor gerencial experto en
