"""
Requerimiento 2 - Caminos mínimos sobre la componente fuertemente conexa (peso: travel_time, s).

Entrada : req1/red_vial_quindio_filtered.graphml, req1/catalogo_lugares_nodos.csv
Salidas : req2/resultados/req2_mediciones.csv       (una fila por par: tiempos y nodos explorados)
          req2/resultados/req2_cociente.json        (mediana/mín/máx de lineal/heap + máquina)
          req2/resultados/req2_tiempo_vs_explorados.png
          req2/resultados/req2_matriz.json          (resumen de la matriz)
          req2/matriz_tiempos.csv                   (matriz 40x40 en s; la usan req4 y la app)

Uso:
  py req2/req2.py            -> verificación + mediciones + gráfica + matriz
  py req2/req2.py medir      -> solo verificación + mediciones + gráfica
  py req2/req2.py matriz     -> solo la matriz de tiempos (rápido)

Protocolo (sección 6): solo se mide el algoritmo (la carga del grafo y la lista de
adyacencia quedan por fuera), 5 repeticiones y mediana, tiempos en ms, y cada
algoritmo se verifica antes de medir.
"""
import json
import math
import random
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))
sys.path.append(str(RAIZ / "req2"))
from auxiliar_functions import (generar_tabla_desde_csv, guardar_resultados_csv, info_maquina,
                                medir_tiempo_ejecucion)
from dijkstra_heap import construir_lista_adyacencia, costo_ruta, dijkstra_heap, matriz_tiempos
from dijkstra_lineal import dijkstra_lineal

RUTA_GRAFO = RAIZ / "req1" / "red_vial_quindio_filtered.graphml"
RUTA_CATALOGO = RAIZ / "req1" / "catalogo_lugares_nodos.csv"
RUTA_MATRIZ = RAIZ / "req2" / "matriz_tiempos.csv"
DIR_RES = RAIZ / "req2" / "resultados"
DIR_RES.mkdir(parents=True, exist_ok=True)

# Pares (id origen, id destino) del catálogo.
# 10 cercanos (mismo municipio o municipios vecinos): se miden con ambas versiones.
PARES_CERCANOS = [
    (3, 37),   # Calarcá -> Central de Beneficio (Calarcá)
    (6, 38),   # Filandia -> Cooperativa (Filandia)
    (7, 39),   # Génova -> Punto de acopio (Génova)
    (11, 40),  # Quimbaya -> Trilladora (Quimbaya)
    (12, 22),  # Salento -> Mirador Alto de la Cruz (Salento)
    (1, 36),   # Armenia -> Trilladora Armenia
    (1, 21),   # Armenia -> Parque de la Vida (Armenia)
    (9, 13),   # Montenegro -> Parque Nacional del Café (Montenegro)
    (1, 3),    # Armenia -> Calarcá (vecinos)
    (1, 4),    # Armenia -> Circasia (vecinos)
]
# 10 más, entre municipios lejanos: solo la versión con cola de prioridad.
PARES_LEJANOS = [
    (1, 15),   # Armenia -> Valle de Cocora
    (1, 14),   # Armenia -> PANACA
    (1, 7),    # Armenia -> Génova
    (7, 6),    # Génova -> Filandia
    (14, 24),  # PANACA -> Cascadas Río Verde
    (2, 12),   # Buenavista -> Salento
    (8, 32),   # La Tebaida -> Hotel Sazagua
    (26, 15),  # Valle de Maravélez -> Valle de Cocora
    (39, 38),  # Acopio Génova -> Coop. Filandia
    (30, 10),  # Finca Bosque de Samán -> Pijao
]
TOL = 1e-6


def cargar():
    G = ox.load_graphml(RUTA_GRAFO)          # ox convierte travel_time a float (nx.read_graphml no)
    adj = construir_lista_adyacencia(G)
    cat = pd.read_csv(RUTA_CATALOGO).set_index("id")
    return G, adj, cat


