# AGENTS.md — Contrato operativo para Codex

## Misión
Resolver el ejercicio AFI de valoración Monte Carlo del Snowblade bajo Libor Market Model (LMM) **con las entradas originales**, y producir:
1. Una **valoración numérica correcta, reproducible y auditada**.
2. Un **Excel de entrega** con la implementación y cálculos interpretables.
3. Una **memoria PDF** que explique implementación, decisiones y análisis de resultados.
4. Un desarrollo que permita al estudiante **entender y defender oralmente** cada paso.

Idioma de informes y conversaciones: español; código, nombres de funciones y tests pueden estar en inglés. Redacción académica clara y natural, sin texto de relleno, afirmaciones no verificadas ni aparente seguridad ante dudas reales.

## Punto de entrada vigente
Leer `docs/ESTADO.md`, `docs/DECISIONES.md` y `docs/ACLARACIONES_PROFESOR.md`.
Resultados, implementación y reproducción: `docs/RESULTADOS.md`; evidencia: `docs/VALIDACION.md`.
La Fase 0 está concluida. No reabrir las condiciones confirmadas del profesor por
ambigüedades del PDF anteriores a sus respuestas.

## Fuentes de verdad (orden)
1. Aclaraciones del profesor documentadas en docs/ACLARACIONES_PROFESOR.md, que complementan el PDF; en su ámbito resuelven sus ambigüedades.
2. data/original/2026_Ejercicio.pdf
3. data/original/2026_Datos.xlsm, incluidas tablas, numerario, aleatorios, PCA y referencia a cinterpol.
4. docs/DECISIONES.md para opciones aprobadas.
5. Código y tests ya validados.

Si faltan los originales, **no simular que están disponibles** ni fabricar cifras. docs/ENUNCIADO.md es una transcripción auxiliar. **Nunca modificar los originales**; no ejecutar VBA no revisado ni sobrescribir/convertir el XLSM (podría perder cinterpol, fórmulas y metadatos).

## Contrato cuantitativo
- Instrumento: Snowblade; 10 años; 20 periodos semestrales; referencia Euribor 6M; base ACT/365.
- Modelo: LMM monocurva, cotización shifted lognormal; usar el **shift = 0.03** indicado en plantilla, sujeto a comprobación en la fuente.
- Numerario: bono de la última fecha disponible (N+1), **no** cuenta monetaria ni bono de cada cupón.
- Inputs: curva de descuentos, volatilidades, correlaciones y las **3 primeras componentes principales precomputadas**; no recalcular PCA ni sustituir aleatorios salvo como validación independiente.
- Aleatorios: en hoja Aleatorios, 200 simulaciones en columnas C:GT, organizadas en tres bloques de 20 periodos (V1, V2 y V3); verificar orientación, mapeo, celdas y significado de cada bloque antes de usar. **No regenerar ni aumentar el número de paths** en el resultado base.
- La hoja Correlaciones contiene la matriz y su descomposición; la hoja Curva y volas contiene el term structure, caplet vols y parámetros. Confirmar índices y correspondencias temporal/madurez. No tratar como iguales maturities, resets y fechas de pago.
- Segunda ronda del profesor: el primer tipo es spot, sin sigma; el primer forward futuro usa la primera volatilidad (F9). Usar F9:F28 para F1…F20 y preservar la fila extra F29 sin aplicarla al spot. Partición de difusión h=0.5 (30/360); mantener ACT/365 en devengos. Fixing advance confirmado.
- Calcular forwards iniciales coherentes con los factores de descuento interpolados, y evolucionar solo los tipos vivos.
- Modelizar exactamente la dinámica desplazada bajo la medida del bono terminal, incluido su drift dependiente de forwards y de la correlación. Diferenciar volatilidad marginal, carga PCA y difusión correlacionada; revisar escalados sqrt(dt), shift y signos.
- Para cada pago, valorar la **expectativa del cashflow dividido por el numerario terminal en su fecha** y multiplicar por el numerario inicial. Auditar los índices del producto de forwards (posible fuente de errores off-by-one).
- Cupones recursivos: periodos 1 y 2 al 1%; 3 y 4 cupón anterior menos Euribor 6M; 5-8 +1%, 9-12 +1.25%, 13-16 +1.50%, 17-20 +2%, siempre menos Euribor 6M. El profesor confirma tasas anualizadas, ACT/365 y ausencia de floor: el inversor paga el cupón negativo y la recursión conserva ese valor. No reintroducir alternativas ya descartadas.
- Cancelación y amortización a la par al alcanzar intereses efectivos netos acumulados del 4%, confirmado por el profesor. Aplicar devengo una sola vez; no anualizar el acumulado. El cupón completo sigue como lectura de trabajo: el segundo «Correcto» del profesor no selecciona expresamente entre pago completo y recorte. Registrar ese límite, sin inventar una confirmación inequívoca. Si no ocurre, amortizar a la par en periodo 20.
- El enunciado no establece por sí solo todas las convenciones necesarias. **No ocultar ambigüedades**: realizar escenarios interpretativos cuando cambien resultados y recomendar una interpretación justificada. Registrar la elegida en DECISIONES.md.

