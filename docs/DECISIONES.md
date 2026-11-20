# Decisiones finales y razones

Las respuestas literales y su alcance están en [ACLARACIONES_PROFESOR.md](ACLARACIONES_PROFESOR.md).
Las fórmulas pertenecen a [FUNDAMENTOS.md](FUNDAMENTOS.md), los índices a
[AUDITORIA_INPUTS.md](AUDITORIA_INPUTS.md) y las cifras a [RESULTADOS.md](RESULTADOS.md).
Aquí se registra por qué esa es la solución elegida y qué estatus tiene cada decisión.

| ID | Decisión vigente | Fundamento y alternativa descartada |
| --- | --- | --- |
| D01 | Acumular intereses efectivos netos desde origen | Profesor: suma de intereses reales; ejemplo 2%×.5+3%×.5. Sumar tasas o anualizar de nuevo responde a otro contrato. Los cupones negativos restan. |
| D02 | Cupones en tasas anuales; pago con ACT/365 | Confirmado por el profesor. El 1% no es un importe efectivo del 1% por semestre. Devengar una vez. |
| D03 | Sin floor; memoria del cupón negativo | Confirmado. Un floor del pago o del estado cambiaría los cupones futuros y el trigger. No introducir protección por costumbre comercial. |
| D04 | Fixing advance | Confirmado al explicar que se usa el Euribor fijado al inicio del semestre. Observar el Euribor al pago sería una estructura in-arrears distinta. |
| D05 | Bono terminal a t21, seis meses después del último pago | Elección admitida por el profesor. No añade cupón. Cambiar de numeraire exige cambiar medida/drift y descuento; dos muestras finitas no tienen por qué dar la misma media. |
| D06 | Interpolar logaritmos de factores, modo0 de CInterPol | Equivalente a la función suministrada. No spline ni interpolación de tipos cero. Python rechaza extrapolación, innecesaria en el calendario final; el VBA no se ejecuta. |
| D07 | Cargas finales G117:I136 literales y A Aᵀ en todo el modelo | La plantilla ya las normaliza. Reescalarlas otra vez altera sigmas; usar R original en el drift y A Aᵀ en difusión rompe la coherencia de medida. La aproximación PCA se conserva y se declara. |
| D08 | h=.5 de difusión y ACT/365 de devengo | Confirmación del profesor sobre partición 30/360. Son funciones distintas; no trasladar .5 automáticamente al importe de los cupones. Aniversarios sin ajuste ni lag son un supuesto mínimo de calendario. |
| D09 | Spot inicial sin sigma; F1 usa la primera sigma | Aclaración expresa del profesor. Se corrige el antiguo desplazamiento de filas: F9:F28 para F1…F20; F29 extra preservada sin uso. Sigma constante hasta reset es parametrización mínima, no respuesta literal adicional. |
| D10 | Opción A: cupón íntegro más nominal al autocall | Confirmación final explícita. No limitar el acumulado a exactamente 4%. El ejemplo 3,80+.60 termina en 4,40 y paga 100,60. La respuesta anterior «Correcto» no era suficiente para escoger entre dos opciones. |
| D11 | Log-Euler, drift congelado con estado anterior común | Elección numérica sencilla y trazable. Predictor-corrector es un control adicional con los mismos shocks; no se presenta como prueba de convergencia temporal. |
| D12 | Los 200 paths completos, sin excluir extremos | Exigencia de fuente y condición de reproducibilidad. SE sobre los 200PV; no sobre pagos ni solo sobre cupones. La cola negativa limita la precisión, no autoriza quitar el peor path. |
| D13 | Frecuencias y vida media bajo Q terminal | Es la medida de simulación. No son probabilidades físicas ni pronósticos de rentabilidad del inversor. |
| D14 | XLSX nuevo, sin VBA, con fórmulas y recálculo externo probado | Se preserva el XLSM original. Leer cachés no demuestra ejecución: se usa control centinela y sigma=0 en LibreOffice. Microsoft Excel no probado. |

## Correcciones que explican el estado final

La primera solución (`63a681f`) daba **98,51983210** con reloj de difusión ACT/365 y
la primera sigma sin uso en el spot. Era reproducible bajo esas hipótesis, pero encajar
las dimensiones del Excel no demostraba la intención del enunciado.

Las respuestas sobre h=.5 y spot/primer forward sustituyeron esas dos hipótesis y
llevaron el caso final a **98,26916479** (`b5b6b95`). La diferencia conjunta es
-0,25066730 por 100; no se reconstruye sumando sensibilidades con bases distintas,
porque el primer cruce de autocall es no lineal.

La confirmación explícita de opción A (`a44632a`) cerró la incertidumbre contractual
restante **sin cambiar el precio ni los flujos**: ese era ya el payoff implementado.
El contexto esencial queda en estas decisiones; los documentos y scripts de etapas
intermedias se recuperan en Git si se necesitan, sin mantenerlos como instrucciones activas.

## Supuestos y límites que no son preguntas contractuales abiertas

El calendario de aniversarios sin ajuste/lag y la sigma constante hasta reset se
conservan como opciones mínimas de modelización. Las fuentes no identifican una
parametrización temporal única. Son coherentes con el ejercicio y están contrastadas;
no se atribuye al profesor una aprobación literal que no dio.

El test de alcance es S>=.04. La explicación final usó «mayor»: en la muestra original
no hay igualdad exacta al4%, y se comprobó que ambos tests dan los mismos resultados.
No se afirma precisión de céntimos ni que el IC Monte Carlo englobe el riesgo de modelo.
