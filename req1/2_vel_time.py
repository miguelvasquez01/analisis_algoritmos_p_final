import osmnx as ox

G = ox.load_graphml("req1/red_vial_quindio.graphml")

# 1. Asignar/imputar velocidades a cada arista (en km/h)
# Si 'maxspeed' no existe, asigna valores por defecto según el tipo de vía (highway)
G = ox.add_edge_speeds(G)

# 2. Calcular el tiempo de viaje de cada arista (en segundos)
# Añade el atributo 'travel_time' a cada arista
G = ox.add_edge_travel_times(G)

ox.save_graphml(G, filepath="req1/red_vial_quindio.graphml")

# 3. Verificación: Inspeccionar los atributos calculados en una arista de ejemplo
# Tomamos la primera arista del grafo para comprobar
u, v, k, data = list(G.edges(data=True, keys=True))[0]

print("=== VERIFICACIÓN DE ATRIBUTOS EN UNA ARISTA DE EJEMPLO ===")
print(f"Tramo entre nodo {u} y nodo {v}:")
print(f" - Distancia (length): {data.get('length'):.2f} metros")
print(f" - Tipo de vía (highway): {data.get('highway')}")
print(f" - Velocidad asignada (speed_kph): {data.get('speed_kph')} km/h")
print(f" - Tiempo estimado (travel_time): {data.get('travel_time'):.2f} segundos")