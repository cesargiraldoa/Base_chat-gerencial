import streamlit as st
import pandas as pd

# Configura la página
st.set_page_config(page_title="Chat Gerencial - Análisis de Ventas", layout="wide")
st.title("🤖 Chat Gerencial - Análisis de Ventas")

# Cargar el archivo Excel
archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

# Función para calcular la tendencia y variación porcentual
def calcular_tendencia(df, columna_ventas, periodos="mensual"):
    # Verifica si hay una columna de fechas
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
        if periodos == "mensual":
            df['mes'] = df['fecha'].dt.to_period('M')
        elif periodos == "trimestral":
            df['trimestre'] = df['fecha'].dt.to_period('Q')

        # Agrupamos por el periodo elegido (mes o trimestre)
        ventas_por_periodo = df.groupby('mes')[columna_ventas].sum() if periodos == "mensual" else df.groupby('trimestre')[columna_ventas].sum()

        # Calculamos la tendencia (porcentaje de variación entre los periodos)
        variacion = ventas_por_periodo.pct_change().fillna(0) * 100  # En porcentaje
        return ventas_por_periodo, variacion
    else:
        st.warning("No se encuentra una columna de 'fecha' en el archivo. La comparación entre periodos no es posible.")

# Si el archivo está cargado, procesarlo
if archivo:
    # Lee los datos del archivo
    df = pd.read_excel(archivo)
    st.subheader("Vista general de los datos cargados")
    st.dataframe(df)  # Mostrar los datos cargados
    
    # Verificar las columnas del archivo
    st.write("Columnas disponibles en el archivo:")
    st.write(df.columns)
    
    # Campo de preguntas
    pregunta = st.text_input("Escribe tu pregunta sobre las ventas:")

    if pregunta:
        # Buscar la columna de ventas, sin importar el nombre exacto
        columnas_posibles = [col for col in df.columns if 'venta' in col.lower()]
        
        if columnas_posibles:
            columna_ventas = columnas_posibles[0]  # Usamos la primera columna que contenga 'venta'
            st.write(f"Columna de ventas detectada: {columna_ventas}")
            
            # Responder dependiendo de la pregunta
            if "tendencia positiva" in pregunta.lower() or "tendencia negativa" in pregunta.lower():
                # Calcular la tendencia por sucursal o producto
                periodo = "mensual"  # Ajustar el periodo a comparar (mensual/trimestral)
                ventas_periodo, variacion_periodo = calcular_tendencia(df, columna_ventas, periodos=periodo)
                
                tendencia = "positiva" if variacion_periodo.iloc[-1] > 0 else "negativa"
                st.write(f"La tendencia en ventas es {tendencia} para el periodo {ventas_periodo.index[-1]}.")

            elif "comparación" in pregunta.lower():
                # Comparativo entre productos o sucursales
                if "producto" in pregunta.lower():
                    ventas_por_producto = df.groupby('producto')[columna_ventas].sum()
                    top_productos = ventas_por_producto.sort_values(ascending=False).head(10)
                    st.write("Top 10 productos de mayor venta:")
                    st.write(top_productos)
                elif "sucursal" in pregunta.lower():
                    ventas_por_sucursal = df.groupby('sucursal')[columna_ventas].sum()
                    top_sucursales = ventas_por_sucursal.sort_values(ascending=False).head(10)
                    st.write("Top 10 sucursales de mayor venta:")
                    st.write(top_sucursales)

            elif "ventas por sucursal" in pregunta.lower():
                # Total de ventas por sucursal
                ventas_sucursal = df.groupby('sucursal')[columna_ventas].sum()
                st.write("Total de ventas por sucursal:")
                st.write(ventas_sucursal)

            elif "top 10 productos" in pregunta.lower():
                # Mostrar el top 10 productos de mayor y menor venta
                ventas_por_producto = df.groupby('producto')[columna_ventas].sum()
                top_productos_venta = ventas_por_producto.sort_values(ascending=False).head(10)
                bottom_productos_venta = ventas_por_producto.sort_values(ascending=True).head(10)

                st.write("Top 10 productos con mayores ventas:")
                st.write(top_productos_venta)
                st.write("Top 10 productos con menores ventas:")
                st.write(bottom_productos_venta)

            else:
                st.write("Lo siento, no puedo responder a esa pregunta en este momento. Intenta otra consulta.")
        else:
            st.warning("El archivo cargado no contiene una columna relacionada con 'ventas'. Asegúrate de que los datos estén correctamente estructurados.")
else:
    st.info("Por favor, carga un archivo Excel para continuar.")
