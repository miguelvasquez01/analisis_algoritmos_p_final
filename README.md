# Instalación

Requiere Python 3.11 o superior. Desde la raíz del repositorio:

```
py -m venv .venv
.venv\Scripts\activate          (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

# Requerimiento 5 (aplicación)

Los datos procesados ya están en el repositorio, así que la aplicación no necesita volver a descargar la red.
Desde la raíz del repositorio, con el entorno activado:

```
streamlit run app/Inicio.py
```

Se abre en http://localhost:8501. Páginas:
- **Ruta mínima**: origen y destino del catálogo → ruta en el mapa, tiempo de viaje, distancia y nodos explorados (Dijkstra con cola de prioridad, `req2/dijkstra_heap.py`).
- **Envolvente**: envolvente convexa sobre el mapa del departamento (`req3/resultados/req3_envolvente_red.json`), con botón para recalcularla con el QuickHull propio.
- **Itinerario**: lugar de partida (por defecto Armenia) y 6 a 8 atractivos → recorrido con Held-Karp y con el vecino más cercano, tiempo total de cada uno, diferencia y si cabe en 11 h (opcionalmente aplica el criterio de recorte del req. 4).
- **Resultados**: tablas y gráficas de los requerimientos 1 a 4, leídas de `req*/resultados/`.

Las rutas y el itinerario se calculan en el momento con las implementaciones propias. Estructura:
- `app/servicios/`: carga de datos y orquestación de los algoritmos (sin Streamlit).
- `app/pages/`, `app/Inicio.py`, `app/ui.py`: interfaz (Streamlit + Folium).
- Verificación de la app contra los resultados de req2, req3 y req4: `py app/verificar_app.py`

# Inicialización de los datos

(Solo si se quieren regenerar los datos; ya están en el repositorio)
- Ejecute los siguientes comandos en orden:
1. py req1/1_importar_red_vial.py
2. py req1/2_vel_time.py
3. py req1/3_componente_conexo.py
4. py req1/4_catalogo.py
5. py req1/4.1_asociar_nodos.py
6. py req2/dijkstra_heap.py  (matriz de tiempos 40x40 que usa el req4)

# Requerimiento 3 (envolvente convexa)
- py req3/1_envolvente_experimento.py  -> req3/resultados/

# Requerimiento 4 (viajante asimétrico)
- py req4/1_experimentos_tsp.py        -> req4/resultados/ (todo)
- py req4/1_experimentos_tsp.py 3 4 5  -> solo calidad, itinerario y contraejemplo (rápido)
- El punto 1 tarda ~10 min: la fuerza bruta con k=12 se corta a los 5 min.
- La lógica del itinerario de un día (criterio de recorte) está en `req4/itinerario.py`; la usan el script y la aplicación.


# Archivos de datos:
- red_vial_quindio.graphml: Grafo directamnete descargado.
- red_vial_quindio_filtered.graphml: Grafo scc.
- red_vial_quindio_utm18n.graphml: Grafo scc en UTM 18N.

- catalogo_lugares_quindio.csv: Los 40 lugares pedidos.
- catalogo_lugares_nodos.csv: Mismo catalogo_lugares_quindio.csv pero con los ids de los nodos mas cercanos del Grafo scc original.


Por cada algoritmo: Big(O) de tiempo y memoria con fuentes, medir 5 veces, una sola unidad de tiempo, pregunta al profe(anexo y otras mediciones propias), hacer csv o json de resultados.