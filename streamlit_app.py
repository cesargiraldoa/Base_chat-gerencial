import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configura la página
st.set_page_config(page_title="Chat Gerencial - Análisis de Ventas", layout="wide")
st.title("🤖 Chat Gerencial - Análisis de Ventas")

# Cargar el archivo Excel
archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

# Función para calcular la tendencia y variación porcentual
def calcular_tendencia(df, columna_ventas, periodos="mensual"):
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
        if periodos == "mensual":
            df['mes'] = df['fecha'].dt.to_period('M')
        elif periodos == "trimestral":
            df['trimestre'] = df['fecha'].dt.to_period('Q')

        ventas_por_periodo = df.groupby('mes')[columna_ventas].sum() if periodos == "mensual" else df.groupby('trimestre')[columna_ventas].sum()

        variacion = ventas_por_periodo.pct_change().fillna(0) * 100
        return ventas_por_periodo, variacion
    else:
        st.warning("No se encuentra una columna de 'fecha' en el archivo. La comparación entre periodos no es posible.")

# Si el archivo está cargado, procesarlo
if archivo:
    df = pd.read_excel(archivo)
    st.subheader("Vista general de los datos cargados")
    st.dataframe(df)

    st.write("Columnas disponibles en el archivo:")
    st.write(df.columns)

    # =======================
    # 🔹 Sección de KPIs dinámicos
    # =======================
    st.markdown("## 📊 Resumen Ejecutivo de KPIs")
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes'] = df['fecha'].dt.to_period('M')

    meses_disponibles = sorted(df['mes'].unique())
    mes_seleccionado = st.selectbox("Selecciona un mes para ver los KPIs:", options=["Todos"] + list(map(str, meses_disponibles)))

    if mes_seleccionado != "Todos":
        df_filtrado = df[df['mes'] == mes_seleccionado]
    else:
        df_filtrado = df

    ventas_totales = df_filtrado['ventas_reales'].sum()
    promedio_mensual = df.groupby('mes')['ventas_reales'].sum().mean()
    producto_top = df_filtrado.groupby('producto')['ventas_reales'].sum().idxmax()
    sucursal_top = df_filtrado.groupby('sucursal')['ventas_reales'].sum().idxmax()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ventas Totales", f"{ventas_totales:,.0f}")
    col2.metric("Promedio Mensual Global", f"{promedio_mensual:,.0f}")
    col3.metric("Producto Más Vendido", producto_top)
    col4.metric("Sucursal Top", sucursal_top)

    # Resto del código sigue igual...
