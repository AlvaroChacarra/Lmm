import unittest
from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import shutil

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import numpy as np
from lmm.inputs import load_inputs, interpolate, verify_originals
from lmm.model import Config, drift, simulate
from lmm.payoff import SPREADS, cashflows
from lmm.valuation import estimate, martingale_checks
from reference import scalar_reference

class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_inputs();cls.s=simulate(cls.data)
        cls.report,cls.cf,cls.pv,_,_=estimate(cls.s)

    def test_originals_and_interpolation(self):
        self.assertEqual(len(verify_originals()),2)
        np.testing.assert_allclose(interpolate(self.data,self.data.days),self.data.discounts,rtol=0,atol=2e-16)
        for day in [-1,20000,float('nan')]:
            with self.assertRaises(ValueError):interpolate(self.data,day)

    def test_corruption_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)/'data/original';folder.mkdir(parents=True)
            for name in ['SHA256SUMS','2026_Datos.xlsm','2026_Ejercicio.pdf']:
                shutil.copyfile(ROOT/'data/original'/name,folder/name)
            with (folder/'2026_Datos.xlsm').open('ab') as f:f.write(b'corruption')
            with self.assertRaises(ValueError):verify_originals(d)

    def test_calendar_and_initial_forwards(self):
        s=self.s
        self.assertEqual(str(s.dates[20].date()),'2032-01-26')
        self.assertEqual(str(s.dates[21].date()),'2032-07-26')
        self.assertEqual(s.delta[0],181/365)
        np.testing.assert_allclose(1/np.cumprod(1+s.delta*s.f0),s.p0[1:],atol=1e-14)
        np.testing.assert_array_equal(s.diffusion[1:],self.data.loadings*self.data.vols[:20,None])

    def test_professor_spot_first_forward_and_unused_vol(self):
        s=self.s
        self.assertEqual(s.config.diffusion_clock,'template')
        self.assertEqual(s.config.vol_offset,0)
        np.testing.assert_array_equal(s.diffusion[0],np.zeros(3))
        np.testing.assert_array_equal(s.diffusion[1],self.data.vols[0]*self.data.loadings[0])
        np.testing.assert_array_equal(s.diffusion[20],self.data.vols[19]*self.data.loadings[19])
        vols=self.data.vols.copy();vols[20]*=2  # Solo fixture en memoria, original intacto.
        np.testing.assert_array_equal(simulate(replace(self.data,vols=vols)).states,s.states)

    def test_diffusion_clock_does_not_change_ACT365_coupon_accrual(self):
        alternate=simulate(self.data,replace(Config(),diffusion_clock='act365'))
        np.testing.assert_array_equal(alternate.delta,self.s.delta)
        np.testing.assert_array_equal(alternate.fixings[:,:1],self.s.fixings[:,:1])
        self.assertEqual(self.s.delta[0],181/365)
        self.assertFalse(np.array_equal(alternate.states,self.s.states))

    def test_terminal_drift_shift_and_sign(self):
        s=self.s; f=np.broadcast_to(s.f0[1:],(2,20))
        mu=drift(f,s.delta[1:],s.diffusion[1:],self.data.shift)
        self.assertTrue(np.all(mu[:,-1]==0))
        expected=-sum(s.delta[j]*(s.f0[j]+.03)/(1+s.delta[j]*s.f0[j])*np.dot(s.diffusion[1],s.diffusion[j]) for j in range(2,21))
        self.assertAlmostEqual(mu[0,0],expected,places=15)
        # No sustituir F+s por F en el numerador.
        wrong=-sum(s.delta[j]*s.f0[j]/(1+s.delta[j]*s.f0[j])*np.dot(s.diffusion[1],s.diffusion[j]) for j in range(2,21))
        self.assertGreater(abs(expected-wrong),1e-4)

    def test_freeze_fixings_and_last_discount(self):
        s=self.s
        for n in range(1,21):
            np.testing.assert_array_equal(s.states[n,:,:n],s.states[n-1,:,:n])
        for j in range(20):
            np.testing.assert_array_equal(s.fixings[:,j],s.states[j,:,j])
        np.testing.assert_allclose(s.terminal_bonds[:,-1],1/(1+s.delta[20]*s.states[20,:,20]),rtol=0,atol=1e-15)

    def test_last_forward_exact_log_step(self):
        # El último forward tiene drift cero; telescopa log-incrementos exactos.
        s=self.s;lam=s.diffusion[-1];h=np.full(20,.5)
        exponent=np.sum(np.sqrt(h)[:,None]*(self.data.normals.transpose(1,2,0)@lam)-.5*np.dot(lam,lam)*h[:,None],axis=0)
        expected=(s.f0[-1]+.03)*np.exp(exponent)-.03
        np.testing.assert_allclose(s.states[20,:,-1],expected,rtol=0,atol=2e-16)

    def test_deterministic_zero_volatility(self):
        s=simulate(self.data,replace(Config(),vol_scale=0))
        r,cf,pv,_,_=estimate(s)
        np.testing.assert_allclose(s.states,np.broadcast_to(s.f0,s.states.shape),rtol=0,atol=2e-16)
        direct=np.sum((cf.paid_coupon+cf.paid_principal)*s.p0[1:21],axis=1)
        np.testing.assert_allclose(pv,direct,atol=1e-12,rtol=0)
        self.assertLess(r['standard_error'],1e-12)
        self.assertEqual(cf.redemption_period[0],5)

    def test_determinism_domain_and_covariance(self):
        other=simulate(self.data)
        np.testing.assert_array_equal(other.states,self.s.states)
        for n in range(21):
            self.assertTrue(np.all(self.s.states[n]+.03>0))
            self.assertTrue(np.all(1+self.s.delta*self.s.states[n]>0))
        np.testing.assert_allclose(np.diag(self.s.diffusion[1:]@self.s.diffusion[1:].T),self.data.vols[:20]**2,rtol=1e-14)

    def test_invalid_states_fail_closed(self):
        for state in [np.array([[-.031]]),np.array([[float('nan')]])]:
            with self.assertRaises(ValueError):drift(state,np.array([.5]),np.array([[.2,0,0]]),.03)
        for cfg in [Config(terminal=19),Config(scheme='bad'),Config(vol_scale=-1),Config(diffusion_clock='bad')]:
            with self.assertRaises(ValueError):simulate(self.data,cfg)

    def test_independent_scalar_all_paths(self):
        states,coupon,principal,pv=scalar_reference(self.data,self.s.dates,self.s.config)
        np.testing.assert_allclose(self.s.states,states,atol=1e-14,rtol=0)
        np.testing.assert_allclose(self.cf.paid_coupon,coupon,atol=1e-10,rtol=0)
        np.testing.assert_array_equal(self.cf.paid_principal,principal)
        np.testing.assert_allclose(self.pv,pv,atol=1e-10,rtol=0)

    def test_martingale_mc_diagnostics(self):
        checks=martingale_checks(self.s)
        self.assertEqual(len(checks),230)
        self.assertTrue(all(c['within_5se'] for c in checks))

    def test_estimator_is_on_whole_paths(self):
        r=self.report
        self.assertAlmostEqual(r['standard_error'],np.std(self.pv,ddof=1)/np.sqrt(200),places=14)
        self.assertAlmostEqual(r['price'],r['coupon_pv']+r['principal_pv'],places=12)
        self.assertEqual(sum(r['autocall_counts'])+r['maturity_no_call_count'],200)
        np.testing.assert_array_equal(self.cf.paid_principal.sum(axis=1),np.full(200,100))

