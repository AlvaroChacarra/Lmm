# Resultado final y lectura económica

**Precio: 98,2691647950 por 100 de nominal.** El contrato vigente usa fixing advance,
cupones anuales ACT/365 sin floor ni recorte, memoria negativa, objetivo efectivo4%,
h=.5 de difusión y primera sigma para el primer forward futuro. Las fuentes y razones
están en [ACLARACIONES_PROFESOR](ACLARACIONES_PROFESOR.md) y [DECISIONES](DECISIONES.md).

## Estimación sobre los 200 paths originales

| Magnitud | Valor |
| --- | ---: |
| PV cupones | -2,2533577743 |
| PV principal | 100,5225225693 |
| Precio total | 98,2691647950 |
| Error estándar MC | 2,7453503522 |
| IC95% Student aproximado | [92,8554532016; 103,6828763883] |
| Vida media bajo Q terminal | 3,3801643836 años |
| Autocalls / vencimientos sin autocall | 185 / 15 |
| Paths con algún cupón negativo / PV neto negativo | 29 / 5 |
| Mediana del PV | 103,9453260046 |

Los decimales permiten reconciliar implementaciones; no representan esa precisión
económica. Muestra corta, asimetría y aproximaciones del modelo limitan la estimación.
El IC es aproximado y no incorpora error PCA, parametrización ni discretización.

El principal tiene PV superior a 100 por el descuento y la devolución frecuentemente
temprana, en una curva inicial con tipos negativos. Los cupones tienen PV neto negativo
por pocos escenarios que sobreviven y exigen pagos elevados al inversor. Ambas cosas
son compatibles con devolver el nominal a la par y con un producto sin floor.

El peor path es el 71, con PV -310,6175641748. Omitirlo subiría la media a 100,3238719757:
es solo influencia muestral, no otro precio admisible. Ningún path fue eliminado.
El 61,5% autocancela hasta periodo 5 y el 80% hasta periodo 6; el 7,5% vence sin autocall.
Son frecuencias bajo Q terminal, no probabilidades físicas ni recomendaciones de inversión.

## Controles conservados

Sigma cero da 105,3565962616 y permite comparar contra descuento directo. El esquema
predictor-corrector da 98,3074505558 y el terminal T20 da 98,1855226344. Son controles
del método con los mismos shocks, no demostraciones de convergencia ni obligación de
igualdad exacta entre muestras bajo medidas diferentes.

El JSON conserva asimismo reloj, fila de volatilidad, arrears y cupón recortado como
contrafactuales de trazabilidad. El profesor descartó sus interpretaciones contractuales;
no son precios candidatos ni extremos de un intervalo probabilístico. Las correcciones
que llevaron al estado final se explican una sola vez en [DECISIONES](DECISIONES.md).

## Artefactos y trazabilidad

| Fichero | Contenido |
| --- | --- |
| [Excel](../entrega/Snowblade_LMM.xlsx) | Inputs originales copiados, calendario, cargas, shocks, fórmulas de estados/flujos, 200 PV y resumen |
| [Memoria](../entrega/Memoria_Snowblade.pdf) | Cinco páginas de contrato, metodología, resultados y límites |
| [resultados.json](../outputs/resultados.json) | Base, configuración, componentes, probabilidades, controles y contraste con el caso anterior |
| [path_pv.csv](../outputs/path_pv.csv) | Los 200 PV, componentes y fecha de amortización por path |
| [cashflows.csv](../outputs/cashflows.csv) | Los 4.000 registros de fixing, devengo, cupón, principal y descuento |
| [validacion.json](../outputs/validacion.json) | Referencia escalar, opción A, bonos y caplets analíticos |
| [recalculo_validacion.json](../outputs/recalculo_validacion.json) | Recálculo externo vinculado al hash exacto del XLSX |
| [entrega_validacion.json](../outputs/entrega_validacion.json) | Relectura y reconciliación de Excel/PDF contra Python |

La [validación](VALIDACION.md) distingue cachés de ejecución real. El libro es nuevo,
sin VBA. La hoja Ejemplo enlaza los flujos del primer path y las sensibilidades se conservan en el JSON. Para regenerar cálculo y entregas,
seguir el orden de [README](../README.md); los originales permanecen inmutables.
