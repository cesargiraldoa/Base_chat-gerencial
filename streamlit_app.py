import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from io import BytesIO
from reportlab.pdfgen import canvas
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="Chat Gerencial - Modo Oscuro", page_icon="🔟")

# Logo y título
logo = Image.open("assets/logo.png")
st.image(logo, width=180)
st.markdown("<h1 style='color:#FF4B4B;'>🎬 Chat Gerencial Estilo Netflix - Modo Oscuro</h1>", unsafe_allow_html=True)

# Crear o reemplazar archivo con datos de ejemplo
ejemplo = pd.DataFrame({
    "fecha": pd.date_range(start="2025-01-01", periods=60, freq="D").tolist() * 3,
    "sucursal": ["Barranquilla"]*60 + ["Bogotá"]*60 + ["Medellín"]*60,
    "producto": ["Cepillo", "Crema", "Enjuague"] * 60,
    "ventas": [5000, 3000, 2000]*60,
    "meta": [4500, 3500, 2500]*60,
})
os.makedirs("data", exist_ok=True)
ejemplo.to_excel("data/ventas_ejemplo.xlsx", index=False)

# Cargar datos
data = pd.read_excel("data/ventas_ejemplo.xlsx")

# Filtro por fechas
fecha_inicio = st.date_input("🗓️ Fecha inicial", value=pd.to_datetime("2025-01-01"))
fecha_fin = st.date_input("🗓️ Fecha final", value=pd.to_datetime("2025-12-31"))
data = data[(data['fecha'] >= pd.to_datetime(fecha_inicio)) & (data['fecha'] <= pd.to_datetime(fecha_fin))]

# Tabs
tab_inicio, tab_productos, tab_sucursales, tab_tendencias, tab_chat = st.tabs(["🏠 Inicio", "📦 Productos", "🏢 Sucursales", "📈 Tendencias", "💬 Chat Gerencial"])

with tab_inicio:
    st.subheader("📊 Métricas Generales")
    total_ventas = data['ventas'].sum()
    total_meta = data['meta'].sum()
    cumplimiento_global = (total_ventas / total_meta) * 100
    producto_top = data.groupby("producto")["ventas"].sum().idxmax()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏆 Ventas Totales", f"${total_ventas:,.0f}")
    col2.metric("🎯 Meta Total", f"${total_meta:,.0f}")
    col3.metric("📈 Cumplimiento (%)", f"{cumplimiento_global:.2f}%")
    col4.metric("🔥 Producto Más Vendido", producto_top)

with tab_sucursales:
    st.subheader("🏢 Ranking de Sucursales")
    vista = st.radio("Selecciona vista:", ["📂 Vista estándar", "🎬 Vista tipo Netflix (Top)"], horizontal=True)

    top_sucursales = data.groupby("sucursal").agg({'ventas': 'sum', 'meta': 'sum'}).reset_index()
    top_sucursales["cumplimiento"] = (top_sucursales["ventas"] / top_sucursales["meta"]) * 100
    top_sucursales = top_sucursales.sort_values(by="ventas", ascending=False).reset_index(drop=True)

    if vista == "🎬 Vista tipo Netflix (Top)":
        st.markdown("### 🏆 Sucursales Top (estilo Netflix)")
        selected_sucursal = st.selectbox("Selecciona una sucursal para ver análisis:", top_sucursales["sucursal"])

        for i, row in top_sucursales.iterrows():
            rank = i + 1
            color = "#00FFAA" if row["cumplimiento"] >= 100 else "#FF4B4B" if row["cumplimiento"] < 70 else "#FFD700"
            st.markdown(f"""
                <div style='border:1px solid #333; border-radius:12px; padding:20px; margin-bottom:15px;'>
                    <h3 style='color:{color};'>🏢 {rank}. {row['sucursal']}</h3>
                    <p>💰 Ventas: ${row['ventas']:,.0f}</p>
                    <p>📊 Cumplimiento: {row['cumplimiento']:.2f}%</p>
                </div>
            """, unsafe_allow_html=True)

        if selected_sucursal:
            st.markdown(f"### 📊 Análisis de {selected_sucursal}")
            df_suc = data[data['sucursal'] == selected_sucursal].groupby("producto").agg({'ventas': 'sum'}).reset_index()
            fig = px.bar(df_suc, x="producto", y="ventas", title=f"Ventas por producto en {selected_sucursal}", color="ventas")
            st.plotly_chart(fig, use_container_width=True)

            cumplimiento = top_sucursales[top_sucursales['sucursal'] == selected_sucursal]['cumplimiento'].values[0]
            if cumplimiento < 70:
                st.warning(f"⚠️ Alerta: {selected_sucursal} tiene un cumplimiento de {cumplimiento:.2f}%. Requiere atención.")
            elif cumplimiento < 100:
                st.info(f"🔍 {selected_sucursal} está cerca de cumplir su meta.")
            else:
                st.success(f"✅ Excelente: {selected_sucursal} superó la meta con {cumplimiento:.2f}%.")

with tab_productos:
    st.subheader("📦 Ranking de Productos")
    vista_productos = st.radio("Selecciona vista:", ["📂 Vista estándar", "🎬 Vista tipo Netflix (Top)"], horizontal=True, key="productos")

    top_productos = data.groupby("producto").agg({'ventas': 'sum'}).reset_index()
    top_productos = top_productos.sort_values(by="ventas", ascending=False).reset_index(drop=True)

    if vista_productos == "🎬 Vista tipo Netflix (Top)":
        st.markdown("### 🍿 Productos Top (estilo Netflix)")
        for i, row in top_productos.iterrows():
            rank = i + 1
            color = "#00FFAA" if i == 0 else "#FFD700" if i == 1 else "#FF4B4B"
            st.markdown(f"""
                <div style='border:1px solid #333; border-radius:12px; padding:20px; margin-bottom:15px;'>
                    <h3 style='color:{color};'>📦 {rank}. {row['producto']}</h3>
                    <p>💵 Ventas: ${row['ventas']:,.0f}</p>
                </div>
            """, unsafe_allow_html=True)

with tab_tendencias:
    st.subheader("📈 Tendencias de Ventas")
    tendencia = data.groupby(pd.Grouper(key="fecha", freq="M")).agg({'ventas': 'sum'}).reset_index()
    fig = px.line(tendencia, x="fecha", y="ventas", title="Tendencia mensual de ventas")
    st.plotly_chart(fig, use_container_width=True)

with tab_chat:
    st.subheader("💬 Chat Gerencial")
    pregunta = st.text_input("🤖 Escribe tu pregunta (ej: ¿Cuál es el producto top de esta semana?)")
    if pregunta:
        if "producto top" in pregunta.lower():
            st.info(f"🔍 El producto más vendido es: **{producto_top}**")
        elif "cumplimiento" in pregunta.lower():
            st.info(f"📊 El cumplimiento global actual es de **{cumplimiento_global:.2f}%**")
        elif "promedio" in pregunta.lower() and "ventas" in pregunta.lower():
            promedio_ventas = data['ventas'].mean()
            fig = px.histogram(data, x='producto', y='ventas', histfunc='avg', title="Promedio de ventas por producto")
            st.info(f"📉 El promedio de ventas es **${promedio_ventas:,.0f}**")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("🤔 Lo siento, aún no tengo una respuesta para esa pregunta.")
