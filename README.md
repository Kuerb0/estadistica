# Estadística básica, jugando

Lecciones interactivas: cambias un control y ves al instante qué pasa. Nueve lecciones: media y dispersión, normal, grandes números, juegos de probabilidad (Monty Hall, cumpleaños, dados), teorema central del límite, intervalos de confianza, contrastes y p-valor, regresión lineal que se acerca paso a paso y GLM (convertir Y y X).

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Probar

```bash
python tests/test_nucleo.py   # descriptiva y normal, sin Streamlit
python tests/test_calculo.py  # inferencia, juegos, regresión y GLM
python tests/test_app.py      # la web entera con el probador de Streamlit
```

## Añadir una lección

1. Un fichero nuevo en `paginas/` con una función `pagina()` (mira `normal.py`).
2. Su cálculo (`nucleo.py`, `inferencia.py`, `azar.py` o `modelos.py`), con un test en `tests/`.
3. Registrarla en `app.py` (`PAGINAS`) y en `paginas/inicio.py` (`BLOQUES`).

## Desplegar en Streamlit Community Cloud

*Main file path*: `app.py`.
