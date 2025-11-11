#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def rebinGabriel(arr, binning, cut_to_bin=False, method=np.mean):
    ''' Rebin an array by summing its pixels values.
    Parameters
    ==========
    arr : np.ndarray
        The numpy array to bin. The array dimensions must be divisible by the
        requested binning.
    binning : tuple
        A tuple of size arr.ndim containing the binning. This could be (2, 3)
        to perform binning 2x3.
    cut_to_bin : bool (default: False)
        If set to true, and the dimensions of `arr` are not multiples of
        `binning`, clip `arr`, and still bin it.
    method : function (default: np.sum)
        Method to use when gathering pixels values. This value must take a
        np.ndarray as first argument, and accept kwarg `axis`.
    Partly copied from <https://gist.github.com/derricw/95eab740e1b08b78c03f>.
    '''
    new_shape = np.array(arr.shape) // np.array(binning)
    new_shape_residual = np.array(arr.shape) % np.array(binning)
    if np.any(new_shape_residual):
        m = 'Bad binning {} for array with dimension {}.'
        m = m.format(binning, arr.shape)
        if cut_to_bin:
            m += ' Clipping array to {}.'
            m = m.format(tuple(np.array(arr.shape) - new_shape_residual))
            print(m)
            new_slice = [slice(None, -i) if i else slice(None)
                         for i in new_shape_residual]
            arr = arr[new_slice]
        else:
            raise ValueError(m)

    compression_pairs = [
        (d, c//d) for d, c in zip(new_shape, arr.shape)]
    flattened = [l for p in compression_pairs for l in p]
    arr = arr.reshape(flattened)
    axis_to_sum = (2*i + 1 for i in range(len(new_shape)))
    arr = method(arr, axis=tuple(axis_to_sum))

    assert np.all(arr.shape == new_shape)

    return arr

def rebinFred(arr, new_shape):
    shape = (new_shape, arr.shape[0] // new_shape)
    return arr.reshape(shape).mean(-1)

"""a = np.array([1,2,3,4,5,6])
b = rebinGabriel(a, (2))
facteur = len(a) / len(b)
print(b, facteur)"""

#c = rebinFred(a, 6)
#print(c)