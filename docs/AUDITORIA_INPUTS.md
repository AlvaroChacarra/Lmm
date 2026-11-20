# Mapa definitivo de fuentes, datos e índices

Este es el mapa vigente. Se sustituyó el calendario provisional de la auditoría inicial
porque asignaba la primera sigma al tipo inicial; el profesor aclaró que ese tipo es
spot y que la primera sigma pertenece al primer forward futuro.

## Originales y lectura

| Fichero | SHA-256 |
| --- | --- |
| 2026_Datos.xlsm | `74d51e6531cc4b46e8cf7d2ddbe60ce930a10c0cf908942b39454d557c7ec0bd` |
| 2026_Ejercicio.pdf | `5bd06ea075689c9086eda2ac698b40d2f5a2a7079367bcfac824bd90bf875b76` |

Están en `data/original/`. El manifiesto comprueba identidad con los ficheros recibidos,
no autenticidad externa frente a AFI. El PDF tiene dos páginas. El XLSM tiene tres
hojas visibles y 70 fórmulas activas: las fechas `B5:B74 = $C$2 + A[fila]` de la curva.
PCA y aleatorios son valores almacenados, no fórmulas que haya que recalcular.
Hay 20 `#N/A` en Correlaciones!C76:V76, fuera de los rangos numéricos utilizados.

## Rangos usados

| Hoja / celda o rango | Dato | Uso |
| --- | --- | --- |
| Curva y volas!C2 | 26/01/2022 | Fecha de origen, no fecha actual de ejecución |
| A5:A74 / B5:B74 / C5:C74 | 70 nodos: días / fechas / descuentos | Interpolación log-lineal de factores |
| F5 | 0.03 | Shift, en decimal |
| F6 | 0.5 | Paso temporal de difusión |
| E9:E29 / F9:F29 | Periodos 1…21 / sigmas | Primeras veinte para F1…F20; F29 extra conservada |
| Correlaciones!C7:V26 | Matriz objetivo 20×20 | Diagnóstico de aproximación, no covarianza simultánea del motor de tres factores |
| C117:E136 | Tres cargas escaladas antes de normalizar filas | Diagnóstico de la preparación de la plantilla |
| G117:I136 | Cargas finales A, 20×3 | Uso literal, sin sqrt(lambda) ni normalización adicionales |
| Aleatorios!C2:GT2 | Paths 1…200 | Cada columna es una trayectoria |
| C3:GT22 / C25:GT44 / C47:GT66 | Factores V1 / V2 / V3 | Cada bloque tiene veinte pasos y 200 paths |

Todas las tasas/sigmas se leen como decimales. Los factores de descuento son positivos
y pueden superar 1; no se impone monotonía a una curva con tipos negativos. Los shocks
son compatibles en escala con normales estándar: se aplica `sqrt(h)` una sola vez.
Su generador/seed no se conoce; no se recentran ni se sustituyen para normalizar la muestra.

## Calendario y correspondencia final

`t_i` es el aniversario de seis meses calendario desde C2, sin ajuste hábil ni lag.
Los pagos son t1…t20 (26/01/2032); t21 (26/07/2032) es solo el terminal auxiliar.
`delta_i = días(t_(i+1)−t_i)/365`. La partición estocástica es `u_i=i/2`, con h=.5;
no es necesario que h coincida con delta_i. Primeros devengos: 181/365 y 184/365.

| Índice | Intervalo | Sigma / PCA | Observación |
| --- | --- | --- | --- |
| 0 | [t0,t1] | Ninguna | Tipo spot inicial conocido; el código conserva el índice F0 por comodidad |
| i=1…20 | [t_i,t_(i+1)] | F(8+i) / fila 116+i de G:I | F1 usa F9 y fila117; F20 usa F28 y fila136 |
| Cupón j | Devengo [t_(j−1),t_j], pago t_j | Fixing F_(j−1)(t_(j−1)) | Primeros dos cupones fijos |
| Último descuento | [t20,t21] | F20 | Sigue siendo necesario aunque no entre en el cupón20 |

En el paso n se usan los tres shocks de la fila temporal n para evolucionar solo
forwards i>=n con el estado anterior común. La columna p se conserva como path p.
El calendario, tipos iniciales, sigmas y cargas efectivos son visibles en la hoja
Calendario del Excel final; no hace falta mantener otro CSV con un mapa paralelo.

## Interpolación y componentes

[CInterPol, fuente extraída](evidencias/cinterpol_fuente.bas) se conserva como copia
estática de lectura, vinculada al XLSM de hash anterior; el motor no la carga ni la ejecuta.
Modo 0: `exp((1-w)log(Pa)+w log(Pb))`; modo 1: lineal en factores. Se usa modo 0,
equivalente a interpolar los logaritmos en Python. El VBA extrapola con extremos y no
valida el soporte; Python rechaza extrapolaciones, que el calendario final no necesita.

Las filas de A cumplen suma de cuadrados igual a1 (desviación máxima 2.22e-16).
La covarianza/correlación
reducida efectiva es A Aᵀ: se emplea tanto en drift como en difusión. El residual máximo
frente a la matriz objetivo es 0.15350247. La descomposición almacenada es aproximada;
no se sustituye por una diagonalización nueva. El 92.35035% de varianza acumulada en
Correlaciones!E85 se refiere a la descomposición previa, no a una garantía de error del
precio ni de la matriz final normalizada. [Razón metodológica](FUNDAMENTOS.md).
