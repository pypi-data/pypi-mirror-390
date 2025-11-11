#!/usr/bin/env python3
'''Test basil_core.astro.relations

Authors
-------
    Vera Delfavero
    xevra86@gmail.com - vera.delfavero@ligo.org - vera.delfavero@nasa.gov
'''

######## Imports #########
import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
import numpy as np
from os.path import join
from scipy.interpolate import CubicSpline
from astropy import units as u
import warnings

######## Globals ########
PLOTDIR = "./data"
FNAME_BLUE = "./archive/Peng2015/stellarMZR-SF.TXT"
FNAME_RED = "./archive/Peng2015/stellarMZR-passive.txt"
SEED = 42
RS = np.random.RandomState(SEED)

MSTAR_MIN = 0.08 * u.solMass
MSTAR_MAX = 150.0 * u.solMass
MGAL_MIN = 1e7 * u.solMass
MGAL_MAX = 3e11 * u.solMass

IMF_alpha=2.35
'''Kroupa adjustment for IMF'''

ZBINS = [0.0001, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006, 0.0007, 0.0008,
    0.0009, 0.001, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045,
    0.005, 0.0055, 0.006, 0.0065, 0.007, 0.0075, 0.008, 0.0085, 0.009,
    0.0095, 0.01, 0.015, 0.02, 0.025, 0.03,]
'''Metallicity bins used by StarTrack in Delfavero et al. 2023'''

######## test IMF ########

def test_IMF(n_mass=50):
    '''test the IMF function'''
    from basil_core.astro.relations import Salpeter_IMF
    # Get mstar array
    mstar_arr = np.exp(np.linspace(np.log(MSTAR_MIN.value), np.log(MSTAR_MAX.value), n_mass)) * MSTAR_MIN.unit
    # Get IMF
    IMF = Salpeter_IMF(mstar_arr)
    # Plot
    fig, ax = plt.subplots()
    ax.loglog(mstar_arr, IMF)
    ax.set_xlabel(r"m [$\mathrm{M}_{\odot}$]")
    ax.set_ylabel(r"IMF")
    plt.savefig(join(PLOTDIR, "test_IMF.png"))
    plt.close()

######## Test AGND ########

def test_AGND(n_redshift=50):
    '''Test the AGN Density'''
    from basil_core.astro.relations.AGND.AGND import Ueda_AGND_gp
    from basil_core.astro.relations import Ueda_AGND
    from astropy.cosmology import Planck15 as cosmo
    from astropy.cosmology import z_at_value
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
    # Estimate AGND
    phi_gp, z_train, phi_train, sig_phi_train = Ueda_AGND_gp(z_arr, return_train=True)
    phi_fit = Ueda_AGND(z_arr, logLx=46., dlogLx=2, max_redshift=5)
    # Plot
    fig, ax = plt.subplots()
    ax.plot(z_arr, np.log10(phi_gp.value), label="Ueda gp")
    #ax.scatter(z_train, phi_train, label="Training data")
    ax.errorbar(z_train, phi_train, yerr=sig_phi_train,fmt='o',label="training data")
    ax.plot(z_arr, np.log10(phi_fit.value), label="Ueda best fit")
    ax.errorbar
    ax.set_xlim(0.0,5)
    ax.set_ylim(-9,-3)
    ax.set_xlabel("Redshift")
    ax.set_ylabel(r"AGND $[\mathrm{Mpc}^{-3}]$")
    ax.legend()
    plt.savefig(join(PLOTDIR, "test_AGND.png"))
    plt.close()
    return


