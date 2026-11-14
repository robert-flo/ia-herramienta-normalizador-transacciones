#!/usr/bin/env python3
"""CLI del normalizador de transacciones multifuente.

Uso:
  python3 main.py ruta/al/archivo.json   # informe directo del lote
  python3 main.py                        # carga un archivo y abre el menú interactivo

La ruta la elige el usuario (argumento posicional o prompt). No se envía
nada a un servidor. Los errores ordinarios de archivo se informan en
español y terminan con código distinto de cero, sin traceback.
"""

from __future__ import annotations

import sys
from pathlib import Path

from cargador import cargar_reglas
from normalizador import procesar_archivo
from metricas import calcular
from modelo import Resultado
from interfaz import ejecutar_menu, imprimir_metricas


def _obtener_ruta(argv: list[str]) -> str | None:
    if len(argv) > 1:
        return argv[1]
    try:
        return input("Ruta del archivo de transacciones: ").strip()
    except EOFError:
        print("Error: no se proporcionó una ruta.", file=sys.stderr)
        return None


def informe_directo(resultado: Resultado, origen: str) -> str:
    """Informe de consola en modo directo (una ejecución, sin menú)."""
    datos = calcular(resultado)
    lineas = [
        f"Origen: {origen}",
        f"Transacciones procesadas: {datos['total_procesadas']}",
        f"Válidas: {datos['total_validas']}",
        f"Inválidas: {datos['total_invalidas']}",
        "Conteo por estado (sobre válidas):",
    ]
    for estado, conteo in datos["por_estado"].items():
        lineas.append(f"  {estado}: {conteo}")
    lineas.append("Totales por moneda (sobre válidas):")
    if datos["total_por_moneda"]:
        for moneda, total in datos["total_por_moneda"].items():
            lineas.append(
                f"  {moneda}: {total:.2f} en {datos['conteo_por_moneda'][moneda]} transacciones"
            )
    else:
        lineas.append("  (ninguna)")
    lineas.append("Conteo por fuente detectada (sobre válidas):")
    if datos["por_fuente"]:
        for fuente, conteo in datos["por_fuente"].items():
            lineas.append(f"  {fuente}: {conteo}")
    else:
        lineas.append("  (ninguna)")
    lineas.append(
        "Solapamiento: las métricas por estado, moneda y fuente solo suman "
        "transacciones VÁLIDAS. Una transacción inválida cuenta en "
        "Inválidas y en su detalle con motivo, nunca en los conteos por estado."
    )
    texto = "\n".join(lineas) + "\n"
    if resultado.invalidas:
        texto += "\n" + detalle_invalidas_texto(resultado)
    return texto


def detalle_invalidas_texto(resultado: Resultado) -> str:
    lineas = [f"Detalle de inválidas ({resultado.total_invalidas}):"]
    for invalida in resultado.invalidas:
        lineas.append(f"  - registro {invalida.indice}: {'; '.join(invalida.motivos)}")
    return "\n".join(lineas) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    ruta = _obtener_ruta(argv)
    if not ruta:
        print("Error: la ruta está vacía.", file=sys.stderr)
        return 1

    camino = Path(ruta)
    if not camino.is_file():
        if camino.is_dir():
            print(f"Error: {ruta!r} es un directorio, no un archivo.", file=sys.stderr)
        else:
            print(f"Error: no se encontró el archivo {ruta!r}.", file=sys.stderr)
        return 1

    try:
        reglas = cargar_reglas()
        resultado = procesar_archivo(camino, reglas)
    except PermissionError:
        print(f"Error: sin permiso para leer {ruta!r}.", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if len(argv) > 1:
        # Modo directo: informe y termina (el mismo que usan las pruebas E2E).
        sys.stdout.write(informe_directo(resultado, str(camino)))
        return 0

    # Modo interactivo: menú de exploración sobre el lote cargado.
    imprimir_metricas(resultado)
    ejecutar_menu(resultado, origen=str(camino))
    return 0


if __name__ == "__main__":
    sys.exit(main())
