# Fase 0 — Auditoría cuantitativa de inputs y contrato Snowblade

> **Documento histórico de Fase 0.** Las ambigüedades de cupón, floor y magnitud del
> objetivo se resolvieron después: ver [ACLARACIONES_PROFESOR.md](ACLARACIONES_PROFESOR.md).
> El estado y la solución vigentes están en [RESULTADOS.md](RESULTADOS.md). Las
> recomendaciones de este documento reflejan la evidencia disponible antes de las respuestas.
> La segunda ronda sustituye especialmente el mapa de volatilidades (primera sigma para F1,
> sin sigma para el spot) y el reloj de difusión (h=.5). No usar este mapa histórico como base vigente.

Fecha: 2026-11-13. Baseline: `15359f2` (main al clonar). Modo **standard**.
Veredicto: **PASS WITH CONDITIONS** para comenzar una valoración provisional por escenarios;
no autoriza confiar en un precio final. Conformidad de Fase 0: **FULL**.
No existe motor que validar todavía. No se ha calculado un precio, ejecutado VBA,
modificado originales, regenerado aleatorios ni sustituido PCA.

## 1. Contrato de auditoría y evidencia

Baseline fijado por la petición y AGENTS.md, antes de derivar resultados:

| ID | Requisito material | Criterio | Autoridad |
| --- | --- | --- | --- |
| B1 | Integridad e inspección del PDF/XLSM | SHA-256, lectura PDF, ZIP/XML, fórmulas y VBA estático | Usuario, Fase 0 |
| B2 | Calendario, forwards, LMM terminal y descuento | Índices y unidades explícitos; identidades verificables | PDF p. 1, AGENTS.md |
| B3 | Payoff y ambigüedades | Recursión, evento, principal y ejemplos deterministas | PDF p. 2 |
| B4 | Trazabilidad persistente | Auditoría, decisiones, estado, evidencia reproducible | Usuario |
| B5 | Parada | Sin simulación completa ni Excel/PDF de entrega | Usuario |

B1–B5 satisfechos dentro del alcance indicado. Prioridad de fuentes: PDF original,
XLSM original, decisiones aprobadas, código validado. Las propuestas de este informe
**no son decisiones contractuales aprobadas**. No se activan módulos de backtesting,
ML, cartera ni valoración fundamental de la skill: no aplican al ejercicio LMM.

Evidencia numérica: [auditoria_fase0.json](evidencias/auditoria_fase0.json), generado por
[scripts/audit_phase0.py](../scripts/audit_phase0.py). El JSON incluye las 70 fórmulas con
sus cachés, todos los errores de celda, estructura, hashes de cada parte ZIP,
inventario de procedimientos VBA, diagnósticos y 22 comprobaciones ejecutadas.
[calendario_recomendado.csv](evidencias/calendario_recomendado.csv) contiene **21 intervalos**:
20 de pago más uno auxiliar de descuento. No es un calendario suministrado por AFI.

Reproducción desde raíz (Python 3.12; versiones medidas en JSON):

```sh
(cd data/original && sha256sum -c SHA256SUMS)
python -m venv --system-site-packages /tmp/lmm-audit-venv
/tmp/lmm-audit-venv/bin/pip install -r scripts/requirements-audit.txt
pdftotext -layout data/original/2026_Ejercicio.pdf /tmp/lmm_enunciado.txt
/tmp/lmm-audit-venv/bin/python scripts/audit_phase0.py
```

## 2. Integridad y contenido de los originales — hechos verificados

| Original | SHA-256 | Resultado |
| --- | --- | --- |
| 2026_Datos.xlsm | `74d51e6531cc4b46e8cf7d2ddbe60ce930a10c0cf908942b39454d557c7ec0bd` | Coincide con SHA256SUMS antes y después |
| 2026_Ejercicio.pdf | `5bd06ea075689c9086eda2ac698b40d2f5a2a7079367bcfac824bd90bf875b76` | Coincide con SHA256SUMS antes y después |

Esto acredita identidad con el manifiesto versionado, no autenticidad externa frente a AFI.
PDF: dos páginas, leído mediante extracción de texto; tabla de los 20 cupones y cláusula
de cancelación contrastadas directamente. XLSM: CRC ZIP correcto, tres hojas visibles,
sin filas/columnas ocultas, sin nombres definidos ni tablas Excel, sin relaciones externas.
Dos gráficos en Correlaciones: chart1 referencia G117:I136 (cargas finales),
chart2 C7:V26 (matriz original); referencias XML completas en JSON. Las dimensiones incluyen celdas de formato vacías.
Cálculo: `fullCalcOnLoad=True`, `calcOnSave=False`; no se ha recalculado el libro.

