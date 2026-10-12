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
assert "Estadística básica" in inicio.title[0].value and len(inicio.get("page_link")) == 9, "una entrada por lección"

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

# 5. intervalos de confianza: a la larga aciertan el nivel elegido
at = abrir("intervalos")
assert not at.exception, at.exception
assert "50" in at.metric[3].value, at.metric[3].value                  # «N de 50» intervalos que aciertan
largo = float(at.metric[4].value.split()[0])
assert 92 < largo < 98, largo
at.select_slider(key="ic_nivel").set_value(0.8).run()
assert not at.exception and 76 < float(at.metric[4].value.split()[0]) < 84, "con el 80 %, aciertan un 80 % de las veces"
ancho = at.metric[1].value
at.slider(key="ic_n").set_value(200).run()
assert not at.exception and at.metric[1].value != ancho
at.button(key="ic_otra").click().run()
assert not at.exception, at.exception

# 6. contrastes: sin diferencia real se rechaza un α de las veces; con diferencia, la potencia sube con n
at = abrir("contrastes")
assert not at.exception, at.exception
at.slider(key="co_real").set_value(100.0).run()
assert not at.exception, at.exception
tipo1 = float(next(m for m in at.metric if m.label.startswith("Rechaza H0 (y H0 es cierta)")).value.split()[0])
assert 2.5 < tipo1 < 8, tipo1
at.slider(key="co_real").set_value(108.0).run()
pot_n30 = float(next(m for m in at.metric if m.label.startswith("Rechaza H0 (detecta")).value.split()[0])
at.slider(key="co_n").set_value(200).run()
pot_n200 = float(next(m for m in at.metric if m.label.startswith("Rechaza H0 (detecta")).value.split()[0])
assert pot_n200 > pot_n30 and pot_n200 > 95, (pot_n30, pot_n200)
at.button(key="co_otra").click().run()
assert not at.exception, at.exception

# 7. juegos: cambiar gana 2 de cada 3
at = abrir("juegos")
assert not at.exception, at.exception
quedarse, cambiar = (float(m.value.split()[0]) for m in at.metric[:2])
assert abs(quedarse - 33.3) < 5 and abs(cambiar - 66.7) < 5, (quedarse, cambiar)
at.slider(key="ju_personas").set_value(23).run()
assert not at.exception and any(m.value.startswith("50.") for m in at.metric), [m.value for m in at.metric]
at.slider(key="ju_dados").set_value(5).run()
assert not at.exception, at.exception

# 8. regresión: el descenso se acerca a la solución, y con un paso demasiado grande se avisa
at = abrir("regresion")
assert not at.exception, at.exception
at.slider(key="re_b1").set_value(1.5).run()
assert not at.exception, at.exception
at.select_slider(key="re_tasa").set_value(0.08).run()
assert not at.exception and any("sube en vez de bajar" in w.value for w in at.warning), "paso demasiado grande"
at.select_slider(key="re_tasa").set_value(0.01).run()
at.slider(key="re_total").set_value(1000).run()
at.slider(key="re_k").set_value(1000).run()
assert not at.exception and not at.warning
at.button(key="re_otros").click().run()
assert not at.exception, at.exception

# 9. GLM: todas las familias y enlaces se dibujan; transformar X; log(Y) frente a enlace log
at = abrir("glm")
assert not at.exception, at.exception
for fam in at.selectbox(key="glm_fam").options:
    at.selectbox(key="glm_fam").set_value(fam).run()
    assert not at.exception, (fam, at.exception)
    for enlace in at.selectbox(key=f"glm_enlace_{fam}").options:
        at.selectbox(key=f"glm_enlace_{fam}").set_value(enlace).run()
        assert not at.exception, (fam, enlace, at.exception)
at.slider(key="glm_b1").set_value(-2.0).run()                 # con la identidad la media puede salir negativa: aviso, no error
assert not at.exception, at.exception
at.selectbox(key="glm_real").set_value("1/x").run()
at.radio(key="glm_trans").set_value("1/x").run()
assert not at.exception and any("Has acertado" in s.value for s in at.success), [s.value for s in at.success]
at.radio(key="glm_trans").set_value("x²").run()
assert not at.exception and any("no es la mejor" in s.value for s in at.success)
print("TEST OK")
