# Especificación – Requerimiento 4: Ruta óptima de recorrido (ATSP)

## Entrada
- Matriz de tiempos 40 × 40 en segundos (`req2/matriz_tiempos.csv`), no simétrica, generada con Dijkstra con cola de prioridad desde cada lugar.
- Lugar de partida por defecto: Armenia (id 1). Los k lugares se eligen al azar entre los otros 39, con semilla fija.

## Comportamiento esperado (`req4/tsp.py`)
- `tsp_fuerza_bruta(D)`: enumera todas las permutaciones (sin poda) y devuelve `(costo, recorrido)`. Lanza `LimiteDeTiempo` si pasa de 300 s.
- `tsp_held_karp(D)`: programación dinámica sobre subconjuntos; devuelve el costo óptimo **y el recorrido**.
- `tsp_vecino_mas_cercano(D)`: heurística voraz; respeta el sentido D[i][j].
- Todos los recorridos empiezan y terminan en el índice 0 y visitan cada lugar exactamente una vez.

## Casos de prueba
- 300 matrices aleatorias con n = 1..8: fuerza bruta y Held-Karp dan el mismo costo; el costo del recorrido de Held-Karp coincide con el costo devuelto; la voraz nunca es menor que el óptimo.
- En el experimento, para k = 5..11, fuerza bruta = Held-Karp (assert).
- Contraejemplo con k = 3 donde la voraz no es óptima.

## Experimentos (`req4/1_experimentos_tsp.py`)
1. Tiempo vs k (5..12; Held-Karp además 13..16), semilla `42 + k`. Límite de 5 min.
2. Calidad de la voraz: k = 5, 8, 10, 12; 10 instancias por k, semilla `1000 + 100k + i`.
3. Itinerario de un día (11 h = 660 min) desde Armenia con 8 atractivos; si no cabe, se quita el atractivo cuya eliminación libera más tiempo y se recalcula con Held-Karp.
4. Contraejemplo voraz vs óptimo.
