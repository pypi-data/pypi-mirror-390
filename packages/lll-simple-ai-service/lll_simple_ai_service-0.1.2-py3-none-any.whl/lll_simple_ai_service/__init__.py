from .core.structured_ai import StructuredAIModel
from .config.default_config import AIConfig
from .web.api import create_app

__version__ = "0.1.2"
__all__ = ["StructuredAIModel", "AIConfig", "create_app"]
