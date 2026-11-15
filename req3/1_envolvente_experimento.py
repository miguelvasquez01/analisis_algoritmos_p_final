"""
Requerimiento 3 - Envolvente convexa de la red vial.

1. Carga los nodos de la componente (ya proyectada a UTM 18N en req1),
   redondea a enteros y elimina repetidos.
2. Verifica QuickHull (propio) contra scipy.spatial.ConvexHull en casos
   pequeños hechos a mano, en la red y en los conjuntos aleatorios.
3. Mide ambos (5 repeticiones, mediana, ms) con la red y con 1 000, 10 000
   y 50 000 puntos al azar en un cuadrado (semilla 42).
4. Guarda resultados (CSV/JSON) y genera la figura de la envolvente y la tabla.
"""
import json
import random
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import osmnx as ox
from scipy.spatial import ConvexHull

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))
sys.path.append(str(RAIZ / "req3"))
from auxiliar_functions import medir_tiempo_ejecucion, guardar_resultados_csv, generar_tabla_desde_csv
from quickhull import quickhull

SEMILLA = 42
LADO_CUADRADO = 100_000          # puntos aleatorios en [0, 100000]^2 (enteros)
TAMANOS = [1_000, 10_000, 50_000]
DIR_RES = RAIZ / "req3" / "resultados"
DIR_RES.mkdir(parents=True, exist_ok=True)


def puntos_red():
    G = ox.load_graphml(RAIZ / "req1" / "red_vial_quindio_utm18n.graphml")
    pts = {(int(round(d["x"])), int(round(d["y"]))) for _, d in G.nodes(data=True)}
    return len(G.nodes), sorted(pts)


def puntos_aleatorios(n, semilla=SEMILLA):
    rng = random.Random(semilla)
    pts = set()
    while len(pts) < n:
        pts.add((rng.randint(0, LADO_CUADRADO), rng.randint(0, LADO_CUADRADO)))
    return sorted(pts)


def scipy_hull(arr):
    return ConvexHull(arr)


def vertices_scipy(arr, hull):
    return {tuple(int(v) for v in arr[i]) for i in hull.vertices}


