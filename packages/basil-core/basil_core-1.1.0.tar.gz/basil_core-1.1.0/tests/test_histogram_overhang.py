#!/usr/env/bin python3

######## Setup ########
import numpy as np
import time

from basil_core.stats.density.density_utils import prune_samples
from basil_core.stats.density.density_utils import multigauss_samples
from basil_core.stats.density.histogram_overhang import weighted_histogram_density_error
from basil_core.stats.density.histogram_overhang import bin_combination_seeds
from basil_core.stats.density.histogram_overhang import histogram_overhang_edge_factor
from basil_core.stats.density.histogram_overhang import histogram_overhang_bins_of_ndim
from basil_core.stats.density.histogram_overhang import HOGPEN
from basil_core.stats.distance import bhattacharyya_distance
from basil_core.stats.distance import hellinger_distance
from basil_core.stats.distance import rel_entr
from basil_core.plots.corner import Corner

######## GLOBALS ########
SEED = np.random.RandomState(42)

######## Functions ########

def generate_samples(nsample=1000, ngauss=2, ndim=3):
    samples = multigauss_samples(ndim, ngauss, nsample, seed=SEED)
    return samples

def gp_api_compact(x_train, y_train, y_train_err):
    from gp_api.utils import fit_compact_nd
    gp_fit = fit_compact_nd(x_train, y_train, whitenoise=0.01,order=1,train_err=y_train_err)
    gp_lambda = lambda x: gp_fit.mean(x)
    return gp_lambda

######## Tests ########

def prune_samples_test(nsample=1000, ngauss=2, ndim=3):
    print("Prune samples test:")
    print("  nsample = %d; ngauss = %d, ndim = %d"%(nsample, ngauss, ndim))
    samples = generate_samples(nsample, ngauss, ndim)
    print("  samples: %s"%(samples.shape[0]))
    print("  mean = ",np.mean(samples,axis=0))
    print("  std = ",np.std(samples,axis=0))
    print("  min = ",np.min(samples, axis=0))
    print("  max = ",np.max(samples, axis=0))
    print("  pruning...")
    # Generate limits
    limits = np.zeros((ndim, 2))
    limits[:,1] = 1.0
    samples = samples[prune_samples(samples, limits)]
    print("  samples: %s"%(samples.shape[0]))
    print("  mean = ",np.mean(samples,axis=0))
    print("  std = ",np.std(samples,axis=0))
    print("  min = ",np.min(samples, axis=0))
    print("  max = ",np.max(samples, axis=0))
    print("  Done!")

def HOGPEN_test_3d(nsample=1000, ngauss=2, min_bins = 7, max_bins=10, **kwargs):
    ndim=3
    print("HOGPEN test:")
    print("  nsample = %d; ngauss = %d, ndim = %d"%(nsample, ngauss, ndim))
    # Generate some samples
    samples = generate_samples(nsample, ngauss, ndim)
    print("  samples generated!")
    # Create some limits
    limits = np.zeros((ndim, 2))
    limits[:,1] = 1.0
    # Initialize object
    hogpen_example = HOGPEN(samples, limits, verbose=True)
    print("  hogpen object initialized!")
    # Get a 1D histogram
    print("  1d histogram test:")
    x_train, y_train, y_train_err = hogpen_example.fit_hist1d(min_bins,0,True)
    print("  success!")
    # Get a 2D histogram
    print("  2d histogram test:")
    x_train, y_train, y_train_err = hogpen_example.fit_hist2d(min_bins,1,2,True)
    print("  success!")
    # Get a 3D histogram
    print("  dd histogram test:")
    x_train, y_train, y_train_err = hogpen_example.fit_histdd([0,1,2],min_bins,grab_edge=True)
    print("  success!")
    # Fit a 3D marginal
    print("  fitting a 3D marginal:")
    err, bins, gp_fit, x_train, y_train, y_train_err = \
        hogpen_example.fit_marginal(
                                    gp_api_compact,
                                    min_bins=min_bins,
                                    max_bins=max_bins,
                                    grab_edge=True,
                                   )
    print("  minimum err: %f; bins:"%(err), bins)
    print("  pass!")
    # Do a search by like bins
    print("  fitting a 2D marginal with like method:")
    err, bins, gp_fit, x_train, y_train, y_train_err = \
        hogpen_example.fit_marginal_methods(
                                            gp_api_compact,
                                            np.asarray([0,1]),
                                            method="like",
                                            grab_edge=True,
                                            min_bins=min_bins,
                                            max_bins=max_bins,
                                           )
    print("  minimum err: %f; bins:"%(err), bins)
    print("  pass!")
    # Do a search by given bins
    print("  fitting a 2D marginal with bins method:")
    err, bins, gp_fit, x_train, y_train, y_train_err = \
        hogpen_example.fit_marginal_methods(
                                            gp_api_compact,
                                            np.asarray([0,1]),
                                            method="bins",
                                            grab_edge=True,
                                            bins=np.asarray([4,5]),
                                            max_bins=max_bins,
                                           )
    print("  minimum err: %f; bins:"%(err), bins)
    print("  pass!")
    # Do a search of many bin combinations
    print("  fitting a 2D marginal with search method:")
    err, bins, gp_fit, x_train, y_train, y_train_err = \
        hogpen_example.fit_marginal_methods(
                                            gp_api_compact,
                                            np.asarray([0,1]),
                                            method="search",
                                            grab_edge=True,
                                            min_bins=min_bins,
                                            max_bins=max_bins,
                                           )

    print("  minimum err: %f; bins:"%(err), bins)
    print("  pass!")
    # Go through all of the 1D marginals
    print("  fitting all of the 1D marginals")
    print("  (also tests dd code for 1d)")
    hogpen_dict = hogpen_example.multifit_marginal1d(
                                                     gp_api_compact,
                                                     grab_edge=True,
                                                     min_bins=min_bins,
                                                     max_bins=max_bins,
                                                    )
    print("  pass!")
    # Go through all of the 2D marginals
    print("  fitting all of the 2D marginals")
    print("  (also tests dd code for 2d)")
    hogpen_dict = hogpen_example.multifit_marginal2d(
                                                     gp_api_compact,
                                                     grab_edge=True,
                                                     min_bins=min_bins,
                                                     max_bins=max_bins,
                                                    )

    print("  pass!")
    # Go through all of the 1D and 2D marginals
    print("  fitting all of the 1D and 2D marginals")
    hogpen_dict = hogpen_example.multifit_marginal1d2d(
                                                     gp_api_compact,
                                                     grab_edge=True,
                                                     min_bins=min_bins,
                                                     max_bins=max_bins,
                                                    )
    print("  pass!")

