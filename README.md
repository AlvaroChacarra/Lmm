# Snowblade — solución LMM del ejercicio AFI

Valoración Monte Carlo bajo LMM shifted lognormal monocurva y bono terminal, con los
**200 paths originales**. El contrato está aclarado por el profesor y el caso final
está validado para el ejercicio académico.

**Resultado: 98,26916479 por 100 de nominal.** Error estándar 2,74535035; IC 95%
aproximado [92,85545320; 103,68287639]. La precisión está limitada por la muestra y
las aproximaciones del modelo. [Resultados y lectura económica](docs/RESULTADOS.md).

[Excel con implementación](entrega/Snowblade_LMM.xlsx) ·
[Memoria PDF](entrega/Memoria_Snowblade.pdf)

El Excel abre en **Resumen**. **Ejemplo** permite seguir la trayectoria 1 y comprobar su valor en **Paths**. La memoria desarrolla las mismas cifras en la página 5. El [plan de acción y los criterios de aceptación](docs/PLAN_ENTREGA.md) documentan el diseño y la revisión de la entrega.

## Cómo entender y reconstruir la solución

| Documento | Pregunta que resuelve |
| --- | --- |
| [Aclaraciones del profesor](docs/ACLARACIONES_PROFESOR.md) | ¿Qué información contractual se obtuvo fuera del PDF? |
| [Mapa de inputs](docs/AUDITORIA_INPUTS.md) | ¿De qué celdas salen los datos y cómo se asignan a cada fecha? |
| [Decisiones](docs/DECISIONES.md) | ¿Qué se eligió, por qué y qué alternativas se descartaron? |
| [Fundamentos y reflexión](docs/FUNDAMENTOS.md) | ¿Cómo funciona la valoración y qué respalda el procedimiento seguido? |
| [Validación](docs/VALIDACION.md) | ¿Qué se comprobó realmente y qué no demuestra cada prueba? |
| [Estado](docs/ESTADO.md) | ¿Qué está terminado y cómo retomar sin depender del chat? |

Las versiones intermedias se recuperan en Git. La documentación vigente presenta una
sola solución: no es un archivo de prompts ni de planes ya consumidos.

## Verificar el estado publicado

Desde la raíz, con Python 3.12, las dependencias de [requirements.txt](requirements.txt)
y los originales disponibles:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
(cd data/original && sha256sum -c SHA256SUMS)
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python scripts/check_delivery.py
```

El último comando reconcilia los valores guardados del Excel y el PDF con Python y
comprueba si existe evidencia externa de recálculo vinculada al hash del libro.
**Leer cachés por sí solo no acredita ejecutar sus fórmulas.**

## Regenerar cálculo y entregas

```sh
python scripts/value_snowblade.py
python scripts/validate_solution.py
python scripts/build_delivery.py
python scripts/recalculate_delivery.py
python scripts/check_delivery.py
```

Los comandos escriben únicamente resultados derivados en `outputs/` y `entrega/`.
El PDF requiere DejaVu en `/usr/share/fonts/truetype/dejavu/`. El recálculo externo
requiere `soffice` en PATH, o `--soffice /ruta/soffice`; trabaja con copias temporales.
Los escenarios adicionales se regeneran desde Python y se conservan en `outputs/resultados.json`.

## Estructura y fuentes

[Enunciado original](data/original/2026_Ejercicio.pdf) ·
[XLSM original](data/original/2026_Datos.xlsm) · [SHA-256](data/original/SHA256SUMS)

- `data/original/`: PDF, XLSM, manifiesto SHA-256 e instrucciones de conservación.
- `src/lmm/`: lectura, curva, simulación, payoff y estimación.
- `tests/`: controles cuantitativos y referencia escalar separada.
- `scripts/`: ejecución, validación, generación y comprobación de las entregas.
- `outputs/`: resultados finales y evidencia reproducible, incluidos 200 PV y 4.000 flujos.
- `entrega/`: XLSX sin VBA y memoria docente de siete páginas.
- `docs/`: fuentes adicionales, decisiones, método y evidencia; [AGENTS.md](AGENTS.md)
  contiene las reglas para mantenerlos consistentes.

No modificar los originales ni sustituir aleatorios o PCA. El recálculo se ha probado
en LibreOffice; Microsoft Excel no está probado. No hay consulta contractual material
pendiente para la solución presentada; los supuestos mínimos y límites siguen explícitos.
