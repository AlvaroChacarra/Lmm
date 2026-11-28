"""Lee Excel/PDF de entrega y reconcilia cachés; no sustituye recálculo en Excel."""
import json
from hashlib import sha256
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
import openpyxl
from pypdf import PdfReader
from lmm.inputs import load_inputs,verify_originals
from lmm.model import simulate
from lmm.valuation import estimate

data=load_inputs();s=simulate(data);r,cf,pv,cp,pp=estimate(s)
w=openpyxl.load_workbook(ROOT/'entrega/Snowblade_LMM.xlsx',read_only=True,data_only=True)
assert w.sheetnames[:2]==['Resumen','Ejemplo']
example=np.asarray(list(w['Ejemplo'].iter_rows(min_row=5,max_row=24,max_col=9,values_only=True)),float)
expected_example=np.column_stack([np.arange(1,21),s.fixings[0],cf.rates[0],s.delta[:20],
    cf.paid_coupon[0],cf.cumulative_paid_fraction[0],cf.paid_principal[0],s.terminal_bonds[0],
    (cf.paid_coupon[0]+cf.paid_principal[0])*s.initial_terminal/s.terminal_bonds[0]])
np.testing.assert_allclose(example,expected_example,rtol=0,atol=1e-12)
np.testing.assert_allclose(w['Ejemplo']['I26'].value,pv[0],rtol=0,atol=1e-12)
np.testing.assert_allclose(w['Resumen']['B2'].value,r['price'],rtol=0,atol=1e-12)
np.testing.assert_allclose(w['Resumen']['B5'].value,r['standard_error'],rtol=0,atol=1e-12)
assert w['Resumen']['B12'].value == sum(r['autocall_counts'])
assert w['Resumen']['B13'].value == r['maturity_no_call_count']
frequency_rows = list(w['Paths'].iter_rows(min_row=2, max_row=21, min_col=9, max_col=11, values_only=True))
np.testing.assert_allclose(frequency_rows, [
    (period, count / len(pv), count) for period, count in enumerate(r['autocall_counts'], 1)
], rtol=0, atol=1e-12)
actual=np.array([[c.value for c in row[7:28]] for row in w['Estados'].iter_rows(min_row=2)],float)
expected=s.states.transpose(1,0,2).reshape(-1,21)
np.testing.assert_allclose(actual,expected,rtol=0,atol=1e-14)
flows=np.array([[c.value for c in row[3:15]] for row in w['Flujos'].iter_rows(min_row=2)],float)
for column,expected_cf in [(0,s.fixings),(1,cf.rates),(3,cf.alive_before),(4,cf.paid_coupon),
                           (5,cf.cumulative_paid_fraction),(6,cf.call_event),(7,cf.paid_principal),(8,s.terminal_bonds)]:
    np.testing.assert_allclose(flows[:,column],expected_cf.ravel(),rtol=0,atol=1e-12)
path_values=np.array([[c.value for c in row[1:4]] for row in w['Paths'].iter_rows(min_row=2)])
np.testing.assert_allclose(path_values,np.stack([cp,pp,pv],axis=1),rtol=0,atol=1e-12)
error_cells=[f'{sh.title}!{c.coordinate}' for sh in w for row in sh for c in row if c.data_type=='e']
assert not error_cells,error_cells
w.close()
f=openpyxl.load_workbook(ROOT/'entrega/Snowblade_LMM.xlsx',read_only=True,data_only=False)
for i,row in enumerate(f['Calendario'].iter_rows(min_row=3,max_row=22,min_col=8,max_col=10,values_only=True),2):
    assert row==tuple(f'=PCA!{column}{i}' for column in 'BCD')
count=sum(c.data_type=='f' for sh in f for row in sh for c in row)
f.close()
pdf=PdfReader(ROOT/'entrega/Memoria_Snowblade.pdf')
text=' '.join(' '.join(p.extract_text().split()) for p in pdf.pages)
assert len(pdf.pages)==5
def spanish(x):return f'{x:.4f}'.replace('.',',')
assert all(spanish(value) in text for value in [r['price'],r['standard_error'],*r['ci95_student']])
assert 'h=0,5' in text
assert 'cupones negativos' in text
assert 'cupón íntegro' in text and 'Ejemplo!I26' in text
assert spanish(pv[0]) in text
assert all(spanish(v) in text for v in [cp[0], pp[0], cf.paid_coupon[0,2], cf.paid_coupon[0,4]])
assert 'como lectura de trabajo' not in text
assert r['cap_target'] is False
recalc_file=ROOT/'outputs/recalculo_validacion.json'
recalc=json.loads(recalc_file.read_text()) if recalc_file.exists() else {}
recalc_matches=recalc.get('source_xlsx_sha256')==sha256((ROOT/'entrega/Snowblade_LMM.xlsx').read_bytes()).hexdigest()
report={'excel_state_values_checked':actual.size,'excel_flow_rows_checked':len(flows),
        'excel_paths_checked':len(path_values),'excel_formula_count':count,'excel_cached_error_cells':error_cells,
        'excel_engine_recalculation':'LIBREOFFICE_VALIDATED_SEPARATELY' if recalc_matches else 'NOT_EXECUTED',
        'external_recalc_evidence':'outputs/recalculo_validacion.json' if recalc_matches else None,'pdf_pages':len(pdf.pages),'pdf_key_figures_match':True,
        'original_sha256':verify_originals()}
(ROOT/'outputs/entrega_validacion.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
