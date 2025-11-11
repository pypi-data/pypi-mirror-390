"""
LegalMind AI - Indonesian Legal Assistant
"""

__version__ = "1.0.0"
__author__ = "LegalMind AI Team"
__email__ = "contact@legalmind.ai"

from .core import LegalMind, create_analyzer

# Main exports
__all__ = [
    "LegalMind",
    "create_analyzer",
]
