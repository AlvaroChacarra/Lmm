# Información contractual adicional al enunciado

Fuente: respuestas del profesor aportadas por el usuario durante la resolución.
Este documento conserva las frases materiales y su alcance final; no reproduce el
correo completo ni datos personales. No se ha autenticado externamente al remitente.
Las respuestas completan las ambigüedades del PDF original y tienen prioridad en su ámbito.

## Condiciones confirmadas

| Cuestión | Evidencia aportada por el profesor | Aplicación final |
| --- | --- | --- |
| Cupón negativo | «Si hay cupón negativo => el inversor tiene que pagar»; «El siguiente cupón se calcula […] sobre el valor negativo» | Sin floor. El estado recursivo conserva el negativo. |
| Objetivo del 4% | «La suma de los intereses reales acumulados»; ejemplo `2%*0.5+3%*0.5` | Acumular importes efectivos sobre nominal, netos de cupones negativos. No sumar tasas ni anualizar otra vez. |
| Cupones iniciales | «Es un tipo anual que debéis prorratear semestralmente en base ACT/365» | El 1% es anualizado. El devengo se aplica una vez al pago. |
| Fixing al comienzo | A la explicación de fijación al inicio: «Si, lo habeis hecho correctamente» | Advance: cupón j usa la fijación al inicio de su semestre. |
| Bono terminal 10 / 10,5 años | «En realidad da igual» | Se conserva 10,5 años con cambio de medida coherente; no implica igualdad de muestras finitas. |
| Primera volatilidad | «La primera volatilidad corresponde al primer forward. Pero el primer tipo, el del primer semestre no es forward, es spot» | Spot inicial sin sigma. F1…F20 usan las primeras veinte sigmas y las veinte filas PCA. |
| Paso de difusión | «El paso temporal para la partición hacedlo con 0,5 (base 30/360)» | h=.5; no sustituir por .5 el devengo ACT/365 de cupones y forwards. |
| Exceso del objetivo | «La opción sería la opción A […] no se \"capa\" el último cupón» | Cupón íntegro y principal en la liquidación de autocancelación. Recorte descartado. |

## Ejemplo que cierra la opción A

Con nominal 100, intereses acumulados de 3,80 y siguiente cupón efectivo de 0,60:
se pagan **100,60**, los intereses terminan en **4,40** y se cancelan los pagos
posteriores. La respuesta inicial «Correcto» a una pregunta con dos alternativas no
era inequívoca; por eso se pidió este ejemplo. La confirmación explícita resolvió la
duda y ratificó el payoff que ya estaba implementado, sin cambiar el precio.

## Frontera entre respuesta y supuesto

La asignación exacta a celdas está en [AUDITORIA_INPUTS.md](AUDITORIA_INPUTS.md).
El calendario de aniversarios sin ajuste hábil ni lag y la sigma constante hasta reset
son elecciones mínimas documentadas, no respuestas literales adicionales del profesor.
Su justificación está en [DECISIONES.md](DECISIONES.md).

El PDF dice «alcance» el 4% y el código usa `S>=.04`. La última explicación emplea
«mayor». Ningún acumulado observado vivo de los 200 paths es exactamente .04; ambos
tests dan la misma valoración en esta muestra, como registra la validación ejecutada.