| Hoja | Dimensión | Celdas no vacías | Fórmulas | Datos y rango efectivo |
| --- | --- | ---: | ---: | --- |
| Aleatorios | A1:GT66 | 12 267 | 0 | C3:GT22, C25:GT44, C47:GT66 |
| Correlaciones | A1:W139 | 1 999 | 0 | Tablas C7:V136 con separadores descritos abajo |
| Curva y volas | A1:F74 | 262 | 70 | A5:C74, E9:F29 y parámetros F5:F6 |

Las únicas fórmulas son `B5:B74 = $C$2 + A[fila]`: sus 70 cachés coinciden con la
fecha base más días. No hay fórmulas activas de LMM, payoff, PCA ni llamadas a CInterPol.
Los datos de aleatorios y PCA son **valores almacenados**, no funciones que deban recalcularse.
Errores: **20 `#N/A` en C76:V76**, fila adicional bajo la matriz 20×20 C56:V75.
No pertenecen a los inputs numéricos recomendados; leer rangos explícitos, nunca todo el used range.
La etiqueta C139 «Matriz Aprox» no tiene una matriz numérica debajo dentro del libro.

### VBA y CInterPol

Extracción estática con oletools 0.60.2; ningún procedimiento ejecutado. Seis módulos:
Sheet4, ThisWorkbook, Hoja1 y Hoja2 sin procedimientos; Interpolacion con una función,
Matrix con 66 procedimientos (1 974 líneas). Inventario y hashes de fuente en JSON.
Matrix contiene álgebra lineal, Jacobi/QR, funciones `MatRnd*` con `Randomize`/`Rnd` y
subs como QR/Solve_singolar_system que escriben sobre rangos de la selección. Su presencia
no prueba cómo se generaron los valores actuales; no deben ejecutarse en esta fase.
Las rutinas Jacobi trabajan con número de iteraciones `MaxLoops` (por defecto 1),
sin criterio de tolerancia de convergencia: es compatible con una descomposición aproximada,
pero no conocemos qué número de iteraciones originó los valores pegados.
La inspección del código fuente no constituye auditoría de seguridad del p-code; oletools
advierte que no verifica VBA stomping en el contenedor en memoria.

Fuente extraída: [cinterpol_fuente.bas](evidencias/cinterpol_fuente.bas).
`CInterPol(fecha, inCurva, modo)` busca dos nodos por bisección y aplica:

\[
w=\frac{x-x_a}{x_b-x_a},\qquad
P(x)=\exp((1-w)\log P_a+w\log P_b)\quad(\text{modo }0).
\]

Modo 1: interpolación lineal de factores. El opcional es Integer (por defecto 0);
calcula una variable `m` pero el `Select Case` usa `modo`. No implementa una spline.
Fuera del soporte extrapola usando el primer/último tramo; modos distintos de 0/1 no
tienen retorno definido explícito. No valida orden, duplicados ni positividad.
Recomendación: usar modo 0 y rechazar inputs fuera del soporte en Python. Fechas Excel
seriales con B5:C74 o días con A5/C5:A74/C74 dan el mismo peso si el origen es coherente;
no mezclar días desde origen con fechas seriales. Reproducción algebraica de sus nodos y
medias geométricas en puntos medios: error < 1e-14. **No es reconciliación ejecutada en Excel.**

## 3. Mapa de datos numéricos

### Curva y volatilidades

- C2: fecha de valoración **26/01/2022**, no la fecha del archivo o de esta auditoría.
- A5:A74: **70 nodos**, días 0…18 266 estrictamente crecientes.
- B5:B74: fecha calendario; C5:C74: factores positivos, rango
  **0.683637065429523…1.0156581094851727**, P(0,0)=1.
- Factores superiores a uno y curva no monótona son compatibles con tipos negativos;
  no recortar ni imponer monotonía a los descuentos.
- E5/F5: shifted = **0.03**; E6/F6: DT(años) = **0.5**.
- E9:E29: **21** periodos 1…21; F9:F29: volatilidades shifted lognormal anuales en decimal,
  positivas (0.21, …, 0.1992541389719689). No son volas normales ni porcentajes a dividir otra vez por 100.
