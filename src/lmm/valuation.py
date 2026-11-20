"""Estimación de PV y errores sobre 200 trayectorias completas."""
from dataclasses import asdict
import numpy as np
from scipy.stats import t as student_t
from .payoff import cashflows


def estimate(simulation, nominal=100., cap_target=False):
    s=simulation
    cf=cashflows(s.fixings,s.delta[:20],nominal=nominal,cap_target=cap_target)
    weight=s.initial_terminal/s.terminal_bonds
    coupon_pv=np.sum(cf.paid_coupon*weight,axis=1)
    principal_pv=np.sum(cf.paid_principal*weight,axis=1)
    pv=coupon_pv+principal_pv
    n=len(pv); se=float(np.std(pv,ddof=1)/np.sqrt(n)); mean=float(pv.mean())
    q=float(student_t.ppf(.975,n-1))
    events=cf.call_event.sum(axis=0)
    maturity_no_call=int(np.sum(~cf.call_event.any(axis=1)))
    expected_life=float(np.mean(s.days[cf.redemption_period]/365))
    report={'config':asdict(s.config),'nominal':nominal,'paths':n,'price':mean,
            'coupon_pv':float(coupon_pv.mean()),'principal_pv':float(principal_pv.mean()),
            'standard_error':se,'ci95_student':[mean-q*se,mean+q*se],
            'expected_life_years_Q_terminal':expected_life,
            'autocall_counts':events.tolist(),'autocall_probabilities_Q_terminal':(events/n).tolist(),
            'maturity_no_call_count':maturity_no_call,'maturity_no_call_probability_Q_terminal':maturity_no_call/n,
            'negative_coupon_paths':int(np.sum(np.any(cf.paid_coupon<0,axis=1))),
            'negative_paid_coupon_count':int(np.sum(cf.paid_coupon<0)),
            'min_path_pv':float(pv.min()),'max_path_pv':float(pv.max()),
            'min_live_shifted_forward':float(min(np.min(s.states[k,:,k:]+.03) for k in range(1,min(s.config.terminal,21)))),
            'cap_target':cap_target,
            'negative_pv_paths':int(np.sum(pv<0)),
            'median_path_pv':float(np.median(pv)),
            'worst_path_id':int(np.argmin(pv)+1),
            'mean_excluding_worst_influence_only':float(np.delete(pv,np.argmin(pv)).mean())}
    return report,cf,pv,coupon_pv,principal_pv


def martingale_checks(s):
    """P(t_m,t_k)/P(t_m,T*) martingala; diagnósticos, no pruebas de no sesgo."""
    checks=[]
    for m in range(1,21):
        for k in range(m,s.config.terminal+1):
            # P(t_m,t_k)/P(t_m,t_terminal)=producto j=k..terminal-1.
            values=np.prod(1+s.delta[k:]*s.states[m,:,k:],axis=1)
            expected=s.p0[k]/s.p0[-1]
            err=float(np.mean(values)-expected)
            se=float(np.std(values,ddof=1)/np.sqrt(len(values)))
            checks.append({'observation':m,'maturity':k,'mean':float(values.mean()),
                           'expected':float(expected),'error':err,'standard_error':se,
                           'z_score':err/se if se>1e-14 else 0.,
                           'within_5se':bool(abs(err)<=5*se+1e-12)})
    return checks
