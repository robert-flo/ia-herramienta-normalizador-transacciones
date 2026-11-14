"""Métricas del lote normalizado.

Autor: Roberto Carlos Flores Quintanilla
Programa: Kodigo — AI For Devs Jr. 5 (Instructor: Ing. Ronald Mejia)
Actividad: Normalización y Exploración de Transacciones Multifuente

Métricas exigidas por la actividad (todas sobre transacciones VÁLIDAS,
salvo los totales del lote):
- Total procesadas, válidas e inválidas.
- Conteo por estado (SUCCESS / FAILED / PENDING).
- Totales por moneda (suma de montos, redondeada a 2 decimales).
- Conteo por fuente detectada.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from modelo import ESTADOS, Resultado


def calcular(resultado: Resultado) -> dict[str, Any]:
    """Construye el diccionario de métricas con orden estable."""
    por_estado: Counter[str] = Counter({estado: 0 for estado in ESTADOS})
    por_moneda: Counter[str] = Counter()
    total_por_moneda: dict[str, float] = {}
    por_fuente: Counter[str] = Counter()
    for transaccion in resultado.validas:
        por_estado[transaccion.status] += 1
        por_moneda[transaccion.currency] += 1
        total_por_moneda[transaccion.currency] = round(
            total_por_moneda.get(transaccion.currency, 0.0) + transaccion.amount, 2
        )
        por_fuente[transaccion.source] += 1
    return {
        "total_procesadas": resultado.total,
        "total_validas": resultado.total_validas,
        "total_invalidas": resultado.total_invalidas,
        "por_estado": {estado: por_estado[estado] for estado in ESTADOS},
        "conteo_por_moneda": dict(sorted(por_moneda.items())),
        "total_por_moneda": dict(sorted(total_por_moneda.items())),
        "por_fuente": dict(sorted(por_fuente.items())),
    }
