"""
VersaLaw2 Core Package
Complete legal AI system
"""

from .system import VersaLaw2System
from .config import Config
from .data_loader import MayaLawDataLoader

__version__ = "2.0.0"
__all__ = ['VersaLaw2System', 'Config', 'MayaLawDataLoader']
