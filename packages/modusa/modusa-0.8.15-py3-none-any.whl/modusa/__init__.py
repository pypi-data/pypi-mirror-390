# Loader
from ._loader.loader import Loader as load

# Synthesizer
from ._synthesizer.synthesizer import Synthesizer as synthesize

# Media Player
from ._mediaplayer.mediaplayer import MediaPlayer as play

# Media Recorder
from ._mediarecorder.mediarecorder import MediaRecorder as record

# Saver
from ._saver.saver import Saver as saveas

# Feature Extractor
from ._feature_extractor.feature_extractor import FeatureExtractor as extract

# =================== Visualizer ======================
# Plotter
from ._visualizer._plotter.plotter import Plotter as plot

# Style Setter
from ._visualizer._style_setter.style_setter import StyleSetter as set

# Interactor
from ._visualizer._interactor.interactor import Interactor as interact

# Animator
from ._visualizer._animator.animator import Animator as animate

# Layout Generator
from ._visualizer._layout_generator.layout_generator import LayoutGenerator as layouts

# Quick Plotter
from ._visualizer._plotter._quick_plotter import hill_plot

#==========================================================


#====================
# GLOBAL ATTRIBUTES

__version__ = "0.8.15" # This is dynamically used by the documentation, and pyproject.toml; Only need to change it here; rest gets taken care of.

#====================