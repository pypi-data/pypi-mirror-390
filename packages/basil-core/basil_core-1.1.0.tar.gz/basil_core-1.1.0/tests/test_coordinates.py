#!/usr/env/bin python3

######## Setup ########
import numpy as np
from basil_core.astro.coordinates import mc_of_m1_m2, eta_of_m1_m2, mc_eta_of_m1_m2
from basil_core.astro.coordinates import M_of_mc_eta
from basil_core.astro.coordinates import m1_of_M_eta, m2_of_M_eta, m1_m2_of_M_eta
from basil_core.astro.coordinates import m1_of_mc_eta, m2_of_mc_eta, m1_m2_of_mc_eta
from basil_core.astro.coordinates import q_of_mc_eta
from basil_core.astro.coordinates import detector_of_source, source_of_detector
from basil_core.astro.coordinates import chieff_of_m1_m2_chi1z_chi2z
from basil_core.astro.coordinates import chiMinus_of_m1_m2_chi1z_chi2z
from basil_core.astro.coordinates import chieff_chiMinus_of_m1_m2_chi1z_chi2z
from basil_core.astro.coordinates import chi1z_of_m1_m2_chieff_chiMinus
from basil_core.astro.coordinates import chi2z_of_m1_m2_chieff_chiMinus
from basil_core.astro.coordinates import chi1z_chi2z_of_m1_m2_chieff_chiMinus
from basil_core.astro.coordinates import lambda_tilde_of_eta_lambda1_lambda2
from basil_core.astro.coordinates import delta_lambda_of_eta_lambda1_lambda2
from basil_core.astro.coordinates import lambda_tilde_delta_lambda_of_eta_lambda1_lambda2
from basil_core.astro.coordinates import lambda1_lambda2_of_eta_lambda_tilde_delta_lambda

import time

######## Functions ########

def get_m1_m2_examples(n=10):
    m1 = np.arange(n).astype(np.double) + 1.
    m2 = m1 + 1.
    return m1, m2

def get_m_z_examples(n=10):
    m = np.arange(1,n+1).astype(np.double)
    z = np.linspace(2,11,n)
    return m, z

def get_m1_m2_chi1z_chi2z_examples(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    chi1z = np.linspace(-0.5, 0.5, n)
    chi2z = np.copy(chi1z[::-1])
    return m1, m2, chi1z, chi2z

def get_eta_lambdatilde_deltalambda(n=10):
    m1 = np.arange(n).astype(np.double) + 1.
    m2 = m1 + 1.
    lambdatilde = np.linspace(1.,1000.,n)
    deltalambda = np.linspace(-100., 100., n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    return eta, lambdatilde, deltalambda

    
    

######## C extensions ########

def cext_mc_of_m1m2_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    t0 = time.time()
    mc = mc_of_m1_m2(m1, m2)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1 - t0))
    return mc

def cext_eta_of_m1m2_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    t0 = time.time()
    eta = eta_of_m1_m2(m1, m2)
    t1 = time.time()
    print("  C extension time\t%f seconds"%(t1 - t0))
    return eta

def cext_mc_eta_of_m1m2_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    t0 = time.time()
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1 - t0))
    return mc, eta

def cext_M_of_mc_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t0 = time.time()
    M = M_of_mc_eta(mc, eta)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return M

def cext_m1_of_M_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    M = M_of_mc_eta(mc, eta)
    t0 = time.time()
    m1 = m1_of_M_eta(M, eta)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return m1

def cext_m2_of_M_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    M = M_of_mc_eta(mc, eta)
    t0 = time.time()
    m2 = m2_of_M_eta(M, eta)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return m2

def cext_m1_m2_of_M_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    M = M_of_mc_eta(mc, eta)
    t0 = time.time()
    m1, m2 = m1_m2_of_M_eta(M, eta)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return m1, m2

def cext_m1_of_mc_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t0 = time.time()
    m1 = m1_of_mc_eta(mc, eta)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return m1

def cext_m2_of_mc_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t0 = time.time()
    m2 = m2_of_mc_eta(mc, eta)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return m2

def cext_m1_m2_of_mc_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t0 = time.time()
    m1, m2 = m1_m2_of_mc_eta(mc, eta)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return m1, m2

def cext_q_of_mc_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t0 = time.time()
    q = q_of_mc_eta(mc, eta)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return q

