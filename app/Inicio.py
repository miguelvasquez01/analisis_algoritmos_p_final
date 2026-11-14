"""
Requerimiento 5 - Aplicación demostrativa del proyecto "Rutas del Paisaje Cultural Cafetero".

Ejecutar desde la raíz del repositorio:   streamlit run app/Inicio.py
"""
import platform
import sys

import streamlit as st

import ui

ui.configurar_pagina("Inicio")

st.title("☕ Rutas del Paisaje Cultural Cafetero")
st.markdown(
    "Aplicación demostrativa del proyecto final de **Análisis de Algoritmos**. "
    "Trabaja sobre la componente fuertemente conexa de la red vial del Quindío (OpenStreetMap) "
    "y el catálogo de 40 lugares. Las rutas y el itinerario se calculan **en el momento** con las "
    "implementaciones propias del proyecto; la envolvente se lee del resultado del requerimiento 3 "
    "y se puede recalcular."
)

red = ui.red()
cat = ui.catalogo()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Nodos (V)", f"{red.G.number_of_nodes():,}".replace(",", " "))
c2.metric("Aristas (E)", f"{red.G.number_of_edges():,}".replace(",", " "))
c3.metric("Lugares del catálogo", len(cat))
c4.metric("Atractivos turísticos", int((cat["categoria"] == "Atractivo turístico").sum()))

st.subheader("Páginas")
st.markdown(
    """
| Página | Qué muestra | Algoritmo (implementación propia) |
|---|---|---|
| **Ruta mínima** | Ruta entre un origen y un destino del catálogo, con su tiempo de viaje | Dijkstra con cola de prioridad (`req2/dijkstra_heap.py`) |
| **Envolvente** | Envolvente convexa de la red sobre el mapa del departamento | QuickHull, divide y vencerás (`req3/quickhull.py`) |
| **Itinerario** | Recorrido de un día con 6 a 8 atractivos: óptimo vs voraz, tiempos y diferencia | Held-Karp y vecino más cercano (`req4/tsp.py`, `req4/itinerario.py`) |
| **Resultados** | Tablas y gráficas de los requerimientos 1 a 4 | Lee los CSV, JSON y PNG de `req*/resultados/` |
"""
)

st.subheader("Catálogo de lugares")
ui.leyenda_categorias()
m = ui.mapa_base()
ui.agregar_lugares(m, cat, radio=6)
ui.mostrar_mapa(m, key="mapa_inicio", altura=480)

with st.expander("Entorno de ejecución"):
    st.write({"Python": sys.version.split()[0], "Sistema operativo": platform.platform(),
              "Procesador": platform.processor() or platform.machine()})
