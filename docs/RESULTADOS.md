# Solución numérica del Snowblade

**Precio estimado: 98.51983210 por 100 de nominal.** Caso base con las tres condiciones
confirmadas por el profesor, 200 paths originales y convenciones residuales explícitas.
No es una valoración con precisión de céntimos: SE=2.63848960.

## Resultado base

| Magnitud | Valor |
| --- | ---: |
| Precio | 98.5198320979 |
| PV cupones | -1.9627063651 |
| PV principal | 100.4825384630 |
| Error estándar, 200 PV completos | 2.6384896011 |
| IC 95% aproximado Student (199 g.l.) | [93.3168452620, 103.7228189337] |
| Vida media bajo medida terminal | 3.3826438356 años |
| Autocancelan | 185 / 200 (92.5%) |
| Vencen sin autocall | 15 / 200 (7.5%) |
| Paths con algún cupón pagado negativo | 29 / 200 |
| Cupones pagados negativos | 276 |
| Paths con PV neto negativo | 4 / 200 |
| Mínimo / máximo PV de trayectoria | -292.7628494254 / 139.7480358069 |
| Mediana PV de trayectoria | 103.5984172196 |

El PV del principal supera 100 por la estructura inicial de descuentos y la devolución
frecuentemente temprana; devolución a la par no significa PV igual a 100. Los cupones
netos tienen PV negativo por la cola de escenarios supervivientes con tipos altos.
Los pagos negativos pueden superar el principal: el contrato no establece floor ni
límite de responsabilidad del inversor. No se han excluido ni winsorizado escenarios.
La trayectoria 71 es la peor; omitirla llevaría la media a 100.48607673. Esa cifra se
registra solo como influencia muestral, **no como una estimación admisible**.

El IC supone columnas independientes y una aproximación de la distribución de la media.
La cola muy asimétrica y n=200 limitan su cobertura real. No incluye incertidumbre por
calendario, sigma, discretización ni aproximación PCA. No se generan shocks adicionales.

## Autocall por fecha bajo Q terminal

| Periodo | Paths | Frecuencia |
| --- | ---: | ---: |
| 1–3 | 0 | 0% |
| 4 | 10 | 5% |
| 5 | 113 | 56.5% |
| 6 | 34 | 17% |
| 7 | 12 | 6% |
| 8 | 6 | 3% |
| 9 | 3 | 1.5% |
| 10 | 3 | 1.5% |
| 11 | 1 | 0.5% |
| 12 | 1 | 0.5% |
| 13 | 1 | 0.5% |
| 14–18 | 0 | 0% |
| 19 | 1 | 0.5% |
| 20 autocall | 0 | 0% |
| 20 vencimiento sin autocall | 15 | 7.5% |

Son frecuencias **bajo la medida del bono terminal**, no probabilidades físicas.
Lo mismo se aplica a la vida media publicada. Contajes de autocall más supervivientes=200.

## Convenciones y sensibilidades sobre los mismos shocks

Base: fecha 26/01/2022, pagos semestrales sin ajuste hasta 26/01/2032; bono terminal
26/07/2032; forward F0 fijo, F1…F20 aleatorios. Fixing advance. Volatilidades de F1…F20
=F10:F29, constantes hasta reset. Cargas finales originales y A Aᵀ en ambos términos.
ACT/365 tanto en devengo como en reloj de difusión; log-Euler; cupón completo al cruce.

| Cambio aislado | Precio | Diferencia base | SE de diferencia pareada |
| --- | ---: | ---: | ---: |
| Predictor-corrector | 98.5561817103 | +0.0363496124 | 0.0112374740 |
| Reloj de difusión h=.5 | 98.5293632017 | +0.0095311038 | 0.0272010800 |
| Bono terminal t20 (10 años calendario) | 98.4768989329 | -0.0429331649 | 0.0714644716 |
| F1 usa primera fila de volatilidad | 98.2909499837 | -0.2288821142 | 0.1279515318 |
| Sigma=0, control determinista | 105.3565962616 | +6.8367641638 | 2.6384896011 |
| Cupón recortado al objetivo (no base) | 97.3279125493 | -1.1919195485 | 0.0588458159 |

No se mantienen escenarios de floor o cupón efectivo: el profesor los ha descartado.
La sensibilidad a cupón recortado sigue siendo material porque esa condición no se
confirmó expresamente. Predictor-corrector no acredita convergencia temporal: no añade
subpasos Brownianos. El cambio de bono terminal implica cambio de medida y dimensión;
la diferencia pareada es una comparación de implementaciones con números comunes.

## Fórmulas operacionales

Con c1=c2=.01, b3=b4=0, b5…8=.01, b9…12=.0125, b13…16=.015 y b17…20=.02:

\[
c_j=c_{j-1}+b_j-F_{j-1}(t_{j-1}),\qquad
S_m=\sum_{j=1}^m\delta_{j-1}c_j,\quad
\tau=\min(\{m:S_m\ge.04\}\cup\{20\}).
\]

\[
CF_m=100\,1_{m\le\tau}\delta_{m-1}c_m+100\,1_{m=\tau}.
\]

Con X_i=F_i+.03, lambda_i=sigma_i a_i y medida Q^21:

\[
\mu_i=-\sum_{j=i+1}^{20}\frac{\delta_j(F_j+.03)}{1+\delta_jF_j}
\lambda_i\cdot\lambda_j,\quad
X_i'=X_i\exp[(\mu_i-\|\lambda_i\|^2/2)h+\sqrt h\,\lambda_i\cdot Z].
\]

\[
P(t_m,t_{21})=\prod_{j=m}^{20}(1+\delta_jF_j(t_m))^{-1},\quad
V=\frac{P(0,t_{21})}{200}\sum_p\sum_m\frac{CF_{p,m}}{P_p(t_m,t_{21})}.
\]

Los errores frecuentes son aplicar ACT/365 dos veces, borrar la memoria negativa,
usar F+s en el denominador, incluir j=i en el drift, omitir F20 del descuento final,
o calcular SE sobre pagos en lugar de trayectorias. Tests cubren esos caminos.

## Reproducir, leer y entregar

```sh
python -m pip install -r requirements.txt
python scripts/value_snowblade.py
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/validate_solution.py
python scripts/build_delivery.py
python scripts/check_delivery.py
```

`check_delivery.py` usa además pypdf (incluido en requirements.txt). La generación PDF
requiere las fuentes DejaVu en `/usr/share/fonts/truetype/dejavu/`.

- [Excel con implementación](../entrega/Snowblade_LMM.xlsx): inputs, calendario, shocks,
  estados con fórmulas de LMM, cashflows, 200 PV, resumen y sensibilidades.
- [Memoria PDF](../entrega/Memoria_Snowblade.pdf): 5 páginas, cifras, método y límites.
- [Resultados máquina](../outputs/resultados.json), [200 PV](../outputs/path_pv.csv),
  [4000 registros de flujos](../outputs/cashflows.csv),
  [contraste numérico](../outputs/validacion.json) y
  [comprobación de entregas](../outputs/entrega_validacion.json).

Los originales no se han convertido ni modificado. El XLSX es nuevo, no contiene VBA.
Sus fórmulas llevan caches numéricas de Python contrastadas con referencia escalar.
No se ha ejecutado recálculo en Excel/LibreOffice: no afirmar equivalencia de ejecución
entre motores. El libro expone esa limitación y debe regenerarse si cambia el calendario.
