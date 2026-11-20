"""Evidencia numérica de reconciliación escalar y caso sigma=0, sin ruido nuevo."""
import json
from dataclasses import replace
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')]
import numpy as np
from scipy.stats import norm
from lmm.inputs import load_inputs
from lmm.model import Config, simulate
from lmm.valuation import estimate, martingale_checks
from lmm.payoff import cashflows
from reference import scalar_reference

if __name__=='__main__':
    inputs=load_inputs();s=simulate(inputs);r,cf,pv,_,_=estimate(s)
    ref,c,p,refpv=scalar_reference(inputs,s.dates,s.config)
    zero=simulate(inputs,replace(Config(),vol_scale=0))
    _,zcf,zpv,_,_=estimate(zero)
    direct=((zcf.paid_coupon+zcf.paid_principal)*zero.p0[1:21]).sum(axis=1)
    caplets=[]
    for i in range(1,s.config.terminal):
        # Pago conocido al reset: P(t_i,t_(i+1))/P(t_i,T*) excluye el factor propio.
        ratio=np.prod(1+s.delta[i+1:]*s.states[i,:,i+1:],axis=1)
        sigma=float(np.linalg.norm(s.diffusion[i]))
        expiry=i*inputs.dt_template if s.config.diffusion_clock=='template' else s.days[i]/365
        vol=sigma*np.sqrt(expiry)
        for bump in [-.01,0.,.01]:
            strike=s.f0[i]+bump
            X=s.f0[i]+inputs.shift;K=strike+inputs.shift
            d1=(np.log(X/K)+.5*vol**2)/vol;d2=d1-vol
            analytic=float(s.p0[i+1]*s.delta[i]*(X*norm.cdf(d1)-K*norm.cdf(d2)))
            samples=s.initial_terminal*s.delta[i]*np.maximum(s.states[i,:,i]-strike,0)*ratio
            se=float(samples.std(ddof=1)/np.sqrt(len(samples)))
            error=float(samples.mean()-analytic)
            caplets.append({'forward':i,'strike':float(strike),'mc_price':float(samples.mean()),
                            'black_price':analytic,'se':se,'z':error/se if se>1e-14 else 0.})
    assert all(abs(c['z'])<5 for c in caplets)
    # Ejemplo confirmado por el profesor: 3.80 acumulados + cupón .60 => 100.60.
    # Fixings sintéticos solo de prueba, todos dentro del soporte desplazado.
    fixture=np.zeros((1,20));fixture[0,2]=-.018;fixture[0,4]=.026
    option_a=cashflows(fixture,np.full(20,.5))
    np.testing.assert_allclose(option_a.cumulative_paid_fraction[0,3],.038,rtol=0,atol=1e-15)
    np.testing.assert_allclose(option_a.paid_coupon[0,4],.60,rtol=0,atol=1e-12)
    np.testing.assert_allclose(option_a.cumulative_paid_fraction[0,4],.044,rtol=0,atol=1e-15)
    assert option_a.paid_principal[0,4]==100 and option_a.redemption_period[0]==5
    assert not np.any(option_a.paid_coupon[0,5:])
    no_equal=np.all(cf.cumulative_paid_fraction[cf.alive_before] != .04)
    assert no_equal  # En esta muestra >4% y >=4% producen las mismas cancelaciones.
    record={'professor_option_A':{'prior_interest_per_100':3.80,'full_trigger_coupon_per_100':float(option_a.paid_coupon[0,4]),
                                  'total_payment_per_100':float(option_a.paid_coupon[0,4]+option_a.paid_principal[0,4]),
                                  'final_interest_per_100':float(100*option_a.cumulative_paid_fraction[0,4]),
                                  'redemption_period_fixture':int(option_a.redemption_period[0]),
                                  'strict_and_inclusive_trigger_equivalent_on_original_paths':bool(no_equal)},
        'base_config':r['config'],'caplet_checks':len(caplets),
        'caplet_max_abs_z':float(max(abs(c['z']) for c in caplets)),
        'caplet_detail':caplets,'all_200_paths_scalar_reference':{
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
