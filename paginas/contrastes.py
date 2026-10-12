"""Lección: contrastes de hipótesis y p-valor."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

import inferencia

MU0 = 100.0      # lo que dice la hipótesis nula


def pagina():
    st.title("⚖️ Contrastes de hipótesis y p-valor")
    st.markdown("Un contraste responde a: *«si la hipótesis nula fuera cierta, ¿sería muy raro lo que he visto?»*. "
                f"Aquí la hipótesis nula (H0) es que la media vale **{MU0:.0f}**. Tú decides cuál es la media **real** y mira qué pasa.")
    c1, c2, c3, c4 = st.columns(4)
    real = c1.slider("Media real", 90.0, 115.0, 105.0, 0.5, key="co_real")
    sigma = c2.slider("Dispersión (σ)", 5, 30, 15, key="co_sigma")
    n = c3.slider("Tamaño de muestra (n)", 3, 300, 30, key="co_n")
    alfa = c4.select_slider("Nivel de significación (α)", [0.01, 0.05, 0.10], 0.05, key="co_alfa")

    st.subheader("Un experimento")
    rng = np.random.default_rng(st.session_state.setdefault("co_semilla", 3))
    muestra = rng.normal(real, sigma, n)
    r = inferencia.prueba_t(muestra, MU0)
    a, b, c = st.columns(3)
    a.metric("Media de la muestra", f"{r['media']:.1f}", f"{r['media'] - MU0:+.1f} frente a H0", delta_color="off")
    b.metric("Estadístico t", f"{r['t']:.2f}")
    c.metric("p-valor", f"{r['p']:.4f}")
    rechaza = r["p"] < alfa
    (st.error if rechaza else st.info)(
        f"p = {r['p']:.4f} {'<' if rechaza else '≥'} α = {alfa}: **{'se rechaza H0' if rechaza else 'no se rechaza H0'}**." +
        (" Hay una diferencia «estadísticamente significativa»." if rechaza else " No hay evidencia suficiente de que la media sea distinta de 100."))
    xs = np.linspace(-5, 5, 400)
    crit = inferencia.t_ppf(1 - alfa / 2, r["gl"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=inferencia.t_pdf(xs, r["gl"]), mode="lines", line=dict(color="#5b7fd1", width=3), name="Si H0 fuera cierta"))
    for lado in (xs <= -crit, xs >= crit):
        fig.add_trace(go.Scatter(x=xs[lado], y=inferencia.t_pdf(xs[lado], r["gl"]), fill="tozeroy", mode="none",
                                 fillcolor="rgba(229,57,53,.35)", showlegend=False))
    fig.add_vline(x=float(np.clip(r["t"], -5, 5)), line_color="#111", line_width=3, annotation_text="tu t")
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0), showlegend=False, yaxis=dict(visible=False))
    st.plotly_chart(fig, width="stretch")
    st.caption("Las zonas rojas son la «región de rechazo»: los valores tan extremos que, si H0 fuera cierta, ocurrirían solo el α de las veces. "
               "El p-valor es la probabilidad de ver algo **igual de raro o más** si H0 fuera cierta.")
    st.button("Repetir con otra muestra", key="co_otra", on_click=lambda: st.session_state.update(co_semilla=st.session_state.co_semilla + 1))

    st.subheader("Repetido 2000 veces: errores y potencia")
    p = inferencia.simular_pvalores(real, MU0, sigma, n, 2000, semilla=11)
    f2 = go.Figure(go.Histogram(x=p, xbins=dict(start=0, end=1, size=0.05), marker_color="#5b7fd1"))
    f2.add_vline(x=alfa, line_color="#e53935", annotation_text="α")
    f2.update_layout(height=280, margin=dict(l=0, r=0, t=30, b=0), xaxis_title="p-valor", yaxis_title="Experimentos")
    st.plotly_chart(f2, width="stretch")
    rech = float((p < alfa).mean())
    a, b = st.columns(2)
    if abs(real - MU0) < 1e-9:
        a.metric("Rechaza H0 (y H0 es cierta)", f"{100 * rech:.1f} %", f"error de tipo I ≈ α = {100 * alfa:.0f} %", delta_color="off")
        st.caption("Cuando no hay diferencia real, los p-valores se reparten por igual entre 0 y 1: es inevitable equivocarse un α de las veces.")
    else:
        a.metric("Rechaza H0 (detecta la diferencia)", f"{100 * rech:.1f} %", "esto es la potencia", delta_color="off")
        b.metric("Se le escapa (error de tipo II)", f"{100 * (1 - rech):.1f} %", delta_color="off")
        st.caption("La **potencia** es la probabilidad de detectar una diferencia que existe de verdad. Sube con la diferencia, con n y con α.")

    st.subheader("¿Qué tamaño de muestra necesito?")
    d = st.slider("Diferencia que quiero poder detectar", 1.0, 20.0, 5.0, 0.5, key="co_dif")
    ns = np.arange(5, 400, 5)
    pot = [inferencia.potencia_z(MU0 + d, MU0, sigma, int(k), alfa) for k in ns]
    f3 = go.Figure(go.Scatter(x=ns, y=pot, mode="lines", line=dict(color="#43a047", width=3)))
    f3.add_hline(y=0.8, line_dash="dash", annotation_text="80 %")
    f3.update_layout(height=260, margin=dict(l=0, r=0, t=20, b=0), xaxis_title="Tamaño de muestra", yaxis_title="Potencia", yaxis_range=[0, 1])
    st.plotly_chart(f3, width="stretch")
    st.metric("Muestra para llegar al 80 % de potencia", f"{inferencia.tamano_para_potencia(d, sigma, 0.8, alfa)}")
    with st.expander("Errores típicos al interpretar un p-valor"):
        st.markdown("- No es la probabilidad de que H0 sea cierta.\n- «No significativo» no prueba que no haya diferencia: quizá la muestra era pequeña.\n"
                    "- «Significativo» no es lo mismo que «importante»: con n enorme, una diferencia minúscula da p muy pequeño.\n"
                    "- Si pruebas muchas cosas, alguna saldrá significativa por azar.")
