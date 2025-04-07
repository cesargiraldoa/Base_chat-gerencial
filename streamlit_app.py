import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Chat Gerencial - Análisis de Ventas", layout="wide")
st.title("🤖 Chat Gerencial - Análisis de Ventas")

archivo = st.file_uploader("Cargar archivo Excel de ventas", type=["xlsx"])

def calcular_tendencia(df, columna_ventas, periodos="mensual"):
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])
        if periodos == "mensual":
            df['mes'] = df['fecha'].dt.to_period('M')
        elif periodos == "trimestral":
            df['trimestre'] = df['fecha'].dt.to_period('Q')

        ventas_por_periodo = df.groupby('mes')[columna_ventas].sum() if periodos == "mensual" else df.groupby('trimestre')[columna_ventas].sum()
        variacion = ventas_por_periodo.pct_change().fillna(0) * 100
        return ventas_por_periodo, variacion
    else:
        st.warning("No se encuentra una columna de 'fecha' en el archivo. La comparación entre periodos no es posible.")

if archivo:
    df = pd.read_excel(archivo)
    st.subheader("Vista general de los datos cargados")
    st.dataframe(df)
    st.write("Columnas disponibles en el archivo:")
    st.write(df.columns)

    tabs = st.tabs(["📊 Dashboard", "📰 Diario de Análisis"])

    with tabs[0]:
        st.markdown("## 📊 Resumen Ejecutivo de KPIs")
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['mes'] = df['fecha'].dt.to_period('M')
        meses_disponibles = sorted(df['mes'].unique())
        mes_seleccionado = st.selectbox("Selecciona un mes para ver los KPIs:", options=["Todos"] + list(map(str, meses_disponibles)))
        df_filtrado = df[df['mes'] == mes_seleccionado] if mes_seleccionado != "Todos" else df

        ventas_totales = df_filtrado['ventas_reales'].sum()
        promedio_mensual = df.groupby('mes')['ventas_reales'].sum().mean()
        producto_top = df_filtrado.groupby('producto')['ventas_reales'].sum().idxmax()
        sucursal_top = df_filtrado.groupby('sucursal')['ventas_reales'].sum().idxmax()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ventas Totales", f"{ventas_totales:,.0f}")
        col2.metric("Promedio Mensual Global", f"{promedio_mensual:,.0f}")
        col3.metric("Producto Más Vendido", producto_top)
        col4.metric("Sucursal Top", sucursal_top)

        with st.sidebar:
            st.markdown("## 🤖 Preguntas rápidas")
            opciones_pregunta = [
                "¿Cuál es la tendencia de ventas mensual?",
                "¿Cuál es el promedio de ventas mensual?",
                "¿Cuáles son las ventas por hora?",
                "¿Cuáles son las ventas por día de la semana?",
                "Muéstrame la comparación trimestral"
            ]
            seleccion = st.selectbox("Selecciona una pregunta sugerida:", [""] + opciones_pregunta)
            st.markdown("---")
            st.markdown("Haz clic en una opción:")
            boton_presionado = ""
            for opcion in opciones_pregunta:
                if st.button(opcion, key=opcion):
                    boton_presionado = opcion
                    st.session_state.pregunta_auto = opcion
            st.markdown("---")
            pregunta = st.text_area("Escribe tu pregunta sobre las ventas:", value=boton_presionado or seleccion)
            enviar = st.button("Enviar pregunta", key="enviar")

        auto_pregunta = st.session_state.pop("pregunta_auto", None)
        ejecutar = enviar or auto_pregunta
        pregunta = auto_pregunta or pregunta

        if ejecutar and pregunta:
            columnas_posibles = [col for col in df.columns if 'venta' in col.lower()]
            if columnas_posibles:
                columna_ventas = columnas_posibles[0]
                st.write(f"Columna de ventas detectada: {columna_ventas}")
                df['trimestre'] = df['fecha'].dt.to_period('Q')
                df['hora'] = df['hora'].astype(str)
                df['dia_semana'] = df['fecha'].dt.day_name()

                respuesta = ""

                if any(kw in pregunta.lower() for kw in ["tendencia", "evolución", "ventas por mes"]):
                    ventas_periodo, variacion_periodo = calcular_tendencia(df, columna_ventas, periodos="mensual")
                    if len(ventas_periodo) < 2:
                        respuesta = "No hay suficientes datos de meses anteriores para calcular la tendencia mensual."
                    else:
                        tendencia = "positiva" if variacion_periodo.iloc[-1] > 0 else "negativa"
                        variacion_texto = f" ({variacion_periodo.iloc[-1]:.2f}%)"
                        respuesta = f"La tendencia en ventas es {tendencia}{variacion_texto} para el periodo {ventas_periodo.index[-1]}."