# ---------------------------------------------------------------------------
def verificar(G, adj, cat):
    """Protocolo 6.6: verificar antes de medir."""
    print("\n=== Verificación ===")
    # 1) Caso pequeño resuelto a mano. Camino óptimo a->d: a-b-c-d = 1+2+1 = 4
    #    (a->d directo cuesta 10; a->c directo cuesta 5). Es dirigido: d->a no existe.
    mini = {"a": [("b", 1.0), ("c", 5.0), ("d", 10.0)], "b": [("c", 2.0)],
            "c": [("d", 1.0)], "d": [], "e": [("a", 1.0)]}
    for f in (dijkstra_heap, dijkstra_lineal):
        assert f(mini, "a", "d")[:2] == (4.0, ["a", "b", "c", "d"]), f.__name__
        assert f(mini, "d", "a")[:2] == (math.inf, []), f.__name__
        dist, _, _ = f(mini, "a")
        assert dist == {"a": 0, "b": 1, "c": 3, "d": 4}, (f.__name__, dist)
    print(" [OK] Caso a mano (5 nodos): ambas versiones dan a->d = 4 por a-b-c-d")

    # 2) Pares del experimento: heap contra NetworkX y contra la versión lineal.
    for o, d in PARES_CERCANOS + PARES_LEJANOS:
        s, t = int(cat.loc[o, "nodo_osm"]), int(cat.loc[d, "nodo_osm"])
        th, rh, _ = dijkstra_heap(adj, s, t)
        ref = nx.shortest_path_length(G, s, t, weight="travel_time")
        assert abs(th - ref) < TOL, (o, d, th, ref)
        assert rh[0] == s and rh[-1] == t and abs(costo_ruta(adj, rh) - th) < TOL, (o, d)
        if (o, d) in PARES_CERCANOS:
            tl, rl, _ = dijkstra_lineal(adj, s, t)
            assert abs(tl - th) < TOL, f"Lineal != heap en {o}->{d}: {tl} vs {th}"
            assert abs(costo_ruta(adj, rl) - tl) < TOL, (o, d)
    print(f" [OK] {len(PARES_CERCANOS) + len(PARES_LEJANOS)} pares: heap = NetworkX y el costo de la ruta "
          f"devuelta = tiempo devuelto")
    print(f" [OK] {len(PARES_CERCANOS)} pares cercanos: lineal = heap (mismo tiempo de viaje)")


# ---------------------------------------------------------------------------
def medir(adj, cat):
    print("\n=== Mediciones (ms, mediana de 5) ===")
    filas = []
    for n, (o, d) in enumerate(PARES_CERCANOS + PARES_LEJANOS, start=1):
        s, t = int(cat.loc[o, "nodo_osm"]), int(cat.loc[d, "nodo_osm"])
        cercano = (o, d) in PARES_CERCANOS
        print(f" Par {n}: {cat.loc[o, 'nombre']} -> {cat.loc[d, 'nombre']}")
        (tv, ruta, exp_h), ms_h, _ = medir_tiempo_ejecucion(dijkstra_heap, adj, s, t, unidad_tiempo="ms")
        fila = {"par": n, "tipo": "cercano" if cercano else "lejano",
                "origen_id": o, "destino_id": d,
                "origen": cat.loc[o, "nombre"], "destino": cat.loc[d, "nombre"],
                "municipio_origen": cat.loc[o, "municipio"], "municipio_destino": cat.loc[d, "municipio"],
                "tiempo_viaje_s": round(tv, 3), "tiempo_viaje_min": round(tv / 60, 2),
                "nodos_ruta": len(ruta),
                "heap_ms": ms_h, "heap_explorados": exp_h,
                "lineal_ms": None, "lineal_explorados": None, "cociente_lineal_heap": None}
        if cercano:
            (tl, _, exp_l), ms_l, _ = medir_tiempo_ejecucion(dijkstra_lineal, adj, s, t, unidad_tiempo="ms")
            assert abs(tl - tv) < TOL
            fila.update(lineal_ms=ms_l, lineal_explorados=exp_l,
                        cociente_lineal_heap=round(ms_l / ms_h, 2))
        filas.append(fila)
    ruta_csv = DIR_RES / "req2_mediciones.csv"
    guardar_resultados_csv(filas, str(ruta_csv))
    return pd.read_csv(ruta_csv)


def resumen_cociente(df, V, E):
    c = df["cociente_lineal_heap"].dropna()
    res = {"pares_con_ambas": int(c.size),
           "cociente_mediana": round(float(c.median()), 2),
           "cociente_min": round(float(c.min()), 2),
           "cociente_max": round(float(c.max()), 2),
           "unidad_tiempo": "ms (mediana de 5 ejecuciones)",
           "grafo": {"V": V, "E_lista_adyacencia": E},
           "maquina": info_maquina()}
    with open(DIR_RES / "req2_cociente.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"\nCociente lineal/heap en {res['pares_con_ambas']} pares: mediana {res['cociente_mediana']}x, "
          f"mín {res['cociente_min']}x, máx {res['cociente_max']}x")
    return res


