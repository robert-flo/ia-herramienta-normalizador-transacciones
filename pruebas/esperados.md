# Valores esperados calculados a mano ANTES de ejecutar el programa

Cálculo manual, registro por registro, de los tres lotes de prueba. El
programa debe reproducir exactamente estos números (si no, hay un bug).

---

## pruebas/ejemplo_enunciado.json (los 3 registros del enunciado)

| # | Registro | Fuente | Monto | Moneda | Estado | Fecha ISO | Válida |
|---|---|---|---|---|---|---|---|
| 1 | tx_001 | terminal_pos | 100.50 | USD | SUCCESS | 2025-03-10T14:22:00Z | Sí |
| 2 | 204 (total 10050) | pasarela_web | 100.50 | USD | SUCCESS | 2025-03-10T14:22:00Z | Sí |
| 3 | A-77 | app_movil | 99.99 | EUR | SUCCESS | 2025-03-10T14:22:00Z | Sí |

- Procesadas: **3** · Válidas: **3** · Inválidas: **0**
- Por estado: SUCCESS **3**, FAILED 0, PENDING 0
- Totales por moneda: USD **201.00** (100.50+100.50, 2), EUR **99.99** (1)
- Por fuente: terminal_pos 1, pasarela_web 1, app_movil 1

---

## pruebas/bien_formado.json (10 registros, todos válidos)

| # | Registro | Fuente | Monto | Moneda | Estado | Válida |
|---|---|---|---|---|---|---|
| 1 | tx_101 | terminal_pos | 250.00 | USD | SUCCESS | Sí |
| 2 | tx_102 | terminal_pos | 18.75 | USD | PENDING | Sí |
| 3 | tx_103 | terminal_pos | 64.30 | EUR | FAILED | Sí |
| 4 | 205 (total 9990) | pasarela_web | 99.90 | USD | SUCCESS | Sí |
| 5 | 206 (total 450000) | pasarela_web | 4500.00 | USD | PENDING | Sí |
| 6 | 207 (total 1250) | pasarela_web | 12.50 | EUR | FAILED | Sí |
| 7 | A-80 | app_movil | 12.50 | EUR | SUCCESS | Sí |
| 8 | A-81 | app_movil | 1230.45 | EUR | SUCCESS | Sí |
| 9 | A-82 | app_movil | 7.00 | EUR | PENDING | Sí |
| 10 | tx_105 | terminal_pos | 99.99 | EUR | SUCCESS | Sí |

- Procesadas: **10** · Válidas: **10** · Inválidas: **0**
- Por estado: SUCCESS **5**, FAILED **2**, PENDING **3**
- Totales por moneda: USD **4868.65** (250.00+18.75+99.90+4500.00, 4 transacciones),
  EUR **1426.74** (64.30+12.50+12.50+1230.45+7.00+99.99, 6 transacciones)
- Por fuente: terminal_pos **4**, pasarela_web **3**, app_movil **3**

---

## pruebas/con_errores.json (12 registros: 4 válidos, 8 inválidos)

| # | Registro | Fuente | Resultado esperado y motivo |
|---|---|---|---|
| 1 | tx_201 | terminal_pos | Válida (50.00 USD, SUCCESS) |
| 2 | tx_202, monto "abc" | terminal_pos | Inválida: monto no numérico |
| 3 | 301, moneda "gbp" | pasarela_web | Inválida: moneda no soportada |
| 4 | tx_203, fecha 2025-02-30 | terminal_pos | Inválida: fecha inexistente en el calendario |
| 5 | tx_204, monto 0.00 | terminal_pos | Inválida: monto no positivo |
| 6 | tx_201 (repetido) | terminal_pos | Inválida: id duplicado (el #1 ya reservó tx_201) |
| 7 | A-90, estado "charged" | app_movil | Inválida: estado no reconocido |
| 8 | 302, fecha 13/03/2025 | pasarela_web | Válida (15.00 USD, SUCCESS). Prueba del orden día/mes: el mes 13 no existe en MM/DD |
| 9 | {"foo": "bar"} | — | Inválida: fuente desconocida |
| 10 | tx_205, monto "" | terminal_pos | Inválida: monto ausente o vacío |
| 11 | 303 (total 800) | pasarela_web | Válida (8.00 USD, SUCCESS) |
| 12 | A-91 | app_movil | Válida (5.25 EUR, PENDING) |

- Procesadas: **12** · Válidas: **4** · Inválidas: **8**
- Por estado: SUCCESS **3**, FAILED **0**, PENDING **1**
- Totales por moneda: USD **73.00** (50.00+15.00+8.00, 3 transacciones),
  EUR **5.25** (1 transacción)
- Por fuente: terminal_pos **1**, pasarela_web **2**, app_movil **1**
