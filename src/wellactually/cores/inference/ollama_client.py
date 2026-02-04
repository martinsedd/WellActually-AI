from typing import Any, AsyncIterator

import httpx
from rich.console import Console

console = Console()


class OllamaClient:
    """
    Manages async communication with local Ollama API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "codellama:7b",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def warmup(self) -> bool:
        """
        Warm up the GPU by sending a no-op prompt to load the model into VRAM.

        Returns:
            True if warmup successful, False otherwise
        """
        console.print("[dim]Warming up GPU...[/dim]")

        try:
            response = await self.generate("ping", max_tokens=1)
            console.print("[dim]GPU ready[/dim]")
            return True
        except Exception as e:
            console.print(f"[bold red]GPU warmup failed:[/bold red] {e}")
            return False

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a completion from Ollama (non-streaming).

        Args:
            prompt: The user prompt
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature322

        Returns:
            Generated text
        """
        url = f"{self.base_url}/api/generate"

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        if system:
            payload["system"] = system

        response = await self.client.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        return result.get("response", "")

    async def generate_stream(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """
        Generate a completion from Ollama with streaming.

        Args:
            prompt: The user prompt
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Yields:
            Token strings as they are generated
        """
        url = f"{self.base_url}/api/generate"

        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        if system:
            payload["system"] = system

        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line:
                    import json

                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done", False):
                        break

    async def close(self) -> None:
        await self.client.aclose()
