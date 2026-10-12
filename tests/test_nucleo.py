"""Cálculo de las lecciones, sin Streamlit. Ejecutar desde la raíz: python tests/test_nucleo.py"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import nucleo

# resumen: valores conocidos
r = nucleo.resumen([1, 2, 2, 3, 4, 5, 10])
assert r["n"] == 7 and abs(r["media"] - 27 / 7) < 1e-12 and r["mediana"] == 3 and r["moda"] == 2
assert r["minimo"] == 1 and r["maximo"] == 10 and r["rango"] == 9
assert abs(r["desviacion"] - np.std([1, 2, 2, 3, 4, 5, 10], ddof=1)) < 1e-12 and abs(r["varianza"] - r["desviacion"] ** 2) < 1e-9
assert r["iqr"] == r["q3"] - r["q1"] == 2.5
assert nucleo.resumen([5])["desviacion"] == 0.0, "con un solo dato no hay dispersión que medir"

# un dato extremo mueve la media mucho más que la mediana
x = nucleo.conjunto("Alturas de adultos (cm): simétrico", 60)
a, b = nucleo.resumen(x), nucleo.resumen(nucleo.con_extremo(x, 400))
assert len(x) == 60 and 150 < a["media"] < 190 and (nucleo.conjunto("Alturas de adultos (cm): simétrico", 60) == x).all(), "reproducible"
assert b["media"] - a["media"] > 10 * abs(b["mediana"] - a["mediana"]) and b["iqr"] - a["iqr"] < 2
for nombre in nucleo.CONJUNTOS:
    assert len(nucleo.conjunto(nombre, 41)) == 41
assert nucleo.conjunto("Notas de un examen: dos grupos", 80).max() <= 10

# normal: valores de tabla
assert abs(nucleo.normal_cdf(0) - 0.5) < 1e-12 and abs(nucleo.normal_cdf(1.96) - 0.9750021) < 1e-6
assert abs(nucleo.prob_entre(-1, 1) - 0.6826895) < 1e-6 and abs(nucleo.prob_entre(1, -1) - 0.6826895) < 1e-6, "a y b se pueden dar al revés"
assert abs(nucleo.prob_entre(100, 120, 100, 20) - 0.3413447) < 1e-6, "con otra media y desviación"
assert abs(nucleo.normal_pdf(0) - 1 / math.sqrt(2 * math.pi)) < 1e-12
xs = np.linspace(-8, 8, 4001)
assert abs(np.trapezoid(nucleo.normal_pdf(xs), xs) - 1) < 1e-6, "el área total es 1"
assert nucleo.z_de(190, 170, 10) == 2.0
reg = nucleo.regla_empirica(0, 1)
assert [round(f["prob"], 3) for f in reg] == [0.683, 0.954, 0.997] and reg[1]["desde"] == -2 and reg[2]["hasta"] == 3

# teorema central del límite: la dispersión de las medias baja con la raíz de n
m1, pob = nucleo.medias_muestrales("Exponencial (muy asimétrica)", 1, 3000)
m25, _ = nucleo.medias_muestrales("Exponencial (muy asimétrica)", 25, 3000)
assert abs(m1.std() - pob.std()) < 0.08 and abs(m25.std() - nucleo.error_tipico(pob.std(), 25)) < 0.02
assert abs(m25.mean() - pob.mean()) < 0.03
asim = lambda v: float(((v - v.mean()) ** 3).mean() / v.std() ** 3)  # noqa: E731
assert asim(m1) > 1.5 > 0.8 > asim(m25) > -0.5, "la asimetría de la población desaparece al promediar"
assert nucleo.error_tipico(10, 100) == 1.0
for nombre in nucleo.POBLACIONES:
    assert len(nucleo.medias_muestrales(nombre, 3, 50)[0]) == 50

# grandes números
acum = nucleo.proporcion_acumulada(0.5, 5000)
assert len(acum) == 5000 and abs(acum[-1] - 0.5) < 0.03 and 0 <= acum.min() and acum.max() <= 1
assert (nucleo.proporcion_acumulada(0.3, 100, 7) == nucleo.proporcion_acumulada(0.3, 100, 7)).all()
assert nucleo.proporcion_acumulada(1.0, 10).min() == 1.0 and nucleo.proporcion_acumulada(0.0, 10).max() == 0.0
print("TEST OK")
