"""Juegos de probabilidad con simulación: Monty Hall, el problema del cumpleaños y la suma de dados. Sin Streamlit."""
import numpy as np


def monty_hall(partidas, semilla=1):
    """Juega muchas veces. Devuelve (victorias si te quedas, victorias si cambias): el presentador siempre abre una puerta con cabra."""
    rng = np.random.default_rng(semilla)
    coche = rng.integers(0, 3, partidas)
    eleccion = rng.integers(0, 3, partidas)
    quedarse = int((coche == eleccion).sum())
    return quedarse, partidas - quedarse          # al cambiar ganas justo cuando tu primera elección era una cabra


def cumpleanos_prob(personas):
    """Probabilidad exacta de que al menos dos de `personas` cumplan años el mismo día (365 días, todos igual de probables)."""
    p_distintos = 1.0
    for i in range(personas):
        p_distintos *= (365 - i) / 365
    return 1 - p_distintos


def cumpleanos_sim(personas, repeticiones, semilla=1):
    """Proporción de grupos simulados en los que alguien coincide."""
    rng = np.random.default_rng(semilla)
    dias = rng.integers(0, 365, (repeticiones, personas))
    ordenados = np.sort(dias, axis=1)
    return float((ordenados[:, 1:] == ordenados[:, :-1]).any(axis=1).mean())


def suma_dados(dados, repeticiones, semilla=1):
    """Frecuencia relativa de cada suma al tirar `dados` dados, y la distribución exacta: (sumas, simulada, exacta)."""
    rng = np.random.default_rng(semilla)
    sumas = rng.integers(1, 7, (repeticiones, dados)).sum(axis=1)
    valores = np.arange(dados, 6 * dados + 1)
    simulada = np.array([(sumas == v).mean() for v in valores])
    exacta = np.array([1.0])
    for _ in range(dados):
        exacta = np.convolve(exacta, np.ones(6) / 6)
    return valores, simulada, exacta
