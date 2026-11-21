# Plan de acción y criterios de cierre

**Objetivo docente.** El profesor debe poder localizar el precio al abrir el Excel, seguir una trayectoria completa y contrastarla con la memoria. Quien defienda el trabajo debe poder explicar la decisión contractual, el cambio de numerario y la incertidumbre muestral.

## Dos revisiones del plan antes de producir

| Vuelta | Propuesta | Crítica | Cambio incorporado |
|---|---|---|---|
| 1 | Ampliar la memoria a 10–12 páginas y reorganizar todas las hojas | El enunciado exige implementación, decisiones y análisis. Una cuota de páginas y una migración del motor añaden esfuerzo sin probar comprensión. | Usar siete preguntas consecutivas. Desarrollar el caso 1, que termina en cinco semestres. Conservar las referencias operativas de las hojas de cálculo. |
| 2 | Narrar el caso y añadir una copia de sus cálculos al Excel | Una segunda implementación podría divergir. Mostrar solo cinco semestres ocultaría flujos si al cambiar un parámetro el producto sobrevive. | La hoja de ejemplo enlaza los veinte semestres. El PDF desarrolla los cinco vivos del caso base. Añadir referencias exactas, un control del cierre y una segunda trayectoria únicamente para explicar la cola. |

## Secuencia de ejecución

| Paso | Trabajo concreto | Justificación | Criterio de aceptación |
|---|---|---|---|
| 1. Fijar la referencia | Recuperar originales y scripts de una revisión identificada. Comprobar hashes, ejecutar los tests y regenerar el libro anterior. | Distingue un cambio editorial de un cambio de precio. | Originales íntegros, 200 trayectorias y libro anterior reconciliado con el hash del certificado. |
| 2. Ordenar el Excel | Abrir en Resumen, colocar Ejemplo a continuación y acortar la guía dentro de la pantalla inicial. Agrupar cálculo y fuentes por función. | Facilita revisar el precio antes de explorar el detalle. | Precio, unidad, error y acceso al ejemplo en la primera vista. Porcentajes, años e importes diferenciados. |
| 3. Unificar fuentes | Enlazar las cargas de Calendario a PCA. Mantener las fórmulas de simulación y usar la hoja Flujos como fuente del caso. | Permite rastrear un valor hasta un origen único. | Los enlaces del ejemplo cubren los veinte periodos. Cambiar el nominal modifica los importes de la vista. |
| 4. Construir la memoria | Resultado y pregunta económica; contrato; curva y tres factores; dinámica y numerario; ejemplo; distribución; validación y decisiones. | Introduce cada variable cuando el lector la necesita. | El lector reconstruye el tercer cupón, el pago de cancelación y el PV de la trayectoria con la precisión mostrada. |
| 5. Seleccionar evidencia | Dibujar el comportamiento de dos trayectorias, la distribución de cancelaciones y la distribución de PV. Identificar unidades, medida y denominador. | Cada visual resuelve una pregunta distinta. | Los recuentos cierran en 200 y los gráficos incluyen los extremos. |
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
| Primera | En la página del modelo, los recuadros de ecuaciones quedaban demasiado próximos al párrafo siguiente. La primera versión del generador reutilizaba un nombre para el formato de entrada y la columna de origen al agregar los PV. | Aumentar separación y cuerpo de lectura, definir el browniano al presentar la ecuación y distinguir el formato de entrada de la referencia de columna. Crear las hojas directamente en su orden de lectura. | Render completo de siete páginas, apertura del libro y recálculo real. La revisión intermedia concilió 196.215 fórmulas y las cifras del ejemplo. |
| Segunda | En el ejemplo, los quince periodos posteriores a la cancelación competían visualmente con los cinco pagos vivos. En Resumen, cuatro decimales en las frecuencias excedían la resolución de la muestra y el nominal figuraba en una nota fija. La memoria necesitaba explicar el valor del principal superior a 100. | Dar contraste a la amortización, atenuar automáticamente los periodos posteriores y mostrar frecuencias con un decimal. Enlazar el nominal visible y derivar el tamaño muestral del rango de PV. Explicar la contribución del principal en página 1 y acortar las aclaraciones de cierre. | Nueva renderización del libro y de la memoria. Comprobación de los veinte periodos del ejemplo, su PV total, las cargas PCA enlazadas, los 200 PV y los principales resultados. Recálculo externo sobre la revisión definitiva. |

**Prueba de lectura resuelta.** Resumen!B2 contiene el valor de 98,27 para el nominal de Resumen!F4. En Ejemplo!E7 se observa el tercer cupón de 0,7910. El quinto semestre devuelve 100 y paga 2,2411. El valor de la trayectoria completa asciende a 101,4358 y coincide con Paths!D2. La página 5 permite reconstruir estos pasos; la página 6 contrasta el caso con la trayectoria 71.

**Evidencia.** Los resultados numéricos de la revisión definitiva están en [entrega_validacion.json](../outputs/entrega_validacion.json) y [recalculo_validacion.json](../outputs/recalculo_validacion.json). La primera comprobación contrasta el libro y el PDF con Python; la segunda ejecuta las fórmulas en LibreOffice. El criterio visual se contrastó sobre las siete páginas y las dos hojas destinadas a la lectura.
