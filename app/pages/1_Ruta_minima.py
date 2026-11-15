"""Ruta mínima entre dos lugares del catálogo (Dijkstra con cola de prioridad, calculado en el momento)."""
import math

import folium
import streamlit as st

import ui
from servicios.datos import ID_ARMENIA
from servicios.rutas import ruta_entre

ui.configurar_pagina("Ruta mínima")
st.title("Ruta mínima entre dos lugares")
st.caption("Dijkstra con cola de prioridad (montículo binario), O((V + E) log V). "
           "Peso: tiempo de viaje estimado de cada tramo (s). Se detiene al sacar el destino de la cola.")

red = ui.red()
cat = ui.catalogo()
ids = list(cat.index)

c1, c2 = st.columns(2)
origen = c1.selectbox("Origen", ids, index=ids.index(ID_ARMENIA), format_func=lambda i: ui.nombre(cat, i))
destino = c2.selectbox("Destino", ids, index=ids.index(15), format_func=lambda i: ui.nombre(cat, i))

ruta = ruta_entre(red, int(cat.loc[origen, "nodo_osm"]), int(cat.loc[destino, "nodo_osm"]))

if math.isinf(ruta.tiempo_s):
    st.error("No hay ruta entre esos lugares en la componente.")
    st.stop()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Tiempo de viaje", ui.formato_min(ruta.tiempo_s / 60), f"{ruta.tiempo_s:,.1f} s", delta_color="off")
m2.metric("Distancia", f"{ruta.distancia_m / 1000:.2f} km")
m3.metric("Nodos explorados", f"{ruta.explorados:,}".replace(",", " "))
m4.metric("Cálculo (Dijkstra)", f"{ruta.calculo_ms:.1f} ms")
st.caption(f"La ruta pasa por {len(ruta.nodos)} nodos. El tiempo es una estimación del modelo "
           "(distancia / velocidad del tramo), no el tiempo real de recorrido.")

for i, papel in ((origen, "origen"), (destino, "destino")):
    d = cat.loc[i, "distancia_al_nodo_m"]
    if d > 500:
        st.info(f"El {papel} ({cat.loc[i, 'nombre']}) está a {d:.0f} m de su nodo vial más cercano; "
                "ese tramo se asume a pie y queda dentro del tiempo de visita (requerimiento 1.4).")

m = ui.mapa_base()
ui.agregar_lugares(m, cat, radio=4)
if ruta.coords:
    folium.PolyLine(ruta.coords, color=ui.COLOR_RUTA, weight=5, opacity=0.85,
                    tooltip=f"{ui.formato_min(ruta.tiempo_s / 60)}").add_to(m)
    ui.ajustar_a(m, ruta.coords)
ui.marcador_numerado(m, cat.loc[origen, "lat"], cat.loc[origen, "lon"], "A", "#2e7d32",
                     f"Origen: {cat.loc[origen, 'nombre']}")
ui.marcador_numerado(m, cat.loc[destino, "lat"], cat.loc[destino, "lon"], "B", ui.COLOR_RUTA,
                     f"Destino: {cat.loc[destino, 'nombre']}")
ui.mostrar_mapa(m, key="mapa_ruta")
