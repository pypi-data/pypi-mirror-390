#!/usr/env/bin python3

######## Setup ########
import numpy as np
import time

from basil_core.stats.distance import bhattacharyya_distance
from basil_core.stats.distance import hellinger_distance
from basil_core.stats.distance import rel_entr

######## Functions ########

def gaussian(x,mu=0., sig=1.):
    from scipy.stats import norm
    Y = norm.pdf(x,loc=mu,scale=sig)
    Y /= np.sum(Y)
    return Y

def misaligned_gaussians(x, mu1=0, mu2=1, sig1=1, sig2=1):
    P = gaussian(x,mu=mu1,sig=sig1)
    Q = gaussian(x,mu=mu2,sig=sig2)
    return P, Q

def gaussian_example_data(n=100):
    x = np.linspace(1,2,n)
    P, Q = misaligned_gaussians(x)
    return x, P, Q

def more_gaussian_example_data(n=100,nQ=10):
    assert nQ <= 1e4
    x = np.linspace(1e-4,1,n)
    rs = np.random.RandomState(42)
    mu = rs.uniform(size=nQ)
    P = gaussian(x)
    Q = []
    for item in mu:
        Q.append(gaussian(x,mu=item))
    Q = np.asarray(Q)
    return x, P, Q

######## C extensions ########

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

def cext_hellinger_distance(n=100, nQ=1):
    # Get data
    if nQ == 1:
        x, P, Q = gaussian_example_data(n=n)
    else:
        x, P, Q = more_gaussian_example_data(n=n,nQ=nQ)
    t0 = time.time()
    B = hellinger_distance(P, Q)
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return B

def cext_relative_entropy(opts=[0,0,0,0],n=100, nQ=1):
    # Get data
    if nQ == 1:
        x, P, Q = gaussian_example_data(n=n)
    else:
        x, P, Q = more_gaussian_example_data(n=n,nQ=nQ)
    ## Check if we need to normalize or not
    if opts[0] == 0:
        normQ = False
    else:
        normQ = True
        Q *= 1.1
    # Get log values
    lnP = np.log(P)
    lnQ = np.log(Q)
    # Delete important things to test code
    if opts[1] == 0:
        lnP = None
    if opts[2] == 0:
        Q = None
    if opts[3] == 0:
        lnQ = None
    # start timing
    t0 = time.time()
    # Calculate the entropy
    E = rel_entr(P, lnP=lnP, Q=Q, lnQ=lnQ, normQ=normQ)
    # end the time
    t1 = time.time()
    print("  C extension time:\t%f seconds"%(t1-t0))
    return E

######## Numpy functions ########

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

def numpy_hellinger_distance(n=100,nQ=1):
    # Get data
    if nQ == 1:
        x, P, Q = gaussian_example_data(n=n)
    else:
        x, P, Q = more_gaussian_example_data(n=n,nQ=nQ)
    t0 = time.time()
    if nQ == 1:
        B = np.sqrt(1 - np.sum(np.sqrt(P*Q)))
    else:
        B = np.sqrt(1 - np.sum(np.sqrt(P*Q),axis=1))
    t1 = time.time()
    print("  Numpy time:\t\t%f seconds"%(t1-t0))
    return B

######## Scipy functions ########

def scipy_relative_entropy(n=100, nQ=1, opts=[0,0,0,0]):
    from scipy.special import rel_entr
    # Get data
    if nQ == 1:
        x, P, Q = gaussian_example_data(n=n)
    else:
        x, P, Q = more_gaussian_example_data(n=n,nQ=nQ)
    # Start timing
    t0 = time.time()
    # Check if we need to do a sum
    if opts[0]:
        if nQ == 1:
            Q = Q/np.sum(Q)
        else:
            Q = Q/np.sum(Q,axis=1).reshape((nQ,1))
    # Case nQ == 1
    if nQ == 1:
        E = np.sum(rel_entr(P, Q))
    # Case nQ > 1
    else:
        E = np.empty(nQ)
        for i in range(nQ):
            E[i] = np.sum(rel_entr(P, Q[i]))
    # end timing
    t1 = time.time()
    print("  Scipy time:\t\t%f seconds"%(t1-t0))
    return E

######## Tests ########

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

def hellinger_distance_test(n=100, nQ=100):
    print("Hellinger distance test")
    print(" nQ=1")
    H1 = cext_hellinger_distance(n=n,nQ=1)
    H2 = numpy_hellinger_distance(n=n,nQ=1)
    assert np.allclose(H1, H2)
    print("  pass!")

    print(" nQ=",nQ)
    H1 = cext_hellinger_distance(n=n,nQ=nQ)
    H2 = numpy_hellinger_distance(n=n,nQ=nQ)
    assert np.allclose(H1, H2)
    print("  pass!")

