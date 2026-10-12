"""Lección: intervalos de confianza."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

import inferencia

MU = 100.0     # la media real de la población (en la vida real, la que no conocemos)


def pagina():
    st.title("📐 Intervalos de confianza")
    st.markdown("Una muestra da **una** media, y otra muestra daría otra. Un intervalo de confianza dice entre qué valores puede estar "
                "la media real, y el «95 %» habla de **cuántas veces acierta el método** si lo repites muchas veces, no de este intervalo en concreto.")
    c1, c2, c3 = st.columns(3)
    sigma = c1.slider("Dispersión de la población (σ)", 5, 40, 15, key="ic_sigma")
    n = c2.slider("Tamaño de cada muestra (n)", 3, 200, 20, key="ic_n")
    nivel = c3.select_slider("Nivel de confianza", [0.80, 0.90, 0.95, 0.99], 0.95, format_func=lambda v: f"{int(100 * v)} %", key="ic_nivel")

    st.subheader("Una muestra")
    rng = np.random.default_rng(st.session_state.setdefault("ic_semilla", 1))
    muestra = rng.normal(MU, sigma, n)
    desde, hasta = inferencia.intervalo_media(muestra, nivel)
    a, b, c = st.columns(3)
    a.metric("Media de la muestra", f"{muestra.mean():.1f}")
    b.metric("Intervalo", f"{desde:.1f} a {hasta:.1f}")
    c.metric("¿Contiene la media real (100)?", "Sí ✅" if desde <= MU <= hasta else "No ❌")
    st.button("Sacar otra muestra", key="ic_otra", on_click=lambda: st.session_state.update(ic_semilla=st.session_state.ic_semilla + 1))

    st.subheader("Repetir el experimento")
    reps = st.slider("Cuántas veces", 10, 100, 50, key="ic_reps")
    d, h, dentro = inferencia.simular_intervalos(MU, sigma, n, nivel, reps, semilla=st.session_state.ic_semilla)
    fig = go.Figure()
    for i in range(reps):
        fig.add_trace(go.Scatter(x=[d[i], h[i]], y=[i, i], mode="lines", line=dict(color="#43a047" if dentro[i] else "#e53935", width=3),
                                 hoverinfo="skip", showlegend=False))
    fig.add_vline(x=MU, line_color="#111", line_dash="dash", annotation_text="media real", annotation_position="top")
    fig.update_layout(height=420, margin=dict(l=0, r=0, t=30, b=0), yaxis=dict(visible=False))
    st.plotly_chart(fig, width="stretch")
    a, b = st.columns(2)
    a.metric("Aciertan (verdes)", f"{int(dentro.sum())} de {reps}", f"{100 * dentro.mean():.0f} %", delta_color="off")
    largo = inferencia.simular_intervalos(MU, sigma, n, nivel, 4000, semilla=7)[2].mean()
    b.metric("A la larga (4000 repeticiones)", f"{100 * largo:.1f} %", f"nivel elegido: {int(100 * nivel)} %", delta_color="off")
    st.caption("Los rojos son los intervalos que **no** contienen la media real. A la larga son más o menos el resto hasta el 100 %. "
               "Con una sola muestra no sabemos si nos ha tocado verde o rojo: de ahí la «confianza».")
    with st.expander("¿Qué hace que el intervalo sea más estrecho?"):
        st.markdown("- **Más datos (n)**: el ancho baja con la raíz de n. Para dividir el ancho entre 2 hacen falta 4 veces más datos.\n"
                    "- **Menos dispersión (σ)**: datos más parecidos entre sí dan una media más precisa.\n"
                    "- **Menos confianza**: un intervalo del 80 % es más estrecho que uno del 99 %, pero falla más a menudo.")
        ancho = [(inferencia.t_ppf(1 - (1 - nivel) / 2, k - 1) * 2 * sigma / np.sqrt(k)) for k in (5, 20, 80, 320)]
        st.dataframe({"n": [5, 20, 80, 320], "Ancho aproximado del intervalo": [f"{v:.1f}" for v in ancho]}, hide_index=True)
