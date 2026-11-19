# Aclaraciones contractuales del profesor

Fuente: respuestas del profesor a las tres preguntas del alumno, aportadas por el usuario
en esta sesión. El correo compartido no incluye fecha. Se consideran aclaraciones
autorizadas del ejercicio; no son una verificación externa del remitente.

## Condiciones confirmadas

1. **Sin floor cero.** Si el cupón es negativo, el inversor tiene que pagar.
   El siguiente cupón se calcula sobre el valor negativo, sin resetearlo a cero.
2. **Objetivo del 4% de intereses reales acumulados.** El profesor ejemplifica:
   «2% anualizado» un semestre más «3% anualizado» el siguiente suma
   `2% × 0.5 + 3% × 0.5 = 2.5%` del nominal. No es suma de tasas ni media anual.
   Al combinarlo con la confirmación del primer punto, se adopta acumulación neta:
   los pagos negativos restan intereses acumulados.
3. **Cupones iniciales anualizados.** El 1% de los dos primeros periodos se prorratea
   con ACT/365. Las sumas y restas de la tabla contractual se implementan en tasas
   anualizadas, y el devengo se aplica al importe pagado una sola vez.

Estas aclaraciones cierran D01–D03 y sustituyen las alternativas que se estudiaron
antes de obtener respuesta. No procede seguir presentando floor cero o 1% efectivo
semestral como lecturas contractuales igualmente válidas.

## Convenciones pendientes tras la primera ronda (histórico)

- Calendario hábil, spot/fixing lag y fixing advance frente a arrears.
- Qué fecha es N+1 y cómo encajan las 21 volatilidades con las 20 filas de PCA.
- Volatilidades constantes hasta reset frente a una estructura instantánea temporal.
- Frecuencia operacional del test y tratamiento del exceso al cruzar el 4%.

Antes de la segunda ronda, el caso base aplicaba test en cada pago, cupón completo sin recortar el exceso, y el
calendario H-cal de la auditoría. Son convenciones adoptadas para resolver, no citas
del profesor. Las diferencias de precio relevantes se publican en RESULTADOS.md.

## Segunda ronda — respuestas recibidas después de la auditoría de 63a681f

Fuente: nueva respuesta del profesor aportada por el usuario. Se preservan a
continuación las frases materiales y su interpretación operativa; no se conserva el
hilo de correo ni datos personales. Esta sección sustituye las preguntas abiertas
anteriores en el ámbito que efectivamente resuelve.

| Pregunta | Respuesta literal | Consecuencia |
| --- | --- | --- |
| Fixing al inicio frente a observación al pago; se explicó que usamos inicio | «Si, lo habeis hecho correctamente» | Advance confirmado; no cambiar a arrears. |
| Pago completo frente a recorte del cupón al cruzar el 4% | «Correcto» | Respuesta breve ante dos alternativas: no selecciona inequívocamente una. Se mantiene cupón completo como lectura de trabajo, sin declarar el recorte expresamente descartado. |
| Bono terminal a 10 o 10,5 años; se explicó que usamos 10,5 | «En realidad da igual.» | Se admite conservar el terminal de 10,5 años. Es elección de numerario: exige cambiar consistentemente drift y descuento. No garantiza igualdad path a path ni idéntico MC con 200 normales. |
| Primera volatilidad y tipo del primer semestre | «La primera volatilidad corresponde al primer forward. Pero el primer tipo, el del primer semestre no es forward, es spot» | El spot inicial no consume sigma; F1 usa F9, F20 usa F28. Hay veinte forwards futuros y veinte filas PCA; F29 es una fila extra no usada, conservada en el original y en la hoja Volatilidades de entrega. |
| Paso temporal efectivo ACT/365 frente a 0,5 de plantilla | «No, el paso temporal para la partición hacedlo con 0,5 (base 30/360)» | Difusión con h=.5 fijo. Devengo de cupones ACT/365 sigue vigente: no cambiarlo a 30/360. |

La persistencia de sigma constante hasta reset **no fue contestada expresamente** en
la respuesta sobre su correspondencia. Se conserva como parametrización mínima del
modelo, no como nueva instrucción literal del profesor. El calendario de aniversarios
sin ajuste hábil ni lag también se mantiene como supuesto documentado.

La notación de código `f0[0]`/`F0` es solo el índice del spot inicial calculado desde la
curva; no se afirma que sea un forward futuro ni se le simula una volatilidad.
La sigma21 no se fuerza sobre el spot ni se elimina del archivo para encajar dimensiones.
