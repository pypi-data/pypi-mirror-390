# -*- coding: utf-8 -*-

"""Interactive TUI for Feature Flag Service (FFS) management.

This module provides the entry point for the FFS TUI application.
"""

# Export the main TUI runner
from .tui import run_tui

__all__ = ["run_tui"]
