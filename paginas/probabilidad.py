"""Lección 4: probabilidad y ley de los grandes números."""
import plotly.graph_objects as go
import streamlit as st

import nucleo

EJEMPLOS = {"Moneda (cara)": .5, "Dado (sacar un 6)": 1 / 6, "Ruleta (rojo, sin el 0)": .5, "Una probabilidad a mano": None}


def pagina():
    st.title("🎲 Probabilidad y ley de los grandes números")
    st.markdown("La probabilidad es lo que **se acerca a ser** la proporción de veces que algo ocurre cuando repetimos muchísimo. "
                "Con pocas repeticiones, el azar engaña; con muchas, se ordena.")
    c1, c2 = st.columns(2)
    ejemplo = c1.selectbox("¿Qué lanzamos?", list(EJEMPLOS), key="pr_ej")
    p = EJEMPLOS[ejemplo]
    if p is None:
        p = c2.slider("Probabilidad de que ocurra", .01, .99, .3, .01, key="pr_p")
    tiradas = st.select_slider("Número de repeticiones", [10, 30, 100, 300, 1000, 5000], 300, key="pr_n")
    semilla = st.number_input("Semilla (otro número, otro azar)", 0, 9999, 1, key="pr_semilla")

    acumulada = nucleo.proporcion_acumulada(p, tiradas, int(semilla))
    fig = go.Figure(go.Scatter(x=list(range(1, tiradas + 1)), y=acumulada, mode="lines", line=dict(color="#5b7fd1", width=2)))
    fig.add_hline(y=p, line_color="#e53935", line_dash="dash", annotation_text=f"probabilidad real: {p:.3f}")
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=20, b=0), xaxis_title="Repeticiones", yaxis_title="Proporción de veces que ocurre",
                      yaxis_range=[0, 1], xaxis_type="log" if tiradas >= 300 else "linear", showlegend=False)
    st.plotly_chart(fig, width="stretch")
    a, b, c = st.columns(3)
    a.metric("Proporción al final", f"{acumulada[-1]:.3f}")
    b.metric("Diferencia con la real", f"{abs(acumulada[-1] - p):.3f}")
    c.metric("Proporción tras las 10 primeras", f"{acumulada[9]:.2f}")
    st.caption("Fíjate en que la línea oscila mucho al principio y se pega a la real después. Nada «compensa» las rachas: simplemente "
               "cada nueva tirada pesa menos que todas las anteriores juntas.")
    with st.expander("Un error muy común: la falacia del jugador"):
        st.write("Después de cinco caras seguidas, la siguiente moneda sigue teniendo un 50 % de salir cara. Las tiradas no tienen "
                 "memoria. Lo que ocurre es que, en el conjunto, esas cinco caras se diluyen entre cientos de tiradas.")
