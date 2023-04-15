"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""


import numpy as np


def normalize_signal(signal: np.ndarray, outlier_thresh: int = 5) -> np.ndarray:
    """MED/MAD normalization with windsorizing

    Parameters
    ----------
    signal : np.ndarray
        signal to normalize
    outlier_thresh : int, optional
        windsorize threshold, by default 5

    Returns
    -------
    np.ndarray
        numpy array with dtype np.float64 of normalized signal
    """
    shift = np.median(signal)
    scale = np.median(np.abs(signal - shift))

    norm_signal = (signal - shift) / scale

    # windsorize the raw signal
    read_med = np.median(norm_signal)
    read_mad = np.median(np.abs(norm_signal - read_med))
    lower_lim = read_med - (read_mad * outlier_thresh)
    upper_lim = read_med + (read_mad * outlier_thresh)

    norm_signal[norm_signal < lower_lim] = lower_lim
    norm_signal[norm_signal > upper_lim] = upper_lim

    return norm_signal
