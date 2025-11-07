#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 06/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

import numpy as np

class OnsetsSynthesizer:
	
	def __init__(self):
		pass
		
	
	def synthesize(onsets, sr, freq, nharm, click_duration_ms, size=None):
		"""
		Synthesize a pleasant metronome-like click train.
	
		Parameters
		----------
		onsets : array-like
			Times of clicks in seconds.
		sr : int
			Sample rate.
		freq : float
			Fundamental frequency of the click.
		nharm : int
			Number of harmonics to include (richer sound).
		click_duration_ms : float
			Duration of each click in milliseconds.
		size : int or None
			Length to trim/pad the final output (in samples). If None, determined from onsets.
		
		Returns
		-------
		y : np.ndarray
			Synthesized audio signal.
		"""
		click_duration = click_duration_ms / 1000
		t_click = np.linspace(0, click_duration, int(sr * click_duration), False)
		
		# Create click with harmonics
		click = np.zeros_like(t_click)
		for h in range(1, nharm + 1):
			click += np.sin(2 * np.pi * freq * h * t_click) / h
			
		# Apply exponential decay envelope for a percussive feel
		click *= np.exp(-15 * t_click)
		
		# Determine output length
		if size is None:
			size = int(np.ceil((max(onsets) + click_duration) * sr))
			
		y = np.zeros(size)
		
		# Place clicks at specified onsets
		for onset in onsets:
			start = int(onset * sr)
			end = start + len(click)
			if end > size:
				end = size
			y[start:end] += click[:end-start]
			
		# Normalize
		y /= np.max(np.abs(y)) + 1e-10
		
		return y, sr