- La tabla se titula «CAPLETS EUR 6M». No proporciona superficie temporal, strikes,
  algoritmo de stripping ni fechas de reset: tratar cada sigma como constante hasta reset
  es una **hipótesis mínima**, no calibración acreditada a precios de caplets.

### Correlaciones y componentes principales

| Rango | Significado observado / identidad contrastada |
| --- | --- |
| C6:V6, B7:B26 | Etiquetas 1…20 |
| C7:V26 | R simétrica 20×20, diagonal 1, positiva definida; R_ij=exp(-0.05 abs(i-j)) |
| C33:V52 | U: vectores ortonormales almacenados, columnas sin ordenar |
| C56:V75 | D: matriz casi diagonal almacenada; no es exactamente UᵀRU |
| C79:V79 | lambda: diagonal de D, no autovalores exactos certificados |
| C81:V81 / C82:V82 | lambda ordenada / índices originales; tres primeros: 2,20,10 |
| C83:V83 / C85:V85 | Fracciones / acumuladas; E85=0.9235035014404246 |
| C91:V110 | U diag(sqrt(lambda)), comprobado; C111:V111 contiene ceros extra |
| C117:E136 | B: tres columnas escaladas seleccionadas (2,20,10), no vectores unitarios puros |
| G117:I136 | A: B normalizada por la norma de cada fila, cargas finales 20×3 |

Resultados de diagnóstico independiente (no se reemplaza ninguna entrada):

- Autovalor mínimo de R: **0.02514912399**; error máximo UᵀU−I: **8.88e-16**.
- max abs(RU−U diag(lambda)) = **0.03926755**; max abs(D−UᵀRU) = **0.04805720**;
  D tiene términos fuera de diagonal de hasta **0.00427079**.
- Reconstrucción completa U diag(lambda) Uᵀ frente a R: error máximo **0.03424833**.
  Por tanto, la descomposición suministrada es aproximada; no afirmar que es exacta.
- Varianza explicada almacenada: **92.35035014%**. Diagonalización independiente de R,
  solo diagnóstica: **92.35086885%**. La cercanía del total no implica igualdad de vectores.
- B Bᵀ tiene diagonal **0.87719928…0.96006768**. Usar B directamente rebajaría las
  volatilidades marginales. A reproduce exactamente B/||B_fila|| y tiene diagonal
  A Aᵀ igual a 1 con error **2.22e-16**.
- R aproximada efectiva = A Aᵀ: rango ≤3, error máximo frente a R **0.15350247**,
  error Frobenius relativo **9.2675%**. La normalización implica que el 92.35% no es
  una afirmación de varianza total preservada por la matriz final normalizada.

**Decisión recomendada:** usar **G117:I136 literalmente**, conservando orden y signos;
no multiplicar otra vez por sqrt(lambda), no normalizar de nuevo. Usar A Aᵀ tanto en
el drift como en la difusión. R original queda como objetivo de comparación, no como
covarianza simultánea incompatible con solo tres factores. El riesgo PCA es distinto
del error Monte Carlo y debe quedar explícito en Fases 1–2.

### Aleatorios

C2:GT2 = paths 1…200, columnas; B3:B22, B25:B44, B47:B66 = pasos 1…20.
V1 en A3, V2 en A25, V3 en A47. Para factor k=1,2,3, paso n=1…20, path p=1…200:

\[
Z_{k,n,p}=\text{celda}(\text{fila}=s_k+n-1,\ \text{columna}=p+2),\quad s=(3,25,47).
\]

12 000 números finitos; 200 vectores de path distintos; sin fórmulas ni faltantes.
Medias por factor: **0.036134, −0.008511, 0.015687**; desviaciones muestrales:
**1.001452, 1.008520, 0.992887**. Correlación cruzada máxima absoluta: **0.017438**;
correlaciones de lag 1: **0.001113, −0.013242, 0.020509**.
Son compatibles en escala con N(0,1), no con incrementos ya escalados por sqrt(0.5).
KS contra normal estándar: p=0.0373, 0.9137, 0.6217; el primer bloque muestra desviación
muestral moderada. Son diagnósticos descriptivos, no prueba de independencia/normalidad
ni motivo para recentrar, transformar o regenerar muestras. Generador, seed y técnica
original desconocidos; el archivo fijo asegura reproducibilidad. Error estándar futuro
condicional a interpretar las 200 columnas como trayectorias independientes.

