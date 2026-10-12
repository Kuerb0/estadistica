"""Lección 2: la distribución normal."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

import nucleo


def pagina():
    st.title("🔔 La distribución normal")
    st.markdown("La campana que aparece cuando muchas pequeñas causas se suman: estaturas, errores de medida, notas... "
                "Se define con solo dos números: la **media** (dónde está el centro) y la **desviación típica** (cuánto se abre).")
    c1, c2 = st.columns(2)
    mu = c1.slider("Media (μ)", -10.0, 10.0, 0.0, .5, key="no_mu")
    sigma = c2.slider("Desviación típica (σ)", .5, 5.0, 1.0, .1, key="no_sigma")
    a, b = st.slider("Probabilidad entre estos dos valores", float(mu - 4 * sigma), float(mu + 4 * sigma),
                     (float(mu - sigma), float(mu + sigma)), key="no_rango")
    p = nucleo.prob_entre(a, b, mu, sigma)

    x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 400)
    y = nucleo.normal_pdf(x, mu, sigma)
    dentro = (x >= a) & (x <= b)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color="#5b7fd1", width=3), name="Densidad"))
    fig.add_trace(go.Scatter(x=x[dentro], y=y[dentro], fill="tozeroy", mode="none", fillcolor="rgba(229,57,53,.45)", name="Esa zona"))
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=20, b=0), showlegend=False, yaxis_title="Densidad")
    st.plotly_chart(fig, width="stretch")
    st.metric("Probabilidad de que un valor caiga en la zona roja", f"{100 * p:.1f} %")
    st.caption("La probabilidad es el **área** bajo la curva. El área total vale 1 (el 100 %).")

    st.subheader("La regla del 68-95-99,7")
    filas = nucleo.regla_empirica(mu, sigma)
    st.dataframe({"Distancia a la media": [f"± {r['k']} σ" for r in filas],
                  "Intervalo": [f"{r['desde']:.1f} a {r['hasta']:.1f}" for r in filas],
                  "Probabilidad": [f"{100 * r['prob']:.1f} %" for r in filas]}, hide_index=True)

    st.subheader("¿Cuánto de raro es un valor? La puntuación z")
    v = st.number_input("Un valor concreto", value=float(mu + 2 * sigma), key="no_valor")
    z = nucleo.z_de(v, mu, sigma)
    mas_alto = 1 - float(nucleo.normal_cdf(v, mu, sigma))
    st.markdown(f"**z = {z:.2f}**: el valor está a {abs(z):.2f} desviaciones típicas {'por encima' if z >= 0 else 'por debajo'} de la "
                f"media. Solo el **{100 * mas_alto:.1f} %** de los casos queda por encima de él.")
    with st.expander("¿Para qué sirve la z?"):
        st.write("Convierte cualquier normal en la normal estándar (media 0, desviación 1), así que se pueden comparar cosas medidas "
                 "en unidades distintas: un 8,5 en un examen y 190 cm de altura se comparan por su z.")
