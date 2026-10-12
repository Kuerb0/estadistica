"""Intervalos de confianza y contrastes de hipótesis, sin Streamlit ni scipy (la t de Student se calcula con la beta incompleta)."""
import math

import numpy as np

from nucleo import normal_cdf


# ------------------------------------------------------------------ distribuciones
def _fraccion_beta(a, b, x, iteraciones=300, eps=3e-14):
    """Fracción continua de la beta incompleta (método de Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, iteraciones + 1):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)), -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
            d = 1 + aa * d
            d = 1 / (d if abs(d) > tiny else tiny)
            c = 1 + aa / c
            c = c if abs(c) > tiny else tiny
            h *= d * c
        if abs(d * c - 1) < eps:
            break
    return h


def beta_incompleta(a, b, x):
    """Beta incompleta regularizada I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _fraccion_beta(a, b, x) / a
    return 1 - bt * _fraccion_beta(b, a, 1 - x) / b


def t_cdf(t, gl):
    """Probabilidad de que una t de Student con gl grados de libertad sea menor o igual que t."""
    ib = beta_incompleta(gl / 2, 0.5, gl / (gl + t * t))
    return 1 - 0.5 * ib if t > 0 else 0.5 * ib


def _inversa(cdf, p, bajo, alto):
    for _ in range(200):
        medio = (bajo + alto) / 2
        if cdf(medio) < p:
            bajo = medio
        else:
            alto = medio
    return (bajo + alto) / 2


def t_pdf(x, gl):
    """Densidad de la t de Student."""
    x = np.asarray(x, float)
    c = math.exp(math.lgamma((gl + 1) / 2) - math.lgamma(gl / 2)) / math.sqrt(gl * math.pi)
    return c * (1 + x ** 2 / gl) ** (-(gl + 1) / 2)


def t_ppf(p, gl):
    """Valor t que deja a su izquierda la probabilidad p."""
    return _inversa(lambda v: t_cdf(v, gl), p, -1e4, 1e4)


def z_ppf(p):
    """Valor z de la normal estándar que deja a su izquierda la probabilidad p."""
    return _inversa(lambda v: float(normal_cdf(v)), p, -40.0, 40.0)


# ------------------------------------------------------------------ intervalos de confianza
def intervalo_media(x, nivel=0.95):
    """Intervalo de confianza para la media con la t de Student: (desde, hasta)."""
    x = np.asarray(x, float)
    n = len(x)
    ee = x.std(ddof=1) / math.sqrt(n)
    t = t_ppf(1 - (1 - nivel) / 2, n - 1)
    return float(x.mean() - t * ee), float(x.mean() + t * ee)


def simular_intervalos(mu, sigma, n, nivel, repeticiones, semilla=1):
    """Repite el experimento: saca una muestra normal, calcula su intervalo y apunta si contiene la media real."""
    rng = np.random.default_rng(semilla)
    t = t_ppf(1 - (1 - nivel) / 2, n - 1)
    muestras = rng.normal(mu, sigma, (repeticiones, n))
    medias = muestras.mean(axis=1)
    ee = muestras.std(axis=1, ddof=1) / math.sqrt(n)
    desde, hasta = medias - t * ee, medias + t * ee
    return desde, hasta, (desde <= mu) & (mu <= hasta)


# ------------------------------------------------------------------ contrastes
def prueba_t(x, mu0):
    """Prueba t de una muestra frente a H0: media = mu0 (bilateral). Devuelve estadístico, grados de libertad y p-valor."""
    x = np.asarray(x, float)
    n = len(x)
    ee = x.std(ddof=1) / math.sqrt(n)
    t = (x.mean() - mu0) / ee
    return {"t": float(t), "gl": n - 1, "p": float(2 * (1 - t_cdf(abs(t), n - 1))), "media": float(x.mean()), "ee": float(ee)}


def simular_pvalores(mu_real, mu0, sigma, n, repeticiones, semilla=1):
    """p-valores de muchas repeticiones del mismo experimento cuando la media real es mu_real y se contrasta H0: mu = mu0."""
    rng = np.random.default_rng(semilla)
    muestras = rng.normal(mu_real, sigma, (repeticiones, n))
    t = (muestras.mean(axis=1) - mu0) / (muestras.std(axis=1, ddof=1) / math.sqrt(n))
    return np.array([2 * (1 - t_cdf(abs(v), n - 1)) for v in t])


def potencia_z(mu_real, mu0, sigma, n, alfa=0.05):
    """Probabilidad de rechazar H0 (prueba z bilateral con sigma conocida) cuando la media real es mu_real."""
    d = (mu_real - mu0) * math.sqrt(n) / sigma
    z = z_ppf(1 - alfa / 2)
    return float(1 - normal_cdf(z - d) + normal_cdf(-z - d))


def tamano_para_potencia(efecto, sigma, potencia=0.8, alfa=0.05):
    """Tamaño de muestra aproximado (prueba z bilateral) para detectar una diferencia `efecto` con esa potencia."""
    return math.ceil(((z_ppf(1 - alfa / 2) + z_ppf(potencia)) * sigma / efecto) ** 2)