## 4. Calendario y esquema de forwards — reconstrucción recomendada

**Hechos:** 20 pagos semestrales, 10 años, ACT/365 (PDF); 21 sigmas, 20 filas PCA y
20 pasos aleatorios (XLSM). No hay calendario contractual, ajuste hábil, spot lag,
fixing lag ni correspondencia explícita de las 21 sigmas con resets.

**Hipótesis de trabajo H-cal:** t0=26/01/2022; t_i=t0+6i meses calendario sin ajuste,
i=0…21. Último pago t20=26/01/2032; numerario terminal t21=26/07/2032. Los 20 pagos
son t1…t20, nunca se añade un cupón 21. Esto interpreta N+1 como un semestre auxiliar,
no como la última fecha de la curva (50 años, sin factores para modelizarla).

\[
\delta_i=\frac{\operatorname{días}(t_{i+1}-t_i)}{365},\quad
F_i(t)=\frac{P(t,t_i)/P(t,t_{i+1})-1}{\delta_i},\quad i=0,\ldots,20.
\]

- F0 fija hoy para [t0,t1]; no se simula. Vol F9 sin uso estocástico.
- F_i, i=1…20, corresponde a fila PCA 116+i y vol **F(9+i)**: 20 tipos estocásticos.
- Cupón j usa fixing **r_j=F_(j−1)(t_(j−1))** y paga en t_j; los dos primeros son fijos.
- F20 no entra en el cupón 20, pero sí en P(t20,t21) y en drift de tipos anteriores.
- Paso n usa columna p de los tres bloques Z para avanzar [t_(n−1),t_n], evolucionando
  solo i≥n. Se congela F_n tras llegar a su reset t_n. El paso 20 sirve al descuento final.
- Los 20 pasos no son 20 índices de madurez intercambiables: cada Z es un shock común
  que se mezcla mediante una fila distinta de A para cada forward vivo.

Calendario completo y forwards: CSV adjunto. Primer accrual **181/365**, segundo **184/365**;
periodos con año bisiesto difieren. DT=0.5 no es identidad ACT/365. Recomendación:
usar tiempo de difusión h_n=(t_n−t_(n−1))/365, coherente con curva, y cuantificar en
Fase 1 la sensibilidad a malla académica exacta de 0.5 años (fechas sintéticas/fraccionarias).
No mezclar silenciosamente h=0.5 con devengos declarados como seis meses exactos.

Con H-cal y modo 0: P(0,t20)=**0.9796669785616863**, P(0,t21)=**0.9738424983829392**;
forwards iniciales en **[−0.00441141435692, 0.01199471476675]**, todos F_i+0.03>0.
Se verifica la identidad P(0,t_m)=prod_(i=0)^(m−1)(1+delta_i F_i(0))^(-1).
Estos son datos de reconstrucción, **no un precio del Snowblade**.

Alternativa H-cal-10: terminal en t20 con F0…F19 y una sigma sobrante; o 20 tipos
con resets .5…10 y producto que empieza en .5 (inicio diferido). No equivalen a H-cal.
La primera requiere solo 19 forwards aleatorios; la segunda desplaza los pagos respecto
a los diez años del PDF. H-cal usa todas las dimensiones con menor excepción, pero
**la coincidencia dimensional no demuestra la intención contractual**.

## 5. LMM shifted lognormal bajo medida terminal

Numeraire B(t)=P(t,t21), medida Q^21. Definir X_i=F_i+s, s=.03;
a_i = fila i de A (i=1…20); lambda_i(t)=sigma_i a_i antes de t_i y cero después.
Las sigmas se mapean según H-cal (sigma_i = celda F(9+i)). Entonces:

\[
\frac{dX_i(t)}{X_i(t)}=\mu_i(t)dt+\boldsymbol\lambda_i(t)\cdot d\mathbf W^{21}(t),
\qquad
\mu_i(t)=-\sum_{j=i+1}^{20}
 \frac{\delta_j(F_j(t)+s)}{1+\delta_jF_j(t)}
 \boldsymbol\lambda_i(t)\cdot\boldsymbol\lambda_j(t).
\]

