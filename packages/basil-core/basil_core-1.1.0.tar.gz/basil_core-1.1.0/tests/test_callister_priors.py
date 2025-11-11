#!/usr/env/bin python3

######## Setup ########
AMAX = 1.
Q_LIMITS = [1e-6, 1.]
CHIEFF_LIMITS = [-1., 1.]
CHI_P_LIMITS = [-1., 1.]
M_LIMITS = [1., 150.]

######## Imports ########
import numpy as np
import time
from scipy.stats import gaussian_kde
from scipy.special import spence as PL

from basil_core.astro.priors.callister_priors import chi_effective_prior_from_aligned_spins
from basil_core.astro.priors.callister_priors import chi_effective_prior_from_isotropic_spins
from basil_core.astro.priors.callister_priors import chi_p_prior_from_isotropic_spins
from basil_core.astro.priors.callister_priors import chi_p_prior_given_chi_eff_q
from basil_core.astro.priors.callister_priors import chi_p_from_components
from basil_core.stats.hypercube import hypercube

######## Functions ########
def generate_q_xs(n=100):
    '''Generate initial data'''
    # Get number of points in one dimension
    ngrid = int(np.sqrt(n))
    # Get linspaces for each dimension
    q_grid = np.linspace(Q_LIMITS[0], Q_LIMITS[1],ngrid)
    xs_grid = np.linspace(CHIEFF_LIMITS[0], CHIEFF_LIMITS[1], ngrid)
    # Meshgrid
    q_grid, xs_grid = np.meshgrid(q_grid, xs_grid)
    # Flatten coordinates
    q_grid = q_grid.flatten()
    xs_grid = xs_grid.flatten()
    return q_grid, xs_grid

def generate_q_xs_xp(n=100):
    '''Generate initial data'''
    # Get number of points in one dimension
    ngrid = int(np.cbrt(n))
    # Get linspaces for each dimension
    limits = np.asarray([
                         Q_LIMITS,
                         CHIEFF_LIMITS,
                         CHI_P_LIMITS,
                        ])
    grid = hypercube(limits, ngrid)
    q, xs, xp = grid[:,0], grid[:,1], grid[:,2]
    return q, xs, xp

######## C extensions ########

'''
def cext_bhattacharyya_distance(n=100, nQ=1):
    # Get data
    if nQ == 1:
        x, P, Q = gaussian_example_data(n=n)
    else:
        x, P, Q = more_gaussian_example_data(n=n,nQ=nQ)
    t0 = time.time()
    B = bhattacharyya_distance(P, Q)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return B
'''

######## Numpy functions ########

def callister_chi_effective_prior_from_aligned_spins(n=100):
    # Get data
    q, xs = generate_q_xs(n=n)
    t0 = time.time()
    p = chi_effective_prior_from_aligned_spins(q, AMAX, xs)
    t1 = time.time()
    print("  Callister prior: %f seconds!"%(t1-t0))
    return p

def callister_chi_effective_prior_from_isotropic_spins(n=100):
    # Get data
    q, xs = generate_q_xs(n=n)
    t0 = time.time()
    p = chi_effective_prior_from_isotropic_spins(q, AMAX, xs)
    t1 = time.time()
    print("  Callister prior: %f seconds!"%(t1-t0))
    return p

def callister_chi_p_prior_from_isotropic_spins(n=100):
    # Get data
    q, xs = generate_q_xs(n=n)
    t0 = time.time()
    p = chi_p_prior_from_isotropic_spins(q, AMAX, xs)
    t1 = time.time()
    print("  Callister prior: %f seconds!"%(t1-t0))
    return p

def callister_chi_effective_prior_from_aligned_spins_fixed_q(n=100):
    # Get data
    q, xs = generate_q_xs(n=n)
    q = q[0]
    t0 = time.time()
    p = chi_effective_prior_from_aligned_spins(q, AMAX, xs)
    t1 = time.time()
    print("  Callister prior: %f seconds!"%(t1-t0))
    return p

