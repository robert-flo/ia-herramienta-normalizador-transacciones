"""Carga de transacciones y detección de la fuente de cada registro.

Autor: Roberto Carlos Flores Quintanilla
Programa: Kodigo — AI For Devs Jr. 5 (Instructor: Ing. Ronald Mejia)
Actividad: Normalización y Exploración de Transacciones Multifuente

Decisiones del desarrollador:
- La fuente de cada transacción se detecta por FIRMA de campos: un registro
  pertenece a la fuente cuyas llaves del rol (id, amount, currency,
  timestamp, status) están TODAS presentes. Las fuentes se evalúan en el
  orden en que aparecen en reglas.json y se toma la primera coincidencia
  completa; si ninguna encaja, la fuente es desconocida y el registro es
  inválido.
- El archivo se lee como UTF-8 con BOM tolerado (utf-8-sig): los editores de
  Windows no rompen el primer registro.
- Un archivo cuya raíz no sea una lista JSON se rechaza con un mensaje claro,
  sin traceback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RUTA_REGLAS = Path(__file__).resolve().parent / "reglas.json"


def cargar_reglas(ruta: Path | str | None = None) -> dict[str, Any]:
    """Lee el archivo de reglas (mapeo de estados, monedas, fechas, fuentes)."""
    camino = Path(ruta) if ruta else RUTA_REGLAS
    with camino.open("r", encoding="utf-8-sig") as manejador:
        return json.load(manejador)


def leer_archivo_json(ruta: Path | str) -> list[dict[str, Any]]:
    """Lee un archivo de transacciones y devuelve la lista de registros.

    Levanta ValueError con mensaje en español si la raíz no es una lista.
    FileNotFoundError / PermissionError se propagan para que la interfaz
    los traduzca a mensajes claros.
    """
    camino = Path(ruta)
    with camino.open("r", encoding="utf-8-sig") as manejador:
        datos = json.load(manejador)
    if not isinstance(datos, list):
        raise ValueError("El archivo debe contener una lista JSON de transacciones ([ ... ]).")
    return [registro for registro in datos if registro is not None]


def parsear_json_texto(texto: str) -> list[dict[str, Any]]:
    """Parsea el contenido JSON desde texto (la web usa esta vía con Pyodide)."""
    datos = json.loads(texto)
    if not isinstance(datos, list):
        raise ValueError("El JSON debe ser una lista de transacciones ([ ... ]).")
    return [registro for registro in datos if registro is not None]


def detectar_fuente(
    registro: dict[str, Any], fuentes: dict[str, dict[str, Any]]
) -> str | None:
    """Devuelve el nombre de la fuente cuyos campos están todos presentes.

    Devuelve None cuando ninguna firma completa encaja. Un registro con
    campos de dos fuentes a la vez entra por la primera fuente declarada en
    reglas.json (orden de declaración), decisión documentada en el README.
    """
    for nombre, mapa in fuentes.items():
        # La firma son los NOMBRES DE CAMPO de la fuente (los valores del
        # mapeo), no los roles del esquema. app_movil no trae campo de
        # moneda (viene incrustada en el monto), así que los roles nulos
        # no participan de la firma.
        if all(clave in registro for clave in mapa.values() if clave):
            return nombre
    return None
