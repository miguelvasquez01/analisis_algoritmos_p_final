"""
Requerimiento 4 - Experimentos del viajante asimétrico sobre la matriz de tiempos.

Entrada : req2/matriz_tiempos.csv (generada por req2/dijkstra_heap.py)
Salidas : req4/resultados/*.csv, *.json, *.png

Semillas documentadas:
  - Punto 1 (tiempo vs k):      random.Random(42 + k)
  - Punto 3 (calidad voraz):    random.Random(1000 + 100*k + instancia)
"""
import json
import random
import sys
import time
import tracemalloc
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))
sys.path.append(str(RAIZ / "req4"))
from auxiliar_functions import medir_tiempo_ejecucion, guardar_resultados_csv, generar_tabla_desde_csv
from itinerario import recortar_itinerario, resolver, tabla_itinerario
from tsp import (LimiteDeTiempo, costo_recorrido, memoria_teorica_held_karp,
                 tsp_fuerza_bruta, tsp_held_karp, tsp_vecino_mas_cercano)

DIR_RES = RAIZ / "req4" / "resultados"
DIR_RES.mkdir(parents=True, exist_ok=True)
LIMITE_S = 300.0                  # 5 minutos (protocolo, sección 6)
K_EXACTOS = range(5, 13)          # 5..12 (pedido)
K_HK_EXTRA = range(13, 17)        # extra: solo Held-Karp, para ver la curva
K_CALIDAD = [5, 8, 10, 12]
INSTANCIAS_CALIDAD = 10

M = pd.read_csv(RAIZ / "req2" / "matriz_tiempos.csv", index_col=0)
CAT = pd.read_csv(RAIZ / "req1" / "catalogo_lugares_nodos.csv").set_index("id")
IDS = [int(c) for c in M.columns]                 # ids del catálogo, en orden
MAT = M.values.tolist()                            # segundos
ID_ARMENIA = 1


def submatriz(ids_ruta):
    """ids_ruta[0] es la partida. Devuelve la matriz (en s) restringida a esos lugares."""
    pos = [IDS.index(i) for i in ids_ruta]
    return [[MAT[a][b] for b in pos] for a in pos]


def instancia(k, semilla):
    candidatos = [i for i in IDS if i != ID_ARMENIA]
    return [ID_ARMENIA] + random.Random(semilla).sample(candidatos, k)


def nombres(ids_ruta, ruta_local):
    return [CAT.loc[ids_ruta[i], "nombre"] for i in ruta_local]


