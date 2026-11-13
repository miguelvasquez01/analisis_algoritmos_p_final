"""
Requerimiento 4 - Problema del viajante asimétrico (ATSP). Implementaciones propias.

Convención: `D` es una matriz n x n (lista de listas) de tiempos en segundos,
el índice 0 es el lugar de partida/llegada y 1..n-1 son los k = n-1 lugares
a visitar. Todas las funciones devuelven (costo_total, recorrido), donde el
recorrido empieza y termina en 0, p. ej. [0, 3, 1, 2, 0].
"""
import math
import time


class LimiteDeTiempo(Exception):
    """Se lanza cuando una ejecución supera el límite del protocolo (5 min)."""


# ---------------------------------------------------------------------------
# 1. Fuerza bruta: todas las permutaciones de los k lugares.
#    Tiempo O(k * k!)   (k! permutaciones; el costo se acumula de forma
#    incremental, así que cada hoja cuesta O(1) amortizado y los nodos
#    internos del árbol de recursión suman ~e*k!).  Memoria O(k).
# ---------------------------------------------------------------------------
def tsp_fuerza_bruta(D, limite_s=300.0):
    n = len(D)
    if n == 1:
        return 0.0, [0, 0]
    usados = [False] * n
    usados[0] = True
    actual = [0]
    mejor = [math.inf, None]
    t0 = time.perf_counter()
    hojas = [0]

    def permutar(ultimo, costo, nivel):
        if nivel == n:                               # permutación completa
            total = costo + D[ultimo][0]
            if total < mejor[0]:
                mejor[0] = total
                mejor[1] = actual + [0]
            hojas[0] += 1
            if hojas[0] & 0xFFFF == 0 and time.perf_counter() - t0 > limite_s:
                raise LimiteDeTiempo
            return
        for v in range(1, n):
            if not usados[v]:
                usados[v] = True
                actual.append(v)
                permutar(v, costo + D[ultimo][v], nivel + 1)
                actual.pop()
                usados[v] = False

    permutar(0, 0.0, 1)
    return mejor[0], mejor[1]


# ---------------------------------------------------------------------------
# 2. Held-Karp (programación dinámica sobre subconjuntos).
#    C(S, j) = costo mínimo de salir de 0, visitar exactamente los lugares
#              de S (S ⊆ {1..k}, j ∈ S) y terminar en j.
#    C({j}, j) = D[0][j]
#    C(S, j)   = min_{i ∈ S\{j}} C(S\{j}, i) + D[i][j]
#    Óptimo    = min_{j} C({1..k}, j) + D[j][0]
#    Tiempo O(k^2 * 2^k), memoria O(k * 2^k).
# ---------------------------------------------------------------------------
def tsp_held_karp(D):
    n = len(D)
    k = n - 1
    if k == 0:
        return 0.0, [0, 0]
    INF = math.inf
    total_mascaras = 1 << k
    # Lugar j (1..k) <-> bit (j-1)
    C = [[INF] * k for _ in range(total_mascaras)]
    P = [[-1] * k for _ in range(total_mascaras)]   # predecesor para reconstruir
    for j in range(k):
        C[1 << j][j] = D[0][j + 1]

    for S in range(1, total_mascaras):
        fila = C[S]
        for j in range(k):
            bj = 1 << j
            if not (S & bj) or S == bj:
                continue
            S_sin_j = S ^ bj
            previa = C[S_sin_j]
            mejor, arg = INF, -1
            col_j = j + 1
            for i in range(k):
                if S_sin_j & (1 << i):
                    c = previa[i] + D[i + 1][col_j]
                    if c < mejor:
                        mejor, arg = c, i
            fila[j] = mejor
            P[S][j] = arg

    completo = total_mascaras - 1
    mejor, ultimo = INF, -1
    for j in range(k):
        c = C[completo][j] + D[j + 1][0]
        if c < mejor:
            mejor, ultimo = c, j

    # Reconstrucción del recorrido siguiendo los predecesores
    ruta = []
    S, j = completo, ultimo
    while j != -1:
        ruta.append(j + 1)
        S, j = S ^ (1 << j), P[S][j]
    ruta.reverse()
    return mejor, [0] + ruta + [0]


def memoria_teorica_held_karp(k, bytes_por_celda=8):
    """Bytes de las tablas C y P si cada celda ocupa `bytes_por_celda` (float64 / int64)."""
    return 2 * (2 ** k) * k * bytes_por_celda


# ---------------------------------------------------------------------------
# 3. Heurística voraz: vecino más cercano.
#    Desde el lugar actual se va al lugar no visitado con menor D[actual][v]
#    (respetando el sentido, por ser asimétrico). Tiempo O(k^2), memoria O(k).
# ---------------------------------------------------------------------------
def tsp_vecino_mas_cercano(D):
    n = len(D)
    visitado = [False] * n
    visitado[0] = True
    ruta, actual, costo = [0], 0, 0.0
    for _ in range(n - 1):
        mejor, sig = math.inf, -1
        for v in range(1, n):
            if not visitado[v] and D[actual][v] < mejor:
                mejor, sig = D[actual][v], v
        visitado[sig] = True
        ruta.append(sig)
        costo += mejor
        actual = sig
    costo += D[actual][0]
    ruta.append(0)
    return costo, ruta


def costo_recorrido(D, ruta):
    return sum(D[ruta[i]][ruta[i + 1]] for i in range(len(ruta) - 1))
