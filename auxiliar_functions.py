"""
Módulo genérico de herramientas y benchmark para análisis de algoritmos.
"""
import os
import time
import statistics
import pandas as pd

def medir_tiempo_ejecucion(funcion, *args, unidad_tiempo="s", umbral_segundos=60.0, repeticiones=5, **kwargs):
    """
    Ejecuta cualquier función y mide su tiempo con soporte para múltiples unidades.
    
    Parámetros:
        funcion: La función a ejecutar/medir.
        *args: Argumentos posicionales de la función.
        unidad_tiempo (str): Unidad del resultado: 's' (segundos), 'ms' (milisegundos) o 'ns' (nanosegundos).
        umbral_segundos (float): Tiempo límite en segundos para decidir si medir 1 sola vez.
        repeticiones (int): Número de repeticiones para calcular la mediana si t <= umbral.
        **kwargs: Argumentos nombrados de la función.
        
    Retorna:
        tuple: (resultado_de_la_funcion, tiempo_mediana_convertido, unidad_tiempo)
    """
    factores = {"s": 1e9, "ms": 1e6, "ns": 1.0}
    if unidad_tiempo not in factores:
        raise ValueError(f"Unidad '{unidad_tiempo}' no válida. Usa 's', 'ms' o 'ns'.")

    def _ejecutar():
        t0 = time.perf_counter_ns()
        res = funcion(*args, **kwargs)
        return res, time.perf_counter_ns() - t0

    resultado, primer_t_ns = _ejecutar()
    divisor = factores[unidad_tiempo]
    fmt = (lambda t: int(t / divisor)) if unidad_tiempo == "ns" else (lambda t: round(t / divisor, 5))

    if primer_t_ns / 1e9 > umbral_segundos:
        print(f"   [!] Ejecución pesada (> {umbral_segundos}s): 1 sola medición ({fmt(primer_t_ns)} {unidad_tiempo})")
        return resultado, fmt(primer_t_ns), unidad_tiempo

    tiempos_ns = [primer_t_ns] + [_ejecutar()[1] for _ in range(repeticiones - 1)]
    mediana_ns = statistics.median(tiempos_ns)
    tiempo_final = fmt(mediana_ns)
    
    tiempos_impresion = [fmt(t) for t in tiempos_ns]
    print(f"   [+] {repeticiones} corridas. Tiempos ({unidad_tiempo}): {tiempos_impresion} | Mediana: {tiempo_final} {unidad_tiempo}")

    return resultado, tiempo_final, unidad_tiempo


def guardar_resultados_csv(datos, ruta_csv):
    """
    Guarda una lista de diccionarios o un DataFrame en un archivo CSV.
    Crea automáticamente las carpetas si no existen.
    
    Parámetros:
        datos (list | pd.DataFrame): Datos a guardar.
        ruta_csv (str): Ruta relativa o absoluta del archivo CSV de destino.
    """
    if isinstance(datos, list):
        df = pd.DataFrame(datos)
    else:
        df = datos
        
    # Crear directorio si no existe
    directorio = os.path.dirname(ruta_csv)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio, exist_ok=True)
        
    df.to_csv(ruta_csv, index=False)
    print(f" -> Resultados guardados exitosamente en CSV: '{ruta_csv}'")


def generar_tabla_desde_csv(ruta_csv, titulo_tabla="TABLA DE RESULTADOS", unidad_tiempo="segundos (s)"):
    """
    Lee un archivo CSV guardado y genera una representación formateada de la tabla.
    
    Parámetros:
        ruta_csv (str): Ruta del archivo CSV a leer.
        titulo_tabla (str): Encabezado explicativo de la tabla.
        unidad_tiempo (str): Especificación explícita de la unidad de tiempo según Requisito 8.
        
    Retorna:
        pd.DataFrame: El DataFrame cargado por si se requiere procesamiento adicional.
    """
    if not os.path.exists(ruta_csv):
        raise FileNotFoundError(f"No se encontró el archivo de resultados en: {ruta_csv}")
        
    df = pd.read_csv(ruta_csv)
    
    print("\n" + "=" * 60)
    print(f"{titulo_tabla.upper()}")
    print(f"[Unidad de tiempo especificada: {unidad_tiempo}]")
    print("=" * 60)
    print(df.to_string(index=False))
    print("=" * 60 + "\n")
    
    return df