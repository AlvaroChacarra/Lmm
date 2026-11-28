# Plan de acción y criterios de cierre

**Objetivo docente.** El profesor debe poder localizar el precio al abrir el Excel, seguir una trayectoria completa y contrastarla con la memoria. Quien defienda el trabajo debe poder explicar la decisión contractual, el cambio de numerario y la incertidumbre muestral.

## Dos revisiones del plan antes de producir

| Vuelta | Propuesta | Crítica | Cambio incorporado |
|---|---|---|---|
| 1 | Ampliar la memoria a 10–12 páginas y reorganizar todas las hojas | El enunciado exige implementación, decisiones y análisis. Una cuota de páginas y una migración del motor añaden esfuerzo sin probar comprensión. | Organizar la memoria en cinco páginas, con el caso numérico y los resultados al final. Desarrollar el caso 1, que termina en cinco semestres. Conservar las referencias operativas de las hojas de cálculo. |
| 2 | Narrar el caso y añadir una copia de sus cálculos al Excel | Una segunda implementación podría divergir. Mostrar solo cinco semestres ocultaría flujos si al cambiar un parámetro el producto sobrevive. | La hoja de ejemplo enlaza los veinte semestres. El PDF desarrolla los cinco vivos del caso base. Añadir referencias exactas, un control del cierre y una segunda trayectoria únicamente para explicar la cola. |

## Secuencia de ejecución

| Paso | Trabajo concreto | Justificación | Criterio de aceptación |
|---|---|---|---|
| 1. Fijar la referencia | Recuperar originales y scripts de una revisión identificada. Comprobar hashes, ejecutar los tests y regenerar el libro anterior. | Distingue un cambio editorial de un cambio de precio. | Originales íntegros, 200 trayectorias y libro anterior reconciliado con el hash del certificado. |
| 2. Ordenar el Excel | Abrir en Resumen, colocar Ejemplo a continuación y acortar la guía dentro de la pantalla inicial. Agrupar cálculo y fuentes por función. | Facilita revisar el precio antes de explorar el detalle. | Precio, unidad, error y acceso al ejemplo en la primera vista. Porcentajes, años e importes diferenciados. |
| 3. Unificar fuentes | Enlazar las cargas de Calendario a PCA. Mantener las fórmulas de simulación y usar la hoja Flujos como fuente del caso. | Permite rastrear un valor hasta un origen único. | Los enlaces del ejemplo cubren los veinte periodos. Cambiar el nominal modifica los importes de la vista. |
| 4. Construir la memoria | Resultado y pregunta económica; contrato; curva y tres factores; dinámica y numerario; ejemplo; distribución; validación y decisiones. | Introduce cada variable cuando el lector la necesita. | El lector reconstruye el tercer cupón, el pago de cancelación y el PV de la trayectoria con la precisión mostrada. |
| 5. Seleccionar evidencia | Mostrar la cronología de un semestre, los cobros del ejemplo y la distribución de PV. Identificar unidades, medida y denominador. | Cada visual resuelve una pregunta distinta. | Los recuentos cierran en 200 y los gráficos incluyen los extremos. |
| 6. Auditar y remediar | Renderizar todas las páginas y las primeras vistas del libro. Examinar densidad, saltos, jerarquía, decimales, referencias y fórmulas. Registrar hallazgos y resolverlos en el generador. | Detecta defectos que una comparación de números no encuentra. | Texto legible a tamaño normal, tablas sin cortes, una tarea principal por página. |
| 7. Repetir sobre la versión corregida | Volver a inspeccionar renders, verificar la ruta de lectura y recalcular el libro con cachés alteradas, sigma cero y nominal doble. | Comprueba que una mejora visual conserva el comportamiento del archivo entregado. | Coinciden PDF, Excel y motor. El certificado identifica el hash del XLSX final y el motor utilizado. |

## Prueba de lectura para el cierre

1. Abrir el libro y localizar precio, nominal e intervalo sin desplazamiento horizontal.
2. Abrir el ejemplo. En el periodo 3, pasar de fixing a tasa anual, aplicar ACT/365 y localizar el pago.
3. En el periodo 5, explicar la devolución íntegra, señalar el cupón que rebasa el objetivo y verificar los flujos posteriores.
4. Reconciliar el valor de la trayectoria con Paths y el precio con la media de 200 valores.
5. Con la memoria sola, explicar qué representa el bono terminal, por qué la mediana supera la media y qué mide el intervalo.

La revisión visual y el recorrido de lectura son pruebas de escritorio. Una prueba con el profesor o en Microsoft Excel requiere observar ese uso directamente.

## Resultado de las dos rondas de ejecución

| Ronda | Observación sobre los archivos generados | Remedio aplicado | Cómo se volvió a comprobar |
|---|---|---|---|
| Primera | El detalle del modelo y los gráficos competían con el ejemplo. | Unir curva, simulación y numerario en una página. Usar una cronología, una tabla del caso y una distribución. | Leer las cinco páginas renderizadas y reconstruir el caso con nominal 100. |
| Segunda | La distribución por semestre ocupaba la mayor parte de Resumen. El PV del ejemplo se mostraba con dos decimales. | Mover el detalle por semestre a Paths, dejar los dos recuentos de amortización en Resumen y mostrar cuatro decimales en el PV del ejemplo. | Inspección de las nuevas vistas, conciliación de las fórmulas y prueba de los recuentos con volatilidad cero. |

**Prueba de lectura resuelta.** Resumen!B2 contiene el valor de 98,27 para el nominal de Resumen!F4. En Ejemplo!E7 se observa el tercer cupón de 0,7910. El quinto semestre devuelve 100 y paga 2,2411. El valor de la trayectoria completa asciende a 101,4358 y coincide con Paths!D2. La página 4 reconstruye estos pasos. La página 5 explica el efecto de la cola con la trayectoria 71.

**Evidencia.** Los resultados numéricos de la revisión definitiva están en [entrega_validacion.json](../outputs/entrega_validacion.json) y [recalculo_validacion.json](../outputs/recalculo_validacion.json). La primera comprobación contrasta el libro y el PDF con Python; la segunda ejecuta las fórmulas en LibreOffice. El criterio visual se contrastó sobre las cinco páginas y las vistas iniciales de las hojas del libro.
