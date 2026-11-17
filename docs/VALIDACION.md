# Validación cuantitativa y de entregas

**Veredicto: PASS WITH CONDITIONS** para utilizar la estimación del caso documentado.
No equivale a precio exacto, contrato enteramente confirmado ni recálculo validado en Excel.
La referencia escalar es una implementación separada en el mismo workspace; no hubo
revisión por otro agente. Se mantienen los originales y las 200 trayectorias.

## Evidencia ejecutada del motor

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/validate_solution.py
```

**17 tests PASS**, sin omisiones:

- Hashes, rechazo de corrupción y lectura; interpolación de nodos y extrapolación inválida.
- Calendario, ACT/365, identidad curva/forwards y mapa exacto de sigmas/cargas.
- Drift terminal con shift, numerador/denominador y último drift nulo.
- Tipos congelados al reset, fijaciones advance y último factor de descuento F20.
- Último forward como exponencial de incrementos telescópicos de drift cero.
- Sigma=0: flujos y descuento directo coinciden; nominal una vez.
- Repetición determinista, dominio X>0 y 1+delta F>0, varianza marginal PCA.
- Estados/configuración inválidos fallan sin clipping ni datos fabricados.
- Referencia escalar independiente para todos los estados y flujos de los 200 paths.
- Diagnósticos de martingalas con tolerancia MC; agregación y SE sobre PV completos.
- Payoff r=0, cupón completo del evento, memoria negativa, ausencia de autocall,
  cruce por igualdad, autocall inmediato de fixture y entradas inválidas.

[outputs/validacion.json](../outputs/validacion.json) registra:

| Contraste | Máximo error absoluto |
| --- | ---: |
| Forwards vectorizados vs escalar | 1.4571677198e-15 |
| Cupones vectorizados vs escalar | 5.9507954120e-14 |
| Principal vectorizado vs escalar | 0 |
| 200 PV vectorizados vs escalar | 2.2737367544e-13 |
| Sigma=0 vs descuento directo de flujos | 7.1054273576e-14 |

Se contrasta una implementación escalar con sumas explícitas y búsqueda independiente
de interpolación, que no llama a los kernels de simulación, payoff o valoración del motor.
Las dos comparten los mismos datos y convenciones; no prueban que la interpretación
contractual ni la asignación temporal sean únicas o hayan sido confirmadas externamente.

230 diagnósticos P(t_m,t_k)/P(t_m,T*) dentro de 5SE, máximo |z|=2.02858.
No prueba de ausencia de sesgo: comparten muestra y están correlacionados. El esquema
predictor-corrector cambia el precio +.03635 con SE pareado .01124; no se realizó
convergencia por refinamiento Browniano, que requeriría ruido adicional no autorizado.

## Entregas

```sh
python scripts/build_delivery.py
python scripts/check_delivery.py
```

[outputs/entrega_validacion.json](../outputs/entrega_validacion.json):

- Libro nuevo XLSX: **191 914 fórmulas**, sin VBA ni errores de celda cacheados.
- Relectura y reconciliación de **88 200** forwards de estado, **4 000** filas de flujos
  y **200** PV de trayectorias, además del precio y SE del resumen.
- PDF de **5 páginas**: precio, SE e intervalo coinciden con resultados máquina.
  Páginas de resultados y fórmulas inspeccionadas por render; sin desbordamientos observados.
- **Recálculo con aplicación Excel/LibreOffice: NO EJECUTADO.** Se verifican las caches,
  no la ejecución de las fórmulas por un motor Excel externo. Esa limitación figura en
  el libro y en la memoria; no afirmar equivalencia de ejecución entre aplicaciones.

Dos ejecuciones consecutivas de `value_snowblade.py` producen SHA-256 idénticos de
resultados.json, path_pv.csv y cashflows.csv (verificación ejecutada al cierre).
Los SHA-256 de ambos originales coinciden con el manifiesto al terminar; `git diff`
de `data/original/` vacío respecto a main.

## Evidencia histórica y riesgo residual

Fase 0: 22 comprobaciones PASS y extracción VBA estática registradas en
[docs/evidencias/auditoria_fase0.json](evidencias/auditoria_fase0.json).
Los tres artefactos históricos se habían reproducido con hashes idénticos. No se
recalculan para sustituir los inputs de la plantilla. CInterPol no se ha ejecutado en VBA.

PCA suministrada aproximada; solo 200 columnas con procedencia RNG desconocida;
IC aproximado frente a cola negativa. Convenciones sin confirmación del profesor:
fechas/terminal, fixing, mapa sigma y cupón completo sin recortar exceso. Ver
[DECISIONES.md](DECISIONES.md) y [RESULTADOS.md](RESULTADOS.md). No se auditó calibración
contra precios de mercado externos ni se afirma que haya precisión subpunto.
