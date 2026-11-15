"""Utilidades de presentación compartidas por las páginas: datos en caché y mapas Folium."""
import folium
import streamlit as st
from folium.plugins import BeautifyIcon
from streamlit_folium import st_folium

from servicios import datos

CENTRO_QUINDIO = (4.46, -75.68)
COLORES_CATEGORIA = {
    "Cabecera municipal": "#1f4e79",
    "Atractivo turístico": "#2e8b57",
    "Finca/Hotel rural": "#b8860b",
    "Centro de acopio/Trilladora": "#8b4513",
}
COLOR_HK = "#1565c0"
COLOR_VORAZ = "#e65100"
COLOR_RUTA = "#c62828"


# ---------------------------------------------------------------- datos en caché
@st.cache_resource(show_spinner="Cargando la red vial (componente fuertemente conexa)...")
def red():
    return datos.cargar_red()


@st.cache_data
def catalogo():
    return datos.cargar_catalogo()


@st.cache_data
def envolvente_guardada():
    return datos.cargar_envolvente()


def nombre(cat, i):
    return f"{i} · {cat.loc[i, 'nombre']}"


def formato_min(minutos):
    h, m = divmod(round(minutos), 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"


def configurar_pagina(titulo):
    st.set_page_config(page_title=f"{titulo} · Rutas PCC", page_icon="☕", layout="wide")


# ---------------------------------------------------------------- mapas
def mapa_base(zoom=10, centro=CENTRO_QUINDIO):
    return folium.Map(location=centro, zoom_start=zoom, tiles="OpenStreetMap", control_scale=True)


def agregar_lugares(m, cat, ids=None, radio=5):
    """Marcadores circulares de los lugares del catálogo, coloreados por categoría."""
    capa = folium.FeatureGroup(name="Lugares del catálogo")
    for i, f in cat.iterrows():
        if ids is not None and i not in ids:
            continue
        color = COLORES_CATEGORIA.get(f["categoria"], "gray")
        folium.CircleMarker(
            (f["lat"], f["lon"]), radius=radio, color=color, fill=True, fill_opacity=0.85, weight=1,
            tooltip=f"{i} · {f['nombre']} ({f['categoria']})").add_to(capa)
    capa.add_to(m)
    return capa


def marcador_numerado(m, lat, lon, texto, color, tooltip):
    folium.Marker((lat, lon), tooltip=tooltip, icon=BeautifyIcon(
        number=texto, border_color=color, text_color=color, icon_shape="marker")).add_to(m)


def ajustar_a(m, coords):
    if coords:
        lats, lons = zip(*coords)
        m.fit_bounds([(min(lats), min(lons)), (max(lats), max(lons))], padding=(20, 20))


def mostrar_mapa(m, key, altura=560):
    folium.LayerControl(collapsed=False).add_to(m)
    st_folium(m, key=key, height=altura, use_container_width=True, returned_objects=[])


def leyenda_categorias():
    st.caption(" · ".join(f"<span style='color:{c}'>●</span> {k}" for k, c in COLORES_CATEGORIA.items()),
               unsafe_allow_html=True)
