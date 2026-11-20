"""Reproducir resultados con los 200 paths originales. Ejecutar desde raíz."""
import csv
from dataclasses import replace
import json
from pathlib import Path
import platform
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
import scipy
import openpyxl
from lmm.inputs import load_inputs, verify_originals
from lmm.model import Config, simulate
from lmm.valuation import estimate, martingale_checks


def run():
    data=load_inputs(); base=Config(); s=simulate(data,base)
    result,cf,pv,coupon_pv,principal_pv=estimate(s)
    checks=martingale_checks(s)
    alternatives={}
    for name,config in [('predictor_corrector',replace(base,scheme='predictor_corrector')),
                        ('diffusion_dt_05',replace(base,diffusion_clock='template')),
                        ('terminal_10_years',replace(base,terminal=20)),
                        ('vol_mapping_first_row',replace(base,vol_offset=0)),
                        ('zero_volatility',replace(base,vol_scale=0.))]:
        report,_,alt_pv,_,_=estimate(simulate(data,config))
        report['paired_difference_to_base']=float(np.mean(alt_pv-pv))
        report['paired_difference_se']=float(np.std(alt_pv-pv,ddof=1)/np.sqrt(len(pv)))
        alternatives[name]=report
    capped,_,capped_pv,_,_=estimate(s,cap_target=True)
    capped['paired_difference_to_base']=float(np.mean(capped_pv-pv))
    capped['paired_difference_se']=float(np.std(capped_pv-pv,ddof=1)/np.sqrt(len(pv)))
    alternatives['coupon_capped_at_target_not_base']=capped
    payload={'status':'PROVISIONAL_CON_CONVENCIONES_EXPLICITAS','source_hashes':data.hashes,
             'professor_clarifications_source':'respuestas aportadas por el usuario; correo sin fecha','versions':{'python':platform.python_version(),
             'numpy':np.__version__,'scipy':scipy.__version__,'openpyxl':openpyxl.__version__},
             'base':result,'sensitivities':alternatives,
             'martingale_diagnostics':{'max_abs_z':float(max(abs(c['z_score']) for c in checks)),
                                      'all_within_5se':all(c['within_5se'] for c in checks),'checks':checks}}
    (ROOT/'outputs').mkdir(exist_ok=True)
    (ROOT/'outputs/resultados.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    with (ROOT/'outputs/path_pv.csv').open('w') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['path','coupon_pv','principal_pv','pv','redemption_period','life_years','autocalled'])
        for p in range(len(pv)):
            w.writerow([p+1,coupon_pv[p],principal_pv[p],pv[p],cf.redemption_period[p],s.days[cf.redemption_period[p]]/365,bool(cf.call_event[p].any())])
    with (ROOT/'outputs/cashflows.csv').open('w') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['path','period','payment','fixing','annual_coupon_rate','accrual','coupon','principal','cumulative_interest_fraction','terminal_bond','weight','pv','alive_before','autocall'])
        for p in range(len(pv)):
            for j in range(20):
                weight=s.initial_terminal/s.terminal_bonds[p,j]
                w.writerow([p+1,j+1,s.dates[j+1].date(),s.fixings[p,j],cf.rates[p,j],s.delta[j],cf.paid_coupon[p,j],cf.paid_principal[p,j],cf.cumulative_paid_fraction[p,j],s.terminal_bonds[p,j],weight,(cf.paid_coupon[p,j]+cf.paid_principal[p,j])*weight,bool(cf.alive_before[p,j]),bool(cf.call_event[p,j])])
    verify_originals()
    print(json.dumps({'base':result,'sensitivities':{n:{k:r[k] for k in ['price','paired_difference_to_base','paired_difference_se']} for n,r in alternatives.items()},'martingale_max_z':payload['martingale_diagnostics']['max_abs_z']},indent=2))
    return data,s,payload,cf

if __name__=='__main__':
    run()
