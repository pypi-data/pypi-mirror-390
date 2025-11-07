#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 06/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

class Synthesizer:
	
	def __init__(self):
		pass
		
	def f0(f0_, f0t, sr, nharm=0):
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
		
		from ._f0 import F0Synthesizer
		
		y, sr = F0Synthesizer.synthesize(f0_, f0t, sr, nharm)
		
		return y, sr
	
	def onsets(onsets_, sr, freq=1000, nharm=1, click_duration_ms=30, size=None):
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
		np.ndarray
			Audio signal with sine wave clicks (with harmonics) at event times.
		int
			Sampling rate of the generated click audio.
		"""
		
		from ._onsets import OnsetsSynthesizer
		
		y, sr = OnsetsSynthesizer.synthesize(onsets_, sr, freq, nharm, click_duration_ms, size)
		
		return y, sr