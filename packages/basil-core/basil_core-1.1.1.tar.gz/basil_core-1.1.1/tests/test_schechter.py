#!/usr/env/bin python3
'''Test Schechter implementation in basil-core'''

######## Imports #########
import numpy as np
from astropy import units as u
import time
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from os.path import join
from scipy.interpolate import CubicSpline
import warnings

######## Setup ########
SEED = 42
rs = np.random.RandomState(SEED)

# Galaxy things
MGAL_MIN = 1e7 * u.solMass
MGAL_MAX = 1e12 * u.solMass

# Metallicity bins
ZBINS = [0.0001, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008,
    0.0009, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045,
    0.005, 0.0055, 0.006, 0.0065, 0.007, 0.0075, 0.008, 0.0085, 0.009,
    0.0095, 0.01, 0.015, 0.02, 0.025, 0.03,]
'''Metallicity bins used by StarTrack in Delfavero et al. 2023'''

#### Schechter function parameters ####
# Local universe schechter function
COLE_M0 = 11.16
COLE_alpha0 = -1.18
COLE_phi0 = 0.0035

# Fontana fit
FONTANA_M1 = 0.17
FONTANA_M2 = -0.07
FONTANA_alpha1 = -0.082
FONTANA_phi1 = -2.20

######## Functions ########

def unique_monatonic_increasing(n, inc=3):
    arr = np.arange(n*inc,step=inc)
    return arr

def sample_array(arr, n):
    ind = rs.randint(0, high=arr.size, size=n)
    return arr[ind]

def sample_data(n_mono=int(1e4), n_samples=int(1e3), inc=3):
    arr = unique_monatonic_increasing(n_mono, inc=inc)
    samples = sample_array(arr, n_samples)
    return arr, samples
    
######## Numpy functions ########
def schechter_numpy(
                    gsm,
                    redshift,
                    phi0=COLE_phi0,
                    phi1=0.,
                    alpha0=COLE_alpha0,
                    alpha1=0.,
                    Mcarrot0=COLE_M0,
                    Mcarrot1=0.,
                    Mcarrot2=0.,
                    gsm_min=1e7*u.solMass,
                    gsm_max=1e12*u.solMass,
                   ):
    '''The Schechter function following Fontana et al (2006)

    Citation
    --------
        https://www.aanda.org/articles/aa/pdf/2006/45/aa5475-06.pdf

    Parameters
    ----------
        gsm
    '''
    # Check astropy units
    gsm_min = gsm_min.to('solMass').value
    gsm_max = gsm_max.to('solMass').value
    gsm     = gsm.to('solMass').value
    # Initialize output array
    psi     = np.zeros_like(gsm)
    # phi_z
    phi_scale = phi0 * (1 + redshift)**(phi1)
    # alpha_z
    alpha_z = 1. + alpha0 + (alpha1 * redshift)
    # mcal
    gsm_scale = Mcarrot0 + (Mcarrot1 * redshift) + (Mcarrot2 * redshift**2)
    gsm_mask = (gsm >= gsm_min) & (gsm <= gsm_max)
    gsm_factor = gsm * 10**(-gsm_scale)
    # find answer
    psi[gsm_mask] = phi_scale * np.log(10) * gsm_factor**(alpha_z) * np.exp(-gsm_factor)
    return psi

def fontana_schechter_numpy(gsm, redshift, **kwargs):
    return schechter_numpy(
                           gsm,
                           redshift,
                           phi1=FONTANA_phi1,
                           alpha1=FONTANA_alpha1,
                           Mcarrot1=FONTANA_M1,
                           Mcarrot2=FONTANA_M2,
                           **kwargs
                          )

######## Test GSMF ########

def test_GSMF(n_redshift=1370, n_mass=1000):
    '''Test the GSMF function'''
    from astropy.cosmology import Planck15 as cosmo
    from astropy.cosmology import z_at_value
    from basil_core.stats import schechter
    print("Testing GSMF:")
    # Get hubble time
    hubble_time = cosmo.lookback_time(9001)
    # Get t_arr
    t_arr = np.linspace(0, hubble_time, n_redshift+1)
    # Get reduced t_arr
    t_arr = 0.5*(t_arr[:-1] + t_arr[1:])
    # get redshifts
    z_arr = np.zeros(t_arr.shape)
    # Get redshift values
    for _i, _t in enumerate(t_arr):
        z_arr[_i] = z_at_value(cosmo.lookback_time, _t)
    # Get mstar array
    mstar_arr = np.exp(np.linspace(np.log(MGAL_MIN.value),np.log(MGAL_MAX.value), n_mass)) * MGAL_MIN.unit

    ## GSMF ##
    t0 = time.time()
    # Initialize gsmf array 
    gsmf_numpy = np.zeros((n_redshift, n_mass))
    # Loop the redshifts
    for _i, _z in enumerate(z_arr):
        # Estimate GSMF
        gsmf_numpy[_i] = fontana_schechter_numpy(mstar_arr, _z, gsm_min=MGAL_MIN, gsm_max=MGAL_MAX)
    t1 = time.time()
    print("  NumPy time: %f seconds!"%(t1-t0)) 

    ## C Extension ##

    t0 = time.time()
    # Initialize gsmf array 
    gsmf_cext = np.zeros((n_redshift, n_mass))
    # Loop the redshifts
    for _i, _z in enumerate(z_arr):
        # Estimate GSMF
        gsmf_cext[_i] = schechter(
                                  mstar_arr, _z,
                                  phi0=COLE_phi0,
                                  phi1=FONTANA_phi1,
                                  alpha0=COLE_alpha0,
                                  alpha1=FONTANA_alpha1,
                                  M0=COLE_M0,
                                  M1=FONTANA_M1,
                                  M2=FONTANA_M2,
                                  gsm_min=MGAL_MIN.to('solMass').value,
                                  gsm_max=MGAL_MAX.to('solMass').value
                                 )
    t1 = time.time()
    print("  C Extension time: %f seconds!"%(t1-t0)) 
    assert np.allclose(gsmf_numpy, gsmf_cext)

    #### Serial test ####
    # Set up inputs
    mstar_serial = np.tile(mstar_arr, n_redshift)
    redshift_serial = np.repeat(z_arr, n_mass)

    ## Numpy ##
    t0 = time.time()
    gsmf_numpy = fontana_schechter_numpy(mstar_serial, redshift_serial, gsm_min=MGAL_MIN, gsm_max=MGAL_MAX)
    t1 = time.time()
    print("  NumPy serial time: %f seconds!"%(t1-t0))

    t0 = time.time()
    ## C Extension ##
    gsmf_cext = schechter(
                          mstar_serial, redshift_serial,
                          phi0=COLE_phi0,
                          phi1=FONTANA_phi1,
                          alpha0=COLE_alpha0,
                          alpha1=FONTANA_alpha1,
                          M0=COLE_M0,
                          M1=FONTANA_M1,
                          M2=FONTANA_M2,
                          gsm_min=MGAL_MIN.to('solMass').value,
                          gsm_max=MGAL_MAX.to('solMass').value
                         )
    t1 = time.time()
    print("  C Extension serial time: %f seconds!"%(t1-t0)) 
    assert np.allclose(gsmf_numpy, gsmf_cext)
    print("  pass!")

######## Main ########
def main():
    test_GSMF()
    return

######## Execution ########
if __name__ == "__main__":
    main()


