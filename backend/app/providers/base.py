"""Provider-agnostic AI interface (ARCHITECTURE.md, Section 5).

This module defines the contract every AI provider (Ollama, OpenAI,
Claude, Gemini, ...) must satisfy. No business logic anywhere in the
application should ever import a specific provider directly — only
this abstraction. That is the entire point of "Provider Agnostic" as
a stated project principle: swapping providers is a configuration
change (which concrete class `ProviderFactory` resolves to), never a
code change in any service that consumes `AIProvider`.

The interface is deliberately minimal (`generate`, `chat` only, no
embeddings yet) per YAGNI — it grows only when a real feature needs a
new capability, not speculatively.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

class ProviderError(Exception):
    """Base exception for all AI provider-related failures.

    Every exception raised by a provider implementation (or by code
    that resolves/uses one, such as `ProviderFactory`) should inherit
    from this, so calling code can catch `ProviderError` once rather
    than needing to know about every provider's own exception types.
    """


class ProviderGenerationError(ProviderError):
    """Raised when a provider fails to produce a response.

    Covers failures during `generate()` or `chat()` specifically — as
    opposed to configuration/setup failures, which providers should
    raise as a more specific `ProviderError` subclass if one is ever
    needed (none is, yet, per YAGNI).
    """


class MessageRole(str, Enum):
    """Who authored a given message in a chat conversation.

    A small, closed set shared by every provider's `chat()` — using an
    enum here (rather than a bare string) means a typo like `"asistant"`
    is caught by type checking, not by a provider silently misbehaving
    at request time.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True)
class ChatMessage:
    """A single message in a chat conversation.

    Frozen (immutable) because a conversation history is a record of
    what was said, not a mutable object callers should be able to edit
    in place after constructing it.

    Attributes:
        role: Who authored this message (system, user, or assistant).
        content: The message text.
    """

    role: MessageRole
    content: str


class AIProvider(ABC):
    """Abstract base class every AI provider implementation must satisfy.

    This class defines *what* an AI provider can do (generate text,
    hold a conversation), never *how* — no method here may assume a
    specific vendor's request/response shape, authentication scheme,
    or model-naming convention. Provider-specific configuration (API
    keys, model names, endpoints, sampling parameters a particular
    vendor supports) belongs in each concrete provider's own
    `__init__`, not in this interface.

    Both methods are `async` because every real provider implementation
    will involve network I/O (even a local Ollama call goes over HTTP),
    and the interface should not force a synchronous shape onto
    implementations that are fundamentally asynchronous.
    """

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a single text completion for a prompt.

        This is the simplest possible AI operation: one prompt in, one
        piece of generated text out — no conversation history, no
        role-tracking. Used for single-shot tasks (e.g. disambiguating
        a dictionary sense, per ARCHITECTURE.md Section 7's Japanese
        pipeline) where a full chat exchange would be overkill.

        Args:
            prompt: The input text to generate a completion for. Must
                be a non-empty string; implementations should reject
                blank/whitespace-only prompts rather than silently
                returning an empty or meaningless response.
            **kwargs: Provider-specific tuning parameters (e.g.
                temperature, max tokens, model override). Deliberately
                not named parameters on this interface — see the
                module docstring: naming a parameter here would bake
                one provider's concept of "tuning" into a supposedly
                provider-agnostic contract. Implementations should
                document which kwargs they actually support.

        Returns:
            The generated text completion.

        Raises:
            ProviderGenerationError: If the provider fails to produce
                a response (network failure, upstream API error, or
                any other failure during generation).
            ValueError: If `prompt` is empty or not a valid string.
        """
        raise NotImplementedError

    @abstractmethod
    async def chat(self, messages: list[ChatMessage], **kwargs: Any) -> str:
        """Continue a conversation and return the assistant's reply.

        Unlike `generate()`, this method is conversation-aware: it
        receives the full message history (system/user/assistant turns
        so far) and returns only the next assistant reply as plain
        text — the caller is responsible for appending that reply back
        onto the history if the conversation continues, keeping this
        interface stateless (no provider implementation should need to
        remember previous calls).

        Args:
            messages: The conversation so far, oldest first. Must
                contain at least one message; implementations should
                reject an empty history rather than guessing at a
                reply with no context.
            **kwargs: Provider-specific tuning parameters, as in
                `generate()`.

        Returns:
            The assistant's reply, as plain text.

        Raises:
            ProviderGenerationError: If the provider fails to produce
                a response.
            ValueError: If `messages` is empty.
        """

        raise NotImplementedError
__all__ = [
    "AIProvider",
    "ChatMessage",
    "MessageRole",
    "ProviderError",
    "ProviderGenerationError",
]