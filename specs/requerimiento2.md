# Especificación – Requerimiento 2: Caminos mínimos (Dijkstra)

## Entrada
- Componente fuertemente conexa del req. 1 (`req1/red_vial_quindio_filtered.graphml`), cargada con `ox.load_graphml` (convierte `travel_time` a float; `nx.read_graphml` lo deja como texto).
- Peso: `travel_time` (s). Si hay aristas paralelas u→v se usa la de menor tiempo.
- Catálogo con nodo asociado (`req1/catalogo_lugares_nodos.csv`).

## Comportamiento esperado
Ambas versiones reciben la misma lista de adyacencia `{u: [(v, w), ...]}` (`construir_lista_adyacencia`) y tienen la misma interfaz:
- `f(adj, origen, destino)` → `(tiempo_s, ruta, explorados)`; se detiene al sacar `destino`. Si no es alcanzable: `(inf, [], explorados)`.
- `f(adj, origen)` → `(dist, pred, explorados)` recorriendo todo el grafo.
- La ruta se reconstruye con los predecesores y va de `origen` a `destino`.
- Un nodo cuenta como explorado una sola vez, la primera vez que se extrae.

| Versión | Archivo | Tiempo | Memoria |
|---|---|---|---|
| Recorrido lineal | `req2/dijkstra_lineal.py` | O(V² + E) = O(V²) | O(V) |
| Cola de prioridad (heapq, lazy deletion) | `req2/dijkstra_heap.py` | O((V + E) log V) | O(V + E) |

Fuente: Cormen, Leiserson, Rivest y Stein, *Introduction to Algorithms*, 4.ª ed., 2022, sec. 22.3.

## Correctitud
- **Invariante**: cada vez que un nodo u se extrae (se marca explorado), `dist[u]` es la distancia mínima real δ(origen, u); y para todo nodo no explorado, `dist[v]` es el menor costo de un camino a v que solo pasa por nodos explorados.
- **Parada temprana**: al extraer el destino su distancia ya es definitiva por el invariante; seguir no puede mejorarla.
- **Condición sobre los pesos**: no negativos (w ≥ 0). Con un peso negativo, un camino que pase por un nodo aún no explorado podría terminar siendo más corto que `dist[u]` y el invariante falla. Aquí `travel_time = length / velocidad ≥ 0`.

## Casos de prueba (`verificar()` en `req2/req2.py`)
- Grafo de 5 nodos resuelto a mano: a→d = 4 por a‑b‑c‑d (el arco directo cuesta 10); d→a inalcanzable → `(inf, [])`; distancias completas desde a = {a:0, b:1, c:3, d:4}.
- 20 pares del catálogo: heap = `networkx.shortest_path_length` (tolerancia 1e‑6) y el costo de la ruta devuelta = tiempo devuelto.
- 10 pares cercanos: lineal = heap.
- Matriz: 30 celdas al azar (semilla 42) = NetworkX; todas finitas.

## Experimentos (`req2/req2.py`)
1. 20 pares fijos (lista en el script): 10 cercanos (mismo municipio o vecinos) medidos con ambas versiones y 10 lejanos solo con heap. Mediana de 5 ejecuciones, en ms; solo se mide la llamada al algoritmo.
2. Gráfica tiempo vs nodos explorados con ambas versiones; cociente lineal/heap (mediana, mín, máx) en los 10 pares.
3. Matriz 40×40 (s) con heap sin destino, una vez por lugar → `req2/matriz_tiempos.csv` (entrada del req. 4 y de la app).
