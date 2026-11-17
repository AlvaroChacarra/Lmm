"""Evidencia numérica de reconciliación escalar y caso sigma=0, sin ruido nuevo."""
import json
from dataclasses import replace
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')]
import numpy as np
from lmm.inputs import load_inputs
from lmm.model import Config, simulate
from lmm.valuation import estimate, martingale_checks
from reference import scalar_reference

if __name__=='__main__':
    inputs=load_inputs();s=simulate(inputs);r,cf,pv,_,_=estimate(s)
    ref,c,p,refpv=scalar_reference(inputs,s.dates,s.config)
    zero=simulate(inputs,replace(Config(),vol_scale=0))
    _,zcf,zpv,_,_=estimate(zero)
    direct=((zcf.paid_coupon+zcf.paid_principal)*zero.p0[1:21]).sum(axis=1)
    record={'all_200_paths_scalar_reference':{
        'forward_max_abs_error':float(np.max(abs(s.states-ref))),
        'coupon_max_abs_error':float(np.max(abs(cf.paid_coupon-c))),
        'principal_max_abs_error':float(np.max(abs(cf.paid_principal-p))),
        'path_pv_max_abs_error':float(np.max(abs(pv-refpv)))},
        'zero_volatility_direct_discount_max_abs_error':float(np.max(abs(zpv-direct))),
        'zero_volatility_price':float(zpv.mean()),
        'martingale_tests':len(martingale_checks(s)),
        'mc_checks_all_within_5se':all(c['within_5se'] for c in martingale_checks(s)),
        'martingale_max_abs_z':float(max(abs(c['z_score']) for c in martingale_checks(s))),
        'originals':inputs.hashes}
    (ROOT/'outputs/validacion.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))
