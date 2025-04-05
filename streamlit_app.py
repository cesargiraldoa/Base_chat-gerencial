import streamlit as st
import pandas as pd
import openai
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

st.set_page_config(page_title="Chat Gerencial - Análisis de Ventas", layout="wide")
st.title("📊 Chat Gerencial - Análisis de Ventas")

# Configura la clave de OpenAI desde los secretos
openai.api_key = os.getenv("OPENAI_API_KEY")

# Función para generar descripción de clústeres usando la nueva interfaz de OpenAI
def generar_descripcion_clusters(df_cluster):
    try:
        prompt = f"""
Analiza la siguiente tabla de clústeres y genera una breve descripción de cada grupo, enfocándote en el volumen de ventas, el cumplimiento de metas y las diferencias relevantes.

{df_cluster.to_string(index=False)}
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un analista experto en ventas y segmentación de clientes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error al generar descripción con IA:\n\n{e}"

# Carga del archivo Excel
archivo = st.file_uploader("📥 Cargar archivo Excel de ventas", type=["xlsx"])

if archivo is not None:
    df = pd.read_excel(archivo)

    st.subheader("🔍 Vista general de los datos")
    st.dataframe(df)

    # Verifica que existan las columnas necesarias
    if 'ventas_reales' in df.columns and 'meta_sucursal' in df.columns:
        # Genera columnas derivadas
        df['cumple_meta'] = df['ventas_reales'] >= df['meta_sucursal']
        df['diferencia'] = df['ventas_reales'] - df['meta_sucursal']

        st.subheader("📊 Resumen estadístico")
        st.dataframe(df.describe())

        # ========== Gráfica 1: Ventas vs Metas ==========
        st.subheader("📊 Ventas Reales vs Metas por Sucursal")
        fig1, ax1 = plt.subplots()
        ax1.bar(df['sucursal'], df['ventas_reales'], label='Ventas', color='blue')
        ax1.bar(df['sucursal'], df['meta_sucursal'], alpha=0.6, label='Meta', color='orange')
        ax1.set_title("Ventas vs Metas por Sucursal")
        ax1.legend()
        st.pyplot(fig1)

        # ========== Gráfica 2: Cumplimiento de Metas (Pie) ==========
        st.subheader("✅ Cumplimiento de Metas")
        fig2, ax2 = plt.subplots()
        cumple_counts = df['cumple_meta'].value_counts()
        ax2.pie(cumple_counts, labels=['Cumple', 'No cumple'], autopct='%1.1f%%', colors=['green', 'red'])
        st.pyplot(fig2)

        # ========== Gráfica 3: Diferencia entre Ventas y Metas ==========
        st.subheader("📉 Diferencia entre Ventas y Metas")
        fig3, ax3 = plt.subplots()
        colores = ['green' if x >= 0 else 'red' for x in df['diferencia']]
        ax3.bar(df['sucursal'], df['diferencia'], color=colores)
        ax3.axhline(0, linestyle='--', color='gray')
        ax3.set_title("Diferencia (Ventas - Meta)")
        st.pyplot(fig3)

        # ========== Gráfica 4: Mapa de Calor de Correlaciones ==========
        st.subheader("🌡️ Mapa de Calor de Correlaciones")
        numeric_cols = df.select_dtypes(include='number')
        fig4, ax4 = plt.subplots()
        sns.heatmap(numeric_cols.corr(), annot=True, cmap="coolwarm", ax=ax4)
        st.pyplot(fig4)

        # ========== Clustering: Análisis de clústeres ==========
        st.subheader("🔎 Análisis de Clústeres (Agrupación de Sucursales)")
        clustering_data = df[['ventas_reales', 'meta_sucursal', 'diferencia']]
        scaler = StandardScaler()
        clustering_scaled = scaler.fit_transform(clustering_data)

        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(clustering_scaled)

        st.markdown("📋 **Asignación de clúster por sucursal**")
        st.dataframe(df[['sucursal', 'ventas_reales', 'meta_sucursal', 'diferencia', 'cluster']])

        st.subheader("📈 Visualización de Clústeres")
        fig5, ax5 = plt.subplots()
        scatter = ax5.scatter(
            clustering_scaled[:, 0],
            clustering_scaled[:, 2],
            c=df['cluster'],
            cmap='viridis',
            s=100
        )
        ax5.set_xlabel("Ventas (escaladas)")
        ax5.set_ylabel("Diferencia (escalada)")
        ax5.set_title("Agrupación de Sucursales")
        st.pyplot(fig5)

        # ========== Descripción de Clústeres con IA ==========
        st.subheader("🧠 Descripción de Clústeres (IA)")
        df_cluster = df[['sucursal', 'ventas_reales', 'meta_sucursal', 'diferencia', 'cluster']]
        descripcion_clusters = generar_descripcion_clusters(df_cluster)
        st.write(descripcion_clusters)

        # ========== Asistente Gerencial - Pregunta Libre ==========
        st.subheader("💬 Asistente Gerencial - Pregunta libre con IA")
        pregunta = st.text_area("Escribe tu pregunta sobre estos datos:")
        if st.button("Obtener análisis con IA") and pregunta:
            resumen = ""
            for _, row in df.iterrows():
                resumen += (
                    f"Sucursal: {row['sucursal']} - "
                    f"Ventas: {row['ventas_reales']} - "
                    f"Meta: {row['meta_sucursal']} - "
                    f"Diferencia: {row['diferencia']} - "
                    f"Cumple: {'Sí' if row['cumple_meta'] else 'No'}\n"
                )

            prompt = f"""
Eres un asistente experto en análisis gerencial de ventas. Con base en el siguiente resumen, responde de forma ejecutiva y profesional:

{resumen}

Pregunta del usuario: {pregunta}
"""
            try:
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=800
                )
                st.success("Respuesta del asistente:")
                st.write(resp.choices[0].message.content.strip())
            except Exception as e:
                st.error(f"Ocurrió un error al consultar la IA: {e}")
    else:
        st.warning("❗ El archivo debe contener las columnas: 'ventas_reales' y 'meta_sucursal'")
