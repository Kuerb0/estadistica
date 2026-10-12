"""Página de inicio: qué hay y por dónde empezar."""
import streamlit as st

LECCIONES = [
    ("medias", "📏", "Media, mediana y dispersión", "Resumir datos con pocos números, y por qué un dato extremo mueve unas medidas y otras no."),
    ("normal", "🔔", "La distribución normal", "La campana, la regla del 68-95-99,7 y cómo medir cuánto de raro es un valor."),
    ("tcl", "🎯", "El teorema central del límite", "Por qué las medias de muestras acaban siendo normales, sea cual sea el origen."),
    ("probabilidad", "🎲", "Probabilidad y grandes números", "Qué significa realmente «50 %» y por qué el azar se ordena al repetir."),
]
PROXIMAMENTE = ["Intervalos de confianza", "Contrastes de hipótesis y p-valor", "Correlación y regresión", "Muestreo y encuestas"]


def pagina(paginas):
    """paginas: {clave de la lección: st.Page}, para poder enlazar cada una."""
    st.title("📊 Estadística básica, jugando")
    st.markdown("Los principios de la estadística explicados con **simulaciones que se mueven**: cambias un control y ves al instante "
                "qué pasa. Sin fórmulas de golpe y sin saber programar.")
    for clave, icono, titulo, texto in LECCIONES:
        with st.container(border=True):
            st.markdown(f"### {icono} {titulo}")
            st.write(texto)
            st.page_link(paginas[clave], label="Empezar la lección", icon="➡️")
    st.subheader("Próximamente")
    st.write(" · ".join(PROXIMAMENTE))
    st.caption("Consejo: haz las lecciones en orden. Cada una usa ideas de la anterior.")
