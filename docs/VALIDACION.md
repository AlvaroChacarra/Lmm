# Plan y evidencia de validación

**Ningún test figura como ejecutado todavía.**

| Check | Estado | Criterio |
| --- | --- | --- |
| Input y checksum de archivos | PENDIENTE | Dos fuentes originales presentes y legibles |
| Curva e interpolación | PENDIENTE | Reproducción de P(0,T), fechas y forwards |
| PCA y shock factors | PENDIENTE | Cargas y unidades compatibles; comparación matriz objetivo/aproximada |
| Shifted lognormal | PENDIENTE | Convención L+shift consistente, dinámica y drift terminal |
| Malla temporal | PENDIENTE | Tenores/fixings/pagos y ACT/365 sin desfases |
| Numerario y descuento | PENDIENTE | P(0,T_N+1) E_QT[CF / P(t,T_N+1)] |
| Payoff Snowblade | PENDIENTE | Ejemplos cerrados y cancelación sin doble pago |
| Escenario sigma=0 | PENDIENTE | Comparación MC frente a determinista |
| Probabilidad autocall | PENDIENTE | Suma de frecuencias y supervivencia = 1 |
| Error estándar | PENDIENTE | Calculado con exactamente los 200 paths suministrados |
| Python vs Excel vs PDF | PENDIENTE | Cifras, convenciones y formato reconciliados |

Añadir salidas verificables (comandos, números y logs) a medida que se ejecuten. Las diferencias por discretización/MC/PCA deben distinguirse explícitamente.
