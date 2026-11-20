# Estado del proyecto

**Estado:** solución numérica y entregas generadas con las aclaraciones del profesor.
**Resultado:** 98.51983210 por 100; SE 2.63848960; IC 95% aproximado [93.31684526,103.72281893].
**Últimas fases ejecutadas:** Fase 1 (motor), comprobaciones de Fase 2 y generación de
Excel/PDF de Fase 4; explicación técnica en RESULTADOS y memoria. La Fase 3 de tutoría
interactiva no se ha ejecutado ni se impone como condición para entregar.
**Estado de confianza:** ÁMBAR por 200 paths con cola asimétrica y convenciones residuales.

Leer [RESULTADOS.md](RESULTADOS.md) para resultados y comandos, [DECISIONES.md](DECISIONES.md)
para convenciones y [VALIDACION.md](VALIDACION.md) para evidencias. La auditoría inicial
[AUDITORIA_INPUTS.md](AUDITORIA_INPUTS.md) queda como histórico de Fase 0.

## Hechos comprobados

- SHA-256 de originales conservados. Los 200 paths y las cargas PCA suministradas se usan
  literalmente. No se ejecuta VBA ni se sobrescribe/convierte el XLSM.
- Condiciones confirmadas: [ACLARACIONES_PROFESOR.md](ACLARACIONES_PROFESOR.md): tasas
  anualizadas ACT/365, sin floor, memoria negativa y objetivo efectivo acumulado.
- Motor `src/lmm/`: lectura, interpolación, calendario, LMM terminal, payoff y PV.
- 17 tests superados; referencia escalar de los 200 paths, diferencia máxima PV 2.28e-13;
  sigma=0 coincide con descuento directo (7.11e-14); 230 diagnósticos de bonos dentro de 5SE.
- 185 autocalls, 15 vencimientos sin autocall, 29 paths con algún cupón negativo.
- Excel nuevo con fórmulas y caches; memoria PDF de 5 páginas; CSV/JSON reproducibles.
  No se ha ejecutado recálculo del XLSX con una aplicación Excel.

## Pendientes y límites

- No confirmados por el profesor: fechas/terminal, mapa sigma, fixing y pago completo
  frente a recorte al objetivo. Convenciones adoptadas y sensibilidades publicadas.
- El SE no mide riesgo de PCA, parametrización ni discretización. El IC es aproximado,
  con cobertura no garantizada ante la cola negativa de una muestra de 200 paths.
- El contraste escalar es otra implementación en el mismo workspace, no revisión por
  un agente externo ni auditoría independiente de mercado/calibración.
- Antes de entrega académica definitiva: comprobar recálculo del XLSX en la aplicación
  del receptor y, si se consigue, confirmar tratamiento del exceso del objetivo.

## Operación y publicación

Rama `valuation/snowblade-confirmado`, basada en `c98855c` (auditoría, PR #2).
No se fusionan PR automáticamente. El commit vigente se consulta con
`git log -1 --format='%H %cs' -- docs/ESTADO.md`.

```sh
python scripts/value_snowblade.py
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/validate_solution.py
python scripts/build_delivery.py
python scripts/check_delivery.py
(cd data/original && sha256sum -c SHA256SUMS)
```

No hace falta repetir Fase 0 para retomar. Próximo trabajo material: recálculo del libro
en Excel y resolución de la convención de exceso, sin reabrir D01–D03 ya confirmadas.