def test_SFRD(n_redshift=50):
    '''Test the SFRD'''
    from basil_core.astro.relations import Madau_Fragos_SFRD
    from basil_core.astro.relations import Madau_Dickinson_SFRD
    from basil_core.astro.relations import Strogler_SFRD
    from basil_core.astro.relations import Neijssel_SFRD
    from astropy.cosmology import Planck15 as cosmo
    from astropy.cosmology import z_at_value
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
    # estimate sfrd
    sfr1 = Madau_Fragos_SFRD(z_arr)
    sfr2 = Madau_Dickinson_SFRD(z_arr)
    sfr3 = Strogler_SFRD(z_arr)
    sfr4 = Neijssel_SFRD(z_arr)
    # Plot
    fig, ax = plt.subplots()
    ax.loglog(z_arr, sfr1, label="Madau Fragos")
    ax.loglog(z_arr, sfr2, label="Madau Dickinson")
    ax.loglog(z_arr, sfr3, label="Strogler")
    ax.loglog(z_arr, sfr4, label="Neijssel")
    ax.set_xlabel("Redshift")
    ax.set_ylabel(r"SFRD $[\mathrm{M}_{\odot}/\mathrm{Mpc}^3/yr]$")
    ax.legend()
    plt.savefig(join(PLOTDIR, "test_SFRD.png"))
    plt.close()
    return

######## Test MZR ########

def test_MZR(n_redshift=50):
    '''Test the MZR'''
    from basil_core.astro.relations import Madau_Fragos_MZR
    from basil_core.astro.relations import Ma2015_MZR
    from basil_core.astro.relations import Nakajima2023_MZR
    from astropy.cosmology import Planck15 as cosmo
    from astropy.cosmology import z_at_value
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
    # Plot
    fig, ax = plt.subplots()
    ax.loglog(z_arr, Madau_Fragos_MZR(z_arr, 1e9), label="Madau & Fragos (2017)")
    ax.loglog(z_arr, Ma2015_MZR(z_arr, 1e7), label=r"$1e7 M_{\odot}$;Ma (2015)")
    ax.loglog(z_arr, Ma2015_MZR(z_arr, 1e9), label=r"$1e9 M_{\odot}$;Ma (2015)")
    ax.loglog(z_arr, Ma2015_MZR(z_arr, 1e11), label=r"$1e11 M_{\odot}$;Ma (2015)")
    ax.loglog(z_arr, Nakajima2023_MZR(z_arr, 1e7), label=r"$1e7 M_{\odot}$;Nakajima (2023)")
    ax.loglog(z_arr, Nakajima2023_MZR(z_arr, 1e9), label=r"$1e9 M_{\odot}$;Nakajima (2023)")
    ax.loglog(z_arr, Nakajima2023_MZR(z_arr, 1e11), label=r"$1e11 M_{\odot}$;Nakajima (2023)")
    ax.set_xlabel("Redshift")
    ax.set_ylabel("Metallicity")
    ax.legend()
    plt.savefig(join(PLOTDIR, "test_MZR.png"))
    plt.close()
    return

def test_MZR_utils(redshift=1., nsample=int(1e4)):
    '''Test the MZR utils, such as sampling'''
    from basil_core.astro.relations import Madau_Fragos_MZR
    from basil_core.astro.relations.MZR.utils import metallicity_samples
    gsm=1.e10
    Zsample = metallicity_samples(Madau_Fragos_MZR, redshift, gsm, nsample, seed=RS)

######## Test GSMF ########

