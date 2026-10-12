"""Cálculo de las lecciones de estadística básica, sin Streamlit (así se puede probar sin abrir la web).
Solo usa numpy: la normal se calcula con math.erf."""
import math

import numpy as np

# ------------------------------------------------------------------ estadística descriptiva
CONJUNTOS = {
    "Alturas de adultos (cm): simétrico": ("normal", {"loc": 170, "scale": 8}),
    "Sueldos mensuales (€): con cola a la derecha": ("lognormal", {"mean": 7.4, "sigma": 0.45}),
    "Notas de un examen: dos grupos": ("dos_grupos", {}),
}


def conjunto(nombre, n=60, semilla=1):
    """Datos de ejemplo reproducibles (misma semilla, mismos datos)."""
    rng = np.random.default_rng(semilla)
    familia, p = CONJUNTOS[nombre]
    if familia == "normal":
        x = rng.normal(p["loc"], p["scale"], n)
    elif familia == "lognormal":
        x = rng.lognormal(p["mean"], p["sigma"], n)
    else:
        x = np.concatenate([rng.normal(4.5, 0.9, n // 2), rng.normal(7.8, 0.8, n - n // 2)]).clip(0, 10)
    return np.round(x, 1)


def resumen(x):
    """Medidas de centro y de dispersión de una muestra (la desviación típica es la muestral, con n - 1)."""
    x = np.asarray(x, float)
    n = len(x)
    q1, med, q3 = np.percentile(x, [25, 50, 75])
    valores, cuentas = np.unique(np.round(x, 1), return_counts=True)
    return {"n": n, "media": float(x.mean()), "mediana": float(med), "moda": float(valores[cuentas.argmax()]),
            "minimo": float(x.min()), "maximo": float(x.max()), "rango": float(x.max() - x.min()),
            "q1": float(q1), "q3": float(q3), "iqr": float(q3 - q1),
            "varianza": float(x.var(ddof=1)) if n > 1 else 0.0, "desviacion": float(x.std(ddof=1)) if n > 1 else 0.0}


def con_extremo(x, valor):
    """La misma muestra con un valor más (por ejemplo, un dato atípico)."""
    return np.append(np.asarray(x, float), valor)


# ------------------------------------------------------------------ distribución normal
def normal_pdf(x, mu=0.0, sigma=1.0):
    x = np.asarray(x, float)
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def normal_cdf(x, mu=0.0, sigma=1.0):
    """Probabilidad de que la variable sea menor o igual que x."""
    z = (np.asarray(x, float) - mu) / (sigma * math.sqrt(2))
    return 0.5 * (1 + np.vectorize(math.erf)(z))


def prob_entre(a, b, mu=0.0, sigma=1.0):
    """P(a < X < b) en una normal. Si a > b se intercambian."""
    a, b = min(a, b), max(a, b)
    return float(normal_cdf(b, mu, sigma) - normal_cdf(a, mu, sigma))


def z_de(valor, mu, sigma):
    """Cuántas desviaciones típicas por encima (o por debajo) de la media está el valor."""
    return (valor - mu) / sigma


def regla_empirica(mu, sigma):
    """El 68-95-99,7 %: intervalos a 1, 2 y 3 desviaciones típicas y su probabilidad exacta."""
    return [{"k": k, "desde": mu - k * sigma, "hasta": mu + k * sigma, "prob": prob_entre(mu - k * sigma, mu + k * sigma, mu, sigma)}
            for k in (1, 2, 3)]


# ------------------------------------------------------------------ teorema central del límite
POBLACIONES = ("Uniforme", "Exponencial (muy asimétrica)", "Dos picos", "Normal")


def poblacion(nombre, tamano, rng):
    """Una muestra grande de esa población: sirve para dibujarla y para sacar muestras."""
    if nombre == "Uniforme":
        return rng.uniform(0, 1, tamano)
    if nombre.startswith("Exponencial"):
        return rng.exponential(1.0, tamano)
    if nombre == "Dos picos":
        mezcla = rng.random(tamano) < 0.5
        return np.where(mezcla, rng.normal(-1.5, 0.5, tamano), rng.normal(1.5, 0.5, tamano))
    return rng.normal(0, 1, tamano)


def medias_muestrales(nombre, n, repeticiones, semilla=1):
    """Saca `repeticiones` muestras de tamaño n y devuelve la media de cada una, junto con la población usada."""
    rng = np.random.default_rng(semilla)
    pob = poblacion(nombre, 200_000, rng)
    medias = rng.choice(pob, size=(repeticiones, n)).mean(axis=1)
    return medias, pob


def error_tipico(sigma, n):
    """Desviación típica de la media de una muestra de tamaño n: sigma / raíz de n."""
    return sigma / math.sqrt(n)


# ------------------------------------------------------------------ probabilidad
def proporcion_acumulada(p, tiradas, semilla=1):
    """Proporción de éxitos tras 1, 2, 3… tiradas de algo que sale con probabilidad p (ley de los grandes números)."""
    rng = np.random.default_rng(semilla)
    exitos = rng.random(tiradas) < p
    return np.cumsum(exitos) / np.arange(1, tiradas + 1)
