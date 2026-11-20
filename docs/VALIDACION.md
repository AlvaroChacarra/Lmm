# Validación con opción A confirmada

**PASS para el uso académico y el caso documentado**, con precisión MC limitada:
h=.5, sigma1 para F1, spot sin sigma y cupón íntegro al autocall confirmado por el
profesor (opción A). No se ha cambiado el algoritmo ni el precio. Calendario sin ajuste
y sigma constante hasta reset permanecen como supuestos mínimos explícitos.

El anterior commit 63a681f fue auditado por cinco agentes. Esta actualización no reclama
una nueva auditoría multiagente: reejecuta los contrastes de la nueva configuración,
incluido el motor real de hoja de cálculo. No se modifican los originales ni los shocks.

## Motor y referencia escalar

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/validate_solution.py
```

**19 tests PASS.** Se conservan los 17 anteriores y se añaden dos controles materiales:
mapa spot/F1/F20, sigma21 fuera de malla; separación entre h=.5 y devengos ACT/365.
La fórmula cerrada del último forward con drift cero usa veinte incrementos de .5,
no los días ACT/365. El checksum original sigue siendo obligatorio.

| Comparación de los 200 paths | Máximo error absoluto |
| --- | ---: |
| Forwards vectorizados / escalar | 1.5404344467e-15 |
| Cupones vectorizados / escalar | 6.2616578589e-14 |
| Principal | 0 |
| PV por path | 2.8421709430e-13 |
| Sigma=0 / descuento directo | 7.1054273576e-14 |

[outputs/validacion.json](../outputs/validacion.json) identifica la configuración y
contiene 230 diagnósticos de bonos: máximo abs(z)=2.0263283, todos dentro de 5SE.
Añade 60 caplets, strikes F0 y F0±1%, contra shifted-Black con expiries de difusión
T_i=i*.5 y sigmas F9:F28: máximo abs(z)=1.8261018. Se valora el payoff conocido al reset
mediante el cociente de bonos, sin simular números nuevos. Es contraste de calibración
marginal para esta parametrización, no prueba de convergencia temporal ni cobertura exacta.

La referencia escalar comparte inputs y convenciones, pero no los kernels de drift,
payoff, interpolación o PV. Reproduce todas las trayectorias y decisiones de amortización.
La ambigüedad de «Correcto» se cierra por fuente explícita del profesor, no por un test.
Se ha ejecutado además el fixture de aceptación 3.80+.60: acumulado4.40, cupón.60
y principal100 en ese pago, sin flujos posteriores. Resultado en professor_option_A del JSON.
En los 200 paths reales no hay igualdad exacta al4%: los tests > y >= producen las
mismas cancelaciones. La lectura de alcance del PDF sigue siendo >=.

## Entregas y recálculo real

```sh
python scripts/build_delivery.py
python scripts/recalculate_delivery.py
python scripts/check_delivery.py
```

El nuevo XLSX contiene **195.934 fórmulas**. Incluye la hoja Volatilidades con las
21 sigmas originales, su fuente y uso; la fila extra21 no se fuerza en el spot.
La difusión usa Parametros!B8=.5 y los cupones Calendario!ACT365.

Relectura: 88.200 estados, 4.000 registros de flujos, 200 PV y cifras del resumen/PDF
coinciden. PDF de cinco páginas con precios y convenciones actuales. El comprobador
lee las cifras esperadas desde resultados actuales, sin perpetuar un precio antiguo.

**Recálculo efectivo en LibreOfficeDev 26.8**, reproducible con script incluido:

1. Se adulteran los caches de las 195.934 fórmulas en una copia temporal.
2. Perfil de no recálculo conserva todos los centinelas (control negativo).
3. Perfil OOXMLRecalcMode=0 sustituye todos: cero centinelas y cero errores.
   Máxima diferencia frente a caches auténticos: **1.5916157281e-12**.
   Precio recalculado **98.2691647949938**.
4. Otra copia con las 21 sigmas puestas a cero se recalcula a **105.35659626163304**,
   con todos los paths amortizando en5. Estados difieren de la referencia como máximo
   8.96e-16 y componentes de PV como máximo 4.98e-13.
5. El original XLSX y las fuentes conservan sus hashes. El script no ejecuta macros
   ni sobrescribe la entrega; verifica el SHA del libro y del PDF contractual.

Evidencia: [recalculo_validacion.json](../outputs/recalculo_validacion.json), vinculada
al hash del XLSX. `check_delivery.py` solo marca recálculo externo válido si ese hash
coincide; no acepta un certificado de una versión anterior. **Microsoft Excel no probado.**
La prueba no convierte las tablas estáticas de sensibilidades en una aplicación de escenarios.

Dos ejecuciones de valor, validación y generación producen los mismos resultados de
precio y archivos numéricos. Se verifica SHA de JSON/CSV al cierre. Los SHA-256 de PDF/XLSM
originales coinciden con SHA256SUMS; git diff de data/original está vacío.

## Reconciliación y límites

Anterior: 98.51983209787186. Nuevo: 98.26916479499383. Diferencia sobre paths comunes
-0.2506673028780, SE pareado .1281646202970. Se corrigen conjuntamente reloj y mapa;
la no linealidad del primer cruce impide sumar efectos de escenarios con bases diferentes.

La libertad de numerario indicada por el profesor significa invariancia teórica con
cambio consistente de medida/drift/descuento, no igualdad de dos estimadores finitos.
El terminal T20 alternativo da 98.1855226344 con los mismos números; no prueba fallo.

El precio actual tiene SE2.74535035 e IC aproximado [92.85545320,103.68287639], con
cola negativa y solo200paths. No incluye incertidumbre contractual, PCA o discretización.
La calibración externa de mercado, p-code/VBA y convergencia Browniana no se han auditado.
No se ha generado ni sustituido ninguna normal o componente principal.

## Cierre de la confirmación final

El objeto base de resultados.json coincide exactamente con el de b5b6b95. Los SHA-256
de los CSV de los200PV y los4.000flujos también coinciden, comprobados antes/después.
La opción A no exige recalcular con otro payoff: era el utilizado. Se regeneran las
entregas para retirar la advertencia contractual ya resuelta y se verifica su recálculo.
El escenario de recorte permanece solo como contrafactual expresamente descartado.