def test_GSMF(n_redshift=137, n_mass=50):
    '''Test the GSMF function'''
    from basil_core.astro.relations import Fontana_GSMF
    from basil_core.astro.relations import Cole_GSMF
    from basil_core.astro.relations import Navarro_GSMF
    from basil_core.astro.relations import Weibel_GSMF
    from basil_core.astro.relations import Furlong2015_GSMF
    from astropy.cosmology import Planck15 as cosmo
    from astropy.cosmology import z_at_value
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
    # Initialize gsmf array 
    gsmf_arr = np.zeros((n_redshift, n_mass))
    # Loop the redshifts
    for _i, _z in enumerate(z_arr):
        gsmf_arr[_i] = Fontana_GSMF(mstar_arr, _z, gsm_min=MGAL_MIN, gsm_max=MGAL_MAX)

    # Make assertions
    mask = gsmf_arr >= 0
    assert mask.all()

    ## Plot ##
    plt.style.use('bmh')
    fig, ax = plt.subplots()
    ax.imshow(
              gsmf_arr,
              extent=(np.log10(z_arr[0]+1),np.log10(z_arr[-1]+1),np.log10(mstar_arr[0].value),np.log10(mstar_arr[-1].value)),
              origin="lower",
              aspect='auto',
             )
               
    ax.set_xlim(np.log10(z_arr[0]+1), np.log10(z_arr[-1]+1))
    ax.set_ylim(np.log10(mstar_arr[0].value), np.log10(mstar_arr[-1].value))
    ax.set_xlabel("log10(Redshift+1)")
    ax.set_ylabel(r"Galactic Stellar Mass $log_{10}[M_{\odot}]$")
    plt.savefig(join(PLOTDIR, "test_gsmf.png"))
    plt.close()

    ## More plots ##
    for redshift in [0., 1., 2., 4., 6., 8.]:
        fname_out = join(PLOTDIR, "test_gsmf_z_%0.1f.png"%(redshift))
        fig, ax = plt.subplots()
        ax.plot(
                np.log10(mstar_arr.to('solMass').value),
                np.log10(Cole_GSMF(mstar_arr, redshift, gsm_min=MGAL_MIN,gsm_max=MGAL_MAX)),
                label="Cole (2001)",
               )
        ax.plot(
                np.log10(mstar_arr.to('solMass').value),
                np.log10(Fontana_GSMF(mstar_arr, redshift, gsm_min=MGAL_MIN,gsm_max=MGAL_MAX)),
                label="Fontana (2006)",
               )
        ax.plot(
                np.log10(mstar_arr.to('solMass').value),
                np.log10(Navarro_GSMF(mstar_arr, redshift, gsm_min=MGAL_MIN,gsm_max=MGAL_MAX)),
                label="Navarro-Carrera (2023)",
               )
        ax.plot(
                np.log10(mstar_arr.to('solMass').value),
                np.log10(Weibel_GSMF(mstar_arr, redshift, gsm_min=MGAL_MIN,gsm_max=MGAL_MAX)),
                label="Weibel (2023)",
               )
        ax.plot(
                np.log10(mstar_arr.to('solMass').value),
                np.log10(Furlong2015_GSMF(mstar_arr, redshift, gsm_min=MGAL_MIN,gsm_max=MGAL_MAX)),
                label="Furlong et al. (2015)",
               )
        ax.legend(loc='best')
        ax.set_title("GSMF (z = %0.1f)"%(redshift))
        ax.set_ylabel(r"$\mathrm{log}_{10}(\mathrm{PDF})$")
        ax.set_ylim([-8,2])
        ax.set_xlabel(r"$\mathrm{log}_{10}(\mathrm{Galactic Stellar Mass} [\mathrm{M}_{\odot}])$")
        plt.savefig(fname_out)
        plt.close()
    # z = 0.
    # z = 1.
    # z = 4.
    return

def test_GSMF_utils(
                    redshift=1.,
                    n_mass=2000,
                    confidence_value=0.68,
                    mgal_min_local=1e9*u.solMass,
                    mgal_max_local=1e11*u.solMass,
                    norm_bins=int(1e6),
                   ): 
    '''Test the GSMF utilities'''
    from basil_core.astro.relations import Fontana_GSMF
    from basil_core.astro.relations.GSMF.utils import GSMF_cdf
    from basil_core.astro.relations.GSMF.utils import GSMF_mean
    from basil_core.astro.relations.GSMF.utils import GSMF_confidence
    from basil_core.astro.relations.GSMF.utils import GSMF_normalization
    from basil_core.astro.relations.GSMF.utils import GSMF_samples
    from astropy.cosmology import Planck15 as cosmo
    from astropy.cosmology import z_at_value
    # Get cdf
    cdf = GSMF_cdf(Fontana_GSMF, redshift, MGAL_MIN, MGAL_MAX, mbins=n_mass)
    # Get mean
    mu = GSMF_mean(Fontana_GSMF, redshift, MGAL_MIN, MGAL_MAX, mbins=n_mass)
    # Get confidence
    confidence = GSMF_confidence(Fontana_GSMF, redshift, MGAL_MIN, MGAL_MAX, mbins=n_mass, confidence_value=confidence_value)
    # Get normalization
    norm = GSMF_normalization(Fontana_GSMF, redshift, mgal_min_local, mgal_max_local, MGAL_MIN, MGAL_MAX, nbins=norm_bins)
    # Get samples
    samples = GSMF_samples(Fontana_GSMF, redshift, MGAL_MIN, MGAL_MAX, norm_bins, mbins=norm_bins, seed=RS) 
    sample_index = (samples >= mgal_min_local) & (samples <= mgal_max_local)
    sample_norm = np.sum(sample_index) / norm_bins
    sample_norm_weighted = np.sum(samples[sample_index]) / np.sum(samples)
    fractional_error = (sample_norm_weighted - norm)/ norm
    assert fractional_error  <= 0.01

