"""
BEBE Task Recorder - Professional macro recorder and automation tool for Windows

A powerful, user-friendly macro recording and playback application designed for Windows.
Record mouse movements, clicks, keyboard input, and key combinations with precision.
"""

__version__ = "1.0.0"
__author__ = "BEBE Team"
__email__ = ""

from .bebe_gui import (
    TaskRecorder,
    TaskPlayer,
    BebeGUI,
    is_admin,
    run_as_admin,
    main
)

__all__ = [
    'TaskRecorder',
    'TaskPlayer',
    'BebeGUI',
    'is_admin',
    'run_as_admin',
    'main',
    '__version__',
]

