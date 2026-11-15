"""Itinerario de un día: Held-Karp vs vecino más cercano (req4), calculado en el momento.

La matriz de tiempos entre los lugares elegidos se obtiene ejecutando Dijkstra con heap
(sin destino) desde cada lugar; con los mismos predecesores se dibujan los tramos."""
import time
from dataclasses import dataclass, field

from dijkstra_heap import dijkstra_heap
from itinerario import JORNADA_MIN, recortar_itinerario, resolver, tabla_itinerario

from .rutas import camino_desde_predecesores, coords_de_ruta


@dataclass
class Solucion:
    metodo: str
    recorrido: list        # ids del catálogo, empieza y termina en la partida
    viaje_min: float
    visitas_min: float
    tabla: list            # filas con el formato del anexo
    calculo_ms: float

    @property
    def total_min(self):
        return self.viaje_min + self.visitas_min


@dataclass
class Itinerario:
    partida: int
    atractivos_iniciales: list
    atractivos_finales: list
    pasos: list                      # pasos del recorte (vacío si no se aplicó)
    held_karp: Solucion
    voraz: Solucion
    jornada_min: float
    dijkstra_ms: float
    tramos: dict = field(default_factory=dict)   # (id_a, id_b) -> [(lat, lon), ...]

    @property
    def diferencia_min(self):
        return self.voraz.viaje_min - self.held_karp.viaje_min

    @property
    def diferencia_pct(self):
        hk = self.held_karp.viaje_min
        return 100 * self.diferencia_min / hk if hk else 0.0


def matriz_en_vivo(red, catalogo, ids):
    """Una ejecución de Dijkstra (sin destino) desde cada lugar. Devuelve (tiempos, predecesores, ms)."""
    nodo = catalogo["nodo_osm"].to_dict()
    tiempos, preds = {}, {}
    t0 = time.perf_counter()
    for a in ids:
        dist, pred, _ = dijkstra_heap(red.adj, nodo[a])
        tiempos[a] = {b: dist[nodo[b]] for b in ids}
        preds[a] = pred
    return tiempos, preds, (time.perf_counter() - t0) * 1000


def _solucion(metodo, ids, tiempos, duracion):
    t0 = time.perf_counter()
    costo, recorrido = resolver(ids, tiempos, metodo)
    ms = (time.perf_counter() - t0) * 1000
    visitas = sum(duracion[i] for i in ids[1:])
    return Solucion(metodo, recorrido, costo / 60, visitas,
                    tabla_itinerario(recorrido, tiempos, duracion), ms)


def planificar(red, catalogo, partida, atractivos, recortar=True, jornada_min=JORNADA_MIN):
    """Calcula el itinerario. Si `recortar` y no cabe en la jornada, aplica el criterio de req4."""
    atractivos = [a for a in atractivos if a != partida]
    ids = [partida] + atractivos
    duracion = catalogo["duracion_visita_min"].to_dict()
    tiempos, preds, ms_dij = matriz_en_vivo(red, catalogo, ids)

    pasos, finales = [], list(atractivos)
    if recortar:
        pasos, finales = recortar_itinerario(partida, atractivos, tiempos, duracion, jornada_min)

    ids_finales = [partida] + finales
    hk = _solucion("held_karp", ids_finales, tiempos, duracion)
    nn = _solucion("voraz", ids_finales, tiempos, duracion)

    nodo = catalogo["nodo_osm"].to_dict()
    tramos = {}
    for sol in (hk, nn):
        for a, b in zip(sol.recorrido, sol.recorrido[1:]):
            if (a, b) not in tramos:
                tramos[(a, b)] = coords_de_ruta(red.G, camino_desde_predecesores(preds[a], nodo[b]))
    return Itinerario(partida, list(atractivos), finales, pasos, hk, nn, jornada_min, ms_dij, tramos)
