"""Rutas a los archivos del proyecto y carga de datos.

Agrega al sys.path la raíz y las carpetas req2, req3 y req4 para importar las
implementaciones propias sin modificarlas (mismo patrón que los scripts del repo)."""
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import osmnx as ox
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
for carpeta in (RAIZ, RAIZ / "req2", RAIZ / "req3", RAIZ / "req4"):
    if str(carpeta) not in sys.path:
        sys.path.append(str(carpeta))

from dijkstra_heap import construir_lista_adyacencia  # noqa: E402

RUTA_GRAFO = RAIZ / "req1" / "red_vial_quindio_filtered.graphml"     # SCC, WGS84
RUTA_CATALOGO = RAIZ / "req1" / "catalogo_lugares_nodos.csv"
RUTA_MATRIZ = RAIZ / "req2" / "matriz_tiempos.csv"
RUTA_ENVOLVENTE = RAIZ / "req3" / "resultados" / "req3_envolvente_red.json"
CRS_UTM = "EPSG:32618"
ID_ARMENIA = 1
CATEGORIA_ATRACTIVO = "Atractivo turístico"


@dataclass
class Red:
    """Componente fuertemente conexa: grafo de OSMnx (para coordenadas y geometría)
    y listas de adyacencia {u: [(v, travel_time_s), ...]} que usa Dijkstra."""
    G: object
    adj: dict


def cargar_red():
    G = ox.load_graphml(RUTA_GRAFO)
    return Red(G=G, adj=construir_lista_adyacencia(G, peso="travel_time"))


def cargar_catalogo():
    """Catálogo indexado por id, con el nodo de la red asociado (req1.4)."""
    return pd.read_csv(RUTA_CATALOGO).set_index("id")


def cargar_matriz():
    """Matriz de tiempos precalculada en req2 (s), como {id: {id: s}}. Solo se usa para verificar."""
    M = pd.read_csv(RUTA_MATRIZ, index_col=0)
    M.columns = M.columns.astype(int)
    return {int(i): {int(j): float(M.loc[i, j]) for j in M.columns} for i in M.index}


def cargar_envolvente():
    with open(RUTA_ENVOLVENTE, encoding="utf-8") as f:
        return json.load(f)
