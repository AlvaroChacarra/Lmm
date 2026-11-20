# Registro de decisiones

Actualización Fase 0: 2026-11-13, baseline `15359f2`, rama `audit/fase-0-snowblade`.
**No hay decisiones contractuales finales aprobadas.** Las recomendaciones siguientes
permiten implementar escenarios provisionales; no constituyen confirmación del enunciado.
No se eliminan alternativas. Evidencia: [AUDITORIA_INPUTS.md](AUDITORIA_INPUTS.md).

## Hechos verificados / restricciones adoptadas

Originales íntegros frente a SHA256SUMS; PDF y XLSM leídos directamente. Shift=.03,
DT=.5, curva de 70 nodos fechada 26/01/2022, 21 sigmas, A final 20×3 normalizada,
12 000 aleatorios fijos en 200 columnas. CInterPol modo 0 es log-lineal en descuentos.
Originales, orden/signos de PCA y aleatorios se conservan. No precio en Fase 0.

## Hipótesis recomendadas y cuestiones pendientes

| ID | Pregunta | Estado | Recomendación, alternativas y evidencia |
| --- | --- | --- | --- |
| D01 | ¿Intereses anuales acumulados del 4%? | ABIERTA; BASE PROPUESTA | Suma neta de efectivo devengado desde origen, test en cada pago después del cupón completo. Alternativas: suma de tasas, intereses de cada año, media anual desde origen. Ejemplo r=0: cruce base en 6, suma de tasas en 4, test anual de pareja en 8. Falta cuantificar PV en Fase 1. |
| D02 | ¿Tasas anualizadas o importes semestrales? | ABIERTA; BASE PROPUESTA | Tasas c_j anualizadas; pago H delta c_j; recurrencia en tasas. ACT/365 apoya esta lectura, no la prueba. Alternativa: c_j importe semestral; distinguir si Euribor y escalones se devengan también. Sensibilidad sobre mismos paths. |
| D03 | ¿Floor cero? | HECHO NEGATIVO DE FUENTE; BASE PROPUESTA | PDF no lo indica; base sin floor/cap, acumulación neta con cupones negativos. No inferir floor por costumbre comercial. Si se estudia alternativa, separar floor del estado y floor del pago. |
| D04 | ¿Fixing de cada cupón? | ABIERTA; BASE PROPUESTA | Advance: cupón j observa F_(j−1)(t_(j−1)), paga t_j; primeros dos cupones fijos. In arrears y lag no explicitados en fuente. |
| D05 | ¿N+1 y bono terminal? | ABIERTA; MAPA PROPUESTO | H-cal: t0=26/01/2022, t1…t20 pagos semestrales, t21=26/07/2032 auxiliar. F0 fijo, F1…F20 estocásticos. Favorecida por 21 sigmas/20 PCA/20 shocks. No deducible de forma única del PDF. Alternativa terminal t20 deja sigma/paso sobrantes. Producto de descuento j=m…20, incluido F20 al último pago. |
| D06 | ¿CInterPol? | RESUELTA EN CÓDIGO FUENTE; RECONCILIACIÓN EXCEL PENDIENTE | Usar modo 0 log-lineal; bisección y extremos inspeccionados; 70 nodos y 69 puntos medios reproducidos algebraicamente. Modo 1 lineal existe. Python rechazará extrapolación no necesaria; VBA extrapola sin avisar. No se ejecutó Excel/VBA. |
| D07 | ¿Qué cargas/correlación usar? | HECHO VERIFICADO; USO RECOMENDADO | G117:I136 es A final normalizada; usar literalmente y AAᵀ tanto en drift como difusión. No reescalar ni reemplazar PCA. R original es objetivo diagnóstico. Descomposición almacenada aproximada; error max R−AAᵀ=.15350247. |
| D08 | ¿Calendario y tiempo de difusión? | ABIERTA; BASE PROPUESTA | Seis meses calendario desde C2, sin ajuste hábil ni lag; ACT/365 en accrual y h. DT=.5 orienta malla académica pero no coincide exactamente con ACT/365; sensibilidad separada. CSV de 21 intervalos documenta el mapa. |
| D09 | ¿Cómo mapear las 21 volatilidades? | ABIERTA; BASE PROPUESTA | Bajo H-cal: F0 usa F9 sin evolución; F_i usa F(9+i), i=1…20. Sigma constante hasta reset es hipótesis mínima. No hay superficie/calibración para afirmar stripping independiente. |
| D10 | ¿Cupón del evento y exceso del objetivo? | ABIERTA; BASE PROPUESTA | Pagar cupón completo y principal una vez en primer cruce ≥4%; sin cap al exceso. Si no cruza, principal en 20. Separar autocall en 20 y vencimiento natural en reporting. |
| D11 | ¿Esquema numérico inicial? | RECOMENDADO PARA FASE 1 | Log-Euler sobre F+s, drift congelado con estado común anterior y h ACT/365; 20 shocks originales. No implementar/refinar simulación en Fase 0. Validar error de discretización aparte del SE. |

Histórico: al preparar el repositorio D01–D06 estaban abiertas. Fase 0 verifica la
semántica de CInterPol y propone bases explícitas para las demás; no transforma
esas propuestas en decisiones aprobadas. Efectos cuantitativos de precio pendientes.
La fecha y commit exacto de esta actualización se obtienen con:
`git log -1 --format='%H %cs' -- docs/DECISIONES.md`.
