"""
Lexia Integration Package
========================

Clean, minimal package for Lexia platform integration.
Contains only essential components for communication.
"""

__version__ = "1.2.9"

from .models import ChatResponse, ChatMessage, Variable, Memory
from .response_handler import create_success_response
from .unified_handler import LexiaHandler, create_link_button_block, create_action_button_block
from .utils import get_variable_value, get_openai_api_key, Variables, MemoryHelper, ForceToolsHelper, decode_base64_file
from .dev_stream_client import DevStreamClient

# Web framework utilities
try:
    from .web import create_lexia_app, add_standard_endpoints
    __all__ = [
        'ChatResponse', 'ChatMessage', 'Variable', 'Memory',
        'create_success_response', 'LexiaHandler', 'DevStreamClient',
        'get_variable_value', 'get_openai_api_key', 'Variables', 'MemoryHelper', 'ForceToolsHelper', 'decode_base64_file',
        'create_link_button_block', 'create_action_button_block',
        'create_lexia_app', 'add_standard_endpoints',
        '__version__'
    ]
except ImportError:
    # Fallback if web dependencies aren't available
    __all__ = [
        'ChatResponse', 'ChatMessage', 'Variable', 'Memory',
        'create_success_response', 'LexiaHandler', 'DevStreamClient',
        'get_variable_value', 'get_openai_api_key', 'Variables', 'MemoryHelper', 'ForceToolsHelper', 'decode_base64_file',
        'create_link_button_block', 'create_action_button_block',
        '__version__'
    ]
