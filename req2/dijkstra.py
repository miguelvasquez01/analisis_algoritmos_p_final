import heapq
import time
import networkx as nx

def dijkstra_lineal(G, source, target=None, weight='travel_time'):
    """
    Dijkstra con búsqueda lineal sobre un arreglo de distancias.
    Complejidad: O(V^2)
    """
    nodos = list(G.nodes)
    dist = {node: float('inf') for node in nodos}
    pred = {node: None for node in nodos}
    dist[source] = 0
    
    unvisited = set(nodos)
    nodos_explorados = 0

    while unvisited:
        # Búsqueda lineal del nodo con menor distancia no visitado O(V)
        u = min(unvisited, key=lambda node: dist[node])
        
        if dist[u] == float('inf'):
            break  # No hay más nodos alcanzables
            
        unvisited.remove(u)
        nodos_explorados += 1

        if target is not None and u == target:
            break

        # Relajación de aristas
        for v, edge_data in G[u].items():
            if v in unvisited:
                # Obtener el peso mínimo entre multiaristas
                costo_arista = min(
                    d.get(weight, d.get('length', 1) / (d.get('speed_kph', 30) / 3.6)) 
                    for d in edge_data.values()
                )
                if dist[u] + costo_arista < dist[v]:
                    dist[v] = dist[u] + costo_arista
                    pred[v] = u

    # Reconstrucción de la ruta si hay un destino específico
    if target is not None:
        if dist[target] == float('inf'):
            return float('inf'), [], nodos_explorados
        ruta = []
        curr = target
        while curr is not None:
            ruta.append(curr)
            curr = pred[curr]
        ruta.reverse()
        return dist[target], ruta, nodos_explorados

    return dist, pred, nodos_explorados


def dijkstra_min_heap(G, source, target=None, weight='travel_time'):
    """
    Dijkstra utilizando Cola de Prioridad (Min-Heap).
    Complejidad: O((V + E) log V)
    """
    dist = {node: float('inf') for node in G.nodes}
    pred = {node: None for node in G.nodes}
    dist[source] = 0

    # Heap contiene tuplas (distancia, nodo)
    pq = [(0, source)]
    visited = set()
    nodos_explorados = 0

    while pq:
        d_u, u = heapq.heappop(pq)

        if u in visited:
            continue
        
        visited.add(u)
        nodos_explorados += 1

        if target is not None and u == target:
            break

        for v, edge_data in G[u].items():
            costo_arista = min(
                d.get(weight, d.get('length', 1) / (d.get('speed_kph', 30) / 3.6)) 
                for d in edge_data.values()
            )
            if dist[u] + costo_arista < dist[v]:
                dist[v] = dist[u] + costo_arista
                pred[v] = u
                heapq.heappush(pq, (dist[v], v))

    if target is not None:
        if dist[target] == float('inf'):
            return float('inf'), [], nodos_explorados
        ruta = []
        curr = target
        while curr is not None:
            ruta.append(curr)
            curr = pred[curr]
        ruta.reverse()
        return dist[target], ruta, nodos_explorados

    return dist, pred, nodos_explorados