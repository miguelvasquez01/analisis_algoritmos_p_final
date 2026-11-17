"""Itinerario de un día: Held-Karp (óptimo) vs vecino más cercano (voraz), calculado en el momento."""
import folium
import pandas as pd
import streamlit as st

import ui
from servicios.datos import CATEGORIA_ATRACTIVO, ID_ARMENIA
from servicios.itinerario import planificar

ui.configurar_pagina("Itinerario de un día")
st.title("Itinerario de un día")
st.caption("Se sale del lugar de partida, se visitan los atractivos y se regresa (viajante asimétrico). "
           "La matriz de tiempos entre los lugares elegidos se calcula en el momento con Dijkstra, "
           "el orden se obtiene con Held-Karp, "
           "O(k²·2ᵏ), y con el vecino más cercano, O(k²). Jornada: 11 h.")

red = ui.red()
cat = ui.catalogo()
ids = list(cat.index)
POR_DEFECTO = [13, 15, 16, 17, 18, 21, 22, 25]     # los del documento técnico (req4.4)

c1, c2 = st.columns([1, 2])
partida = c1.selectbox("Lugar de partida", ids, index=ids.index(ID_ARMENIA),
                       format_func=lambda i: ui.nombre(cat, i))
opciones = [i for i in ids if cat.loc[i, "categoria"] == CATEGORIA_ATRACTIVO and i != partida]
atractivos = c2.multiselect("Atractivos (entre 6 y 8)", opciones,
                            default=[i for i in POR_DEFECTO if i in opciones],
                            max_selections=8, format_func=lambda i: ui.nombre(cat, i))
recortar = st.checkbox(
    " quitar atractivos (quitar atractivos si no cabe en 11 h (se quita el que más tiempo libera, hasta que quepa))", value=False)

if not 6 <= len(atractivos) <= 8:
    st.warning(f"Elija entre 6 y 8 atractivos (lleva {len(atractivos)}).")
    st.stop()


@st.cache_data(show_spinner="Calculando Dijkstra, Held-Karp y vecino más cercano...")
def calcular(partida, atractivos, recortar):
    return planificar(ui.red(), ui.catalogo(), partida, list(atractivos), recortar=recortar)


it = calcular(partida, tuple(atractivos), recortar)
hk, nn = it.held_karp, it.voraz
jornada = it.jornada_min

# ------------------------------------------------------------------ resumen
m1, m2, m3, m4 = st.columns(4)
m1.metric("Held-Karp: jornada total", ui.formato_min(hk.total_min), f"viaje {hk.viaje_min:.1f} min",
          delta_color="off")
m2.metric("Voraz: jornada total", ui.formato_min(nn.total_min), f"viaje {nn.viaje_min:.1f} min",
          delta_color="off")
m3.metric("Diferencia (voraz − óptimo)", f"{it.diferencia_min:.1f} min", f"{it.diferencia_pct:+.1f} %",
          delta_color="inverse")
cabe = hk.total_min <= jornada
m4.metric("¿Cabe en 11 h? (Held-Karp)", "Sí" if cabe else "No",
          f"holgura {jornada - hk.total_min:.0f} min" if cabe else f"exceso {hk.total_min - jornada:.0f} min",
          delta_color="normal" if cabe else "inverse")

st.caption(f"Visitas: {hk.visitas_min:.0f} min (iguales para ambos métodos). Tiempo de cómputo: "
           f"Dijkstra ×{len(it.atractivos_iniciales) + 1} {it.dijkstra_ms:.0f} ms · "
           f"Held-Karp {hk.calculo_ms:.2f} ms · voraz {nn.calculo_ms:.3f} ms.")
if not cabe and not recortar:
    st.error("El recorrido no cabe en la jornada de 11 h.")

if it.pasos and len(it.pasos) > 1:
    with st.expander(f"Recorte de atractivos ({len(it.pasos) - 1} pasos)", expanded=True):
        st.dataframe(pd.DataFrame([{
            "paso": n, "atractivos": len(p["atractivos"]), "viaje (min)": round(p["viaje_min"], 1),
            "visitas (min)": int(p["visitas_min"]), "total (h)": round(p["total_min"] / 60, 2),
            "¿cabe en 11 h?": "Sí" if p["cabe"] else "No",
            "se quita": "" if p["quitado"] is None else
            f"{ui.nombre(cat, p['quitado'])} (libera {p['libera_min']:.1f} min)"}
            for n, p in enumerate(it.pasos)]), hide_index=True, width="stretch")


# ------------------------------------------------------------------ tablas (formato del anexo)
def tabla(sol):
    filas = [{"Orden": "Salida", "Lugar": cat.loc[it.partida, "nombre"], "Desplazamiento (min)": None,
              "Visita (min)": None, "Acumulado (h)": 0.0}]
    filas += [{"Orden": str(f["orden"]), "Lugar": cat.loc[f["id"], "nombre"],
               "Desplazamiento (min)": round(f["desplazamiento_min"], 1),
               "Visita (min)": f["visita_min"], "Acumulado (h)": round(f["acumulado_h"], 2)}
              for f in sol.tabla]
    return pd.DataFrame(filas)


t1, t2 = st.columns(2)
for col, sol, titulo in ((t1, hk, "Held-Karp (óptimo)"), (t2, nn, "Vecino más cercano (voraz)")):
    with col:
        st.subheader(titulo)
        st.dataframe(tabla(sol), hide_index=True, width="stretch")
        st.markdown(f"**Visitas:** {sol.visitas_min:.0f} min · **Desplazamientos:** {sol.viaje_min:.1f} min · "
                    f"**Jornada:** {sol.total_min:.1f} min ({ui.formato_min(sol.total_min)})")

if hk.recorrido == nn.recorrido:
    st.success("En esta instancia la heurística voraz encontró el mismo recorrido que Held-Karp.")

# ------------------------------------------------------------------ mapa
st.subheader("Recorridos en el mapa")
m = ui.mapa_base()
todas = []
for sol, color, nombre_capa, guiones in ((hk, ui.COLOR_HK, "Held-Karp", None),
                                         (nn, ui.COLOR_VORAZ, "Voraz", "8 8")):
    capa = folium.FeatureGroup(name=f"{nombre_capa} ({sol.viaje_min:.1f} min de viaje)")
    for a, b in zip(sol.recorrido, sol.recorrido[1:]):
        coords = it.tramos[(a, b)]
        todas += coords
        folium.PolyLine(coords, color=color, weight=5 if guiones is None else 3, opacity=0.8,
                        dash_array=guiones,
                        tooltip=f"{nombre_capa}: {cat.loc[a, 'nombre']} → {cat.loc[b, 'nombre']}").add_to(capa)
    capa.add_to(m)
for pos, i in enumerate(hk.recorrido[:-1]):
    orden_voraz = nn.recorrido.index(i)
    ui.marcador_numerado(m, cat.loc[i, "lat"], cat.loc[i, "lon"], "P" if pos == 0 else pos,
                         ui.COLOR_HK, f"{cat.loc[i, 'nombre']} — orden Held-Karp: {pos or 'partida'}, "
                                      f"orden voraz: {orden_voraz or 'partida'}")
ui.ajustar_a(m, todas)
ui.mostrar_mapa(m, key="mapa_itinerario", altura=600)
st.caption("Línea continua azul: Held-Karp. Línea discontinua naranja: voraz. "
           "Los números son el orden de visita de Held-Karp")
