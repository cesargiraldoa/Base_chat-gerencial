import openai
import os

# Asegúrate de tener esta variable como secreto en Streamlit Cloud
openai.api_key = os.getenv("OPENAI_API_KEY")

def generar_descripcion_clusters(df_clusters):
    try:
        # Convertimos la tabla en texto
        tabla_texto = df_clusters.to_string(index=False)

        # Creamos el mensaje para enviar al modelo
        mensaje = (
            "A continuación te presento una tabla con información de distintos clústeres de clientes. "
            "Por favor, genera una descripción clara y útil para un gerente comercial, "
            "indicando las características principales de cada clúster, sus diferencias y cualquier oportunidad relevante.\n\n"
            f"{tabla_texto}"
        )

        # Llamada a la API de OpenAI (nuevo formato)
        respuesta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente experto en análisis de datos comerciales."},
                {"role": "user", "content": mensaje}
            ],
            temperature=0.7
        )

        return respuesta.choices[0].message.content

    except Exception as e:
        return f"❌ Error al generar descripción con IA:\n\n{str(e)}"
