# Estado final

**Resolución académica terminada y validada.** Precio 98,26916479 por 100, con error
estándar 2,74535035. El resultado completo y su interpretación pertenecen a
[RESULTADOS.md](RESULTADOS.md); la evidencia a [VALIDACION.md](VALIDACION.md).

## Qué existe

Originales íntegros, motor reproducible con 200 paths, 19 tests, referencia escalar,
contraste con 60 caplets, 230 controles de bonos, CSV/JSON y entregas Excel/PDF.
La [guía pedagógica](Guia_pedagogica_Snowblade_LMM.pdf) acompaña la solución para
su estudio y defensa.
El Excel está comprobado por recálculo real en LibreOffice con centinelas y sigma=0.

Las aclaraciones materiales están cerradas: tasas anuales ACT/365, memoria negativa
sin floor, intereses efectivos netos, fixing advance, h=.5, spot sin sigma y cupón
íntegro al autocall. Las citas están en [ACLARACIONES_PROFESOR.md](ACLARACIONES_PROFESOR.md).

## Límites y continuidad

Calendario sin ajuste/lag y sigma constante hasta reset son supuestos mínimos,
identificados en [DECISIONES.md](DECISIONES.md). Muestra corta, PCA y discretización
limitan el precio económico; el IC no engloba todas esas fuentes de incertidumbre.
Microsoft Excel y la convergencia por refinamiento Browniano no se han probado.

No hace falta otra aclaración para reproducir o defender el caso presentado. Para
retomar, seguir [README.md](../README.md) y las instrucciones de [AGENTS.md](../AGENTS.md).
No repetir etapas concluidas ni reabrir interpretaciones descartadas por el profesor.
La versión exacta se obtiene con `git rev-parse HEAD`; las versiones intermedias y
sus cambios de precio permanecen en el historial Git, no como instrucciones vigentes.
