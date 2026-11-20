# Evidencia de validación — Fase 0

2026-11-13; baseline 15359f2. **No hay motor ni precio validado.**
El estado inicial «ningún test ejecutado» queda sustituido por la evidencia siguiente.

Comando ejecutado: `/tmp/lmm-audit-venv/bin/python scripts/audit_phase0.py`.
Resultado: **22/22 comprobaciones PASS**. Detalle booleano, versiones y cifras en
[evidencia JSON](evidencias/auditoria_fase0.json). SHA256SUMS también PASS para ambos
originales; contraste antes y después en script. VBA extraído, nunca ejecutado. Dos ejecuciones consecutivas produjeron los mismos
SHA-256 para los tres artefactos de evidencia (JSON, CSV, BAS).

| Check | Resultado y límite |
| --- | --- |
| Integridad | PASS, SHA-256 y CRC ZIP; autenticidad externa no acreditada |
| Estructura/fórmulas | PASS, 70 fórmulas de fechas, cachés concordantes |
| Aleatorios | PASS, dimensiones 3×20×200, finitos y etiquetas; distribución solo diagnóstica |
| Curva | PASS, días ordenados, descuentos positivos, origen 1; tipos negativos permitidos |
| CInterPol modo 0 | PASS, traducción algebraica en nodos y puntos medios <1e-14; Excel no ejecutado |
| PCA final | PASS, A=B/||B_fila|| y varianzas unitarias; conserva entradas suministradas |
| PCA exacta del objetivo | NO EXACTA, residual RU−U lambda hasta .03927 y R−AAᵀ hasta .15350 |
| Forwards y bono terminal | PASS identidades estáticas del calendario propuesto; todavía no MC |
| Payoff | PASS diagnóstico r=0, triggers distintos 4/6/8; todavía no tests del motor |
| Originales al terminar | PASS en script; git diff de originales sin cambios |
| Dinámica / sigma=0 / martingalas | PENDIENTE, Fases 1–2 |
| Autocall, principal y SE del motor | PENDIENTE, Fases 1–2 |
| Python vs Excel vs PDF de entrega | PENDIENTE, no se han generado entregas |

El veredicto de avance condicionado está en AUDITORIA_INPUTS.md; estos checks no prueban
normalidad o independencia del RNG ni resuelven las ambigüedades del contrato.
