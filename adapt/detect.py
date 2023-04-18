"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""


from typing import List

import numpy as np

from ont_fast5_api.fast5_read import Fast5Read

from ._c_llr_segmentation import c_llr_detect_adapter
from .normalize import normalize_signal
from .utils import detectResults


def detect_adapter_in_signal(
    signal: np.ndarray,
    max_obs: int = 40000,
    min_obs_adapter: int = 1000,
    border_trim: int = 500,
) -> detectResults:
    """Function to detect DNA adapter segment in dRNA raw signal.

    Parameters
    ----------
    signal : np.ndarray
        One-dimensional numpy array representation of dRNA signal.
    max_obs : int, optional
        Look for adapter in first `max_obs` data points of the raw signal. Value taken from default params in Tombo, by default 40000
    min_obs_adapter : int, optional
        Minimal length of the adapter signal, by default 1000
    border_trim : int, optional
        Ignore outer `border_trim` data points, a boundary can be detected between `border_trim` and `max_obs`-`border_trim`, by default 500

    Returns
    -------
    res : detectResults
        Results class containing adapter start and end coordinates.
        Start=end=0 indicates that no adapter was detected.

    """

    start, stop = c_llr_detect_adapter(signal[:max_obs], min_obs_adapter, border_trim)

    return detectResults(start, stop)


def detect_adapter_in_read(
    read: Fast5Read,
    max_obs: int = 40000,
    min_obs_adapter: int = 1000,
    border_trim: int = 500,
) -> detectResults:
    """Function to detect DNA adapter segment in dRNA raw signal, directly from the fast5 read.
    Signal is normalized prior to detection.

    Parameters
    ----------
    read : Fast5Read
        read entry from fast5 file (multi or single)
    max_obs : int, optional
        Look for adapter in first `max_obs` data points of the raw signal. Value taken from default params in Tombo, by default 40000
    min_obs_adapter : int, optional
        Minimal length of the adapter signal, by default 1000
    border_trim : int, optional
        Ignore outer `border_trim` data points, a boundary can be detected between `border_trim` and `max_obs`-`border_trim`, by default 500

    Returns
    -------
    res : detectResults
        Results class containing adapter start and end coordinates.
        Start=end=0 indicates that no adapter was detected.

    """

    signal = read.get_raw_data(scale=False).copy()
    norm_signal = normalize_signal(signal)

    return detect_adapter_in_signal(
        norm_signal,
        max_obs=max_obs,
        min_obs_adapter=min_obs_adapter,
        border_trim=border_trim,
    )
