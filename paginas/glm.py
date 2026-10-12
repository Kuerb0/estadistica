"""Lección: modelos lineales generalizados. Cómo «convertir» Y (enlaces) y X (transformaciones) según la familia."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

import modelos


def pagina():
    st.title("🔁 GLM: convertir Y y convertir X")
    st.markdown("Un **modelo lineal generalizado** sigue siendo una recta, pero **en otra escala**: la media de Y se convierte con una función de "
                "**enlace** hasta que depende linealmente de X. Cada familia (tipo de Y) tiene su enlace habitual.")
    t1, t2, t3, t4 = st.tabs(["🧩 Familias y enlaces", "📉 Convertir Y", "🔀 Convertir X", "⚠️ ¿log(Y) o enlace log?"])

    with t1:
        st.dataframe({"Familia": list(modelos.FAMILIAS), "Y es…": [f["y"] for f in modelos.FAMILIAS.values()],
                      "Enlace habitual": [f["canonico"] for f in modelos.FAMILIAS.values()],
                      "Varianza": [f["formula"] for f in modelos.FAMILIAS.values()], "Ejemplos": [f["uso"] for f in modelos.FAMILIAS.values()]},
                     hide_index=True, width="stretch")
        st.caption("El enlace **canónico** es el que sale de la propia familia; no es obligatorio. En la práctica, el enlace log se usa mucho "
                   "con Poisson y Gamma porque convierte los efectos en multiplicaciones («cada año extra sube un 4 %»).")

    with t2:
        a, b = st.columns(2)
        familia = a.selectbox("Familia de Y", list(modelos.FAMILIAS), index=1, key="glm_fam")
        fam = modelos.FAMILIAS[familia]
        enlace = b.selectbox("Enlace", fam["enlaces"], key=f"glm_enlace_{familia}")
        c1, c2 = st.columns(2)
        b0 = c1.slider("β₀ (ordenada, en la escala del predictor)", -3.0, 3.0, 0.5, 0.1, key="glm_b0")
        b1 = c2.slider("β₁ (pendiente, en la escala del predictor)", -2.0, 2.0, 0.4, 0.05, key="glm_b1")
        x = np.linspace(0, 4, 200)
        eta = b0 + b1 * x
        with np.errstate(all="ignore"):
            mu = modelos.media_desde_predictor(eta, enlace)
        valida = np.isfinite(mu) & (mu > 0 if familia != "Normal (gaussiana)" else True)
        if familia == "Binomial":
            valida &= (mu < 1)
        if not valida.all():
            st.warning("Con estos valores la media sale fuera de lo posible para esta familia (por ejemplo, negativa). Esa es la razón de "
                       "usar un enlace: **log** o **logit** garantizan que la media siempre cae en el rango correcto.")
        xs = np.random.default_rng(2).uniform(0, 4, 120)
        mus = modelos.media_desde_predictor(b0 + b1 * xs, enlace)
        buenos = np.isfinite(mus) & ((mus > 0) if familia != "Normal (gaussiana)" else True) & ((mus < 1) if familia == "Binomial" else True)
        y = np.full_like(xs, np.nan)
        y[buenos] = modelos.simular_y(familia, mus[buenos], 4, 0.3)
        f1 = go.Figure(go.Scatter(x=x, y=eta, mode="lines", line=dict(color="#5b7fd1", width=3)))
        f1.update_layout(title="Escala del predictor: η = β₀ + β₁·x (una recta)", height=300, margin=dict(l=0, r=0, t=40, b=0))
        f2 = go.Figure(go.Scatter(x=xs, y=y, mode="markers", marker=dict(size=7, color="#9aa6bf"), name="Y simulada"))
        f2.add_trace(go.Scatter(x=x[valida], y=mu[valida], mode="lines", line=dict(color="#e53935", width=3), name="Media: μ = g⁻¹(η)"))
        f2.update_layout(title="Escala de Y: la media es una curva", height=300, margin=dict(l=0, r=0, t=40, b=0), legend=dict(orientation="h", y=-0.2))
        g1, g2 = st.columns(2)
        g1.plotly_chart(f1, width="stretch")
        g2.plotly_chart(f2, width="stretch")
        st.markdown(f"En la escala del predictor es **una recta**; al deshacer el enlace **{enlace}** se convierte en la curva de la derecha. "
                    f"La dispersión de Y alrededor de la media depende de la familia: **{fam['formula']}**.")
        e = np.linspace(-3, 3, 7)
        with np.errstate(all="ignore"):
            st.dataframe({"η (predictor)": e, "μ = g⁻¹(η)": np.round(modelos.media_desde_predictor(e, enlace), 3)}, hide_index=True)

    with t3:
        st.markdown("A veces la relación con X no es una recta, pero lo es con **alguna transformación de X**. Elige la que la endereza: "
                    "la correlación con Y se acerca a ±1 cuando acierta.")
        real = st.selectbox("Relación verdadera (oculta en la práctica)", ["log(x)", "√x", "x²", "1/x"], key="glm_real")
        ruido = st.slider("Ruido", 0.0, 1.0, 0.2, 0.05, key="glm_ruido_x")
        xs = np.random.default_rng(5).uniform(0.5, 10, 100)
        base = modelos.TRANSFORMACIONES_X[real](xs)
        y = 2 + 3 * (base - base.mean()) / base.std() + np.random.default_rng(6).normal(0, ruido * 3, 100)
        elegida = st.radio("Transformación de X que pruebas", list(modelos.TRANSFORMACIONES_X), horizontal=True, key="glm_trans")
        tx = modelos.TRANSFORMACIONES_X[elegida](xs)
        b0, b1 = modelos.minimos_cuadrados(tx, y)
        fig = go.Figure(go.Scatter(x=tx, y=y, mode="markers", marker=dict(size=7, color="#5b7fd1")))
        rr = np.array([tx.min(), tx.max()])
        fig.add_trace(go.Scatter(x=rr, y=b0 + b1 * rr, mode="lines", line=dict(color="#e53935", width=3)))
        fig.update_layout(height=320, margin=dict(l=0, r=0, t=20, b=0), showlegend=False, xaxis_title=elegida, yaxis_title="Y")
        st.plotly_chart(fig, width="stretch")
        tabla = {k: abs(modelos.correlacion_con(xs, y, k)) for k in modelos.TRANSFORMACIONES_X}
        mejor = max(tabla, key=tabla.get)
        st.dataframe({"Transformación": list(tabla), "|Correlación| con Y": [round(v, 3) for v in tabla.values()]}, hide_index=True)
        st.success(f"Con **{mejor}** la nube queda más alineada." + (" ¡Has acertado!" if mejor == elegida else f" Tu elección ({elegida}) no es la mejor."))
        st.caption("Reglas rápidas: **log(x)** cuando los efectos son de «por cada multiplicación»; **√x** para recuentos; **x²** si la curva sube cada vez más; "
                   "**1/x** si la relación se estabiliza. Transformar X no cambia la familia de Y.")

    with t4:
        st.markdown("Un importe Y con cola a la derecha suele modelarse con un **log**. Pero hay dos formas y no dan lo mismo:\n"
                    "1. **Convertir los datos**: ajustar una recta a log(Y) y luego deshacer con exp(·).\n"
                    "2. **Convertir la media** (GLM Gamma con enlace log): ajustar la media de Y directamente.")
        c1, c2 = st.columns(2)
        disp = c1.slider("Dispersión de Y (cuanto más, más cola)", 0.1, 2.0, 1.0, 0.1, key="glm_disp")
        n = c2.slider("Datos", 200, 5000, 2000, 200, key="glm_n")
        x = np.random.default_rng(1).uniform(0, 3, n)
        verdad = np.exp(1.0 + 0.5 * x)
        y = modelos.simular_y("Gamma", verdad, 3, disp)
        (m0, m1), (g0, g1) = modelos.comparar_log_y(x, y)
        xx = np.linspace(0, 3, 100)
        fig = go.Figure(go.Scatter(x=x[:600], y=y[:600], mode="markers", marker=dict(size=5, color="#9aa6bf"), name="Datos"))
        fig.add_trace(go.Scatter(x=xx, y=np.exp(1.0 + 0.5 * xx), mode="lines", line=dict(color="#111", width=3), name="Media verdadera"))
        fig.add_trace(go.Scatter(x=xx, y=np.exp(g0 + g1 * xx), mode="lines", line=dict(color="#43a047", width=3, dash="dash"), name="GLM Gamma, enlace log"))
        fig.add_trace(go.Scatter(x=xx, y=np.exp(m0 + m1 * xx), mode="lines", line=dict(color="#e53935", width=3, dash="dot"), name="exp(recta sobre log Y)"))
        fig.update_layout(height=380, margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h", y=1.1), yaxis_range=[0, float(np.percentile(y, 99))])
        st.plotly_chart(fig, width="stretch")
        a, b = st.columns(2)
        a.metric("Media predicha en x = 2 (GLM)", f"{np.exp(g0 + 2 * g1):.2f}", f"real: {np.exp(2.0):.2f}", delta_color="off")
        b.metric("Media predicha en x = 2 (exp de log Y)", f"{np.exp(m0 + 2 * m1):.2f}", f"{np.exp(m0 + 2 * m1) - np.exp(2.0):+.2f}", delta_color="off")
        st.caption("Con datos muy dispersos, **exp(media de log Y) es menor que la media de Y**: el promedio de logaritmos queda por debajo del logaritmo del promedio "
                   "(desigualdad de Jensen). El GLM con enlace log no cae en eso porque modela la media de Y, no la de log(Y).")
