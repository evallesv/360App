import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.graph_objects as go

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

st.title('Evaluación 360 Grados')

# Ingreso de datos
st.header('Ingreso de Datos')
num_competencias = st.number_input('Número de competencias', min_value=1, max_value=10, value=5)
num_evaluadores = st.number_input('Número de tipos de evaluadores', min_value=1, max_value=5, value=4)

competencias = [st.text_input(f'Nombre de la competencia {i+1}', value=f'Competencia {i+1}') for i in range(num_competencias)]
evaluadores = [st.text_input(f'Tipo de evaluador {i+1}', value=f'Evaluador {i+1}') for i in range(num_evaluadores)]

data = {}
for evaluador in evaluadores:
    data[evaluador] = [st.slider(f'{competencia} - {evaluador}', 1, 5, 3) for competencia in competencias]

df = pd.DataFrame(data, index=competencias)

if st.button('Calcular Resultados'):
    resultados = modelo_evaluacion_360(df)
    
    st.header('Resultados')
    
    # Gráfico de radar para promedios por evaluador
    fig = go.Figure()
    for evaluador in evaluadores:
        fig.add_trace(go.Scatterpolar(
            r=df[evaluador],
            theta=competencias,
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
    st.subheader('Consistencia entre evaluadores')
    st.bar_chart(resultados['consistencia'])
    st.markdown("""
    **Explicación**: La consistencia muestra qué tan de acuerdo están los diferentes evaluadores en cada competencia. 
    - Valores bajos indican que los evaluadores tienden a estar de acuerdo.
    - Valores altos sugieren opiniones más variadas entre los evaluadores.
    Una alta inconsistencia puede indicar la necesidad de aclarar expectativas o criterios de evaluación para esa competencia.
    """)
    
    # Desviación estándar por competencia
    st.subheader('Desviación estándar por competencia')
    st.bar_chart(resultados['desviacion_estandar_por_competencia'])
    st.markdown("""
    **Explicación**: La desviación estándar mide la variabilidad de las puntuaciones para cada competencia.
    - Una desviación estándar baja indica que las puntuaciones tienden a estar cerca del promedio.
    - Una desviación estándar alta sugiere una mayor dispersión en las puntuaciones.
    Competencias con alta desviación estándar pueden requerir una discusión más detallada para entender las diferentes percepciones.
    """)

st.sidebar.header('Instrucciones')
st.sidebar.write("""
1. Ingrese el número de competencias y tipos de evaluadores.
2. Proporcione nombres para las competencias y tipos de evaluadores.
3. Use los sliders para ingresar las calificaciones (1-5) para cada competencia y evaluador.
4. Haga clic en 'Calcular Resultados' para ver el análisis.
""")