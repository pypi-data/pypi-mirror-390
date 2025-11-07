# llm/protocol.py

from enum import StrEnum, auto
from typing import Protocol, TypedDict


class ChatMessage(TypedDict):
    """Represents a single message in a chat conversation.

    The 'role' can be 'user', 'assistant'.
    """

    role: str
    content: str


class LLMProtocol(Protocol):
    """A protocol defining the interface for a Large Language Model."""

    def generate(self, prompt: str) -> str:
        """Generates a text response for a single, stateless prompt.

        Args:
            prompt: The input text to the model.

        Returns:
            The generated text response as a string.
        """

    def chat(self, messages: list[ChatMessage]) -> str:
        """Generates a response for a conversational chat history.

        Args:
            messages: A list of ChatMessage objects representing the conversation history.

        Returns:
            The generated text response from the assistant.
        """

    def set_system_prompt(self, system_prompt: str | None) -> None:
        """Set the system prompt."""


class LLMProvider(StrEnum):
    """An enumeration of the supported LLM providers."""

    GEMMA_3 = auto()
