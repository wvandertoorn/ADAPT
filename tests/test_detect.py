"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""

import numpy as np

from adapt.detect import detect_adapter_in_signal


def test_constant_signal():
    signal = np.ones(5000, dtype=np.float64)

    res = detect_adapter_in_signal(signal, max_obs=4000)
    assert res.adapter_start == 0
    assert res.adapter_end == 0


def test_adapter_present():
    signal = np.concatenate(
        [
            np.random.normal(120, 5, 1000),
            np.random.normal(60, 3, 5000),
            np.random.normal(100, 7, 10000),
        ]
    )

    res = detect_adapter_in_signal(signal, max_obs=16000)
    assert np.abs(np.subtract(res.adapter_start, 1000)) < 100
    assert np.abs(np.subtract(res.adapter_end, 6000)) < 100


def test_max_obs_greater_than_length():
    signal = np.ones(5000, dtype=np.float64)

    res = detect_adapter_in_signal(signal, max_obs=40000)
    assert res.adapter_start == 0
    assert res.adapter_end == 0

    signal = np.concatenate(
        [
            np.random.normal(120, 5, 1000),
            np.random.normal(60, 3, 5000),
            np.random.normal(100, 7, 10000),
        ]
    )

    res = detect_adapter_in_signal(signal, max_obs=40000)
    assert np.abs(np.subtract(res.adapter_start, 1000)) < 100
    assert np.abs(np.subtract(res.adapter_end, 6000)) < 100


def test_trim_too_much():
    signal = np.concatenate(
        [
            np.random.normal(120, 5, 1000),
            np.random.normal(60, 3, 5000),
            np.random.normal(100, 7, 10000),
        ]
    )

    res = detect_adapter_in_signal(signal, min_obs_adapter=12000, border_trim=2000)
    assert res.adapter_start == 0
    assert res.adapter_end == 0
