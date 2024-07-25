# Archivo: app.py
import random
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go

# Función para el modelo de evaluación 360
def modelo_evaluacion_360(datos):
    promedios_por_evaluador = datos.mean()
    desviacion_estandar_por_competencia = datos.std(axis=1)
    
    n = len(datos.columns)
    error_estandar = desviacion_estandar_por_competencia / np.sqrt(n)
    promedio_por_competencia = datos.mean(axis=1)
    
    intervalo_confianza = stats.t.interval(confidence=0.95, df=n-1, 
                                           loc=promedio_por_competencia, 
                                           scale=error_estandar)
    
    promedio_general_por_competencia = datos.mean(axis=1)
    fortalezas = promedio_general_por_competencia.nlargest(3)
    areas_mejora = promedio_general_por_competencia.nsmallest(3)
    
    consistencia = datos.var(axis=1)
    
    return {
        'promedios_por_evaluador': promedios_por_evaluador,
        'desviacion_estandar_por_competencia': desviacion_estandar_por_competencia,
        'intervalo_confianza': intervalo_confianza,
        'fortalezas': fortalezas,
        'areas_mejora': areas_mejora,
        'consistencia': consistencia
    }

# Configuración de la página
st.set_page_config(page_title="Evaluación 360 Grados", layout="wide")