def HOGPEN_test_distances(nsample=100000, ngauss=2, min_bins = 7, max_bins=30, **kwargs):
    ndim=3
    print("HOGPEN distance test:")
    print("  nsample = %d; ngauss = %d, ndim = %d"%(nsample, ngauss, ndim))
    # Generate some samples
    samples = generate_samples(nsample, ngauss, ndim)
    # Create some limits
    limits = np.zeros((ndim, 2))
    limits[:,1] = 1.0
    # Initialize object
    hogpen_example = HOGPEN(samples, limits)
    # Test with default (RMS)
    print("Bin selection by RMS error (default) test:")
    err, bins, gp_fit, x_train, y_train, y_train_err = \
        hogpen_example.fit_marginal(
                                    gp_api_compact,
                                    indices=[0],
                                    min_bins=min_bins,
                                    max_bins=max_bins,
                                    grab_edge=True,
                                   )
    print("  minimum err: %f; bins:"%(err), bins)
    print("  pass!")
    # Test with bhattacharrya distance
    print("Bin selection by Bhattacharyya distance (default) test:")
    err, bins, gp_fit, x_train, y_train, y_train_err = \
        hogpen_example.fit_marginal(
                                    gp_api_compact,
                                    criteria=bhattacharyya_distance,
                                    indices=[0],
                                    min_bins=min_bins,
                                    max_bins=max_bins,
                                    grab_edge=True,
                                   )
    print("  minimum err: %f; bins:"%(err), bins)
    print("  pass!")
    # Test with hellinger distance
    print("Bin selection by Hellinger distance (default) test:")
    err, bins, gp_fit, x_train, y_train, y_train_err = \
        hogpen_example.fit_marginal(
                                    gp_api_compact,
                                    criteria=hellinger_distance,
                                    indices=[0],
                                    min_bins=min_bins,
                                    max_bins=max_bins,
                                    grab_edge=True,
                                   )
    print("  minimum err: %f; bins:"%(err), bins)
    print("  pass!")
    # Test with relative entropy distance
    print("Bin selection by relative entropy (default) test:")
    err, bins, gp_fit, x_train, y_train, y_train_err = \
        hogpen_example.fit_marginal(
                                    gp_api_compact,
                                    criteria=rel_entr,
                                    indices=[0],
                                    min_bins=min_bins,
                                    max_bins=max_bins,
                                    grab_edge=True,
                                   )
    print("  minimum err: %f; bins:"%(err), bins)
    print("  pass!")

def HOGPEN_corner_test(nsample=1000, ngauss=2, min_bins = 7, max_bins=15, **kwargs):
    '''Test the HOGPEN corner plot capabilities'''
    ndim=3
    print("HOGPEN test:")
    print("  nsample = %d; ngauss = %d, ndim = %d"%(nsample, ngauss, ndim))
    # Generate some samples
    samples = generate_samples(nsample=nsample, ngauss=ngauss, ndim=ndim)
    print("  samples generated!")
    # Create some limits
    limits = np.zeros((ndim, 2))
    limits[:,1] = 1.0
    # Initialize object
    hogpen_example = HOGPEN(samples, limits, verbose=True)
    # Go through all of the 1D and 2D marginals
    print("  fitting all of the 1D and 2D marginals")
    hogpen_dict = hogpen_example.multifit_corner(
                                                 gp_api_compact,
                                                 grab_edge=True,
                                                 min_bins=min_bins,
                                                 max_bins=max_bins,
                                                 savename="data/test_HOGPEN_corner.png",
                                                )

######## All Tests ########

def all_test(**kwargs):
    #prune_samples_test(**kwargs)
    #HOGPEN_test_3d(**kwargs)
    #HOGPEN_test_distances(**kwargs)
    HOGPEN_corner_test(**kwargs)
    return

######## Main ########
def main():
    nsample = 100000
    ndim = 3
    ngauss = 2
    all_test(nsample=nsample, ndim=ndim, ngauss=ngauss)
    return

######## Execution ########
if __name__ == "__main__":
    main()

