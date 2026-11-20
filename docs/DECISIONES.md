# Registro de decisiones

Estado vigente tras la confirmación final de opción A: cupón íntegro al autocall,
fixing advance, primera sigma para el primer forward futuro y h=.5. Las bases anteriores se conservan en git y como
contrafactuales de trazabilidad, no como alternativas igualmente abiertas.
Fuente de aclaraciones: [ACLARACIONES_PROFESOR.md](ACLARACIONES_PROFESOR.md).
El histórico anterior se conserva en git; la auditoría Fase 0 sigue como fotografía inicial.

| ID | Pregunta | Estado vigente | Decisión, evidencia y consecuencias |
| --- | --- | --- | --- |
| D01 | ¿Qué acumula el objetivo del 4%? | CONFIRMADA LA MAGNITUD | Intereses efectivos netos desde origen: S_m=sum delta c. No anualizar de nuevo ni sumar tasas. Profesor aporta ejemplo 2%×.5+3%×.5. Test en cada pago es convención operacional adoptada. |
| D02 | ¿Cupones anualizados? | CONFIRMADA | 1% anualizado inicial y ACT/365; recurrencia en tasas anualizadas, pago H delta c. La lectura de 1% efectivo por semestre queda descartada. |
| D03 | ¿Floor y memoria negativa? | CONFIRMADA | No floor; inversor paga cupón negativo, que permanece como base del siguiente. Las hipótesis de floor del pago/estado quedan descartadas. |
| D04 | ¿Qué fixing? | CONFIRMADA EN SEGUNDA RONDA | Advance: r_j=F_(j−1)(t_(j−1)); pago t_j. «Si, lo habeis hecho correctamente». No reabrir arrears como interpretación contractual vigente. |
| D05 | ¿N+1? | ELECCIÓN ADMITIDA | Profesor: «En realidad da igual». Se conserva t21=26/07/2032 frente a último pago t20=26/01/2032. Elección de numerario con drift/descuento consistentes; no exige igualdad muestral bajo medidas distintas. F20 sigue en el descuento final. |
| D06 | ¿CInterPol? | EQUIVALENTE IMPLEMENTADO; VBA NO EJECUTADO | Equivalente log-lineal modo0; se rechaza extrapolación no necesaria. Caches/nodos contrastados en Fase0; implementación Python contrastada por referencia escalar. |
| D07 | ¿PCA/covarianza? | IMPLEMENTADA SEGÚN FUENTE | A=G117:I136 literal, orden y signos conservados; A Aᵀ en drift y difusión. Sin nuevo sqrt(lambda), normalización ni sustitución PCA. Descomposición aproximada residual documentada en auditoría. |
| D08 | ¿Fechas/reloj? | h=.5 CONFIRMADO; CALENDARIO ADOPTADO | Partición de difusión semestral 30/360, h=.5, según segunda respuesta. Cupones y denominadores de forwards devengan ACT/365. Aniversarios desde C2 sin ajuste/lag son supuesto de calendario. No duplicar ni confundir los dos relojes. |
| D09 | ¿Volas? | MAPA CORREGIDO POR PROFESOR | El tipo inicial es spot, sin sigma. Primer forward futuro F1 usa F9; F_i usa F(8+i), i=1…20, hasta F28. F29 extra no usada, preservada. Sigma constante hasta reset sigue como supuesto mínimo, no confirmación literal ni stripping externo. |
| D10 | ¿Exceso del objetivo? | CONFIRMADA — OPCIÓN A | El profesor confirma expresamente opción A y que no se capa el último cupón. Cupón íntegro y principal en la liquidación del evento. Ejemplo 3.80+.60: pago100.60 e intereses4.40. Recorte descartado para el contrato; solo contrafactual de trazabilidad. Caso base y precio98.26916479 ya correctos. |
| D11 | ¿Esquema? | IMPLEMENTADA Y CONTRASTADA | Log-Euler con drift congelado y estado anterior común. Predictor-corrector con mismos shocks publicado como sensibilidad actual. Es control de sensibilidad, no test de convergencia con subpasos. |
| D12 | ¿Estadística y colas? | IMPLEMENTADA | 200 paths originales sin exclusiones/recentrado. SE sobre los 200 PV completos; IC Student aproximado. Los cinco PV negativos actuales son compatibles con cupones sin floor. Diagnóstico sin peor path no es precio alternativo. |
| D13 | ¿Probabilidades/vida media? | IMPLEMENTADA | Frecuencias y vida media bajo Q terminal, no probabilidades físicas. No presentar como pronósticos comerciales. |
| D14 | ¿Entrega Excel? | RECÁLCULO EXTERNO REPRODUCIBLE | Libro nuevo XLSX sin VBA. scripts/recalculate_delivery.py fuerza LibreOffice con caches centinela y sigma=0 en copias; evidencia en outputs/recalculo_validacion.json. Microsoft Excel no probado; original intacto. |

Fuentes numéricas y sensibilidades: [RESULTADOS.md](RESULTADOS.md) y
[outputs/resultados.json](../outputs/resultados.json). La fecha de publicación y commit se
obtienen con `git log -1 --format='%H %cs' -- docs/DECISIONES.md`.
