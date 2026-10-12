"""La web entera con el probador de Streamlit (sin navegador): cada lección se abre y reacciona a sus controles.
Ejecutar desde la raíz: python tests/test_app.py"""
import os

from streamlit.testing.v1 import AppTest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def abrir(modulo):
    """Una lección sola (el probador no sabe cambiar de página cuando las páginas son funciones)."""
    codigo = f"import sys; sys.path.insert(0, {RAIZ!r}); from paginas import {modulo}; {modulo}.pagina()"
    return AppTest.from_string(codigo, default_timeout=60).run()


inicio = AppTest.from_file(os.path.join(RAIZ, "app.py"), default_timeout=60).run()
assert not inicio.exception, inicio.exception
assert "Estadística básica" in inicio.title[0].value and len(inicio.get("page_link")) >= 4, "una entrada por lección"

# 1. media y dispersión: un valor extraordinario mueve la media más que la mediana
at = abrir("media_dispersion")
assert not at.exception, at.exception
media0 = float(at.metric[0].value)
mediana0 = float(at.metric[1].value)
at.slider(key="md_extremo").set_value(at.slider(key="md_extremo").max).run()
assert not at.exception, at.exception
assert float(at.metric[0].value) - media0 > 5 * abs(float(at.metric[1].value) - mediana0), "la media se mueve mucho más que la mediana"
for nombre in at.selectbox(key="md_datos").options:
    assert not at.selectbox(key="md_datos").set_value(nombre).run().exception, nombre

# 2. normal: la regla del 68 % y la z
at = abrir("normal")
assert not at.exception, at.exception
assert at.metric[0].value == "68.3 %", at.metric[0].value
at.slider(key="no_mu").set_value(5.0).run()
at.slider(key="no_sigma").set_value(2.0).run()
assert not at.exception and at.metric[0].value == "68.3 %", "el rango por defecto sigue siendo ±1σ al cambiar μ y σ... o se ajusta"
at.number_input(key="no_valor").set_value(9.0).run()
assert any("z = 2.00" in m.value for m in at.markdown), [m.value for m in at.markdown][-3:]

# 3. teorema central del límite
at = abrir("tcl")
assert not at.exception, at.exception
for n in (1, 30, 200):
    at.slider(key="tcl_n").set_value(n).run()
    assert not at.exception, (n, at.exception)
for nombre in at.selectbox(key="tcl_pob").options:
    assert not at.selectbox(key="tcl_pob").set_value(nombre).run().exception, nombre
error_teorico = float(at.metric[1].value)
assert abs(float(at.metric[2].value) - error_teorico) < 0.15 * error_teorico + 0.01, "la dispersión real se parece a σ/√n"

# 4. probabilidad
at = abrir("probabilidad")
assert not at.exception, at.exception
at.select_slider(key="pr_n").set_value(5000).run()
assert not at.exception and float(at.metric[1].value) < 0.05, "con 5000 repeticiones la proporción se acerca a la real"
at.selectbox(key="pr_ej").set_value("Una probabilidad a mano").run()
at.slider(key="pr_p").set_value(0.8).run()
assert not at.exception and abs(float(at.metric[0].value) - 0.8) < 0.05
print("TEST OK")
