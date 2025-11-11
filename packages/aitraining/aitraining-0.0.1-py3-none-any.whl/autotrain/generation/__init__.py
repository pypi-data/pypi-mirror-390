"""
Generation/Completers Interface for AutoTrain Advanced
========================================================

Provides clean abstractions for model generation at different levels:
- TokenCompleter: Low-level token generation (for RL)
- MessageCompleter: High-level message generation
- AsyncCompleter: Asynchronous generation support
"""

from .completers import (
    Completer,
    TokenCompleter,
    MessageCompleter,
    AsyncTokenCompleter,
    AsyncMessageCompleter,
    CompletionConfig,
    CompletionResult,
    TokenCompletionResult,
    MessageCompletionResult,
)

from .sampling import (
    SamplingConfig,
    SamplingStrategy,
    TopKSampler,
    TopPSampler,
    BeamSearchSampler,
    TypicalSampler,
)

from .utils import (
    create_completer,
    batch_complete,
    stream_tokens,
    stream_messages,
    create_chat_session,
    ChatSession,
)

__all__ = [
    # Core completers
    "Completer",
    "TokenCompleter",
    "MessageCompleter",
    "AsyncTokenCompleter",
    "AsyncMessageCompleter",
    # Configurations
    "CompletionConfig",
    "CompletionResult",
    "TokenCompletionResult",
    "MessageCompletionResult",
    # Sampling
    "SamplingConfig",
    "SamplingStrategy",
    "TopKSampler",
    "TopPSampler",
    "BeamSearchSampler",
    "TypicalSampler",
    # Utils
    "create_completer",
    "batch_complete",
    "stream_tokens",
    "stream_messages",
    "create_chat_session",
    "ChatSession",
]