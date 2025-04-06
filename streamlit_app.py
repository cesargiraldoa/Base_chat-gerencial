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

# Función para manejar las respuestas y el historial
def handle_response():
    nueva_pregunta = st.session_state["input_question"]
    if nueva_pregunta:
        try:
            # Si tienes un archivo cargado, procesa los datos de ventas
            if 'df' in st.session_state:
                # Verifica si la columna 'ventas' está en el dataframe
                if 'ventas' in st.session_state['df'].columns:
                    # Datos extraídos del archivo Excel
                    ventas_data = st.session_state['df']

                    # Genera un contexto con datos específicos de ventas
                    ventas_totales = ventas_data['ventas'].sum()
                    ventas_promedio = ventas_data['ventas'].mean()
                    ventas_maximas = ventas_data['ventas'].max()
                    ventas_minimas = ventas_data['ventas'].min()

                    contexto = f"""
                    Se analizaron los datos de ventas con los siguientes resultados:
                    - Ventas totales: {ventas_totales}
                    - Ventas promedio: {ventas_promedio}
                    - Ventas máximas en un periodo: {ventas_maximas}
                    - Ventas mínimas en un periodo: {ventas_minimas}

                    Estos datos proporcionan una base sólida para analizar las tendencias de ventas a lo largo del tiempo y compararlas con metas establecidas.
                    """
                else:
                    st.warning("⚠️ El archivo cargado no contiene la columna 'ventas'. Asegúrate de que los datos estén correctamente estructurados.")
                    return

            else:
                # En caso de que no haya datos cargados
                contexto = "No se han cargado datos de ventas aún. Por favor, sube un archivo Excel de ventas."

            prompt_chat = f"""
{contexto}

Pregunta: {nueva_pregunta}
"""
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto analista en ventas y gerencia."},
                    {"role": "user", "content": prompt_chat}
                ]
            )
            respuesta = response.choices[0].message.content
            # Añadir la pregunta y respuesta al historial
            st.session_state.chat_history.append((nueva_pregunta, respuesta))
            st.session_state["input_question"] = ""  # Limpiar la entrada de la nueva pregunta
        except Exception as e:
            st.warning(f"⚠️ Error al generar análisis: {e}")

# Subir archivo Excel de ventas
archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

if archivo:
    df = pd.read_excel(archivo)
    st.session_state['df'] = df  # Guardar el dataframe en el estado de la sesión
    st.subheader("📊 Vista general de los datos")
    st.dataframe(df)

# Campo para ingresar nueva pregunta
with st.form(key="question_form"):
    nueva_pregunta = st.text_input("Escribe tu pregunta:", key="input_question")
    submit_button = st.form_submit_button("Enviar pregunta")
    if submit_button:
        handle_response()

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
