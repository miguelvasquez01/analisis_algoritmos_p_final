# Incializacion:

(Solo la primera vez, para preparar los datos)
- Debe tener python instalado.
- Asegurese de tener instalada la libreria osmnx para importar la red vial de OpenStreetMap con `py -m pip install osmnx`
- Para hacer busqueda espacial en arboles: `pip install scipy`
- Ejecute los siguientes comandos en orden:
1. py req1/1_importar_red_vial.py
2. py req1/2_vel_time.py
3. py req1/3_componente_conexo.py
4. py req1/4_catalogo.py
5. py req1/4.1_asociar_nodos.py


# Archivos de datos:
- red_vial_quindio.graphml: Grafo directamnete descargado.
- red_vial_quindio_filtered.graphml: Grafo scc.
- red_vial_quindio_utm18n.graphml: Grafo scc en UTM 18N.

- catalogo_lugares_quindio.csv: Los 40 lugares pedidos.
- catalogo_lugares_nodos.csv: Mismo catalogo_lugares_quindio.csv pero con los ids de los nodos mas cercanos del Grafo scc original.


Por cada algoritmo: Big(O) de tiempo y memoria con fuentes, medir 5 veces, una sola unidad de tiempo, pregunta al profe(anexo y otras mediciones propias), hacer csv o json de resultados.