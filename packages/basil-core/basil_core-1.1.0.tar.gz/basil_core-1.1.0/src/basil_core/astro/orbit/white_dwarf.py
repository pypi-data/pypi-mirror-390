#!/usr/bin/env python3
"""Handle orbital integration specific to binaries containing a white dwarf

Follows 2507.21821 for orbital integration
"""
######## Imports ########
#### Standard Library ####
#### Third-Party ####
import numpy as np
from astropy import units as u
from astropy import constants as const
#### Homemade ####
#### Local ####

######## Setup #########

J2243 = {
    "name"      : "J2243",
    "fgw_0"     : 3.8 * u.mHz,
    "mc"        : 0.286 * u.solMass,
    "m1"        : 0.32 * u.solMass,
    "m2"        : 0.33 * u.solMass,
    "tauGW"     : 0.476 * u.Myr,
    "fgw_RL"    : 7.2 * u.mHz,
    "tauRL"     : 0.39 * u.Myr,
    "dist"      : 1.756 * u.kpc,
    "R_by_a"    : 0.244,
    "P_0"       : 527.93 * u.s,
    "tauTH"     : 18.6 * u.Myr,
    "taucool"   : 9351.34 * u.Myr,
    "R1_0"      : 0.0298 * u.solRad,
    "T1_0"      : 26.3 * u.kK,
    "k_by_Q"    : 8e-12,
    "Omega1_0"  : 0.1 * u.mHz,
}

######## Functions #########

def dfdt_GW(mc, f):
    """CHECKED WITH LUCY on 251106"""
    return (96 * np.power(const.G,5/3) * np.power(np.pi,8/3) /(5*np.power(const.c,5))) * np.power(mc.si,5/3) * np.power(f.si,11/3)

def dfdt_TH(k_by_Q, m1, m2, R1, fgw, Omega1):
    """CHECKED WITH LUCY on 251106"""
    return (18 * k_by_Q) * (m2 * np.pi**(13/3) * R1**5 * fgw**(13/3) * ((fgw/2) - Omega1)) / (const.G**(5/3) * m1 * (m1 + m2)**(5/3))

def dOmega1dt(k_by_Q, m1, m2, R1, fgw, Omega1, rg2 = 0.01):
    return (3*k_by_Q) * (np.pi**3 * m2**2 * fgw**3 * R1**3 * \
        ((fgw/2) - Omega1)) / \
        (const.G * m1 * rg2 * (m1 + m2)**2)


def Rcold_fn(m, Mch=1.44*u.solMass, Mp=5.7e-4*u.solMass):
    """Verbunt and Rappaport 1988"""
    if hasattr(m, 'unit'):
        m = m.to('solMass')
    else:
        raise ValueError("Within this implementation, R_of_T wants units")
    return 0.0114 * u.solRad *np.sqrt(
        (m/Mch)**(-2/3) - (m/Mch)**(2/3)
        ) * np.power(
        1 + 3.5*((m/Mp)**(-2/3)) + Mp/m, -2/3)

def R_of_T(m, teff, safety=True):
    """Verified with McNeil+2025"""
    if hasattr(m, 'unit'):
        m = m.to('solMass')
    else:
        raise ValueError("Within this implementation, R_of_T wants units")
    if hasattr(teff, 'unit'):
        teff = teff.to('K')
    else:
        raise ValueError("Within this implementation, R_of_T wants units")
    # Estimate cold radius
    Rcold = Rcold_fn(m)
    #print(f"Cold (degenerate) radius: {Rcold_fn(m)}")
    # Estimate the square root of the temperature
    sqrt_teff = np.sqrt(teff / (10_000 * u.K))
    #print(teff, sqrt_teff)
    # Estimate the mass value
    mval = m.value
    # Estimate the exponents
    exp1 = -0.177 * sqrt_teff
    exp2 = 0.148 - (0.941 * sqrt_teff)
    #print(f"Exponents: exp1: {exp1}; exp2: {exp2}")
    R_TH = 0.0132 * (10**exp1) * (mval**exp2)
    R_TH = R_TH.si
    R_TH = R_TH * u.solRad
    #print(f"R_TH: {R_TH}")
    # Set radii less than cold radii equal to cold radii
    if not safety:
        if np.size(R_TH) == 1:
            R_TH = Rcold
        else:
            R_TH[R_TH < Rcold] = Rcold
    # Catch exceptions
    if np.any(R_TH < Rcold):
        raise RuntimeError(
            f"Cold radius ({Rcold:.4f}) should not be " + \
            f"larger than hot radius ({R_TH:.4f})")
    else:
        return R_TH

def dRdT(m, teff):
    if hasattr(m, 'unit'):
        m = m.to('solMass')
    else:
        raise ValueError("Within this implementation, dRdT wants units")
    if hasattr(teff, 'unit'):
        teff = teff.to('kK')
    else:
        raise ValueError("Within this implementation, dRdT wants units")
    return R_of_T(m, teff) * \
        (0.941 * np.log(10*m.value) + 0.177 * np.log(10)) / \
        (-2 * np.sqrt(teff/(10 * u.kK)) * u.kK) 
    
def dTdt_TH(k_by_Q, m1, m2, R1, fgw, Omega1, T1):
    """Estimate the time derivative of temperature for a tidal DWD primary"""
    value = (135*np.pi**(25/3) * R1**9 * m2**3 * fgw**(19/3)) / \
        (const.G**(8/3) * m1 * (m1+m2)**(11/3))
    value = value * k_by_Q**2
    value = value * (fgw/2 - 0.6*Omega1) * (fgw/2 - Omega1)**2
    value = value / (const.sigma_sb * T1**3 * (2*R1 + dRdT(m1,T1)*T1))
    return value.si

def print_derivatives(obs):
    """Print the derivatives of a given object at the time of observation"""
    _R_of_T = R_of_T(obs["m1"], obs["T1_0"])
    print(f"{obs['name']} R(T)_(t=0): {_R_of_T:.4e}; R_0: {obs['R1_0']:.4e}")
    _dfdt_GW = dfdt_GW(obs["mc"], obs["fgw_0"]).si
    print(f"{obs['name']} (df/dt)_(GW,t=0): {_dfdt_GW:.4e}")
    _dfdt_TH = dfdt_TH(obs["k_by_Q"], obs["m1"], obs["m2"], _R_of_T, obs["fgw_0"], obs["Omega1_0"]).si
    print(f"{obs['name']} (df/dt)_(TH,t=0): {_dfdt_TH:.4e}")
    _dOmega1dt = dOmega1dt(obs["k_by_Q"], obs["m1"], obs["m2"], _R_of_T, obs["fgw_0"], obs["Omega1_0"]).si
    print(f"{obs['name']} (dOmega1/dt)_(TH,t=0): {_dOmega1dt:.4e}")
    _dRdT = dRdT(obs["m1"], obs["T1_0"])
    print(f"{obs['name']} dRdT_(t=0): {_dRdT:.4e}") 
    _dTdt_TH = dTdt_TH(obs["k_by_Q"], obs["m1"], obs["m2"], _R_of_T, obs["fgw_0"], obs["Omega1_0"], obs["T1_0"])
    print(f"{obs['name']} dTdt_(TH,t=0): {_dTdt_TH:.4e}")


######## Main ########
def main():
    print_derivatives(J2243)
    return

######## Execution #########
if __name__ == "__main__":
    main()