def area_poligono(v):
    s = 0
    for i in range(len(v)):
        x1, y1 = v[i]
        x2, y2 = v[(i + 1) % len(v)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def verificar(pts, nombre):
    propio = quickhull(pts)
    arr = np.array(pts, dtype=np.int64)
    ref = vertices_scipy(arr, ConvexHull(arr))
    ok = set(propio) == ref and len(propio) == len(ref)
    print(f"   Verificación {nombre}: {'OK' if ok else 'FALLA'} ({len(propio)} vértices)")
    assert ok
    return propio


def pruebas_a_mano():
    print("=== Casos pequeños resueltos a mano ===")
    casos = {
        "cuadrado + interior": ([(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (1, 3)],
                                {(0, 0), (4, 0), (4, 4), (0, 4)}),
        "colineales en lados": ([(0, 0), (2, 0), (4, 0), (4, 2), (4, 4), (2, 4), (0, 4), (0, 2), (2, 2)],
                                {(0, 0), (4, 0), (4, 4), (0, 4)}),
        "triángulo": ([(0, 0), (10, 0), (5, 8), (5, 3), (6, 1)],
                      {(0, 0), (10, 0), (5, 8)}),
        "empate en x mínima": ([(0, 0), (0, 5), (0, 3), (10, 2), (5, 2)],
                               {(0, 0), (0, 5), (10, 2)}),
    }
    for nombre, (pts, esperado) in casos.items():
        r = quickhull(pts)
        assert set(r) == esperado and len(r) == len(esperado), (nombre, r)
        print(f"   {nombre}: OK -> {r}")


def main():
    pruebas_a_mano()

    V, pts_red = puntos_red()
    print(f"\nRed: {V} nodos -> {len(pts_red)} puntos enteros distintos")

    conjuntos = [("Red vial Quindío (nodos SCC)", pts_red)]
    conjuntos += [(f"Aleatorios n={n}", puntos_aleatorios(n)) for n in TAMANOS]

    filas = []
    hull_red = None
    for nombre, pts in conjuntos:
        print(f"\n=== {nombre} ({len(pts)} puntos) ===")
        propio = verificar(pts, nombre)
        if hull_red is None:
            hull_red = propio
        arr = np.array(pts, dtype=np.int64)
        print("  QuickHull propio (Python):")
        _, t_propio, _ = medir_tiempo_ejecucion(quickhull, pts, unidad_tiempo="ms")
        print("  SciPy ConvexHull (Qhull, C):")
        _, t_scipy, _ = medir_tiempo_ejecucion(scipy_hull, arr, unidad_tiempo="ms")
        filas.append({
            "Conjunto": nombre,
            "Puntos (n)": len(pts),
            "Vértices (h)": len(propio),
            "QuickHull propio (ms)": t_propio,
            "SciPy ConvexHull (ms)": t_scipy,
            "Cociente propio/SciPy": round(t_propio / t_scipy, 1),
            "Mismos vértices": "Sí",
        })

    ruta_csv = DIR_RES / "req3_tiempos_envolvente.csv"
    guardar_resultados_csv(filas, str(ruta_csv))
    generar_tabla_desde_csv(str(ruta_csv), "Envolvente convexa: QuickHull propio vs SciPy",
                            "milisegundos (ms), mediana de 5 corridas")

    area_km2 = area_poligono(hull_red) / 1e6
    with open(DIR_RES / "req3_envolvente_red.json", "w", encoding="utf-8") as f:
        json.dump({"crs": "EPSG:32618", "semilla_aleatorios": SEMILLA,
                   "n_puntos": len(pts_red), "n_vertices": len(hull_red),
                   "area_km2": round(area_km2, 2),
                   "vertices_antihorario": hull_red}, f, indent=1)
    print(f"Área de la envolvente de la red: {area_km2:.1f} km²")

    # Figura 1: envolvente sobre los nodos
    fig, ax = plt.subplots(figsize=(7, 9))
    xs, ys = zip(*pts_red)
    ax.scatter(xs, ys, s=0.6, c="#5a6b7b", alpha=0.6, label=f"Nodos ({len(pts_red)})")
    hx, hy = zip(*(hull_red + [hull_red[0]]))
    ax.plot(hx, hy, "-", c="#c0392b", lw=1.8, label=f"Envolvente ({len(hull_red)} vértices)")
    ax.scatter(hx, hy, s=18, c="#c0392b", zorder=3)
    ax.set_title(f"Envolvente convexa de la red vial del Quindío\nÁrea ≈ {area_km2:,.0f} km²")
    ax.set_xlabel("Este UTM 18N (m)")
    ax.set_ylabel("Norte UTM 18N (m)")
    ax.set_aspect("equal")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(DIR_RES / "req3_envolvente_red.png", dpi=150)

    # Figura 2: tiempos (escala log)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    etiquetas = [f"{r['Conjunto'].replace('Red vial Quindío (nodos SCC)', 'Red vial')}\n(n={r['Puntos (n)']})" for r in filas]
    x = np.arange(len(filas))
    ax.bar(x - 0.2, [r["QuickHull propio (ms)"] for r in filas], 0.4, label="QuickHull propio (Python)", color="#2c7fb8")
    ax.bar(x + 0.2, [r["SciPy ConvexHull (ms)"] for r in filas], 0.4, label="SciPy ConvexHull (Qhull, C)", color="#e6550d")
    ax.set_xticks(x, etiquetas, fontsize=8)
    ax.set_yscale("log")
    ax.set_ylabel("Tiempo, mediana de 5 corridas (ms, escala log)")
    ax.set_title("Envolvente convexa: implementación propia vs SciPy")
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIR_RES / "req3_tiempos.png", dpi=150)
    print("Figuras guardadas en", DIR_RES)


if __name__ == "__main__":
    main()
