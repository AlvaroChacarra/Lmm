"""Lectura validada de los originales; ninguna escritura sobre el XLSM."""
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import calendar

import numpy as np
import openpyxl

ROOT = Path(__file__).resolve().parents[2]

@dataclass
class Inputs:
    start: datetime
    days: np.ndarray
    discounts: np.ndarray
    vols: np.ndarray
    loadings: np.ndarray
    normals: np.ndarray  # factor, paso, path
    shift: float
    dt_template: float
    hashes: dict


def verify_originals(root=ROOT):
    folder = Path(root) / 'data/original'
    expected = {line.split()[1]: line.split()[0] for line in (folder/'SHA256SUMS').read_text().splitlines()}
    actual = {name: sha256((folder/name).read_bytes()).hexdigest() for name in expected}
    if actual != expected:
        raise ValueError('SHA-256 de originales distinto del manifiesto')
    return actual


def load_inputs(root=ROOT):
    hashes = verify_originals(root)
    w = openpyxl.load_workbook(Path(root)/'data/original/2026_Datos.xlsm', data_only=True, read_only=True)
    def cells(sheet, ref):
        return np.array([[c.value for c in row] for row in w[sheet][ref]], dtype=float)
    c = w['Curva y volas']
    data = Inputs(c['C2'].value, cells(c.title,'A5:A74').ravel(),
                  cells(c.title,'C5:C74').ravel(), cells(c.title,'F9:F29').ravel(),
                  cells('Correlaciones','G117:I136'),
                  np.stack([cells('Aleatorios', f'C{r}:GT{r+19}') for r in (3,25,47)]),
                  c['F5'].value, c['F6'].value, hashes)
    w.close()
    if not all(np.isfinite(a).all() for a in (data.days,data.discounts,data.vols,data.loadings,data.normals)):
        raise ValueError('Inputs no finitos')
    if data.normals.shape != (3,20,200) or data.loadings.shape != (20,3) or data.vols.shape != (21,):
        raise ValueError('Dimensiones incompatibles con los originales')
    if not (np.all(np.diff(data.days)>0) and np.all(data.discounts>0) and data.days[0]==0 and data.discounts[0]==1):
        raise ValueError('Curva inválida')
    if not (data.shift==.03 and data.dt_template==.5 and np.all(data.vols>0)):
        raise ValueError('Parámetros distintos de la plantilla auditada')
    if not np.allclose(np.sum(data.loadings**2,axis=1),1,rtol=0,atol=1e-14):
        raise ValueError('Cargas finales sin varianza unitaria')
    return data


def interpolate(inputs, days):
    x = np.asarray(days, dtype=float)
    if not np.isfinite(x).all() or np.any(x<inputs.days[0]) or np.any(x>inputs.days[-1]):
        raise ValueError('Interpolación fuera de soporte o fecha no finita')
    return np.exp(np.interp(x, inputs.days, np.log(inputs.discounts)))


def add_months(date, months):
    m = date.year*12+date.month-1+months
    y, m = divmod(m,12)
    return date.replace(year=y, month=m+1, day=min(date.day,calendar.monthrange(y,m+1)[1]))
