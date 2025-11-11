#!/usr/bin/env python3
'''Test the hypercube generation'''

######## Imports ########
import numpy as np
from basil_core.stats.hypercube import hypercube

######## Settings ########

NDIM = 3
RES_INT = 10
RES_ARR = 10*(np.arange(NDIM).astype(int) + 1)
LIMITS = np.asarray([
                     [-7., 7.],
                     [-7., 7.],
                     [-7., 7.],
                    ])

######## main ########

def main():
    # Test Hypercube with one resolution
    print("Testing hypercube with one resolution:")
    sample1 = hypercube(LIMITS, RES_INT)
    assert len(sample1.shape) == 2
    assert sample1.shape == (RES_INT**NDIM, NDIM)
    assert np.allclose(sample1[0], LIMITS[:,0])
    assert np.allclose(sample1[-1], LIMITS[:,1])
    print("  pass!")
    # Test Hypercube with many resolutions
    print("Testing hypercube with several resolutions:")
    sample2 = hypercube(LIMITS, RES_ARR)
    print(sample2.shape)
    assert len(sample2.shape) == 2
    assert sample2.shape == (np.prod(RES_ARR), NDIM)
    assert np.allclose(sample2[0], LIMITS[:,0])
    assert np.allclose(sample2[-1], LIMITS[:,1])
    print("  pass!")
    return

######## Execution ########
if __name__ == "__main__":
    main()
