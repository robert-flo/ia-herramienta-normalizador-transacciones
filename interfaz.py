"""Interfaz interactiva de exploración (CLI con menú).

Autor: Roberto Carlos Flores Quintanilla
Programa: Kodigo — AI For Devs Jr. 5 (Instructor: Ing. Ronald Mejia)
Actividad: Normalización y Exploración de Transacciones Multifuente

El menú permite explorar y filtrar los datos normalizados, no solo verlos:
listar, filtrar por estado/moneda/fuente, revisar las inválidas con su
motivo exacto, ver métricas y exportar el JSON normalizado. Funciona con
los mismos objetos Resultado que la web, así que ambas vistas coinciden.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from cargador import cargar_reglas
from metricas import calcular
from normalizador import procesar_archivo
from modelo import ESTADOS, Resultado


def _leer_opcion(texto: str) -> str:
    try:
        return input(texto).strip()
    except EOFError:
        return "0"


def _leer_indice(opciones: list[str]) -> str | None:
    """Muestra opciones numeradas y devuelve la elegida (None si cancela)."""
    for numero, nombre in enumerate(opciones, start=1):
        print(f"  {numero}) {nombre}")
    eleccion = _leer_opcion("#> ")
    if not eleccion.isdigit() or not (1 <= int(eleccion) <= len(opciones)):
        print("Opción fuera de rango.\n")
        return None
    return opciones[int(eleccion) - 1]


def _mostrar_tabla_validas(transacciones: list[Any]) -> None:
    if not transacciones:
        print("  (sin resultados para este filtro)\n")
        return
    print(f"  {'#':>3}  {'ID':<10} {'MONTO':>12} {'MONEDA':<7} {'TIMESTAMP':<21} {'ESTADO':<8} FUENTE")
    for numero, transaccion in enumerate(transacciones, start=1):
        print(
            f"  {numero:>3}  {transaccion.id:<10} {transaccion.amount:>12.2f} "
            f"{transaccion.currency:<7} {transaccion.timestamp:<21} {transaccion.status:<8} {transaccion.source}"
        )
    print()


def _menu_filtros(resultado: Resultado) -> None:
    print("\n--- Filtrar transacciones válidas ---")
    elegida = _leer_indice(["por estado", "por moneda", "por fuente", "volver"])
    if elegida is None:
        return
    if elegida == "volver":
        return
    if elegida == "por estado":
        estado = _leer_indice(list(ESTADOS))
        if estado is None:
            return
        seleccion = [t for t in resultado.validas if t.status == estado]
        print(f"\nTransacciones con estado {estado}: {len(seleccion)}")
        _mostrar_tabla_validas(seleccion)
    elif elegida == "por moneda":
        monedas = sorted({t.currency for t in resultado.validas}) or ["(ninguna)"]
        moneda = _leer_indice(monedas)
        if moneda is None:
            return
        seleccion = [t for t in resultado.validas if t.currency == moneda]
        print(f"\nTransacciones en {moneda}: {len(seleccion)}")
        _mostrar_tabla_validas(seleccion)
    elif elegida == "por fuente":
        fuentes = sorted({t.source for t in resultado.validas}) or ["(ninguna)"]
        fuente = _leer_indice(fuentes)
        if fuente is None:
            return
        seleccion = [t for t in resultado.validas if t.source == fuente]
        print(f"\nTransacciones de la fuente {fuente}: {len(seleccion)}")
        _mostrar_tabla_validas(seleccion)


def _exportar(resultado: Resultado) -> None:
    ruta = _leer_opcion("Ruta del JSON de salida [salida/normalizadas.json]: ").strip()
    if not ruta:
        ruta = "salida/normalizadas.json"
    import json

    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8") as manejador:
        json.dump([t.como_dict() for t in resultado.validas], manejador, ensure_ascii=False, indent=2)
        manejador.write("\n")
    print(f"Exportadas {resultado.total_validas} transacciones a {destino}\n")


def ejecutar_menu(resultado: Resultado, origen: str) -> None:
    """Bucle principal del menú interactivo."""
    while True:
        print(f"\n===== EXPLORADOR DE TRANSACCIONES — {origen} =====")
        print(f"  Lote cargado: {resultado.total} procesadas | "
              f"{resultado.total_validas} válidas | {resultado.total_invalidas} inválidas")
        print("  1) Ver métricas generales")
        print("  2) Listar transacciones normalizadas")
        print("  3) Filtrar transacciones válidas")
        print("  4) Ver transacciones inválidas y sus motivos")
        print("  5) Exportar JSON normalizado")
        print("  0) Salir")
        opcion = _leer_opcion("Opción> ")
        if opcion == "1":
            imprimir_metricas(resultado)
        elif opcion == "2":
            print(f"\nTransacciones normalizadas ({resultado.total_validas}):")
            _mostrar_tabla_validas(resultado.validas)
        elif opcion == "3":
            _menu_filtros(resultado)
        elif opcion == "4":
            imprimir_invalidas(resultado)
        elif opcion == "5":
            _exportar(resultado)
        elif opcion == "0":
            print("Hasta luego.")
            return
        else:
            print("Opción no válida.")


def imprimir_metricas(resultado: Resultado) -> None:
    datos = calcular(resultado)
    print("\n--- Métricas ---")
    print(f"Total procesadas: {datos['total_procesadas']}")
    print(f"Válidas: {datos['total_validas']}")
    print(f"Inválidas: {datos['total_invalidas']}")
    print("Conteo por estado:")
    for estado, conteo in datos["por_estado"].items():
        print(f"  {estado}: {conteo}")
    print("Totales por moneda:")
    if datos["total_por_moneda"]:
        for moneda, total in datos["total_por_moneda"].items():
            print(f"  {moneda}: {total:.2f} ({datos['conteo_por_moneda'][moneda]} transacciones)")
    else:
        print("  (ninguna)")
    print("Conteo por fuente:")
    if datos["por_fuente"]:
        for fuente, conteo in datos["por_fuente"].items():
            print(f"  {fuente}: {conteo}")
    else:
        print("  (ninguna)")
    print()


def imprimir_invalidas(resultado: Resultado) -> None:
    print(f"\n--- Transacciones inválidas ({resultado.total_invalidas}) ---")
    if not resultado.invalidas:
        print("  (ninguna: todas las transacciones pasaron la validación)\n")
        return
    print("Una cuenta por registro, aunque tenga varias razones:")
    for invalida in resultado.invalidas:
        texto = str(invalida.texto) if invalida.texto else "(registro vacío)"
        print(f"  - registro {invalida.indice}: {'; '.join(invalida.motivos)}")
        print(f"      contenido: {texto}")
    print()


def ejecutar_interactivo(ruta: str) -> int:
    """Carga el archivo indicado y abre el menú de exploración."""
    try:
        reglas = cargar_reglas()
        resultado = procesar_archivo(ruta, reglas)
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo {ruta!r}.", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"Error: sin permiso para leer {ruta!r}.", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    imprimir_metricas(resultado)
    ejecutar_menu(resultado, origen=str(ruta))
    return 0
