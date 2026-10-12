"""Regresión lineal (mínimos cuadrados y descenso del gradiente) y modelos lineales generalizados (GLM): funciones de enlace,
familias y ajuste por mínimos cuadrados reponderados (IRLS). Solo numpy, sin Streamlit."""
import math

import numpy as np

# ------------------------------------------------------------------ regresión lineal
def generar_recta(n, pendiente, ordenada, ruido, semilla=1):
    rng = np.random.default_rng(semilla)
    x = rng.uniform(0, 10, n)
    return x, ordenada + pendiente * x + rng.normal(0, ruido, n)


def minimos_cuadrados(x, y):
    """Solución exacta: (ordenada, pendiente)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    b1 = ((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum()
    return float(y.mean() - b1 * x.mean()), float(b1)


def suma_cuadrados(x, y, b0, b1):
    """Suma de los errores al cuadrado de la recta y = b0 + b1·x."""
    return float(((np.asarray(y, float) - (b0 + b1 * np.asarray(x, float))) ** 2).sum())


def descenso_gradiente(x, y, tasa=0.01, pasos=100, inicio=(0.0, 0.0)):
    """Va acercando la recta paso a paso: cada paso se mueve un poco en la dirección que más reduce el error medio.
    Devuelve una matriz (pasos + 1, 3) con ordenada, pendiente y suma de cuadrados en cada paso (el 0 es el inicio)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    b0, b1 = inicio
    camino = [(b0, b1, suma_cuadrados(x, y, b0, b1))]
    for _ in range(pasos):
        error = (b0 + b1 * x) - y
        b0, b1 = (min(max(v, -1e6), 1e6) for v in (b0 - tasa * 2 * error.mean(), b1 - tasa * 2 * (error * x).mean()))   # sin infinitos
        camino.append((b0, b1, suma_cuadrados(x, y, b0, b1)))
    return np.array(camino)


def r_cuadrado(x, y, b0, b1):
    y = np.asarray(y, float)
    return 1 - suma_cuadrados(x, y, b0, b1) / float(((y - y.mean()) ** 2).sum())


# ------------------------------------------------------------------ enlaces y familias (GLM)
ENLACES = {   # nombre: (g(μ) → η, g⁻¹(η) → μ, dμ/dη)
    "identidad": (lambda m: m, lambda e: e, lambda e: np.ones_like(e)),
    "log": (np.log, np.exp, np.exp),
    "logit": (lambda m: np.log(m / (1 - m)), lambda e: 1 / (1 + np.exp(-e)), lambda e: np.exp(-e) / (1 + np.exp(-e)) ** 2),
    "inversa": (lambda m: 1 / m, lambda e: 1 / e, lambda e: -1 / e ** 2),
    "raíz": (np.sqrt, lambda e: e ** 2, lambda e: 2 * e),
}

FAMILIAS = {
    "Normal (gaussiana)": {"varianza": lambda m: np.ones_like(m), "canonico": "identidad", "enlaces": ["identidad", "log"],
                           "formula": "V(μ) = 1", "y": "Número continuo, a ambos lados del cero", "uso": "Alturas, errores de medida, notas"},
    "Poisson": {"varianza": lambda m: m, "canonico": "log", "enlaces": ["log", "raíz", "identidad"], "formula": "V(μ) = μ",
                "y": "Contar sucesos: 0, 1, 2, 3...", "uso": "Siniestros, llamadas, visitas por día"},
    "Binomial": {"varianza": lambda m: m * (1 - m), "canonico": "logit", "enlaces": ["logit"], "formula": "V(μ) = μ(1 − μ)",
                 "y": "Sí/no (o proporción de sís)", "uso": "Impago, abandono, compra"},
    "Gamma": {"varianza": lambda m: m ** 2, "canonico": "inversa", "enlaces": ["log", "inversa", "identidad"], "formula": "V(μ) = μ²",
              "y": "Número positivo con cola a la derecha", "uso": "Coste de siniestros, tiempos, importes"},
    "Gaussiana inversa": {"varianza": lambda m: m ** 3, "canonico": "inversa", "enlaces": ["log"], "formula": "V(μ) = μ³",
                          "y": "Número positivo, cola muy larga", "uso": "Tiempos hasta un evento, importes extremos"},
}


