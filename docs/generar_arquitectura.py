"""
Genera docs/arquitectura.png: diagrama de componentes y flujo de datos entre requerimientos.

Uso: py docs/generar_arquitectura.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

SALIDA = Path(__file__).resolve().parent / "arquitectura.png"

ESTILO = {
    "script":  dict(fc="#dbe9f6", ec="#2c7fb8"),   # código
    "archivo": dict(fc="#fff4cc", ec="#c9a227"),   # datos en disco
    "externo": dict(fc="#e8e8e8", ec="#666666"),   # fuentes externas
    "app":     dict(fc="#e3f4e1", ec="#3a9a3a"),
}
NEGRO, FLUJO, VERDE = "#333333", "#7b3fa0", "#3a9a3a"

fig, ax = plt.subplots(figsize=(20, 11))
ax.set_xlim(0, 20)
ax.set_ylim(-0.6, 10.8)
ax.axis("off")


def grupo(x0, y0, x1, y1, titulo, color="#555555"):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0.02,rounding_size=0.15",
                                fc="none", ec=color, lw=1.4, ls="--"))
    ax.text(x0 + 0.15, y1 - 0.12, titulo, ha="left", va="top", fontsize=12.5, weight="bold", color=color)


def caja(x, y, texto, tipo="script", w=2.5, h=0.85, fs=9.2):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                lw=1.3, zorder=3, **ESTILO[tipo]))
    ax.text(x, y, texto, ha="center", va="center", fontsize=fs, zorder=4,
            family="monospace" if tipo in ("script", "archivo") else None)


def ruta(*puntos, color=NEGRO, lw=1.4, ls="-", flecha=True):
    """Polilínea por los puntos dados; punta de flecha en el último tramo."""
    xs, ys = zip(*puntos)
    if len(puntos) > 2:
        ax.plot(xs[:-1], ys[:-1], color=color, lw=lw, ls=ls, zorder=2, solid_capstyle="butt")
    if flecha:
        ax.annotate("", xy=puntos[-1], xytext=puntos[-2], zorder=2,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, ls=ls, mutation_scale=14,
                                    shrinkA=0, shrinkB=0))
    else:
        ax.plot(xs[-2:], ys[-2:], color=color, lw=lw, ls=ls, zorder=2)


def nota(x, y, texto, color=FLUJO, rot=0, ha="center"):
    ax.text(x, y, texto, fontsize=8.6, color=color, ha=ha, va="center", style="italic", rotation=rot, zorder=5,
            bbox=dict(fc="white", ec="none", pad=1.0))


def union(x, y, color=FLUJO):
    ax.plot([x], [y], "o", ms=5, color=color, zorder=3)


# ---------------------------------------------------------------- Fuentes externas
caja(1.15, 9.0, "OpenStreetMap\n(vía OSMnx)", "externo", w=1.9, h=0.95, fs=10)
caja(1.15, 2.15, "Fuentes del\ncatálogo (mapas,\nsitios oficiales)", "externo", w=1.9, h=1.2, fs=9.5)

# ---------------------------------------------------------------- R1
grupo(2.3, 0.8, 8.6, 9.75, "R1 · Modelo de la red vial")
caja(4.0, 8.85, "1_importar_red_vial.py\n2_vel_time.py", w=2.9)
caja(4.0, 7.75, "red_vial_quindio.graphml\nlength, travel_time", "archivo", w=2.9)
caja(4.0, 6.55, "3_componente_conexo.py\nlargest_component(\n  strongly=True)", w=2.9, h=1.0)
caja(4.0, 4.6, "4.1_asociar_nodos.py\nnodo más cercano\n(UTM 18N)", w=2.9, h=1.0)
caja(4.0, 3.3, "catalogo_lugares_\nquindio.csv", "archivo", w=2.9)
caja(4.0, 2.15, "4_catalogo.py", w=2.9)
# Salidas de R1 (columna derecha, alineadas con quien las consume)
caja(7.25, 8.4, "red_vial_quindio_\nfiltered.graphml\n(comp. fuerte)", "archivo", w=2.3, h=1.0)
caja(7.25, 5.0, "red_vial_quindio_\nutm18n.graphml", "archivo", w=2.3)
caja(7.25, 1.75, "catalogo_lugares_\nnodos.csv\nlugar → nodo_osm", "archivo", w=2.3, h=1.0)

ruta((2.1, 9.0), (2.55, 9.0))                        # OSM -> importar
ruta((2.1, 2.15), (2.55, 2.15))                      # fuentes -> catálogo
ruta((4.0, 8.425), (4.0, 8.175))                     # importar -> graphml
ruta((4.0, 7.325), (4.0, 7.05))                      # graphml -> componente
ruta((5.45, 6.95), (6.1, 8.2))                       # componente -> filtered
ruta((6.45, 7.9), (5.3, 5.1))                        # filtered -> asociar
ruta((4.0, 2.575), (4.0, 2.875))                     # catalogo.py -> csv
ruta((4.0, 3.725), (4.0, 4.1))                       # csv -> asociar
ruta((5.45, 4.75), (6.1, 4.95))                      # asociar -> utm18n
ruta((5.45, 4.3), (6.1, 2.0))                        # asociar -> catálogo con nodos

# ---------------------------------------------------------------- R2, R3, R4
SX, MX = 10.9, 13.45          # columna de scripts / columna de módulos y archivos
grupo(9.4, 6.6, 14.6, 9.75, "R2 · Caminos mínimos")
caja(SX, 8.25, "req2.py\nverificación,\nmediciones, matriz", w=2.2, h=1.0)
caja(MX, 8.85, "dijkstra_heap.py\ndijkstra_lineal.py", w=2.1)
caja(MX, 7.4, "matriz_tiempos.csv\n40×40 (s)", "archivo", w=2.1)
ruta((12.4, 8.85), (12.0, 8.55))                     # módulos -> req2.py
ruta((12.0, 7.95), (12.4, 7.55))                     # req2.py -> matriz

grupo(9.4, 3.75, 14.6, 6.3, "R3 · Envolvente convexa")
caja(SX, 5.0, "1_envolvente_\nexperimento.py\n(vs scipy)", w=2.2, h=1.0)
caja(MX, 5.6, "quickhull.py", w=2.1, h=0.7)
caja(MX, 4.45, "req3_envolvente_\nred.json", "archivo", w=2.1, h=0.75)
ruta((12.4, 5.6), (12.0, 5.3))
ruta((12.0, 4.7), (12.4, 4.45))

grupo(9.4, 0.8, 14.6, 3.45, "R4 · Ruta óptima (ATSP)")
caja(SX, 2.0, "1_experimentos_\ntsp.py", w=2.2)
caja(MX, 1.8, "tsp.py: fuerza bruta,\nHeld-Karp, voraz\nitinerario.py", w=2.1, h=1.2, fs=8.8)
ruta((12.4, 1.75), (12.0, 1.75))

# ---------------------------------------------------------------- R5 y resultados
grupo(15.5, 3.75, 19.85, 9.75, "R5 · Aplicación (Streamlit)", color=VERDE)
caja(17.7, 7.9, "app/servicios/\ndatos · rutas ·\nenvolvente · itinerario", "app", w=3.3, h=1.1, fs=9.8)
caja(17.7, 5.2, "app/pages/\nRuta mínima · Envolvente\nItinerario · Resultados", "app", w=3.3, h=1.1, fs=9.8)
caja(17.7, 2.0, "req*/resultados/\nCSV · JSON · PNG\n(los generan los scripts\nde R1 a R4)", "archivo",
     w=3.3, h=1.3, fs=8.8)
ruta((17.7, 7.35), (17.7, 5.75))                     # servicios -> páginas
ruta((17.7, 2.65), (17.7, 4.65))                     # resultados -> página Resultados

# ---------------------------------------------------------------- Flujo entre requerimientos
# filtered.graphml -> req2.py
ruta((8.4, 8.25), (9.8, 8.25), color=FLUJO, lw=1.7)
# utm18n.graphml -> R3
ruta((8.4, 5.0), (9.8, 5.0), color=FLUJO, lw=1.7)
nota(9.0, 5.25, "UTM")
# catálogo -> R4 y bus vertical hacia R2 y la app
ruta((8.4, 1.75), (9.8, 1.75), color=FLUJO, lw=1.7)
union(9.0, 1.75)
ruta((9.0, 1.75), (9.0, 7.85), (9.8, 7.85), color=FLUJO, lw=1.7)
union(9.0, 7.85)
ruta((9.0, 7.85), (9.0, 10.15), color=FLUJO, lw=1.7, flecha=False)
nota(9.0, 3.4, "catálogo\n+ nodos", rot=0)
# filtered.graphml + catálogo -> app (carril superior)
ruta((7.25, 8.9), (7.25, 10.15), (17.7, 10.15), (17.7, 8.45), color=FLUJO, lw=1.7)
union(9.0, 10.15)
nota(12.0, 10.15, "grafo filtrado + catálogo → la app calcula las rutas en el momento")
# matriz -> R4 (por el pasillo entre scripts y módulos)
ruta((12.4, 7.2), (12.2, 7.2), (12.2, 2.3), (12.0, 2.3), color=FLUJO, lw=1.7)
nota(12.2, 3.6, "matriz 40×40")
# envolvente -> app
ruta((14.5, 4.45), (15.0, 4.45), (15.0, 7.6), (16.05, 7.6), color=FLUJO, lw=1.7)
nota(15.0, 6.0, "envolvente", rot=90)
# la app importa los mismos módulos que se miden (verde punteado)
ruta((14.5, 8.85), (15.3, 8.85), (15.3, 8.25), (16.05, 8.25), color=VERDE, lw=1.3, ls="--")
ruta((14.5, 5.6), (15.3, 5.6), (15.3, 8.85), color=VERDE, lw=1.3, ls="--", flecha=False)
ruta((14.5, 1.8), (15.3, 1.8), (15.3, 5.6), color=VERDE, lw=1.3, ls="--", flecha=False)

# ---------------------------------------------------------------- Pie: utilidades y leyenda
caja(5.6, -0.15, "auxiliar_functions.py: medición (5 repeticiones, mediana), CSV, tablas y datos de la máquina;"
                 " lo usan los scripts de experimentos de R1 a R4", "script", w=10.9, h=0.55, fs=8.6)
for x, t, k in [(11.4, "Código", "script"), (12.85, "Archivo de datos", "archivo"),
                (15.0, "Fuente externa", "externo")]:
    ax.add_patch(FancyBboxPatch((x, -0.28), 0.42, 0.26, boxstyle="round,pad=0.01", lw=1.2, **ESTILO[k]))
    ax.text(x + 0.52, -0.15, t, va="center", fontsize=9)
ax.plot([16.95, 17.35], [0.0, 0.0], color=FLUJO, lw=1.8)
ax.text(17.45, 0.0, "Datos entre requerimientos", va="center", fontsize=9)
ax.plot([16.95, 17.35], [-0.33, -0.33], color=VERDE, lw=1.3, ls="--")
ax.text(17.45, -0.33, "La app importa el módulo", va="center", fontsize=9)

ax.text(10, 10.6, "Arquitectura de la solución: componentes y flujo de datos entre requerimientos",
        ha="center", va="center", fontsize=15, weight="bold")
fig.tight_layout()
fig.savefig(SALIDA, dpi=170, facecolor="white")
print(f"Diagrama guardado en {SALIDA}")
