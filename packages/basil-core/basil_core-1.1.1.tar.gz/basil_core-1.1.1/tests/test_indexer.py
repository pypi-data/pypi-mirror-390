#!/usr/env/bin python3

######## Setup ########
import numpy as np
#from basil_core.array_tools import indexer
import time

SEED = 42
rs = np.random.RandomState(SEED)

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
    

######## C extensions ########

def cext_indexer(arr, samples):
    from basil_core.array_tools import unique_array_index
    return unique_array_index(arr, samples)

######## Numpy functions ########
def list_indexer(arr, samples):
    arr = list(arr)
    indices = np.zeros(samples.size, dtype=int)
    for i in range(indices.size):
        assert samples[i] in arr
        indices[i] = arr.index(samples[i])
    return indices

def numpy_indexer(arr, samples):
    indices = np.zeros(samples.size, dtype=int)
    for i in range(indices.size):
        assert samples[i] in arr
        indices[i] = np.where(arr == samples[i])[0]
    return indices

######## Tests ########
def test_indexer(n_mono=int(1e4), n_samples=int(1e5), inc=300):
    arr, samples = sample_data(n_mono, n_samples, inc)
    print("Testing indexer:")
    #t0 = time.time()
    #indices_list = list_indexer(arr, samples)
    #t1 = time.time()
    #assert all(arr[indices_list] == samples)
    #print("  list time: %s seconds"%(t1-t0))
    t0 = time.time()
    indices_numpy = numpy_indexer(arr, samples)
    t1 = time.time()
    assert all(arr[indices_numpy] == samples)
    print("  numpy time: %s seconds"%(t1-t0))
    t0 = time.time()
    indices_cext = cext_indexer(arr, samples)
    t1 = time.time()
    assert indices_cext.size == samples.size
    assert all(arr[indices_cext] == samples)
    print("  c extension time: %s seconds"%(t1-t0))


    #### Test types ####
    ## uint16 ##
    arr, samples = sample_data(int(1e3), n_samples, 3)
    arr = arr.astype(np.uint16)
    samples = samples.astype(np.uint16)
    indices_cext = cext_indexer(arr, samples)
    assert all(arr[indices_cext] == samples)

    ## uint32 ##
    arr, samples = sample_data(int(1e3), n_samples, np.iinfo(np.int16).max)
    arr = arr.astype(np.uint32)
    samples = samples.astype(np.uint32)
    indices_cext = cext_indexer(arr, samples)
    assert all(arr[indices_cext] == samples)

    ## uint64 ##
    arr, samples = sample_data(int(1e3), n_samples, np.iinfo(np.int32).max)
    arr = arr.astype(np.uint64)
    samples = samples.astype(np.uint64)
    indices_cext = cext_indexer(arr, samples)
    assert all(arr[indices_cext] == samples)

    #### Test failures ####
    ## int16 ##
    arr, samples = sample_data(int(1e3), n_samples, 3)
    arr = arr.astype(np.int16)
    samples = samples.astype(np.int16)
    _id = np.argmax(samples)
    samples[_id] -= 1
    assert not (samples[_id] in arr)
    indices_cext = cext_indexer(arr, samples)
    mask = indices_cext >=0
    assert all(arr[indices_cext[mask]] == samples[mask])
    assert all(indices_cext[~mask] == -1)

    ## int32 ##
    arr, samples = sample_data(int(1e3), n_samples, np.iinfo(np.int16).max)
    arr = arr.astype(np.int32)
    samples = samples.astype(np.int32)
    _id = np.argmax(samples)
    samples[_id] -= 1
    assert not (samples[_id] in arr)
    indices_cext = cext_indexer(arr, samples)
    mask = indices_cext >=0
    assert all(arr[indices_cext[mask]] == samples[mask])
    assert all(indices_cext[~mask] == -1)

    ## int64 ##
    arr, samples = sample_data(int(1e3), n_samples, np.iinfo(np.int32).max)
    arr = arr.astype(np.int64)
    samples = samples.astype(np.int64)
    _id = np.argmax(samples)
    samples[_id] -= 1
    assert not (samples[_id] in arr)
    indices_cext = cext_indexer(arr, samples)
    mask = indices_cext >=0
    assert all(arr[indices_cext[mask]] == samples[mask])
    assert all(indices_cext[~mask] == -1)

    print("  pass!")
    return

######## Main ########
def main():
    test_indexer()
    return

######## Execution ########
if __name__ == "__main__":
    main()