# ---------------------------------------------------------------------------
def punto1_tiempo_vs_k():
    print("\n=== PUNTO 1: fuerza bruta y Held-Karp, tiempo vs k ===")
    filas = []
    fb_activa = True
    for k in list(K_EXACTOS) + list(K_HK_EXTRA):
        ids = instancia(k, 42 + k)
        D = submatriz(ids)
        fila = {"k": k, "lugares": " ".join(map(str, ids[1:]))}

        # Fuerza bruta (solo k <= 12 y mientras no haya pasado el límite)
        if k in K_EXACTOS and fb_activa:
            print(f" k={k} fuerza bruta:")
            t0 = time.perf_counter()
            try:
                (c_fb, r_fb) = tsp_fuerza_bruta(D, LIMITE_S)
                t1 = (time.perf_counter() - t0) * 1000
                if t1 / 1000 > 60:
                    print(f"   [!] > 60 s: 1 sola medición ({t1:.1f} ms)")
                    t_fb = round(t1, 5)
                else:
                    _, t_fb, _ = medir_tiempo_ejecucion(tsp_fuerza_bruta, D, LIMITE_S, unidad_tiempo="ms")
                fila.update(fb_ms=t_fb, fb_costo_s=round(c_fb, 3), fb_estado="completada")
            except LimiteDeTiempo:
                print(f"   [X] superó {LIMITE_S:.0f} s: NO COMPLETADA")
                fila.update(fb_ms=None, fb_costo_s=None, fb_estado=f"no completada (> {LIMITE_S:.0f} s)")
                fb_activa = False
                c_fb = None
        else:
            fila.update(fb_ms=None, fb_costo_s=None,
                        fb_estado="no ejecutada" if k in K_EXACTOS else "fuera del rango pedido")
            c_fb = None

        print(f" k={k} Held-Karp:")
        (c_hk, r_hk), t_hk, _ = medir_tiempo_ejecucion(tsp_held_karp, D, unidad_tiempo="ms")
        tracemalloc.start()
        tsp_held_karp(D)
        _, pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert abs(costo_recorrido(D, r_hk) - c_hk) < 1e-6
        coinciden = None
        if c_fb is not None:
            coinciden = abs(c_fb - c_hk) < 1e-6
            assert coinciden, f"k={k}: FB {c_fb} != HK {c_hk}"
        fila.update(hk_ms=t_hk, hk_costo_s=round(c_hk, 3), hk_costo_min=round(c_hk / 60, 2),
                    fb_igual_hk="Sí" if coinciden else ("-" if coinciden is None else "No"),
                    hk_celdas_tabla=2 * (2 ** k) * k,
                    hk_mem_teorica_KB=round(memoria_teorica_held_karp(k) / 1024, 1),
                    hk_mem_pico_python_KB=round(pico / 1024, 1),
                    hk_recorrido=" -> ".join(str(ids[i]) for i in r_hk))
        filas.append(fila)
    ruta = DIR_RES / "req4_tiempo_vs_k.csv"
    guardar_resultados_csv(filas, str(ruta))
    return pd.read_csv(ruta)


def grafica_tiempo_vs_k(df):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    fb = df.dropna(subset=["fb_ms"])
    ax.plot(fb["k"], fb["fb_ms"], "o-", c="#e6550d", label="Fuerza bruta  O(k·k!)")
    pedido = df[df["k"] <= 12]
    extra = df[df["k"] >= 12]
    ax.plot(pedido["k"], pedido["hk_ms"], "s-", c="#2c7fb8", label="Held-Karp  O(k²·2ᵏ)")
    ax.plot(extra["k"], extra["hk_ms"], "s--", c="#2c7fb8", alpha=0.5, label="Held-Karp (k > 12, extra)")
    no_comp = df[df["fb_estado"].astype(str).str.startswith("no completada")]
    for _, r in no_comp.iterrows():
        ax.axvline(r["k"], color="#e6550d", ls=":", lw=1)
        ax.annotate("FB > 5 min\n(no completada)", (r["k"], LIMITE_S * 1000 * 0.6), color="#e6550d",
                    fontsize=8, ha="center", va="top")
    ax.axhline(LIMITE_S * 1000, color="gray", ls="--", lw=0.8)
    ax.set_yscale("log")
    ax.set_xlabel("k (lugares a visitar además de Armenia)")
    ax.set_ylabel("Tiempo (ms, mediana de 5; escala log)")
    ax.set_title("ATSP exacto: tiempo de ejecución frente a k")
    ax.set_xticks(list(df["k"]))
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(DIR_RES / "req4_tiempo_vs_k.png", dpi=150)


