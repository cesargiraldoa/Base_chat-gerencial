import streamlit as st
import openai
from fpdf import FPDF
import io

# Configuración de la API de OpenAI
openai.api_key = 'your_openai_api_key'

# Función para generar la respuesta con la API ChatCompletion de OpenAI
def generar_respuesta(pregunta):
    try:
        # Realiza una llamada a la nueva API ChatCompletion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # O el modelo que prefieras
            messages=[
                {"role": "system", "content": "Eres un asesor gerencial experto en ventas y análisis de datos."},
                {"role": "user", "content": pregunta}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Error al generar respuesta: {e}"

# Función para generar el PDF de la respuesta
def generar_pdf(respuesta):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, respuesta)
    
    # Guardar el archivo PDF en memoria
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Función para mostrar el formulario de preguntas y respuestas
def mostrar_pregunta_y_respuesta():
    # Mostrar un campo para ingresar la pregunta
    pregunta = st.text_input("Escribe tu pregunta:")

    if pregunta:
        respuesta = generar_respuesta(pregunta)
        st.write(respuesta)  # Mostrar la respuesta de la IA

        # Crear los botones para exportar la respuesta
        pdf_output = generar_pdf(respuesta)
        st.download_button(
            label="Descargar PDF",
            data=pdf_output,
            file_name="respuesta.pdf",
            mime="application/pdf"
        )
        
        st.download_button(
            label="Descargar TXT",
            data=respuesta,
            file_name="respuesta.txt",
            mime="text/plain"
        )

# Mostrar una nueva pregunta sin borrar las anteriores
def main():
    if 'input_question' not in st.session_state:
        st.session_state.input_question = ""
    
    # Pregunta nueva
    mostrar_pregunta_y_respuesta()

if __name__ == "__main__":
    main()
