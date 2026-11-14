"""Núcleo de normalización: orquesta carga, validación y resultado.

Autor: Roberto Carlos Flores Quintanilla
Programa: Kodigo — AI For Devs Jr. 5 (Instructor: Ing. Ronald Mejia)
Actividad: Normalización y Exploración de Transacciones Multifuente

Este módulo es el mismo que ejecutan la CLI (main.py / interfaz.py) y la
demo web (docs/index.html vía Pyodide), garantizando paridad de resultados.

Flujo por registro:
1. Detección de fuente por firma de campos (cargador.detectar_fuente).
2. Mapeo de los campos de la fuente a los roles del esquema.
3. Validación y normalización campo por campo (validador.*), acumulando
   todos los motivos si algo falla.
4. Regla de unicidad: un id ya reservado por una transacción VÁLIDA hace
   inválida la segunda aparición. Los ids de transacciones inválidas no
   reservan nada.
5. Las inválidas NO se descartan: se separan con su motivo exacto y quedan
   exportables, para que nada se pierda en silencio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cargador import cargar_reglas, detectar_fuente, leer_archivo_json, parsear_json_texto
from modelo import ESTADOS, Resultado, Transaccion, TransaccionInvalida
from validador import validar_estado, validar_fecha, validar_id, validar_monto, validar_moneda

_MONEDAS_CON_SIMBOLO = {"€": "EUR", "$": "USD"}


def _extraer_simbolo_de_monto(texto: str) -> str | None:
    """Si el monto trae un símbolo de moneda incrustado, se extrae."""
    for simbolo, codigo in _MONEDAS_CON_SIMBOLO.items():
        if simbolo in texto:
            return codigo
    return None


def _procesar_registro(
    indice: int,
    registro: dict[str, Any],
    reglas: dict[str, Any],
    ids_reservados: set[str],
) -> tuple[Transaccion | None, list[str]]:
    """Normaliza un registro. Devuelve (transaccion, []) o (None, motivos)."""
    fuentes: dict[str, dict[str, Any]] = reglas["fuentes"]
    nombre_fuente = detectar_fuente(registro, fuentes)
    if nombre_fuente is None:
        return None, ["fuente desconocida (ninguna firma de campos de reglas.json encaja)"]
    mapa = fuentes[nombre_fuente]

    motivos: list[str] = []

    id_valor, motivo = validar_id(registro.get(mapa["id"]))
    if motivo:
        motivos.append(motivo)

    monto_bruto = registro.get(mapa["amount"])
    simbolo = _extraer_simbolo_de_monto(str(monto_bruto)) if isinstance(monto_bruto, str) else None

    # La moneda se resuelve PRIMERO: el entero del monto necesita saber si
    # su moneda tiene unidad menor (centavos) para interpretarse bien.
    moneda, motivo = validar_moneda(
        registro.get(mapa["currency"]) if mapa["currency"] else None,
        simbolo,
        reglas["monedas"],
    )
    if motivo:
        motivos.append(motivo)

    monto, motivo = validar_monto(monto_bruto, moneda, reglas["monedas"])
    if motivo:
        motivos.append(motivo)

    fecha, motivo = validar_fecha(registro.get(mapa["timestamp"]), reglas["formatos_fecha"])
    if motivo:
        motivos.append(motivo)

    estado, motivo = validar_estado(registro.get(mapa["status"]), reglas["estados"])
    if motivo:
        motivos.append(motivo)

    if motivos:
        return None, motivos

    assert id_valor is not None and monto is not None and moneda is not None
    assert fecha is not None and estado is not None
    if id_valor in ids_reservados:
        return None, [f"id duplicado ({id_valor} ya fue aceptado en una transacción válida anterior)"]
    ids_reservados.add(id_valor)

    transaccion = Transaccion(
        id=id_valor, amount=monto, currency=moneda, timestamp=fecha, status=estado, source=nombre_fuente
    )
    return transaccion, []


def procesar(registros: list[dict[str, Any]], reglas: dict[str, Any]) -> Resultado:
    """Normaliza una lista de registros con las reglas dadas."""
    resultado = Resultado(total=len(registros))
    ids_reservados: set[str] = set()
    for indice, registro in enumerate(registros, start=1):
        transaccion, motivos = _procesar_registro(indice, registro, reglas, ids_reservados)
        if transaccion is None:
            resultado.invalidas.append(TransaccionInvalida(indice=indice, motivos=motivos, texto=registro))
        else:
            resultado.validas.append(transaccion)
    return resultado


def procesar_archivo(ruta: Path | str, reglas: dict[str, Any] | None = None) -> Resultado:
    """Lee un archivo JSON de transacciones y lo normaliza completo."""
    if reglas is None:
        reglas = cargar_reglas()
    return procesar(leer_archivo_json(ruta), reglas)


def procesar_texto(texto: str, reglas: dict[str, Any] | None = None) -> Resultado:
    """Normaliza desde texto JSON (la vía que usa la demo web con Pyodide)."""
    if reglas is None:
        reglas = cargar_reglas()
    return procesar(parsear_json_texto(texto), reglas)
