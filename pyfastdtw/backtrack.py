# -*- coding: utf-8 -*-

import numpy as np
from numba import jit

@jit(nopython=True)
def _backtrack_jit(D,p_ar):
        """fast implementation by numba.jit

        Parameters
        ----------
        D : 2D array
            cumsum cost matrix
        p_ar : 3D array
            step pattern array (see step_pattern.py)

        Returns
        -------
        path : 2D array
            alignment path

        """
        # number of patterns
        num_pattern = p_ar.shape[0]
        # max pattern length
        max_pattern_len = p_ar.shape[1]
        # initialize index
        i,j = D.shape
        i -= 1
        j -= 1
        # alignment path
        path = np.array(((i,j),),dtype=np.int64)
        # cache to memorize D
        D_cache = np.ones(num_pattern,dtype=np.float64) * np.inf

        while not (i == 0 and j == 0):
            for pidx in range(num_pattern):
                # get D value corresponds to end of pattern node
                pattern_index = p_ar[pidx,0,0:2]
                ii = int(i + pattern_index[0])
                jj = int(j + pattern_index[1])
                if ii < 0 and jj < 0:
                    D_cache[pidx] = np.inf
                else:
                    D_cache[pidx] = D[ii,jj]

            # find path minimize D_chache
            min_pattern_idx = np.argmin(D_cache)
            # get where pattern passed
            path_to_add = _get_local_path(D,p_ar[min_pattern_idx,:,:],i,j)
            # concatenate
            path = np.vstack((path,path_to_add))

            i += p_ar[min_pattern_idx,0,0]
            j += p_ar[min_pattern_idx,0,1]
            if i < 0: i = 0
            if j < 0: j = 0

        return path[::-1]

@jit(nopython=True)
def _get_local_path(D,p_ar,i,j):
    """helper function to get local path
    D : cumsum matrix
    p_ar : array of pattern that minimize D at i,j
    """
    weight_col = p_ar[:,2]
    step_selector = np.where(weight_col != 0)[0]
    # note: starting point of pattern was already added
    step_selector = step_selector[:-1]
    # initialize local path
    local_path = np.ones((step_selector.size,2),\
        dtype=np.int64) * -1
    for sidx in step_selector:
        # memorize where passed
        pattern_index = p_ar[sidx,0:2]

        ii = int(i + pattern_index[0])
        jj = int(j + pattern_index[1])

        local_path[sidx,:] = (ii,jj)
    return local_path[::-1]


def _backtrack_py(D,pattern):
    """
    naive implementation
    """
    i,j = D.shape
    i -= 1
    j -= 1
    # path
    path = [(i,j)]
    # pattern array
    p_ar = pattern.array

    D_cache = np.ones(pattern.num_pattern) * np.inf
    while not (i == 0 and j == 0):
        path_cache = []
        for pidx in range(pattern.num_pattern):
            # get D value corresponds to end of pattern
            pattern_index = p_ar[pidx,0,0:2]
            ii = int(i + pattern_index[0])
            jj = int(j + pattern_index[1])
            if ii < 0 and jj < 0:
                D_cache[pidx] = np.inf
            else:
                D_cache[pidx] = D[ii,jj]

            path_step = []
            for sidx in range(pattern.max_pattern_len)[::-1]:
                # memorize where arrived
                if p_ar[pidx,sidx,2] == 0:
                    # if weight value is 0, the row is padded-row
                    continue
                pattern_index = p_ar[pidx,sidx,0:2]
                if pattern_index[0] == 0 and pattern_index[1] == 0:
                    # note: starting point of pattern was already added
                    continue
                ii = int(i + pattern_index[0])
                jj = int(j + pattern_index[1])
                path_step.append((ii,jj))
            path_cache.append(path_step)

        # find path minimize D_chache
        # print("D_cache:{},path_cache:{}".format(D_cache,path_cache))
        min_pattern_idx = np.argmin(D_cache)
        path += path_cache[min_pattern_idx]
        i += p_ar[min_pattern_idx,0,0]
        j += p_ar[min_pattern_idx,0,1]
        if i < 0: i = 0
        if j < 0: j = 0

    path.reverse()
    path = np.array(path)
    return path
