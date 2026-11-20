# Registro de decisiones

Estado vigente tras incorporar las respuestas del profesor y ejecutar la valoración.
Fuente de aclaraciones: [ACLARACIONES_PROFESOR.md](ACLARACIONES_PROFESOR.md).
El histórico anterior se conserva en git; la auditoría Fase 0 sigue como fotografía inicial.

| ID | Pregunta | Estado vigente | Decisión, evidencia y consecuencias |
| --- | --- | --- | --- |
| D01 | ¿Qué acumula el objetivo del 4%? | CONFIRMADA LA MAGNITUD | Intereses efectivos netos desde origen: S_m=sum delta c. No anualizar de nuevo ni sumar tasas. Profesor aporta ejemplo 2%×.5+3%×.5. Test en cada pago es convención operacional adoptada. |
| D02 | ¿Cupones anualizados? | CONFIRMADA | 1% anualizado inicial y ACT/365; recurrencia en tasas anualizadas, pago H delta c. La lectura de 1% efectivo por semestre queda descartada. |
| D03 | ¿Floor y memoria negativa? | CONFIRMADA | No floor; inversor paga cupón negativo, que permanece como base del siguiente. Las hipótesis de floor del pago/estado quedan descartadas. |
| D04 | ¿Qué fixing? | ADOPTADA, NO CONFIRMADA | Advance: r_j=F_(j−1)(t_(j−1)); pago t_j. No lag ni ajuste hábil suministrados. |
| D05 | ¿N+1? | ADOPTADA, NO CONFIRMADA | H-cal: t0=26/01/2022, t20=26/01/2032 último pago, t21=26/07/2032 bono auxiliar. 20 forwards estocásticos F1…F20 y F0 fijo. F20 entra en descuento del pago20, no en su cupón. Terminal10años vale 98.4769 frente a 98.5198 base. |
| D06 | ¿CInterPol? | IMPLEMENTADA, RECÁLCULO EXCEL NO EJECUTADO | Equivalente log-lineal modo0; se rechaza extrapolación no necesaria. Caches/nodos contrastados en Fase0; implementación Python contrastada por referencia escalar. |
| D07 | ¿PCA/covarianza? | IMPLEMENTADA SEGÚN FUENTE | A=G117:I136 literal, orden y signos conservados; A Aᵀ en drift y difusión. Sin nuevo sqrt(lambda), normalización ni sustitución PCA. Descomposición aproximada residual documentada en auditoría. |
| D08 | ¿Fechas/reloj? | ADOPTADA, NO CONFIRMADA | Seis meses calendario desde C2, sin ajuste hábil, h y devengo ACT/365. DT=.5 como sensibilidad de difusión: 98.5294; no cambia devengo ni fechas. |
| D09 | ¿Volas? | ADOPTADA, NO CONFIRMADA | F0 usa F9 sin evolución; F_i usa F(9+i), i=1…20; sigma constante hasta reset. Desplazar a la primera fila para F1: 98.2909. No se afirma stripping a precios externos. |
| D10 | ¿Exceso del objetivo? | ADOPTADA, NO CONFIRMADA | Cupón completo al primer S>=.04; principal una sola vez; sin cruce, principal en20. Recortar cupón al objetivo reduce precio 1.1919 puntos. Convención material que debe acompañar el resultado. |
| D11 | ¿Esquema? | IMPLEMENTADA Y CONTRASTADA | Log-Euler con drift congelado y estado anterior común. Predictor-corrector con mismos shocks: 98.5562 (+.03635). Es control de sensibilidad, no test de convergencia con subpasos. |
| D12 | ¿Estadística y colas? | IMPLEMENTADA | 200 paths originales sin exclusiones/recentrado. SE sobre los 200 PV completos; IC Student aproximado. Cuatro PV negativos son compatibles con cupones sin floor. Diagnóstico sin peor path no es precio alternativo. |
| D13 | ¿Probabilidades/vida media? | IMPLEMENTADA | Frecuencias y vida media bajo Q terminal, no probabilidades físicas. No presentar como pronósticos comerciales. |
| D14 | ¿Entrega Excel? | GENERADA; RECÁLCULO DE APP PENDIENTE | Libro nuevo XLSX sin VBA, fórmulas de estados/flujos y caches de Python. No se convierte el original; lectura posterior reconcilia caches. No se afirma recálculo con Excel/LibreOffice. |

Fuentes numéricas y sensibilidades: [RESULTADOS.md](RESULTADOS.md) y
[outputs/resultados.json](../outputs/resultados.json). La fecha de publicación y commit se
obtienen con `git log -1 --format='%H %cs' -- docs/DECISIONES.md`.
