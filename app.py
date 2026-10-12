"""Estadística básica: lecciones interactivas con simulaciones. Para ejecutarla: streamlit run app.py
Cada lección está en paginas/ y todo el cálculo en nucleo.py (sin Streamlit, con tests)."""
import streamlit as st

from paginas import inicio, media_dispersion, normal, probabilidad, tcl

st.set_page_config(page_title="Estadística básica", page_icon="📊", layout="wide")

PAGINAS = {
    "medias": st.Page(media_dispersion.pagina, title="Media y dispersión", icon="📏", url_path="medias"),
    "normal": st.Page(normal.pagina, title="La normal", icon="🔔", url_path="normal"),
    "tcl": st.Page(tcl.pagina, title="Teorema central del límite", icon="🎯", url_path="tcl"),
    "probabilidad": st.Page(probabilidad.pagina, title="Probabilidad", icon="🎲", url_path="probabilidad"),
}
INICIO = st.Page(lambda: inicio.pagina(PAGINAS), title="Inicio", icon="🏠", url_path="inicio", default=True)

st.navigation([INICIO, *PAGINAS.values()]).run()
st.sidebar.caption("Parte de una colección de pequeñas webs interactivas.")