def media_desde_predictor(eta, enlace):
    """μ = g⁻¹(η): lo que se espera de Y a partir del predictor lineal."""
    return ENLACES[enlace][1](np.asarray(eta, float))


def predictor_desde_media(mu, enlace):
    """η = g(μ): el valor de Y (esperado) en la escala donde el modelo es una recta."""
    return ENLACES[enlace][0](np.asarray(mu, float))


def simular_y(familia, mu, semilla=1, dispersion=0.3):
    """Valores de Y con esa media y la forma de esa familia (dispersion: φ en Gamma y Gaussiana inversa; sigma en la normal)."""
    rng = np.random.default_rng(semilla)
    mu = np.asarray(mu, float)
    if familia == "Normal (gaussiana)":
        return rng.normal(mu, dispersion * np.maximum(np.abs(mu).mean(), 1.0))
    if familia == "Poisson":
        return rng.poisson(mu).astype(float)
    if familia == "Binomial":
        return (rng.random(mu.shape) < mu).astype(float)
    if familia == "Gamma":
        forma = 1 / dispersion
        return rng.gamma(forma, mu / forma)
    forma = 1 / dispersion                      # gaussiana inversa (Wald): media mu, forma lambda = 1/φ
    return rng.wald(mu, forma)


def ajustar_glm(x, y, familia, enlace=None, iteraciones=60):
    """Ajusta y ~ b0 + b1·x por IRLS. Devuelve (b0, b1, iteraciones usadas). enlace = el canónico si no se dice."""
    fam = FAMILIAS[familia]
    enlace = enlace or fam["canonico"]
    g, ginv, dmu = ENLACES[enlace]
    x, y = np.asarray(x, float), np.asarray(y, float)
    X = np.column_stack([np.ones_like(x), x])
    mu = (y + y.mean()) / 2 if familia != "Binomial" else (y + 0.5) / 2
    mu = np.clip(mu, 1e-6, None) if familia != "Normal (gaussiana)" else mu
    eta = g(mu)
    beta = np.zeros(2)
    for it in range(1, iteraciones + 1):
        d = dmu(eta)
        z = eta + (y - mu) / d
        w = d ** 2 / fam["varianza"](mu)
        nuevo = np.linalg.solve(X.T @ (X * w[:, None]), X.T @ (w * z))
        eta = X @ nuevo
        mu = ginv(eta)
        if familia == "Binomial":
            mu = np.clip(mu, 1e-9, 1 - 1e-9)
        elif familia != "Normal (gaussiana)":
            mu = np.clip(mu, 1e-9, None)
        if np.abs(nuevo - beta).max() < 1e-9:
            return float(nuevo[0]), float(nuevo[1]), it
        beta = nuevo
    return float(beta[0]), float(beta[1]), iteraciones


# ------------------------------------------------------------------ transformar X
TRANSFORMACIONES_X = {
    "x (sin transformar)": lambda x: x,
    "log(x)": np.log,
    "√x": np.sqrt,
    "x²": lambda x: x ** 2,
    "1/x": lambda x: 1 / x,
}


def correlacion_con(x, y, transformacion):
    """Correlación lineal entre y y x transformada: cuanto más cerca de ±1, mejor se aproxima con una recta."""
    return float(np.corrcoef(TRANSFORMACIONES_X[transformacion](np.asarray(x, float)), np.asarray(y, float))[0, 1])


def comparar_log_y(x, y):
    """Dos formas de modelar un importe Y > 0 que crece con x, ambas con log. Devuelve (b0, b1) de:
    1) MCO sobre log(Y): modela la media de log(Y), no la de Y; al deshacer el log con exp(...) se queda corta.
    2) GLM Gamma con enlace log: modela directamente la media de Y."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    mco = minimos_cuadrados(x, np.log(y))
    glm = ajustar_glm(x, y, "Gamma", "log")[:2]
    return mco, glm
