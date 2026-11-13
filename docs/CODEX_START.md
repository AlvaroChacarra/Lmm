# Prompts de inicio para Codex

## 1. Primera ejecución — Auditoría (recomendada)
Lee AGENTS.md, docs/ESTADO.md, docs/ENUNCIADO.md y los dos archivos originales de data/original. Comprueba antes sus checksums frente a SHA256SUMS. Ejecuta **únicamente la Fase 0**: mapa exhaustivo de inputs/hojas/celdas/macros, calendario, 200 paths, 3 factores PCA, definición contractual del Snowblade y controversias interpretativas. Genera docs/AUDITORIA_INPUTS.md, actualiza ESTADO.md y DECISIONES.md. No valores todavía el instrumento ni fabriques supuestos. Haz un commit y dame un resumen ejecutivo de los riesgos materiales y el siguiente paso.

## 2. Primera valoración cuantitativa
Con la auditoría revisada, implementa Fase 1 de AGENTS.md: motor Python LMM bajo medida terminal y shifted lognormal, con aleatorios y componentes principales **exactamente** del Excel. Construye tests mínimos de curva, mapeo de shocks, numerario, payoff y autocall. Produce precio provisional, desglose, tabla autocall y error MC. Actualiza documentación y haz commit. Si hay ambigüedades contractuales relevantes, cuantifica escenarios alternativos antes de fijar un precio único.

## 3. Validación independiente
Audita los cálculos a fondo sin asumir que el código es correcto. Verifica drift, índices, medidas, ACT/365, correlaciones PCA, cashflows, stop event y amortización. Ejecuta tests y documenta evidencias reales, anomalías, sensibilidad y límites. No pases a entrega si hay fallos críticos.

## 4. Explicación y defensa
Produce una explicación progresiva, con ejemplos pequeños, de cada paso matemático y cuantitativo. Conecta la derivación del modelo con el código y la valoración. Señala decisiones defensables y preguntas probables del corrector; no conviertas esto aún en una memoria final.

## 5. Excel + PDF
Con el modelo validado, crea un Excel auditable y una memoria PDF de estilo académico humano, sin inflación de texto. Todos los precios, convenciones, fórmulas y fechas deben reconciliarse con Python. Conserva los originales intactos; actualiza docs/ESTADO.md y entrega archivos finales en entrega/.

## Reglas de contexto
Al abrir un chat nuevo, escribe: «Lee AGENTS.md y docs/ESTADO.md, inspecciona el repo y continúa desde la fase pendiente; no repitas tareas concluidas ni vuelvas a decidir cuestiones cerradas».