## Fases y puntos de parada
**Fase 0 — Auditoría (primera tarea recomendada):**
- Comprobar integridad/lectura de los dos originales, macros, estructura de hojas, dimensiones, fórmulas relevantes y cinterpol.
- Construir mapa preciso de celdas, inputs y convenciones en docs/AUDITORIA_INPUTS.md.
- Formalizar payoff con línea temporal t0..tN+1, reset/cupón/amortización, con ejemplos deterministas.
- Registrar ambigüedades materiales y cómo afectan al precio.
- **Parar y resumir hallazgos.** No generar un precio final en esta fase salvo petición.

**Fase 1 — Primera solución rápida y sólida:**
- Implementar Python modular en src/: lectura de inputs, interpolación, forwards iniciales, factores PCA, dinámica LMM terminal, payoff y discounting.
- Usar exclusivamente las 200 paths del Excel; determinismo exacto entre ejecuciones.
- Reportar precio por 100 de nominal (si la interpretación contractual lo permite), componentes cupón/principal, probabilidad de autocall por fecha, duración esperada, error estándar e IC Monte Carlo, con límites de precisión dados 200 paths.
- Incorporar tests en tests/; mostrar resultado **provisional** hasta superar validaciones.

**Fase 2 — Auditoría:**
- Comprobar identidad P(0,T) / forwards, signos y escalado de drift, dimensions/covarianzas PCA, estabilidad shifted rates, accrual ACT/365, descuento terminal, cashflows y amortización.
- Tests de escenarios deterministas (incluida sigma=0), ausencia de autocall y autocall inmediato, variaciones de parámetros y reconciliación independiente.
- Distinguir error estadístico, error de discretización, aproximación PCA y ambigüedad contractual. No emitir cifras de precisión espuria.
- Mantener docs/VALIDACION.md con resultados reales, comandos y estados pass/fail; **no dar tests por pasados sin ejecutarlos**.

**Fase 3 — Aprendizaje / explicación:**
- En iteraciones cortas explicar la medida terminal, desplazamiento, PCA, SDE, drift, MC, payoff y PV, con baby steps y ejemplos, sin perder rigor.
- Documentar por qué se adopta o descarta cada decisión. Evitar narrar linealmente el código.

**Fase 4 — Entrega:**
- Excel legible: inputs originales intactos, hoja de supuestos, mapa de cálculo, paths/cashflows, checks, tablas y gráficos útiles; **preservar estructura y macros del original si se trabaja sobre XLSM**, o crear un libro nuevo que enlace claramente las entradas sin afirmar que incorpora VBA si no lo hace.
- Memoria PDF: resumen ejecutivo; contrato y convenciones; formulación LMM; calibración/inputs; simulación; payoff; metodología de descuento; validación; resultados; limitaciones y conclusiones. Incluir fórmulas y unidades, no plantillas genéricas.
- Reconciliar exactamente precio y métricas entre Python, Excel y memoria; explicar diferencias si son inherentes a otro motor de cálculo.

## Reglas de ingeniería y contexto
- Codex debe **leer AGENTS.md al comienzo** de cada nueva tarea.
- No reescribir código validado sin tests; commits pequeños y descriptivos; no subir archivos temporales, secretos, cachés o entornos virtuales.
- Documentos persistentes: docs/ESTADO.md (qué existe/qué sigue), docs/DECISIONES.md (supuestos y porqués), docs/VALIDACION.md (evidencia cuantitativa), docs/AUDITORIA_INPUTS.md (fuentes).
- Actualizar ESTADO.md al finalizar cada fase con comandos de reproducción y tareas pendientes. Esto sustituye depender de la memoria del chat.
- No usar 'sin cambios' o 'comprobado' sin evidencias. No solicitar al usuario múltiples confirmaciones triviales; proponer opciones, cuantificar diferencias y señalar únicamente decisiones materialmente ambiguas.
- Preferir numpy/scipy y tests a soluciones Excel excesivamente complejas. Excel es el artefacto auditable exigido, no el lugar donde esconder una caja negra.
- Mantener todo en español salvo identificadores; comunicar primero resultados y problemas concretos, luego detalles.

## Comprobaciones y documentación al cambiar el motor
Ejecutar los comandos de `docs/RESULTADOS.md`; como mínimo, tests y contraste escalar.
Actualizar decisiones, resultados, estado y validación cuando cambie una verdad documentada.
Regenerar entregas si cambian cifras; no afirmar recálculo Excel sin ejecutarlo.
