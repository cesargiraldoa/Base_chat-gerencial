import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

st.set_page_config(page_title="Chat Gerencial - Ventas", layout="wide")
st.title("📊 Chat Gerencial - Análisis de Ventas")

archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])
if archivo is not None:
    df = pd.read_excel(archivo)
    st.subheader("📋 Vista general de los datos")
    st.dataframe(df.head())

    st.subheader("📊 Resumen estadístico")
    st.dataframe(df.describe())

    if 'ventas_reales' in df.columns and 'meta_sucursal' in df.columns:
        df['cumple_meta'] = df['ventas_reales'] >= df['meta_sucursal']

        st.subheader("✅ Evaluación de metas")
        resumen = df.groupby('sucursal').agg({
            'ventas_reales': 'sum',
            'meta_sucursal': 'mean',
            'cumple_meta': 'mean'
        })
        resumen['cumple_meta'] = resumen['cumple_meta'].apply(lambda x: 'Sí' if x >= 1 else 'No')
        st.dataframe(resumen)

    st.subheader("📉 Mapa de calor de correlaciones")
    corr = df.select_dtypes(include='number').corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

    st.subheader("🔍 Análisis de Clústeres (KMeans + PCA)")
    features = df.select_dtypes(include='number').dropna(axis=1)
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(features)

    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(scaled_data)

    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(pca_result)

    df['cluster'] = clusters
    st.dataframe(df[['sucursal', 'cluster']])

    fig2, ax2 = plt.subplots()
    scatter = ax2.scatter(pca_result[:, 0], pca_result[:, 1], c=clusters, cmap='Set1')
    ax2.set_title("Clústeres de Sucursales")
    st.pyplot(fig2)

    st.subheader("🧠 Descripción de Clústeres (Lógica Interna)")
    descripcion = ""
    for i in sorted(df['cluster'].unique()):
        subset = df[df['cluster'] == i]
        descripcion += f"\n- Clúster {i}:\n"
        descripcion += f"  - Total de sucursales: {subset.shape[0]}\n"
        if 'ventas_reales' in subset.columns:
            descripcion += f"  - Promedio de ventas reales: {subset['ventas_reales'].mean():,.0f}\n"
        if 'meta_sucursal' in subset.columns:
            descripcion += f"  - Promedio de meta: {subset['meta_sucursal'].mean():,.0f}\n"
    st.info(descripcion)

    st.subheader("🤖 Asistente Gerencial")
    pregunta = st.text_input("¿Qué deseas analizar o preguntar?")
    if st.button("Generar análisis con IA"):
        st.warning("IA deshabilitada temporalmente por límite de cuota. Puedes usar las gráficas y tablas para análisis.")
