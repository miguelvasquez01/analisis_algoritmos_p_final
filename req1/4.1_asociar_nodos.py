from pathlib import Path
import sys
import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.geometry import Point

# Resolver ruta raíz del proyecto
sys.path.append(str(Path(__file__).resolve().parent.parent))
from auxiliar_functions import (
    generar_tabla_desde_csv,
    guardar_resultados_csv,
)

def asociar_lugares_utm18n(G_scc, ruta_catalogo_csv, epsg_target='EPSG:32618'):
  """Proyecta el grafo a UTM Zona 18N (EPSG:32618), vincula los lugares del catálogo

  al nodo más cercano y calcula la distancia euclidiana en metros.

  Retorna:
      tuple: (G_proj, df_catalogo_procesado)
  """
  # 1. Proyectar el grafo a UTM 18N (coordenadas planas en metros)
  G_proj = ox.project_graph(G_scc, to_crs=epsg_target)

  # 2. Cargar catálogo de lugares
  df_catalogo = pd.read_csv(ruta_catalogo_csv)

  # 3. Convertir catálogo a GeoDataFrame en WGS84 y reproyectar a UTM 18N
  geometry = [Point(xy) for xy in zip(df_catalogo['lon'], df_catalogo['lat'])]
  gdf_lugares = gpd.GeoDataFrame(df_catalogo, geometry=geometry, crs='EPSG:4326')
  gdf_lugares_proj = gdf_lugares.to_crs(epsg_target)

  # Extraer coordenadas planas (en metros)
  x_coords = gdf_lugares_proj.geometry.x.values
  y_coords = gdf_lugares_proj.geometry.y.values

  # 4. Encontrar el nodo proyectado más cercano en metros
  nodos_cercanos = ox.distance.nearest_nodes(G_proj, X=x_coords, Y=y_coords)
  df_catalogo['nodo_osm'] = nodos_cercanos

  # 5. Calcular distancia euclidiana exactas en metros
  distancias_m = []
  for idx, row in gdf_lugares_proj.iterrows():
    nodo_id = nodos_cercanos[idx]
    nodo_data = G_proj.nodes[nodo_id]

    x_lugar, y_lugar = row.geometry.x, row.geometry.y
    x_nodo, y_nodo = nodo_data['x'], nodo_data['y']

    # Distancia euclidiana plana en metros
    dist_m = ((x_lugar - x_nodo) ** 2 + (y_lugar - y_nodo) ** 2) ** 0.5
    distancias_m.append(round(dist_m, 2))

  df_catalogo['distancia_al_nodo_m'] = distancias_m

  return G_proj, df_catalogo

# 1. Cargar la componente fuertemente conexa guardada en el Requerimiento 3
G_scc = ox.load_graphml("req1/red_vial_quindio_filtered.graphml")

# 2. Ejecutar la asociación y proyección a UTM Zona 18N
ruta_catalogo = "req1/catalogo_lugares_quindio.csv"
G_proj, df_catalogo_procesado = asociar_lugares_utm18n(G_scc, ruta_catalogo)

# 3. Guardar catálogo procesado con nodos y distancias en CSV
ruta_salida_csv = "req1/catalogo_lugares_nodos.csv"
guardar_resultados_csv(df_catalogo_procesado, ruta_salida_csv)

# 4. Guardar la versión proyectada del grafo
ox.save_graphml(G_proj, filepath="req1/red_vial_quindio_utm18n.graphml")

# 5. Reporte de lugares a más de 500 metros
df_lejos = df_catalogo_procesado[
    df_catalogo_procesado["distancia_al_nodo_m"] > 500.0
]
ruta_lejos_csv = "req1/resultados/requerimiento_4_lugares_mas_500m.csv"
guardar_resultados_csv(df_lejos, ruta_lejos_csv)

# Mostrar tablas en consola
generar_tabla_desde_csv(
    ruta_salida_csv,
    titulo_tabla="Catálogo Procesado y Distancias a Nodos viales (UTM 18N)",
    unidad_tiempo="N/A (Metros)",
)

print(f"\n--- REPORTES DE LUGARES A MÁS DE 500 METROS ---")
print(
    f"Total de lugares a > 500 m del nodo de carretera más cercano:"
    f" {len(df_lejos)}"
)
if len(df_lejos) > 0:
  print(df_lejos[["id", "nombre", "categoria", "distancia_al_nodo_m"]])