"""
Dijkstra con cola de prioridad (implementación propia) y cálculo de la
matriz de tiempos entre los lugares del catálogo.

La matriz es la entrada del Requerimiento 4 (problema del viajante asimétrico).
Se usa `heapq` (montículo binario de la librería estándar) solo como estructura
de apoyo: push/pop en O(log n).

Complejidad: O((V + E) log V) en tiempo y O(V + E) en memoria
(Cormen et al., 2022, Introduction to Algorithms, 4th ed., sec. 22.3).
"""
import heapq
import math
from pathlib import Path

import osmnx as ox
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RUTA_GRAFO = RAIZ / "req1" / "red_vial_quindio_filtered.graphml"
RUTA_CATALOGO = RAIZ / "req1" / "catalogo_lugares_nodos.csv"
RUTA_MATRIZ = RAIZ / "req2" / "matriz_tiempos.csv"


def construir_lista_adyacencia(G, peso="travel_time"):
    """Convierte el MultiDiGraph de OSMnx en listas de adyacencia {u: [(v, w), ...]}.
    Si hay aristas paralelas u->v se conserva la de menor peso."""
    mejor = {}
    for u, v, d in G.edges(data=True):
        w = float(d[peso])
        if (u, v) not in mejor or w < mejor[(u, v)]:
            mejor[(u, v)] = w
    adj = {n: [] for n in G.nodes}
    for (u, v), w in mejor.items():
        adj[u].append((v, w))
    return adj


def dijkstra_heap(adj, origen, destino=None):
    """Dijkstra con montículo binario y 'lazy deletion'.

    Si `destino` se da, se detiene al sacarlo de la cola y devuelve
    (tiempo, ruta, explorados). Si no, recorre todo el grafo y devuelve
    (dist, pred, explorados)."""
    dist = {origen: 0.0}
    pred = {origen: None}
    explorados = set()
    cola = [(0.0, origen)]
    while cola:
        d, u = heapq.heappop(cola)
        if u in explorados:          # entrada obsoleta
            continue
        explorados.add(u)
        if u == destino:
            ruta = []
            while u is not None:
                ruta.append(u)
                u = pred[u]
            return d, ruta[::-1], len(explorados)
        for v, w in adj[u]:
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                pred[v] = u
                heapq.heappush(cola, (nd, v))
    if destino is not None:
        return math.inf, [], len(explorados)
    return dist, pred, len(explorados)


def matriz_tiempos(adj, nodos_lugares):
    """Una ejecución de Dijkstra (sin destino) desde cada lugar -> matriz n x n (s)."""
    n = len(nodos_lugares)
    M = [[0.0] * n for _ in range(n)]
    for i, s in enumerate(nodos_lugares):
        dist, _, _ = dijkstra_heap(adj, s)
        for j, t in enumerate(nodos_lugares):
            M[i][j] = dist.get(t, math.inf)
    return M


if __name__ == "__main__":
    G = ox.load_graphml(RUTA_GRAFO)
    adj = construir_lista_adyacencia(G)
    cat = pd.read_csv(RUTA_CATALOGO)
    M = matriz_tiempos(adj, cat["nodo_osm"].tolist())

    # Verificación contra NetworkX (solo para comprobar resultados)
    import networkx as nx
    import random
    random.seed(42)
    for _ in range(30):
        i, j = random.randrange(40), random.randrange(40)
        ref = nx.shortest_path_length(G, cat.nodo_osm[i], cat.nodo_osm[j], weight="travel_time")
        assert abs(ref - M[i][j]) < 1e-6, (i, j, ref, M[i][j])
    print("Verificación contra NetworkX: OK (30 pares)")

    df = pd.DataFrame(M, index=cat["id"], columns=cat["id"])
    df.index.name = "id_origen"
    df.round(3).to_csv(RUTA_MATRIZ)
    asim = sum(abs(M[i][j] - M[j][i]) > 1 for i in range(40) for j in range(i + 1, 40))
    print(f"Matriz {len(M)}x{len(M)} guardada en {RUTA_MATRIZ}. Pares asimétricos (>1 s): {asim}")
