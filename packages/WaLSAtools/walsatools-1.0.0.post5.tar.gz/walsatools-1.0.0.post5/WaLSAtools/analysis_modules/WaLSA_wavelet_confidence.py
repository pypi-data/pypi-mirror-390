# -----------------------------------------------------------------------------------------------------
# WaLSAtools - Wave analysis tools
# Copyright (C) 2025 WaLSA Team - Shahin Jafarzadeh et al.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# Note: If you use WaLSAtools for research, please consider citing:
# Jafarzadeh, S., Jess, D. B., Stangalini, M. et al. 2025, Nature Reviews Methods Primers, 5, 21
# -----------------------------------------------------------------------------------------------------

import numpy as np # type: ignore

def WaLSA_wavelet_confidence(ps_perm, siglevel=None):
    """
    Find the confidence levels (significance levels) for the given wavelet power spectrum permutations.

    Parameters:
    -----------
    ps_perm : np.ndarray
        2D array where each row represents a power spectrum, and each column represents a permutation.
    siglevel : float
        e.g., 0.95 for 95% confidence level (significance at 5%).

    Returns:
    --------
    signif : np.ndarray
        Significance levels for each frequency.
    """
    nnff , nntt, nnperm = ps_perm.shape

    signif = np.zeros((nnff, nntt))

    for iv in range(nnff):
        for it in range(nntt):
            signif[iv, it] = np.percentile(ps_perm[iv, it, :], 100 * siglevel) # e.g., 95% percentile (for 95% consideence level)

    return signif