def relative_entropy_test(n=1000,nQ=100):
    print("Relative Entropy test")
    _nQ = np.copy(nQ)

    #### Failing cases ####
    # Case nQ = 1, Qnorm = False, lnP = None, Q = None, lnQ = None
    # should fail
    _nQ, opts = 1, [0,0,0,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    try:
        E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
        raise RuntimeError("This should have failed!")
    except:
        pass

    # Case nQ = nQ, Qnorm = False, lnP = None, Q = None, lnQ = None
    # should fail
    _nQ, opts = nQ, [0,0,0,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    try:
        E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
        raise RuntimeError("This should have failed!")
    except:
        pass

    # Case nQ = 1, Qnorm = True, lnP = None, Q = None, lnQ = None
    # should fail
    _nQ, opts = 1, [1,0,0,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    try:
        E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
        raise RuntimeError("This should have failed!")
    except:
        pass

    # Case nQ = nQ, Qnorm = True, lnP = None, Q = None, lnQ = None
    # should fail
    _nQ, opts = nQ, [1,0,0,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    try:
        E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
        raise RuntimeError("This should have failed!")
    except:
        pass

    # Case nQ = 1, Qnorm = False, lnP = lnP, Q = None, lnQ = None
    # should fail
    _nQ, opts = 1, [0,1,0,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    try:
        E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
        raise RuntimeError("This should have failed!")
    except:
        pass

    # Case nQ = nQ, Qnorm = False, lnP = lnP, Q = None, lnQ = None
    # should fail
    _nQ, opts = nQ, [0,1,0,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    try:
        E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
        raise RuntimeError("This should have failed!")
    except:
        pass

    # Case nQ = 1, Qnorm = True, lnP = lnP, Q = None, lnQ = None
    # should fail
    _nQ, opts = 1, [1,1,0,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    try:
        E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
        raise RuntimeError("This should have failed!")
    except:
        pass

    # Case nQ = nQ, Qnorm = True, lnP = lnP, Q = None, lnQ = None
    # should fail
    _nQ, opts = nQ, [1,1,0,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    try:
        E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
        raise RuntimeError("This should have failed!")
    except:
        pass

    #### Cases that should not fail ####
    # Case nQ = 1, Qnorm = False, lnP = None, Q = Q lnQ = None
    _nQ, opts = 1, [0,0,1,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = False, lnP = None, Q = Q lnQ = None
    _nQ, opts = nQ, [0,0,1,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = True, lnP = None, Q = Q lnQ = None
    _nQ, opts = 1, [1,0,1,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = True, lnP = None, Q = Q lnQ = None
    _nQ, opts = nQ, [1,0,1,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = False, lnP = lnP, Q = Q lnQ = None
    _nQ, opts = 1, [0,1,1,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = False, lnP = lnP, Q = Q lnQ = None
    _nQ, opts = nQ, [0,1,1,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = True, lnP = lnP, Q = Q lnQ = None
    _nQ, opts = 1, [1,1,1,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = True, lnP = lnP, Q = Q lnQ = None
    _nQ, opts = nQ, [1,1,1,0]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = False, lnP = None, Q = None, lnQ = lnQ
    _nQ, opts = 1, [0,0,0,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = False, lnP = None, Q = None, lnQ = lnQ
    _nQ, opts = nQ, [0,0,0,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = True, lnP = None, Q = None, lnQ = lnQ
    _nQ, opts = 1, [1,0,0,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = True, lnP = None, Q = None, lnQ = lnQ
    _nQ, opts = nQ, [1,0,0,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = False, lnP = lnP, Q = None, lnQ = lnQ
    _nQ, opts = 1, [0,1,0,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = False, lnP = lnP, Q = None, lnQ = lnQ
    _nQ, opts = nQ, [0,1,0,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = True, lnP = lnP, Q = None, lnQ = lnQ
    _nQ, opts = 1, [1,1,0,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = True, lnP = lnP, Q = None, lnQ = lnQ
    _nQ, opts = nQ, [1,1,0,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = False, lnP = None, Q = Q, lnQ = lnQ
    _nQ, opts = 1, [0,0,1,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = False, lnP = None, Q = Q, lnQ = lnQ
    _nQ, opts = nQ, [0,0,1,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = True, lnP = None, Q = Q, lnQ = lnQ
    _nQ, opts = 1, [1,0,1,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = True, lnP = None, Q = Q, lnQ = lnQ
    _nQ, opts = nQ, [1,0,1,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = False, lnP = lnP, Q = Q, lnQ = lnQ
    _nQ, opts = 1, [0,1,1,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = False, lnP = lnP, Q = Q, lnQ = lnQ
    _nQ, opts = nQ, [0,1,1,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = 1, Qnorm = True, lnP = lnP, Q = Q, lnQ = lnQ
    _nQ, opts = 1, [1,1,1,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")

    # Case nQ = nQ, Qnorm = True, lnP = lnP, Q = Q, lnQ = lnQ
    _nQ, opts = nQ, [1,1,1,1]
    print(" nQ=%d, opts = %s"%(_nQ, str(opts)))
    E1 = cext_relative_entropy(n=n, nQ=_nQ, opts=opts)
    E2 = scipy_relative_entropy(n=n, nQ=_nQ, opts=opts)
    assert np.allclose(E1, E2)
    print("  pass!")



######## All Tests ########

def all_test(**kwargs):
    bhattacharyya_distance_test(**kwargs)
    hellinger_distance_test(**kwargs)
    relative_entropy_test(**kwargs)

######## Main ########
def main():
    n = int(1e5)
    nQ = 1000
    all_test(n=n, nQ=nQ)
    return

######## Execution ########
if __name__ == "__main__":
    main()

