"""Lección: regresión lineal, la recta que se va acercando."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

import modelos


def pagina():
    st.title("📈 Regresión lineal: la recta que se acerca")
    st.markdown("Ajustar una recta a una nube de puntos es buscar la que **menos error** comete. Aquí puedes probar rectas a mano y ver cómo "
                "un ordenador las va **acercando paso a paso** hasta la mejor.")
    c1, c2, c3, c4 = st.columns(4)
    n = c1.slider("Puntos", 10, 200, 50, 10, key="re_n")
    pend = c2.slider("Pendiente real", -3.0, 3.0, 1.5, 0.1, key="re_pend")
    ord_ = c3.slider("Ordenada real", -5.0, 10.0, 3.0, 0.5, key="re_ord")
    ruido = c4.slider("Ruido", 0.2, 6.0, 2.0, 0.2, key="re_ruido")
    x, y = modelos.generar_recta(n, pend, ord_, ruido, st.session_state.setdefault("re_semilla", 1))
    b0m, b1m = modelos.minimos_cuadrados(x, y)
    sse_min = modelos.suma_cuadrados(x, y, b0m, b1m)
    xs = np.array([0.0, 10.0])

    tab_mano, tab_pasos = st.tabs(["✋ Pruébalo a mano", "🤖 Que se acerque sola"])
    with tab_mano:
        a, b = st.columns(2)
        b0 = a.slider("Tu ordenada", -10.0, 15.0, 0.0, 0.1, key="re_b0")
        b1 = b.slider("Tu pendiente", -5.0, 5.0, 0.0, 0.05, key="re_b1")
        residuos = st.toggle("Dibujar los errores (distancia de cada punto a tu recta)", True, key="re_res")
        fig = go.Figure(go.Scatter(x=x, y=y, mode="markers", marker=dict(size=8, color="#5b7fd1"), name="Datos"))
        if residuos:
            for xi, yi in zip(x, y):
                fig.add_trace(go.Scatter(x=[xi, xi], y=[yi, b0 + b1 * xi], mode="lines", line=dict(color="rgba(229,57,53,.5)", width=1),
                                         hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=xs, y=b0 + b1 * xs, mode="lines", line=dict(color="#e53935", width=3), name="Tu recta"))
        fig.add_trace(go.Scatter(x=xs, y=b0m + b1m * xs, mode="lines", line=dict(color="#43a047", width=3, dash="dash"), name="La mejor (mínimos cuadrados)"))
        fig.update_layout(height=380, margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width="stretch")
        sse = modelos.suma_cuadrados(x, y, b0, b1)
        m1, m2, m3 = st.columns(3)
        m1.metric("Error de tu recta (suma de cuadrados)", f"{sse:,.0f}".replace(",", "."))
        m2.metric("Error mínimo posible", f"{sse_min:,.0f}".replace(",", "."))
        m3.metric("Tu R²", f"{modelos.r_cuadrado(x, y, b0, b1):.2f}", f"la mejor: {modelos.r_cuadrado(x, y, b0m, b1m):.2f}", delta_color="off")
        st.caption("Se elevan los errores al **cuadrado** para que no se anulen arriba con abajo y para castigar más los grandes. "
                   f"La recta mejor es y = {b0m:.2f} + {b1m:.2f}·x (la real era {ord_:.1f} + {pend:.1f}·x: no sale exacta porque hay ruido).")

    with tab_pasos:
        a, b = st.columns(2)
        tasa = a.select_slider("Tamaño del paso (tasa de aprendizaje)", [0.001, 0.003, 0.01, 0.02, 0.04, 0.08], 0.01, key="re_tasa")
        total = b.slider("Pasos del recorrido", 10, 1000, 300, 10, key="re_total")
        camino = modelos.descenso_gradiente(x, y, tasa, total)
        k = st.slider("Mirar el paso número", 0, total, min(20, total), key="re_k")
        b0k, b1k, sse_k = camino[k]
        fig = go.Figure(go.Scatter(x=x, y=y, mode="markers", marker=dict(size=7, color="#9aa6bf"), name="Datos"))
        for j in sorted({0, max(k // 4, 0), max(k // 2, 0)}):
            fig.add_trace(go.Scatter(x=xs, y=camino[j, 0] + camino[j, 1] * xs, mode="lines", line=dict(color="rgba(229,57,53,.25)", width=2),
                                     hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=xs, y=b0k + b1k * xs, mode="lines", line=dict(color="#e53935", width=4), name=f"Paso {k}"))
        fig.add_trace(go.Scatter(x=xs, y=b0m + b1m * xs, mode="lines", line=dict(color="#43a047", width=3, dash="dash"), name="La mejor"))
        fig.update_layout(height=340, margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h", y=1.1))
        f2 = go.Figure(go.Scatter(x=list(range(total + 1)), y=np.minimum(camino[:, 2], camino[0, 2] * 2), mode="lines", line=dict(color="#5b7fd1", width=3)))
        f2.add_trace(go.Scatter(x=[k], y=[min(sse_k, camino[0, 2] * 2)], mode="markers", marker=dict(size=12, color="#e53935")))
        f2.add_hline(y=sse_min, line_dash="dash", line_color="#43a047", annotation_text="mínimo")
        f2.update_layout(height=340, margin=dict(l=0, r=0, t=20, b=0), showlegend=False, xaxis_title="Paso", yaxis_title="Error")
        g1, g2 = st.columns(2)
        g1.plotly_chart(fig, width="stretch")
        g2.plotly_chart(f2, width="stretch")
        if camino[-1, 2] > camino[0, 2] * 5:
            st.warning("Con ese tamaño de paso el error **sube en vez de bajar**: das pasos tan grandes que te pasas de largo cada vez. Prueba uno más pequeño.")
        st.metric("Error en este paso", f"{sse_k:,.0f}".replace(",", "."), f"{sse_k - sse_min:,.0f} por encima del mínimo".replace(",", "."), delta_color="off")
        st.caption("Cada paso mira hacia dónde baja más el error y se mueve un poco en esa dirección (descenso del gradiente). "
                   "Al principio se acerca rápido y luego va más lento, porque cerca del mínimo ya queda poco que mejorar.")
    st.button("Otros datos", key="re_otros", on_click=lambda: st.session_state.update(re_semilla=st.session_state.re_semilla + 1))
