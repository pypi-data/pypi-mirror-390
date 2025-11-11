"""
Core Message Rendering System
==============================

Handles conversation-to-token conversion with fine-grained control.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Union
from enum import Enum
from abc import ABC, abstractmethod
import torch
from transformers import AutoTokenizer


class ChatFormat(Enum):
    """Supported chat formats."""
    CHATML = "chatml"
    ALPACA = "alpaca"
    VICUNA = "vicuna"
    ZEPHYR = "zephyr"
    LLAMA = "llama"
    MISTRAL = "mistral"
    CUSTOM = "custom"


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0  # Token-level weight for training


@dataclass
class Conversation:
    """Represents a full conversation."""
    messages: List[Message]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content, **kwargs))

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            "messages": [
                {"role": m.role, "content": m.content, "weight": m.weight}
                for m in self.messages
            ],
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        """Create conversation from dictionary."""
        messages = [
            Message(
                role=m["role"],
                content=m["content"],
                weight=m.get("weight", 1.0)
            )
            for m in data["messages"]
        ]
        return cls(messages=messages, metadata=data.get("metadata", {}))


@dataclass
class TokenWeight:
    """Represents token-level weights for training."""
    start_idx: int
    end_idx: int
    weight: float

    def apply_to_tensor(self, tensor: torch.Tensor) -> torch.Tensor:
        """Apply weight to tensor slice."""
        weighted_tensor = tensor.clone()
        weighted_tensor[self.start_idx:self.end_idx] *= self.weight
        return weighted_tensor


@dataclass
class RenderConfig:
    """Configuration for message rendering."""
    format: ChatFormat = ChatFormat.CHATML
    add_generation_prompt: bool = False
    add_special_tokens: bool = True
    truncation: bool = True
    max_length: int = 512
    padding: str = "max_length"
    return_tensors: str = "pt"

    # Token weight settings
    mask_system: bool = False  # Don't train on system messages
    mask_user: bool = False    # Don't train on user messages
    only_assistant: bool = True  # Only train on assistant responses

    # Custom templates (for CUSTOM format)
    system_template: Optional[str] = None
    user_template: Optional[str] = None
    assistant_template: Optional[str] = None
    separator: str = "\n"


class MessageRenderer(ABC):
    """Abstract base class for message rendering."""

    def __init__(self, tokenizer: AutoTokenizer, config: RenderConfig):
        self.tokenizer = tokenizer
        self.config = config

    @abstractmethod
    def render_conversation(self, conversation: Conversation) -> str:
        """Render conversation to string format."""
        pass

    @abstractmethod
    def get_stop_sequences(self) -> List[str]:
        """Get stop sequences for this format."""
        pass

    @abstractmethod
    def parse_response(self, response: str) -> str:
        """Parse model response to extract content."""
        pass

    def build_generation_prompt(self, conversation: Conversation) -> str:
        """Build prompt for generation.

        For generation, we want to include the conversation context but remove
        any trailing assistant messages, then add an empty assistant marker to
        trigger generation.
        """
        # Find last non-assistant message index
        last_non_assistant_idx = -1
        for i, msg in enumerate(conversation.messages):
            if msg.role != "assistant":
                last_non_assistant_idx = i

        # Create conversation with messages up to and including last non-assistant message
        gen_conversation = Conversation(
            messages=conversation.messages[:last_non_assistant_idx + 1] if last_non_assistant_idx >= 0 else [],
            metadata=conversation.metadata
        )

        # Add empty assistant message to trigger generation
        gen_conversation.add_message("assistant", "")

        # Render the conversation - this will end with the assistant marker
        rendered = self.render_conversation(gen_conversation)

        return rendered

    def tokenize_conversation(
        self,
        conversation: Conversation
    ) -> Dict[str, torch.Tensor]:
        """Tokenize conversation with proper formatting."""

        rendered = self.render_conversation(conversation)

        # Tokenize
        encoded = self.tokenizer(
            rendered,
            truncation=self.config.truncation,
            max_length=self.config.max_length,
            padding=self.config.padding,
            return_tensors=self.config.return_tensors,
            add_special_tokens=self.config.add_special_tokens,
        )

        # Add labels for training
        encoded["labels"] = encoded["input_ids"].clone()

        # Apply token weights if configured
        if self.config.only_assistant or self.config.mask_system or self.config.mask_user:
            weights = self._compute_token_weights(conversation, rendered, encoded)
            encoded["token_weights"] = weights

            # Mask labels where weight is 0
            if "labels" in encoded:
                mask = weights == 0
                encoded["labels"][mask] = -100

        return encoded

    def _compute_token_weights(
        self,
        conversation: Conversation,
        rendered_text: str,
        encoded: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """Compute token-level weights based on message roles."""

        # Initialize weights to 1
        weights = torch.ones_like(encoded["input_ids"], dtype=torch.float)

        # Find message boundaries in the rendered text
        current_pos = 0
        for message in conversation.messages:
            # Find where this message starts in the rendered text
            message_rendered = self._render_single_message(message)
            start_pos = rendered_text.find(message_rendered, current_pos)

            if start_pos == -1:
                continue

            end_pos = start_pos + len(message_rendered)

            # Convert character positions to token positions
            # This is approximate - for exact mapping, use tokenizer's offset mapping
            start_tokens = len(self.tokenizer.encode(rendered_text[:start_pos], add_special_tokens=False))
            end_tokens = len(self.tokenizer.encode(rendered_text[:end_pos], add_special_tokens=False))

            # Apply weights based on role and config
            if message.role == "system" and self.config.mask_system:
                weights[0, start_tokens:end_tokens] = 0
            elif message.role == "user" and self.config.mask_user:
                weights[0, start_tokens:end_tokens] = 0
            elif message.role == "assistant":
                if not self.config.only_assistant:
                    weights[0, start_tokens:end_tokens] = message.weight
            else:
                # For only_assistant mode, non-assistant messages get 0 weight
                if self.config.only_assistant:
                    weights[0, start_tokens:end_tokens] = 0

            current_pos = end_pos

        return weights

    @abstractmethod
    def _render_single_message(self, message: Message) -> str:
        """Render a single message (needed for weight computation)."""
        pass

    def build_supervised_example(
        self,
        conversation: Conversation,
        tokenizer: Optional[AutoTokenizer] = None
    ) -> Dict[str, Any]:
        """Build a supervised training example with proper masking."""

        if tokenizer:
            self.tokenizer = tokenizer

        # Tokenize with weights
        encoded = self.tokenize_conversation(conversation)

        # Add additional training information
        encoded["conversation_metadata"] = conversation.metadata

        return encoded


class ChatMLRenderer(MessageRenderer):
    """Renderer for ChatML format."""

    def render_conversation(self, conversation: Conversation) -> str:
        """Render conversation in ChatML format."""
        rendered = []

        for message in conversation.messages:
            rendered.append(self._render_single_message(message))

        return self.config.separator.join(rendered)

    def _render_single_message(self, message: Message) -> str:
        """Render a single message in ChatML format."""
        if message.content:
            return f"<|im_start|>{message.role}\n{message.content}<|im_end|>"
        else:
            # For generation prompts
            return f"<|im_start|>{message.role}\n"

    def get_stop_sequences(self) -> List[str]:
        """Get ChatML stop sequences."""
        return ["<|im_end|>", "<|im_start|>"]

    def parse_response(self, response: str) -> str:
        """Parse ChatML response."""
        # Remove special tokens
        response = response.replace("<|im_end|>", "")
        response = response.replace("<|im_start|>", "")

        # Extract content after role marker
        if "\n" in response:
            response = response.split("\n", 1)[1]

        return response.strip()


class AlpacaRenderer(MessageRenderer):
    """Renderer for Alpaca format."""

    def render_conversation(self, conversation: Conversation) -> str:
        """Render conversation in Alpaca format."""
        rendered = []

        # Extract system message if present
        system_msg = None
        messages = []
        for msg in conversation.messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                messages.append(msg)

        # Build instruction from system + user messages
        for i in range(0, len(messages), 2):
            if i < len(messages):
                user_msg = messages[i]
                instruction = user_msg.content

                if system_msg:
                    instruction = f"{system_msg}\n\n{instruction}"

                # Add response if present
                if i + 1 < len(messages):
                    assistant_msg = messages[i + 1]
                    rendered.append(
                        f"### Instruction:\n{instruction}\n\n"
                        f"### Response:\n{assistant_msg.content}"
                    )
                else:
                    # For generation
                    rendered.append(
                        f"### Instruction:\n{instruction}\n\n"
                        f"### Response:\n"
                    )

        return self.config.separator.join(rendered)

    def _render_single_message(self, message: Message) -> str:
        """Render single message in Alpaca format."""
        if message.role == "user":
            return f"### Instruction:\n{message.content}"
        elif message.role == "assistant":
            return f"### Response:\n{message.content}"
        else:
            return message.content

    def get_stop_sequences(self) -> List[str]:
        """Get Alpaca stop sequences."""
        return ["### Instruction:", "###", "\n\n\n"]

    def parse_response(self, response: str) -> str:
        """Parse Alpaca response."""
        # Remove format markers
        response = response.replace("### Response:", "")
        response = response.replace("### Instruction:", "")

        # Take content before next instruction
        if "###" in response:
            response = response.split("###")[0]

        return response.strip()


class CustomRenderer(MessageRenderer):
    """Renderer with custom templates."""

    def render_conversation(self, conversation: Conversation) -> str:
        """Render conversation with custom templates."""
        rendered = []

        for message in conversation.messages:
            rendered.append(self._render_single_message(message))

        return self.config.separator.join(rendered)

    def _render_single_message(self, message: Message) -> str:
        """Render message with custom template."""
        if message.role == "system" and self.config.system_template:
            return self.config.system_template.format(content=message.content)
        elif message.role == "user" and self.config.user_template:
            return self.config.user_template.format(content=message.content)
        elif message.role == "assistant" and self.config.assistant_template:
            return self.config.assistant_template.format(content=message.content)
        else:
            return message.content

    def get_stop_sequences(self) -> List[str]:
        """Get custom stop sequences."""
        # Extract prefixes from templates as stop sequences
        stops = []

        if self.config.user_template:
            # Extract prefix before {content}
            prefix = self.config.user_template.split("{content}")[0]
            if prefix:
                stops.append(prefix)

        return stops

    def parse_response(self, response: str) -> str:
        """Parse custom response."""
        # Remove template markers if present
        for stop in self.get_stop_sequences():
            response = response.replace(stop, "")

        return response.strip()


# Import renderers from formats module
from .formats import VicunaRenderer, ZephyrRenderer, LlamaRenderer, MistralRenderer

# Registry of available renderers
RENDERER_REGISTRY = {
    ChatFormat.CHATML: ChatMLRenderer,
    ChatFormat.ALPACA: AlpacaRenderer,
    ChatFormat.VICUNA: VicunaRenderer,
    ChatFormat.ZEPHYR: ZephyrRenderer,
    ChatFormat.LLAMA: LlamaRenderer,
    ChatFormat.MISTRAL: MistralRenderer,
    ChatFormat.CUSTOM: CustomRenderer,
}


def get_renderer(
    format: Union[ChatFormat, str],
    tokenizer: AutoTokenizer,
    config: Optional[RenderConfig] = None
) -> MessageRenderer:
    """Get a message renderer for the specified format."""

    if isinstance(format, str):
        format = ChatFormat(format)

    if config is None:
        config = RenderConfig(format=format)
    else:
        config.format = format

    renderer_class = RENDERER_REGISTRY.get(format)
    if renderer_class is None:
        raise ValueError(f"Unknown chat format: {format}")

    return renderer_class(tokenizer, config)