def cext_detector_of_source_test(n=10):
    m, z = get_m_z_examples(n=n)
    t0 = time.time()
    mdet = detector_of_source(m, z)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return mdet
    
def cext_source_of_detector_test(n=10):
    m, z = get_m_z_examples(n=n)
    t0 = time.time()
    msrc = source_of_detector(m, z)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return msrc
    
def cext_chieff_of_m1_m2_chi1z_chi2z_test(n=10):
    m1, m2, chi1z, chi2z = get_m1_m2_chi1z_chi2z_examples(n=n)
    t0 = time.time()
    chieff = chieff_of_m1_m2_chi1z_chi2z(m1, m2, chi1z, chi2z)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return chieff
    
def cext_chiMinus_of_m1_m2_chi1z_chi2z_test(n=10):
    m1, m2, chi1z, chi2z = get_m1_m2_chi1z_chi2z_examples(n=n)
    t0 = time.time()
    chiMinus = chiMinus_of_m1_m2_chi1z_chi2z(m1, m2, chi1z, chi2z)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return chiMinus
    
def cext_chieff_chiMinus_of_m1_m2_chi1z_chi2z_test(n=10):
    m1, m2, chi1z, chi2z = get_m1_m2_chi1z_chi2z_examples(n=n)
    t0 = time.time()
    chieff, chiMinus = chieff_chiMinus_of_m1_m2_chi1z_chi2z(m1, m2, chi1z, chi2z)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return chieff, chiMinus
    
def cext_chi1z_chi2z_of_m1_m2_chieff_chiMinus_test(n=10):
    m1, m2, s1z, s2z = get_m1_m2_chi1z_chi2z_examples(n=n)
    chieff, chiMinus = chieff_chiMinus_of_chi1z_chi2z(m1, m2, s1z, s2z)
    t0 = time.time()
    chi1z, chi2z = chi1z_chi2z_of_m1_m2_chieff_chiMinus(m1, m2, chieff, chiMinus)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return chi1z, chi2z

def cext_lambda_tilde_of_eta_lambda1_lambda2_test(n=10):
    eta, lambdatilde, deltalambda = get_eta_lambdatilde_deltalambda(n=n)
    lambda1, lambda2 = lam1_lam2_of_pe_params(eta, lambdatilde, deltalambda)
    t0 = time.time()
    lambda_tilde = lambda_tilde_of_eta_lambda1_lambda2(eta, lambda1, lambda2)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return lambda_tilde

def cext_delta_lambda_of_eta_lambda1_lambda2_test(n=10):
    eta, lambdatilde, deltalambda = get_eta_lambdatilde_deltalambda(n=n)
    lambda1, lambda2 = lam1_lam2_of_pe_params(eta, lambdatilde, deltalambda)
    t0 = time.time()
    delta_lambda = delta_lambda_of_eta_lambda1_lambda2(eta, lambda1, lambda2)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return delta_lambda

def cext_lambda_tilde_delta_lambda_of_eta_lambda1_lambda2_test(n=10):
    eta, lambdatilde, deltalambda = get_eta_lambdatilde_deltalambda(n=n)
    lambda1, lambda2 = lam1_lam2_of_pe_params(eta, lambdatilde, deltalambda)
    t0 = time.time()
    lambda_tilde, delta_lambda = lambda_tilde_delta_lambda_of_eta_lambda1_lambda2(eta, lambda1, lambda2)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return lambda_tilde, delta_lambda

def cext_lambda1_lambda2_of_eta_lambda_tilde_delta_lambda_test(n=10):
    eta, lambdatilde, deltalambda = get_eta_lambdatilde_deltalambda(n=n)
    #lambda1, lambda2 = lam1_lam2_of_pe_params(eta, lambdatilde, deltalambda)
    t0 = time.time()
    lambda1, lambda2 = lambda1_lambda2_of_eta_lambda_tilde_delta_lambda(eta, lambdatilde, deltalambda)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return lambda1, lambda2

######## Numpy functions ########

def numpy_mc_of_m1m2_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    t0 = time.time()
    mc = ((m1*m2)**0.6) * ((m1+m2)**-0.2)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return mc

def numpy_eta_of_m1m2_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    t0 = time.time()
    eta = (m1*m2)/((m1+m2)*(m1+m2))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return eta

