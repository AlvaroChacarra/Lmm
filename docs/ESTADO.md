# Estado de proyecto

**Fecha:** 2026-11-13. **Última fase concluida:** Fase 0, auditoría cuantitativa.
**Estado:** inputs inspeccionados y formulación documentada; sin precio calculado.
**Siguiente fase:** Fase 1, primera valoración provisional por escenarios.
Baseline revisado: `15359f2`. Rama: `audit/fase-0-snowblade`.
Commit de esta fase: consultar `git log -1 --format='%H %cs' -- docs/ESTADO.md`.

## Completado y verificado

- SHA-256 de PDF/XLSM coincide con manifiesto antes y después; no se guardó el XLSM.
- PDF original de dos páginas leído; XLSM inspeccionado en modo fórmula y caché y como ZIP/XML.
- Tres hojas, 70 fórmulas de fechas y sus cachés, errores, metadatos, rangos y VBA extraído
  estáticamente; CInterPol es log-lineal por defecto. Ninguna macro ejecutada.
- 70 nodos positivos; 21 sigmas y shift .03. 200 paths con tres bloques de 20 shocks.
- PCA final normalizada verificada, sin recalcular ni sustituir datos; descomposición
  aproximada detectada. Diferencia máxima R−AAᵀ=.15350247.
- Calendario **recomendado**, no contractual, de 20 pagos más semestre terminal auxiliar;
  21 forwards iniciales y correspondencias de índices en CSV.
- Drift shifted bajo medida terminal, producto de descuento y payoff formalizados;
  ejemplo r=0 muestra cancelaciones en periodos 4/6/8 según lectura del trigger.
- Script de auditoría ejecutado: 22 comprobaciones superadas. No son validación de un motor.

## Hipótesis y pendientes materiales

La fuente no define de forma única unidades del cupón, trigger anual acumulado,
fixing, fechas ajustadas, malla ni correspondencia exacta del numerario. Base propuesta:
tasas anualizadas, sin floor, objetivo efectivo neto desde origen, pago completo del evento,
advance, calendario desde 26/01/2022 con terminal 26/07/2032, sigmas constantes.
D01–D11 registran qué es hecho, propuesta y pregunta abierta. Falta sensibilidad de precio.
El SE futuro sobre 200 paths no incluirá incertidumbre contractual, PCA o discretización.

## Entregables

| Entregable | Estado |
| --- | --- |
| Auditoría de inputs y formulación | Completada: AUDITORIA_INPUTS.md |
| Evidencia reproducible | Script, JSON, CSV y fuente CInterPol extraída |
| Decisiones contractuales finales | Pendientes; bases y alternativas documentadas |
| Motor Monte Carlo | No implementado (fuera de Fase 0) |
| Tests del motor / validación independiente | Pendientes |
| Precio y métricas de 200 paths | Pendientes |
| Excel y PDF de entrega | Pendientes (no generados) |

## Reproducción

Desde la raíz, comandos completos y dependencias en AUDITORIA_INPUTS.md:

```sh
(cd data/original && sha256sum -c SHA256SUMS)
/tmp/lmm-audit-venv/bin/python scripts/audit_phase0.py
git diff --exit-code -- data/original
```

Archivos de esta fase: `scripts/audit_phase0.py`, `scripts/requirements-audit.txt`,
`docs/AUDITORIA_INPUTS.md`, `docs/DECISIONES.md`, `docs/ESTADO.md`, `docs/VALIDACION.md`,
`docs/evidencias/{auditoria_fase0.json,calendario_recomendado.csv,cinterpol_fuente.bas}`.

Siguiente paso concreto (sin ejecutarlo en esta fase): lector de inputs, mapa H-cal,
log-Euler terminal con A original y AAᵀ, payoff parametrizado y descuento terminal;
validar sigma=0, índices, principal único y martingalas; reportar precio provisional
por 100, desglose, autocall/duración y SE/IC con exactamente los 200 paths. Comparar
primero las interpretaciones D01/D02 usando idénticas trayectorias.
