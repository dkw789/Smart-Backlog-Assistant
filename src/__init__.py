"""Smart Backlog Assistant - AI-powered backlog management system.

This package provides intelligent backlog management capabilities using
multi-agent architecture and AI services for requirements analysis,
user story generation, and priority assessment.
"""

__version__ = "0.1.0"
__author__ = "Smart Backlog Assistant Team"

# Import main components for easy access
from .agents import *
from .api import *
from .database import *
from .generators import *
from .models import *
from .processors import *
from .providers import *
from .utils import *

__all__ = [
    "__version__",
    "__author__",
]