# Codex — instrucciones listas para copiar

El repositorio ya contiene los originales PDF y XLSM. Se trabaja por fases separadas para reducir errores y mantener bajo control el contexto.

## Prompt 1 — Auditoría inicial (PRIMERA EJECUCIÓN)

> Estamos resolviendo el ejercicio AFI Snowblade / LMM de este repositorio.
>
> **Lee primero `AGENTS.md`, `docs/ESTADO.md`, `docs/DECISIONES.md` y el enunciado PDF original. Examina `2026_Datos.xlsm` sin modificarlo.**
>
> Ejecuta **únicamente la Fase 0 de AGENTS.md**. Quiero una auditoría técnica ejecutable y orientada a despejar riesgos antes de valorar:
>
> 1. Confirma integridad de ambos originales con `sha256sum -c data/original/SHA256SUMS`; lista hojas, rangos, formatos, fórmulas, valores, macros y anomalías relevantes del XLSM. Si necesitas extraer VBA, hazlo sin ejecutarlo.
> 2. Localiza y documenta las entradas precisas (hoja, rango, índice, unidad): curva, plazos, day count, volatilidades, shifted rate, correlación, PCA, 200 trayectorias y convención de los shocks. No asumir dimensiones ni signos porque estén sugeridos en documentación previa: comprobarlos.
> 3. Reconstruye calendario de fijación/devengo/pago de los 20 periodos, forwards iniciales, medida del bono terminal y la dinámica shifted-LMM con drift correcto. Deja señalados los posibles errores de índices y el encaje de PCA.
> 4. Formaliza de manera matemática el cupón recursivo, la cancelación automática y la amortización. Destaca cualquier ambigüedad contractual material: especialmente «intereses anuales acumulados del 4%», su cálculo con ACT/365, cupones negativos y si el cupón se paga en el autocall. Propón una convención principal justificada y, cuando proceda, escenarios alternativos.
> 5. Crea `docs/AUDITORIA_INPUTS.md` con tabla de mapeo de celdas, cronología, fórmulas y riesgos; actualiza `docs/DECISIONES.md` y `docs/ESTADO.md`. Registra lo **verificado**, **inferido** y **no resuelto** por separado.
>
> **Límites:** no implementes aún el motor Monte Carlo ni prepares la entrega. No regeneres los aleatorios, no recalcules PCA para reemplazar la plantilla ni modifiques el XLSM. No inventes cifras o pruebas. Usa scripts pequeños de inspección solo si aportan evidencia.
>
> **Cierre:** ejecuta las verificaciones posibles, haz commit en una rama de trabajo y, si el entorno lo permite, abre PR sin hacer merge automático. Responde con: (a) mapa breve de datos; (b) 3-5 riesgos materiales; (c) hipótesis recomendadas; (d) verificaciones superadas/fallidas; (e) propuesta concreta para Fase 1. No hagas preguntas salvo bloqueos reales.

## Prompt 2 — Primera valoración rápida

> Continúa desde `AGENTS.md`, `docs/ESTADO.md`, `docs/AUDITORIA_INPUTS.md` y `docs/DECISIONES.md`. Ejecuta la **Fase 1**: motor Python de valoración LMM shifted-lognormal bajo numerario terminal, utilizando los factores PCA y exactamente los 200 caminos aleatorios originales. Conecta cada input a hoja/celda y cada output a una fórmula trazable.
>
> Prioriza una primera respuesta cuantitativa **provisional**: precio por 100 nominal, cupones/principal, distribución de cancelación y error estándar/IC condicionado al conjunto de caminos. Incluye tests de invariantes del descuento, escenarios deterministas y cashflows. Si hay ambigüedades relevantes, calcula el precio bajo varias interpretaciones, sin ocultarlas ni seleccionar arbitrariamente una. Registra comandos, resultados y anomalías; deja el código reproducible. No prepares todavía Excel final ni PDF.

## Prompt 3 — Validación independiente

> Relee `AGENTS.md` y el estado. Audita sin dar por bueno el código existente: dinámica y drift terminal, índices, calendarios, shifted lognormal, PCA, shocks y descuento del payoff. Ejecuta tests de límite y escenarios alternativos; cuantifica error MC, discretización y efecto PCA en la medida posible. Escribe evidencia y estado pass/fail en `docs/VALIDACION.md`, actualiza `docs/ESTADO.md` y propone correcciones concretas.

## Prompt 4 — Preparación para defensa

> Basándote exclusivamente en las decisiones y resultados ya validados, explica el ejercicio paso a paso, con intuiciones matemáticas, ejemplos pequeños y mapeo fórmula→código→resultado. Prioriza que el alumno pueda defender oralmente el procedimiento. No escribas todavía una memoria final genérica.

## Prompt 5 — Entrega Excel + memoria

> Tras superar la validación, prepara un Excel de entrega auditable y una memoria PDF académica, clara y concisa. Explica implementación, decisiones y análisis de resultados exigidos por el enunciado. No cambies los originales. Comprueba la reconciliación de cifras, fórmulas y convenciones entre Python, Excel y PDF. Documenta cualquier limitación y guarda los entregables en `entrega/`.

## Para abrir un hilo nuevo

> Lee `AGENTS.md`, `docs/ESTADO.md` y la última validación; revisa el historial reciente y continúa desde la fase pendiente sin repetir trabajo validado ni reinterpretar decisiones cerradas.
