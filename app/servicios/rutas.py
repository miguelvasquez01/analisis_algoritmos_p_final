"""Ruta mínima entre dos lugares con Dijkstra con cola de prioridad (req2, implementación propia)."""
import math
import time
from dataclasses import dataclass

from dijkstra_heap import dijkstra_heap


@dataclass
class Ruta:
    tiempo_s: float
    distancia_m: float
    nodos: list          # secuencia de nodos OSM
    coords: list         # [(lat, lon), ...] siguiendo la geometría de las vías
    explorados: int
    calculo_ms: float


def _mejor_arista(G, u, v):
    """Entre aristas paralelas u->v, la de menor tiempo (la misma que usa la lista de adyacencia)."""
    return min(G[u][v].values(), key=lambda d: float(d["travel_time"]))


def coords_de_ruta(G, nodos):
    """Convierte una secuencia de nodos en coordenadas (lat, lon), usando la geometría
    de cada tramo cuando existe para que la línea siga la vía."""
    if not nodos:
        return []
    coords = [(G.nodes[nodos[0]]["y"], G.nodes[nodos[0]]["x"])]
    for u, v in zip(nodos, nodos[1:]):
        geom = _mejor_arista(G, u, v).get("geometry")
        if geom is not None:
            coords.extend((lat, lon) for lon, lat in list(geom.coords)[1:])
        else:
            coords.append((G.nodes[v]["y"], G.nodes[v]["x"]))
    return coords


def distancia_de_ruta(G, nodos):
    return sum(float(_mejor_arista(G, u, v)["length"]) for u, v in zip(nodos, nodos[1:]))


def ruta_entre(red, nodo_origen, nodo_destino):
    """Dijkstra con heap que se detiene al sacar el destino. Devuelve un objeto Ruta."""
    t0 = time.perf_counter()
    tiempo, nodos, explorados = dijkstra_heap(red.adj, nodo_origen, nodo_destino)
    ms = (time.perf_counter() - t0) * 1000
    if math.isinf(tiempo):
        return Ruta(tiempo, math.inf, [], [], explorados, ms)
    return Ruta(tiempo, distancia_de_ruta(red.G, nodos), nodos,
                coords_de_ruta(red.G, nodos), explorados, ms)


def camino_desde_predecesores(pred, destino):
    """Reconstruye la secuencia de nodos origen -> destino a partir de los predecesores."""
    if destino not in pred:
        return []
    camino = []
    while destino is not None:
        camino.append(destino)
        destino = pred[destino]
    return camino[::-1]
