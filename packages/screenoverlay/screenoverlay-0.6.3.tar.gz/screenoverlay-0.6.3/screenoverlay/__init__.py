"""
ScreenOverlay - Cross-platform screen overlay library
Provides blur, black, white, and custom color overlays with minimal latency
"""

from .overlay import NativeBlurOverlay as Overlay

__version__ = '0.6.3'
__author__ = 'ScreenStop'
__all__ = ['Overlay']

