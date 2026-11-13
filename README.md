# LMM — AFI | Valoración Monte Carlo de un Snowblade

Repositorio de trabajo para resolver, validar y explicar la valoración de un **Snowblade a 10 años** bajo **Libor Market Model (LMM)**, en esquema monocurva, cotización **shifted lognormal** y numerario bono terminal \(T_{N+1}\).

## Cómo empezar en Codex

1. Seleccionar este repositorio (`AlvaroChacarra/Lmm`) y partir de `main`.
2. Abrir [`docs/CODEX_START.md`](docs/CODEX_START.md), copiar el **prompt 1 (Fase 0)** y ejecutarlo.
3. Revisar el mapa de inputs y las ambigüedades detectadas antes de pasar a la primera simulación.
4. En cada nuevo hilo, pedir a Codex que lea `AGENTS.md` y `docs/ESTADO.md` para retomar el trabajo.

**La primera tarea no es generar un precio ni el Excel final:** consiste en confirmar que los inputs, las convenciones, la dinámica LMM y el payoff están definidos sin errores.

## Fuentes inmutables
- [`data/original/2026_Ejercicio.pdf`](data/original/2026_Ejercicio.pdf): enunciado contractual.
- [`data/original/2026_Datos.xlsm`](data/original/2026_Datos.xlsm): datos, plantilla Excel, aleatorios, PCA y macro VBA `cinterpol`.
- [`data/original/SHA256SUMS`](data/original/SHA256SUMS): verificación de integridad; ejecutar `sha256sum -c data/original/SHA256SUMS` desde la raíz.

**No editar ni convertir las fuentes originales.** `docs/ENUNCIADO.md` es solo una transcripción auxiliar.

## Estructura de trabajo
| Ruta | Propósito |
| --- | --- |
| `AGENTS.md` | Contrato persistente, reglas matemáticas y fases para Codex |
| `docs/CODEX_START.md` | Prompts preparados para cada fase |
| `docs/ESTADO.md` | Punto de control para retomar en conversaciones nuevas |
| `docs/DECISIONES.md` | Supuestos y alternativas contractuales |
| `docs/VALIDACION.md` | Evidencias reales de tests y reconciliación |
| `docs/ENUNCIADO.md` | Síntesis del enunciado |
| `data/original/` | Archivos originales verificados |
| `src/` | Código de valoración, después de la auditoría |
| `tests/` | Tests unitarios y cuantitativos |
| `entrega/` | Excel final y memoria PDF |

## Hitos
**Fase 0:** auditoría contractual y de datos → **Fase 1:** baseline reproducible Python con aleatorios originales → **Fase 2:** verificación independiente → **Fase 3:** explicación pedagógica → **Fase 4:** Excel y PDF coherentes con los resultados.

**Estado actual:** fase 0 pendiente. No hay precio calculado ni tests ejecutados.
