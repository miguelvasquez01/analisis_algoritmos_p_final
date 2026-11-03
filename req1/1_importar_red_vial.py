import os
import osmnx as ox
from datetime import datetime

# 1. Configurar OSMnx para guardar la caché donde prefieras (opcional) o desactivarla
ox.settings.use_cache = True
ox.settings.cache_folder = "req1/osmnx_cache"  # Cambia la ruta según tu preferencia

# Registramos la fecha de descarga requerida
FECHA_DESCARGA = datetime.now().strftime("%Y-%m-%d")
print(f"Fecha de descarga de la red vial: {FECHA_DESCARGA}")

# 1. Descarga de la red vial de conducción para el Quindío
LUGAR = "Quindío, Colombia"
G = ox.graph_from_place(LUGAR, network_type="drive")

ruta_destino = os.path.join(os.getcwd(), "req1/red_vial_quindio.graphml")
ox.save_graphml(G, filepath=ruta_destino)

print(f"Grafo descargado con éxito: {len(G.nodes)} nodos y {len(G.edges)} aristas.")