# ---------------------------------------------------------------------------
def punto3_calidad():
    print("\n=== PUNTO 3: calidad del vecino más cercano vs Held-Karp ===")
    filas = []
    for k in K_CALIDAD:
        for inst in range(INSTANCIAS_CALIDAD):
            ids = instancia(k, 1000 + 100 * k + inst)
            D = submatriz(ids)
            c_opt, r_opt = tsp_held_karp(D)
            c_nn, r_nn = tsp_vecino_mas_cercano(D)
            filas.append({"k": k, "instancia": inst, "lugares": " ".join(map(str, ids[1:])),
                          "optimo_min": round(c_opt / 60, 2), "voraz_min": round(c_nn / 60, 2),
                          "desviacion_pct": round(100 * (c_nn - c_opt) / c_opt, 2),
                          "voraz_es_optimo": "Sí" if abs(c_nn - c_opt) < 1e-6 else "No"})
    det = pd.DataFrame(filas)
    guardar_resultados_csv(det, str(DIR_RES / "req4_calidad_detalle.csv"))
    res = det.groupby("k").agg(instancias=("instancia", "count"),
                               desviacion_promedio_pct=("desviacion_pct", "mean"),
                               desviacion_maxima_pct=("desviacion_pct", "max"),
                               desviacion_minima_pct=("desviacion_pct", "min"),
                               veces_optimo=("voraz_es_optimo", lambda s: (s == "Sí").sum())).reset_index()
    res = res.round(2)
    ruta = DIR_RES / "req4_calidad_resumen.csv"
    guardar_resultados_csv(res, str(ruta))
    generar_tabla_desde_csv(str(ruta), "Desviación del vecino más cercano respecto al óptimo", "N/A (%)")

    fig, ax = plt.subplots(figsize=(7, 4.2))
    for k in K_CALIDAD:
        y = det[det.k == k]["desviacion_pct"]
        ax.scatter([k] * len(y), y, c="#2c7fb8", alpha=0.5, s=22)
    ax.plot(res["k"], res["desviacion_promedio_pct"], "o-", c="#c0392b", label="Promedio")
    ax.plot(res["k"], res["desviacion_maxima_pct"], "^--", c="#e6550d", label="Máximo")
    ax.set_xticks(K_CALIDAD)
    ax.set_xlabel("k")
    ax.set_ylabel("Desviación sobre el óptimo (%)")
    ax.set_title(f"Vecino más cercano vs Held-Karp ({INSTANCIAS_CALIDAD} instancias por k)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(DIR_RES / "req4_calidad_voraz.png", dpi=150)
    return res


# ---------------------------------------------------------------------------
def punto4_itinerario(partida=ID_ARMENIA, atractivos=(13, 15, 16, 17, 18, 21, 22, 25), jornada_min=660):
    """Ordena con Held-Karp; si no cabe en la jornada, quita en cada paso el atractivo
    cuya eliminación más reduce la duración total (visita + desvío) y recalcula.
    La lógica está en req4/itinerario.py (la reutiliza la aplicación)."""
    print("\n=== PUNTO 4: itinerario de un día ===")
    tiempos = {a: {b: MAT[i][j] for j, b in enumerate(IDS)} for i, a in enumerate(IDS)}
    duracion = CAT["duracion_visita_min"].to_dict()
    pasos_it, actuales = recortar_itinerario(partida, atractivos, tiempos, duracion, jornada_min)
    pasos = []
    for n, p in enumerate(pasos_it):
        print(f"  {len(p['atractivos'])} atractivos: viaje {p['viaje_min']:.1f} + visitas {p['visitas_min']}"
              f" = {p['total_min']:.1f} min")
        quitado = ""
        if p["quitado"] is not None:
            quitado = f"{p['quitado']} ({CAT.loc[p['quitado'], 'nombre']}) libera {p['libera_min']:.1f} min"
        pasos.append({"paso": n, "atractivos": len(p["atractivos"]),
                      "orden": " -> ".join(str(i) for i in p["recorrido"]),
                      "orden_nombres": " -> ".join(CAT.loc[i, "nombre"] for i in p["recorrido"]),
                      "viaje_min": round(p["viaje_min"], 1), "visitas_min": int(p["visitas_min"]),
                      "total_min": round(p["total_min"], 1), "total_h": round(p["total_min"] / 60, 2),
                      "cabe_en_11h": "Sí" if p["cabe"] else "No", "quitado": quitado})

    # Comparación con la voraz para el itinerario final
    ids = [partida] + actuales
    c_hk, r_hk = resolver(ids, tiempos, "held_karp")
    c_nn, r_nn = resolver(ids, tiempos, "voraz")
    final = {"partida": partida, "atractivos_iniciales": list(atractivos), "atractivos_finales": actuales,
             "held_karp": {"orden": [CAT.loc[i, "nombre"] for i in r_hk], "viaje_min": round(c_hk / 60, 1)},
             "voraz": {"orden": [CAT.loc[i, "nombre"] for i in r_nn], "viaje_min": round(c_nn / 60, 1)},
             "visitas_min": int(sum(CAT.loc[i, "duracion_visita_min"] for i in actuales)),
             "jornada_min": jornada_min}
    guardar_resultados_csv(pasos, str(DIR_RES / "req4_itinerario_pasos.csv"))
    with open(DIR_RES / "req4_itinerario_final.json", "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=1)

    # Tabla con el formato del anexo (una fila por parada + regreso)
    tabla = [{"orden": f["orden"], "lugar": CAT.loc[f["id"], "nombre"],
              "desplazamiento_desde_anterior_min": round(f["desplazamiento_min"], 1),
              "visita_min": "" if f["visita_min"] is None else int(f["visita_min"]),
              "tiempo_acumulado_h": round(f["acumulado_h"], 2)}
             for f in tabla_itinerario(r_hk, tiempos, duracion)]
    guardar_resultados_csv(tabla, str(DIR_RES / "req4_itinerario_tabla.csv"))
    return pasos, final


# ---------------------------------------------------------------------------
def punto5_contraejemplo():
    """Busca la instancia real más pequeña (k mínimo) en la que el vecino más
    cercano no es óptimo, para explicarla paso a paso."""
    print("\n=== PUNTO 5: contraejemplo voraz vs óptimo ===")
    for k in range(3, 8):
        mejores = []
        for s in range(200):
            ids = instancia(k, 5000 + s)
            D = submatriz(ids)
            c_opt, r_opt = tsp_held_karp(D)
            c_nn, r_nn = tsp_vecino_mas_cercano(D)
            if c_nn - c_opt > 60:                          # al menos 1 minuto peor
                mejores.append(((c_nn - c_opt) / c_opt, s, ids, D, (c_opt, r_opt), (c_nn, r_nn)))
        if mejores:
            gap, s, ids, D, (c_opt, r_opt), (c_nn, r_nn) = max(mejores, key=lambda t: t[0])
            tramos = lambda r: [{"de": CAT.loc[ids[r[i]], "nombre"], "a": CAT.loc[ids[r[i + 1]], "nombre"],
                                 "min": round(D[r[i]][r[i + 1]] / 60, 1)} for i in range(len(r) - 1)]
            out = {"k": k, "semilla": 5000 + s,
                   "lugares": {int(i): CAT.loc[i, "nombre"] for i in ids},
                   "matriz_min": [[round(x / 60, 1) for x in fila] for fila in D],
                   "voraz": {"total_min": round(c_nn / 60, 1), "tramos": tramos(r_nn)},
                   "optimo": {"total_min": round(c_opt / 60, 1), "tramos": tramos(r_opt)},
                   "desviacion_pct": round(100 * gap, 2)}
            with open(DIR_RES / "req4_contraejemplo.json", "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=1)
            print(json.dumps(out, ensure_ascii=False, indent=1))
            return out


if __name__ == "__main__":
    solo = sys.argv[1:] or ["1", "3", "4", "5"]
    if "3" in solo:
        punto3_calidad()
    if "4" in solo:
        punto4_itinerario()
    if "5" in solo:
        punto5_contraejemplo()
    if "1" in solo:
        df = punto1_tiempo_vs_k()
        grafica_tiempo_vs_k(df)
        generar_tabla_desde_csv(str(DIR_RES / "req4_tiempo_vs_k.csv"), "Tiempo vs k", "milisegundos (ms)")
