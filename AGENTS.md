# Instrucciones para trabajar en LMM

## Entrada y autoridad

Leer [README.md](README.md) y [docs/ESTADO.md](docs/ESTADO.md). La solución académica
está terminada; no reiniciar la auditoría ni ejecutar planes de fases antiguas.

- Contrato y aclaraciones externas: [ACLARACIONES_PROFESOR](docs/ACLARACIONES_PROFESOR.md).
- Datos e índices: [AUDITORIA_INPUTS](docs/AUDITORIA_INPUTS.md).
- Decisiones y razones: [DECISIONES](docs/DECISIONES.md) y [FUNDAMENTOS](docs/FUNDAMENTOS.md).
- Resultado: [RESULTADOS](docs/RESULTADOS.md). Pruebas y límites: [VALIDACION](docs/VALIDACION.md).

Las respuestas explícitas del profesor completan las ambigüedades del PDF. Los originales
mandan sobre transcripciones; las decisiones adoptadas no deben atribuirse al profesor
si este no las confirmó. Código y evidencia ejecutada determinan qué está implementado.

## Invariantes

1. No modificar nada de `data/original/`, convertir el XLSM ni ejecutar VBA.
2. Conservar los 200 paths y las cargas PCA originales: sin regenerar, recentrar,
   renormalizar, cambiar signos o sustituirlas para mejorar el resultado.
3. Spot inicial sin sigma; F1…F20 usan F9:F28. F29 se conserva sin usar.
4. Difusión h=0.5; devengos ACT/365. Fixing advance. Cupones sin floor y con memoria
   negativa. Objetivo neto 4%; opción A, cupón íntegro más principal al autocall.
5. Drift y descuento bajo el mismo bono terminal y la misma covarianza efectiva PCA.
   Nominal exactamente una vez. No eliminar trayectorias negativas.
6. Resultados y probabilidades bajo Q terminal, con SE sobre 200 PV completos.
   No confundir determinismo de ejecución con precisión económica.

## Cambios y cierre

Ejecutar la comprobación adecuada de [README](README.md): tests y contraste escalar si
cambia el cálculo; regeneración y recálculo externo si cambian las fórmulas o cifras.
No afirmar recálculo Microsoft Excel: el motor externo comprobado es LibreOffice.
Actualizar la superficie que posee la verdad, revisar enlaces y conservar trazabilidad
sin duplicar resultados ni crear diarios de sesión. Mantener código, datos y evidencia
consistentes con las entregas. No dejar cambios funcionales sin comprobar ni hacer merge
automático. Informes en español; identificadores de código pueden estar en inglés.
