"""
Verificación de la capa de servicios de la aplicación (req5) contra los resultados
ya calculados en los requerimientos 2, 3 y 4. Uso:  py app/verificar_app.py
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from servicios import envolvente as env                       # noqa: E402
from servicios.datos import (cargar_catalogo, cargar_envolvente,  # noqa: E402
                             cargar_matriz, cargar_red)
from servicios.itinerario import planificar                    # noqa: E402
from servicios.rutas import ruta_entre                         # noqa: E402


def main():
    red, cat, M = cargar_red(), cargar_catalogo(), cargar_matriz()

    # 1. Ruta mínima: Dijkstra con destino = celda de la matriz de req2
    rnd = random.Random(7)
    pares = [tuple(rnd.sample(list(cat.index), 2)) for _ in range(20)]
    for a, b in pares:
        r = ruta_entre(red, cat.nodo_osm[a], cat.nodo_osm[b])
        assert abs(r.tiempo_s - M[a][b]) < 1e-2, (a, b, r.tiempo_s, M[a][b])
        assert r.nodos[0] == cat.nodo_osm[a] and r.nodos[-1] == cat.nodo_osm[b]
    r = ruta_entre(red, cat.nodo_osm[1], cat.nodo_osm[1])
    assert r.tiempo_s == 0
    print(f"[OK] Rutas: 20 pares coinciden con req2/matriz_tiempos.csv; origen = destino -> 0 s")

    # 2. Envolvente: QuickHull propio sobre los nodos = vértices guardados en req3
    J = cargar_envolvente()
    v, n, ms = env.recalcular(red.G)
    assert n == J["n_puntos"] and len(v) == J["n_vertices"]
    assert set(map(tuple, v)) == set(map(tuple, J["vertices_antihorario"]))
    assert abs(env.area_km2(v) - J["area_km2"]) < 0.1
    print(f"[OK] Envolvente: n={n}, h={len(v)}, área {env.area_km2(v):.1f} km², iguales a req3 ({ms:.1f} ms)")

    # 3. Itinerario: mismo resultado que req4 punto 4
    it = planificar(red, cat, 1, [13, 15, 16, 17, 18, 21, 22, 25], recortar=True)
    assert sorted(it.atractivos_finales) == [17, 18, 21, 22, 25], it.atractivos_finales
    assert round(it.held_karp.viaje_min, 1) == 123.9 and round(it.voraz.viaje_min, 1) == 127.4
    assert it.held_karp.recorrido == [1, 21, 17, 18, 25, 22, 1]
    assert abs(it.held_karp.tabla[-1]["acumulado_h"] * 60 - it.held_karp.total_min) < 1e-6
    print(f"[OK] Itinerario: finales {it.atractivos_finales}, HK {it.held_karp.viaje_min:.1f} min, "
          f"voraz {it.voraz.viaje_min:.1f} min (Dijkstra x9: {it.dijkstra_ms:.0f} ms)")
    print("Todas las verificaciones pasaron.")


if __name__ == "__main__":
    main()
