#!/usr/env/bin python3

######## Setup ########
import numpy as np
import time

from basil_core.stats.density.density_utils import prune_samples
from basil_core.stats.density.density_utils import multigauss_samples

from basil_core.plots.corner import Corner

######## GLOBALS ########
SEED = 42
RS = np.random.RandomState(SEED)

######## Functions ########

def generate_samples(nsample=1000, ngauss=2, ndim=3):
    samples = multigauss_samples(ndim, ngauss, nsample, seed=RS)
    return samples

######## Tests ########

def prune_samples_test(nsample=1000, ngauss=2, ndim=3, **kwargs):
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

def test_corner(ndim=2, nsample=1000, ngauss=3, bins=100):
    '''Test the basic functionality of the corner plot code'''
    # Generate some samples
    samples = generate_samples(nsample=nsample, ngauss=ngauss, ndim=ndim)
    samples2 = generate_samples(nsample=nsample, ngauss=ngauss, ndim=ndim)
    # Get some realisitic limits
    #limits = np.quantile(samples, [0.05, 0.95], axis=0).T
    # Generate some labels
    somelabels = []
    for i in range(ndim):
        somelabels.append(r"$X_{%d}$"%(i))
    # Initialize a corner plot
    mycorner = Corner(
                      ndim,
                      labels=somelabels,
                      fontscale=1.0,
                      figsize=7.,
                      log_scale=False,
                      title="Mycorner",
                     )
    # Add a histogram layer
    mycorner.add_histogram_layer(
                                 samples,
                                 bins=bins,
                                 imshow=False,
                                 contour=True,
                                 linestyle="solid",
                                 label="samples",
                                )
    # Add a histogram layer
    mycorner.add_histogram_layer(
                                 samples2,
                                 bins=bins,
                                 imshow=False,
                                 contour=True,
                                 linestyle="dotted",
                                 label="samples2",
                                )
    # Create a scatter layer
    mycorner.add_scatter2d_layer(
                               samples[:10],
                               np.std(samples,axis=0),
                              )
    # Show it to me
    #mycorner.show()
    # Save it
    mycorner.save("data/test_corner.png")

######## All Tests ########

def all_test(**kwargs):
    test_corner(**kwargs)
    return

######## Main ########
def main():
    nsample = 1000000
    ndim = 3
    ngauss = 2
    bins=30
    all_test(nsample=nsample, ndim=ndim, ngauss=ngauss, bins=bins)
    return

######## Execution ########
if __name__ == "__main__":
    main()

