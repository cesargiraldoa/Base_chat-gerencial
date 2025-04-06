import streamlit as st
import pandas as pd

# Configura la página
st.set_page_config(page_title="Chat Gerencial - Análisis de Ventas", layout="wide")
st.title("🤖 Chat Gerencial - Análisis de Ventas")

# Cargar el archivo Excel
archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

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
            # Aquí puedes agregar la lógica para responder de manera dinámica
            if "horas de mayor venta" in pregunta.lower():
                # Ejemplo de respuesta para una pregunta específica
                ventas_por_hora = df.groupby('hora')[columna_ventas].sum()
                hora_max = ventas_por_hora.idxmax()
                st.write(f"La hora de mayor venta es a las {hora_max} con {ventas_por_hora.max()} ventas.")
            elif "tendencia general" in pregunta.lower():
                # Respuesta para la tendencia general de ventas
                total_ventas = df[columna_ventas].sum()
                promedio_ventas = df[columna_ventas].mean()
                st.write(f"La tendencia general de las ventas es la siguiente: Total de ventas: {total_ventas}, Promedio de ventas: {promedio_ventas}.")
        else:
            st.warning("El archivo cargado no contiene una columna relacionada con 'ventas'. Asegúrate de que los datos estén correctamente estructurados.")
else:
    st.info("Por favor, carga un archivo Excel para continuar.")