emoji = "📈🔼" if tendencia == "positiva" else "📉🔽"
respuesta = f"{emoji} " + respuesta
                        fig = px.bar(x=ventas_periodo.index.astype(str), y=ventas_periodo.values,
                                     labels={'x': 'Mes', 'y': 'Ventas'}, title="Ventas por Mes",
                                     color_discrete_sequence=['#00BFFF'])
                        fig.update_layout(height=300, margin=dict(t=30, b=30))
                        st.plotly_chart(fig, use_container_width=True)

                elif any(kw in pregunta.lower() for kw in ["promedio de ventas", "promedio mensual"]):
                    promedio_mensual = df.groupby('mes')[columna_ventas].mean()
                    promedio_general = promedio_mensual.mean()
                    respuesta = f"El promedio de ventas mensual es {promedio_general:,.2f} unidades."
                    fig = px.bar(x=promedio_mensual.index.astype(str), y=promedio_mensual.values,
                                 labels={'x': 'Mes', 'y': 'Promedio'}, title="Promedio de Ventas por Mes",
                                 color_discrete_sequence=['#9370DB'])
                    fig.update_layout(height=300, margin=dict(t=30, b=30))
                    st.plotly_chart(fig, use_container_width=True)

                elif "ventas por hora" in pregunta.lower():
                    ventas_hora = df.groupby('hora')[columna_ventas].sum().sort_index()
                    respuesta = "Ventas por hora:\n" + str(ventas_hora)
                    fig = px.bar(x=ventas_hora.index, y=ventas_hora.values, labels={'x': 'Hora', 'y': 'Ventas'},
                                 title="Ventas por Hora", color_discrete_sequence=['#1E90FF'])
                    fig.update_layout(height=300, margin=dict(t=30, b=30))
                    st.plotly_chart(fig, use_container_width=True)

                elif "ventas por día" in pregunta.lower() or "ventas por dia" in pregunta.lower():
                    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    ventas_dia = df.groupby('dia_semana')[columna_ventas].sum().reindex(dias_orden)
                    respuesta = "Ventas por día de la semana:\n" + str(ventas_dia)
                    fig = px.bar(x=ventas_dia.index, y=ventas_dia.values, labels={'x': 'Día', 'y': 'Ventas'},
                                 title="Ventas por Día de la Semana", color_discrete_sequence=['#FFD700'])
                    fig.update_layout(height=300, margin=dict(t=30, b=30))
                    st.plotly_chart(fig, use_container_width=True)

                elif "comparación trimestral" in pregunta.lower():
                    ventas_trimestre = df.groupby('trimestre')[columna_ventas].sum()
                    respuesta = "Ventas por trimestre:\n" + str(ventas_trimestre)
                    fig = px.bar(x=ventas_trimestre.index.astype(str), y=ventas_trimestre.values,
                                 labels={'x': 'Trimestre', 'y': 'Ventas'}, title="Ventas por Trimestre",
                                 color_discrete_sequence=['#008080'])
                    fig.update_layout(height=300, margin=dict(t=30, b=30))
                    st.plotly_chart(fig, use_container_width=True)

                if respuesta:
                    if "tendencia" in pregunta.lower():
                        respuesta += "

