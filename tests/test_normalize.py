"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""


import numpy as np

from adapt.normalize import normalize_signal


def test_shape():
    signal = np.random.randint(50, 350, 100, dtype=np.int16)
    norm_signal = normalize_signal(signal)

    assert signal.shape == norm_signal.shape


def test_dtype():
    signal = np.random.randint(50, 350, 100, dtype=np.int16)
    norm_signal = normalize_signal(signal)

    assert norm_signal.dtype == np.float64


def test_windsorizing():
    signal = np.random.randint(50, 350, 100, dtype=np.int16)
    outlier_thresh = 2
    norm_signal = normalize_signal(signal, outlier_thresh)

    norm_med = np.median(norm_signal)
    norm_mad = np.median(np.abs(norm_signal - norm_med))

    lower_lim = norm_med - (norm_mad * outlier_thresh)
    upper_lim = norm_med + (norm_mad * outlier_thresh)

    assert (norm_med <= upper_lim).all()
    assert (norm_med >= lower_lim).all()
