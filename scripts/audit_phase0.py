"""Auditoría de solo lectura; no simula, no ejecuta VBA, no genera aleatorios.
Ejecutar desde la raíz. Dependencias: numpy, scipy, openpyxl, oletools.
"""
import csv
import hashlib
import json
import platform
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

import numpy as np
import openpyxl
import scipy
from scipy import stats
from oletools.olevba import VBA_Parser

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / 'data/original'
OUT = ROOT / 'docs/evidencias'
OUT.mkdir(exist_ok=True)
sha = lambda b: hashlib.sha256(b).hexdigest()
expected = dict(line.split()[::-1] for line in (ORIG/'SHA256SUMS').read_text().splitlines())
before = {p.name: sha(p.read_bytes()) for p in ORIG.iterdir() if p.suffix in ('.pdf', '.xlsm')}
assert before == expected, 'Originales distintos del manifiesto'
p = ORIG/'2026_Datos.xlsm'
w = openpyxl.load_workbook(p, data_only=False, keep_vba=True)
v = openpyxl.load_workbook(p, data_only=True)
report = {'baseline_commit': '15359f2', 'original_sha256': before,
          'versions': {'python': platform.python_version(), 'numpy': np.__version__,
                       'scipy': scipy.__version__, 'openpyxl': openpyxl.__version__},
          'sheets': {}, 'checks': {}}
def check(name, condition):
    report['checks'][name] = bool(condition)
    assert condition, name

def block(sheet, ref):
    return np.array([[c.value for c in row] for row in v[sheet][ref]], dtype=float)

with zipfile.ZipFile(p) as z:
    check('zip_crc', z.testzip() is None)
    report['zip_parts'] = {n: {'size': z.getinfo(n).file_size, 'sha256': sha(z.read(n))} for n in z.namelist()}
    report['external_relationships'] = {n: z.read(n).decode() for n in z.namelist() if n.endswith('.rels') and b'TargetMode="External"' in z.read(n)}
    report['workbook_xml'] = z.read('xl/workbook.xml').decode()
    report['chart_references'] = {n: [e.text for e in ET.fromstring(z.read(n)).iter() if e.tag.split('}')[-1] == 'f'] for n in z.namelist() if n.startswith('xl/charts/chart') and n.endswith('.xml')}
for s in w:
    populated = [c for row in s for c in row if c.value is not None]
    formulas = [{'cell': c.coordinate, 'formula': c.value, 'cache': str(v[s.title][c.coordinate].value)} for c in populated if c.data_type == 'f']
    report['sheets'][s.title] = {
        'dimension': s.calculate_dimension(), 'nonempty': len(populated), 'state': s.sheet_state,
        'formulas': formulas, 'errors': {c.coordinate: c.value for c in populated if c.data_type == 'e'},
        'merged': [str(x) for x in s.merged_cells],
        'hidden_rows': [i for i,d in s.row_dimensions.items() if d.hidden],
        'hidden_columns': [i for i,d in s.column_dimensions.items() if d.hidden],
        'comments': {c.coordinate: c.comment.text for c in populated if c.comment},
        'tables': list(s.tables), 'charts': len(s._charts),
    }
check('70_formulas_only_dates', sum(len(x['formulas']) for x in report['sheets'].values()) == 70 and all(c.value == '=$C$2+A'+str(c.row) for c in w['Curva y volas']['B'][4:74]))
check('date_caches', all((v['Curva y volas'][f'B{r}'].value-v['Curva y volas']['C2'].value).days == v['Curva y volas'][f'A{r}'].value for r in range(5,75)))
Z = np.stack([block('Aleatorios', f'C{r}:GT{r+19}') for r in (3,25,47)])
check('Z_finite_shape', Z.shape == (3,20,200) and np.isfinite(Z).all())
check('Z_time_labels', all([v['Aleatorios'].cell(r+j,2).value for j in range(20)] == list(range(1,21)) for r in (3,25,47)))
check('Z_path_labels', [v['Aleatorios'].cell(2,c).value for c in range(3,203)] == list(range(1,201)))
report['random'] = {'shape_factor_step_path': list(Z.shape), 'sha256_float64_le_C_order': sha(Z.astype('<f8').tobytes()),
 'blocks': [{'range': f'C{r}:GT{r+19}', 'mean': float(a.mean()), 'sample_std': float(a.std(ddof=1)), 'min': float(a.min()), 'max': float(a.max()), 'KS_normal_p_descriptive': float(stats.kstest(a.ravel(), 'norm').pvalue), 'lag1_corr': float(np.corrcoef(a[:-1].ravel(), a[1:].ravel())[0,1])} for r,a in zip((3,25,47),Z)],
 'factor_corr': np.corrcoef(Z.reshape(3,-1)).tolist(), 'unique_path_vectors': int(np.unique(Z.transpose(2,0,1).reshape(200,-1), axis=0).shape[0])}
