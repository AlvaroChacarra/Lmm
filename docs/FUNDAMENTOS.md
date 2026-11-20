# Fundamentos y reflexión sobre la solución

La finalidad es valorar y poder defender un Snowblade con memoria y cancelación,
no reproducir una cifra por coincidencia. La solución enlaza fuentes, contrato,
modelo, estimador y entregas; cada enlace necesita una justificación distinta.

## 1. Qué sabemos y qué hemos elegido

El PDF exige LMM monocurva shifted lognormal bajo bono terminal. El XLSM aporta
curva, sigmas, cargas PCA y shocks. El profesor completa el contrato: tasas anuales,
ACT/365, memoria negativa sin floor, acumulación efectiva, advance y cupón íntegro.
También aclara h=.5 y la primera volatilidad del primer forward futuro.

No todos los detalles son citas del profesor. Calendario sin ajustes y sigma constante
hasta reset son opciones mínimas. [DECISIONES.md](DECISIONES.md) distingue su estatus;
[AUDITORIA_INPUTS.md](AUDITORIA_INPUTS.md) conecta cada parámetro con su celda.

## 2. Calendario, curva y dos relojes

Denotamos t0 el origen y t_j los aniversarios semestrales. Se pagan veinte cupones en
t1…t20; t21 es solo el terminal del numeraire. El índice0 corresponde al spot conocido,
y F_i, i=1…20, al tipo del intervalo futuro [t_i,t_(i+1)].

$$
\delta_i=\frac{\operatorname{días}(t_{i+1}-t_i)}{365},\qquad
F_i(0)=\frac{P(0,t_i)/P(0,t_{i+1})-1}{\delta_i}.
$$

Para i=0 la misma identidad calcula el spot inicial. La interpolación log-lineal
reproduce el modo0 de CInterPol y permite factores mayores que 1 cuando hay tipos
negativos. No procede imponer monotonía ni recortar los descuentos a 1.

El reloj de difusión es u_i=i/2, h=.5, indicado por el profesor; delta_i devenga
intereses ACT/365. Confundirlos genera otra implementación, aunque sus primeros
resultados puedan parecer cercanos. El primer devengo real es181/365, no.5.

## 3. Dinámica desplazada y cambio de medida

Se define X_i=F_i+s con s=.03 y lambda_i=sigma_i a_i, donde a_i es la fila de las
cargas finales suministradas. Bajo la medida del bono terminal Q21:

$$
\frac{dX_i}{X_i}=\mu_i\,du+\lambda_i\cdot dW^{21},\qquad
\mu_i=-\sum_{j=i+1}^{20}
\frac{\delta_j(F_j+s)}{1+\delta_jF_j}\,\lambda_i\cdot\lambda_j.
$$

El forward i es martingala bajo la medida de su bono de pago t_(i+1), no bajo
cualquier medida. Al cambiar al bono t21 aparece la suma de volatilidades de bonos
posteriores. El factor de ese cambio es delta_j(F_j+s)/(1+delta_jF_j): la difusión
está desplazada, mientras la identidad del bono contiene el tipo F_j sin desplazar.
Por eso el shift no se añade al denominador y la suma empieza en j=i+1.
El último forward tiene suma vacía y drift cero, un control analítico útil.

La difusión de tres factores implica covarianza lambda_i·lambda_j. Usar en el drift
la correlación original de rango 20 y en el ruido la aproximación de rango 3 no describe
un único modelo coherente. Se usa A Aᵀ en ambos términos. Las filas finales ya tienen
norma 1, de modo que la varianza marginal conserva sigma_i²; otro sqrt(lambda) o una
segunda normalización introducirían una transformación no solicitada de los inputs.

El paso implementado es log-Euler:

$$
X_i(u+h)=X_i(u)\exp\left[(\mu_i-\tfrac12\|\lambda_i\|^2)h
+\sqrt h\,\lambda_i\cdot Z\right],\qquad h=.5.
$$

Solo evolucionan forwards vivos; todos los drifts usan el estado anterior común.
Se conserva X>0 en aritmética exacta y se comprueban finitud y 1+delta F>0. No hay
clipping para ocultar estados inválidos. Sigue siendo una discretización, no solución
exacta del sistema acoplado. Compararla con predictor-corrector no demuestra convergencia.

## 4. Payoff con memoria y primer cruce

