# Estado del proyecto

**Estado:** segunda ronda del profesor incorporada; nueva estimación reproducible.
**Precio actualizado:** 98.26916479 por 100; SE 2.74535035;
IC 95% aproximado [92.85545320,103.68287639]. El 98.51983210 anterior corresponde a
las hipótesis previas de reloj ACT/365 y primera sigma asignada al spot; queda supersedido.

Leer [ACLARACIONES_PROFESOR.md](ACLARACIONES_PROFESOR.md),
[DECISIONES.md](DECISIONES.md), [RESULTADOS.md](RESULTADOS.md) y
[VALIDACION.md](VALIDACION.md). La auditoría Fase 0 es histórica; la auditoría multiagente
de 63a681f valida la formulación anterior, no certifica por sí sola estos nuevos parámetros.

## Cambios autorizados por la segunda respuesta

- Fixing al inicio confirmado; se conserva advance.
- Partición de difusión h=.5 (30/360), manteniendo ACT/365 del cupón y forwards.
- El tipo inicial es spot, sin sigma. F1 usa primera volatilidad F9; F20 usa F28.
  F29 extra queda preservada y sin usar; ya no se asigna una sigma al spot.
- Se conserva bono terminal auxiliar a 10,5 años: el profesor permite la elección de
  numerario. Drift y descuento se mantienen coherentes; no se promete igualdad muestral.
- «Correcto» ante pago completo o recorte no selecciona inequívocamente una opción:
  se mantiene cupón completo como lectura de trabajo y se publica sensibilidad al recorte.

## Evidencia actual

- Originales íntegros; 200 paths y PCA sin sustitución, normalización o recentrado.
- 19 tests PASS; todos los PV con referencia escalar difieren como máximo 2.85e-13.
- Sigma=0 coincide con descuento directo; 230 controles de bonos y 60 caplets Black
  superan las tolerancias MC. No se afirma convergencia temporal ni IC de cobertura exacta.
- 185 autocalls, 15 vencimientos sin autocall; 29 paths con cupón negativo y 5 con PV negativo.
- Excel/PDF regenerados. Script de recálculo LibreOffice con centinelas y sigma=0
  integrado en el repositorio; evidencia actual en outputs/recalculo_validacion.json.
  Microsoft Excel no probado. La generación no sobrescribe los originales.

## Límites restantes

Calendario de aniversarios sin ajuste/lag y sigma constante hasta reset son supuestos
mínimos; esa parte de la pregunta no recibió confirmación literal. El tratamiento del
exceso es la única respuesta con dos opciones que quedó ambigua. No se exige otra
confirmación para calcular el caso presentado, pero no debe declararse contrato único
inequívocamente confirmado. La cola y n=200 limitan precisión; SE no incluye modelo/PCA.

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
