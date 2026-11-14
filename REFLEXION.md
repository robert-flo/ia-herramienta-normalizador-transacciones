# Documento de Reflexión Técnica

- **Programa:** Kodigo — AI For Devs Jr. 5
- **Actividad Individual:** Normalización y Exploración de Transacciones Multifuente
- **Estudiante:** Roberto Carlos Flores Quintanilla
- **Repositorio GitHub:** [https://github.com/robert-flo/ia-herramienta-normalizador-transacciones](https://github.com/robert-flo/ia-herramienta-normalizador-transacciones)
- **Demo Web Interactiva:** [https://robert-flo.github.io/ia-herramienta-normalizador-transacciones/](https://robert-flo.github.io/ia-herramienta-normalizador-transacciones/)

---

## 1. Delimitación de Responsabilidades: IA como Apoyo vs. Control del Desarrollador

El objetivo central fue construir un sistema de normalización de transacciones multifuente
manteniendo en todo momento el control humano sobre el esquema final, las reglas de
transformación y los criterios de validez, usando la IA únicamente como asistente técnico.

### Qué partes fueron decisión del desarrollador (Control Humano)

1. **El esquema normalizado final:** exactamente el contrato de la consigna (`id`, `amount`,
   `currency`, `timestamp`, `status`, `source`), con tipos concretos: monto SIEMPRE en
   unidades mayores, moneda ISO-4217 en mayúsculas, fecha ISO-8601 en UTC con sufijo `Z`,
   estado como enum cerrado `SUCCESS | FAILED | PENDING` y fuente detectada.
2. **La detección de fuente por firma de campos** (no por contenido ni por orden): un
   registro pertenece a la fuente cuyos nombres de campo están todos presentes, evaluando
   las fuentes en el orden de declaración de `reglas.json`. Fuente desconocida = inválida.
3. **La regla del monto entero en unidad menor:** `10050` con moneda USD son `100.50`
   (centavos de pasarela). La decidió el desarrollador tras leer los datos de ejemplo de la
   consigna, donde la misma transacción vale `100.50` en una fuente y `10050` en otra. El
   entero solo se interpreta así si su moneda tiene decimales declarados en el archivo de
   reglas; sin moneda resuelta, es inválido.
4. **La política ante inválidas (separación, no descarte):** nada se descarta en silencio.
   Toda transacción inválida queda separada con su índice, TODOS sus motivos y su contenido
   original, exportable; y solo suma a "Inválidas", nunca a las métricas por estado, moneda
   o fuente.
5. **La regla de unicidad de id:** un id repetido contra una transacción ya VÁLIDA es
   inválido por `id duplicado`; un id cuyo primer intento fue inválido no reserva nada.
6. **Los formatos de fecha y su orden de prueba:** ISO-8601 primero, `YYYY-MM-DD HH:MM:SS`
   después, y `DD/MM/AAAA` al final (convención latinoamericana). La fecha sin zona se
   asume UTC. Ver la evidencia del experimento en el punto 2.
7. **Monedas soportadas:** solo USD y EUR, con sus alias en el archivo de reglas. Cualquier
   otra moneda invalida el registro en lugar de "adivinar" tasas o ampliar el dominio.

### Qué partes del código fueron sugeridas o apoyadas por IA

1. **Estructura modular y dataclasses:** la IA ayudó a organizar la separación de
   responsabilidades (cargador / validador / normalizador / metricas / interfaz) y la
   forma de los dataclasses `Transaccion`, `TransaccionInvalida` y `Resultado`.
2. **La araña de formatos de monto y la demo web con Pyodide:** la IA propuso cómo
   tratar los formatos de monto europeos y cómo reutilizar el mismo núcleo Python en el
   navegador (descargando los `.py` del propio sitio en Pyodide, sin duplicar lógica en
   JavaScript).
3. **El arnés de pruebas E2E:** la IA ayudó a estructurar `tests/test_e2e.py` con
   `subprocess`, pero los valores esperados (`pruebas/esperados.md`) se calcularon a mano,
   registro por registro, ANTES de ejecutar nada.

---

## 2. Ejemplos Concretos: Sugerencias de IA, Detección y Corrección

### i. El orden de los componentes de fecha (sugerencia de IA incompleta)

Al pedir cómo parsear `"10/03/2025 14:22"`, la IA sugirió usar directamente
`strptime` con `"%m/%d/%Y"` (el orden por defecto que usan la mayoría de ejemplos en
inglés). Parece inofensivo, pero el formato de la fuente es día/mes/año:

- Con `"%m/%d/%Y"`, `"10/03/2025"` se lee como **3 de octubre** (transacción de una fecha
  distinta, silenciosamente) y `"13/03/2025"` ni siquiera parsea porque no hay mes 13.
- Con `"%d/%m/%Y"`, ambos tokens se leen correctamente como 10 y 13 de marzo.

Lo comprobé con un experimento real en Python 3.11 (`evidencia/experimento_orden_fecha.txt`)
y por eso `reglas.json` declara los formatos en orden explícito (ISO primero, día/mes
después) y `validar_fecha` los prueba en ese orden. Además, el lote
`pruebas/con_errores.json` incluye el registro `13/03/2025` como prueba de regresión: si
alguien reintroduce el orden MES/DIA, ese registro deja de ser válido y las 24 pruebas E2E
fallan.

### ii. La suma de montos con flotantes (sugerencia de IA ingenua)

La IA sugirió acumular los totales por moneda sumando `float` a medida que se recorre la
lista. El problema: los flotantes binarios acumulan residuos (`0.1 + 0.2` da
`0.30000000000000004`), y en un lote grande el total por moneda puede terminar mostrando
`4868.649999999999` en lugar de `4868.65`. Lo verifiqué con un experimento
(`evidencia/experimento_suma_flotantes.txt`) y la corrección fue redondear el acumulado a
2 decimales **en cada transacción**, no solo al final (`metricas.py`).

### iii. La detección de fuente por rol en lugar de por nombre de campo (bug propio detectado con las pruebas)

En la primera versión, la detección de fuente comparaba los **roles** del esquema
(`id`, `amount`...) en lugar de los **nombres de campo reales** de cada fuente
(`transaction_id`, `total`...). Las pruebas E2E del lote del enunciado lo atraparon al
instante: los registros 2 y 3 salían como "fuente desconocida" pese a tener todos sus
campos. La corrección fue comparar contra los valores del mapeo de `reglas.json`, y el
caso quedó cubierto por las pruebas para que no regrese.

---

## 3. Aprendizajes sobre el Uso de la IA como Herramienta y no como Reemplazo

1. **El valor esperado se calcula a mano, no se genera.** Calcular `pruebas/esperados.md`
   antes de ejecutar el programa fue lo que permitió detectar que dos de mis propios
   conteos manuales estaban mal (un total USD y un total EUR mal sumados) y que el bug de
   detección de fuente existía. Si la IA hubiera generado también los valores esperados,
   el programa habría "coincidido" con su propio error.
2. **Una sugerencia plausible de IA puede ser sutilmente incorrecta para el dominio.**
   El orden MES/DIA de `strptime` es el patrón más frecuente en código público, pero las
   fuentes de esta actividad usan día/mes/año. Verificar los límites de una función con
   datos adversos antes de integrarla fue la diferencia entre una fecha bien normalizada y
   un mes corrido en silencio.
3. **Las decisiones de negocio se expresan en datos, no en código disperso.** Poner las
   monedas, alias, estados, formatos de fecha y firmas de fuente en `reglas.json` hizo que
   cambiar una regla sea un cambio de configuración auditable, y que el código quede como
   maquinaria genérica al servicio de reglas explícitas.
