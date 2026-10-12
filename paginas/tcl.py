"""Lección 3: el teorema central del límite."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

import nucleo


def pagina():
    st.title("🎯 El teorema central del límite")
    st.markdown("Aunque los datos tengan una forma rara, **las medias de muestras** acaban formando una campana. "
                "Elige una población, el tamaño de cada muestra y mira cómo se redondea la figura de abajo.")
    c1, c2, c3 = st.columns(3)
    nombre = c1.selectbox("Población", nucleo.POBLACIONES, index=1, key="tcl_pob")
    n = c2.slider("Tamaño de cada muestra (n)", 1, 200, 5, key="tcl_n")
    rep = c3.select_slider("Cuántas muestras", [200, 500, 1000, 2000, 5000], 1000, key="tcl_rep")
    medias, pob = nucleo.medias_muestrales(nombre, n, rep)

    col1, col2 = st.columns(2)
    f1 = go.Figure(go.Histogram(x=pob[:20000], nbinsx=40, histnorm="probability density", marker_color="#9aa6bf"))
    f1.update_layout(title="La población", height=300, margin=dict(l=0, r=0, t=40, b=0), showlegend=False)
    col1.plotly_chart(f1, width="stretch")

    mu, sigma = float(pob.mean()), float(pob.std())
    ee = nucleo.error_tipico(sigma, n)
    f2 = go.Figure(go.Histogram(x=medias, nbinsx=40, histnorm="probability density", marker_color="#5b7fd1", name="Medias"))
    xs = np.linspace(medias.min(), medias.max(), 300)
    f2.add_trace(go.Scatter(x=xs, y=nucleo.normal_pdf(xs, mu, ee), mode="lines", line=dict(color="#e53935", width=3), name="Normal"))
    f2.update_layout(title=f"Medias de {rep} muestras de tamaño {n}", height=300, margin=dict(l=0, r=0, t=40, b=0), showlegend=False)
    col2.plotly_chart(f2, width="stretch")

    a, b, c = st.columns(3)
    a.metric("Media de la población", f"{mu:.2f}")
    b.metric("Error típico teórico σ/√n", f"{ee:.3f}")
    c.metric("Dispersión real de las medias", f"{medias.std():.3f}")
    st.caption("La curva roja es la campana que predice el teorema. Con n = 1 la figura de las medias es igual que la población; "
               "al subir n se estrecha (el error típico baja con la raíz de n) y se vuelve simétrica.")
    with st.expander("¿Por qué importa?"):
        st.write("Casi todo lo que se hace con encuestas, ensayos clínicos o pruebas A/B se apoya en esto: aunque no sepamos cómo se "
                 "distribuyen los datos, la media de una muestra grande se comporta como una normal, y eso permite calcular "
                 "márgenes de error e intervalos de confianza.")
