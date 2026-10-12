"""Página de inicio: qué hay y por dónde empezar."""
import streamlit as st

BLOQUES = [
    ("Datos y probabilidad", [
        ("medias", "📏", "Media, mediana y dispersión", "Resumir datos con pocos números, y por qué un dato extremo mueve unas medidas y otras no."),
        ("normal", "🔔", "La distribución normal", "La campana, la regla del 68-95-99,7 y cómo medir cuánto de raro es un valor."),
        ("probabilidad", "🎲", "Probabilidad y grandes números", "Qué significa realmente «50 %» y por qué el azar se ordena al repetir."),
        ("juegos", "🎰", "Juegos de probabilidad", "Monty Hall, el problema del cumpleaños y la suma de dados: donde la intuición falla."),
        ("tcl", "🎯", "El teorema central del límite", "Por qué las medias de muestras acaban siendo normales, sea cual sea el origen."),
    ]),
    ("Inferencia", [
        ("intervalos", "📐", "Intervalos de confianza", "Qué significa «95 %» de verdad, viéndolo repetido 50 veces."),
        ("contrastes", "⚖️", "Contrastes y p-valor", "Hipótesis nula, p-valor, errores de tipo I y II, potencia y tamaño de muestra."),
    ]),
    ("Modelos", [
        ("regresion", "📈", "Regresión lineal", "Una recta que se va acercando paso a paso a la mejor, con el error a la vista."),
        ("glm", "🔁", "GLM: convertir Y y X", "Familias y funciones de enlace, transformaciones de X y la trampa de modelar log(Y)."),
    ]),
]
PROXIMAMENTE = ["Correlación y causalidad", "Regresión múltiple", "Muestreo y encuestas", "ANOVA", "Bootstrap", "Regresión logística"]


def pagina(paginas):
    """paginas: {clave de la lección: st.Page}, para poder enlazar cada una."""
    st.title("📊 Estadística básica, jugando")
    st.markdown("Los principios de la estadística explicados con **simulaciones que se mueven**: cambias un control y ves al instante "
                "qué pasa. Sin fórmulas de golpe y sin saber programar.")
    for bloque, lecciones in BLOQUES:
        st.subheader(bloque)
        for i in range(0, len(lecciones), 2):
            for col, (clave, icono, titulo, texto) in zip(st.columns(2), lecciones[i:i + 2]):
                with col, st.container(border=True):
                    st.markdown(f"#### {icono} {titulo}")
                    st.write(texto)
                    st.page_link(paginas[clave], label="Empezar la lección", icon="➡️")
    st.subheader("Próximamente")
    st.write(" · ".join(PROXIMAMENTE))
    st.caption("Consejo: sigue el orden de arriba abajo. Cada lección usa ideas de las anteriores.")
