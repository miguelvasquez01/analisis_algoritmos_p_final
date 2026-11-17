"""
Dijkstra con búsqueda lineal del mínimo (implementación propia).

Recibe la misma lista de adyacencia {u: [(v, w), ...]} que `dijkstra_heap`
(ver `construir_lista_adyacencia` en dijkstra_heap.py), para que la única
diferencia entre las dos versiones sea cómo se elige el siguiente nodo:
aquí se recorren los V nodos buscando el de menor distancia tentativa.

Complejidad: O(V^2 + E) = O(V^2) en tiempo y O(V) en memoria adicional
(Cormen et al., 2022, Introduction to Algorithms, 4th ed., sec. 22.3: con un
arreglo simple, cada EXTRACT-MIN cuesta O(V) y hay V extracciones).
"""
import math


def dijkstra_lineal(adj, origen, destino=None):
    """Dijkstra con arreglo de distancias y búsqueda lineal del mínimo.

    Misma interfaz que `dijkstra_heap`:
      - con `destino`: se detiene al sacar el destino y devuelve (tiempo, ruta, explorados);
      - sin `destino`: recorre todo el grafo y devuelve (dist, pred, explorados).
    Un nodo cuenta como explorado una sola vez, cuando se extrae como mínimo."""
    nodos = list(adj)                                   # O(V)
    dist = dict.fromkeys(nodos, math.inf)               # "arreglo" de distancias
    pred = {origen: None}
    explorado = dict.fromkeys(nodos, False)
    dist[origen] = 0.0
    explorados = 0

    while True:
        # Recorrido lineal: el nodo no explorado con menor distancia tentativa. O(V)
        u, mejor = None, math.inf
        for n in nodos:
            if not explorado[n] and dist[n] < mejor:
                u, mejor = n, dist[n]
        if u is None:                                   # quedan solo nodos inalcanzables
            break

        explorado[u] = True
        explorados += 1

        if u == destino:
            ruta = []
            while u is not None:
                ruta.append(u)
                u = pred[u]
            return mejor, ruta[::-1], explorados

        for v, w in adj[u]:                             # relajación: O(grado(u))
            nd = mejor + w
            if nd < dist[v]:
                dist[v] = nd
                pred[v] = u

    if destino is not None:
        return math.inf, [], explorados
    return {n: d for n, d in dist.items() if d < math.inf}, pred, explorados
