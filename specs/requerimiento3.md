# Especificación – Requerimiento 3: Envolvente convexa

## Entrada
- Nodos de la componente fuertemente conexa en UTM 18N (`req1/red_vial_quindio_utm18n.graphml`).
- Coordenadas redondeadas al entero más cercano; puntos repetidos eliminados.
- Conjuntos aleatorios de 1 000, 10 000 y 50 000 puntos enteros distintos en [0, 100 000]², semilla 42.

## Comportamiento esperado
- `quickhull(puntos)` (implementación propia, divide y vencerás) devuelve los vértices de la envolvente en sentido antihorario.
- Los puntos colineales sobre un lado NO son vértices (solo giros estrictos, producto cruz > 0).
- Aritmética entera exacta (enteros de Python, sin desbordamiento).

## Casos de prueba
| Caso | Entrada | Vértices esperados |
|---|---|---|
| Cuadrado con puntos interiores | (0,0),(4,0),(4,4),(0,4),(2,2),(1,3) | 4 esquinas |
| Colineales en los lados | cuadrado 4×4 con puntos medios de cada lado | 4 esquinas |
| Triángulo con interiores | (0,0),(10,0),(5,8),(5,3),(6,1) | (0,0),(10,0),(5,8) |
| Empate en x mínima | (0,0),(0,5),(0,3),(10,2),(5,2) | (0,0),(0,5),(10,2) |
| Red vial y aleatorios | — | mismo conjunto de vértices que `scipy.spatial.ConvexHull` |

## Medición
- QuickHull propio y `ConvexHull` de SciPy, 5 repeticiones, mediana en ms. Solo se mide el cálculo (la lectura del grafo y la generación de puntos quedan fuera).
- Resultados: `req3/resultados/req3_tiempos_envolvente.csv`, `req3_envolvente_red.json`, `req3_envolvente_red.png`, `req3_tiempos.png`.
