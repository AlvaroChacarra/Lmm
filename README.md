# LMM — Valoración Monte Carlo de un Snowblade

Ejercicio de Modelos de Tipos de Interés (AFI). Objetivo: valorar un **Snowblade a 10 años** mediante **Libor Market Model (LMM)**, numerario bono de la última fecha (N+1), esquema monocurva y cotización **shifted lognormal**.

## Estado
**Fase 0 — Preparación.** El modelo todavía no está implementado ni validado.

## Archivos originales requeridos
Conservar en el repositorio, sin reescritura ni conversión:
- **data/original/2026_Ejercicio.pdf**: enunciado contractual.
- **data/original/2026_Datos.xlsm**: plantilla con la macro VBA cinterpol y todos los datos.

**Integridad:** ambos originales binarios están incorporados en `data/original/`, sin conversiones. Verificar su SHA-256 con `data/original/SHA256SUMS` antes de utilizarlos. docs/ENUNCIADO.md es una transcripción de consulta, no una sustitución del PDF.

## Protocolo de trabajo
1. Auditar archivos de origen, rangos, convenciones y ambigüedades del payoff.
2. Obtener una primera valoración **reproducible** en Python con los aleatorios suministrados, sin inventar datos.
3. Verificar fórmulas, simulación, descuento, cashflows, estadística y resultados.
4. Explicar paso a paso matemáticas e implementación, manteniendo decisiones explícitas.
5. Preparar el Excel y memoria PDF exigidos, consistentes con la solución validada.

**Para iniciar Codex:** leer AGENTS.md, docs/ESTADO.md y docs/ENUNCIADO.md; comprobar los dos originales y ejecutar únicamente la fase solicitada.

## Estructura
- **AGENTS.md**: instrucciones persistentes para Codex.
- **data/original/**: fuentes inmutables.
- **docs/**: enunciado, bitácora, decisiones, validación y resultados.
- **src/**: implementación (pendiente).
- **tests/**: tests (pendiente).
- **entrega/**: Excel y memoria definitivos (pendiente).

Principio de diseño: rigor cuantitativo, trazabilidad y entendimiento humano antes que sofisticación innecesaria.
