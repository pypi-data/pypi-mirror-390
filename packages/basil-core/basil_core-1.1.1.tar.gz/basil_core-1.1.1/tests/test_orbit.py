#!/usr/env/bin python3

######## Setup ########
import numpy as np
import time

from astropy import constants as const
from astropy import units as u

######## Globals ########
MSUN = const.M_sun.value
RSUN = const.R_sun.value
G = const.G.value
c = const.c.value
SEC_PER_DAY = 86400
CHANDRASEKHAR_LIMIT = 1.4

######## Functions ########

def m1m2_grid(m1_min=1., m1_max=50., m2_min=1., m2_max=50., n=10):
    m1 = np.linspace(m1_min, m1_max, n)
    m2 = np.linspace(m2_min, m2_max, n)
    m1, m2 = np.meshgrid(m1, m2)
    m1, m2 = m1.flatten(), m2.flatten()
    m1, m2 = m1*MSUN, m2*MSUN
    return m1, m2

def ecc_grid(ecc_min=1e-6, n=10):
    ecc_low = np.logspace(np.log10(ecc_min), np.log10(0.5), n//2)
    return np.concatenate([ecc_low, 1-ecc_low[::-1]])

def a0t_grid(a0_min=1., a0_max=100.,t_min=1.,t_max=100., n=10):
    a0 = np.linspace(a0_min, a0_max, n)
    t = np.linspace(t_min, t_max, n)
    a0, t = np.meshgrid(a0, t)
    a0, t = a0.flatten(), t.flatten()
    a0 = a0*RSUN
    t = t*SEC_PER_DAY
    return a0, t

def m1m2a0t_data(n=10):
    m1, m2 = m1m2_grid(n=n)
    a0, t = a0t_grid(n=n)
    return m1, m2, a0, t

def numpy_rad_WD(M):
    R_NS = 1.4e-5*np.ones(len(M))
    M_CH = CHANDRASEKHAR_LIMIT * MSUN
    M_CH_M_2_3 = (M_CH/M)**(2/3)
    M_M_CH_2_3 = (M/M_CH)**(2/3)
    A = 0.0115 * np.sqrt(M_CH_M_2_3 - M_M_CH_2_3)
    rad = np.max(np.array([R_NS, A]),axis=0)
    rad *= RSUN
    return rad
    
def m1m2r1r2_data(n=10):
    m1, m2 = m1m2_grid(m1_max=CHANDRASEKHAR_LIMIT,m2_max=CHANDRASEKHAR_LIMIT,n=n)
    r1, r2 = numpy_rad_WD(m1), numpy_rad_WD(m2)
    return m1, m2, r1, r2

######## C extensions ########

def cext_beta(n=100):
    from basil_core.astro.orbit import beta
    # Get data
    m1, m2 = m1m2_grid(n=n)
    tic = time.perf_counter()
    beta_arr = beta(m1, m2,unit=True,fallback=False)
    toc = time.perf_counter()
    print("  C extension time:\t%f seconds"%(toc-tic))
    return beta_arr

def cext_peters_ecc_const(n=100):
    from basil_core.astro.orbit import peters_ecc_const
    # Get data
    ecc = ecc_grid(n=n)
    tic= time.perf_counter()
    c0_ecc = peters_ecc_const(ecc,fallback=False)
    toc = time.perf_counter()
    print(f"  C extension time:\t{toc-tic:.6f} seconds")
    return c0_ecc

def cext_peters_ecc_integrand(n=100):
    from basil_core.astro.orbit import peters_ecc_integrand
    # Get data
    ecc = ecc_grid(n=n)
    tic= time.perf_counter()
    c0_ecc = peters_ecc_integrand(ecc,fallback=False)
    toc = time.perf_counter()
    print(f"  C extension time:\t{toc-tic:.6f} seconds")
    return c0_ecc

def cext_orbital_separation_evolve(n=100):
    from basil_core.astro.orbit import orbital_separation_evolve
    m1, m2, a0, t = m1m2a0t_data(n=n)
    tic = time.perf_counter()
    a_arr = orbital_separation_evolve(m1, m2, a0, t)
    toc = time.perf_counter()
    print("  C extension time:\t%f seconds"%(toc-tic))
    return a_arr

def cext_orbital_period_of_m1_m2_a(n=100):
    from basil_core.astro.orbit import orbital_period_of_m1_m2_a
    m1, m2, a, t = m1m2a0t_data(n=n)
    tic = time.perf_counter()
    P_arr = orbital_period_of_m1_m2_a(m1, m2, a, fallback=False)
    toc = time.perf_counter()
    print("  C extension time:\t%f seconds"%(toc-tic))
    return P_arr

def cext_time_of_orbital_shrinkage(n=100):
    from basil_core.astro.orbit import time_of_orbital_shrinkage
    m1, m2, a0, t = m1m2a0t_data(n=n)
    af = a0/2
    tic = time.perf_counter()
    t_arr = time_of_orbital_shrinkage(m1, m2, a0, af)
    toc = time.perf_counter()
    print("  C extension time:\t%f seconds"%(toc-tic))
    return t_arr

def cext_time_to_merge_of_m1_m2_a0(n=100,silent=False):
    from basil_core.astro.orbit import time_to_merge_of_m1_m2_a0
    m1, m2, a0, t = m1m2a0t_data(n=n)
    tic = time.perf_counter()
    t_arr = time_to_merge_of_m1_m2_a0(m1*u.kg, m2*u.kg, a0*u.m, fallback=False)
    toc = time.perf_counter()
    if not silent:
        print("  C extension time:\t%f seconds"%(toc-tic))
    return t_arr

def cext_merge_time_integral_sgl(n=100):
    from basil_core.astro.orbit import merge_time_integral_sgl
    m1, m2, a0, t = m1m2a0t_data(n=n)
    ecc = ecc_grid(n=n**2)
    tic = time.perf_counter()
    t_arr = np.empty_like(ecc)
    for i in range(ecc.size):
        t_arr[i] = merge_time_integral_sgl(m1[i],m2[i],a0[i],ecc[i])
    toc = time.perf_counter()
    print(f"  C extension (sgl) time:\t{toc-tic:.6f} seconds")
    return t_arr

def cext_merge_time_integral_arr(n=100):
    from basil_core.astro.orbit import merge_time_integral
    m1, m2, a0, t = m1m2a0t_data(n=n)
    ecc = ecc_grid(n=n**2)
    tic = time.perf_counter()
    t_arr = merge_time_integral(m1,m2,a0,ecc)
    toc = time.perf_counter()
    print(f"  C extension (arr) time:\t{toc-tic:.6f} seconds")
    return t_arr

def cext_orbital_period_evolved_GW(n=100):
    from basil_core.astro.orbit import orbital_period_evolved_GW
    m1, m2, a0, t = m1m2a0t_data(n=n)
    tic = time.perf_counter()
    P_arr = orbital_period_evolved_GW(m1, m2, a0, t)
    toc = time.perf_counter()
    print("  C extension time:\t%f seconds"%(toc-tic))
    return P_arr

def cext_DWD_r_of_m(n=100):
    from basil_core.astro.orbit import DWD_r_of_m
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    tic = time.perf_counter()
    a_arr = DWD_r_of_m(m1)
    toc = time.perf_counter()
    print("  C extension time:\t%f seconds"%(toc-tic))
    return a_arr

def cext_DWD_RLOF_a_of_m1_m2_r1_r2(n=100):
    from basil_core.astro.orbit import DWD_RLOF_a_of_m1_m2_r1_r2
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    tic = time.perf_counter()
    a_arr = DWD_RLOF_a_of_m1_m2_r1_r2(m1, m2, r1, r2)
    toc = time.perf_counter()
    print("  C extension time:\t%f seconds"%(toc-tic))
    return a_arr

def cext_DWD_RLOF_P_of_m1_m2_r1_r2(n=100):
    from basil_core.astro.orbit import DWD_RLOF_P_of_m1_m2_r1_r2
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    tic = time.perf_counter()
    P_arr = DWD_RLOF_P_of_m1_m2_r1_r2(m1, m2, r1, r2)
    toc = time.perf_counter()
    print("  C extension time:\t%f seconds"%(toc-tic))
    return P_arr


######## NumPy functions ########

def numpy_beta(n=100):
    from basil_core.astro.orbit import beta_fn_numpy
    m1, m2 = m1m2_grid(n=n)
    tic = time.perf_counter()
    beta_arr = beta_fn_numpy(m1,m2,unit=True)
    toc = time.perf_counter()
    print("  NumPy time:\t\t%f seconds"%(toc-tic))
    return beta_arr

def numpy_peters_ecc_const(n=100):
    from basil_core.astro.orbit import peters_ecc_const_numpy
    # Get data
    ecc = ecc_grid(n=n)
    tic= time.perf_counter()
    c0_ecc = peters_ecc_const_numpy(ecc)
    toc = time.perf_counter()
    print(f"  NumPy time:\t\t{toc-tic:.6f} seconds")
    return c0_ecc

def numpy_peters_ecc_integrand(n=100):
    from basil_core.astro.orbit import peters_ecc_integrand_numpy
    # Get data
    ecc = ecc_grid(n=n)
    tic= time.perf_counter()
    c0_ecc = peters_ecc_integrand_numpy(ecc)
    toc = time.perf_counter()
    print(f"  NumPy time:\t\t{toc-tic:.6f} seconds")
    return c0_ecc

def numpy_orbital_separation_evolve(n=100):
    m1, m2, a0, t = m1m2a0t_data(n=n)
    tic = time.perf_counter()
    const = ((64 / 5) * G**3) * (c**-5)
    beta_arr = const * m1 * m2 * (m1 + m2)
    a_arr = np.sqrt(np.sqrt((a0 ** 4) - (4 * beta_arr * t)))
    toc = time.perf_counter()
    print("  NumPy time:\t\t%f seconds"%(toc-tic))
    return a_arr

def numpy_orbital_period_of_m1_m2_a(n=100):
    from basil_core.astro.orbit import orbital_period_numpy
    m1, m2, a, t = m1m2a0t_data(n=n)
    tic = time.perf_counter()
    P_arr = orbital_period_numpy(m1*u.kg,m2*u.kg,a*u.m)
    toc = time.perf_counter()
    print("  NumPy time:\t\t%f seconds"%(toc-tic))
    return P_arr

def numpy_time_of_orbital_shrinkage(n=100):
    m1, m2, a0, t = m1m2a0t_data(n=n)
    af = a0/2
    tic = time.perf_counter()
    const = ((64 / 5) * G**3) * (c**-5)
    beta_arr = const * m1 * m2 * (m1 + m2)
    t_arr = (a0 ** 4 - af ** 4) / 4 / beta_arr
    toc = time.perf_counter()
    print("  NumPy time:\t\t%f seconds"%(toc-tic))
    return t_arr

def numpy_time_to_merge_of_m1_m2_a0(n=100):
    from basil_core.astro.orbit import merge_time_circ_numpy
    m1, m2, a0, t = m1m2a0t_data(n=n)
    tic = time.perf_counter()
    t_arr = merge_time_circ_numpy(m1*u.kg,m2*u.kg,a0*u.m)
    toc = time.perf_counter()
    print("  NumPy time:\t\t%f seconds"%(toc-tic))
    return t_arr

def numpy_orbital_period_evolved_GW(n=100):
    m1, m2, a0, t = m1m2a0t_data(n=n)
    tic = time.perf_counter()
    const = ((64 / 5) * G**3) * (c**-5)
    beta_arr = const * m1 * m2 * (m1 + m2)
    a_arr = np.sqrt(np.sqrt((a0 ** 4) - (4 * beta_arr * t)))
    P_arr = np.sqrt(4 * np.pi**2 * a_arr**3 / (G * (m1 + m2)))
    toc = time.perf_counter()
    print("  NumPy time:\t\t%f seconds"%(toc-tic))
    return P_arr

def numpy_DWD_r_of_m(n=100):
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    tic = time.perf_counter()
    a_arr = numpy_rad_WD(m1)
    toc = time.perf_counter()
    print("  NumPy time:\t\t%f seconds"%(toc-tic))
    return a_arr

def numpy_DWD_RLOF_a_of_m1_m2_r1_r2(n=100):
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    tic = time.perf_counter()
    mA = np.where(m1>m2, m1, m2)
    mB = np.where(m1>m2, m2, m1)
    rB = np.where(m1>m2, r2, r1)
    q = mB/mA
    denominator = 0.49 * q**(2/3)
    numerator = 0.6 * q**(2/3) + np.log(1 + q**(1/3))
    a_arr = numerator * rB / denominator
    toc = time.perf_counter()
    print("  NumPy time:\t\t%f seconds"%(toc-tic))
    return a_arr

def numpy_DWD_RLOF_P_of_m1_m2_r1_r2(n=100):
    m1, m2, r1, r2 = m1m2r1r2_data(n=n)
    tic = time.perf_counter()
    mA = np.where(m1>m2, m1, m2)
    mB = np.where(m1>m2, m2, m1)
    rB = np.where(m1>m2, r2, r1)
    q = mB/mA
    denominator = 0.49 * q**(2/3)
    numerator = 0.6 * q**(2/3) + np.log(1 + q**(1/3))
    a_arr = numerator * rB / denominator
    P_arr = np.sqrt(4 * np.pi**2 * a_arr**3 / (G * (m1 + m2)))
    toc = time.perf_counter()
    print("  NumPy time:\t\t%f seconds"%(toc-tic))
    return P_arr

######## External ########
def legwork_merge_time_integral(n=100):
    import legwork
    from basil_core.astro.orbit import forb_of_m1_m2_a
    m1, m2, a0, t = m1m2a0t_data(n=n)
    m1 = m1 * u.kg
    m2 = m2 * u.kg
    a0 = a0 * u.m
    ecc = ecc_grid(n=n**2)
    forb = forb_of_m1_m2_a(m1,m2,a0).to("1/s")
    tic = time.perf_counter()
    Tl = legwork.evol.get_t_merge_ecc(
        ecc_i=ecc,
        f_orb_i=forb,
        m_1=m1,
        m_2=m2,
        small_e_tol=0.00001,
        large_e_tol=0.99999,
    )
    toc = time.perf_counter()
    print(f"  Legwork time:\t{toc-tic:.6f} seconds")
    return Tl

######## Tests ########
def beta_test(n=100):
    n = 2*int(np.sqrt(n)//2)
    print("Beta test")
    B1 = cext_beta(n=n)
    B2 = numpy_beta(n=n)
    assert np.allclose(B1, B2)
    print("  pass!")

def peters_ecc_const_test(n=100):
    print("Peters (1964) eccentricity part of constant of motion test")
    c1_ecc = cext_peters_ecc_const(n=n)
    c2_ecc = numpy_peters_ecc_const(n=n)
    assert np.allclose(c1_ecc, c2_ecc)
    print("  pass!")

def peters_ecc_integrand_test(n=100):
    print("Peters (1964) eccentricity part of constant of motion test")
    c1_ecc = cext_peters_ecc_integrand(n=n)
    c2_ecc = numpy_peters_ecc_integrand(n=n)
    assert np.allclose(c1_ecc, c2_ecc)
    print("  pass!")

def orbital_separation_evolve_test(n=100):
    print("Orbital Separation test")
    a1 = cext_orbital_separation_evolve(n=n)
    a2 = numpy_orbital_separation_evolve(n=n)
    assert np.allclose(a1, a2)
    print("  pass!")

def orbital_period_of_m1_m2_a_test(n=100):
    n = 2*int(np.sqrt(n)//2)
    print("Orbital Period test")
    P1 = cext_orbital_period_of_m1_m2_a(n=n)
    P2 = numpy_orbital_period_of_m1_m2_a(n=n)
    assert np.allclose(P1, P2.value)
    print("  pass!")

def orbital_frequency_test(n=100):
    n = 2*int(np.sqrt(n)//2)
    print(f"Orbital Frequency test")
    from basil_core.astro.orbit import orbital_period_of_m1_m2_a
    from basil_core.astro.orbit import forb_of_m1_m2_a
    from basil_core.astro.orbit import a_of_m1_m2_forb
    # Generate training data
    m1, m2, a, t = m1m2a0t_data(n=n)
    m1 = m1 * u.kg
    m2 = m2 * u.kg
    a = a * u.m
    # Ecaluate orbital period (tested previously)
    P = orbital_period_of_m1_m2_a(m1,m2,a).to('s')
    # Test orbital frequency
    forb = forb_of_m1_m2_a(m1,m2,a).to('1/s')
    assert np.allclose(1/P, forb)
    # Test semi-major axis
    sep = a_of_m1_m2_forb(m1,m2,forb).to('m')
    assert np.allclose(sep,a)
    print("  pass!")

def eccentricity_root_finder_test(n=100):
    n = 2*int(np.sqrt(n)//2)
    print(f"Eccentricity root finder test")
    from basil_core.astro.orbit import a_of_ecc
    from basil_core.astro.orbit import ecc_of_a0_e0_a1
    from basil_core.astro.orbit import peters_ecc_const
    # Generate training data
    a, t = a0t_grid(n=n)
    ecc = ecc_grid(n=n**2,ecc_min=1e-2)
    a = a * u.m
    # Get c0
    c0_ecc = peters_ecc_const(ecc,fallback=False)
    c0 = c0_ecc * a
    # Estimate a of ecc
    a1 = a_of_ecc(ecc, a0=a, e0=ecc)
    a2 = a_of_ecc(ecc, c0=c0)
    assert np.allclose(a1,a)
    assert np.allclose(a2,a)
    # Estimate ecc_of_a
    tic = time.perf_counter()
    ecc2 = ecc_of_a0_e0_a1(a,ecc,a2)
    toc = time.perf_counter()
    #print(f"  ecc_of_a ({n:.3e} evaluations): {toc-tic:.6f} s")
    #print(f"max: {np.max(np.abs(ecc-ecc2))}; avg: {np.std(np.abs(ecc-ecc2))}")
    assert np.allclose(ecc, ecc2)
    # TODO this is a pretty weak test
    print("  pass!")

    
def time_of_orbital_shrinkage_test(n=100):
    print("Orbital Shrinkage test")
    toc = cext_time_of_orbital_shrinkage(n=n)
    t2 = numpy_time_of_orbital_shrinkage(n=n)
    assert np.allclose(toc, t2)
    print("  pass!")

def time_to_merge_of_m1_m2_a0_test(n=100):
    n = 2*int(np.sqrt(n)//2)
    print("Time to merger test")
    t1 = cext_time_to_merge_of_m1_m2_a0(n=n)
    t2 = numpy_time_to_merge_of_m1_m2_a0(n=n)
    assert np.allclose(t1, t2)
    print("  pass!")

def merge_time_integral_test(n=100):
    n = 2*int(np.sqrt(n)//2)
    print("merge_time_integral_test")
    Tc = cext_time_to_merge_of_m1_m2_a0(n=n,silent=True).to('Myr')
    Tsgl = (cext_merge_time_integral_sgl(n=n) * u.s).to('Myr')
    Tarr = (cext_merge_time_integral_arr(n=n) * u.s).to('Myr')
    assert not np.any(Tc < Tsgl)
    assert np.allclose(Tsgl, Tarr)
    # External test (depends on packages not required by default)
    try:
        import legwork
    except:
        print("  pass!")
        return
    # Test Legwork
    Tl = legwork_merge_time_integral(n=n)
    residual = np.abs(Tl - Tarr)
    print("  Numerical integral vs legwork residual"
        f"max: {np.max(residual)}, mean: {np.mean(residual)}")
    print("  pass!")

def merge_time_methods_test(n=100):
    from matplotlib import pyplot as plt
    from basil_core.astro.orbit import merge_time
    from basil_core.astro.orbit import inv_merge_time_circ

    n = (2*int(np.sqrt(n)//2))**2
    print(f"merge time methods test ({n} evaluations)")
    # Get data
    ecc = ecc_grid(n=n)
    m1 = np.ones(n) * 4 * u.solMass
    m2 = np.ones(n) * u.solMass
    a = np.ones(n) * u.solRad
    ## Try methods ##
    # Circular
    tic = time.perf_counter()
    Tc = merge_time(m1,m2,a,ecc, method="circ")
    toc = time.perf_counter()
    print(f"  Circular time:\t\t\t\t{toc-tic:.6f} s ({(toc-tic)/n:.6f} per eval)")
    # Check inverse circular merge time
    a_inv = inv_merge_time_circ(m1,m2,Tc)
    assert np.allclose(a,a_inv)
    # Peters low
    tic = time.perf_counter()
    Tlow = merge_time(m1,m2,a,ecc, method="Peters+1964L")
    toc = time.perf_counter()
    print(f"  Peter's (1964) low eccentricity time:\t\t{toc-tic:.6f} s ({(toc-tic)/n:.6f} per eval)")
    # Peters high
    tic = time.perf_counter()
    Thigh = merge_time(m1,m2,a,ecc, method="Peters+1964H")
    toc = time.perf_counter()
    print(f"  Peter's (1964) high eccentricity time:\t{toc-tic:.6f} s ({(toc-tic)/n:.6f} per eval)")
    # Peters enhancement factor
    tic = time.perf_counter()
    Tenh = merge_time(m1,m2,a,ecc, method="Peters+1964E")
    toc = time.perf_counter()
    print(f"  Peter's (1964) enh eccentricity time:\t\t{toc-tic:.6f} s ({(toc-tic)/n:.6f} per eval)")
    # Ilya's method
    tic = time.perf_counter()
    TIlya = merge_time(m1,m2,a,ecc, method="Mandel+2021")
    toc = time.perf_counter()
    print(f"  Ilya's method time:\t\t\t\t{toc-tic:.6f} s ({(toc-tic)/n:.6f} per eval)")
    # Integral
    tic = time.perf_counter()
    Tnum = merge_time(m1,m2,a,ecc, method="Integrate")
    toc = time.perf_counter()
    print(f"  Numerical integration time:\t\t\t{toc-tic:.6f} s ({(toc-tic)/n:.6f} per eval)")
    print("  pass!")
    plt.style.use('bmh')
    fig, axes = plt.subplots(
        nrows=1,ncols=2,
        figsize=(14,7),
    )
    # Plot wide range of values
    axes[0].plot(ecc,Tlow.to('Myr').value,label="Peters+1964 low")
    axes[0].plot(ecc,Thigh.to('Myr').value,label="Peters+1964 high",linestyle='--')
    axes[0].plot(ecc,Tenh.to('Myr').value,label="Peters+1964 enh")
    axes[0].plot(ecc,TIlya.to('Myr').value,label="Mandel+2021",linestyle='dotted')
    axes[0].plot(ecc,Tnum.to('Myr').value,label="Numerical Int")
    axes[0].plot(ecc,Tc.to('Myr').value,label="Circular")
    axes[0].set_ylim([0.,2*np.max(Tc.to('Myr').value)])
    axes[0].set_ylabel("Decay time (Myr)")
    axes[0].set_xlabel("Eccentricity")
    # Plot close to high eccentricity
    ecc_mask = (ecc > 0.9) & (ecc < 0.9999)
    axes[1].plot(
        ecc[ecc_mask],
        Tlow[ecc_mask].to('yr')/Tnum[ecc_mask].to('yr'),
    )
    axes[1].plot(
        ecc[ecc_mask],
        Thigh[ecc_mask].to('yr')/Tnum[ecc_mask].to('yr'),
    )
    axes[1].plot(
        ecc[ecc_mask],
        Tenh[ecc_mask].to('yr')/Tnum[ecc_mask].to('yr'),
    )
    axes[1].plot(
        ecc[ecc_mask],
        TIlya[ecc_mask].to('yr')/Tnum[ecc_mask].to('yr'),
    )
    axes[1].plot(
        ecc[ecc_mask],
        np.ones(np.sum(ecc_mask)),
    )
    axes[1].set_xlabel("Eccentricity")
    axes[1].set_ylabel("$T/T_{\mathrm{num}}$")
    axes[0].legend()
    plt.savefig("ecc_test.png")
    plt.close()

def ODE_test(n=100, nuse = 100):
    from basil_core.astro.orbit import circular_ODE_integration
    from basil_core.astro.orbit import eccentric_ODE_integration
    # We're not really going to do this many ODEs, but we can generate data
    n = (2*int(np.sqrt(n)//2))**2
    print("ODE test!")
    # Get data
    ecc = ecc_grid(n=n)
    m1 = np.ones(n) * 4 * u.solMass
    m2 = np.ones(n) * u.solMass
    a = np.ones(n) * u.solRad
    # Just one for now
    for index in [n//2]:
        # Identify sample
        _ecc = ecc[index]
        _m1 = m1[index]
        _m2 = m2[index]
        _a = a[index]
        # Do it verbose
        circular_ODE_integration(m1[index],m2[index],a[index],verbose=True)
        eccentric_ODE_integration(m1[index],m2[index],a[index],ecc[index],verbose=True)
    print("  pass!")

def decay_time_test(n=100):
    from matplotlib import pyplot as plt
    from basil_core.astro.orbit import peters_ecc_const
    from basil_core.astro.orbit import forb_of_m1_m2_a
    from basil_core.astro.orbit import decay_time
    from basil_core.astro.orbit import merge_time

    n = (2*int(np.sqrt(n)//2))**2
    print(f"decay time test ({n} evaluations)")
    # Get data
    e0 = ecc_grid(n=n)
    m1 = np.ones(n) * 4 * u.solMass
    m2 = np.ones(n) * u.solMass
    a0 = np.ones(n) * u.solRad
    ef = e0/2
    # Calculate c_0 once
    c0 = a0.to('m') * peters_ecc_const(e0)
    # Calculate af
    af = c0 / peters_ecc_const(ef)
    # Calculate forb_stop
    forb_stop = forb_of_m1_m2_a(m1,m2,af)
    ## Try methods ##
    # Case 1
    T1 = decay_time(m1,m2,a0)
    assert np.allclose(T1, merge_time(m1,m2,a0,e0,method="circ"))
    # Case 2
    T2 = decay_time(m1,m2,a0,e0=e0)
    assert np.allclose(T2, merge_time(m1,m2,a0,e0))
    # Case 3
    T3a = decay_time(m1,m2,a0,af=af)
    assert np.allclose(T3a,merge_time(m1,m2,a0,e0,method="circ")-merge_time(m1,m2,af,e0,method="circ"))
    # Positional argument with no units
    T3b = decay_time(m1.to('kg').value, m2.to('kg').value, a0.to('m').value, af.to('m').value)
    assert np.allclose(T3a.to('s').value, T3b)
    # Case 4
    T4 = decay_time(m1,m2,a0,forb_f=forb_stop)
    assert np.allclose(T3a.to('s').value, T4.to('s').value)
    # Case 5
    T5a = decay_time(m1,m2,a0,af=af,e0=e0)
    assert np.allclose(T5a,merge_time(m1,m2,a0,e0)-merge_time(m1,m2,af,ef))
    # Positional
    T5b = decay_time(m1.to('kg').value,m2.to('kg').value,a0.to('m').value,af.to('m').value,e0)
    assert np.allclose(T5a.to('s').value, T5b)
    # Case 6: Only m1, m2, a0, e0, ef given
    T6 = decay_time(m1,m2,a0,e0=e0,ef=ef)
    assert np.allclose(T6,T5a)
    # Case 7: Only m1, m2, a0, e0, forb_f given
    T7 = decay_time(m1,m2,a0,e0=e0,forb_f=forb_stop)
    assert np.allclose(T7,T5a,atol=0.,rtol=0.1)
    ## Case 8: Only m1, m2, a0, ef, af given
    #T8 = decay_time(m1,m2,a0,ef=ef,af=af)
    #assert np.allclose(T8,T5a,atol=0.,rtol=0.1)
    ## Case 9: Only m1, m2, a0, ef, forb_f given
    #T9 = decay_time(m1,m2,a0,ef=ef,forb_f=forb_stop)
    #assert np.allclose(T9,T5a,atol=0.,rtol=0.1)
    print("  pass!")

def orbit_evolve_test(n=100):
    from basil_core.astro.orbit import decay_time
    from basil_core.astro.orbit import MERGE_TIME_METHODS
    from scipy.integrate._ivp.ivp import METHODS as IVP_METHODS
    from basil_core.astro.orbit import orbital_separation_evolve
    print("Orbit evolve test")
    n = (2*int(np.sqrt(n)//2))**2
    # Get data
    e0 = ecc_grid(n=n)
    m1 = np.ones(n) * 4 * u.solMass
    m2 = np.ones(n) * u.solMass
    a0 = np.ones(n) * u.solRad
    # Identify evolve time
    evolve_time = decay_time(m1,m2,a0,e0=e0) /8
    # List of options we need
    options = [
        "fallback",
        "positional_circ",
        "positional_ecc",
        "return_ecc"
    ]
    # append options
    for opt in IVP_METHODS:
        options.append(opt)
    for opt in MERGE_TIME_METHODS:
        options.append(opt)

    # Just one for now
    for i, opt in enumerate(options):
        print(f"  option: {opt}")
        # Identify sample
        index = (n // 2) + i
        _ecc = e0[index]
        _m1 = m1[index]
        _m2 = m2[index]
        _a = a0[index]
        _t = evolve_time[index]
        # time 
        tic = time.perf_counter()
        # Identify extraneous
        if opt == "positional_circ":
            sep = orbital_separation_evolve(
                _m1.to('kg').value,
                _m2.to('kg').value,
                _a.to('m').value,
                _t.to('s').value,
            )
            assert not hasattr(sep, 'unit')
        elif opt == "positional_ecc":
            sep = orbital_separation_evolve(
                _m1.to('kg').value,
                _m2.to('kg').value,
                _a.to('m').value,
                _t.to('s').value,
                _ecc,
            )
            assert not hasattr(sep, 'unit')
        elif opt == "fallback":
            sep = orbital_separation_evolve(
                _m1,_m2,_a,_t,_ecc,
                fallback=True
            )
        elif opt == "return_ecc":
            sep, ecc = orbital_separation_evolve(
                _m1,_m2,_a,_t,_ecc,
                return_ecc=True,
            )
        elif opt in IVP_METHODS:
            sep = orbital_separation_evolve(_m1,_m2,_a,_t,_ecc,
                method=opt,
            )
        elif opt in MERGE_TIME_METHODS:
            sep = orbital_separation_evolve(_m1,_m2,_a,_t,_ecc,
                method=opt,
            )
        # Time
        toc = time.perf_counter()
        ## Check error
        # Check if evolution is circular or not
        if opt in ["positional_circ", "circular", "circ", "circle", "circ_numpy"]:
            _decay_time = decay_time(_m1,_m2,_a,af=sep)
        else:
            _decay_time = decay_time(_m1,_m2,_a,af=sep,e0=_ecc)
        # estimate error
        err = np.abs(_t - _decay_time).to('s')
        print(f"    {opt} time: {toc-tic:.6f} s")
        print(f"    {opt} err: {err.to('yr')}")
    # Case 0: No eccentricity was given in the first place
    print('  pass!')

def orbital_period_evolved_GW_test(n=100):
    print("Orbital period evolve test")
    P1 = cext_orbital_period_evolved_GW(n=n)
    P2 = numpy_orbital_period_evolved_GW(n=n)
    assert np.allclose(P1, P2)
    print("  pass!")

def DWD_r_of_m_test(n=100):
    print("WD radius test")
    a1 = cext_DWD_r_of_m(n=n)
    a2 = numpy_DWD_r_of_m(n=n)
    assert np.allclose(a1, a2)
    print("  pass!")

def DWD_RLOF_a_of_m1_m2_r1_r2_test(n=100):
    print("DWD Roche-lobe separation test")
    a1 = cext_DWD_RLOF_a_of_m1_m2_r1_r2(n=n)
    a2 = numpy_DWD_RLOF_a_of_m1_m2_r1_r2(n=n)
    assert np.allclose(a1, a2)
    print("  pass!")

def DWD_RLOF_P_of_m1_m2_r1_r2_test(n=100):
    print("DWD Roche-lobe period test")
    P1 = cext_DWD_RLOF_P_of_m1_m2_r1_r2(n=n)
    P2 = numpy_DWD_RLOF_P_of_m1_m2_r1_r2(n=n)
    assert np.allclose(P1, P2)
    print("  pass!")



######## All Tests ########

def all_test(**kwargs):
    beta_test(**kwargs)
    peters_ecc_const_test(**kwargs)
    peters_ecc_integrand_test(**kwargs)
    orbital_period_of_m1_m2_a_test(**kwargs)
    orbital_frequency_test(**kwargs)
    time_to_merge_of_m1_m2_a0_test(**kwargs)
    eccentricity_root_finder_test(**kwargs)
    time_of_orbital_shrinkage_test(**kwargs)
    orbital_separation_evolve_test(**kwargs)
    orbital_period_evolved_GW_test(**kwargs)
    DWD_r_of_m_test(**kwargs)
    DWD_RLOF_a_of_m1_m2_r1_r2_test(**kwargs)
    DWD_RLOF_P_of_m1_m2_r1_r2_test(**kwargs)

    # Slow tests
    ODE_test(**kwargs)
    merge_time_integral_test(**kwargs)
    merge_time_methods_test(**kwargs)
    decay_time_test(**kwargs)
    orbit_evolve_test(**kwargs)
######## Main ########
def main():
    n = int(2e3)
    all_test(n=n)
    return

######## Execution ########
if __name__ == "__main__":
    main()