R = block('Correlaciones','C7:V26')
U = block('Correlaciones','C33:V52')
D = block('Correlaciones','C56:V75')
l = block('Correlaciones','C79:V79')[0]
B = block('Correlaciones','C117:E136')
A = block('Correlaciones','G117:I136')
check('correlation_symmetric_unit_diagonal_positive', np.allclose(R,R.T) and np.allclose(np.diag(R),1) and np.linalg.eigvalsh(R).min()>0)
check('R_exponential', np.max(abs(R-np.exp(-.05*abs(np.arange(20)[:,None]-np.arange(20)))))<1e-14)
check('PCA_supplied_normalized', np.max(abs(A-B/np.linalg.norm(B,axis=1)[:,None]))<1e-14)
check('PCA_supplied_selected_scaled', np.max(abs(B-U[:,[1,19,9]]*np.sqrt(l[[1,19,9]])))<1e-14)
check('corrected_vectors', np.max(abs(block('Correlaciones','C91:V110')-U*np.sqrt(l)))<1e-14)
check('eigen_table_is_diagonal', np.max(abs(np.diag(D)-l))<1e-14)
report['pca'] = {'R_min_eigenvalue': float(np.linalg.eigvalsh(R).min()), 'orthogonality_max_error': float(np.max(abs(U.T@U-np.eye(20)))),
 'RU_minus_Ulambda_max': float(np.max(abs(R@U-U*l))), 'stored_D_minus_UTRU_max': float(np.max(abs(D-U.T@R@U))),
 'D_offdiag_max': float(np.max(abs(D-np.diag(l)))), 'full_spectral_reconstruction_max_error': float(np.max(abs(R-(U*l)@U.T))),
 'explained_stored': v['Correlaciones']['E85'].value, 'explained_exact_diagnostic_only': float(sum(np.linalg.eigvalsh(R)[-3:])/20),
 'raw_B_variance_min_max': [float(np.diag(B@B.T).min()),float(np.diag(B@B.T).max())],
 'A_unit_variance_max_error': float(np.max(abs(np.diag(A@A.T)-1))),
 'R_vs_AAT_max': float(np.max(abs(R-A@A.T))), 'R_vs_AAT_frobenius_relative': float(np.linalg.norm(R-A@A.T)/np.linalg.norm(R))}
curve = block('Curva y volas','A5:A74').ravel(); dfs=block('Curva y volas','C5:C74').ravel()
check('curve_increasing_days_positive_df', np.all(np.diff(curve)>0) and np.all(dfs>0) and curve[0]==0 and dfs[0]==1)
check('shift_dt', v['Curva y volas']['F5'].value==.03 and v['Curva y volas']['F6'].value==.5)
check('vols_21_positive', list(block('Curva y volas','E9:E29').ravel())==list(range(1,22)) and np.all(block('Curva y volas','F9:F29')>0))
# CInterPol modo 0, traducción literal de búsqueda y fórmula, sin ejecutar VBA.
def cinterpol(day):
    a,b=0,len(curve)-1
    while b-a>1:
        n=(a+b)//2
        if curve[n]>=day: b=n
        else: a=n
    return np.exp(np.log(dfs[a])+(np.log(dfs[b])-np.log(dfs[a]))*(day-curve[a])/(curve[b]-curve[a]))
