"""Estadística básica: lecciones interactivas con simulaciones. Para ejecutarla: streamlit run app.py
Cada lección está en paginas/; el cálculo, sin Streamlit y con tests, en nucleo.py (descriptiva y normal), inferencia.py (intervalos
y contrastes), azar.py (juegos) y modelos.py (regresión y GLM)."""
import streamlit as st

from paginas import contrastes, glm, inicio, intervalos, juegos, media_dispersion, normal, probabilidad, regresion, tcl

st.set_page_config(page_title="Estadística básica", page_icon="📊", layout="wide")

PAGINAS = {
    "medias": st.Page(media_dispersion.pagina, title="Media y dispersión", icon="📏", url_path="medias"),
    "normal": st.Page(normal.pagina, title="La normal", icon="🔔", url_path="normal"),
    "probabilidad": st.Page(probabilidad.pagina, title="Grandes números", icon="🎲", url_path="probabilidad"),
    "juegos": st.Page(juegos.pagina, title="Juegos de probabilidad", icon="🎰", url_path="juegos"),
    "tcl": st.Page(tcl.pagina, title="Teorema central del límite", icon="🎯", url_path="tcl"),
    "intervalos": st.Page(intervalos.pagina, title="Intervalos de confianza", icon="📐", url_path="intervalos"),
    "contrastes": st.Page(contrastes.pagina, title="Contrastes y p-valor", icon="⚖️", url_path="contrastes"),
    "regresion": st.Page(regresion.pagina, title="Regresión lineal", icon="📈", url_path="regresion"),
    "glm": st.Page(glm.pagina, title="GLM: convertir Y y X", icon="🔁", url_path="glm"),
}
INICIO = st.Page(lambda: inicio.pagina(PAGINAS), title="Inicio", icon="🏠", url_path="inicio", default=True)

st.navigation({
    "Empezar": [INICIO],
    "Datos y probabilidad": [PAGINAS[k] for k in ("medias", "normal", "probabilidad", "juegos", "tcl")],
    "Inferencia": [PAGINAS[k] for k in ("intervalos", "contrastes")],
    "Modelos": [PAGINAS[k] for k in ("regresion", "glm")],
}).run()
st.sidebar.caption("Parte de una colección de pequeñas webs interactivas.")