class PayoffTests(unittest.TestCase):
    def test_zero_reference_and_full_trigger_coupon(self):
        cf=cashflows(np.zeros((1,20)),np.full(20,.5))
        self.assertEqual(cf.redemption_period[0],6)
        np.testing.assert_allclose(cf.rates[0,:6],[.01,.01,.01,.01,.02,.03])
        self.assertAlmostEqual(cf.cumulative_paid_fraction[0,5],.045)
        self.assertAlmostEqual(cf.paid_coupon[0,5],1.5)
        self.assertTrue(np.all(cf.paid_coupon[0,6:]==0))
        self.assertEqual(cf.paid_principal.sum(),100)

    def test_negative_coupon_memory_no_call_maturity(self):
        r=np.broadcast_to(SPREADS,(1,20)).copy();r[0,2]=.02
        cf=cashflows(r,np.full(20,.5))
        np.testing.assert_allclose(cf.rates[0,2:],-.01,rtol=0,atol=1e-16)
        self.assertTrue(np.all(cf.paid_coupon[0,2:]<0))
        self.assertFalse(cf.call_event.any())
        self.assertEqual(cf.paid_principal[0,-1],100)
        self.assertAlmostEqual(cf.cumulative_paid_fraction[0,-1],-.08)

    def test_equality_first_possible_call_and_no_double_principal(self):
        # Umbral exactamente igual a los intereses del primer cupón (fixture).
        cf=cashflows(np.zeros((1,20)),np.full(20,.5),target=.005)
        self.assertEqual(cf.redemption_period[0],1)
        self.assertEqual(cf.call_event.sum(),1)
        self.assertEqual(cf.paid_principal.sum(),100)
        self.assertAlmostEqual(cf.paid_coupon.sum(),.5)

    def test_negative_interest_reduces_target(self):
        r=np.zeros((1,20));r[0,2]=.03;r[0,3]=-.1
        cf=cashflows(r,np.full(20,.5))
        np.testing.assert_allclose(cf.cumulative_paid_fraction[0,:4],[.005,.01,0,.04],atol=1e-16)
        self.assertEqual(cf.redemption_period[0],4)

    def test_invalid_payoff_inputs(self):
        for r,d in [(np.zeros((1,19)),np.ones(20)),(np.full((1,20),np.nan),np.ones(20)),(np.zeros((1,20)),np.zeros(20))]:
            with self.assertRaises(ValueError):cashflows(r,d)

if __name__=='__main__':unittest.main()
