# LMM — AFI | Valoración Monte Carlo de un Snowblade

Repositorio de trabajo para resolver, validar y explicar la valoración de un **Snowblade a 10 años** bajo **Libor Market Model (LMM)**, en esquema monocurva, cotización **shifted lognormal** y numerario bono terminal \(T_{N+1}\).

## Solución actual

**98.26916479 por 100 de nominal**, con SE Monte Carlo **2.74535035** e IC 95% aproximado
**[92.85545320, 103.68287639]**, usando los 200 paths originales. Sin floor y con memoria
negativa, objetivo de intereses efectivos del 4% y tasas anualizadas ACT/365, según
[aclaraciones del profesor](docs/ACLARACIONES_PROFESOR.md).

- [Resultados y límites](docs/RESULTADOS.md), [estado](docs/ESTADO.md),
  [decisiones](docs/DECISIONES.md) y [validación](docs/VALIDACION.md).
- [Excel con implementación](entrega/Snowblade_LMM.xlsx) y [memoria PDF](entrega/Memoria_Snowblade.pdf).
- [Auditoría inicial](docs/AUDITORIA_INPUTS.md), conservada como fotografía histórica.

El precio depende de convenciones residuales documentadas. El IC es orientativo con
200 paths y cola negativa; no incluye errores de PCA, malla o interpretación residual.
Segunda ronda: fixing advance confirmado; difusión h=.5, primera sigma para F1 y spot
inicial sin sigma. Cupón completo sigue como lectura de trabajo de un «Correcto» ambiguo.
El libro nuevo se ha recalculado con LibreOffice y control centinela; Microsoft Excel no probado.

```sh
python -m pip install -r requirements.txt
python scripts/value_snowblade.py
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/validate_solution.py
python scripts/build_delivery.py
python scripts/recalculate_delivery.py
python scripts/check_delivery.py
```

El PDF requiere fuentes DejaVu y el recálculo requiere soffice; ver RESULTADOS.md.
Para retomar con Codex, leer AGENTS.md y docs/ESTADO.md. No repetir fases concluidas.

## Fuentes inmutables
- [`data/original/2026_Ejercicio.pdf`](data/original/2026_Ejercicio.pdf): enunciado contractual.
- [`data/original/2026_Datos.xlsm`](data/original/2026_Datos.xlsm): datos, plantilla Excel, aleatorios, PCA y macro VBA `cinterpol`.
- [`data/original/SHA256SUMS`](data/original/SHA256SUMS): verificación de integridad; ejecutar `(cd data/original && sha256sum -c SHA256SUMS)` desde la raíz.

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

**Estado actual:** motor y entregas generados; 19 tests y reconciliación escalar superados.
Recálculo LibreOffice reproducible superado. Se mantiene explícita la lectura del exceso
y los supuestos de calendario y volatilidad constante.