def numpy_mc_eta_of_m1m2_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    t0 = time.time()
    mc = ((m1*m2)**0.6) * ((m1+m2)**-0.2)
    eta = (m1*m2)/((m1+m2)*(m1+m2))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return mc, eta

def numpy_M_of_mc_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t0 = time.time()
    M = mc*(eta**-0.6)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return M

def numpy_m1_of_M_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    M = M_of_mc_eta(mc, eta)
    t0 = time.time()
    m1 = (M/2.)*(1. + np.sqrt(1. - 4.*eta))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return m1

def numpy_m2_of_M_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    M = M_of_mc_eta(mc, eta)
    t0 = time.time()
    m2 = (M/2.)*(1. - np.sqrt(1. - 4.*eta))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return m2

def numpy_m1_m2_of_M_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    M = M_of_mc_eta(mc, eta)
    t0 = time.time()
    m1 = (M/2.)*(1. + np.sqrt(1. - 4.*eta))
    m2 = (M/2.)*(1. - np.sqrt(1. - 4.*eta))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return m1, m2

def numpy_m1_of_mc_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t0 = time.time()
    M = mc*(eta**-0.6)
    m1 = (M/2.)*(1. + np.sqrt(1. - 4.*eta))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return m1

def numpy_m2_of_mc_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t0 = time.time()
    M = mc*(eta**-0.6)
    m2 = (M/2.)*(1. - np.sqrt(1. - 4.*eta))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return m2

def numpy_m1_m2_of_mc_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t0 = time.time()
    M = mc*(eta**-0.6)
    m1 = (M/2.)*(1. + np.sqrt(1. - 4.*eta))
    m2 = (M/2.)*(1. - np.sqrt(1. - 4.*eta))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return m1, m2

def numpy_q_of_mc_eta_test(n=10):
    m1, m2 = get_m1_m2_examples(n=n)
    mc, eta = mc_eta_of_m1_m2(m1, m2)
    t0 = time.time()
    M = mc*(eta**-0.6)
    m1 = (M/2.)*(1. + np.sqrt(1. - 4.*eta))
    m2 = (M/2.)*(1. - np.sqrt(1. - 4.*eta))
    q = m2/m1
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return q

def numpy_detector_of_source_test(n=10):
    m, z = get_m_z_examples(n=n)
    t0 = time.time()
    mdet = m*(z + 1.)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return mdet
    
def numpy_source_of_detector_test(n=10):
    m, z = get_m_z_examples(n=n)
    t0 = time.time()
    msrc = m/(z + 1.)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return msrc

def chieff_of_m1m2s1s2(m1, m2, chi1z, chi2z):
    '''Convert from spin components to chieff
    Parameters
    ----------
    m1: array like, shape = (npts,)
        Input mass_1 values
    m2: array like, shape = (npts,)
        Input mass_2 values
    chi1z: array like, shape = (npts,)
        Input spin values
    chi2z: array like, shape = (npts,)
        Input spin values
    '''
    return ((m1*chi1z) + (m2*chi2z))/(m1 + m2)

def numpy_chieff_of_m1_m2_chi1z_chi2z_test(n=10):
    m1, m2, chi1z, chi2z = get_m1_m2_chi1z_chi2z_examples(n=n)
    t0 = time.time()
    chieff = chieff_of_m1m2s1s2(m1, m2, chi1z, chi2z)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return chieff

def chiMinus_of_m1m2s1s2(m1, m2, chi1z, chi2z):
    '''Convert from spin components to chi Minus
    Parameters
    ----------
    m1: array like, shape = (npts,)
        Input mass_1 values
    m2: array like, shape = (npts,)
        Input mass_2 values
    chi1z: array like, shape = (npts,)
        Input spin values
    chi2z: array like, shape = (npts,)
        Input spin values
    '''
    return ((m1*chi1z) - (m2*chi2z))/(m1 + m2)

def numpy_chiMinus_of_m1_m2_chi1z_chi2z_test(n=10):
    m1, m2, chi1z, chi2z = get_m1_m2_chi1z_chi2z_examples(n=n)
    t0 = time.time()
    chiMinus = chiMinus_of_m1m2s1s2(m1, m2, chi1z, chi2z)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return chiMinus

