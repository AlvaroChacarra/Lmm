# Estado de proyecto — actualizar tras cada sesión

**Estado:** preparado para arrancar auditoría, sin precio calculado.
**Fecha de inicio:** 2026-11-13.
**Última fase concluida:** preparación del repositorio.
**Siguiente fase:** Fase 0 de AGENTS.md.

## Hechos comprobados en los adjuntos del chat
- El PDF tiene 2 páginas y exige Excel + memoria PDF.
- El XLSM original tiene tres hojas: **Aleatorios**, **Correlaciones**, **Curva y volas**.
- El archivo contiene **VBA** (macro cinterpol). Hay que conservar el XLSM original.
- Aleatorios: **200** simulaciones (columnas C:GT), tres bloques de 20 filas (V1/V2/V3).
- Correlaciones: matriz para **20** plazos y componentes principales precomputadas.
- Fracción de varianza explicada acumulada en 3 componentes en la plantilla: **0.9235035014404246** (dato de la hoja; comprobar de nuevo al cargar).
- En Curva y volas figura **shift = 0.03**, **DT(años) = 0.5** y volatilidades por periodo. Confirmar la utilización correcta de DT y de ACT/365.
- **Los dos binarios originales están versionados en `data/original/`.** Sus SHA-256 coinciden con `SHA256SUMS`. Antes del cálculo, verificar que siguen íntegros en el checkout.

## Entregables
| Entregable | Estado |
| --- | --- |
| Auditoría detallada de datos, supuestos y payoff | Pendiente |
| Motor Monte Carlo | Pendiente |
| Tests y validación independiente | Pendiente |
| Precio, desglose, prob. autocall y error MC | Pendiente |
| Excel de entrega | Pendiente |
| Memoria PDF | Pendiente |

## Formato del cierre de cada fase
Fecha; commit; archivos modificados; comando de reproducción; resultados medidos; ambigüedades; riesgos; **siguiente paso concreto**. Nunca reemplazar los resultados históricos por afirmaciones sin soporte.
