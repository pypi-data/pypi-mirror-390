"""
Utility functions for generation/completion
============================================

Helper functions for creating and using completers.
"""

from typing import Union, List, Dict, Any, Optional, Iterator, AsyncIterator
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import asyncio

from .completers import (
    TokenCompleter,
    MessageCompleter,
    AsyncTokenCompleter,
    AsyncMessageCompleter,
    CompletionConfig,
    TokenCompletionResult,
    MessageCompletionResult,
)
from .sampling import SamplingConfig, create_sampler
from autotrain.rendering import ChatFormat, Conversation, Message
from autotrain.utils import get_model_loading_kwargs, maybe_move_to_mps


def create_completer(
    model: Union[str, AutoModelForCausalLM],
    tokenizer: Union[str, AutoTokenizer, None] = None,
    completer_type: str = "message",
    config: Optional[CompletionConfig] = None,
    chat_format: Optional[ChatFormat] = None,
    async_mode: bool = False,
) -> Union[TokenCompleter, MessageCompleter, AsyncTokenCompleter, AsyncMessageCompleter]:
    """
    Create a completer instance.

    Args:
        model: Model name or instance
        tokenizer: Tokenizer name or instance
        completer_type: "token" or "message"
        config: Completion configuration
        chat_format: Chat format for message completer
        async_mode: Whether to create async version

    Returns:
        Completer instance
    """
    # Load model if string
    if isinstance(model, str):
        model_kwargs = get_model_loading_kwargs(trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(model, **model_kwargs)
        model = maybe_move_to_mps(model, model_kwargs)

    # Load tokenizer if needed
    if tokenizer is None:
        if hasattr(model, "config") and hasattr(model.config, "name_or_path"):
            tokenizer = AutoTokenizer.from_pretrained(model.config.name_or_path)
        else:
            raise ValueError("Tokenizer must be provided if model doesn't have name_or_path")
    elif isinstance(tokenizer, str):
        tokenizer = AutoTokenizer.from_pretrained(tokenizer)

    # Set padding token if needed
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Create config if not provided
    if config is None:
        config = CompletionConfig()

    # Create completer
    if completer_type == "token":
        if async_mode:
            return AsyncTokenCompleter(model, tokenizer, config)
        else:
            return TokenCompleter(model, tokenizer, config)
    elif completer_type == "message":
        if async_mode:
            return AsyncMessageCompleter(model, tokenizer, config, chat_format)
        else:
            return MessageCompleter(model, tokenizer, config, chat_format)
    else:
        raise ValueError(f"Unknown completer type: {completer_type}")


def batch_complete(
    completer: Union[TokenCompleter, MessageCompleter],
    prompts: List[Any],
    batch_size: int = 8,
    show_progress: bool = True,
    **kwargs
) -> List[Union[TokenCompletionResult, MessageCompletionResult]]:
    """
    Complete multiple prompts in batches.

    Args:
        completer: Completer to use
        prompts: List of prompts
        batch_size: Batch size for processing
        show_progress: Whether to show progress bar

    Returns:
        List of completion results
    """
    results = []

    if show_progress:
        from tqdm import tqdm
        iterator = tqdm(range(0, len(prompts), batch_size), desc="Completing")
    else:
        iterator = range(0, len(prompts), batch_size)

    for i in iterator:
        batch = prompts[i:i + batch_size]
        batch_results = completer.batch_complete(batch, **kwargs)
        results.extend(batch_results)

    return results


def stream_tokens(
    completer: TokenCompleter,
    prompt: Union[str, torch.Tensor],
    callback: Optional[Any] = None,
    **kwargs
) -> Iterator[torch.Tensor]:
    """
    Stream tokens with optional callback.

    Args:
        completer: Token completer
        prompt: Input prompt
        callback: Optional callback function for each token

    Yields:
        Token IDs
    """
    for token in completer.stream_tokens(prompt, **kwargs):
        if callback:
            callback(token)
        yield token


def stream_messages(
    completer: MessageCompleter,
    conversation: Union[Conversation, List[Dict[str, str]]],
    callback: Optional[Any] = None,
    **kwargs
) -> Iterator[str]:
    """
    Stream message content as it's generated.

    This is a simplified version that generates the full message
    then yields it character by character for display.

    Args:
        completer: Message completer
        conversation: Conversation
        callback: Optional callback

    Yields:
        Message content chunks
    """
    # Generate full message
    result = completer.complete(conversation, **kwargs)
    content = result.content

    # Stream character by character
    for char in content:
        if callback:
            callback(char)
        yield char


async def async_batch_complete(
    completer: Union[AsyncTokenCompleter, AsyncMessageCompleter],
    prompts: List[Any],
    max_concurrent: int = 10,
    **kwargs
) -> List[Union[TokenCompletionResult, MessageCompletionResult]]:
    """
    Async batch completion with concurrency limit.

    Args:
        completer: Async completer
        prompts: List of prompts
        max_concurrent: Maximum concurrent completions

    Returns:
        List of results
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def complete_with_semaphore(prompt):
        async with semaphore:
            return await completer.complete_async(prompt, **kwargs)

    tasks = [complete_with_semaphore(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)

    return results


def create_chat_session(
    model: Union[str, AutoModelForCausalLM],
    tokenizer: Union[str, AutoTokenizer, None] = None,
    system_prompt: Optional[str] = None,
    chat_format: ChatFormat = ChatFormat.CHATML,
    config: Optional[CompletionConfig] = None,
) -> "ChatSession":
    """
    Create an interactive chat session.

    Args:
        model: Model to use
        tokenizer: Tokenizer
        system_prompt: System prompt
        chat_format: Chat format
        config: Completion config

    Returns:
        ChatSession instance
    """
    completer = create_completer(
        model=model,
        tokenizer=tokenizer,
        completer_type="message",
        config=config,
        chat_format=chat_format,
    )

    return ChatSession(completer, system_prompt)


class ChatSession:
    """Interactive chat session."""

    def __init__(
        self,
        completer: MessageCompleter,
        system_prompt: Optional[str] = None,
    ):
        self.completer = completer
        self.conversation = Conversation(messages=[])

        if system_prompt:
            self.conversation.add_message("system", system_prompt)

    def chat(self, user_input: str, **kwargs) -> str:
        """
        Send a message and get response.

        Args:
            user_input: User message

        Returns:
            Assistant response
        """
        result = self.completer.chat(
            user_input,
            conversation=self.conversation,
            **kwargs
        )

        # Update conversation
        self.conversation = result.conversation

        return result.content

    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation.messages
        ]

    def clear_history(self, keep_system: bool = True):
        """Clear conversation history."""
        if keep_system:
            system_msgs = [m for m in self.conversation.messages if m.role == "system"]
            self.conversation = Conversation(messages=system_msgs)
        else:
            self.conversation = Conversation(messages=[])

    def save_history(self, filepath: str):
        """Save conversation to file."""
        import json
        with open(filepath, "w") as f:
            json.dump(self.conversation.to_dict(), f, indent=2)

    def load_history(self, filepath: str):
        """Load conversation from file."""
        import json
        with open(filepath, "r") as f:
            data = json.load(f)
        self.conversation = Conversation.from_dict(data)
