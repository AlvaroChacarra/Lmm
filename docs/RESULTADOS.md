# Solución actualizada tras la segunda ronda del profesor

**Precio estimado: 98.2691647950 por 100.** Se usa fixing advance, h=.5 y
primera sigma para el primer forward futuro, conservando los 200 paths originales.
El cupón completo al autocall es lectura de trabajo de la respuesta «Correcto»,
que no selecciona expresamente entre las dos opciones planteadas.

## Resultado actual

| Magnitud | Valor |
| --- | ---: |
| Precio | 98.2691647950 |
| PV cupones | -2.2533577743 |
| PV principal | 100.5225225693 |
| SE sobre 200 PV completos | 2.7453503522 |
| IC 95% Student aproximado | [92.8554532016, 103.6828763883] |
| Vida media Q terminal | 3.3801643836 años |
| Autocalls / vencimientos sin autocall | 185 / 15 |
| Paths con cupón negativo / PV negativo | 29 / 5 |
| Cupones pagados negativos | 276 |
| PV mínimo / máximo | -310.6175641748 / 138.8841210483 |
| Mediana del PV | 103.9453260046 |

El peor path sigue siendo el 71. Omitirlo daría 100.3238719757:
solo diagnóstico de influencia, nunca un precio alternativo admisible. La cola es parte
del contrato sin floor; devolver el principal no limita los pagos negativos de cupones.
La media y el SE están correctamente calculados, pero n=200 y la asimetría limitan la
cobertura real del IC. No incluye riesgo de PCA, parametrización ni discretización.
Probabilidades y vida media corresponden a Q terminal, no a pronósticos físicos.

## Interpretación operativa de las respuestas

Detalle y citas en [ACLARACIONES_PROFESOR.md](ACLARACIONES_PROFESOR.md).

- **Spot:** índice 0, intervalo inicial conocido [t0,t1], sin difusión y sin sigma.
- **Forward F_i, i=1…20:** intervalo [t_i,t_(i+1)]; PCA fila 116+i; sigma de
  Curva y volas!F(8+i), es decir F9:F28. La fila F29 se conserva como extra no utilizada.
- **Cupones:** tasas anualizadas; devengo delta_(j−1)=días(t_j−t_(j−1))/365;
  r_j=F_(j−1)(t_(j−1)), con primeros dos cupones fijos.
- **Dinámica:** h=.5 para drift, término de Itô y shock sqrt(h), según partición 30/360.
  No se cambia delta a .5 ni se transforma ACT/365 del cupón a 30/360.
- **Numerario:** P(t,t21), con t20=26/01/2032 último pago y t21=26/07/2032 auxiliar.
  El profesor admite elegir otro bono terminal: hay que cambiar medida/drift/descuento
  coherentemente. No exige precios idénticos con una realización finita de 200 paths.
- **Exceso:** cupón completo mantenido. No se afirma que «Correcto» ante una disyuntiva
  descarte inequívocamente el recorte. Su efecto actual se muestra abajo.
- **Supuestos que se mantienen:** aniversarios desde C2 sin ajuste hábil ni lag;
  sigma constante hasta reset. No se atribuye al profesor una respuesta que no dio.

## Reconciliación con la valoración anterior

| Caso | Precio |
| --- | ---: |
| Anterior: ACT/365 en difusión, sigma1 asignada al spot sin uso | 98.5198320979 |
| Nuevo: h=.5, sigma1 asignada a F1 | 98.2691647950 |
| Diferencia nueva − anterior | -0.2506673029 |
| SE de esa diferencia pareada | 0.1281646203 |

Se cambian ambos parámetros según las respuestas; el efecto conjunto no debe inferirse
sumando diferencias de escenarios con otra base, porque puede cambiar el primer cruce.
La configuración anterior sigue siendo reproducible con
`Config(diffusion_clock='act365', vol_offset=1)`; ya no es el caso vigente.

## Controles y sensibilidades actuales

| Escenario | Precio | Delta base | SE pareado |
| --- | ---: | ---: | ---: |
| predictor_corrector | 98.3074505558 | +0.0382857608 | 0.0119943601 |
| act365_diffusion_counterfactual | 98.2909499837 | +0.0217851887 | 0.0146460702 |
| terminal_10_years | 98.1855226344 | -0.0836421606 | 0.0606962270 |
| second_vol_row_counterfactual | 98.5293632017 | +0.2601984067 | 0.1299007896 |
| zero_volatility | 105.3565962616 | +7.0874314666 | 2.7453503522 |
| coupon_capped_at_target_not_base | 97.0558651439 | -1.2132996511 | 0.0594628077 |
| arrears_counterfactual | 90.6222680483 | -7.6468967467 | 2.6912749332 |

