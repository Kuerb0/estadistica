"""Lección: juegos de probabilidad (Monty Hall, cumpleaños, dados)."""
import numpy as np
import plotly.graph_objects as go
import streamlit as st

import azar


def pagina():
    st.title("🎰 Probabilidad con juegos")
    st.markdown("Tres problemas famosos donde la intuición suele fallar. Simúlalos miles de veces y compara con la cuenta exacta.")
    monty, cumple, dados = st.tabs(["🚪 Monty Hall", "🎂 Cumpleaños", "🎲 Dados"])

    with monty:
        st.markdown("Hay un coche tras una de **3 puertas** y cabras tras las otras. Eliges una. El presentador, que sabe dónde está el coche, "
                    "abre **otra** con una cabra y te pregunta: *¿te quedas o cambias?*")
        partidas = st.select_slider("Partidas simuladas", [10, 30, 100, 1000, 10000], 1000, key="ju_partidas")
        q, c = azar.monty_hall(partidas, st.session_state.setdefault("ju_semilla", 1))
        a, b = st.columns(2)
        a.metric("Te quedas: ganas", f"{100 * q / partidas:.1f} %", f"{q} de {partidas}", delta_color="off")
        b.metric("Cambias: ganas", f"{100 * c / partidas:.1f} %", f"{c} de {partidas}", delta_color="off")
        fig = go.Figure(go.Bar(x=["Quedarse", "Cambiar"], y=[q / partidas, c / partidas], marker_color=["#e53935", "#43a047"]))
        fig.add_hline(y=2 / 3, line_dash="dash", annotation_text="2/3")
        fig.add_hline(y=1 / 3, line_dash="dash", annotation_text="1/3")
        fig.update_layout(height=280, margin=dict(l=0, r=0, t=20, b=0), yaxis_range=[0, 1], yaxis_title="Proporción de victorias")
        st.plotly_chart(fig, width="stretch")
        st.button("Volver a jugar", key="ju_otra", on_click=lambda: st.session_state.update(ju_semilla=st.session_state.ju_semilla + 1))
        st.info("Cambiar gana **2 de cada 3**. Tu primera elección acierta con probabilidad 1/3 y eso no cambia cuando se abre una puerta; "
                "el 2/3 restante, que antes se repartía entre las otras dos puertas, queda ahora concentrado en la que no se abrió.")

    with cumple:
        st.markdown("¿Cuántas personas hacen falta en una sala para que sea **más probable que no** que dos cumplan años el mismo día?")
        k = st.slider("Personas en la sala", 2, 80, 23, key="ju_personas")
        exacta = [azar.cumpleanos_prob(i) for i in range(1, 81)]
        sim = azar.cumpleanos_sim(k, 5000)
        a, b = st.columns(2)
        a.metric("Probabilidad exacta de coincidencia", f"{100 * azar.cumpleanos_prob(k):.1f} %")
        b.metric("Simulando 5000 salas", f"{100 * sim:.1f} %")
        fig = go.Figure(go.Scatter(x=list(range(1, 81)), y=exacta, mode="lines", line=dict(color="#5b7fd1", width=3)))
        fig.add_trace(go.Scatter(x=[k], y=[azar.cumpleanos_prob(k)], mode="markers", marker=dict(size=14, color="#e53935")))
        fig.add_hline(y=0.5, line_dash="dash", annotation_text="50 %")
        fig.update_layout(height=300, margin=dict(l=0, r=0, t=20, b=0), showlegend=False, xaxis_title="Personas", yaxis_title="P(alguna coincidencia)",
                          yaxis_range=[0, 1])
        st.plotly_chart(fig, width="stretch")
        st.info("Con **23** personas ya es más probable que sí que no, y con 70 es casi seguro. Parece poco porque pensamos en «alguien que cumpla "
                "mis años», pero aquí cuentan **todas las parejas**: con 23 personas hay 253.")

    with dados:
        st.markdown("Al sumar varios dados no todas las sumas son igual de probables: unas se pueden formar de más maneras.")
        k = st.slider("Número de dados", 1, 6, 2, key="ju_dados")
        reps = st.select_slider("Tiradas simuladas", [100, 1000, 10000, 100000], 10000, key="ju_tiradas")
        v, sim, exacta = azar.suma_dados(k, reps)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=v, y=sim, name="Simulado", marker_color="#5b7fd1"))
        fig.add_trace(go.Scatter(x=v, y=exacta, name="Exacto", mode="lines+markers", line=dict(color="#e53935", width=3)))
        fig.update_layout(height=320, margin=dict(l=0, r=0, t=20, b=0), xaxis_title="Suma", yaxis_title="Probabilidad", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, width="stretch")
        st.caption(f"La suma más probable con {k} dado{'s' if k > 1 else ''} es **{int(v[int(np.argmax(exacta))])}**. "
                   "Al sumar más dados la forma se acerca a una campana: es el teorema central del límite otra vez.")
