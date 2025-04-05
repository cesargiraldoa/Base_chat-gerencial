import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from openai import OpenAI

st.set_page_config(page_title="Chat Gerencial - Ventas", layout="wide")
st.title("📊 Chat Gerencial - Análisis de Ventas")

archivo = st.file_uploader("Cargar archivo Excel de ventas", type=[".xlsx"])
if archivo is not None:
    df = pd.read_excel(archivo)

    st.subheader("📄 Vista general de los datos")
    st.dataframe(df.head())

    st.subheader("📈 Resumen estadístico")
    st.dataframe(df.describe())

    if 'ventas_reales' in df.columns and 'meta_sucursal' in df.columns:

        df['cumple_meta_sucursal'] = df['ventas_reales'] >= df['meta_sucursal']

        X = df[['ventas_reales', 'meta_sucursal']].copy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=3, random_state=42)
        df['cluster'] = kmeans.fit_predict(X_scaled)

        st.subheader("📊 Gráfico de Clústeres")
        fig, ax = plt.subplots()
        scatter = ax.scatter(df['ventas_reales'], df['meta_sucursal'], c=df['cluster'], cmap='viridis')
        ax.legend(*scatter.legend_elements(), title="Clústers")
        ax.set_xlabel("Ventas Reales")
        ax.set_ylabel("Meta Sucursal")
        st.pyplot(fig)

        st.subheader("📋 Tabla con Clúster asignado")
        st.dataframe(df[['sucursal', 'ventas_reales', 'meta_sucursal', 'cluster']])

        st.subheader("🌡 Mapa de calor de correlaciones")
        fig2, ax2 = plt.subplots()
        sns.heatmap(df.select_dtypes(include='number').corr(), annot=True, cmap="coolwarm", ax=ax2)
        st.pyplot(fig2)

        st.subheader("🧠 Descripción de Clústeres (IA)")
        try:
            resumen = df.groupby('cluster').agg({
                'ventas_reales': 'mean',
                'meta_sucursal': 'mean',
                'cumple_meta_sucursal': 'mean'
            }).reset_index()

            prompt = f"""
Eres un experto en análisis de datos. A continuación, se presentan los resultados de un análisis de clústeres aplicado a datos de ventas. Cada fila representa un clúster y contiene el promedio de ventas reales, la meta de ventas y el porcentaje de cumplimiento de meta. Por favor, describe de forma ejecutiva y analítica las características de cada clúster y ofrece posibles recomendaciones.

{resumen.to_markdown(index=False)}
"""
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un analista de datos."},
                    {"role": "user", "content": prompt}
                ]
            )
            descripcion = response.choices[0].message.content
            st.markdown(descripcion)

        except Exception as e:
            st.error(f"⚠️ Error al generar descripción con IA:\n\n{str(e)}")

st.subheader("🤖 Asistente Gerencial")
pregunta = st.text_area("¿Qué deseas analizar o preguntar?", placeholder="Ej: ¿Cuáles sucursales cumplieron la meta?")
if st.button("Generar análisis con IA"):
    if archivo is not None and pregunta:
        try:
            prompt_usuario = f"""
Eres un asistente de inteligencia de negocios. Responde en español a la siguiente pregunta basada en los siguientes datos de ventas:

{df.to_markdown(index=False)}

Pregunta: {pregunta}
"""
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            respuesta = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un analista de datos."},
                    {"role": "user", "content": prompt_usuario}
                ]
            )
            st.success(respuesta.choices[0].message.content)

        except Exception as e:
            st.error(f"⚠️ Error al generar respuesta:\n\n{str(e)}")
    else:
        st.warning("Por favor, carga un archivo Excel y escribe tu pregunta.")