📊 **Análisis Gerencial Personalizado:**
"
                        respuesta += "🔹 Como CEO: aproveche la tendencia positiva para expandir mercados o refuerce acciones si es negativa.
"
                        respuesta += "🔹 Como Director Comercial: ajuste los objetivos mensuales en función de la variación reciente.
"
                        respuesta += "🔹 Como Analista de Ventas: profundice en segmentos que impulsan o frenan la tendencia.
"
                        respuesta += "📌 Recomendación: compare contra metas y determine si es necesario redireccionar campañas."
                    elif "promedio" in pregunta.lower():
                        respuesta += "

📊 **Análisis Gerencial Personalizado:**
"
                        respuesta += "🔹 Como CEO: valore la estabilidad o desviaciones del promedio mensual frente a la planeación estratégica.
"
                        respuesta += "🔹 Como Director Comercial: identifique meses que estén sobre o bajo el promedio para reforzar acciones.
"
                        respuesta += "🔹 Como Analista de Ventas: realice benchmarking contra años anteriores o contra la industria.
"
                        respuesta += "📌 Recomendación: optimice la planificación mensual de recursos y metas."
                    elif "hora" in pregunta.lower():
                        respuesta += "

📊 **Análisis Gerencial Personalizado:**
"
                        respuesta += "🔹 Como CEO: identifique si el comportamiento horario permite extender o reducir horarios operativos.
"
                        respuesta += "🔹 Como Director Comercial: evalúe campañas flash o promociones por hora pico.
"
                        respuesta += "🔹 Como Analista de Ventas: determine qué franjas horarias generan mayor conversión.
"
                        respuesta += "📌 Recomendación: refuerce atención y marketing en las horas de mayor impacto."
                    elif "día" in pregunta.lower() or "dia" in pregunta.lower():
                        respuesta += "

📊 **Análisis Gerencial Personalizado:**
"
                        respuesta += "🔹 Como CEO: identifique si hay días con bajo rendimiento que puedan ajustarse operativamente.
"
                        respuesta += "🔹 Como Director Comercial: planifique promociones para reforzar los días débiles.
"
                        respuesta += "🔹 Como Analista de Ventas: relacione los días con comportamiento estacional o campañas previas.
"
                        respuesta += "📌 Recomendación: diseñe estrategias comerciales diferenciadas por día de la semana."
                    elif "trimestre" in pregunta.lower():
                        respuesta += "

📊 **Análisis Gerencial Personalizado:**
"
                        respuesta += "🔹 Como CEO: tome decisiones de alto nivel a partir del rendimiento por trimestre.
"
                        respuesta += "🔹 Como Director Comercial: realinee recursos para el siguiente trimestre si hubo rezagos.
"
                        respuesta += "🔹 Como Analista de Ventas: compare evolución intertrimestral y destaque productos o canales.
"
                        respuesta += "📌 Recomendación: use esta vista como base para el forecast del siguiente trimestre."

                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []
                st.session_state.chat_history.append(("Pregunta: " + pregunta, "Respuesta: " + respuesta))

    with tabs[1]:
        st.markdown("### 📰 Resumen Diario de Inteligencia Comercial")
        if "chat_history" in st.session_state and st.session_state.chat_history:
            for i, (user, bot) in enumerate(reversed(st.session_state.chat_history)):
                with st.container():
                    st.markdown(f"#### 🗓️ Entrada {len(st.session_state.chat_history) - i}")
                    st.markdown(f"**🧑 Pregunta:** {user}")
                    st.markdown(f"**📌 Resumen y Análisis:**\n{bot}")
                    st.markdown("---")
        else:
            st.info("Aún no hay entradas registradas. Haz preguntas desde el dashboard para generar tu diario gerencial.")

else:
    st.info("Por favor, carga un archivo Excel para continuar.")
