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

    # Inicializar el historial de preguntas si no existe
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Campo de preguntas
    pregunta = st.text_input("Escribe tu pregunta sobre las ventas:")

    # Botón para enviar la pregunta
    if st.button('Enviar pregunta') and pregunta:
        # Buscar la columna de ventas, sin importar el nombre exacto
        columnas_posibles = [col for col in df.columns if 'venta' in col.lower()]

        if columnas_posibles:
            columna_ventas = columnas_posibles[0]  # Usamos la primera columna que contenga 'venta'
            st.write(f"Columna de ventas detectada: {columna_ventas}")

            respuesta = ""
            # Responder dependiendo de la pregunta
            if "tendencia positiva" in pregunta.lower() or "tendencia negativa" in pregunta.lower():
                periodo = "mensual"
                ventas_periodo, variacion_periodo = calcular_tendencia(df, columna_ventas, periodos=periodo)
                tendencia = "positiva" if variacion_periodo.iloc[-1] > 0 else "negativa"
                respuesta = f"La tendencia en ventas es {tendencia} para el periodo {ventas_periodo.index[-1]}."

                fig, ax = plt.subplots()
                ventas_periodo.plot(kind='bar', ax=ax)
                ax.set_title("Ventas por Mes")
                ax.set_ylabel("Ventas")
                st.pyplot(fig)

            elif "comparación" in pregunta.lower():
                if "producto" in pregunta.lower():
                    ventas_por_producto = df.groupby('producto')[columna_ventas].sum()
                    top_productos = ventas_por_producto.sort_values(ascending=False).head(10)
                    respuesta = "Top 10 productos de mayor venta:\n" + str(top_productos)

                    fig, ax = plt.subplots()
                    top_productos.plot(kind='bar', ax=ax)
                    ax.set_title("Top 10 Productos")
                    ax.set_ylabel("Ventas")
                    st.pyplot(fig)

                elif "sucursal" in pregunta.lower():
                    ventas_por_sucursal = df.groupby('sucursal')[columna_ventas].sum()
                    top_sucursales = ventas_por_sucursal.sort_values(ascending=False).head(10)
                    respuesta = "Top 10 sucursales de mayor venta:\n" + str(top_sucursales)

                    fig, ax = plt.subplots()
                    top_sucursales.plot(kind='bar', ax=ax)
                    ax.set_title("Top 10 Sucursales")
                    ax.set_ylabel("Ventas")
                    st.pyplot(fig)

            elif "ventas por sucursal" in pregunta.lower():
                ventas_sucursal = df.groupby('sucursal')[columna_ventas].sum()
                respuesta = "Total de ventas por sucursal:\n" + str(ventas_sucursal)

                fig, ax = plt.subplots()
                ventas_sucursal.plot(kind='bar', ax=ax)
                ax.set_title("Ventas por Sucursal")
                ax.set_ylabel("Ventas")
                st.pyplot(fig)

            elif "top 10 productos" in pregunta.lower():
                ventas_por_producto = df.groupby('producto')[columna_ventas].sum()
                top_productos_venta = ventas_por_producto.sort_values(ascending=False).head(10)
                bottom_productos_venta = ventas_por_producto.sort_values(ascending=True).head(10)

                respuesta = f"Top 10 productos con mayores ventas:\n{top_productos_venta}\n"
                respuesta += f"Top 10 productos con menores ventas:\n{bottom_productos_venta}"

                fig1, ax1 = plt.subplots()
                top_productos_venta.plot(kind='bar', ax=ax1)
                ax1.set_title("Top 10 Productos - Mayor Venta")
                ax1.set_ylabel("Ventas")
                st.pyplot(fig1)

                fig2, ax2 = plt.subplots()
                bottom_productos_venta.plot(kind='bar', ax=ax2)
                ax2.set_title("Top 10 Productos - Menor Venta")
                ax2.set_ylabel("Ventas")
                st.pyplot(fig2)

            else:
                respuesta = "Lo siento, no puedo responder a esa pregunta en este momento. Intenta otra consulta."

            st.session_state.chat_history.append(("Pregunta: " + pregunta, "Respuesta: " + respuesta))
            st.text_input("Escribe tu pregunta sobre las ventas:", value="", key="input_question")

    for i, (user, bot) in enumerate(st.session_state.chat_history):
        st.markdown(f"**🧑 Tú:** {user}")
        st.markdown(f"**🤖 Asistente:** {bot}")

else:
    st.info("Por favor, carga un archivo Excel para continuar.")