# Menú de navegación
selected = option_menu(
    menu_title=None,
    options=["Instrucciones", "Captura de Datos", "Resultados"],
    icons=["info-circle", "pencil-square", "graph-up"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# Definición de competencias genéricas reales
competencias = [
    "Liderazgo",
    "Comunicación efectiva",
    "Trabajo en equipo",
    "Resolución de problemas",
    "Adaptabilidad",
    "Innovación",
    "Toma de decisiones",
    "Orientación a resultados",
    "Inteligencia emocional",
    "Ética y valores"
]

# Definición de tipos de evaluadores
evaluadores = [
    "Autoevaluación",
    "Jefe directo",
    "Compañeros",
    "Subordinados",
    "Clientes internos/externos"
]

# Página de instrucciones
if selected == "Instrucciones":
    st.title('Instrucciones para la Evaluación 360 Grados')
    st.write("""
    Bienvenido a la herramienta de Evaluación 360 Grados. Esta evaluación es una oportunidad para recibir retroalimentación valiosa sobre su desempeño desde diferentes perspectivas. Por favor, siga estas instrucciones cuidadosamente:

    1. **Reflexión**: Antes de comenzar, tome un momento para reflexionar sobre su desempeño en las diferentes competencias que se evaluarán.

    2. **Honestidad**: Sea honesto en sus respuestas. Esta evaluación es una herramienta para el crecimiento personal y profesional.

    3. **Contexto**: Al evaluar, considere el comportamiento y desempeño general durante el último año, no solo incidentes aislados.

    4. **Escala de Evaluación y criterios**: 
        1. **Necesita mejorar significativamente**
        - Raramente colabora con otros miembros del equipo
        - Muestra poca disposición para compartir información o recursos
        - No cumple con sus responsabilidades dentro del equipo
        - Tiene dificultades para comunicarse efectivamente con los demás

        2. **Por debajo de las expectativas**
        - Colabora de manera inconsistente con otros miembros del equipo
        - Comparte información o recursos solo cuando se le solicita
        - Cumple parcialmente con sus responsabilidades dentro del equipo
        - Su comunicación con los demás es limitada o poco clara

        3. **Cumple con las expectativas**
        - Colabora regularmente con otros miembros del equipo
        - Comparte información y recursos de manera proactiva
        - Cumple con sus responsabilidades dentro del equipo
        - Se comunica de manera clara y efectiva con los demás

        4. **Supera las expectativas**
        - Fomenta activamente la colaboración entre los miembros del equipo
        - Comparte información y recursos de manera constante y oportuna
        - Asume responsabilidades adicionales para apoyar al equipo
        - Se comunica de manera excepcional, promoviendo el diálogo y la retroalimentación

        5. **Desempeño excepcional**
        - Lidera iniciativas de colaboración y motiva a otros a trabajar en equipo
        - Crea sistemas para compartir información y recursos de manera eficiente
        - Identifica y resuelve problemas que afectan el desempeño del equipo
        - Su comunicación inspira y influye positivamente en todo el equipo

    5. **Objetividad**: Intente ser lo más objetivo posible, basándose en comportamientos observables y resultados concretos.

    6. **Confidencialidad**: Sus respuestas serán tratadas con confidencialidad y se utilizarán de forma agregada para proporcionar retroalimentación.

    7. **Tiempo**: Tómese el tiempo necesario para completar la evaluación. Una reflexión cuidadosa proporcionará resultados más valiosos.

    Recuerde, el objetivo de esta evaluación es fomentar el desarrollo profesional y mejorar el desempeño general. ¡Su participación honesta y reflexiva es crucial para el éxito de este proceso!
    """)

# Página de captura de datos
elif selected == "Captura de Datos":
    st.title('Captura de Datos - Evaluación 360 Grados')

    st.write("""
    Por favor, evalúe cada competencia según la escala proporcionada. Reflexione cuidadosamente sobre cada aspecto antes de asignar una puntuación.
    """)

    data = {}
    for evaluador in evaluadores:
        st.subheader(f"Evaluación como {evaluador}")
        data[evaluador] = []
        for competencia in competencias:
            valor = st.slider(
                f"{competencia} - {evaluador}",
                min_value=1,
                max_value=5,
                value=random.randrange(1, 5),
                help=f"1 = Necesita mejorar significativamente, 5 = Desempeño sobresaliente"
            )
            data[evaluador].append(valor)

    df = pd.DataFrame(data, index=competencias)

    if st.button('Guardar Datos'):
        st.session_state['data'] = df
        st.success('Datos guardados exitosamente. Vaya a la página de Resultados para ver el análisis.')

# Página de resultados
elif selected == "Resultados":
    st.title('Resultados - Evaluación 360 Grados')

    if 'data' not in st.session_state:
        st.warning('No hay datos disponibles. Por favor, capture los datos primero.')
    else:
        df = st.session_state['data']
        resultados = modelo_evaluacion_360(df)

        # Gráfico de radar para promedios por evaluador
        st.subheader('Gráfico de Radar - Promedios por Evaluador')
        fig = go.Figure()
        for evaluador in df.columns:
            fig.add_trace(go.Scatterpolar(
                r=df[evaluador],
                theta=df.index,
                fill='toself',
                name=evaluador
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[1, 5])),
            showlegend=True
        )
        st.plotly_chart(fig)

        # Fortalezas y áreas de mejora
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Fortalezas')
            st.write(resultados['fortalezas'])
            st.markdown("""
            **Explicación**: Las fortalezas son las competencias con las puntuaciones más altas en promedio. 
            Estas son áreas donde el evaluado demuestra un buen desempeño y puede ser un ejemplo para otros.
            """)
        with col2:
            st.subheader('Áreas de Mejora')
            st.write(resultados['areas_mejora'])
            st.markdown("""
            **Explicación**: Las áreas de mejora son las competencias con las puntuaciones más bajas en promedio. 
            Estas son áreas donde el evaluado puede enfocarse para desarrollar y mejorar sus habilidades.
            """)

        # Consistencia entre evaluadores
        st.subheader('Variabilidad entre evaluadores')
        st.bar_chart(resultados['consistencia'])
        st.markdown("""
        **Explicación**: Muestra qué tan de acuerdo están los diferentes evaluadores en cada competencia. 
        - Valores bajos indican que los evaluadores tienden a estar de acuerdo.
        - Valores altos sugieren opiniones más variadas entre los evaluadores.
        Una alta inconsistencia puede indicar la necesidad de aclarar expectativas o criterios de evaluación para esa competencia.
        """)

        # Desviación estándar por competencia
        st.subheader('Variabilidad por competencia')
        st.bar_chart(resultados['desviacion_estandar_por_competencia'])
        st.markdown("""
        **Explicación**: La variabilidad de las puntuaciones para cada competencia.
        - Una variabilidad baja indica que las puntuaciones tienden a estar cerca del promedio.
        - Mientras que valores altos sugieren una mayor diferencia de opiniones entre puntuaciones.
        Competencias con alta desviación estándar pueden requerir una discusión más detallada para entender las diferentes percepciones.
        """)

# Instrucciones en la barra lateral
st.sidebar.title('Navegación')
st.sidebar.write("""
1. Comience en la página 'Instrucciones' para entender el proceso.
2. Vaya a 'Captura de Datos' para ingresar las evaluaciones.
3. Finalmente, revise los 'Resultados' para ver el análisis completo.
""")