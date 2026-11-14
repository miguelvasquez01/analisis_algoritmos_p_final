"""Envolvente convexa de la red vial sobre el mapa del departamento (QuickHull propio, req3)."""
import folium
import pandas as pd
import streamlit as st

import ui
from servicios import envolvente as env

ui.configurar_pagina("Envolvente convexa")
st.title("Envolvente convexa de la red vial")
st.caption("QuickHull (divide y vencerás) sobre los nodos de la componente en UTM 18N, con coordenadas "
           "enteras y sin repetidos. Los puntos alineados sobre los lados no cuentan como vértices.")

red = ui.red()
cat = ui.catalogo()
J = ui.envolvente_guardada()
vertices = [tuple(v) for v in J["vertices_antihorario"]]

c1, c2 = st.columns([3, 1])
with c2:
    mostrar_nodos = st.checkbox("Mostrar nodos de la red", value=True)
    mostrar_lugares = st.checkbox("Mostrar lugares del catálogo", value=False)
    recalcular = st.button("Recalcular con QuickHull propio", width="stretch")

    st.metric("Puntos (n)", f"{J['n_puntos']:,}".replace(",", " "))
    st.metric("Vértices (h)", J["n_vertices"])
    st.metric("Área encerrada", f"{J['area_km2']:,.1f} km²".replace(",", " "))
    st.caption("Superficie del Quindío: ≈ 1 845 km². El polígono convexo incluye zonas fuera del "
               "departamento y deja por fuera la cordillera Central, donde casi no hay vías.")

    if recalcular:
        v, n, ms = env.recalcular(red.G)
        iguales = set(v) == set(vertices)
        st.success(f"QuickHull: {len(v)} vértices sobre {n} puntos en {ms:.1f} ms. "
                   f"{'Mismos vértices que el resultado guardado.' if iguales else 'Difiere del resultado guardado.'}")
        vertices = v

poligono = env.utm_a_latlon(vertices)

with c1:
    m = ui.mapa_base(zoom=9)
    if mostrar_nodos:
        puntos = [[d["x"], d["y"]] for _, d in red.G.nodes(data=True)]
        folium.GeoJson(
            {"type": "Feature", "geometry": {"type": "MultiPoint", "coordinates": puntos}, "properties": {}},
            name=f"Nodos de la red ({len(puntos)})",
            marker=folium.CircleMarker(radius=1, color="#455a64", fill=True, fill_opacity=0.6, weight=0),
        ).add_to(m)
    folium.Polygon(poligono, color="#c62828", weight=3, fill=True, fill_opacity=0.08,
                   name="Envolvente convexa", tooltip=f"Envolvente: {len(poligono)} vértices").add_to(m)
    capa_v = folium.FeatureGroup(name="Vértices")
    for k, (lat, lon) in enumerate(poligono, 1):
        folium.CircleMarker((lat, lon), radius=5, color="#c62828", fill=True, fill_opacity=1,
                            tooltip=f"Vértice {k}").add_to(capa_v)
    capa_v.add_to(m)
    if mostrar_lugares:
        ui.agregar_lugares(m, cat, radio=4)
    ui.ajustar_a(m, poligono)
    ui.mostrar_mapa(m, key="mapa_envolvente", altura=620)

with st.expander("Vértices de la envolvente (sentido antihorario)"):
    st.dataframe(pd.DataFrame(
        [{"vértice": k, "este_utm_m": x, "norte_utm_m": y, "lat": round(lat, 6), "lon": round(lon, 6)}
         for k, ((x, y), (lat, lon)) in enumerate(zip(vertices, poligono), 1)]),
        hide_index=True, width="stretch")
