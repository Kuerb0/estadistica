# Estadística básica, jugando

Lecciones interactivas: cambias un control y ves al instante qué pasa. Media y dispersión, la distribución normal, el teorema central del límite y probabilidad.

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Probar

```bash
python tests/test_nucleo.py   # cálculo, sin Streamlit
python tests/test_app.py      # la web entera con el probador de Streamlit
```

## Añadir una lección

1. Un fichero nuevo en `paginas/` con una función `pagina()` (mira `normal.py`).
2. Su cálculo en `nucleo.py`, con un test en `tests/test_nucleo.py`.
3. Registrarla en `app.py` (`PAGINAS`) y en `paginas/inicio.py` (`LECCIONES`).

## Desplegar en Streamlit Community Cloud

*Main file path*: `app.py`.