######## Test NSC ########

def test_NSCtype(ngal=3000):
    '''Re-plot plot data'''
    from basil_core.astro.relations import Peng_early_frac_estimator
    from basil_core.astro.relations.early_frac_of_GSM_metallicity.early_frac import Peng2015_STAR_FORMING as BLUE
    from basil_core.astro.relations.early_frac_of_GSM_metallicity.early_frac import Peng2015_PASSIVE as RED
    ## Red and Blue data ##
    met_lims = np.asarray([min(np.min(RED[:,1]), np.min(BLUE[:,1])), max(np.max(RED[:,1]), np.max(BLUE[:,1]))])
    # Get mass space for testing
    m_arr = np.linspace(np.min(BLUE[:,0]), np.max(RED[:,0]), ngal)
    # Get metallicity space
    met_arr = ((met_lims[1] - met_lims[0])*RS.uniform(size=ngal)) + met_lims[0]

    ## Get early frac estimator ##
    early_frac_estimator, gp_blue, gp_red = Peng_early_frac_estimator(return_gp=True)

    # Get early frac
    early_frac = early_frac_estimator(m_arr, met_arr)

    # get samples
    blue_index = early_frac <= 0.5
    red_index = early_frac > 0.5
     
    # Plot
    fig, ax = plt.subplots()
    ax.scatter(BLUE[:,0], BLUE[:,1], c='blue',s=6,edgecolor='k',linewidths=0.3,label='star-forming data')
    ax.scatter(RED[:,0], RED[:,1], c='red',s=6,edgecolor='k',linewidths=0.3,label='passive data')
    ax.errorbar(BLUE[:,0], BLUE[:,1], yerr=BLUE[:,2], fmt='none',elinewidth=1,ecolor='blue')#s=13,edgecolor='k',linewidths=0.3)
    ax.errorbar(RED[:,0], RED[:,1],yerr=RED[:,2], fmt='none',elinewidth=1,ecolor='red')#s=13,edgecolor='k',linewidths=0.3)
    ax.scatter(m_arr[blue_index], met_arr[blue_index], color='cornflowerblue',s=6,label="star-forming samples")
    ax.scatter(m_arr[red_index], met_arr[red_index], color='palevioletred',s=6,label="passive samples")
    ax.set_xlabel("log10(GSM) $[M_{\odot}]$")
    ax.set_ylabel("log10(met)")
    ax.legend()
    #plt.show()
    plt.savefig(join(PLOTDIR, "test_NSCtype"))
    plt.close()


