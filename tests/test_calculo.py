"""Inferencia, juegos de azar, regresión y GLM, sin Streamlit. Ejecutar desde la raíz: python tests/test_calculo.py"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import azar
import inferencia as inf
import modelos as mod

# ---- distribuciones: valores de tabla
assert abs(inf.beta_incompleta(2, 2, 0.5) - 0.5) < 1e-12 and inf.beta_incompleta(3, 2, 0) == 0 and inf.beta_incompleta(3, 2, 1) == 1
for gl, esperado in ((1, 12.7062), (5, 2.5706), (10, 2.2281), (30, 2.0423), (200, 1.9719)):
    assert abs(inf.t_ppf(0.975, gl) - esperado) < 1e-3, (gl, inf.t_ppf(0.975, gl))
assert abs(inf.t_cdf(0, 7) - 0.5) < 1e-12 and abs(inf.t_cdf(2.0, 10) + inf.t_cdf(-2.0, 10) - 1) < 1e-12
assert abs(inf.z_ppf(0.975) - 1.959964) < 1e-5 and abs(inf.z_ppf(0.5)) < 1e-9

# ---- intervalos de confianza: a la larga contienen la media real el nivel de las veces
x = np.array([4.9, 5.1, 5.3, 4.7, 5.0, 5.2, 4.8, 5.4])
d, h = inf.intervalo_media(x, 0.95)
ee = x.std(ddof=1) / math.sqrt(8)
assert abs((d + h) / 2 - x.mean()) < 1e-9 and abs((h - d) / 2 - 2.3646 * ee) < 1e-3, "t con 7 grados de libertad"
for nivel in (0.8, 0.95, 0.99):
    cubre = inf.simular_intervalos(10, 2, 8, nivel, 6000)[2].mean()
    assert abs(cubre - nivel) < 0.02, (nivel, cubre)
d90, h90, _ = inf.simular_intervalos(10, 2, 8, 0.90, 50)
d99, h99, _ = inf.simular_intervalos(10, 2, 8, 0.99, 50)
assert ((h99 - d99) > (h90 - d90)).all(), "más confianza, intervalos más anchos (misma semilla)"
assert (inf.simular_intervalos(10, 2, 100, 0.95, 50)[1] - inf.simular_intervalos(10, 2, 100, 0.95, 50)[0]).mean() < \
    (h90 - d90).mean(), "más datos, intervalos más estrechos"

# ---- contrastes
r = inf.prueba_t(x, 5.0)
assert r["gl"] == 7 and abs(r["t"] - (x.mean() - 5.0) / r["ee"]) < 1e-12 and 0.5 < r["p"] <= 1
assert inf.prueba_t(x, 3.0)["p"] < 1e-4, "una media muy lejana de la hipótesis nula da un p-valor diminuto"
p0 = inf.simular_pvalores(5, 5, 1, 20, 3000)
assert abs((p0 < 0.05).mean() - 0.05) < 0.015, "con H0 cierta, se rechaza un α de las veces (error de tipo I)"
assert abs(np.median(p0) - 0.5) < 0.06 and abs((p0 < 0.5).mean() - 0.5) < 0.04, "bajo H0 los p-valores son uniformes"
p1 = inf.simular_pvalores(5.8, 5, 1, 20, 2000)
assert (p1 < 0.05).mean() > 0.9 > 0.2 > (inf.simular_pvalores(5.1, 5, 1, 20, 2000) < 0.05).mean() - 0.0 > 0.04
assert abs(inf.potencia_z(5, 5, 1, 20) - 0.05) < 1e-6, "sin diferencia real, la potencia es α"
assert inf.potencia_z(5.5, 5, 1, 20) < inf.potencia_z(5.5, 5, 1, 80) < inf.potencia_z(5.8, 5, 1, 80) <= 1
assert abs(inf.potencia_z(5.0 + 2.8016 / math.sqrt(20), 5, 1, 20) - 0.8) < 0.01
assert inf.tamano_para_potencia(0.5, 1) == 32 and inf.tamano_para_potencia(0.25, 1) > 3.9 * 32

# ---- juegos
quedarse, cambiar = azar.monty_hall(30000)
assert quedarse + cambiar == 30000 and abs(cambiar / 30000 - 2 / 3) < 0.01 and abs(quedarse / 30000 - 1 / 3) < 0.01
assert abs(azar.cumpleanos_prob(23) - 0.5073) < 1e-3 and azar.cumpleanos_prob(1) == 0 and azar.cumpleanos_prob(366) == 1 \
    and azar.cumpleanos_prob(70) > 0.999
assert abs(azar.cumpleanos_sim(23, 20000) - azar.cumpleanos_prob(23)) < 0.012
v, sim, exacta = azar.suma_dados(2, 40000)
assert list(v) == list(range(2, 13)) and abs(exacta.sum() - 1) < 1e-12 and abs(exacta[5] - 6 / 36) < 1e-12
assert np.abs(sim - exacta).max() < 0.01 and len(azar.suma_dados(4, 10)[0]) == 21

# ---- regresión lineal
x = np.array([0.0, 1, 2, 3, 4])
assert mod.minimos_cuadrados(x, 2 + 3 * x) == (2.0, 3.0) or np.allclose(mod.minimos_cuadrados(x, 2 + 3 * x), (2.0, 3.0))
xs, ys = mod.generar_recta(200, 1.5, 4.0, 2.0)
b0, b1 = mod.minimos_cuadrados(xs, ys)
assert abs(b1 - 1.5) < 0.2 and abs(b0 - 4.0) < 0.6 and 0.7 < mod.r_cuadrado(xs, ys, b0, b1) < 1
assert mod.suma_cuadrados(xs, ys, b0, b1) <= mod.suma_cuadrados(xs, ys, b0 + 0.3, b1) and \
    mod.suma_cuadrados(xs, ys, b0, b1) <= mod.suma_cuadrados(xs, ys, b0, b1 - 0.05), "MCO es el mínimo"
camino = mod.descenso_gradiente(xs, ys, 0.01, 4000)
assert camino.shape == (4001, 3) and np.allclose(camino[0], (0, 0, mod.suma_cuadrados(xs, ys, 0, 0)))
assert abs(camino[-1, 0] - b0) < 0.05 and abs(camino[-1, 1] - b1) < 0.01, "el descenso llega a la solución exacta"
assert (np.diff(camino[:, 2]) <= 1e-9).all(), "con una tasa pequeña, el error nunca sube"
assert mod.descenso_gradiente(xs, ys, 0.5, 30)[-1, 2] > 1e6, "con una tasa demasiado grande, se dispara"

# ---- enlaces: ida y vuelta, y derivadas
eta = np.array([-1.5, -0.2, 0.4, 1.3])
for nombre, (g, ginv, dmu) in mod.ENLACES.items():
    e = np.abs(eta) + 0.5 if nombre in ("inversa", "raíz", "log") else eta
    mu = ginv(e)
    assert np.allclose(g(mu), e), nombre
    paso = 1e-6
    assert np.allclose((ginv(e + paso) - ginv(e - paso)) / (2 * paso), dmu(e), rtol=1e-5), nombre
assert np.allclose(mod.media_desde_predictor([0.0], "logit"), 0.5) and np.allclose(mod.predictor_desde_media([np.e], "log"), 1)
for nombre, fam in mod.FAMILIAS.items():
    assert fam["canonico"] in mod.ENLACES and set(fam["enlaces"]) <= set(mod.ENLACES) and fam["canonico"] in fam["enlaces"] + [fam["canonico"]], nombre

# ---- GLM: se recuperan los coeficientes con muchos datos
rng = np.random.default_rng(3)
xg = rng.uniform(0, 4, 6000)
for familia, enlace, (c0, c1), tol in (("Poisson", "log", (0.5, 0.4), 0.05), ("Gamma", "log", (1.0, 0.3), 0.05),
                                        ("Binomial", "logit", (-1.0, 0.8), 0.15), ("Normal (gaussiana)", "identidad", (2.0, 1.5), 0.1),
                                        ("Gaussiana inversa", "log", (0.8, 0.2), 0.08)):
    mu = mod.media_desde_predictor(c0 + c1 * xg, enlace)
    y = mod.simular_y(familia, mu, 5, 0.3)
    a0, a1, it = mod.ajustar_glm(xg, y, familia, enlace)
    assert abs(a0 - c0) < tol and abs(a1 - c1) < tol and it < 60, (familia, a0, a1, it)
assert mod.ajustar_glm(xg, mod.simular_y("Poisson", np.exp(0.5 + 0.4 * xg), 5), "Poisson")[:2] == mod.ajustar_glm(
    xg, mod.simular_y("Poisson", np.exp(0.5 + 0.4 * xg), 5), "Poisson", "log")[:2], "sin decir enlace, el canónico"
assert set(np.unique(mod.simular_y("Binomial", np.full(100, .4), 1))) <= {0.0, 1.0}
assert (mod.simular_y("Poisson", np.full(100, 3.0), 1) % 1 == 0).all() and (mod.simular_y("Gamma", np.full(100, 3.0), 1) > 0).all()
n0, n1, _ = mod.ajustar_glm(xs, ys, "Normal (gaussiana)", "identidad")
assert abs(n0 - b0) < 1e-6 and abs(n1 - b1) < 1e-6, "GLM normal con enlace identidad = mínimos cuadrados"

# ---- log(Y) frente a enlace log: la media de log(Y) no es el log de la media de Y
xl = rng.uniform(0, 3, 8000)
yl = mod.simular_y("Gamma", np.exp(1.0 + 0.5 * xl), 9, 1.0)         # cola muy a la derecha
(m0, m1), (g0, g1) = mod.comparar_log_y(xl, yl)
assert abs(g0 - 1.0) < 0.1 and abs(g1 - 0.5) < 0.05, "el GLM con enlace log recupera la media de Y"
assert m0 < g0 - 0.3 and abs(m1 - 0.5) < 0.05, "MCO sobre log(Y) deja la ordenada más baja: deshacer el log subestima la media"

# ---- transformar X
xt = np.linspace(1, 20, 80)
assert mod.correlacion_con(xt, np.log(xt), "log(x)") > 0.999 > mod.correlacion_con(xt, np.log(xt), "x (sin transformar)") > 0.9
assert mod.correlacion_con(xt, 3 / xt, "1/x") > 0.999 and mod.correlacion_con(xt, np.sqrt(xt), "√x") > 0.999
assert mod.correlacion_con(xt, xt ** 2, "x²") > 0.999 and set(mod.TRANSFORMACIONES_X) >= {"log(x)", "√x", "x²", "1/x"}
print("TEST OK")
