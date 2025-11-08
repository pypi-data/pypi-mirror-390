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
	
	def onsets(onsets_, sr, freq=1000, click_duration=0.03, size=None, strengths=None):
		"""
		Synthesize a metronome-like click train with optional per-click strengths.
	
		Parameters
		----------
		onsets : array-like
			Times of clicks in seconds.
		sr : int
			Sample rate.
		freq : float
			Frequency of the click sound (Hz).
		click_duration : float
			Duration of each click in seconds.
		size : int or None
			Length to trim/pad the final output (in samples). If None, determined from onsets.
		strengths : array-like or None
			Relative amplitude of each click (same length as `onsets`).
			If None, all clicks are equal in strength (1.0).
	
		Returns
		-------
		np.ndarray
			Audio signal with sine wave clicks at event times.
		int
			Sampling rate of the generated click audio.
		"""
		
		from ._onsets import OnsetsSynthesizer
		
		y, sr = OnsetsSynthesizer.synthesize(onsets_, sr, freq, click_duration, size, strengths)
		
		return y, sr