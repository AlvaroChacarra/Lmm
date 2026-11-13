# Transcripción de trabajo — Ejercicio Modelos de Tipos de Interés

> **Documento de consulta.** La fuente contractual es data/original/2026_Ejercicio.pdf (dos páginas). En caso de discrepancia prevalece el PDF.

## Descripción
Valorar por simulación Monte Carlo el instrumento del Anexo I utilizando el modelo **LMM**.

- Numerario: **precio del bono en la última fecha disponible (N+1)**.
- Esquema **monocurva**.
- Modelo de cotización: **shifted lognormal**.
- Datos y plantilla de valoración: archivo **Datos.xlsm**, con función **cinterpol** para interpolar la curva de descuento.
- Generar el entorno aleatorio a partir de las **componentes principales ya generadas en la plantilla**.
- Usar los números aleatorios de la hoja **Aleatorios**.

## Entrega
1. Hoja de Excel con implementación.
2. Memoria PDF que explique **implementación**, **decisiones tomadas** y **análisis de resultados**.

## Anexo I — Snowblade
- Plazo: **10 años**.
- Pagos: **semestrales**, base **ACT/365**.
- Referencia variable: **Euribor 6 meses**.

| Periodos | Cupón |
| --- | --- |
| 1 y 2 | 1% |
| 3 y 4 | Cupón anterior − Euribor 6M |
| 5 a 8 | Cupón anterior + 1% − Euribor 6M |
| 9 a 12 | Cupón anterior + 1.25% − Euribor 6M |
| 13 a 16 | Cupón anterior + 1.50% − Euribor 6M |
| 17 a 20 | Cupón anterior + 2% − Euribor 6M |

**Amortización automática:** el instrumento cancela y amortiza a la par en el momento en que se alcance unos **intereses anuales acumulados de 4%**. Si el evento no sucede, amortiza a la par en periodo 20.

### No explicitado por el enunciado — documentar antes del resultado final
- Definición operacional de 'intereses anuales acumulados' y forma exacta de comprobar el 4%.
- Aplicación de ACT/365 a cupón acumulado, cuota semestral y trigger.
- Tratamiento de cupones recursivos potencialmente negativos (no se establece suelo).
- Observaciones/fijaciones y pago del cupón en el periodo de autocancelación.
- Convención exacta de fechado T_i/T_{N+1} para la simulación y el descuento.

Estas no son decisiones ya adoptadas.
