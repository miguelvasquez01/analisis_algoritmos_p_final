"""
Envolvente convexa por QuickHull (divide y vencerás) - implementación propia.

Entrada: lista de puntos (x, y) con coordenadas ENTERAS y sin repetidos.
Salida : vértices de la envolvente en sentido antihorario, sin puntos
         colineales sobre los lados (solo se aceptan giros estrictos).

Idea (Barber, Dobkin & Huhdanpaa, 1996; Preparata & Shamos, 1985):
  1. A = punto más a la izquierda, B = más a la derecha: ambos son vértices.
  2. La recta AB parte el conjunto en dos (arriba / abajo).
  3. En cada lado se toma el punto C más lejano a la recta (vértice seguro),
     se descartan los puntos dentro del triángulo A-C-B y se recurre sobre
     los segmentos A-C y C-B.

Recurrencia: T(n) = T(n1) + T(n2) + O(n), con n1 + n2 <= n.
  - Particiones balanceadas: T(n) = 2T(n/2) + O(n)  ->  O(n log n)
  - Peor caso (partición 1 / n-1): T(n) = T(n-1) + O(n) -> O(n^2)
Memoria: O(n) para las listas de cada nivel + pila de recursión O(h)
(h = número de vértices de la envolvente).
"""
import sys

sys.setrecursionlimit(100_000)


def cruz(o, a, b):
    """Producto cruz (a - o) x (b - o). >0 giro antihorario, <0 horario, 0 colineal.
    Con enteros de Python no hay desbordamiento (precisión arbitraria)."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _hull_lado(puntos, a, b, salida):
    """Agrega a `salida` los vértices estrictamente a la izquierda de a->b,
    en orden desde a hasta b (sin incluir a ni b)."""
    if not puntos:
        return
    # Punto más lejano a la recta ab (máximo |cruz|, todos con cruz > 0)
    c = max(puntos, key=lambda p: cruz(a, b, p))
    # Puntos fuera del triángulo a-c-b: a la izquierda de a->c o de c->b.
    izq_ac = [p for p in puntos if cruz(a, c, p) > 0]
    izq_cb = [p for p in puntos if cruz(c, b, p) > 0]
    _hull_lado(izq_ac, a, c, salida)
    salida.append(c)
    _hull_lado(izq_cb, c, b, salida)


def quickhull(puntos):
    """Retorna la lista de vértices de la envolvente (antihorario)."""
    n = len(puntos)
    if n < 3:
        return list(puntos)
    a = min(puntos)                      # menor x (y menor y en empate)
    b = max(puntos)                      # mayor x (y mayor y en empate)
    arriba = [p for p in puntos if cruz(a, b, p) > 0]
    abajo = [p for p in puntos if cruz(b, a, p) > 0]
    # Recorrido horario: los puntos externos quedan a la izquierda de cada lado.
    salida = [a]
    _hull_lado(arriba, a, b, salida)     # cadena superior a -> b
    salida.append(b)
    _hull_lado(abajo, b, a, salida)      # cadena inferior b -> a
    salida.reverse()                     # pasar a sentido antihorario
    return salida
