"""Contrato aclarado por el profesor: tasas anuales, memoria negativa, objetivo neto."""
from dataclasses import dataclass
import numpy as np

SPREADS=np.array([0,0,0,0]+[.01]*4+[.0125]*4+[.015]*4+[.02]*4)

@dataclass
class Cashflows:
    rates: np.ndarray
    paid_coupon: np.ndarray
    paid_principal: np.ndarray
    cumulative_paid_fraction: np.ndarray
    alive_before: np.ndarray
    call_event: np.ndarray
    redemption_period: np.ndarray


def cashflows(fixings, accruals, nominal=100., target=.04, cap_target=False):
    r=np.asarray(fixings,float)
    d=np.asarray(accruals,float)
    if r.ndim!=2 or r.shape[1]!=20 or d.shape!=(20,) or not np.isfinite(r).all() or not np.isfinite(d).all() or np.any(d<=0):
        raise ValueError('Fixings/devengos inválidos')
    if not np.isfinite(nominal) or nominal<=0 or not np.isfinite(target) or target<=0:
        raise ValueError('Nominal/objetivo inválidos')
    paths=r.shape[0]
    rates=np.zeros_like(r); paid=np.zeros_like(r); principal=np.zeros_like(r)
    cumulative=np.zeros_like(r); alive_before=np.zeros_like(r,dtype=bool); call=np.zeros_like(r,dtype=bool)
    alive=np.ones(paths,dtype=bool); accumulated=np.zeros(paths); redemption=np.full(paths,20)
    previous=np.zeros(paths)
    for j in range(20):
        alive_before[:,j]=alive
        theoretical=np.full(paths,.01) if j<2 else previous+SPREADS[j]-r[:,j]
        rates[:,j]=np.where(alive,theoretical,0)
        q=theoretical*d[j]
        if cap_target:
            q=np.minimum(q,target-accumulated)
        paid[:,j]=np.where(alive,nominal*q,0)
        accumulated=accumulated+paid[:,j]/nominal
        cumulative[:,j]=accumulated
        event=alive&(accumulated>=target)
        redeem=event | (alive & (j==19))
        call[:,j]=event
        principal[:,j]=nominal*redeem
        redemption[redeem]=j+1
        alive=alive&~redeem
        previous=theoretical  # memoria teórica sin floor, incluso cuando es negativa
    return Cashflows(rates,paid,principal,cumulative,alive_before,call,redemption)