def chi1z_chi2z_of_chieff_chiMinus(m1, m2, chieff, chiMinus):
    '''get chi1 and chi2 from chieff and chiminus
    Parameters
    ----------
    m1: array like, shape = (npts,)
        Input mass_1 values
    m2: array like, shape = (npts,)
        Input mass_2 values
    chieff: array like, shape = (npts,)
        Input chi effective values
    chiMinus: array like, shape = (npts,)
        Input chi Minus values
    '''
    import numpy as np
    chi1z = (m1 + m2)*(chieff + chiMinus) / (2*m1)
    chi2z = (m1 + m2)*(chieff - chiMinus) / (2*m2)
    return chi1z, chi2z

def chieff_chiMinus_of_chi1z_chi2z(m1, m2, chi1z, chi2z):
    ''' Get chieff and chiminus from chi1z, chi2z
    Parameters
    ----------
    m1: array like, shape = (npts,)
        Input mass_1 values
    m2: array like, shape = (npts,)
        Input mass_2 values
    chi1z: array like, shape = (npts,)
        Input spin values
    chi2z: array like, shape = (npts,)
        Input spin values
    '''
    import numpy as np
    inv_M = 1/(m1 + m2)#np.power(m1 + m2, -1.)
    chieff = inv_M * (chi1z*m1 + chi2z*m2)
    chiMinus = inv_M * (chi1z*m1 - chi2z*m2)
    return chieff, chiMinus

def numpy_chieff_chiMinus_of_m1_m2_chi1z_chi2z_test(n=10):
    m1, m2, chi1z, chi2z = get_m1_m2_chi1z_chi2z_examples(n=n)
    t0 = time.time()
    chieff, chiMinus = chieff_chiMinus_of_chi1z_chi2z(m1, m2, chi1z, chi2z)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return chieff, chiMinus

def numpy_chi1z_chi2z_of_m1_m2_chieff_chiMinus_test(n=10):
    m1, m2, s1z, s2z = get_m1_m2_chi1z_chi2z_examples(n=n)
    chieff, chiMinus = chieff_chiMinus_of_chi1z_chi2z(m1, m2, s1z, s2z)
    t0 = time.time()
    chi1z, chi2z = chi1z_chi2z_of_chieff_chiMinus(m1, m2, chieff, chiMinus)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return chi1z, chi2z

def lam1_lam2_of_pe_params(eta, lambda_tilde, delta_lambda):
    """ get lambda_1 and lambda_2 from lambda_tilde and delta_lambda_tilde
    Parameters
    ----------
    eta: array like, shape = (npts,)
        Input eta values
    lambda_tilde: array_like, shape = (npts,)
        Input lambda tilde values
    delta_lambda: array_like, shape = (npts,)
        Input delta lambda tilde values
    """
    import numpy as np
    a = (8.0/13.0)*(1.0+7.0*eta-31.0*eta**2)
    b = (8.0/13.0)*np.sqrt(1.0-4.0*eta)*(1.0+9.0*eta-11.0*eta**2)
    c = (1.0/2.0)*np.sqrt(1.0-4.0*eta)*(1.0 - 13272.0*eta/1319.0 + 8944.0*eta**2/1319.0)
    d = (1.0/2.0)*(1.0 - 15910.0*eta/1319.0 + 32850.0*eta**2/1319.0 + 3380.0*eta**3/1319.0)
    den = (a+b)*(c-d) - (a-b)*(c+d)
    lambda_1 = ( (c-d)*lambda_tilde - (a-b)*delta_lambda )/den
    lambda_2 = (-(c+d)*lambda_tilde + (a+b)*delta_lambda )/den
    # Adjust lambda_1 and lambda_2 if lambda_1 becomes negative
    # lambda_2 should be adjusted such that lambda_tilde is held fixed
    #    if lambda_1<0:
    #        lambda_1 = 0
    #        lambda_2 = lambda_tilde / (a-b)
    return lambda_1, lambda_2

def numpy_lambda1_lambda2_of_eta_lambda_tilde_delta_lambda_test(n=10):
    eta, lambdatilde, deltalambda = get_eta_lambdatilde_deltalambda(n=n)
    t0 = time.time()
    lambda1, lambda2 = lam1_lam2_of_pe_params(eta, lambdatilde, deltalambda)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return lambda1, lambda2

