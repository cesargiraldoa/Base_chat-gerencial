import streamlit as st
import openai
import pandas as pd
from fpdf import FPDF
import io

# Establecer tu clave de API de OpenAI
openai.api_key = "tu_api_key_de_openai"

# Inicializa el historial de preguntas y respuestas de la sesión
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Función para generar el PDF
def generar_pdf(respuesta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Análisis de Ventas", ln=True, align="C")
    pdf.ln(10)
    pdf.multi_cell(200, 10, txt=respuesta)
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Función para obtener respuesta de OpenAI
def obtener_respuesta(pregunta):
    # Agregar pregunta al historial
    st.session_state.chat_history.append({"role": "user", "content": pregunta})

    # Generar la respuesta utilizando el modelo de OpenAI (nueva versión)
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # O la versión más actual
            prompt=pregunta,
            max_tokens=150
        )

        respuesta = response['choices'][0]['text']
        st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
        return respuesta
    except Exception as e:
        st.error(f"Error al generar respuesta: {e}")
        return None

# Interfaz de usuario en Streamlit
st.title("Chat Gerencial - Análisis de Ventas")
st.subheader("Cargar archivo Excel de ventas")
archivo = st.file_uploader("Sube tu archivo de ventas", type="xlsx")

if archivo:
    df = pd.read_excel(archivo)
    st.dataframe(df)

# Mostrar historial de chat
if len(st.session_state.chat_history) > 0:
    for msg in st.session_state.chat_history:
        role = "Usuario" if msg["role"] == "user" else "Asesor"
        st.write(f"{role}: {msg['content']}")

# Espacio para las preguntas
input_question = st.text_input("Escribe tu pregunta:")

if st.button("Enviar pregunta"):
    if input_question:
        # Obtener la respuesta
        respuesta = obtener_respuesta(input_question)
        
        if respuesta:
            # Mostrar la respuesta en el chat
            st.write(f"Respuesta: {respuesta}")
            
            # Crear el PDF con la respuesta
            pdf_output = generar_pdf(respuesta)
            
            # Opción para descargar el PDF
            st.download_button("Descargar PDF", pdf_output, file_name="respuesta_analisis_ventas.pdf", mime="application/pdf")
            
            # Opción para exportar la conversación en .txt
            conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.chat_history])
            st.download_button("Exportar conversación (.txt)", conversation_text, file_name="conversacion_analisis_ventas.txt", mime="text/plain")

# Limpiar el chat
if st.button("Limpiar chat"):
    st.session_state.chat_history = []
