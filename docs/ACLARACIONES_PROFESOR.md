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

## Convenciones que no se confirmaron expresamente

- Calendario hábil, spot/fixing lag y fixing advance frente a arrears.
- Qué fecha es N+1 y cómo encajan las 21 volatilidades con las 20 filas de PCA.
- Volatilidades constantes hasta reset frente a una estructura instantánea temporal.
- Frecuencia operacional del test y tratamiento del exceso al cruzar el 4%.

El caso base aplica test en cada pago, cupón completo sin recortar el exceso, y el
calendario H-cal de la auditoría. Son convenciones adoptadas para resolver, no citas
del profesor. Las diferencias de precio relevantes se publican en RESULTADOS.md.