def deltalambda_of_eta_lam1_lam2(eta, lambda_1, lambda_2):
    """ Get delta lambda tilde from eta, lambda1, lambda2 

    This is the definition found in Les Wade's paper.
    Les has factored out the quantity \sqrt(1-4\eta). It is different from Marc Favata's paper.
    $\delta\tilde\Lambda(\eta, \Lambda_1, \Lambda_2)$.
    Lambda_1 is assumed to correspond to the more massive (primary) star m_1.
    Lambda_2 is for the secondary star m_2.

    Parameters
    ----------
    eta: array like, shape = (npts,)
        Input eta values
    lambda_1: array_like, shape = (npts,)
        Input lambda_1 neturon star deformability
    lambda_2: array_like, shape = (npts,)
        Input lambda_2 neturon star deformability
    """
    import numpy as np
    return (1.0/2.0)*(
        np.sqrt(1.0-4.0*eta)*(1.0 - 13272.0*eta/1319.0 + 8944.0*eta**2/1319.0)*(lambda_1+lambda_2)
        + (1.0 - 15910.0*eta/1319.0 + 32850.0*eta**2/1319.0 + 3380.0*eta**3/1319.0)*(lambda_1-lambda_2)
    )
    
def lambdatilde_of_eta_lam1_lam2(eta, lambda_1, lambda_2):
    """ Get lambda tilde from eta, lambda1, lambda2 
    $\tilde\Lambda(\eta, \Lambda_1, \Lambda_2)$.
    Lambda_1 is assumed to correspond to the more massive (primary) star m_1.
    Lambda_2 is for the secondary star m_2.

    Parameters
    ----------
    eta: array like, shape = (npts,)
        Input eta values
    lambda_1: array_like, shape = (npts,)
        Input lambda_1 neturon star deformability
    lambda_2: array_like, shape = (npts,)
        Input lambda_2 neturon star deformability
    """
    import numpy as np
    return (8.0/13.0)*((1.0+7.0*eta-31.0*eta**2)*(lambda_1+lambda_2) + np.sqrt(1.0-4.0*eta)*(1.0+9.0*eta-11.0*eta**2)*(lambda_1-lambda_2))

def numpy_lambda_tilde_of_eta_lambda1_lambda2_test(n=10):
    eta, lambdatilde, deltalambda = get_eta_lambdatilde_deltalambda(n=n)
    lambda1, lambda2 = lam1_lam2_of_pe_params(eta, lambdatilde, deltalambda)
    t0 = time.time()
    lambda_tilde = lambdatilde_of_eta_lam1_lam2(eta, lambda1, lambda2)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return lambda_tilde

def numpy_delta_lambda_of_eta_lambda1_lambda2_test(n=10):
    eta, lambdatilde, deltalambda = get_eta_lambdatilde_deltalambda(n=n)
    lambda1, lambda2 = lam1_lam2_of_pe_params(eta, lambdatilde, deltalambda)
    t0 = time.time()
    delta_lambda = deltalambda_of_eta_lam1_lam2(eta, lambda1, lambda2)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return delta_lambda

def numpy_lambda_tilde_delta_lambda_of_eta_lambda1_lambda2_test(n=10):
    eta, lambdatilde, deltalambda = get_eta_lambdatilde_deltalambda(n=n)
    lambda1, lambda2 = lam1_lam2_of_pe_params(eta, lambdatilde, deltalambda)
    t0 = time.time()
    lambda_tilde = lambdatilde_of_eta_lam1_lam2(eta, lambda1, lambda2)
    delta_lambda = deltalambda_of_eta_lam1_lam2(eta, lambda1, lambda2)
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1 - t0))
    return lambda_tilde, delta_lambda

######## Tests ########

def mc_of_m1m2_test(n=10):
    print("mc_of_m1m2 test")
    mc1 = cext_mc_of_m1m2_test(n=n)
    mc2 = numpy_mc_of_m1m2_test(n=n)
    assert np.allclose(mc1, mc2)
    print("  pass!")

def eta_of_m1m2_test(n=10):
    print("eta_of_m1m2 test")
    eta1 = cext_eta_of_m1m2_test(n=n)
    eta2 = numpy_eta_of_m1m2_test(n=n)
    assert np.allclose(eta1, eta2)
    print("  pass!")

def mc_eta_of_m1m2_test(n=10):
    print("mc_eta_of_m1m2 test:")
    mc1, eta1 = cext_mc_eta_of_m1m2_test(n=n)
    mc2, eta2 = numpy_mc_eta_of_m1m2_test(n=n)
    assert np.allclose(mc1, mc2)
    assert np.allclose(eta1, eta2)
    print("  pass!")