Arrears, segunda sigma y reloj ACT/365 son **contrafactuales de trazabilidad**; no se
presentan como lecturas contractuales igualmente abiertas tras la segunda respuesta.
El recorte del objetivo conserva relevancia por la respuesta breve no inequívoca.
Predictor-corrector no demuestra convergencia por refinamiento Browniano. El cambio de
numeraire se compara con números comunes, sin exigir igualdad por path o de las medias.

## Autocall por periodo bajo Q terminal

| Periodo | Paths | Frecuencia |
| --- | ---: | ---: |
| 1 | 0 | 0% |
| 2 | 0 | 0% |
| 3 | 0 | 0% |
| 4 | 7 | 3.5% |
| 5 | 116 | 58% |
| 6 | 37 | 18.5% |
| 7 | 10 | 5% |
| 8 | 5 | 2.5% |
| 9 | 3 | 1.5% |
| 10 | 3 | 1.5% |
| 11 | 1 | 0.5% |
| 12 | 1 | 0.5% |
| 13 | 1 | 0.5% |
| 14 | 0 | 0% |
| 15 | 0 | 0% |
| 16 | 0 | 0% |
| 17 | 0 | 0% |
| 18 | 0 | 0% |
| 19 | 1 | 0.5% |
| 20 | 0 | 0% |
| Vencimiento sin autocall | 15 | 7.5% |

## Fórmulas y evidencias

\[
c_1=c_2=.01,\quad c_j=c_{j-1}+b_j-F_{j-1}(t_{j-1}),\quad
S_m=\sum_{j=1}^m\delta_{j-1}c_j,\quad
\tau=\min(\{m:S_m\ge .04\}\cup\{20\}).
\]

b3=b4=0; b5…8=.01; b9…12=.0125; b13…16=.015; b17…20=.02.
CF_m=100 1_(m<=tau) delta_(m−1)c_m +100 1_(m=tau), sin floor ni recorte en el caso base.
Con X_i=F_i+.03 y lambda_i=sigma_i a_i:

\[
\mu_i=-\sum_{j=i+1}^{20}\frac{\delta_j(F_j+.03)}{1+\delta_jF_j}
\lambda_i\cdot\lambda_j,\quad
X_i'=X_i\exp[(\mu_i-\|\lambda_i\|^2/2)h+\sqrt h\,\lambda_i\cdot Z],\quad h=.5.
\]

\[
P(t_m,t_{21})=\prod_{j=m}^{20}(1+\delta_jF_j(t_m))^{-1},\quad
V=\frac{P(0,t_{21})}{200}\sum_p\sum_m\frac{CF_{p,m}}{P_p(t_m,t_{21})}.
\]

19 tests superados; contraste de todos los PV con referencia escalar, máximo error
2.842e-13; sigma=0 coincide con descuento directo.
230 controles de bonos (máximo |z|=2.026328) y 60 caplets contra
Black desplazado (máximo |z|=1.826102), usando exclusivamente normales originales.
Son verificaciones con tolerancias MC, no pruebas de cobertura exacta o convergencia.

## Reproducción y entregas

```sh
python -m pip install -r requirements.txt
python scripts/value_snowblade.py
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/validate_solution.py
python scripts/build_delivery.py
python scripts/recalculate_delivery.py
python scripts/check_delivery.py
```

El PDF requiere DejaVu en `/usr/share/fonts/truetype/dejavu/`. El recálculo requiere
`soffice` en PATH o `--soffice /ruta/soffice`, trabaja solo sobre copias temporales
y usa controles centinela y sigma=0. Microsoft Excel no está probado.

- [Excel actualizado](../entrega/Snowblade_LMM.xlsx) y [memoria PDF](../entrega/Memoria_Snowblade.pdf).
- [Resultados JSON](../outputs/resultados.json), [200 PV](../outputs/path_pv.csv),
  [4.000 flujos](../outputs/cashflows.csv) y [referencia/Black](../outputs/validacion.json).
- [Recálculo real](../outputs/recalculo_validacion.json) y [relectura de entrega](../outputs/entrega_validacion.json).

El XLSX es nuevo y sin VBA, con todas las 21 sigmas originales visibles y la fila extra
identificada. No se convierte ni modifica el original. Las tablas de escenarios son
estáticas y requieren regeneración si cambia la configuración.
