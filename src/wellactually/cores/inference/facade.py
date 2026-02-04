"""
Inference facade - High-level API for LLM operations.
"""

from typing import AsyncIterator

from wellactually.cores.inference.ollama_client import OllamaClient


class InferenceFacade:
    """
    High-level facade for LLM inference operations.

    Orchestrator interacts with this class without needing to know about Ollama warmpup,
    streaming protocols, or connection management.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "codellama:7b",
        timeout: float = 120.0,
    ) -> None:
        self.client = OllamaClient(base_url, model, timeout)
        self._initialized = False

    async def initialize(self) -> bool:
        """
        Initialize the inference engine with GPU warmup.

        Returns:
            True if initialization successful, False otherwise
        """
        if self._initialized:
            return True

        success = await self.client.warmup()
        self._initialized = success
        return success

    async def analyze_code(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        """
        Analyze code and generate feedback.

        Args:
            prompt: The analysis prompt
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response

        Returns:
            Generated feedback (string if not streaming, AsyncIterator if streaming)
        """
        if not self._initialized:
            raise RuntimeError("InferenceFacade not initialized. Call initialize() first")

        if stream:
            return self.client.generate_stream(prompt, system, max_tokens, temperature)
        else:
            return await self.client.generate(prompt, system, max_tokens, temperature)

    async def close(self) -> None:
        await self.client.close()
        self._initialized = False
