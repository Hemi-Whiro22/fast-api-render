# -*- coding: utf-8 -*-
"""Compatibility layer re-exporting the core settings implementation."""

from __future__ import annotations

from Te_Po.core.config import Settings, get_settings, get_settings_summary, settings

__all__ = ["Settings", "get_settings", "get_settings_summary", "settings"]