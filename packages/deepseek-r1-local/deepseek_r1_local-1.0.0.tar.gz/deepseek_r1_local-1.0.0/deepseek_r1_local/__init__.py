"""
DeepSeek R1 Local - Offline AI Web UI with Council Deliberation System
"""

__version__ = "1.0.0"
__author__ = "DeepSeek R1 Local Team"

from .app import app, ModelManager, Council, WebSearcher

__all__ = ["app", "ModelManager", "Council", "WebSearcher", "__version__"]