Las tasas anuales satisfacen c1=c2=.01 y, para j>=3:

$$
c_j=c_{j-1}+b_j-r_j,\qquad r_j=F_{j-1}(t_{j-1}).
$$

b3=b4=0; b5…8=.01; b9…12=.0125; b13…16=.015; b17…20=.02.
La memoria es la tasa anterior, incluso negativa; no el importe del cupón ni una tasa
limitada a cero. El cupón efectivo es delta_(j−1)c_j y el acumulado neto es

$$
S_m=\sum_{j=1}^{m}\delta_{j-1}c_j,\qquad
\kappa=\min\bigl(\{m:S_m\ge .04\}\cup\{20\}\bigr).
$$

Para nominal H:

$$
CF_m=H\,1_{m\le\kappa}\delta_{m-1}c_m+H\,1_{m=\kappa}.
$$

Se paga completo el cupón que activa el evento, más H, y se detienen los pagos. El
principal se devuelve una vez, también si se llega al vencimiento sin autocall.
El ejemplo externo 3,80 acumulados más 0,60 produce 100,60 y acumulado4,40: esa aceptación
contractual separa inequívocamente la opción A del recorte a exactamente 4%.

Sin floor, algunos escenarios obligan al inversor a pagar cantidades importantes.
Devolver el nominal a la par no limita la suma de cupones negativos al nominal. Esas
trayectorias explican la cola observada; suprimirlas cambiaría el contrato y el estimador.

## 5. Descuento, precio y error estadístico

$$
B(t_m)=P(t_m,t_{21})=\prod_{j=m}^{20}(1+\delta_jF_j(t_m))^{-1},\qquad
Y_p=P(0,t_{21})\sum_{m=1}^{20}\frac{CF_{p,m}}{B_p(t_m)}.
$$

En el último pago queda F20; el producto no es vacío. El bono vale 1 en t21, no en t20.
Cambiar de numeraire es válido con cambio consistente de medida, drift y ponderación;
no consiste en sustituir un factor de descuento manteniendo todo lo demás.

El precio es la media de los 200 Y_p; SE=desviación muestral(Y)/sqrt(200). Primero se
suman todos los pagos y componentes por path: usar 4.000 pagos como observaciones
independientes infravaloraría la incertidumbre. Las frecuencias y vida media obtenidas
son bajo Q terminal, no probabilidades físicas.

El IC Student publicado es aproximado y supone independencia de columnas. Con muestra
corta y cola asimétrica su cobertura real no está garantizada. El SE no incorpora error
PCA, parametrización o discretización. Auditar cinco veces los mismos200paths tampoco
los convierte en 1.000 simulaciones independientes.

## 6. Qué aprendimos del procedimiento y por qué se mantuvo

La auditoría de originales evitó interpretar valores pegados como fórmulas y permitió
localizar errores fuera de los rangos usados. Sin embargo, las dimensiones por sí solas
no resolvían el contrato. La primera solución podía ser internamente coherente y aun
necesitar corregir la asignación de sigma y el reloj al recibir la respuesta del profesor.
Se modificaron solo esos supuestos; [DECISIONES.md](DECISIONES.md) conserva el motivo.

La revisión aislada y la referencia escalar reducen el riesgo de repetir un error de
programación, pero no bastan si comparten la misma ecuación o convención errónea.
Por eso se combinaron identidades de bonos, límites deterministas y caplets analíticos,
y se pidió aclaración a quien definía el contrato. Los tests no deciden qué quiso decir
«Correcto»: un ejemplo de importes permitió obtener una respuesta verificable.

El primer intento de abrir/guardar una hoja conservaba los resultados cacheados.
La prueba con centinelas demostró que eso no era recálculo. Forzar la ejecución de las
fórmulas y perturbar las sigmas a cero aportó una evidencia distinta de leer un fichero
que contenía los mismos números. [VALIDACION.md](VALIDACION.md) delimita esa prueba.

La limpieza final conserva estas razones y la evidencia actual, pero elimina prompts
consumidos, calendarios superados y copias narrativas del PDF. El historial Git permite
recuperar el proceso sin obligar a otro lector a decidir qué instrucciones siguen vigentes.
Lo correcto es la coherencia comprobada entre contrato aclarado, modelo y entregas;
no una afirmación de exactitud económica absoluta ni el número de comprobaciones por sí solo.
