"""Referencia escalar independiente: sumas explícitas, sin kernels del motor.
Usa exactamente los inputs originales; no genera números aleatorios.
"""
import math
import numpy as np


def scalar_reference(inputs, dates, config):
    terminal=config.terminal
    days=[(d-dates[0]).days for d in dates]
    delta=[(days[i+1]-days[i])/365 for i in range(terminal)]
    def discount(day):
        k=0
        while k+1<len(inputs.days)-1 and inputs.days[k+1]<day:
            k+=1
        w=(day-inputs.days[k])/(inputs.days[k+1]-inputs.days[k])
        return math.exp((1-w)*math.log(inputs.discounts[k])+w*math.log(inputs.discounts[k+1]))
    discounts=[discount(d) for d in days]
    f0=[(discounts[i]/discounts[i+1]-1)/delta[i] for i in range(terminal)]
    lam=[[0.,0.,0.]]+[[float(inputs.vols[i-1+config.vol_offset]*config.vol_scale*inputs.loadings[i-1,k]) for k in range(3)] for i in range(1,terminal)]
    out=np.empty((21,200,terminal))
    paid_coupon=np.zeros((200,20)); paid_principal=np.zeros((200,20)); path_pv=np.zeros(200)
    for p in range(200):
        history=[f0.copy()]
        for n in range(1,21):
            old=history[-1]; new=old.copy()
            h=delta[n-1] if config.diffusion_clock=='act365' else inputs.dt_template
            for i in range(n,terminal):
                mu=-math.fsum(delta[j]*(old[j]+inputs.shift)/(1+delta[j]*old[j])*math.fsum(lam[i][k]*lam[j][k] for k in range(3)) for j in range(i+1,terminal))
                shock=math.sqrt(h)*math.fsum(lam[i][k]*inputs.normals[k,n-1,p] for k in range(3))
                variance=math.fsum(x*x for x in lam[i])
                new[i]=(old[i]+inputs.shift)*math.exp((mu-.5*variance)*h+shock)-inputs.shift
            history.append(new)
        out[:,p,:]=history
        accumulated=0.; previous=.01
        for j in range(1,21):
            b=0 if j<=4 else .01 if j<=8 else .0125 if j<=12 else .015 if j<=16 else .02
            coupon=.01 if j<=2 else previous+b-history[j-1][j-1]
            payment=100*delta[j-1]*coupon
            accumulated+=payment/100
            principal=100. if accumulated>=.04 or j==20 else 0.
            paid_coupon[p,j-1]=payment; paid_principal[p,j-1]=principal
            inverse_bond=math.prod(1+delta[k]*history[j][k] for k in range(j,terminal))
            path_pv[p]+=discounts[-1]*(payment+principal)*inverse_bond
            previous=coupon
            if principal:
                break
    return out,paid_coupon,paid_principal,path_pv
