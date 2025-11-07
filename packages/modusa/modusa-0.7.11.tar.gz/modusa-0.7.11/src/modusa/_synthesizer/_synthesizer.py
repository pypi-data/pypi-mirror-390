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
		Synthesize f0 contour so that you can
		hear it back.
	
		Parameters
		----------
		f0: ndarray
			Fundamental frequency (f0) contour in Hz.
		f0t: ndarray
			Timestamps in seconds
		sr: int
			Sampling rate in Hz for the synthesized audio.
		nharm: int
			Number of harmonics
			Default: 0 => Only fundamental frequency (No harmonics)
	
		Returns
		-------
		ndarray
			Syntesized audio.
		sr
			Sampling rate of the synthesized audio
		"""
		
		from ._f0 import F0Synthesizer
		
		y, sr = F0Synthesizer.synthesize(f0_, f0t, sr, nharm)
		
		return y, sr
	
	def onsets(onsets_, sr, freq=500, nharm=4, click_duration_ms=5):
		"""
		Generate a train of short sine wave clicks with harmonics at specified event times.
	
		Parameters
		----------
		onsets_ : array-like
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
		
		from ._onsets import OnsetsSynthesizer
		
		y, sr = OnsetsSynthesizer.synthesize(onsets_, sr, freq, nharm, click_duration_ms)
		
		return y, sr