check('interpolation_nodes', max(abs(cinterpol(x)-y) for x,y in zip(curve,dfs))<1e-14)
mid=(curve[:-1]+curve[1:])/2
check('interpolation_midpoint_geometric_mean', max(abs(cinterpol(x)-np.sqrt(a*b)) for x,a,b in zip(mid,dfs[:-1],dfs[1:]))<1e-14)
# Calendario recomendado, no contractual: 6 meses calendario sin ajuste hábil.
start=v['Curva y volas']['C2'].value
T=[datetime(2022+i//2,1 if i%2==0 else 7,26) for i in range(22)]
days=np.array([(d-start).days for d in T]); P=np.array([cinterpol(x) for x in days]); delta=np.diff(days)/365
F=(P[:-1]/P[1:]-1)/delta
check('forwards_discount_identity', max(abs(P[0]/np.cumprod(1+delta*F)-P[1:]))<1e-14)
check('terminal_discount_empty_product', abs(P[-1]*np.prod(1+delta[1:]*F[1:])-P[1])<1e-14 and np.prod(1+delta[21:]*F[21:])==1)
check('initial_shifted_positive', np.all(F+.03>0))
report['curve']={'nodes':len(curve),'days_min_max':[int(curve.min()),int(curve.max())], 'df_min_max':[float(dfs.min()),float(dfs.max())], 'P_terminal_recommended':float(P[-1]), 'initial_forward_min_max':[float(F.min()),float(F.max())]}
with (OUT/'calendario_recomendado.csv').open('w') as out:
    writer=csv.writer(out);writer.writerow(['i','reset','payment','reset_days','payment_days','delta_ACT365','P0_reset','P0_payment','F0','vol_cell','PCA_row','random_step_to_reset'])
    for i in range(21): writer.writerow([i,T[i].date(),T[i+1].date(),days[i],days[i+1],delta[i],P[i],P[i+1],F[i],f'F{i+9}',117+i-1 if i else 'fijo','1..'+str(i) if i else 'ninguno'])
# Ejemplo conceptual r=0; no precio ni simulación.
c=np.zeros(20);c[:2]=.01
for j in range(2,20): c[j]=c[j-1]+(0 if j<4 else .01 if j<8 else .0125 if j<12 else .015 if j<16 else .02)
acc=np.cumsum(c*delta[:20]); sum_rates=np.cumsum(c); annual=c.reshape(10,2).mean(axis=1)
report['payoff_zero_reference_example']={'coupon_rates':c.tolist(),'cumulative_cash_fraction':acc.tolist(),'first_cash_target_period':int(np.flatnonzero(acc>=.04)[0]+1), 'first_sum_rates_target_period':int(np.flatnonzero(sum_rates>=.04)[0]+1),'first_annual_average_target_period':int(2*(np.flatnonzero(annual>=.04)[0]+1))}
check('payoff_interpretations_differ', report['payoff_zero_reference_example']['first_cash_target_period'] != report['payoff_zero_reference_example']['first_sum_rates_target_period'])
parser=VBA_Parser(str(p)); modules=[]
for _,stream,name,source in parser.extract_macros():
    modules.append({'name':name,'stream':stream,'source_sha256_utf8':sha(source.encode()),'lines':len(source.splitlines()),'procedures':re.findall(r'^\s*(?:(?:Public|Private)\s+)?(?:Sub|Function)\s+(\w+)',source,re.M|re.I)})
    if name=='Interpolacion.bas': (OUT/'cinterpol_fuente.bas').write_text(source)
parser.close();report['vba_modules']=modules
check('originals_unchanged_after', before=={name:sha((ORIG/name).read_bytes()) for name in before})
(OUT/'auditoria_fase0.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'checks_passed':len(report['checks']), 'random':report['random'], 'pca':report['pca'], 'curve':report['curve'], 'payoff':report['payoff_zero_reference_example'], 'vba':[(m['name'],m['lines'],len(m['procedures'])) for m in modules]},indent=2))
