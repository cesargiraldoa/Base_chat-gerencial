import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Configuración general ---
st.set_page_config(page_title="Chat Gerencial V4", layout="wide")

# --- Título principal ---
st.title("🎬 Chat Gerencial - Versión 4")
st.markdown("Bienvenido al panel gerencial inteligente con perfiles personalizados.")

# --- Barra lateral: selección de perfil ---
st.sidebar.title("👤 Selecciona tu perfil")
perfil = st.sidebar.selectbox(
    "¿Quién eres?",
    ["Gerente General", "Director de Ventas", "Director de Marketing"]
)

# Guardar perfil en sesión
st.session_state.perfil = perfil

# --- Cargar archivo de ejemplo ---
@st.cache_data
def cargar_datos():
    df = pd.read_excel("ventas_ejemplo.xlsx")
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    return df

df = cargar_datos()

# --- Filtro por fechas ---
st.sidebar.markdown("### 📅 Rango de fechas")
fecha_inicio = st.sidebar.date_input("Desde", value=df["Fecha"].min())
fecha_fin = st.sidebar.date_input("Hasta", value=df["Fecha"].max())
df_filtrado = df[(df["Fecha"] >= pd.to_datetime(fecha_inicio)) & (df["Fecha"] <= pd.to_datetime(fecha_fin))]

# --- Mostrar contenido según perfil ---
st.markdown(f"## 👤 Bienvenido, {perfil}")

if perfil == "Gerente General":
    st.success("🔎 Visión general de desempeño y cumplimiento global.")

    ventas_totales = df_filtrado["Ventas"].sum()
    metas_totales = df_filtrado["Meta"].sum()
    cumplimiento = round((ventas_totales / metas_totales) * 100, 2) if metas_totales > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Ventas Totales", f"${ventas_totales:,.0f}")
    col2.metric("🎯 Meta Global", f"${metas_totales:,.0f}")
    col3.metric("✅ Cumplimiento", f"{cumplimiento}%")

    fig = px.bar(df_filtrado.groupby("Sucursal")["Ventas"].sum().reset_index(),
                 x="Sucursal", y="Ventas", title="Ventas por Sucursal")
    st.plotly_chart(fig, use_container_width=True)

elif perfil == "Director de Ventas":
    st.info("📈 Análisis detallado de ventas por producto y sucursal.")

    ventas_por_producto = df_filtrado.groupby("Producto")["Ventas"].sum().reset_index()
    fig = px.bar(ventas_por_producto, x="Producto", y="Ventas", title="Ventas por Producto")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(df_filtrado, x="Fecha", y="Ventas", color="Sucursal", title="Tendencia de Ventas")
    st.plotly_chart(fig2, use_container_width=True)

elif perfil == "Director de Marketing":
    st.warning("🎯 Tendencias, productos top y oportunidades.")

    top_productos = df_filtrado.groupby("Producto")["Ventas"].sum().sort_values(ascending=False).head(5).reset_index()
    st.table(top_productos)

    fig = px.pie(top_productos, names="Producto", values="Ventas", title="Top 5 Productos")
    st.plotly_chart(fig, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.caption("🔧 Versión 4 en desarrollo | Hecho con ❤️ y Streamlit")