def test_NSCfrac(n_mass=100):
    '''Re-plot plot data'''
    from basil_core.astro.relations.NSC_frac_of_GSM.NSC_frac_of_GSM import Neumayer_NSC_frac_of_GSM
    from basil_core.astro.relations.NSC_frac_of_GSM.NSC_frac_of_GSM import NEUMAYER_NSC_EARLY_LOGM
    from basil_core.astro.relations.NSC_frac_of_GSM.NSC_frac_of_GSM import NEUMAYER_NSC_EARLY_FRAC
    from basil_core.astro.relations.NSC_frac_of_GSM.NSC_frac_of_GSM import NEUMAYER_NSC_LATE_LOGM
    from basil_core.astro.relations.NSC_frac_of_GSM.NSC_frac_of_GSM import NEUMAYER_NSC_LATE_FRAC
    # Get mass space for testing
    gsm_arr = np.exp(np.linspace(np.log(MGAL_MIN.value),np.log(MGAL_MAX.value), n_mass)) * MGAL_MIN.unit

    ## Get early and late NSC fractions ##
    early_NSC_frac, late_NSC_frac = Neumayer_NSC_frac_of_GSM(gsm_arr)
     
    # Plot
    fig, ax = plt.subplots()
    ax.plot(np.log10(gsm_arr.value), early_NSC_frac, color='red',label='early-interp', zorder=1)
    ax.plot(np.log10(gsm_arr.value), late_NSC_frac, color='blue',label='late-interp', zorder=1)
    ax.scatter(NEUMAYER_NSC_EARLY_LOGM, NEUMAYER_NSC_EARLY_FRAC, c='red', s=24, edgecolor='k', linewidths=0.5, label='early-paper', zorder=2)
    ax.scatter(NEUMAYER_NSC_LATE_LOGM, NEUMAYER_NSC_LATE_FRAC, c='blue', s=24, edgecolor='k', linewidths=0.5, label='late-paper', zorder=2)
    ax.set_xlabel("log10(GSM) $[M_{\odot}]$")
    ax.set_ylabel("probability of NSC")
    ax.legend()
    plt.savefig(join(PLOTDIR, "test_NSCfrac"))
    plt.close()

def test_NSCmass(n_mass=100):
    '''Re-plot plot data'''
    from basil_core.astro.relations import Neumayer_early_NSC_mass, Neumayer_late_NSC_mass
    # Get mass space for testing
    gsm_arr = np.exp(np.linspace(np.log(MGAL_MIN.value),np.log(MGAL_MAX.value), n_mass)) * MGAL_MIN.unit
    # Get NSC mass
    nsc_mass_early = Neumayer_early_NSC_mass(gsm_arr)
    nsc_mass_late = Neumayer_late_NSC_mass(gsm_arr)

    # Plot
    fig, ax = plt.subplots()
    ax.scatter(np.log10(gsm_arr.value), np.log10(nsc_mass_early.value), label='early')
    ax.scatter(np.log10(gsm_arr.value), np.log10(nsc_mass_late.value), label='late')
    ax.set_xlabel("$log10(GSM) [M_{\odot}]$")
    ax.set_ylabel("$log10(M_{\mathrm{NSC}}) [M_{\odot}]$")
    ax.legend()
    plt.savefig(join(PLOTDIR, "test_NSCmass"))
    plt.close()

def test_SMBHmass(n_mass=100):
    '''Re-plot plot data'''
    from basil_core.astro.relations import SchrammSilvermanSMBH_mass_of_GSM as SMBH_mass_of_GSM
    # Get mass space for testing
    gsm_arr = np.exp(np.linspace(np.log(MGAL_MIN.value),np.log(MGAL_MAX.value), n_mass)) * MGAL_MIN.unit
    # Get NSC mass
    smbh_mass = SMBH_mass_of_GSM(gsm_arr)

    # Plot
    fig, ax = plt.subplots()
    ax.scatter(np.log10(gsm_arr.value), np.log10(smbh_mass.value))
    ax.set_xlabel("$log10(GSM) [M_{\odot}]$")
    ax.set_ylabel("$log10(M_{\mathrm{SMBH}}) [M_{\odot}]$")
    ax.legend()
    plt.savefig(join(PLOTDIR, "test_SMBHmass"))
    plt.close()


######## Main ########
def main():
    test_IMF()
    test_AGND()
    test_SFRD()
    test_MZR()
    test_MZR_utils()
    test_GSMF()
    test_GSMF_utils()
    test_SMBHmass()
    #test_NSCtype()
    test_NSCfrac()
    test_NSCmass()
    return

######## Execution ########
if __name__ == "__main__":
    main()

