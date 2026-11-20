# Estado del proyecto

**Estado:** confirmación final del profesor incorporada; resolución académica validada.
Opción A (cupón íntegro sin recorte) confirmada. Precio y 200 PV sin cambios.
**Precio actualizado:** 98.26916479 por 100; SE 2.74535035;
IC 95% aproximado [92.85545320,103.68287639]. El 98.51983210 anterior corresponde a
las hipótesis previas de reloj ACT/365 y primera sigma asignada al spot; queda supersedido.

Leer [ACLARACIONES_PROFESOR.md](ACLARACIONES_PROFESOR.md),
[DECISIONES.md](DECISIONES.md), [RESULTADOS.md](RESULTADOS.md) y
[VALIDACION.md](VALIDACION.md). La auditoría Fase 0 es histórica; la auditoría multiagente
de 63a681f valida la formulación anterior, no certifica por sí sola estos nuevos parámetros.

## Condiciones vigentes tras todas las respuestas

- Fixing al inicio confirmado; se conserva advance.
- Partición de difusión h=.5 (30/360), manteniendo ACT/365 del cupón y forwards.
- El tipo inicial es spot, sin sigma. F1 usa primera volatilidad F9; F20 usa F28.
  F29 extra queda preservada y sin usar; ya no se asigna una sigma al spot.
- Se conserva bono terminal auxiliar a 10,5 años: el profesor permite la elección de
  numerario. Drift y descuento se mantienen coherentes; no se promete igualdad muestral.
- La respuesta final selecciona expresamente **opción A**: cupón completo más principal
  en autocancelación. La duda del «Correcto» queda cerrada; recorte solo contrafactual.

## Evidencia actual

- Originales íntegros; 200 paths y PCA sin sustitución, normalización o recentrado.
- 19 tests PASS; referencia escalar con diferencia máxima PV 2.84e-13.
- Fixture adicional de la opción A: 3.80 acumulados + cupón .60 => pago100.60 e
  intereses4.40; sin pagos posteriores. PV y flujos originales idénticos a b5b6b95.
- Sigma=0 coincide con descuento directo; 230 controles de bonos y 60 caplets Black
  superan las tolerancias MC. No se afirma convergencia temporal ni IC de cobertura exacta.
- 185 autocalls, 15 vencimientos sin autocall; 29 paths con cupón negativo y 5 con PV negativo.
- Excel/PDF regenerados. Script de recálculo LibreOffice con centinelas y sigma=0
  integrado en el repositorio; evidencia actual en outputs/recalculo_validacion.json.
  Microsoft Excel no probado. La generación no sobrescribe los originales.

## Límites restantes

Calendario de aniversarios sin ajuste/lag y sigma constante hasta reset son supuestos
mínimos; esa parte de la pregunta no recibió confirmación literal. Fixing y tratamiento del exceso están confirmados; no queda una consulta contractual
material pendiente para este ejercicio. No se confunde ese cierre con exactitud
estadística ni se atribuye confirmación literal a cada detalle de parametrización. La cola y n=200 limitan precisión; SE no incluye modelo/PCA.

## Reproducir y publicar

Rama `valuation/profesor-spot-forward`, basada en 63a681f. Sin merge automático.
Commit vigente: `git log -1 --format='%H %cs' -- docs/ESTADO.md`.

```sh
python scripts/value_snowblade.py
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/validate_solution.py
python scripts/build_delivery.py
python scripts/recalculate_delivery.py
python scripts/check_delivery.py
(cd data/original && sha256sum -c SHA256SUMS)
```

Fases de cálculo y entrega ejecutadas; tutoría interactiva pendiente solo si se solicita.
No reiniciar Fase 0 ni reabrir floor, memoria negativa, tasas anuales o fixing confirmados.