def callister_chi_effective_prior_from_isotropic_spins_fixed_q(n=100):
    # Get data
    q, xs = generate_q_xs(n=n)
    q = q[0]
    t0 = time.time()
    p = chi_effective_prior_from_isotropic_spins(q, AMAX, xs)
    t1 = time.time()
    print("  Callister prior: %f seconds!"%(t1-t0))
    return p

def callister_chi_p_prior_from_isotropic_spins_fixed_q(n=100):
    # Get data
    q, xs = generate_q_xs(n=n)
    q = q[0]
    t0 = time.time()
    p = chi_p_prior_from_isotropic_spins(q, AMAX, xs)
    t1 = time.time()
    print("  Callister prior: %f seconds!"%(t1-t0))
    return p

'''
def numpy_bhattacharyya_distance(n=100,nQ=1):
    # Get data
    if nQ == 1:
        x, P, Q = gaussian_example_data(n=n)
    else:
        x, P, Q = more_gaussian_example_data(n=n,nQ=nQ)
    t0 = time.time()
    if nQ == 1:
        B = -np.log(np.sum(np.sqrt(P*Q)))
    else:
        B = -np.log(np.sum(np.sqrt(P*Q),axis=1))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return B
'''

######## Tests ########

'''
def bhattacharyya_distance_test(n=100, nQ=100):
    print("Bhattacharyya distance test")
    print(" nQ=1")
    B1 = cext_bhattacharyya_distance(n=n,nQ=1)
    B2 = numpy_bhattacharyya_distance(n=n,nQ=1)
    assert np.allclose(B1, B2)
    print("  pass!")

    print(" nQ=",nQ)
    B1 = cext_bhattacharyya_distance(n=n,nQ=nQ)
    B2 = numpy_bhattacharyya_distance(n=n,nQ=nQ)
    assert np.allclose(B1, B2)
    print("  pass!")
'''

def test_chi_effective_prior_from_aligned_spin(n=100):
    print("Chi effective prior from aligned spin:")
    # Do callister version
    p = callister_chi_effective_prior_from_aligned_spins(n=n)
    print("  pass!")

def test_chi_effective_prior_from_isotropic_spin(n=100):
    print("Chi effective prior from isotropic spin:")
    # Do callister version
    p = callister_chi_effective_prior_from_isotropic_spins(n=n)
    print("  pass!")

def test_chi_p_prior_from_isotropic_spins(n=100):
    print("chi_p prior from isotropic spins:")
    # Do callister version
    p = callister_chi_p_prior_from_isotropic_spins(n=n)
    print("  pass!")

def test_chi_effective_prior_from_aligned_spin_fixed_q(n=100):
    print("Chi effective prior from aligned spin:")
    # Do callister version
    p = callister_chi_effective_prior_from_aligned_spins_fixed_q(n=n)
    print("  pass!")

def test_chi_effective_prior_from_isotropic_spin_fixed_q(n=100):
    print("Chi effective prior from isotropic spin:")
    # Do callister version
    p = callister_chi_effective_prior_from_isotropic_spins_fixed_q(n=n)
    print("  pass!")

def test_chi_p_prior_from_isotropic_spins_fixed_q(n=100):
    print("chi_p prior from isotropic spins:")
    # Do callister version
    p = callister_chi_p_prior_from_isotropic_spins_fixed_q(n=n)
    print("  pass!")

######## All Tests ########

def all_test(**kwargs):
    #bhattacharyya_distance_test(**kwargs)
    test_chi_effective_prior_from_aligned_spin(**kwargs)
    test_chi_effective_prior_from_isotropic_spin(**kwargs)
    test_chi_p_prior_from_isotropic_spins(**kwargs)
    test_chi_effective_prior_from_aligned_spin_fixed_q(**kwargs)
    test_chi_effective_prior_from_isotropic_spin_fixed_q(**kwargs)
    test_chi_p_prior_from_isotropic_spins_fixed_q(**kwargs)

######## Main ########
def main():
    n = int(100)
    all_test(n=n)
    return

######## Execution ########
if __name__ == "__main__":
    main()

