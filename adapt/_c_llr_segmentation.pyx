"""
ADAPT - Adapter Detection and Processing Tool

Copyright (c) 2023 Wiep K. van der Toorn (w.vandertoorn@fu-berlin.de)

"""


#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

# TODO: fix NPY deprecation warming

cimport cython

import numpy as np
cimport numpy as np

from libc.math cimport log

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

DTYPE_INT = np.int64
ctypedef np.int64_t DTYPE_INT_t

# Calculate the variance of a segment of signal, given cumsum and cumsum of squared signal.
@cython.boundscheck(False)
cdef inline double var_c(DTYPE_INT_t start, DTYPE_INT_t end, 
						 DTYPE_t[:] c, DTYPE_t[:] c2):
	"""
	Adapted from https://github.com/jmschrei/PyPore/blob/master/PyPore/cparsers.pyx

	The MIT License (MIT)

	Copyright (c) 2014 jmschrei
	"""
	
	if start == end:
		return 0
	if start == 0:
		return c2[end-1]/end - (c[end-1]/end) ** 2
	return (c2[end-1]-c2[start-1])/(end-start) - ((c[end-1]-c[start-1])/(end-start)) ** 2

# find single best split based on maximal LLR
def _best_split(DTYPE_INT_t start, 
				DTYPE_INT_t end, 
				np.ndarray[DTYPE_t] c, 
				np.ndarray[DTYPE_t] c2, 
				DTYPE_INT_t offset_head, 
				DTYPE_INT_t offset_tail):
	
	cdef DTYPE_t var_summed
	cdef DTYPE_t var_summed_head
	cdef DTYPE_t var_summed_tail
	cdef DTYPE_t gain
	cdef DTYPE_t split_gain = 0.
	cdef DTYPE_INT_t x = 0
	cdef DTYPE_INT_t i
	
	var_summed = ( end-start ) * log( var_c( start, end, c, c2))
	for i in range( start + offset_head, end - offset_tail):
		var_summed_head = ( i-start ) * log( var_c( start, i, c, c2 ) )
		var_summed_tail = ( end-i ) * log( var_c( i, end, c, c2 ) )
		gain = var_summed-( var_summed_head+var_summed_tail )
		if gain > split_gain:
			split_gain = gain
			x = i
	
	return x, split_gain

# return all LLR's 
def _gains(DTYPE_INT_t start, 
				DTYPE_INT_t end, 
				np.ndarray[DTYPE_t] c, 
				np.ndarray[DTYPE_t] c2, 
				DTYPE_INT_t offset_head, 
				DTYPE_INT_t offset_tail):
	
	cdef DTYPE_t var_summed
	cdef DTYPE_t var_summed_head
	cdef DTYPE_t var_summed_tail
	cdef DTYPE_INT_t i

	cdef np.ndarray[DTYPE_t] gains = np.zeros_like(c)
	
	var_summed = ( end-start ) * log( var_c( start, end, c, c2))
	for i in range( start + offset_head, end - offset_tail):
		var_summed_head = ( i-start ) * log( var_c( start, i, c, c2 ) )
		var_summed_tail = ( end-i ) * log( var_c( i, end, c, c2 ) )
		gains[i] = var_summed-( var_summed_head+var_summed_tail )
	
	return gains


def c_llr_detect_adapter(np.ndarray[DTYPE_t] raw_signal, 
						 DTYPE_INT_t min_obs_adapter,
						 DTYPE_INT_t border_trim):

	cdef np.ndarray[DTYPE_t] c = np.cumsum( raw_signal )
	cdef np.ndarray[DTYPE_t] c2 = np.cumsum( np.multiply( raw_signal, raw_signal ) )

	cdef DTYPE_INT_t x_first = 0
	cdef DTYPE_INT_t x_head = 0
	cdef DTYPE_INT_t x_tail = 0
	cdef DTYPE_INT_t length = len(raw_signal ) - 1
	cdef DTYPE_t gain_head = 0.
	cdef DTYPE_t gain_tail = 0.

	x_first, _ = _best_split(0, length, c, c2, min_obs_adapter + border_trim, border_trim)
	x_head, gain_head = _best_split(0, x_first, c, c2, border_trim, min_obs_adapter)
	x_tail, gain_tail = _best_split(x_first, length, c, c2, min_obs_adapter, border_trim)

	cdef np.ndarray[DTYPE_t] medians = np.zeros(4)
	medians[0] = np.median(raw_signal[:x_head])
	medians[1] = np.median(raw_signal[x_head: x_first])
	medians[2] = np.median(raw_signal[x_first:x_tail])
	medians[3] = np.median(raw_signal[x_tail:])

	
	cdef np.ndarray[DTYPE_t] diffs = np.diff(medians)

	# use fact that adapter represents a drop in pA space
	# TODO: this might be too strict, leading to many failed detections

	if gain_head > gain_tail and diffs[0] < 0 and diffs[1] > 0:
		return x_head, x_first 
	# poly-A on 5` side of adapter` is detected as segment and has low variance
	elif diffs[0] < 0 and diffs[1] > 0 and var_c( x_head, x_first, c, c2)  > var_c( x_first, x_tail, c, c2):
		return x_head, x_first  
	elif  gain_tail > gain_head and diffs[1] < 0 and diffs[2] > 0:
		return x_first, x_tail 
	# segment not found
	else:
		return 0,0


def c_llr_detect_adapter_trace(np.ndarray[DTYPE_t] raw_signal, 
						       DTYPE_INT_t min_obs_adapter,
						       DTYPE_INT_t border_trim):

	cdef np.ndarray[DTYPE_t] c = np.cumsum( raw_signal )
	cdef np.ndarray[DTYPE_t] c2 = np.cumsum( np.multiply( raw_signal, raw_signal ) )

	cdef DTYPE_INT_t x_first = 0
	cdef DTYPE_INT_t length = len(raw_signal ) - 1
	cdef np.ndarray[DTYPE_t] gains_first 
	cdef np.ndarray[DTYPE_t] gains_head 
	cdef np.ndarray[DTYPE_t] gains_tail 

	gains_first = _gains(0, length, c, c2, min_obs_adapter + border_trim, border_trim)
	x_first = np.argmax( gains_first )
	gains_head = _gains(0, x_first, c, c2, border_trim, min_obs_adapter)
	gains_tail = _gains(x_first, length, c, c2, min_obs_adapter, border_trim)

	return gains_first, gains_head, gains_tail
