"""
Ollama provider for local LLM inference.

Integrates with Ollama for running LLMs locally.
"""

import logging
from typing import Any

from neurobus.llm.connector import LLMConnector, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class OllamaConnector(LLMConnector):
    """
    Ollama LLM connector.

    Connects to Ollama for local LLM inference.

    Example:
        >>> connector = OllamaConnector(
        ...     base_url="http://localhost:11434",
        ...     model="llama2"
        ... )
        >>> response = await connector.generate("Hello!")
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        **kwargs: Any,
    ):
        """
        Initialize Ollama connector.

        Args:
            base_url: Ollama server URL
            model: Model name (llama2, mistral, codellama, etc.)
            **kwargs: Base connector parameters
        """
        super().__init__(model=model, **kwargs)
        self.base_url = base_url
        self._client: Any = None

    async def _ensure_client(self) -> None:
        """Ensure Ollama client is initialized."""
        if self._client is None:
            try:
                import httpx

                self._client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=60.0,
                )
                logger.info(f"Ollama client initialized (url={self.base_url})")

            except ImportError:
                raise ImportError("httpx not installed. " "Install with: pip install httpx")

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate completion using Ollama."""
        await self._ensure_client()
        self._stats["requests"] += 1

        try:
            # Build request
            request_data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
            }

            if system_prompt:
                request_data["system"] = system_prompt

            # Add any additional options
            if kwargs:
                request_data["options"].update(kwargs)

            # Make request
            response = await self._client.post(
                "/api/generate",
                json=request_data,
            )
            response.raise_for_status()

            # Parse response
            result = response.json()
            content = result.get("response", "")

            # Ollama doesn't provide exact token counts in the same way
            # Estimate based on content length
            tokens = len(content.split()) + len(prompt.split())
            self._stats["tokens_used"] += tokens

            return LLMResponse(
                content=content,
                provider="ollama",
                model=self.model,
                tokens_used=tokens,
                metadata={
                    "done": result.get("done", True),
                    "context": result.get("context", []),
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "eval_count": result.get("eval_count", 0),
                },
            )

        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Ollama generation error: {e}", exc_info=True)
            raise

    async def chat(
        self,
        messages: list[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Chat completion using Ollama."""
        await self._ensure_client()
        self._stats["requests"] += 1

        try:
            # Convert messages to Ollama format
            ollama_messages = []
            for msg in messages:
                ollama_messages.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                    }
                )

            # Build request
            request_data = {
                "model": self.model,
                "messages": ollama_messages,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                },
            }

            # Add any additional options
            if kwargs:
                request_data["options"].update(kwargs)

            # Make request
            response = await self._client.post(
                "/api/chat",
                json=request_data,
            )
            response.raise_for_status()

            # Parse response
            result = response.json()
            content = result.get("message", {}).get("content", "")

            # Estimate token usage
            tokens = len(content.split())
            for msg in messages:
                tokens += len(msg.content.split())

            self._stats["tokens_used"] += tokens

            return LLMResponse(
                content=content,
                provider="ollama",
                model=self.model,
                tokens_used=tokens,
                metadata={
                    "done": result.get("done", True),
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "eval_count": result.get("eval_count", 0),
                },
            )

        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Ollama chat error: {e}", exc_info=True)
            raise

    async def close(self) -> None:
        """Close Ollama client."""
        if self._client:
            await self._client.aclose()
            self._client = None

        logger.info("Ollama connector closed")
