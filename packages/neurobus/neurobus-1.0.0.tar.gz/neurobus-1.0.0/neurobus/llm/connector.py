"""
LLM connector interface and base implementations.

Provides abstraction for different LLM providers (OpenAI, Anthropic, etc.).
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"  # For testing


@dataclass
class LLMMessage:
    """
    A single message in LLM conversation.

    Attributes:
        role: Message role (system, user, assistant)
        content: Message content
    """

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """
    Response from LLM.

    Attributes:
        content: Response text
        provider: Provider name
        model: Model name
        tokens_used: Token count
        metadata: Additional response metadata
    """

    content: str
    provider: str
    model: str
    tokens_used: int = 0
    metadata: dict[str, Any] | None = None


class LLMConnector(ABC):
    """
    Abstract base class for LLM connectors.

    Provides interface for different LLM providers with consistent API.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> None:
        """
        Initialize LLM connector.

        Args:
            api_key: API key for the provider
            model: Model identifier
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Statistics
        self._stats = {
            "requests": 0,
            "tokens_used": 0,
            "errors": 0,
        }

        logger.info(f"{self.__class__.__name__} initialized (model={model})")

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate completion from prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific parameters

        Returns:
            LLM response
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: list[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Chat completion with message history.

        Args:
            messages: List of messages
            **kwargs: Additional provider-specific parameters

        Returns:
            LLM response
        """
        pass

    def get_stats(self) -> dict[str, Any]:
        """Get connector statistics."""
        return {
            "provider": self.__class__.__name__,
            "model": self.model,
            "requests": self._stats["requests"],
            "tokens_used": self._stats["tokens_used"],
            "errors": self._stats["errors"],
        }

    def reset_stats(self) -> None:
        """Reset statistics."""
        self._stats = {
            "requests": 0,
            "tokens_used": 0,
            "errors": 0,
        }


