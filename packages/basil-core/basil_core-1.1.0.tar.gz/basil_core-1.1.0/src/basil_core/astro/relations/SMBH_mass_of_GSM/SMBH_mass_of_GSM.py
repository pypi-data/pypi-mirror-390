#!/usr/bin/env python3
'''SuperMassive Black Hole mass of Galactic Stellar Mass

Use the power law to find SMBH mass of GSM

Authors
-------
    Vera Delfavero
    xevra86@gmail.com - vera.delfavero@ligo.org - vera.delfavero@nasa.gov
'''

def SchrammSilvermanSMBH_mass_of_GSM(mstar):
    '''SMBH mass of Galctic Stellar Mass

    Return the SMBH mass for a galaxy with mstar Stellar mass

    Citation
    --------
        https://iopscience.iop.org/article/10.1088/0004-637X/767/1/13/pdf

    Notes
    -----
        Power law given: 1.12
        Source: log10M_BH = 8.55; log10M_* = 11.34

    Parameters
    ----------
    mass: array_like
        Galaxy stellar mass
    
    Returns
    -------
    SMBH_mass: array_like
        SMBH mass
    '''
    return 7.066429e-05 * mstar**1.12

def GSM_of_SchrammSilvermanSMBH_mass(smbh_mass):
    '''Galctic Stellar Mass of SMBH mass

    Return the mstar Stellar mass for a galaxy with given SMBH mass

    Citation
    --------
        https://iopscience.iop.org/article/10.1088/0004-637X/767/1/13/pdf

    Notes
    -----
        Power law given: 1.12
        Source: log10M_BH = 8.55; log10M_* = 11.34

    Parameters
    ----------
    smbh_mass: array_like
        SMBH mass
    
    Returns
    -------
    stellar_mass: array_like
        Galaxy stellar mass
    '''
    return (smbh_mass / 7.066429e-05) **(1/1.12)
