"""Tablas y gráficas de los requerimientos 1 a 4, leídas de los archivos de resultados del repositorio."""
import json

import pandas as pd
import streamlit as st

import ui
from servicios.datos import RAIZ, RUTA_MATRIZ

ui.configurar_pagina("Resultados")
st.title("Resultados de los requerimientos 1 a 4")
st.caption("Todo se lee de los archivos CSV, JSON y PNG generados por los scripts de cada requerimiento "
           "(carpetas req*/resultados). Si se vuelven a ejecutar los experimentos, esta página se actualiza.")

# Títulos legibles para los archivos conocidos; los demás se muestran con su nombre.
TITULOS = {
    "requerimiento_3_scc.csv": "Tiempo de obtener la componente fuertemente conexa (ms, mediana de 5)",
    "requerimiento_4_lugares_mas_500m.csv": "Lugares cuyo nodo vial más cercano queda a más de 500 m",
    "req3_tiempos_envolvente.csv": "Envolvente: QuickHull propio vs SciPy (ms, mediana de 5)",
    "req3_envolvente_red.png": "Envolvente convexa de la red vial",
    "req3_tiempos.png": "Tiempos QuickHull propio vs SciPy",
    "req4_tiempo_vs_k.csv": "Soluciones exactas: tiempo frente a k (ms)",
    "req4_tiempo_vs_k.png": "Tiempo frente a k: fuerza bruta vs Held-Karp",
    "req4_calidad_resumen.csv": "Calidad de la heurística voraz frente a Held-Karp",
    "req4_calidad_detalle.csv": "Calidad de la heurística: detalle por instancia",
    "req4_calidad_voraz.png": "Desviación del vecino más cercano sobre el óptimo",
    "req4_itinerario_pasos.csv": "Itinerario de un día: recorte de atractivos",
    "req4_itinerario_tabla.csv": "Itinerario de un día (formato del anexo)",
    "req4_itinerario_final.json": "Itinerario final: Held-Karp vs voraz",
    "req4_contraejemplo.json": "Voraz frente a óptimo: contraejemplo",
    "req3_envolvente_red.json": "Vértices de la envolvente (UTM 18N)",
}


def mostrar_carpeta(carpeta, omitir=()):
    """Muestra los CSV (tabla), PNG (imagen) y JSON (desplegable) de una carpeta de resultados."""
    if not carpeta.exists():
        st.info(f"Aún no hay resultados en `{carpeta.relative_to(RAIZ)}`.")
        return
    archivos = sorted(p for p in carpeta.iterdir() if p.name not in omitir)
    for p in [p for p in archivos if p.suffix == ".csv"]:
        st.markdown(f"**{TITULOS.get(p.name, p.name)}** · `{p.relative_to(RAIZ).as_posix()}`")
        st.dataframe(pd.read_csv(p), hide_index=True, width="stretch")
    imagenes = [p for p in archivos if p.suffix == ".png"]
    for fila in range(0, len(imagenes), 2):
        cols = st.columns(2)
        for col, p in zip(cols, imagenes[fila:fila + 2]):
            col.image(str(p), caption=TITULOS.get(p.name, p.name), width="stretch")
    for p in [p for p in archivos if p.suffix == ".json"]:
        with st.expander(f"{TITULOS.get(p.name, p.name)} · {p.name}"):
            st.json(json.loads(p.read_text(encoding="utf-8")))


r1, r2, r3, r4 = st.tabs(["R1. Red vial", "R2. Caminos mínimos", "R3. Envolvente", "R4. Ruta óptima"])

with r1:
    red = ui.red()
    scc = pd.read_csv(RAIZ / "req1" / "resultados" / "requerimiento_3_scc.csv")
    original = scc.iloc[-1]
    st.markdown("**Tamaño de la red antes y después de quedarse con la componente**")
    st.dataframe(pd.DataFrame([
        {"Red": "Red descargada", "Nodos": int(original["Nodos (V)"]), "Aristas": int(original["Aristas (E)"])},
        {"Red": "Componente fuertemente conexa", "Nodos": red.G.number_of_nodes(),
         "Aristas": red.G.number_of_edges()}]), hide_index=True, width="stretch")

    st.markdown(f"**{TITULOS['requerimiento_3_scc.csv']}**")
    scc["c = tiempo / (V + E) (µs)"] = (scc["Tiempo Mediana (ms)"] / scc["Tamaño (V + E)"] * 1000).round(2)
    st.dataframe(scc, hide_index=True, width="stretch")
    st.line_chart(scc, x="Tamaño (V + E)", y="Tiempo Mediana (ms)", height=260)
    st.caption("La constante c se mantiene casi fija (≈ 5 µs por elemento): el crecimiento es "
               "aproximadamente lineal, consistente con O(V + E) del algoritmo de componentes fuertemente conexas.")

    mostrar_carpeta(RAIZ / "req1" / "resultados", omitir={"requerimiento_3_scc.csv"})
    with st.expander("Catálogo de lugares (40) con su nodo asociado"):
        st.dataframe(ui.catalogo().reset_index(), hide_index=True, width="stretch")

with r2:
    st.markdown("**Matriz de tiempos de viaje entre los lugares (min)** · `req2/matriz_tiempos.csv` "
                "(fila = origen, columna = destino; no es simétrica)")
    M = pd.read_csv(RUTA_MATRIZ, index_col=0) / 60
    st.dataframe(M.style.format("{:.1f}").background_gradient(cmap="YlOrRd", axis=None),
                 width="stretch", height=420)
    asim = sum(abs(M.iloc[i, j] - M.iloc[j, i]) > 1 / 60 for i in range(len(M)) for j in range(i + 1, len(M)))
    st.caption(f"Pares con ida y vuelta distintas (> 1 s): {asim} de {len(M) * (len(M) - 1) // 2}.")
    mostrar_carpeta(RAIZ / "req2" / "resultados")

with r3:
    mostrar_carpeta(RAIZ / "req3" / "resultados")

with r4:
    mostrar_carpeta(RAIZ / "req4" / "resultados")