Derivación: el forward i es martingala bajo el bono de su pago t_(i+1);
el cambio al bono t21 agrega la suma negativa de volatilidades de los factores de bono
posteriores. El shift aparece en el **numerador**, mientras el denominador contiene
F_j sin desplazar. No incluir j=i; para i=20 la suma es vacía y mu20=0. No exigir que
todos los drifts sean negativos: los productos escalares pueden tener distinto signo.

Para la primera implementación se recomienda log-Euler de drift congelado por paso:

\[
X_i(t_n)=X_i(t_{n-1})\exp\!\left[
 (\mu_i(t_{n-1})-\tfrac12\|\lambda_i\|^2)h_n
 +\sqrt{h_n}\,\lambda_i\cdot\mathbf Z_{n,p}\right],\quad i\ge n.
\]

Evaluar todos los drifts con el mismo estado anterior (sin actualización secuencial in-place).
A ya normalizada implica ||lambda_i||²=sigma_i². Es una aproximación de discretización,
no solución exacta del LMM. Conserva X>0 en aritmética exacta; validar además
1+delta_i F_i>0 y finitud, sin clipping silencioso. No se ha implementado este paso.
Con solo 20 shocks no hay ruido adicional autorizado para refinar la malla:
no presentar un test de convergencia de subpasos como hecho ya verificado.

### Mecanismo de descuento e índices

Para pago en t_m, m=1…20:

\[
B(t_m)=P(t_m,t_{21})=
 \prod_{j=m}^{20}(1+\delta_jF_j(t_m))^{-1},\qquad
V_0=P(0,t_{21})\,E^{21}\!\left[
 \sum_{m=1}^{20}\frac{CF_m}{B(t_m)}\right].
\]

El producto empieza en **j=m**, no m−1: ese forward ya ha fijado en t_m pero su intervalo
[t_m,t_(m+1)] sigue formando parte del bono. Para m=20 queda **un factor F20**, no un
producto vacío. Solo en t21 B=1. Numerario inicial calculado por interpolación.
El estimador de 200 paths promediará **sumas por trayectoria** (cupones y principal
correlacionados); el error estándar se calcula sobre esos 200 PV, no sobre 4 000 pagos.
No sustituir B(t_m) por P(0,t_m) dentro de la expectativa. No acumular una cuenta monetaria.
La identidad estática de los productos y su límite vacío en t21 se ha ejecutado;
la martingala y el caso sigma=0 del futuro motor siguen pendientes.

## 6. Payoff matemático y ambigüedades materiales

Nominal H, recomendación H=100 para reporting. Bajo lectura de tasas anualizadas:

\[
c_1=c_2=.01,\qquad
c_j=c_{j-1}+b_j-r_j\quad(j=3,\ldots,20),
\]

con b3=b4=0; b5…b8=.01; b9…b12=.0125; b13…b16=.015; b17…b20=.02.
Devengo pagadero q_j=delta_(j−1)c_j. **No floor ni cap**: no hay ninguno en el PDF.
Un cupón negativo reduce el acumulado neto en el escenario base y es flujo negativo
del inversor. No cambiar la memoria c_(j−1) por el importe devengado q_(j−1).

Escenario base recomendado, **interpretación no aprobada**: objetivo de intereses
efectivos netos acumulados desde origen S_m=sum_(j=1)^m q_j; tau=min{m:S_m≥.04},
y tau=20 si no se cruza antes. Test al pago después de incluir el cupón del evento,
con cupón **completo sin recortar el exceso**. Definir tau por primer cruce aunque S
pueda disminuir. Cada cashflow:

\[
CF_m=H\,\mathbf1_{m\le\tau}\,q_m+H\,\mathbf1_{m=\tau}.
\]

Principal exactamente una vez, incluido tau=20. No sumar principal a S. El evento de
autocall y el vencimiento natural deben etiquetarse por separado aunque ambos den tau=20.

### Escenarios que debe reportar la primera valoración

