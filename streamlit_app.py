import streamlit as st
import pandas as pd

# Cargar el archivo Excel
archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

# Procesar los datos
def handle_response(df):
    if archivo:
        try:
            # Comprobar si el archivo tiene las columnas necesarias
            if "hora" not in df.columns or "sucursal" not in df.columns or "ventas" not in df.columns:
                st.warning("El archivo cargado no contiene las columnas 'hora', 'sucursal' y 'ventas'. Asegúrate de que los datos estén correctamente estructurados.")
                return

            # Responder a preguntas sobre las ventas por hora y sucursal
            if "¿Cuáles son las horas de mayor venta en la sucursal?" in st.session_state.input_question:
                sucursal = st.text_input("Escribe la sucursal (ej. 'Norte'):", key="sucursal_input")
                if sucursal:
                    df_sucursal = df[df['sucursal'].str.lower() == sucursal.lower()]
                    ventas_por_hora = df_sucursal.groupby('hora')['ventas'].sum()
                    hora_maxima = ventas_por_hora.idxmax()
                    ventas_maximas = ventas_por_hora.max()
                    st.markdown(f"La hora de mayor venta en la sucursal {sucursal} es a las {hora_maxima} con un total de {ventas_maximas} ventas.")
            
            # Otras preguntas: total de ventas por sucursal
            elif "¿Cuál es el total de ventas de cada sucursal?" in st.session_state.input_question:
                total_ventas_sucursales = df.groupby('sucursal')['ventas'].sum()
                st.markdown("**Total de ventas por sucursal:**")
                st.write(total_ventas_sucursales)

            # Otras posibles preguntas
            elif "¿Cuál es el promedio de ventas por hora?" in st.session_state.input_question:
                promedio_ventas = df.groupby('hora')['ventas'].mean()
                st.markdown("**Promedio de ventas por hora:**")
                st.write(promedio_ventas)

            # Responder otras consultas, ajustando según el tipo de pregunta
            # ...

        except Exception as e:
            st.warning(f"⚠️ Error al generar análisis: {e}")

# Mostrar el historial de chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Mostrar el historial de chat
for i, (user, bot) in enumerate(st.session_state.chat_history):
    st.markdown(f"**🧑 Tú:** {user}")
    st.markdown(f"**🤖 Asistente:** {bot}")

    # Opción para exportar la conversación
    if st.button(f"📥 Exportar conversación .txt (Pregunta {i+1})"):
        chat_export = f"Tú: {user}\nAsistente: {bot}\n"
        st.download_button("Descargar como archivo .txt", chat_export, file_name=f"chat_gerencial_{i+1}.txt")

# Opción para limpiar el historial de chat
if st.button("🧹 Limpiar chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()
