"""Modelo de datos normalizado del sistema de transacciones.

Autor: Roberto Carlos Flores Quintanilla
Programa: Kodigo — AI For Devs Jr. 5 (Instructor: Ing. Ronald Mejia)
Actividad: Normalización y Exploración de Transacciones Multifuente

Decisión del desarrollador: el esquema final normalizado es exactamente el
contrato definido para la actividad, con tipos concretos:

    id        str    identificador único de la transacción (texto)
    amount    float  monto SIEMPRE en unidades mayores (10050 -> 100.50)
    currency  str    código ISO-4217 en mayúsculas (USD, EUR)
    timestamp str    ISO-8601 en UTC con sufijo Z
    status    str    SUCCESS | FAILED | PENDING (enum cerrado)
    source    str    fuente detectada por firma de campos

Toda transacción que no pueda cumplir este contrato queda en
TransaccionInvalida con su motivo exacto: nunca se descarta en silencio.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Estados del enum cerrado, en orden fijo para que el reporte sea estable.
ESTADOS = ("SUCCESS", "FAILED", "PENDING")


@dataclass
class Transaccion:
    """Una transacción ya normalizada al esquema final."""

    id: str
    amount: float
    currency: str
    timestamp: str
    status: str
    source: str

    def como_dict(self) -> dict[str, Any]:
        """Versión JSON del esquema normalizado (el orden es el del contrato)."""
        return {
            "id": self.id,
            "amount": self.amount,
            "currency": self.currency,
            "timestamp": self.timestamp,
            "status": self.status,
            "source": self.source,
        }


@dataclass
class TransaccionInvalida:
    """Una transacción que viola al menos un criterio de validez.

    Decisiones del desarrollador:
    - ``indice`` es la posición 1-based dentro del archivo de entrada, para
      que el usuario pueda localizar el registro original.
    - ``motivos`` acumula TODAS las razones detectadas (no solo la primera),
      pero el registro cuenta UNA sola vez como inválido.
    - ``texto`` guarda el registro original tal cual llegó, para auditoría.
    """

    indice: int
    motivos: list[str]
    texto: dict[str, Any]


@dataclass
class Resultado:
    """Resultado completo de un lote de transacciones procesadas."""

    total: int = 0
    validas: list[Transaccion] = field(default_factory=list)
    invalidas: list[TransaccionInvalida] = field(default_factory=list)

    @property
    def total_validas(self) -> int:
        return len(self.validas)

    @property
    def total_invalidas(self) -> int:
        return len(self.invalidas)
