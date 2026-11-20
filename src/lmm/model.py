"""LMM shifted lognormal bajo bono terminal; sin generación de ruido."""
from dataclasses import dataclass
import numpy as np
from .inputs import add_months, interpolate

@dataclass(frozen=True)
class Config:
    terminal: int = 21
    scheme: str = 'log_euler'
    diffusion_clock: str = 'template'
    vol_offset: int = 0  # Profesor: F1 usa la primera sigma; el tipo inicial es spot
    vol_scale: float = 1.0

@dataclass
class Simulation:
    config: Config
    dates: list
    days: np.ndarray
    delta: np.ndarray
    p0: np.ndarray
    f0: np.ndarray
    diffusion: np.ndarray
    states: np.ndarray  # tiempo 0..20, path 0..199, forward 0..terminal-1
    fixings: np.ndarray  # path, cupón 1..20; F_(j-1)(t_(j-1))
    terminal_bonds: np.ndarray  # path, pago 1..20
    initial_terminal: float


def drift(forwards, delta, diffusion, shift):
    """Devuelve drift relativo de X=F+s, usando un estado común anterior.

    Recibe solo los forwards vivos (última dimensión); covarianza efectiva λλᵀ.
    """
    denominator = 1+forwards*delta
    if not np.isfinite(forwards).all() or np.any(forwards+shift<=0) or np.any(denominator<=0):
        raise ValueError('Estado fuera del dominio shifted-lognormal/bonos')
    weights = delta*(forwards+shift)/denominator
    upper_covariance = np.triu(diffusion@diffusion.T, k=1)
    return -weights@upper_covariance.T


def simulate(inputs, config=Config()):
    if config.terminal not in (20,21) or config.scheme not in ('log_euler','predictor_corrector'):
        raise ValueError('Terminal/esquema no soportado')
    if config.diffusion_clock not in ('act365','template') or config.vol_offset not in (0,1):
        raise ValueError('Reloj/mapa de volatilidades no soportado')
    if not np.isfinite(config.vol_scale) or config.vol_scale<0:
        raise ValueError('Escala de volatilidad inválida')
    terminal=config.terminal
    dates=[add_months(inputs.start,6*i) for i in range(terminal+1)]
    days=np.array([(d-inputs.start).days for d in dates])
    delta=np.diff(days)/365
    p0=interpolate(inputs,days)
    f0=(p0[:-1]/p0[1:]-1)/delta
    # Índice 0: spot del primer semestre, conocido, sin sigma.
    # PCA fila 0 y sigma fila 0 corresponden al primer forward futuro F1.
    diffusion=np.zeros((terminal,3))
    count=terminal-1
    diffusion[1:]=inputs.loadings[:count]*inputs.vols[config.vol_offset:config.vol_offset+count,None]*config.vol_scale
    paths=inputs.normals.shape[2]
    states=np.empty((21,paths,terminal))
    states[0]=np.broadcast_to(f0,(paths,terminal))
    for n in range(1,21):
        previous=states[n-1]
        states[n]=previous
        if n>=terminal:
            continue
        live=previous[:,n:]
        lam=diffusion[n:]
        h=delta[n-1] if config.diffusion_clock=='act365' else inputs.dt_template
        mu=drift(live,delta[n:],lam,inputs.shift)
        brownian=np.sqrt(h)*inputs.normals[:,n-1,:].T@lam.T
        variance=np.sum(lam**2,axis=1)
        increment=(mu-.5*variance)*h+brownian
        if config.scheme=='predictor_corrector':
            predicted=(live+inputs.shift)*np.exp(increment)-inputs.shift
            mu_end=drift(predicted,delta[n:],lam,inputs.shift)
            increment=(.5*(mu+mu_end)-.5*variance)*h+brownian
        updated=(live+inputs.shift)*np.exp(increment)-inputs.shift
        # Fail closed: sin truncar tipos ni sustituir estados inválidos.
        drift(updated,delta[n:],lam,inputs.shift)
        states[n,:,n:]=updated
    fixings=np.stack([states[j-1,:,j-1] for j in range(1,21)],axis=1)
    bonds=np.stack([np.prod(1+delta[m:]*states[m,:,m:],axis=1)**-1 for m in range(1,21)],axis=1)
    return Simulation(config,dates,days,delta,p0,f0,diffusion,states,fixings,bonds,float(p0[-1]))
