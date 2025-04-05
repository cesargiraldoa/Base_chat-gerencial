import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def generar_respuesta(prompt_usuario):
    try:
        respuesta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un analista de datos experto en análisis de ventas y operaciones."},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error al generar respuesta con IA: {str(e)}"
