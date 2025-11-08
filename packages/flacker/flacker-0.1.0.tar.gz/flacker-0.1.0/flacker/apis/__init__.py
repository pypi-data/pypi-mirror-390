"""
Predefined APIs to use as endpoints for the engine.
"""

from .hue_api import HueApi
from .hue_entertainment_api import HueEntertainmentApi
from .log_api import LogApi
from .multi_api import MultiApi
from .plot_api import PlotApi

__all__ = ["HueApi", "HueEntertainmentApi", "LogApi", "MultiApi", "PlotApi"]
