import osmnx as ox
import pandas as pd
import sys
from pathlib import Path
# Añadir la carpeta raíz (p_final) al sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from auxiliar_functions import (medir_tiempo_ejecucion, guardar_resultados_csv, generar_tabla_desde_csv)

# Configuración de caché
ox.settings.use_cache = True
ox.settings.cache_folder = "req1/osmnx_cache"

plaza_bolivar_armenia = (4.532417, -75.673028)

pruebas = [
    ("Armenia 2 km", 2000),
    ("Armenia 5 km", 5000),
    ("Armenia 10 km", 10000),
    ("Armenia 20 km", 20000)
]

resultados = []

print("=== 1. MIDIENDO TIEMPOS EN SUBREDES CRECIENTES ===")

for nombre, radio in pruebas:
    print(f"\nDescargando y midiendo {nombre}...")
    sub_G = ox.graph_from_point(plaza_bolivar_armenia, dist=radio, network_type="drive")
    
    # Uso genérico: pasamos la función, el grafo y la bandera strongly=True
    sub_SCC, tiempo_ms, unidad = medir_tiempo_ejecucion(
        ox.truncate.largest_component, 
        sub_G, 
        strongly=True,
        unidad_tiempo="ms"
    )
    
    V, E = len(sub_G.nodes), len(sub_G.edges)
    
    resultados.append({
        "Red": nombre,
        "Nodos (V)": V,
        "Aristas (E)": E,
        "Tamaño (V + E)": V + E,
        "Tiempo Mediana (ms)": tiempo_ms
    })

# Red Completa
print("\n=== 2. FILTRANDO RED COMPLETA DEL QUINDÍO ===")
G = ox.load_graphml("req1/red_vial_quindio.graphml")

V_inicial, E_inicial = len(G.nodes), len(G.edges)

G_scc, tiempo_ms, unidad = medir_tiempo_ejecucion(
    ox.truncate.largest_component, 
    G, 
    strongly=True,
    unidad_tiempo="ms"
)

V_final, E_final = len(G_scc.nodes), len(G_scc.edges)

resultados.append({
    "Red": "Quindío Completo",
    "Nodos (V)": V_inicial,
    "Aristas (E)": E_inicial,
    "Tamaño (V + E)": V_inicial + E_inicial,
    "Tiempo Mediana (ms)": tiempo_ms
})

ruta_salida_csv = "req1/resultados/requerimiento_3_scc.csv"

# 1. Guardar primero en CSV
guardar_resultados_csv(resultados, ruta_salida_csv)

# 2. Generar y mostrar la tabla leyendo directamente desde el CSV
df_resultado = generar_tabla_desde_csv(
    ruta_salida_csv, 
    titulo_tabla="Medición de Complejidad para Extracción de Mayor SCC",
    unidad_tiempo="milisegundos (ms)"
)

# 3. Guardar la red filtrada lista
ox.save_graphml(G_scc, filepath="req1/red_vial_quindio_filtered.graphml")
print(f"\n¡Grafo procesado guardado exitosamente! Tamaño final: {V_final} nodos y {E_final} aristas.")