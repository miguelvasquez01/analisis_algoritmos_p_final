"""
Dijkstra con cola de prioridad (implementación propia) y utilidades del req. 2.

Se usa `heapq` (montículo binario de la librería estándar) solo como estructura
de apoyo: heappush/heappop en O(log n). Con 'lazy deletion' la cola puede tener
hasta E entradas, así que cada operación cuesta O(log E) = O(log V) (E <= V^2).

Complejidad: O((V + E) log V) en tiempo y O(V + E) en memoria
(Cormen et al., 2022, Introduction to Algorithms, 4th ed., sec. 22.3).

La ejecución de los experimentos y el cálculo de la matriz están en req2/req2.py.
"""
import heapq
import math


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
    (dist, pred, explorados). Un nodo cuenta como explorado una sola vez,
    la primera vez que sale de la cola."""
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


def costo_ruta(adj, ruta):
    """Suma de los pesos de la ruta en la lista de adyacencia (para verificar)."""
    pesos = {u: dict(vecinos) for u, vecinos in adj.items()}
    return sum(pesos[u][v] for u, v in zip(ruta, ruta[1:]))


def matriz_tiempos(adj, nodos_lugares):
    """Una ejecución de Dijkstra (sin destino) desde cada lugar -> matriz n x n (s)."""
    n = len(nodos_lugares)
    M = [[0.0] * n for _ in range(n)]
    for i, s in enumerate(nodos_lugares):
        dist, _, _ = dijkstra_heap(adj, s)
        for j, t in enumerate(nodos_lugares):
            M[i][j] = dist.get(t, math.inf)
    return M