| Ambigüedad | Escenario alternativo operacional | Riesgo / recomendación |
| --- | --- | --- |
| «Anuales acumulados» | S_m=sum c_j; comparar 4% en cada pago | Cambia fechas aun con mismo cupón y r=0; no confundir tasas con efectivo |
| Intereses de cada año | S_(2k)=q_(2k−1)+q_(2k), test anual ≥.04 y reinicio anual | Autocall mucho más tardía que acumulación desde origen |
| Anualización desde origen | S_m=(sum q_j)/(sum delta_(j−1)) | Umbral medio anual distinto de objetivo de efectivo |
| Cupón efectivo semestral | q_j=c_j, recursión literal; o restar delta*r_j en recursión de importes | Dos contratos distintos; fijar unidades de TODOS los términos antes de valorar |
| Cupones negativos | Floor cero aplicado al estado c_j; o solo al pago q_j | Alteran también recursión/trigger; base literal sin floor |
| Exceso de objetivo | Recortar pago final a .04−S_(m−1) | No viene indicado; base cupón completo |
| Trigger/fecha de fixing | Test anual frente a cada pago; fixing in arrears en vez de advance | Cambian exposición y tiempo de amortización; base advance y test por pago |
| Fecha base/terminal/malla | H-cal-10, DT=.5, ajuste hábil | Índices y descuentos cambian; no inferir calendario aprobado de la plantilla |

No es necesario un grid de todas las combinaciones. Primero comparar base y alternativas
D01/D02 con los mismos 200 paths; sensibilidades de floor y calendario separadas y rotuladas.
Ningún escenario convierte una conjetura en condición contractual verificada.

### Ejemplos deterministas ejecutados (no valoración)

Con referencia **r_j=0** para j≥3, c1…c8 = 1%,1%,1%,1%,2%,3%,4%,5%.
En el calendario recomendado, S5=**0.02997260274**, S6=**0.04509589041**: objetivo efectivo
cruza en **periodo 6**. Principal H y cupón 0.01512328767 H en t6, sin pagos posteriores.
La suma de tasas cruza en **periodo 4**. Test de promedio anual de las dos tasas de cada
pareja cruza al final del **periodo 8** (el efectivo de esa pareja también supera 4%).
Las fechas divergentes ya prueban materialidad contractual sin calcular un PV.
Para ausencia de autocall: elegir r3=.02 y r_j=b_j desde j4; c3…c20=−.01,
el acumulado tras c1,c2 nunca llega a .04 y el nominal se devuelve en t20.
Este último ejemplo es una construcción algebraica, no una prueba ejecutada del motor.

## 7. Hallazgos y condiciones de avance

| Severidad | Hallazgo / evidencia | Impacto | Corrección mínima y verificación |
| --- | --- | --- | --- |
| HIGH | D01/D02 abiertos, PDF p.2; ejemplo cruza en 4/6/8 | Un precio único no queda determinado | Motor parametrizado; comparar mismas trayectorias; confirmar lectura antes de entrega final |
| HIGH | Calendario no suministrado; 21 volas/20 PCA/20 shocks | Off-by-one en fixing, sigma y numerario | Implementar mapa H-cal explícito; test de cada índice, F20 solo auxiliar y principal único |
| HIGH | PCA aproximada y final normalizada; error max R−AAᵀ=.1535 | Mezclar covarianzas viola dinámica del modelo simulado | A literal y AAᵀ en ambos términos; comprobar varianzas/covarianzas y bono martingala |
| MEDIUM | 200 paths y muestra fija, procedencia RNG desconocida | Precisión MC limitada; incertidumbre estructural no incluida en IC | No ampliar/recentrar; reportar SE, IC condicional y dispersión de escenarios |
| MEDIUM | Sigma constante y malla semestral son hipótesis | Riesgo de parametrización y discretización | Rotular primera valoración provisional; validar sigma=0, martingalas y sensibilidad DT |

**Siguiente mínimo:** lector con validaciones y mapa explícito; forwards/PCA sin transformaciones
extra; log-Euler terminal; payoff por escenarios; descuento por producto; tests deterministas
sigma=0, último drift cero, signos/shift, ausencia de autocall y cruce con cupón completo,
principal una vez, identidad de bonos y martingalas con tolerancias MC justificadas.
Después reportar por 100: cupones/principal, autocall por fecha, supervivencia, duración,
SE e IC sobre los 200 PV. Comparar diferencias contractuales con ese SE. No exigir más
infraestructura antes de esa primera valoración.

Confianza de auditoría: **HIGH en datos almacenados y álgebra; limitada en interpretación
contractual**. No auditados: ejecución real Excel/VBA, p-code, procedencia externa de datos,
calibración a precios de mercado, estabilidad/convergencia del motor y valoración final,
porque el motor y la entrega pertenecen a fases posteriores.
