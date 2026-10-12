"""Lección 1: media, mediana, moda y dispersión."""
import plotly.graph_objects as go
import streamlit as st

import nucleo


def pagina():
    st.title("📏 Media, mediana y dispersión")
    st.markdown("Resumir muchos datos en pocos números. **Centro** (¿alrededor de qué valor están?) y **dispersión** "
                "(¿cuánto se separan unos de otros?).")
    c1, c2 = st.columns([2, 1])
    nombre = c1.selectbox("Datos de ejemplo", list(nucleo.CONJUNTOS), key="md_datos")
    n = c2.slider("Cuántos datos", 20, 200, 60, 10, key="md_n")
    x = nucleo.conjunto(nombre, n)
    base = nucleo.resumen(x)
    extremo = st.slider("Añadir un valor extraordinario (un solo dato más)", float(x.min()), float(x.max()) * 3, float(x.max()),
                        key="md_extremo", help="Mira qué medida se mueve más cuando llega un dato muy lejano.")
    nuevo = nucleo.resumen(nucleo.con_extremo(x, extremo))

    a, b, c, d = st.columns(4)
    a.metric("Media", f"{nuevo['media']:.1f}", f"{nuevo['media'] - base['media']:+.1f} por el dato añadido", delta_color="off")
    b.metric("Mediana", f"{nuevo['mediana']:.1f}", f"{nuevo['mediana'] - base['mediana']:+.1f}", delta_color="off")
    c.metric("Desviación típica", f"{nuevo['desviacion']:.1f}", f"{nuevo['desviacion'] - base['desviacion']:+.1f}", delta_color="off")
    d.metric("Rango intercuartílico", f"{nuevo['iqr']:.1f}", f"{nuevo['iqr'] - base['iqr']:+.1f}", delta_color="off")

    datos = nucleo.con_extremo(x, extremo)
    fig = go.Figure(go.Histogram(x=datos, nbinsx=25, marker_color="#5b7fd1", opacity=.85, name="Datos"))
    fig.add_vline(x=nuevo["media"], line_color="#e53935", line_width=3, annotation_text="media", annotation_position="top")
    fig.add_vline(x=nuevo["mediana"], line_color="#43a047", line_width=3, annotation_text="mediana", annotation_position="bottom")
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=20, b=0), showlegend=False, bargap=.05, yaxis_title="Cuántos")
    st.plotly_chart(fig, width="stretch")
    st.caption("Una sola observación muy alejada arrastra a la **media** pero casi no mueve la **mediana**: por eso, con sueldos "
               "o precios de vivienda, la mediana suele describir mejor a «una persona típica».")

    with st.expander("¿Qué mide cada cosa?"):
        st.markdown(
            "- **Media**: la suma dividida entre cuántos son. Es el punto de equilibrio de los datos.\n"
            "- **Mediana**: el valor del medio al ordenarlos. La mitad queda por debajo y la otra mitad por encima.\n"
            "- **Moda**: el valor que más se repite.\n"
            "- **Desviación típica**: cuánto se alejan, de media, los datos de la media. Está en las mismas unidades que los datos.\n"
            "- **Rango intercuartílico (IQR)**: lo que ocupa la mitad central de los datos (del percentil 25 al 75). "
            "Casi no le afectan los valores extremos.")
    with st.expander("Los números de esta muestra"):
        st.dataframe({"Medida": ["Datos", "Mínimo", "Primer cuartil", "Mediana", "Tercer cuartil", "Máximo", "Moda", "Varianza"],
                      "Valor": [nuevo["n"], nuevo["minimo"], nuevo["q1"], nuevo["mediana"], nuevo["q3"], nuevo["maximo"],
                                nuevo["moda"], round(nuevo["varianza"], 2)]}, hide_index=True)
