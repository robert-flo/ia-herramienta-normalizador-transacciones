"""Pruebas E2E sobre el CLI real (python3 main.py <archivo>).

Autor: Roberto Carlos Flores Quintanilla
Programa: Kodigo — AI For Devs Jr. 5 (Instructor: Ing. Ronald Mejia)

Los valores esperados provienen de pruebas/esperados.md, calculados a mano
registro por registro ANTES de ejecutar el programa. Si el CLI no reproduce
esos números, la prueba falla y hay un bug.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_MAIN = RAIZ / "main.py"


def ejecutar_cli(ruta_relativa: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUTA_MAIN), ruta_relativa],
        cwd=str(RAIZ),
        capture_output=True,
        text=True,
        check=True,
    )


class TestEjemploEnunciado(unittest.TestCase):
    """Los 3 registros de ejemplo del enunciado."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.salida = ejecutar_cli("pruebas/ejemplo_enunciado.json").stdout

    def test_totales(self) -> None:
        self.assertIn("Transacciones procesadas: 3", self.salida)
        self.assertIn("Válidas: 3", self.salida)
        self.assertIn("Inválidas: 0", self.salida)

    def test_estados(self) -> None:
        self.assertIn("SUCCESS: 3", self.salida)
        self.assertIn("FAILED: 0", self.salida)
        self.assertIn("PENDING: 0", self.salida)

    def test_totales_por_moneda(self) -> None:
        self.assertIn("USD: 201.00 en 2 transacciones", self.salida)
        self.assertIn("EUR: 99.99 en 1 transacciones", self.salida)

    def test_fuentes(self) -> None:
        self.assertIn("terminal_pos: 1", self.salida)
        self.assertIn("pasarela_web: 1", self.salida)
        self.assertIn("app_movil: 1", self.salida)


class TestBienFormado(unittest.TestCase):
    """10 registros válidos con montos, monedas y estados variados."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.salida = ejecutar_cli("pruebas/bien_formado.json").stdout

    def test_totales(self) -> None:
        self.assertIn("Transacciones procesadas: 10", self.salida)
        self.assertIn("Válidas: 10", self.salida)
        self.assertIn("Inválidas: 0", self.salida)

    def test_estados(self) -> None:
        self.assertIn("SUCCESS: 5", self.salida)
        self.assertIn("FAILED: 2", self.salida)
        self.assertIn("PENDING: 3", self.salida)

    def test_totales_por_moneda(self) -> None:
        self.assertIn("USD: 4868.65 en 4 transacciones", self.salida)
        self.assertIn("EUR: 1426.74 en 6 transacciones", self.salida)

    def test_fuentes(self) -> None:
        self.assertIn("terminal_pos: 4", self.salida)
        self.assertIn("pasarela_web: 3", self.salida)
        self.assertIn("app_movil: 3", self.salida)

class TestNucleo(unittest.TestCase):
    """Pruebas del núcleo (las mismas funciones que usa la CLI y la web)."""

    def test_entero_se_interpreta_en_centavos(self) -> None:
        from normalizador import procesar_archivo
        resultado = procesar_archivo("pruebas/bien_formado.json")
        registro_206 = [t for t in resultado.validas if t.id == "206"]
        self.assertEqual(len(registro_206), 1)
        self.assertEqual(registro_206[0].amount, 4500.00)

    def test_esquema_normalizado_es_el_del_enunciado(self) -> None:
        from normalizador import procesar_archivo
        resultado = procesar_archivo("pruebas/ejemplo_enunciado.json")
        como_dict = resultado.validas[0].como_dict()
        self.assertEqual(
            list(como_dict.keys()),
            ["id", "amount", "currency", "timestamp", "status", "source"],
        )
        self.assertEqual(como_dict["timestamp"], "2025-03-10T14:22:00Z")


class TestConErrores(unittest.TestCase):
    """12 registros: 4 válidos y 8 inválidos con motivos específicos."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.salida = ejecutar_cli("pruebas/con_errores.json").stdout

    def test_totales(self) -> None:
        self.assertIn("Transacciones procesadas: 12", self.salida)
        self.assertIn("Válidas: 4", self.salida)
        self.assertIn("Inválidas: 8", self.salida)

    def test_estados(self) -> None:
        self.assertIn("SUCCESS: 3", self.salida)
        self.assertIn("FAILED: 0", self.salida)
        self.assertIn("PENDING: 1", self.salida)

    def test_totales_por_moneda(self) -> None:
        self.assertIn("USD: 73.00 en 3 transacciones", self.salida)
        self.assertIn("EUR: 5.25 en 1 transacciones", self.salida)

    def test_fuentes(self) -> None:
        self.assertIn("terminal_pos: 1", self.salida)
        self.assertIn("pasarela_web: 2", self.salida)
        self.assertIn("app_movil: 1", self.salida)

    def test_motivo_monto_no_numerico(self) -> None:
        self.assertIn("registro 2: monto no numérico ('abc')", self.salida)

    def test_motivo_moneda_no_soportada(self) -> None:
        self.assertIn("registro 3: moneda no soportada ('gbp')", self.salida)

    def test_motivo_fecha_inexistente(self) -> None:
        # 2025-02-30 no existe en el calendario: strptime lo rechaza.
        self.assertIn("registro 4: fecha con formato no reconocido", self.salida)

    def test_motivo_monto_no_positivo(self) -> None:
        self.assertIn("registro 5: monto no positivo", self.salida)

    def test_motivo_id_duplicado(self) -> None:
        self.assertIn("registro 6: id duplicado (tx_201", self.salida)

    def test_motivo_estado_no_reconocido(self) -> None:
        self.assertIn("registro 7: estado no reconocido ('charged')", self.salida)

    def test_motivo_fuente_desconocida(self) -> None:
        self.assertIn("registro 9: fuente desconocida", self.salida)

    def test_orden_dia_mes(self) -> None:
        # 13/03/2025 es 13 de marzo: si se leyera MM/DD, el mes 13 sería inválido.
        self.assertIn("USD: 73.00 en 3 transacciones", self.salida)


class TestCasosBorde(unittest.TestCase):
    def test_archivo_inexistente_devuelve_codigo_1_sin_traceback(self) -> None:
        proceso = subprocess.run(
            [sys.executable, str(RUTA_MAIN), "pruebas/no_existe.json"],
            cwd=str(RAIZ), capture_output=True, text=True,
        )
        self.assertEqual(proceso.returncode, 1)
        self.assertIn("no se encontró el archivo", proceso.stderr)
        self.assertNotIn("Traceback", proceso.stderr)

    def test_archivo_que_no_es_lista_devuelve_codigo_1(self) -> None:
        (RAIZ / "pruebas" / "_no_lista.json").write_text('{"id": "tx"}', encoding="utf-8")
        try:
            proceso = subprocess.run(
                [sys.executable, str(RUTA_MAIN), "pruebas/_no_lista.json"],
                cwd=str(RAIZ), capture_output=True, text=True,
            )
            self.assertEqual(proceso.returncode, 1)
            self.assertIn("lista JSON", proceso.stderr)
        finally:
            (RAIZ / "pruebas" / "_no_lista.json").unlink()


if __name__ == "__main__":
    unittest.main()
