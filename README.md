# Normalizador de Transacciones Multifuente en Python (CLI Interactiva + Demo Web)

- **Programa:** Kodigo — AI For Devs Jr. 5
- **Actividad Individual:** Normalización y Exploración de Transacciones Multifuente
- **Estudiante:** Roberto Carlos Flores Quintanilla
- **Repositorio GitHub:** [https://github.com/robert-flo/ia-herramienta-normalizador-transacciones](https://github.com/robert-flo/ia-herramienta-normalizador-transacciones)
- **Demo Web en Vivo (GitHub Pages):** [https://robert-flo.github.io/ia-herramienta-normalizador-transacciones/](https://robert-flo.github.io/ia-herramienta-normalizador-transacciones/)
- **Documento de Entrega PDF (con Carátula Kodigo):** [`RobertoFlores-Tarea04.pdf`](RobertoFlores-Tarea04.pdf) | [`RobertoFlores-Tarea04.docx`](RobertoFlores-Tarea04.docx)

---

## Descripción del Proyecto

Sistema en Python que lee transacciones de un archivo JSON, detecta la **fuente** de cada
registro por la firma de sus campos, los normaliza a un **esquema común** (id, amount,
currency, timestamp ISO-8601, status, source), aplica reglas explícitas de transformación
y validación, y expone métricas y exploración filtrable a través de una **CLI interactiva**
y de una **demo web** que ejecuta el mismo código en el navegador.

La lógica está separada por responsabilidad: carga y detección de fuente
([`cargador.py`](cargador.py)), reglas de validez puras ([`validador.py`](validador.py)),
orquestación de la normalización ([`normalizador.py`](normalizador.py)), métricas
([`metricas.py`](metricas.py)), modelo de datos ([`modelo.py`](modelo.py)) y la interfaz
([`interfaz.py`](interfaz.py) + [`main.py`](main.py)). El **archivo de reglas**
([`reglas.json`](reglas.json)) concentra el mapeo de estados, las monedas soportadas, los
formatos de fecha admitidos y la firma de cada fuente: cambiar una regla no toca código.

Tanto la CLI como la web ([`docs/index.html`](docs/index.html) mediante Pyodide) ejecutan
exactamente los mismos módulos Python, garantizando resultados idénticos en ambos entornos.

---

## Ejecución Rápida (Consola y Demo)

### 1. Probar en la Web (sin instalar nada)
Abre **[https://robert-flo.github.io/ia-herramienta-normalizador-transacciones/](https://robert-flo.github.io/ia-herramienta-normalizador-transacciones/)**, espera unos segundos a que cargue Python (Pyodide) y:
- Pulsa cualquiera de los **botones de prueba en 1 clic** (`ejemplo_enunciado.json`, `bien_formado.json`, `con_errores.json`), o
- Carga un archivo `.json` desde tu computadora o pega/edite el JSON en el editor integrado.
- Explora con los **filtros por estado, moneda y fuente** y descarga el JSON normalizado.

### 2. Ejecutar desde la Terminal (CLI)

```bash
# Informe directo del lote bien formado
python3 main.py pruebas/bien_formado.json

# Informe del lote con errores, casos borde y detalle de inválidas
python3 main.py pruebas/con_errores.json

# Los 3 registros de ejemplo del enunciado de la actividad
python3 main.py pruebas/ejemplo_enunciado.json

# Modo interactivo: carga el archivo y abre el menú de exploración
python3 main.py

# Ejecutar la demostración completa guiada en terminal
./demo.sh

# Ejecutar las 24 pruebas automatizadas E2E
python3 -m unittest tests.test_e2e -v
```

En modo interactivo el menú permite: **ver métricas generales**, **listar** las
transacciones normalizadas, **filtrar** por estado / moneda / fuente, **revisar las
inválidas** con su motivo exacto, **exportar** el JSON normalizado y **salir**.

---

## Esquema Normalizado Final (Decisión del Desarrollador)

Toda transacción válida queda con esta forma (la de la consigna):

```json
{
  "id": "string",
  "amount": 99.99,
  "currency": "USD",
  "timestamp": "2025-03-10T14:22:00Z",
  "status": "SUCCESS | FAILED | PENDING",
  "source": "string"
}
```

- `amount` es SIEMPRE un número en **unidades mayores** (nunca centavos): `10050` con
  moneda USD se normaliza a `100.50`.
- `currency` es el **código ISO-4217 en mayúsculas** (USD, EUR), se resuelva del campo
  propio (`usd`, `currency_code`), de un alias (`$`) o del **símbolo incrustado en el
  monto** (`€99,99` => EUR).
- `timestamp` es **ISO-8601 en UTC** con sufijo `Z`. Una fecha sin zona se asume UTC.
- `status` es el enum cerrado `SUCCESS | FAILED | PENDING`; cualquier estado fuera del
  mapeo de `reglas.json` invalida el registro.
- `source` es la fuente detectada por firma de campos: `terminal_pos`, `pasarela_web` o
  `app_movil`.

---

## Decisiones Técnicas y Reglas de Normalización y Validación (Definidas por el Desarrollador)

1. **Detección de fuente por firma de campos.** Un registro pertenece a la fuente cuyos
   nombres de campo (los valores del mapeo en `reglas.json`) están TODOS presentes. Las
   fuentes se evalúan en orden de declaración y gana la primera coincidencia completa. Si
   ninguna encaja, el registro es inválido con motivo `fuente desconocida`. Las fuentes
   declaradas son:
   - `terminal_pos`: `id`, `amount`, `currency`, `timestamp`, `status`.
   - `pasarela_web`: `transaction_id`, `total`, `currency_code`, `created_at`, `state`.
   - `app_movil`: `ref`, `amount` (con símbolo), `date`, `result` (sin campo de moneda).
2. **Monto (conversión y unidades):**
   - Formato europeo (`€99,99`, `1.230,45`): la coma es separador decimal y los puntos
     separadores de miles. El símbolo incrustado define la moneda.
   - Formato anglosajón (`100.50`): el punto es separador decimal.
   - Varios puntos sin coma (`1.2.3`): formato AMBIGUO, se rechaza en lugar de adivinar.
   - **Entero puro** con moneda de unidad menor (las declaradas en `reglas.json` con 2
     decimales): se interpreta en la unidad menor (centavos), como reportan las pasarelas:
     `10050` => `100.50`. Un entero sin moneda resuelta es inválido.
   - El monto debe ser **estrictamente positivo**; `0.00` y los negativos son inválidos.
3. **Fechas:** se prueban los formatos de `reglas.json` **en orden declarado**: primero
   los ISO-8601 (`2025-03-10T14:22:00Z`, con o sin zona, con o sin fracción), después
   `YYYY-MM-DD HH:MM:SS` y al final los **día/mes/año** (`10/03/2025 14:22`), convención
   latinoamericana: `10/03` es 10 de marzo, NO 3 de octubre. Ese orden se decidió después
   de experimentar con `strptime` (ver `evidencia/experimento_orden_fecha.txt`): con
   MES/DIA, `10/03/2025` se lee como 3 de octubre y `13/03/2025` ni siquiera parsea.
4. **Estados:** mapeo explícito en `reglas.json`: `completed|ok|success|paid|settled|
   approved|aprobada` => SUCCESS; `failed|error|rejected|declined|denied|cancelled|
   canceled|fallida` => FAILED; `pending|processing|held|en_proceso|espera|pendiente`
   => PENDING. La comparación es case-insensitive. Estado ausente o no mapeado => inválido.
5. **Monedas soportadas:** USD y EUR (alias declarados en `reglas.json`, incluidos `$` y
   `€`). Cualquier otra moneda (`gbp`) => inválida con motivo exacto.
6. **Política ante transacciones inválidas (separación, no descarte):** una transacción
   que viole cualquier criterio NO se descarta en silencio: se separa en la lista de
   inválidas con su **índice 1-based en el archivo**, TODOS sus motivos y su contenido
   original, y se puede exportar. Nunca suma a los conteos por estado, moneda o fuente.
7. **Unicidad de id:** un id ya reservado por una transacción VÁLIDA hace inválida a la
   segunda aparición (`id duplicado`). Los ids de transacciones inválidas no reservan
   nada, para no penalizar un id por el error de otro campo.
8. **Robustez de entrada/salida:** lectura `utf-8-sig` (BOM de Windows tolerado), mensajes
   claros en español para archivo inexistente, directorio, sin permiso o JSON que no sea
   una lista, siempre con código de salida distinto de cero y sin traceback.

---

## Métricas Generadas

- **Total procesadas**, **válidas** e **inválidas**.
- **Conteo por estado** (SUCCESS / FAILED / PENDING).
- **Totales por moneda** (suma de montos redondeada a 2 decimales) y conteo por moneda.
- **Conteo por fuente** detectada.
- **Detalle de inválidas** con índice, motivo(s) y contenido original.

---

## Evidencia de Pruebas: Resultados Esperados vs. Obtenidos

El cálculo manual registro por registro está en [`pruebas/esperados.md`](pruebas/esperados.md)
y las salidas reales en [`evidencia/`](evidencia/).

| Archivo de Prueba | Procesadas | Válidas | Inválidas | SUCCESS | FAILED | PENDING | Totales por moneda | Resultado |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | --- | :---: |
| [`pruebas/ejemplo_enunciado.json`](pruebas/ejemplo_enunciado.json) | **3** | **3** | **0** | **3** | 0 | 0 | USD 201.00 · EUR 99.99 | ✅ Coincide |
| [`pruebas/bien_formado.json`](pruebas/bien_formado.json) | **10** | **10** | **0** | **5** | **2** | **3** | USD 4868.65 · EUR 1426.74 | ✅ Coincide |
| [`pruebas/con_errores.json`](pruebas/con_errores.json) | **12** | **4** | **8** | **3** | 0 | **1** | USD 73.00 · EUR 5.25 | ✅ Coincide |

### Salida en consola para `pruebas/con_errores.json`

```text
Origen: pruebas/con_errores.json
Transacciones procesadas: 12
Válidas: 4
Inválidas: 8
Conteo por estado (sobre válidas):
  SUCCESS: 3
  FAILED: 0
  PENDING: 1
Totales por moneda (sobre válidas):
  USD: 73.00 en 3 transacciones
  EUR: 5.25 en 1 transacciones
Conteo por fuente detectada (sobre válidas):
  terminal_pos: 1
  pasarela_web: 2
  app_movil: 1
Solapamiento: las métricas por estado, moneda y fuente solo suman transacciones VÁLIDAS. Una transacción inválida cuenta en Inválidas y en su detalle con motivo, nunca en los conteos por estado.

Detalle de inválidas (8):
  - registro 2: monto no numérico ('abc')
  - registro 3: moneda no soportada ('gbp')
  - registro 4: fecha con formato no reconocido ('2025-02-30 10:00:00')
  - registro 5: monto no positivo
  - registro 6: id duplicado (tx_201 ya fue aceptado en una transacción válida anterior)
  - registro 7: estado no reconocido ('charged')
  - registro 9: fuente desconocida (ninguna firma de campos de reglas.json encaja)
  - registro 10: monto ausente o vacío
```

---

## Estructura del Repositorio

```text
├── RobertoFlores-Tarea04.pdf   # Documento formal de entrega con carátula Kodigo y nota técnica
├── RobertoFlores-Tarea04.docx  # Versión editable en Word del documento de entrega
├── reglas.json                 # Archivo de reglas: monedas, estados, formatos de fecha y firmas de fuente
├── modelo.py                   # Modelo de datos: Transaccion, TransaccionInvalida, Resultado
├── cargador.py                 # Lectura JSON, carga de reglas y detección de fuente
├── validador.py                # Reglas puras de validez (monto, moneda, fecha, estado)
├── normalizador.py             # Orquestación de la normalización (CLI y web comparten este núcleo)
├── metricas.py                 # Métricas del lote
├── interfaz.py                 # CLI interactiva: menú, filtros, exportación
├── main.py                     # Punto de entrada (informe directo o menú interactivo)
├── demo.sh                     # Script ejecutable para demostración en vivo paso a paso
├── README.md                   # Documentación general, reglas y evidencias de pruebas
├── REFLEXION.md                # Documento de reflexión técnica (decisiones y uso de IA)
├── pruebas/
│   ├── ejemplo_enunciado.json  # Caso de prueba 1: los 3 registros de ejemplo del enunciado
│   ├── bien_formado.json       # Caso de prueba 2: 10 registros 100% válidos
│   ├── con_errores.json        # Caso de prueba 3: 12 registros con 8 inconsistencias distintas
│   └── esperados.md            # Valores esperados calculados manualmente registro por registro
├── tests/
│   └── test_e2e.py             # 24 pruebas automatizadas E2E sobre el CLI real
├── docs/
│   └── index.html              # Interfaz web interactiva con Pyodide y botones de demo
└── evidencia/                  # Salidas reales de CLI, unittest y experimentos documentados
```
