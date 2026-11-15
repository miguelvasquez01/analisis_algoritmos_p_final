"""
Requerimiento 4.4 - Itinerario de un día (lógica reutilizable).

Funciones puras, sin lectura de archivos: las usan el script de experimentos
(req4/1_experimentos_tsp.py) y la aplicación (app/).

Convenciones:
  - `tiempos` es un diccionario de diccionarios {id_origen: {id_destino: segundos}}.
  - `duracion` es un diccionario {id: minutos de visita}.
  - Los recorridos se expresan con ids del catálogo y empiezan y terminan en la partida.
"""
from tsp import tsp_held_karp, tsp_vecino_mas_cercano

JORNADA_MIN = 660          # 11 h


def submatriz(ids, tiempos):
    """Matriz (lista de listas, en s) restringida a `ids`; ids[0] es la partida."""
    return [[tiempos[a][b] for b in ids] for a in ids]


def resolver(ids, tiempos, metodo="held_karp"):
    """Ordena los lugares `ids` (ids[0] = partida). Devuelve (costo_s, recorrido_en_ids)."""
    D = submatriz(ids, tiempos)
    f = tsp_held_karp if metodo == "held_karp" else tsp_vecino_mas_cercano
    costo, ruta = f(D)
    return costo, [ids[i] for i in ruta]


def duracion_dia(partida, atractivos, tiempos, duracion):
    """(viaje_min, visitas_min, recorrido) del recorrido óptimo (Held-Karp)."""
    costo, ruta = resolver([partida] + list(atractivos), tiempos)
    visitas = sum(duracion[a] for a in atractivos)
    return costo / 60, visitas, ruta


def recortar_itinerario(partida, atractivos, tiempos, duracion, jornada_min=JORNADA_MIN):
    """Ordena con Held-Karp; si no cabe en la jornada, quita en cada paso el atractivo
    cuya eliminación más reduce la duración total (visita + desvío) y recalcula.

    Devuelve (pasos, atractivos_finales). Cada paso es un dict con:
    atractivos, recorrido, viaje_min, visitas_min, total_min, cabe, quitado, libera_min.
    """
    actuales = list(atractivos)
    pasos = []
    while True:
        viaje, visitas, ruta = duracion_dia(partida, actuales, tiempos, duracion)
        total = viaje + visitas
        paso = {"atractivos": list(actuales), "recorrido": ruta, "viaje_min": viaje,
                "visitas_min": visitas, "total_min": total, "cabe": total <= jornada_min,
                "quitado": None, "libera_min": None}
        pasos.append(paso)
        if paso["cabe"] or not actuales:
            break
        # Criterio: quitar el atractivo que más tiempo libera
        mejor = None
        for a in actuales:
            resto = [x for x in actuales if x != a]
            v, vis, _ = duracion_dia(partida, resto, tiempos, duracion)
            if mejor is None or v + vis < mejor[1]:
                mejor = (a, v + vis)
        paso["quitado"] = mejor[0]
        paso["libera_min"] = total - mejor[1]
        actuales.remove(mejor[0])
    return pasos, actuales


def tabla_itinerario(recorrido, tiempos, duracion):
    """Filas con el formato del anexo: orden, lugar, desplazamiento (min), visita (min),
    tiempo acumulado (h). La última fila es el regreso a la partida."""
    filas, acumulado = [], 0.0
    for pos in range(1, len(recorrido)):
        a, b = recorrido[pos - 1], recorrido[pos]
        desplaz = tiempos[a][b] / 60
        regreso = pos == len(recorrido) - 1
        visita = 0 if regreso else duracion[b]
        acumulado += desplaz + visita
        filas.append({"orden": "Regreso" if regreso else pos, "id": b,
                      "desplazamiento_min": desplaz, "visita_min": None if regreso else visita,
                      "acumulado_h": acumulado / 60})
    return filas
