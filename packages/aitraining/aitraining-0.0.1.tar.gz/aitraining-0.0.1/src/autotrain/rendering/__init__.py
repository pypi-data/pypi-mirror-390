"""
Message Rendering System for AutoTrain Advanced
================================================

Provides unified conversation-to-token conversion with support for:
- Multiple chat formats (ChatML, Alpaca, Vicuna, etc.)
- Token-level weight control for training
- Stop sequence detection
- Response parsing
"""

from .message_renderer import (
    MessageRenderer,
    Message,
    Conversation,
    RenderConfig,
    TokenWeight,
    ChatFormat,
    get_renderer,
)

from .formats import (
    ChatMLRenderer,
    AlpacaRenderer,
    VicunaRenderer,
    ZephyrRenderer,
    LlamaRenderer,
    MistralRenderer,
    AVAILABLE_FORMATS,
)

from .utils import (
    build_generation_prompt,
    parse_response,
    get_stop_sequences,
    build_supervised_example,
    apply_token_weights,
    detect_chat_format,
    convert_dataset_to_conversations,
    create_chat_template,
)

__all__ = [
    # Core classes
    "MessageRenderer",
    "Message",
    "Conversation",
    "RenderConfig",
    "TokenWeight",
    "ChatFormat",
    "get_renderer",
    # Format renderers
    "ChatMLRenderer",
    "AlpacaRenderer",
    "VicunaRenderer",
    "ZephyrRenderer",
    "LlamaRenderer",
    "MistralRenderer",
    "AVAILABLE_FORMATS",
    # Utility functions
    "build_generation_prompt",
    "parse_response",
    "get_stop_sequences",
    "build_supervised_example",
    "apply_token_weights",
    "detect_chat_format",
    "convert_dataset_to_conversations",
    "create_chat_template",
]