# Loader
from ._loader._loader import Loader as load

# Synthesizer
from ._synthesizer._synthesizer import Synthesizer as synthesize

# Media Player
from ._mediaplayer._mediaplayer import MediaPlayer as play

# Media Recorder
from ._mediarecorder._mediarecorder import MediaRecorder as record

# Visualizer
from ._visualizer._canvas import CanvasGenerator as canvas
from ._visualizer._quick_plotter import hill_plot, plot
from ._visualizer._animator import Animator as animate

# Feature Extractor
from ._feature_extractor._feature_extractor import FeatureExtractor as extract

#====================
# GLOBAL ATTRIBUTES

__version__ = "0.7.14" # This is dynamically used by the documentation, and pyproject.toml; Only need to change it here; rest gets taken care of.

#====================