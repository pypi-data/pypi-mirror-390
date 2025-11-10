"""
ARC Adaptors - Integration adaptors for the Agent Remote Communication Protocol
"""

__version__ = "0.1.0"
__author__ = "ARC Protocol Team"
__license__ = "Apache-2.0"

# Convenience imports
from .base import BaseAdaptor

# Import adaptors if available
try:
    from .langchain import ARCLangChainAdaptor, create_arc_handoff_tool, load_arc_handoff_tools
    _HAS_LANGCHAIN = True
except ImportError:
    _HAS_LANGCHAIN = False

try:
    from .openai import OpenAIAdaptor
    _HAS_OPENAI = True
except ImportError:
    _HAS_OPENAI = False

try:
    from .anthropic import AnthropicAdaptor
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False

try:
    from .mistral import MistralAdaptor
    _HAS_MISTRAL = True
except ImportError:
    _HAS_MISTRAL = False

try:
    from .llama_index import LlamaIndexAdaptor
    _HAS_LLAMA_INDEX = True
except ImportError:
    _HAS_LLAMA_INDEX = False