# Evidencia de validación y alcance

**PASS para el uso académico del caso documentado**, con precisión MC limitada y los
supuestos mínimos de [DECISIONES](DECISIONES.md). Comandos de verificación y regeneración: [README](../README.md).

## Código, contrato y estimador

**19 tests superados** cubren integridad y corrupción de fuente, interpolación, curva/
forwards, spot y mapa sigma, separación h/delta, signo/shift del drift, último forward,
congelación de tipos, dominio, sigma cero, payoff negativo, primer cruce, amortización
única, estadística sobre paths completos y comparación escalar.

| Contraste actual | Máximo error absoluto |
| --- | ---: |
| Forwards vectorizados / escalar | 1,5404344467e-15 |
| Cupones vectorizados / escalar | 6,2616578589e-14 |
| Principal | 0 |
| PV por path | 2,8421709430e-13 |
| Sigma cero / descuento directo | 7,1054273576e-14 |

[validacion.json](../outputs/validacion.json) contiene los 230 controles de ratios de
bonos (máximo abs(z)=2,0263283) y 60 caplets contra shifted-Black (máximo abs(z)=1,8261018).
Usan los mismos200paths originales, expiries de difusión i*.5, sigmas F9:F28 y strikes
F_i(0)±1% y ATM. Todos quedan dentro de las tolerancias de cinco SE aplicadas. Son
contrastes probabilísticos correlacionados, no pruebas de convergencia temporal o
cobertura exacta del IC.

La referencia escalar no llama a kernels de simulación, payoff, interpolación o PV del
motor; comparte inputs y convenciones. Por sí sola no demostraría que esas convenciones
son las del contrato. Se complementa con límites analíticos y respuestas del profesor.
Su ejemplo final se ha ejecutado:3,80 acumulados + 0,60 de cupón produce 100,60, intereses4,40
y ningún flujo posterior. No hay igualdad exacta al4% en los paths originales: > y >=
producen las mismas cancelaciones de la muestra; el test del enunciado es de alcance.

## Recálculo de las entregas

El XLSX contiene **195.974 fórmulas**. Se reconcilian 88.200 estados, 4.000 registros de
flujos y 200 PV, además de las cifras del resumen y el PDF de cinco páginas.

El script de recálculo trabaja con copias temporales en LibreOffice. El certificado
registra la versión del motor junto al hash del libro comprobado.

1. Sustituye todos los resultados guardados de fórmulas por un centinela.
2. Un perfil que no recalcula los conserva: control negativo de que abrir/guardar no
   basta para validar una hoja de cálculo.
3. Con OOXMLRecalcMode=0 se sustituyen todos, sin celdas de error. Desvío máximo frente
   a los valores auténticos: 1,5916157281e-12; precio 98,2691647949938.
4. Con las sigmas a cero y cachés adulteradas, el motor calcula 105,35659626163304 y
   la tabla de `Resumen` registra 200 autocancelaciones (100 %) en el quinto periodo
   y cero en los otros 19. El recuento exige el indicador de autocall de `Paths`.
5. Al cambiar solo el nominal de 100 a 200, «PV del nominal introducido» pasa de
   98,269164795 a 196,538329590.
6. Conserva el hash del XLSX de origen y de los originales contractuales.

El [certificado](../outputs/recalculo_validacion.json) se liga al hash del libro:
[check_delivery.py](../scripts/check_delivery.py) no acepta como vigente un certificado
de otro XLSX. **Microsoft Excel no probado.** Estas pruebas no convierten las tablas
estáticas de escenarios en una aplicación general de valoración.

## Auditoría aislada y lecciones conservadas

Cinco agentes nuevos revisaron aisladamente contrato/inputs, matemáticas, código/
estadística, Excel/PDF y una reconstrucción ciega del commit 63a681f, antes de recibir
las correcciones finales de sigma/reloj. Después contrastaron sus discrepancias.
No identificaron un bug material del caso entonces documentado; reprodujeron su precio
condicional y señalaron el efecto contractual del fixing pendiente de confirmación.

Aquella auditoría no certifica automáticamente parámetros posteriores ni sustituye
al profesor. La configuración final se verificó después con los19tests, referencia
escalar, caplets y recálculo externo actuales. Las respuestas cerraron advance y
opción A; se conservaron sus citas y consecuencias, no informes intermedios con dudas
ya resueltas. [Fundamentos y reflexión](FUNDAMENTOS.md) explica esta separación de pruebas.

## Reproducibilidad y límites

Mismos originales, versión, configuración y200paths producen los mismos JSON/CSV
numéricos. La confirmación de opción A no alteró ni los 200PV ni los 4.000flujos de
b5b6b95. Los SHA-256 de originales y del XLSX actual están en la evidencia citada.

No se afirma independencia demostrada del generador pegado en Excel, precisión de
céntimos, calibración con precios externos, convergencia Browniana, ejecución de VBA
ni auditoría de su p-code. Los límites de muestra, PCA y esquema permanecen explícitos.
La limpieza de documentación no es una nueva auditoría económica ni aumenta el n de MC.
