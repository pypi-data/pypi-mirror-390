#!/usr/bin/env python3

#---------------------------------
# Author: Ankit Anand
# Date: 06/11/25
# Email: ankit0.anand0@gmail.com
#---------------------------------

class Loader:
	def __init__(self):
		pass
		
	@staticmethod
	def audio(path, sr=None, trim=None, ch=None):
		"""
		Lightweight audio loader using imageio-ffmpeg.
	
		Parameters
		----------
		path: PathLike/str/URL
			- Path to the audio file / YouTube video
		sr: int
			- Sampling rate to load the audio in.
			- Default: None => Use the original sampling rate
		trim: tuple[number, number]
			- (start, end) in seconds to trim the audio clip.
			- Default: None => No trimming
		ch: int
			- 1 for mono and 2 for stereo
			- Default: None => Use the original number of channels.
	
		Returns
		-------
		np.ndarray
			- Audio signal Float32 waveform in [-1, 1].
		int:
			Sampling rate.
		str:
			File name stem.
		"""
		
		from ._audio import AudioLoader
		
		y, sr, title = AudioLoader.load(path, sr=sr, trim=trim, ch=ch)
		
		return y, sr, title

	@staticmethod
	def image(path):
		"""
		Loads an images using imageio.
	
		Parameters
		----------
		path: str | PathLike
			Image file path.
		
		Returns
		-------
		ndarray
			Image array (2D/3D with RGB channel)
		"""
		from ._image import ImageLoader
		
		img = ImageLoader.load(path)
		
		return img
	
	@staticmethod
	def annotation(path, trim=None):
		"""
		Load annotation from audatity label
		text file and also ctm file.
	
		Parameters
		----------
		path: str | PathLike
			label text/ctm file path.
		trim: tuple[number, number] | number | None
			Incase you trimmed the audio signal, this parameter will help clip the annotation making sure that the timings are aligned to the trimmed audio.
			If you trimmed the audio, say from (10, 20), set the trim to (10, 20).
			Default: None
	
		Returns
		-------
		list[tuple, ...]
			- annotation data structure
			- [(start, end, label), ...]
		"""
		from ._annotation import AnnotationLoader
		
		ann = AnnotationLoader.load(path, trim)
		
		return ann