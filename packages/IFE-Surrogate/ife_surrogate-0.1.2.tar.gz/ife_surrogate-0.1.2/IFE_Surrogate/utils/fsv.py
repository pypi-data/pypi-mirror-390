# ------------------------------------------------------------------------------
# Project: IFE_Surrogate
# Authors: Tobias Leitgeb, Julian Tischler
# CD Lab 2025
# ------------------------------------------------------------------------------
import numpy as np
from numpy.fft import fft, ifft
from typing import List

def find_point(array):
    """
    Find the index in 'array' where cumulative sum reaches 40% of total sum.
    """
    total_sum = np.sum(np.abs(array))
    target = 0.4 * total_sum
    cum = 0
    for idx, val in enumerate(np.abs(array)):
        cum += val
        if cum >= target:
            return idx
    return len(array) - 1


def _apply_fsv_single(y1, y2):
    """Apply FSV on one pair of signals."""
    N = len(y1)

    # FFT
    F1 = fft(y1)
    F2 = fft(y2)

    # determine split frequency (ignore first 4 bins)
    idx1 = find_point(F1[4:]) + 4
    idx2 = find_point(F2[4:]) + 4
    split = min(idx1, idx2)

    # build low/high filters with linear ramp over ±3 bins
    lo_filter = np.zeros(N)
    hi_filter = np.ones(N)
    start = max(split - 3, 0)
    end = min(split + 3, N - 1)
    ramp = np.linspace(1, 0, end - start + 1)
    lo_filter[start:end + 1] = ramp
    hi_filter[start:end + 1] = 1 - ramp

    # apply filters and inverse FFT
    lo1 = np.real(ifft(F1 * lo_filter))
    lo2 = np.real(ifft(F2 * lo_filter))
    hi1 = np.real(ifft(F1 * hi_filter))
    hi2 = np.real(ifft(F2 * hi_filter))

    # ADM
    alpha = np.abs(lo1 - lo2)
    beta = (1/N) * np.sum(np.abs(lo1) + np.abs(lo2))
    X = np.abs(y1 - y2)
    delta = (1/N) * np.sum(np.abs(y1) + np.abs(y2))
    ADMi = (alpha / beta) + (X / delta) * np.exp(X / delta)
    ADMi[ADMi > 50] = 0
    ADM = np.mean(ADMi)

    # derivatives
    def deriv(arr, order=1):
        if order == 1:
            d = np.zeros_like(arr)
            d[1:-1] = arr[2:] - arr[:-2]
            d[0] = arr[1] - arr[0]
            d[-1] = arr[-1] - arr[-2]
            return d
        elif order == 2:
            return deriv(deriv(arr, 1), 1)
        else:
            raise ValueError("Only orders 1 and 2 supported")

    dlo1 = deriv(lo1, 1); dlo2 = deriv(lo2, 1)
    dhi1 = deriv(hi1, 1); dhi2 = deriv(hi2, 1)
    d2hi1 = deriv(hi1, 2); d2hi2 = deriv(hi2, 2)

    # FDM
    FDM1 = np.abs(dlo1 - dlo2) / ((2/N) * np.sum(np.abs(dlo1) + np.abs(dlo2)))
    FDM2 = np.abs(dhi1 - dhi2) / ((6/N) * np.sum(np.abs(dhi1) + np.abs(dhi2)))
    FDM3 = np.abs(d2hi1 - d2hi2) / ((7.2/N) * np.sum(np.abs(d2hi1) + np.abs(d2hi2)))
    FDMi = 2 * (FDM1 + FDM2 + FDM3)
    FDM = np.mean(FDMi)

    # GDM
    GDMi = np.sqrt(ADMi**2 + FDMi**2)
    GDM = np.mean(GDMi)

    return ADM, FDM, GDM


def apply_fsv(Y_test: np.ndarray, Y_pred: np.ndarray, score_strings: bool = False)-> np.ndarray:
    """
    Batch FSV: apply across multiple test/pred pairs.
    Calculates the FSV parameters as described in [1]
    
    [1] A. P. Duffy, A. J. M. Martin, A. Orlandi, G. Antonini, T. M. Benson, and M. S. Woolfson,
    "Feature Selective Validation (FSV) for Validation of Computational Electromagnetics (CEM).
    Part I—The FSV Method," IEEE Trans. Electromagnetic Compatibility, vol. 48, no. 3,
    pp. 449-458, Aug. 2006, doi:10.1109/TEMC.2006.879358 

    Args:
        Y_test: array of shape (M, N) or list of arrays
        Y_pred: same shape as Y_test
        score_string: returns the labels instead of the numerical scores

    Returns:
        ADM_list, FDM_list, GDM_list: arrays of length M
    """
    Y_test = np.asarray(Y_test, dtype=float)
    Y_pred = np.asarray(Y_pred, dtype=float)
    if Y_test.ndim == 1:
        return _apply_fsv_single(Y_test, Y_pred)

    M = Y_test.shape[0]
    ADM_list = np.zeros(M)
    FDM_list = np.zeros(M)
    GDM_list = np.zeros(M)
    for i in range(M):
        ADM_list[i], FDM_list[i], GDM_list[i] = _apply_fsv_single(Y_test[i], Y_pred[i])

    if score_strings:
        return categorize_scores(ADM_list), categorize_scores(FDM_list), categorize_scores(GDM_list)
    else:
        return ADM_list, FDM_list, GDM_list


def categorize_scores(scores: np.ndarray, bins=None, labels=None) -> List[str]:
    """
    Map numeric scores to qualitative labels based on bins.

    Supports scalars or arrays; returns single label or list correspondingly.

    Args:
        scores: scalar or array-like
        bins: list of bin edges; default [0,0.1,0.2,0.4,0.8,1.6,inf]
        labels: list of labels; default ['Excellent','Very Good','Good','Fair','Poor','Very Poor']

    Returns:
        Single label (str) if input scalar, else list of labels.
    """
    if bins is None:
        bins = [0, 0.1, 0.2, 0.4, 0.8, 1.6, np.inf]
    if labels is None:
        labels = ['Excellent', 'Very Good', 'Good', 'Fair', 'Poor', 'Very Poor']

    arr = np.atleast_1d(scores)
    idx = np.digitize(arr, bins, right=False) - 1
    idx = np.clip(idx, 0, len(labels)-1)
    mapped = [labels[i] for i in idx]
    return mapped[0] if np.isscalar(scores) else mapped
