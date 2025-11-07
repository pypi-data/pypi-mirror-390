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
		
	
	def synthesize(onsets, sr, freq, nharm, click_duration_ms):
		"""
		Generate a train of short sine wave clicks with harmonics at specified event times.
	
		Parameters
		----------
		onsets : array-like
			Times of events in seconds where clicks should be placed.
		sr : int
			Sampling rate in Hz.
		freq : float, optional
			Fundamental frequency of the sine click in Hz. Default is 500 Hz.
		nharm : int | None
			Number of harmonics to include (including fundamental). Default is 4.
		click_duration_ms : float | None
			Duration of each click in milliseconds. Default is 5 ms.
		
		Returns
		-------
		np.ndarray
			Audio signal with sine wave clicks (with harmonics) at event times.
		int
			Sampling rate of the generated click audio.
		"""
		
		n_samples = int(np.ceil(sr * onsets[-1]))
		y = np.zeros(n_samples, dtype=np.float32)
		
		# Single click length
		click_len = int(sr * click_duration_ms / 1000)
		if click_len < 1:
			click_len = 1
			
		t = np.arange(click_len) / sr
		window = np.hanning(click_len)
		
		# Generate harmonic sine click
		sine_click = np.zeros(click_len)
		for n in range(1, nharm+2):
			sine_click += (1 / n**2) * np.sin(2 * np.pi * freq * n * t)
			
		# Apply window
		sine_click = sine_click * window**2
		
		for event_time in onsets:
			start_sample = int(event_time * sr)
			end_sample = start_sample + click_len
			if end_sample > n_samples:
				end_sample = n_samples
			y[start_sample:end_sample] += sine_click[:end_sample - start_sample]
			
		# Normalize to avoid clipping if clicks overlap
		y /= np.max(np.abs(y))
		
		return y, sr