class MockLLMConnector(LLMConnector):
    """
    Mock LLM connector for testing.

    Returns predefined responses without calling actual LLM APIs.
    """

    def __init__(
        self,
        responses: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize mock connector.

        Args:
            responses: List of mock responses (cycles through)
            **kwargs: Base connector parameters
        """
        # Set default model if not provided
        if "model" not in kwargs:
            kwargs["model"] = "mock-model"
        super().__init__(**kwargs)
        self.responses = responses or ["This is a mock response."]
        self._response_index = 0

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate mock response."""
        self._stats["requests"] += 1

        # Cycle through responses
        response_text = self.responses[self._response_index % len(self.responses)]
        self._response_index += 1

        # Simulate token usage
        tokens = len(prompt.split()) + len(response_text.split())
        self._stats["tokens_used"] += tokens

        return LLMResponse(
            content=response_text,
            provider="mock",
            model=self.model or "mock-model",
            tokens_used=tokens,
            metadata={"prompt_length": len(prompt)},
        )

    async def chat(
        self,
        messages: list[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate mock chat response."""
        # Convert messages to prompt
        prompt = "\n".join(f"{m.role}: {m.content}" for m in messages)
        return await self.generate(prompt, **kwargs)


class OpenAIConnector(LLMConnector):
    """
    OpenAI LLM connector.

    Connects to OpenAI API (GPT-3.5, GPT-4, etc.).
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-3.5-turbo",
        **kwargs: Any,
    ) -> None:
        """
        Initialize OpenAI connector.

        Args:
            api_key: OpenAI API key
            model: Model name (gpt-3.5-turbo, gpt-4, etc.)
            **kwargs: Base connector parameters
        """
        super().__init__(api_key=api_key, model=model, **kwargs)
        self._client: Any = None

    async def _ensure_client(self) -> None:
        """Ensure OpenAI client is initialized."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized")

            except ImportError:
                raise ImportError(
                    "openai package not installed. " "Install with: pip install openai"
                )

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate completion using OpenAI."""
        await self._ensure_client()
        self._stats["requests"] += 1

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )

            content = response.choices[0].message.content
            tokens = response.usage.total_tokens
            self._stats["tokens_used"] += tokens

            return LLMResponse(
                content=content,
                provider="openai",
                model=self.model,
                tokens_used=tokens,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                },
            )

        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"OpenAI generation error: {e}", exc_info=True)
            raise

    async def chat(
        self,
        messages: list[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Chat completion using OpenAI."""
        await self._ensure_client()
        self._stats["requests"] += 1

        try:
            # Convert to OpenAI format
            openai_messages = [{"role": m.role, "content": m.content} for m in messages]

            response = await self._client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )

            content = response.choices[0].message.content
            tokens = response.usage.total_tokens
            self._stats["tokens_used"] += tokens

            return LLMResponse(
                content=content,
                provider="openai",
                model=self.model,
                tokens_used=tokens,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                },
            )

        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"OpenAI chat error: {e}", exc_info=True)
            raise


class AnthropicConnector(LLMConnector):
    """
    Anthropic LLM connector.

    Connects to Anthropic API (Claude).
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-3-sonnet-20240229",
        **kwargs: Any,
    ) -> None:
        """
        Initialize Anthropic connector.

        Args:
            api_key: Anthropic API key
            model: Model name (claude-3-sonnet, claude-3-opus, etc.)
            **kwargs: Base connector parameters
        """
        super().__init__(api_key=api_key, model=model, **kwargs)
        self._client: Any = None

    async def _ensure_client(self) -> None:
        """Ensure Anthropic client is initialized."""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic

                self._client = AsyncAnthropic(api_key=self.api_key)
                logger.info("Anthropic client initialized")

            except ImportError:
                raise ImportError(
                    "anthropic package not installed. " "Install with: pip install anthropic"
                )

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate completion using Anthropic."""
        await self._ensure_client()
        self._stats["requests"] += 1

        try:
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt if system_prompt else "You are a helpful assistant.",
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            content = response.content[0].text
            tokens = response.usage.input_tokens + response.usage.output_tokens
            self._stats["tokens_used"] += tokens

            return LLMResponse(
                content=content,
                provider="anthropic",
                model=self.model,
                tokens_used=tokens,
                metadata={
                    "stop_reason": response.stop_reason,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            )

        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Anthropic generation error: {e}", exc_info=True)
            raise

    async def chat(
        self,
        messages: list[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Chat completion using Anthropic."""
        await self._ensure_client()
        self._stats["requests"] += 1

        try:
            # Extract system message if present
            system_prompt = None
            anthropic_messages = []

            for msg in messages:
                if msg.role == "system":
                    system_prompt = msg.content
                else:
                    anthropic_messages.append({"role": msg.role, "content": msg.content})

            response = await self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt if system_prompt else "You are a helpful assistant.",
                messages=anthropic_messages,
                **kwargs,
            )

            content = response.content[0].text
            tokens = response.usage.input_tokens + response.usage.output_tokens
            self._stats["tokens_used"] += tokens

            return LLMResponse(
                content=content,
                provider="anthropic",
                model=self.model,
                tokens_used=tokens,
                metadata={
                    "stop_reason": response.stop_reason,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            )

        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Anthropic chat error: {e}", exc_info=True)
            raise


def create_connector(
    provider: LLMProvider | str,
    api_key: str | None = None,
    model: str | None = None,
    **kwargs: Any,
) -> LLMConnector:
    """
    Factory function to create LLM connector.

    Args:
        provider: Provider name (openai, anthropic, mock)
        api_key: API key for the provider
        model: Model identifier
        **kwargs: Additional connector parameters

    Returns:
        LLM connector instance

    Example:
        >>> connector = create_connector("openai", api_key="sk-...")
        >>> response = await connector.generate("Hello!")
    """
    provider_str = provider.value if isinstance(provider, LLMProvider) else provider

    if provider_str == LLMProvider.OPENAI:
        return OpenAIConnector(api_key=api_key, model=model, **kwargs)
    elif provider_str == LLMProvider.ANTHROPIC:
        return AnthropicConnector(api_key=api_key, model=model, **kwargs)
    elif provider_str == LLMProvider.MOCK:
        return MockLLMConnector(model=model, **kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider_str}")
