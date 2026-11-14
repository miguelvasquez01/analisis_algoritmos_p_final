"""Envolvente convexa de la red (req3): lectura del resultado guardado y recálculo con QuickHull propio."""
import time

from pyproj import Transformer
from quickhull import quickhull

from .datos import CRS_UTM

_A_LATLON = Transformer.from_crs(CRS_UTM, "EPSG:4326", always_xy=True)
_A_UTM = Transformer.from_crs("EPSG:4326", CRS_UTM, always_xy=True)


def utm_a_latlon(vertices):
    """[(x, y) UTM 18N] -> [(lat, lon)]"""
    return [(lat, lon) for lon, lat in (_A_LATLON.transform(x, y) for x, y in vertices)]


def puntos_utm_enteros(G):
    """Nodos de la red en UTM 18N redondeados al entero y sin repetidos (req3, coordenadas)."""
    xs, ys = zip(*((d["x"], d["y"]) for _, d in G.nodes(data=True)))
    ex, ny = _A_UTM.transform(xs, ys)
    return sorted({(int(round(x)), int(round(y))) for x, y in zip(ex, ny)})


def recalcular(G):
    """Corre QuickHull propio sobre los nodos. Devuelve (vertices_utm, n_puntos, ms)."""
    pts = puntos_utm_enteros(G)
    t0 = time.perf_counter()
    v = quickhull(pts)
    return v, len(pts), (time.perf_counter() - t0) * 1000


def area_km2(vertices):
    s = sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(vertices, vertices[1:] + vertices[:1]))
    return abs(s) / 2 / 1e6