def M_of_mc_eta_test(n=10):
    print("M_of_mc_eta test:")
    M1 = cext_M_of_mc_eta_test(n=n)
    M2 = numpy_M_of_mc_eta_test(n=n)
    assert np.allclose(M1, M2)
    print("  pass!")

def m1_of_M_eta_test(n=10):
    print("m1_of_M_eta test:")
    m1a = cext_m1_of_M_eta_test(n=n)
    m1b = numpy_m1_of_M_eta_test(n=n)
    assert np.allclose(m1a, m1b)
    print("  pass!")

def m2_of_M_eta_test(n=10):
    print("m2_of_M_eta test:")
    m2a = cext_m2_of_M_eta_test(n=n)
    m2b = numpy_m2_of_M_eta_test(n=n)
    assert np.allclose(m2a, m2b)
    print("  pass!")

def m1_m2_of_M_eta_test(n=10):
    print("m1_m2_of_M_eta test:")
    m1a, m2a = cext_m1_m2_of_M_eta_test(n=n)
    m1b, m2b = numpy_m1_m2_of_M_eta_test(n=n)
    assert np.allclose(m1a, m1b)
    assert np.allclose(m2a, m2b)
    print("  pass!")

def m1_of_mc_eta_test(n=10):
    print("m1_of_mc_eta test:")
    m1a = cext_m1_of_mc_eta_test(n=n)
    m1b = numpy_m1_of_mc_eta_test(n=n)
    assert np.allclose(m1a, m1b)
    print("  pass!")

def m2_of_mc_eta_test(n=10):
    print("m2_of_mc_eta test:")
    m2a = cext_m2_of_mc_eta_test(n=n)
    m2b = numpy_m2_of_mc_eta_test(n=n)
    assert np.allclose(m2a, m2b)
    print("  pass!")

def m1_m2_of_mc_eta_test(n=10):
    print("m1_m2_of_mc_eta test:")
    m1a, m2a = cext_m1_m2_of_mc_eta_test(n=n)
    m1b, m2b = numpy_m1_m2_of_mc_eta_test(n=n)
    assert np.allclose(m1a, m1b)
    assert np.allclose(m2a, m2b)
    print("  pass!")

def q_of_mc_eta_test(n=10):
    print("q_of_mc_eta test:")
    q1 = cext_q_of_mc_eta_test(n=n)
    q2 = numpy_q_of_mc_eta_test(n=n)
    assert np.allclose(q1, q2)
    print("  pass!")

def detector_of_source_test(n=10):
    print("detector_of_source test:")
    mdet1 = cext_detector_of_source_test(n=n)
    mdet2 = numpy_detector_of_source_test(n=n)
    assert np.allclose(mdet1, mdet2)
    print("  pass!")

def source_of_detector_test(n=10):
    print("source_of_detector test:")
    msrc1 = cext_source_of_detector_test(n=n)
    msrc2 = numpy_source_of_detector_test(n=n)
    assert np.allclose(msrc1, msrc2)
    print("  pass!")

def chieff_of_m1_m2_chi1z_chi2z_test(n=10):
    print("chieff_of_m1_m2_chi1z_chi2z test:")
    chieff1 = cext_chieff_of_m1_m2_chi1z_chi2z_test(n=n)
    chieff2 = numpy_chieff_of_m1_m2_chi1z_chi2z_test(n=n)
    assert np.allclose(chieff1, chieff2)
    print("  pass!")

def chiMinus_of_m1_m2_chi1z_chi2z_test(n=10):
    print("chiMinus_of_m1_m2_chi1z_chi2z test:")
    chiMinus1 = cext_chiMinus_of_m1_m2_chi1z_chi2z_test(n=n)
    chiMinus2 = numpy_chiMinus_of_m1_m2_chi1z_chi2z_test(n=n)
    assert np.allclose(chiMinus1, chiMinus2)
    print("  pass!")

def chieff_chiMinus_of_m1_m2_chi1z_chi2z_test(n=10):
    print("chieff_chiMinus_of_m1_m2_chi1z_chi2z test:")
    chieff1, chiMinus1 = cext_chieff_chiMinus_of_m1_m2_chi1z_chi2z_test(n=n)
    chieff2, chiMinus2 = numpy_chieff_chiMinus_of_m1_m2_chi1z_chi2z_test(n=n)
    assert np.allclose(chieff1, chieff2)
    assert np.allclose(chiMinus1, chiMinus2)
    print("  pass!")

