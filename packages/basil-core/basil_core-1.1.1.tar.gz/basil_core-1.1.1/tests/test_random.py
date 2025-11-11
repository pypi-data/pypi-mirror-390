#!/usr/bin/env python3
'''Test the random number generation'''

######## Imports ########
import numpy as np
from basil_core.stats.random import random_unit_sphere, random_spherical
from fast_histogram import histogram1d
from basil_core.stats.distance import rel_entr

######## Settings ########

NPTS = int(1e6)
NBINS = 10
LIMITS = [-1., 1.]
SEED = 42
RS = np.random.RandomState(SEED)

######## main ########

def main():
    print("Testing random_unit_sphere:")
    # Make random unit sphere points
    X = random_unit_sphere(RS, NPTS)
    # Check that the average of the noize is close to zero
    assert np.abs(np.mean(X[:,0])) < 0.1
    assert np.abs(np.mean(X[:,1])) < 0.1
    assert np.abs(np.mean(X[:,2])) < 0.1
    # Check that noise is in [-1,1]
    assert (np.min(X[:,0]) < -0.99)
    assert (np.max(X[:,0]) > 0.99)
    assert (np.min(X[:,1]) < -0.99)
    assert (np.max(X[:,1]) > 0.99)
    assert (np.min(X[:,2]) < -0.99)
    assert (np.max(X[:,2]) > 0.99)
    # Check the magnitude of the distance
    r = np.sqrt(X[:,0]**2 + X[:,1]**2 + X[:,2]**2)
    #assert (np.max(r) < 1.) or np.isclose(np.max(r), 1.)
    assert np.allclose(r, 1.)
    # Check the distribution
    hx = histogram1d(X[:,0], NBINS, LIMITS) / NPTS
    hy = histogram1d(X[:,1], NBINS, LIMITS) / NPTS
    hz = histogram1d(X[:,2], NBINS, LIMITS) / NPTS
    # This will break if there is asymmetry in x, y, or z
    assert rel_entr(hx, hy) < 1e-4
    assert rel_entr(hy, hx) < 1e-4
    assert rel_entr(hx, hz) < 1e-4
    assert rel_entr(hz, hx) < 1e-4
    assert rel_entr(hy, hz) < 1e-4
    assert rel_entr(hz, hy) < 1e-4
    print("  pass!")

    print("Testing random_spherical:")
    X = random_spherical(RS, NPTS)
    # Check that the average of the noize is close to zero
    assert np.abs(np.mean(X[:,0])) < 0.1
    assert np.abs(np.mean(X[:,1])) < 0.1
    assert np.abs(np.mean(X[:,2])) < 0.1
    # Check that noise is in [-1,1]
    assert (np.min(X[:,0]) < -0.99)
    assert (np.max(X[:,0]) > 0.99)
    assert (np.min(X[:,1]) < -0.99)
    assert (np.max(X[:,1]) > 0.99)
    assert (np.min(X[:,2]) < -0.99)
    assert (np.max(X[:,2]) > 0.99)
    # Check the magnitude of the distance
    r = np.sqrt(X[:,0]**2 + X[:,1]**2 + X[:,2]**2)
    assert np.mean(r) < 1.
    assert (np.max(r) < 1.) or np.isclose(np.max(r), 1.)
    # Check the distribution
    hx = histogram1d(X[:,0], NBINS, LIMITS) / NPTS
    hy = histogram1d(X[:,1], NBINS, LIMITS) / NPTS
    hz = histogram1d(X[:,2], NBINS, LIMITS) / NPTS
    # This will break if there is asymmetry in x, y, or z
    assert rel_entr(hx, hy) < 1e-4
    assert rel_entr(hy, hx) < 1e-4
    assert rel_entr(hx, hz) < 1e-4
    assert rel_entr(hz, hx) < 1e-4
    assert rel_entr(hy, hz) < 1e-4
    assert rel_entr(hz, hy) < 1e-4
    print("  pass!")

######## Execution ########
if __name__ == "__main__":
    main()
