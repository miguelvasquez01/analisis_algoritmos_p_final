import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from dijkstra import dijkstra_lineal, dijkstra_min_heap

# 1. Cargar Red Vial proyectada y Catálogo de Lugares
print("Cargando grafo proyectado y catálogo de lugares...")
G = nx.read_graphml("req1/red_vial_quindio_utm18n.graphml")
cat_lugares = pd.read_csv("req1/catalogo_lugares_nodos.csv")

# Asegurar que el tipo de datos de los nodos coincida con el grafo
cat_lugares['nodo_osm'] = cat_lugares['nodo_osm'].astype(type(list(G.nodes)[0]))

# 2. Selección de Pares del Catálogo para el Benchmark
# A. 10 Pares Cercanos (Mismo municipio o municipios vecinos)
pares_cercanos = []
for i in range(len(cat_lugares)):
    for j in range(i + 1, len(cat_lugares)):
        l1 = cat_lugares.iloc[i]
        l2 = cat_lugares.iloc[j]
        # Filtrar si están en el mismo municipio
        if l1['municipio'] == l2['municipio']:
            pares_cercanos.append((l1['nodo_osm'], l2['nodo_osm'], l1['nombre'], l2['nombre']))
        if len(pares_cercanos) == 10:
            break
    if len(pares_cercanos) == 10:
        break

# B. Completa hasta 20 pares usando otros lugares del catálogo
pares_catalogo = [(row1['nodo_osm'], row2['nodo_osm']) 
                  for i, row1 in cat_lugares.iterrows() 
                  for j, row2 in cat_lugares.iterrows() if i != j]

# Seleccionamos 20 pares en total (los 10 cercanos + 10 adicionales del catálogo)
pares_20_evaluacion = [(p[0], p[1]) for p in pares_cercanos]
for p in pares_catalogo:
    if p not in pares_20_evaluacion and (p[1], p[0]) not in pares_20_evaluacion:
        pares_20_evaluacion.append(p)
    if len(pares_20_evaluacion) == 20:
        break

# 3. Ejecución del Benchmarking y Verificación
resultados_bench = []
print("Ejecutando Benchmarking sobre pares del catálogo...")

for idx, (orig, dest) in enumerate(pares_20_evaluacion):
    # Medición con Cola de Prioridad (Se ejecuta en los 20 pares)
    t0 = time.perf_counter()
    dist_h, ruta_h, exp_h = dijkstra_min_heap(G, orig, dest)
    t_heap = time.perf_counter() - t0

    # Medición Lineal (Solo en los primeros 10 pares cercanos)
    if idx < 10:
        t0 = time.perf_counter()
        dist_l, ruta_l, exp_l = dijkstra_lineal(G, orig, dest)
        t_lineal = time.perf_counter() - t0

        # VERIFICACIÓN: Comprobar la igualdad de tiempos en ambas versiones
        assert abs(dist_h - dist_l) < 1e-4, \
            f"ERROR: Tiempos discrepantes en el par {idx+1} ({dist_h:.2f}s vs {dist_l:.2f}s)"
    else:
        t_lineal, exp_l = np.nan, np.nan

    resultados_bench.append({
        'par_idx': idx + 1,
        'origen': orig,
        'destino': dest,
        'tiempo_heap_ms': t_heap * 1000,
        'tiempo_lineal_ms': t_lineal * 1000 if not np.isnan(t_lineal) else np.nan,
        'nodos_exp_heap': exp_h,
        'nodos_exp_lineal': exp_l,
        'cociente_tiempo': (t_lineal / t_heap) if not np.isnan(t_lineal) else np.nan
    })

df_bench = pd.DataFrame(resultados_bench)

# 4. Cálculo de Estadísticas del Cociente (Lineal / Heap)
df_10_pares = df_bench.dropna(subset=['cociente_tiempo'])
cocientes = df_10_pares['cociente_tiempo']

print("\n--- RESULTADOS DEL COCIENTE DE TIEMPOS (Lineal / Min-Heap) ---")
print(f"Mediana: {cocientes.median():.2f}x")
print(f"Mínimo:  {cocientes.min():.2f}x")
print(f"Máximo:  {cocientes.max():.2f}x")

# 5. Generación de Gráfica: Tiempo vs Nodos Explorados
plt.figure(figsize=(10, 6))
plt.scatter(df_10_pares['nodos_exp_lineal'], df_10_pares['tiempo_lineal_ms'], 
            color='red', label='Dijkstra Lineal O(V^2)', alpha=0.8, s=50)
plt.scatter(df_bench['nodos_exp_heap'], df_bench['tiempo_heap_ms'], 
            color='blue', label='Dijkstra Min-Heap O((V+E) log V)', alpha=0.8, s=50)

plt.title('Tiempo de Ejecución vs. Nodos Explorados en la Red de Quindío')
plt.xlabel('Nodos Explorados')
plt.ylabel('Tiempo de Ejecución (ms)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('req2/grafica_tiempo_vs_nodos.png')
plt.close()

# 6. Cálculo de Matriz Asimétrica de Tiempos 40x40
print("\nCalculando Matriz de Tiempos 40x40 desde el Catálogo...")
nodos_cat = cat_lugares['nodo_osm'].tolist()
n_lugares = len(nodos_cat)
matriz_tiempos = np.zeros((n_lugares, n_lugares))

for idx_orig, orig_node in enumerate(nodos_cat):
    # Algoritmo de origen único (Single-Source) sin nodo destino (target=None)
    dist_map, _, _ = dijkstra_min_heap(G, orig_node, target=None)
    for idx_dest, dest_node in enumerate(nodos_cat):
        matriz_tiempos[idx_orig, idx_dest] = dist_map[dest_node]

# Guardar la matriz asimétrica
df_matriz = pd.DataFrame(
    matriz_tiempos, 
    index=cat_lugares['nombre'], 
    columns=cat_lugares['nombre']
)
df_matriz.to_csv('req2/matriz_tiempos_40x40.csv')
print("Proceso finalizado con éxito. Matriz y gráfica guardadas.")