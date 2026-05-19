"""
Kognitiv Core Python SDK

Easy client library for institutions to integrate Kognitiv API.

Usage:
    from kognitiv import Kognitiv

    client = Kognitiv(api_key="sk_edu_xxxxx")
    response = client.chat("Explain machine learning")
    print(response.choices[0].text)
"""

import asyncio
from typing import Any, Dict, List, Optional
import httpx
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Choice:
    """Response choice from API."""
    text: str
    index: int
    finish_reason: Optional[str] = None


@dataclass
class Usage:
    """Token usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ChatResponse:
    """Response from chat/completions endpoint."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage
    organization: Optional[str] = None

    @property
    def text(self) -> str:
        """Get the first choice text."""
        return self.choices[0].text if self.choices else ""


@dataclass
class AnalysisResponse:
    """Response from analyze endpoint."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Usage


@dataclass
class UsageStats:
    """Organization usage statistics."""
    quota_used: int
    quota_remaining: int
    quota_limit: int
    percent_used: float
    reset_date: str
    tier: str


class KognitivError(Exception):
    """Base exception for Kognitiv errors."""
    pass


class AuthenticationError(KognitivError):
    """Authentication failed."""
    pass


class QuotaExceededError(KognitivError):
    """Monthly quota exceeded."""
    pass


class RateLimitError(KognitivError):
    """Rate limit exceeded."""
    pass


class Kognitiv:
    """
    Kognitiv Core API Client.

    Args:
        api_key: Your Kognitiv API key (starts with sk_edu_ or sk_enterprise_)
        base_url: API base URL (default: https://api.kognitiv.ai)
        timeout: Request timeout in seconds (default: 30)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.kognitivcore.api",
        timeout: float = 30.0,
    ):
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    # ====================================================================
    # CHAT/COMPLETIONS
    # ====================================================================

    def chat(
        self,
        query: str,
        model: str = "kognitiv-core-v2.7",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
    ) -> ChatResponse:
        """
        Send a question to Kognitiv and get an answer.

        Args:
            query: The question or prompt
            model: Model to use (default: kognitiv-core-v2.7)
            temperature: Creativity (0.0-2.0, default: 0.7)
            max_tokens: Maximum response length
            top_p: Nucleus sampling (0.0-1.0, default: 1.0)

        Returns:
            ChatResponse with answer

        Raises:
            AuthenticationError: Invalid API key
            QuotaExceededError: Monthly quota exceeded
            RateLimitError: Rate limit exceeded
            KognitivError: Other API errors
        """
        payload = {
            "query": query,
            "model": model,
            "temperature": temperature,
            "top_p": top_p,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        response = self._post("/v1/chat/completions", payload)
        return self._parse_chat_response(response)

    def chat_stream(
        self,
        query: str,
        model: str = "kognitiv-core-v2.7",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """
        Stream response from chat (yields text chunks).

        Usage:
            for chunk in client.chat_stream("What is AI?"):
                print(chunk, end="", flush=True)
        """
        payload = {
            "query": query,
            "model": model,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        with self._client.stream("POST", f"{self.base_url}/v1/chat/completions", json=payload) as r:
            self._check_response(r)
            for line in r.iter_lines():
                if line.startswith("data:"):
                    data = line[5:].strip()
                    if data and data != "[DONE]":
                        try:
                            import json
                            chunk = json.loads(data)
                            if "choices" in chunk and chunk["choices"]:
                                text = chunk["choices"][0].get("text", "")
                                if text:
                                    yield text
                        except:
                            pass

    # ====================================================================
    # DATA ANALYSIS
    # ====================================================================

    def analyze(
        self,
        data: List[float],
        column_name: str = "data",
        analysis_type: str = "full",
    ) -> AnalysisResponse:
        """
        Analyze numeric data using ML.

        Args:
            data: List of numeric values
            column_name: Label for the data (default: "data")
            analysis_type: Type of analysis ("full", "statistical", "trends", "forecast")

        Returns:
            AnalysisResponse with insights

        Raises:
            KognitivError: Analysis failed
        """
        if not data:
            raise ValueError("data cannot be empty")

        payload = {
            "data": data,
            "column_name": column_name,
            "analysis_type": analysis_type,
        }

        response = self._post("/v1/analyze", payload)
        return self._parse_analysis_response(response)

    # ====================================================================
    # WORKFLOWS
    # ====================================================================

    def workflow(
        self,
        query: str,
        model: str = "kognitiv-core-v2.7",
        context: Optional[Dict[str, Any]] = None,
    ) -> ChatResponse:
        """
        Execute a multi-agent workflow.

        Args:
            query: Workflow query
            model: Model to use
            context: Additional context

        Returns:
            ChatResponse with workflow result
        """
        payload = {
            "query": query,
            "model": model,
        }
        if context:
            payload["context"] = context

        response = self._post("/v1/workflows", payload)
        return self._parse_chat_response(response)

    # ====================================================================
    # MONITORING
    # ====================================================================

    def usage(self) -> UsageStats:
        """
        Get current organization usage stats.

        Returns:
            UsageStats with quota information
        """
        response = self._get("/v1/organizations/usage")

        return UsageStats(
            quota_used=response.get("quota_used", 0),
            quota_remaining=response.get("quota_remaining", 0),
            quota_limit=response.get("quota_limit", 0),
            percent_used=response.get("quota_pct", 0),
            reset_date=response.get("quota_reset_date", ""),
            tier=response.get("tier", ""),
        )

    def models(self) -> List[str]:
        """
        Get available models.

        Returns:
            List of model names
        """
        response = self._get("/v1/models")
        return response.get("models", [])

    def health(self) -> Dict[str, Any]:
        """
        Check API health (no auth required).

        Returns:
            Health status
        """
        with httpx.Client() as client:
            r = client.get(f"{self.base_url}/v1/health", timeout=self.timeout)
            r.raise_for_status()
            return r.json()

    # ====================================================================
    # ASYNC SUPPORT
    # ====================================================================

    async def chat_async(
        self,
        query: str,
        model: str = "kognitiv-core-v2.7",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ChatResponse:
        """Async version of chat()."""
        payload = {
            "query": query,
            "model": model,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
        ) as client:
            r = await client.post(f"{self.base_url}/v1/chat/completions", json=payload)
            self._check_response(r)
            return self._parse_chat_response(r.json())

    async def analyze_async(
        self,
        data: List[float],
        column_name: str = "data",
        analysis_type: str = "full",
    ) -> AnalysisResponse:
        """Async version of analyze()."""
        if not data:
            raise ValueError("data cannot be empty")

        payload = {
            "data": data,
            "column_name": column_name,
            "analysis_type": analysis_type,
        }

        async with httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
        ) as client:
            r = await client.post(f"{self.base_url}/v1/analyze", json=payload)
            self._check_response(r)
            return self._parse_analysis_response(r.json())

    # ====================================================================
    # PRIVATE METHODS
    # ====================================================================

    def _get(self, path: str) -> Dict[str, Any]:
        """Make GET request."""
        r = self._client.get(f"{self.base_url}{path}")
        self._check_response(r)
        return r.json()

    def _post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request."""
        r = self._client.post(f"{self.base_url}{path}", json=data)
        self._check_response(r)
        return r.json()

    def _check_response(self, response: httpx.Response) -> None:
        """Check response for errors."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key or expired token")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded or quota exceeded")
        elif response.status_code == 403:
            raise QuotaExceededError("Monthly quota exceeded")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                raise KognitivError(f"API Error: {error_data.get('detail', 'Unknown error')}")
            except:
                raise KognitivError(f"API Error: {response.status_code} {response.text}")

    @staticmethod
    def _parse_chat_response(data: Dict[str, Any]) -> ChatResponse:
        """Parse chat response."""
        choices = [
            Choice(text=c.get("text", ""), index=c.get("index", 0))
            for c in data.get("choices", [])
        ]
        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
        return ChatResponse(
            id=data.get("id", ""),
            object=data.get("object", ""),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=choices,
            usage=usage,
            organization=data.get("organization"),
        )

    @staticmethod
    def _parse_analysis_response(data: Dict[str, Any]) -> AnalysisResponse:
        """Parse analysis response."""
        usage_data = data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
        return AnalysisResponse(
            id=data.get("id", ""),
            object=data.get("object", ""),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=data.get("choices", []),
            usage=usage,
        )


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================

def quick_chat(api_key: str, query: str) -> str:
    """Quick chat without creating client."""
    with Kognitiv(api_key=api_key) as client:
        response = client.chat(query)
        return response.text


async def quick_chat_async(api_key: str, query: str) -> str:
    """Async quick chat."""
    client = Kognitiv(api_key=api_key)
    try:
        response = await client.chat_async(query)
        return response.text
    finally:
        client.close()


if __name__ == "__main__":
    # Example usage
    import os

    api_key = os.getenv("KOGNITIV_API_KEY")
    if not api_key:
        print("Set KOGNITIV_API_KEY environment variable")
        exit(1)

    # Sync example
    with Kognitiv(api_key=api_key) as client:
        print("Asking Kognitiv a question...")
        response = client.chat("What is Python?")
        print(f"Answer: {response.text}")

        print("\nGetting usage stats...")
        stats = client.usage()
        print(f"Quota used: {stats.quota_used}/{stats.quota_limit}")

    # Async example
    async def async_example():
        client = Kognitiv(api_key=api_key)
        try:
            response = await client.chat_async("Explain machine learning in 100 words")
            print(f"\nAsync answer: {response.text}")
        finally:
            client.close()

    asyncio.run(async_example())
