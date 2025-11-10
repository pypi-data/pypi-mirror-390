"""
Hexagon Python SDK
Makes your website AI-readable by ChatGPT, Perplexity, Claude and other AI platforms
"""

from .hexagon import Hexagon
from .flask_integration import hexagon_middleware as flask_middleware

__version__ = "1.0.0"
__all__ = ["Hexagon", "flask_middleware"]

# Optional Django support
try:
    from .django_integration import HexagonMiddleware as DjangoMiddleware
    __all__.append("DjangoMiddleware")
except ImportError:
    pass

