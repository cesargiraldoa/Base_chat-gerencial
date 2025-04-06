import streamlit as st
import pandas as pd
from openai import OpenAI
from fpdf import FPDF
import io

# Configura el cliente de OpenAI usando el secreto
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Configuración de la página
st.set_page_config(page_title="Chat Gerencial - Ventas", layout="wide")
st.title("🤖 Chat Gerencial - Análisis de Ventas")

# Si no existe el historial de preguntas, inicialízalo
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Cargar archivo Excel de ventas
archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

# Procesar los datos
def handle_response(df):
    if archivo:
        try:
            # Realizar análisis de ventas
            ventas = df['ventas_reales']
            meta_producto = df['meta_producto']
            meta_sucursal = df['meta_sucursal']
            meta_global = df['meta_global']

            # Total de ventas por sucursal
            ventas_sucursal = df.groupby('sucursal')['ventas_reales'].sum()

            # Análisis por producto
            ventas_producto = df.groupby('producto')['ventas_reales'].sum()

            # Análisis de cumplimiento de metas
            cumplimiento_producto = df['ventas_reales'] / df['meta_producto'] * 100
            cumplimiento_sucursal = df.groupby('sucursal')['ventas_reales'].sum() / df.groupby('sucursal')['meta_sucursal'].sum() * 100

            respuesta = f"Análisis de ventas y cumplimiento de metas:\n\n"
            respuesta += f"- Ventas totales por sucursal:\n{ventas_sucursal}\n"
            respuesta += f"- Ventas totales por producto:\n{ventas_producto}\n"
            respuesta += f"- Cumplimiento de metas por producto:\n{cumplimiento_producto.mean():.2f}%\n"
            respuesta += f"- Cumplimiento de metas por sucursal:\n{cumplimiento_sucursal}\n"

            # Añadir la pregunta y respuesta al historial
            st.session_state.chat_history.append(("Análisis de ventas y metas", respuesta))
            st.session_state["input_question"] = ""  # Limpiar la entrada de la nueva pregunta

        except Exception as e:
            st.warning(f"⚠️ Error al generar análisis: {e}")

# Campo para ingresar nueva pregunta
with st.form(key="question_form"):
    nueva_pregunta = st.text_input("Escribe tu pregunta:", key="input_question")
    submit_button = st.form_submit_button("Enviar pregunta")
    if submit_button:
        handle_response(df)

# Mostrar el historial de chat (pregunta y respuesta)
for i, (user, bot) in enumerate(st.session_state.chat_history):
    st.markdown(f"**🧑 Tú:** {user}")
    st.markdown(f"**🤖 Asistente:** {bot}")

    # Opción para exportar la conversación
    if st.button(f"📥 Exportar conversación .txt (Pregunta {i+1})"):
        chat_export = f"Tú: {user}\nAsistente: {bot}\n"
        buffer = io.StringIO()
        buffer.write(chat_export)
        st.download_button("Descargar como archivo .txt", buffer.getvalue(), file_name=f"chat_gerencial_{i+1}.txt")
        
        # Exportar como PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Tú: {user}\nAsistente: {bot}\n")
        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        st.download_button(
            label=f"📄 Exportar como PDF (Pregunta {i+1})",
            data=pdf_output.getvalue(),
            file_name=f"chat_gerencial_{i+1}.pdf",
            mime="application/pdf"
        )

# Opción para limpiar el historial de chat
if st.button("🧹 Limpiar chat"):
    st.session_state.chat_history = []
    st.experimental_rerun()
