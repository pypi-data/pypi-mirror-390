"""
HP UIA Core Library
-------------------
Core abstraction layer for HP internal UI automation.
"""

try:
    from importlib.metadata import version as _v
    __version__ = _v("hp-uia-core")
except Exception:
    __version__ = "0.0.0"

from .app_manager import AppManager

__all__ = ["AppManager"]