def grafica(df, V):
    fig, ax = plt.subplots(figsize=(8.5, 5))
    lin = df.dropna(subset=["lineal_ms"])
    ax.scatter(df["heap_explorados"], df["heap_ms"], c="#2c7fb8", s=40,
               label="Cola de prioridad  O((V+E) log V)  (20 pares)")
    ax.scatter(lin["lineal_explorados"], lin["lineal_ms"], c="#e6550d", marker="s", s=40,
               label="Recorrido lineal  O(V²)  (10 pares cercanos)")
    # Une los dos puntos de cada par medido con ambas versiones
    for _, r in lin.iterrows():
        ax.plot([r["heap_explorados"], r["lineal_explorados"]], [r["heap_ms"], r["lineal_ms"]],
                c="gray", lw=0.6, ls=":")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Nodos explorados (escala log)")
    ax.set_ylabel("Tiempo (ms, mediana de 5; escala log)")
    ax.set_title(f"Dijkstra: tiempo frente a nodos explorados (V = {V})")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(DIR_RES / "req2_tiempo_vs_explorados.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
def calcular_matriz(G, adj, cat):
    print("\n=== Matriz de tiempos (Dijkstra con heap, sin destino, una vez por lugar) ===")
    ids = list(cat.index)
    nodos = [int(x) for x in cat["nodo_osm"]]
    t0 = time.perf_counter()
    M = matriz_tiempos(adj, nodos)
    ms = (time.perf_counter() - t0) * 1000

    # Verificación de 30 celdas al azar contra NetworkX (semilla 42)
    rnd = random.Random(42)
    for _ in range(30):
        i, j = rnd.randrange(len(ids)), rnd.randrange(len(ids))
        ref = nx.shortest_path_length(G, nodos[i], nodos[j], weight="travel_time")
        assert abs(ref - M[i][j]) < TOL, (ids[i], ids[j], ref, M[i][j])
    assert all(math.isfinite(x) for fila in M for x in fila), "Hay lugares inalcanzables"
    print(" [OK] 30 celdas al azar (semilla 42) coinciden con NetworkX; todas finitas (componente fuerte)")

    df = pd.DataFrame(M, index=ids, columns=ids)
    df.index.name = "id_origen"
    df.round(3).to_csv(RUTA_MATRIZ)

    n = len(ids)
    difs = [(abs(M[i][j] - M[j][i]), ids[i], ids[j]) for i in range(n) for j in range(i + 1, n)]
    asim = sum(1 for d, _, _ in difs if d > 1)
    dmax, a, b = max(difs)
    res = {"tamano": f"{n}x{n}", "unidad": "s", "tiempo_calculo_ms": round(ms, 1),
           "ejecuciones_dijkstra": n, "pares_asimetricos_mas_de_1s": asim, "pares_totales": len(difs),
           "mayor_asimetria": {"de": cat.loc[a, "nombre"], "a": cat.loc[b, "nombre"],
                               "ida_s": round(df.loc[a, b], 1), "vuelta_s": round(df.loc[b, a], 1),
                               "diferencia_s": round(dmax, 1)}}
    with open(DIR_RES / "req2_matriz.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f" Matriz {n}x{n} guardada en {RUTA_MATRIZ} ({ms:.0f} ms, 1 medición). "
          f"Pares asimétricos (>1 s): {asim}/{len(difs)}")
    return res


if __name__ == "__main__":
    pasos = sys.argv[1:] or ["medir", "matriz"]
    G, adj, cat = cargar()
    V, E = len(adj), sum(len(v) for v in adj.values())
    print(f"Componente: V = {V}, E = {G.number_of_edges()} (lista de adyacencia sin paralelas: {E})")
    if "medir" in pasos:
        verificar(G, adj, cat)
        df = medir(adj, cat)
        resumen_cociente(df, V, E)
        grafica(df, V)
        generar_tabla_desde_csv(str(DIR_RES / "req2_mediciones.csv"),
                                "Dijkstra: tiempo y nodos explorados por par", "milisegundos (ms)")
    if "matriz" in pasos:
        calcular_matriz(G, adj, cat)
