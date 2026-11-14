"""Reglas de validez de una transacción (puras, sin efectos secundarios).

Autor: Roberto Carlos Flores Quintanilla
Programa: Kodigo — AI For Devs Jr. 5 (Instructor: Ing. Ronald Mejia)
Actividad: Normalización y Exploración de Transacciones Multifuente

Estas funciones son el criterio de validez definido por el desarrollador.
Cada una devuelve (valor_normalizado, None) si pasa o (None, motivo) si
falla, para que la capa de orquestación acumule TODOS los motivos del
registro y lo cuente una sola vez como inválido.
"""

from __future__ import annotations

import datetime
import re
from typing import Any

# Símbolos de moneda que pueden venir incrustados en el monto.
_RE_SIMBOLO_EUR = re.compile(r"[€]")
_RE_SIMBOLO_USD = re.compile(r"[$]")
_RE_NUMERO = re.compile(r"^-?\d+(?:[.,]\d+)*$")


def validar_id(valor: Any) -> tuple[str | None, str | None]:
    """El id es obligatorio y se normaliza a texto no vacío."""
    if valor is None:
        return None, "id ausente"
    texto = str(valor).strip()
    if not texto:
        return None, "id vacío"
    return texto, None


def validar_monto(
    valor: Any, moneda: str | None, monedas: dict[str, Any]
) -> tuple[float | None, str | None]:
    """Normaliza el monto a float positivo en unidades mayores.

    ``moneda`` es el código ISO ya resuelto (del campo de moneda o del
    símbolo incrustado), que solo se necesita para la regla del entero.

    Reglas del desarrollador:
    - Cadena numérica con coma decimal y/o punto de miles (formato
      europeo, como '€99,99' o '1.230,45'): coma = separador decimal,
      puntos = separadores de miles.
    - Cadena con punto decimal simple ('100.50'): punto = separador
      decimal (formato anglosajón).
    - Varios puntos sin coma ('1.2.3'): formato AMBIGUO, se rechaza
      en lugar de adivinar.
    - Entero puro con moneda de unidad menor (decimales == 2 en
      reglas.json): se interpreta en la unidad MENOR (centavos), como
      reportan las pasarelas: 10050 -> 100.50.
    - El monto debe ser estrictamente positivo.
    """
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None, "monto ausente o vacío"

    if isinstance(valor, bool):
        return None, "monto no es un número"

    es_entero = isinstance(valor, int)
    texto: str | None = None
    if isinstance(valor, str):
        # Los símbolos de moneda y los espacios se quitan ANTES de
        # comprobar que el resto es numérico: '€99,99' es un monto
        # numérico cuyo símbolo informa la moneda.
        limpio = valor.strip()
        for simbolo in ("\u20ac", "$"):
            limpio = limpio.replace(simbolo, "")
        limpio = limpio.strip()
        if not _RE_NUMERO.match(limpio):
            return None, f"monto no numérico ({valor!r})"
        texto = limpio
    elif not es_entero and not isinstance(valor, float):
        return None, f"monto con tipo no soportado ({type(valor).__name__})"

    if es_entero:
        # Entero: unidad menor de la moneda (centavos) si la moneda
        # tiene decimales declarados en reglas.json.
        info = monedas.get(moneda) if moneda else None
        decimales = info.get("decimales") if info else None
        if decimales is None:
            return None, "monto entero sin moneda con unidad menor definida"
        monto = valor / (10**decimales)
        return (monto, None) if monto > 0 else (None, "monto no positivo")

    assert texto is not None
    if "," in texto:
        # Formato europeo: puntos son miles, coma es decimal.
        texto = texto.replace(".", "").replace(",", ".")
    elif texto.count(".") > 1:
        return None, f"formato de monto ambiguo ({valor!r})"
    try:
        monto = float(texto)
    except ValueError:
        return None, f"monto no numérico ({valor!r})"
    if monto <= 0:
        return None, "monto no positivo"
    return round(monto, 2), None


def validar_moneda(
    valor: Any, extraida_del_simbolo: str | None, monedas: dict[str, Any]
) -> tuple[str | None, str | None]:
    """Normaliza la moneda a su código ISO-4217 en mayúsculas.

    ``extraida_del_simbolo`` tiene prioridad cuando el monto trae el símbolo
    incrustado ('€99,99' => EUR): el símbolo del monto es la evidencia más
    cercana al dato. Sin símbolo, se resuelve por el campo de moneda contra
    la lista de alias de reglas.json. Moneda no soportada => inválida.
    """
    if extraida_del_simbolo:
        return extraida_del_simbolo, None
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None, "moneda ausente o vacía"
    texto = str(valor).strip().lower()
    for codigo, info in monedas.items():
        if texto == codigo.lower() or texto in [s.lower() for s in info["simbolos"]]:
            return codigo, None
    return None, f"moneda no soportada ({valor!r})"


def validar_fecha(valor: Any, formatos: list[str]) -> tuple[str | None, str | None]:
    """Normaliza la fecha a ISO-8601 UTC con sufijo Z.

    Decisiones del desarrollador:
    - Se prueba cada formato declarado en reglas.json, en orden: primero los
      ISO-8601 y después las variantes dia/mes/año (convención latinoamericana:
      '10/03/2025' es 10 de marzo, NO 3 de octubre).
    - Una fecha sin zona horaria se asume en UTC (decisión explícita para que
      el comparador lexicográfico del timestamp sea estable).
    - Una fecha con zona se convierte a UTC antes de emitir el texto final.
    """
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None, "fecha ausente o vacía"
    texto = str(valor).strip()
    for patron in formatos:
        try:
            fecha = datetime.datetime.strptime(texto, patron)
        except ValueError:
            continue
        if fecha.tzinfo is not None:
            fecha = fecha.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        return fecha.strftime("%Y-%m-%dT%H:%M:%SZ"), None
    return None, f"fecha con formato no reconocido ({valor!r})"


def validar_estado(valor: Any, estados: dict[str, list[str]]) -> tuple[str | None, str | None]:
    """Mapea el estado original al enum cerrado SUCCESS | FAILED | PENDING."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return None, "estado ausente o vacío"
    texto = str(valor).strip().lower()
    for estado, alias in estados.items():
        if texto == estado.lower() or texto in alias:
            return estado, None
    return None, f"estado no reconocido ({valor!r})"