def chi1z_chi2z_of_m1_m2_chieff_chiMinus_test(n=10):
    print("chi1z_chi2z_of_m1_m2_chieff_chiMinus test:")
    chi1za, chi2za = cext_chi1z_chi2z_of_m1_m2_chieff_chiMinus_test(n=n)
    chi1zb, chi2zb = numpy_chi1z_chi2z_of_m1_m2_chieff_chiMinus_test(n=n)
    assert np.allclose(chi1za, chi1zb)
    assert np.allclose(chi2za, chi2zb)
    print("  pass!")

def lambda_tilde_of_eta_lambda1_lambda2_test(n=10):
    print("lambda_tilde_of_eta_lambda1_lambda2 test:")
    lambda_tilde1 = cext_lambda_tilde_of_eta_lambda1_lambda2_test(n=n)
    lambda_tilde2 = numpy_lambda_tilde_of_eta_lambda1_lambda2_test(n=n)
    assert np.allclose(lambda_tilde1, lambda_tilde2)
    print("  pass!")

def delta_lambda_of_eta_lambda1_lambda2_test(n=10):
    print("delta_lambda_of_eta_lambda1_lambda2 test:")
    delta_lambda1 = cext_delta_lambda_of_eta_lambda1_lambda2_test(n=n)
    delta_lambda2 = numpy_delta_lambda_of_eta_lambda1_lambda2_test(n=n)
    assert np.allclose(delta_lambda1, delta_lambda2)
    print("  pass!")

def lambda_tilde_delta_lambda_of_eta_lambda1_lambda2_test(n=10):
    print("lambda_tilde_delta_lambda_of_eta_lambda1_lambda2 test:")
    lambda_tilde1, delta_lambda1 = cext_lambda_tilde_delta_lambda_of_eta_lambda1_lambda2_test(n=n)
    lambda_tilde2, delta_lambda2 = numpy_lambda_tilde_delta_lambda_of_eta_lambda1_lambda2_test(n=n)
    assert np.allclose(lambda_tilde1, lambda_tilde2)
    assert np.allclose(delta_lambda1, delta_lambda2)
    print("  pass!")

def lambda1_lambda2_of_eta_lambda_tilde_delta_lambda_test(n=10):
    print("lambda1_lambda2_of_eta_lambda_tilde_delta_lambda test:")
    lambda1a, lambda2a = cext_lambda1_lambda2_of_eta_lambda_tilde_delta_lambda_test(n=n)
    lambda1b, lambda2b = numpy_lambda1_lambda2_of_eta_lambda_tilde_delta_lambda_test(n=n)
    assert np.allclose(lambda1a, lambda1b)
    assert np.allclose(lambda2a, lambda2b)
    print("  pass!")

######## All Tests ########

def all_test(n=10):
    mc_of_m1m2_test(n=n)
    eta_of_m1m2_test(n=n)
    mc_eta_of_m1m2_test(n=n)
    M_of_mc_eta_test(n=n)
    m1_of_M_eta_test(n=n)
    m2_of_M_eta_test(n=n)
    m1_m2_of_M_eta_test(n=n)
    m1_of_mc_eta_test(n=n)
    m2_of_mc_eta_test(n=n)
    m1_m2_of_mc_eta_test(n=n)
    q_of_mc_eta_test(n=n)
    detector_of_source_test(n=n)
    source_of_detector_test(n=n)
    chieff_of_m1_m2_chi1z_chi2z_test(n=n)
    chiMinus_of_m1_m2_chi1z_chi2z_test(n=n)
    chieff_chiMinus_of_m1_m2_chi1z_chi2z_test(n=n)
    chi1z_chi2z_of_m1_m2_chieff_chiMinus_test(n=n)
    lambda_tilde_of_eta_lambda1_lambda2_test(n=n)
    delta_lambda_of_eta_lambda1_lambda2_test(n=n)
    lambda_tilde_delta_lambda_of_eta_lambda1_lambda2_test(n=n)
    lambda1_lambda2_of_eta_lambda_tilde_delta_lambda_test(n=n)

######## Main ########
def main():
    n = int(1e4)
    all_test(n=n)
    return

######## Execution ########
if __name__ == "__main__":
    main()

