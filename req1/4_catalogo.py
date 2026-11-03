import pandas as pd

lugares_data = [
    # ---------------------------------------------------------------------
    # 1. CABECERAS MUNICIPALES (12) - Coordenadas en Plaza Principal
    # ---------------------------------------------------------------------
    {"id": 1, "nombre": "Armenia (Plaza de Bolívar)", "municipio": "Armenia", "categoria": "Cabecera municipal", "lat": 4.532601950706727, "lon": -75.67296696369789, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 2, "nombre": "Buenavista (Parque Principal)", "municipio": "Buenavista", "categoria": "Cabecera municipal", "lat": 4.359481275255843, "lon": -75.73842154785672, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 3, "nombre": "Calarcá (Parque Bolívar)", "municipio": "Calarcá", "categoria": "Cabecera municipal", "lat": 4.530651880989591, "lon": -75.64046712695813, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 4, "nombre": "Circasia (Parque Principal)", "municipio": "Circasia", "categoria": "Cabecera municipal", "lat": 4.620122347824713, "lon": -75.63466583485183, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 5, "nombre": "Córdoba (Parque Principal)", "municipio": "Córdoba", "categoria": "Cabecera municipal", "lat": 4.390111215590019, "lon": -75.68549165231633, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 6, "nombre": "Filandia (Parque Principal)", "municipio": "Filandia", "categoria": "Cabecera municipal", "lat": 4.6747808, "lon": -75.6581641, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 7, "nombre": "Génova (Parque Principal)", "municipio": "Génova", "categoria": "Cabecera municipal", "lat": 4.2063759, "lon": -75.7905522, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 8, "nombre": "La Tebaida (Parque Principal)", "municipio": "La Tebaida", "categoria": "Cabecera municipal", "lat": 4.4537698, "lon": -75.78932, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 9, "nombre": "Montenegro (Parque Principal)", "municipio": "Montenegro", "categoria": "Cabecera municipal", "lat": 4.5671697, "lon": -75.7504826, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 10, "nombre": "Pijao (Parque Principal)", "municipio": "Pijao", "categoria": "Cabecera municipal", "lat": 4.3341006, "lon": -75.7040288, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 11, "nombre": "Quimbaya (Parque Principal)", "municipio": "Quimbaya", "categoria": "Cabecera municipal", "lat": 4.6224862, "lon": -75.7630803, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},
    {"id": 12, "nombre": "Salento (Parque Principal)", "municipio": "Salento", "categoria": "Cabecera municipal", "lat": 4.6372491, "lon": -75.5698067, "duracion_visita_min": 0, "fuente": "OpenStreetMap Node / Coordenadas de centroide de plaza principal"},

    # ---------------------------------------------------------------------
    # 2. ATRACTIVOS TURÍSTICOS (15) - Incluye duración sugerida (min)
    # Criterio: Tiempos promedios recomendados por operadores turísticos
    # ---------------------------------------------------------------------
    {"id": 13, "nombre": "Parque Nacional del Café", "municipio": "Montenegro", "categoria": "Atractivo turístico", "lat": 4.540273697203204, "lon": -75.77065080233238, "duracion_visita_min": 480, "fuente": "Guía Oficial Parque del Café / Cotelco (Atracciones mecanicas y shows)"},
    {"id": 14, "nombre": "PANACA", "municipio": "Quimbaya", "categoria": "Atractivo turístico", "lat": 4.607683, "lon": -75.8186979, "duracion_visita_min": 480, "fuente": "Operador Turístico PANACA (10 estaciones agropecuarias)"},
    {"id": 15, "nombre": "Valle de Cocora", "municipio": "Salento", "categoria": "Atractivo turístico", "lat": 4.637712, "lon": -75.48907, "duracion_visita_min": 240, "fuente": "MINCIT (Senderismo de media montaña en palmas de cera)"},
    {"id": 16, "nombre": "Jardín Botánico del Quindío", "municipio": "Calarcá", "categoria": "Atractivo turístico", "lat": 4.5116806, "lon": -75.6509772, "duracion_visita_min": 180, "fuente": "Guía del Mariposario del Quindío (Bosque nativo y mariposario)"},
    {"id": 17, "nombre": "Museo del Oro Quimbaya", "municipio": "Armenia", "categoria": "Atractivo turístico", "lat": 4.5713808, "lon": -75.6478397, "duracion_visita_min": 90, "fuente": "Red de Museos Banco de la República (Exhibición arqueológica)"},
    {"id": 18, "nombre": "Mirador del Colina (Filandia)", "municipio": "Filandia", "categoria": "Atractivo turístico", "lat": 4.6688362, "lon": -75.665644, "duracion_visita_min": 60, "fuente": "Alcaldía de Filandia (Torre de avistamiento y paisajes)"},
    {"id": 19, "nombre": "Recuca (Recorrido de la Cultura Cafetera)", "municipio": "Calarcá", "categoria": "Atractivo turístico", "lat": 4.4326046, "lon": -75.7332347, "duracion_visita_min": 180, "fuente": "Experiencia Recuca (Taller vivencial y catación de café)"},
    {"id": 20, "nombre": "Parque Los Arrieros", "municipio": "Quimbaya", "categoria": "Atractivo turístico", "lat": 4.5800499, "lon": -75.780889, "duracion_visita_min": 300, "fuente": "Parque Los Arrieros (Senderos temáticos y muestras culturales)"},
    {"id": 21, "nombre": "Parque de la Vida", "municipio": "Armenia", "categoria": "Atractivo turístico", "lat": 4.548106, "lon": -75.6604214, "duracion_visita_min": 120, "fuente": "Sociedad de Mejoras Públicas de Armenia (Paseo ecológico urbano)"},
    {"id": 22, "nombre": "Mirador Alto de la Cruz", "municipio": "Salento", "categoria": "Atractivo turístico", "lat": 4.6397978, "lon": -75.5663879, "duracion_visita_min": 45, "fuente": "Criterio de caminata urbana (Escalinata de la Calle Real)"},
    {"id": 23, "nombre": "Café San Alberto (Mirador Buenavista)", "municipio": "Buenavista", "categoria": "Atractivo turístico", "lat": 4.3594441, "lon": -75.7346233, "duracion_visita_min": 180, "fuente": "Experiencia San Alberto (Bautizo cafetero y cata de café)"},
    {"id": 24, "nombre": "Cascadas Río Verde", "municipio": "Córdoba", "categoria": "Atractivo turístico", "lat": 4.4030339, "lon": -75.6582667, "duracion_visita_min": 300, "fuente": "Ruta Ecoturística Córdoba (Caminata de acceso y baño)"},
    {"id": 25, "nombre": "Reserva Natural Kasaguadua", "municipio": "Salento", "categoria": "Atractivo turístico", "lat": 4.6293971, "lon": -75.5850789, "duracion_visita_min": 120, "fuente": "Reserva Kasaguadua (Recorrido por bosque de niebla)"},
    {"id": 26, "nombre": "Valle de Maravélez", "municipio": "La Tebaida", "categoria": "Atractivo turístico", "lat": 4.4181244, "lon": -75.8419601, "duracion_visita_min": 180, "fuente": "Ruta Paisajística PCC (Recorrido a orillas del río La Vieja)"},
    {"id": 27, "nombre": "Centro Histórico y Plaza de Pijao", "municipio": "Pijao", "categoria": "Atractivo turístico", "lat": 4.3341006, "lon": -75.7040288, "duracion_visita_min": 90, "fuente": "Red Cittaslow (Recorrido de arquitectura bahareque)"},

    # ---------------------------------------------------------------------
    # 3. FINCAS CAFETERAS U HOTELES RURALES (8)
    # ---------------------------------------------------------------------
    {"id": 28, "nombre": "Finca El Ocaso Salento", "municipio": "Salento", "categoria": "Finca/Hotel rural", "lat": 4.623706428724347, "lon": -75.59527070273641, "duracion_visita_min": 0, "fuente": "Alojamiento rural / Punto de partida o llegada"},
    {"id": 29, "nombre": "Hacienda Combia", "municipio": "Calarcá", "categoria": "Finca/Hotel rural", "lat": 4.4917288, "lon": -75.6864861, "duracion_visita_min": 0, "fuente": "Alojamiento rural / Punto de partida o llegada"},
    {"id": 30, "nombre": "Finca Hotel El Bosque de Samán", "municipio": "Quimbaya", "categoria": "Finca/Hotel rural", "lat": 4.6602912, "lon": -75.7388148, "duracion_visita_min": 0, "fuente": "Alojamiento rural / Punto de partida o llegada"},
    {"id": 31, "nombre": "Finca La Morelia", "municipio": "Armenia", "categoria": "Finca/Hotel rural", "lat": 4.466534191089022, "lon": -75.72347746069879, "duracion_visita_min": 0, "fuente": "Alojamiento rural / Punto de partida o llegada"},
    {"id": 32, "nombre": "Hotel Rural Sazagua Quindío", "municipio": "Circasia", "categoria": "Finca/Hotel rural", "lat": 4.6385134, "lon": -75.5468058, "duracion_visita_min": 0, "fuente": "Alojamiento rural / Punto de partida o llegada"},
    {"id": 33, "nombre": "Finca Hotel Las Palmas", "municipio": "La Tebaida", "categoria": "Finca/Hotel rural", "lat": 4.4311024, "lon": -75.8329317, "duracion_visita_min": 0, "fuente": "Alojamiento rural / Punto de partida o llegada"},
    {"id": 34, "nombre": "Finca Hotel Resplandor Quindiano", "municipio": "Montenegro", "categoria": "Finca/Hotel rural", "lat": 4.571843063225896, "lon": -75.7127186763618, "duracion_visita_min": 0, "fuente": "Alojamiento rural / Punto de partida o llegada"},
    {"id": 35, "nombre": "Finca Hotel Del Bosque", "municipio": "Montenegro", "categoria": "Finca/Hotel rural", "lat": 4.5424421897564695, "lon": -75.73965160727586, "duracion_visita_min": 0, "fuente": "Alojamiento rural / Punto de partida o llegada"},

    # ---------------------------------------------------------------------
    # 4. CENTROS DE ACOPIO O TRILLADORAS DE CAFÉ (5)
    # ---------------------------------------------------------------------
    {"id": 36, "nombre": "Trilladora Armenia (Comité de Cafeteros)", "municipio": "Armenia", "categoria": "Centro de acopio/Trilladora", "lat": 4.5194238, "lon": -75.6907261, "duracion_visita_min": 0, "fuente": "Infraestructura agroindustrial / Logística de carga"},
    {"id": 37, "nombre": "Central de Beneficio de Café - Calarcá", "municipio": "Calarcá", "categoria": "Centro de acopio/Trilladora", "lat": 4.5290536, "lon": -75.6435899, "duracion_visita_min": 0, "fuente": "Infraestructura agroindustrial / Logística de carga"},
    {"id": 38, "nombre": "Coop. de Caficultores del Quindío (Filandia)", "municipio": "Filandia", "categoria": "Centro de acopio/Trilladora", "lat": 4.6755839, "lon": -75.6576487, "duracion_visita_min": 0, "fuente": "Infraestructura agroindustrial / Logística de carga"},
    {"id": 39, "nombre": "Punto de Acopio de Café Génova", "municipio": "Génova", "categoria": "Centro de acopio/Trilladora", "lat": 4.2046518, "lon": -75.7925731, "duracion_visita_min": 0, "fuente": "Infraestructura agroindustrial / Logística de carga"},
    {"id": 40, "nombre": "Trilladora y Almacén de Café Quimbaya", "municipio": "Quimbaya", "categoria": "Centro de acopio/Trilladora", "lat": 4.6207692, "lon": -75.7668589, "duracion_visita_min": 0, "fuente": "Infraestructura agroindustrial / Logística de carga"}
]

df_catalogo = pd.DataFrame(lugares_data)
df_catalogo.to_csv("req1/catalogo_lugares_quindio.csv", index=False)