import streamlit as st
import pandas as pd
import openai
from fpdf import FPDF
import io

# Inicialización de variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'input_question' not in st.session_state:
    st.session_state.input_question = ""

# Configuración de la clave de API de OpenAI
openai.api_key = "your-openai-api-key"

# Cargar archivo Excel de ventas
def cargar_ventas(file):
    df = pd.read_excel(file)
    return df

# Función para generar respuestas del modelo de IA
def generar_respuesta(pregunta, contexto):
    prompt_chat = f"""
    Basado en los datos proporcionados, responde esta pregunta de forma ejecutiva:
    {contexto}
    {pregunta}
    """
    try:
        respuesta_chat = openai.Completion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asesor gerencial experto en ventas y análisis de datos."},
                {"role": "user", "content": prompt_chat}
            ]
        )
        return respuesta_chat.choices[0].message['content']
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

# Función para generar y descargar el PDF
def generar_pdf(respuesta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Análisis de Ventas", ln=True, align='C')
    pdf.multi_cell(200, 10, txt=respuesta)
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Interfaz de usuario
st.title("Chat Gerencial - Análisis de Ventas")
file = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

if file:
    df = cargar_ventas(file)
    st.session_state.input_question = st.text_input("Escribe tu pregunta:")

    if st.button("Enviar pregunta"):
        if st.session_state.input_question:
            # Definir contexto como una descripción del dataset o cualquier análisis relevante
            contexto = df.describe().to_string()

            respuesta = generar_respuesta(st.session_state.input_question, contexto)

            # Mostrar la respuesta en el chat
            st.write("Respuesta:", respuesta)

            # Generar y permitir descarga del PDF con la respuesta
            pdf_output = generar_pdf(respuesta)
            st.download_button(
                label="Descargar respuesta como PDF",
                data=pdf_output,
                file_name="respuesta_ventas.pdf",
                mime="application/pdf"
            )

            # Exportar la conversación a .txt
            with open("conversacion.txt", "w") as f:
                f.write(f"Pregunta: {st.session_state.input_question}\n")
                f.write(f"Respuesta: {respuesta}\n")
            st.download_button(
                label="Exportar conversación (.txt)",
                data="conversacion.txt",
                file_name="conversacion.txt",
                mime="text/plain"
            )

            # Limpiar el chat
            if st.button("Limpiar chat"):
                st.session_state.chat_history.clear()
        else:
            st.warning("Por favor, ingresa una pregunta.")
