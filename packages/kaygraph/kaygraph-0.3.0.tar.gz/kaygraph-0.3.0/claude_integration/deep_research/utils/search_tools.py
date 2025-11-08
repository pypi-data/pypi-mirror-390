"""
Search tools for deep research system.

This module implements real web search using Brave Search API and Jina AI,
following KayGraph patterns of keeping vendor-specific code in utils/.
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Standardized search result across different providers."""
    title: str
    url: str
    description: str
    content: Optional[str] = None
    published_date: Optional[str] = None
    author: Optional[str] = None
    source: str = "unknown"
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "content": self.content,
            "published_date": self.published_date,
            "author": self.author,
            "source": self.source,
            "relevance_score": self.relevance_score,
            "metadata": self.metadata
        }


class BraveSearchClient:
    """
    Brave Search API client for web search.

    Uses Brave's Web Search API for comprehensive web results.
    API Reference: https://brave.com/search/api/
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Brave Search client.

        Args:
            api_key: Brave Search API key (or set BRAVE_SEARCH_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.api_key:
            logger.warning("No Brave Search API key found. Set BRAVE_SEARCH_API_KEY")

        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.client = httpx.AsyncClient(timeout=30.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def search(
        self,
        query: str,
        count: int = 10,
        country: str = "US",
        search_lang: str = "en",
        freshness: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search the web using Brave Search API.

        Args:
            query: Search query
            count: Number of results (max 20)
            country: Country code for results
            search_lang: Language for search
            freshness: Time filter (pd=past day, pw=past week, pm=past month, py=past year)

        Returns:
            List of SearchResult objects
        """
        if not self.api_key:
            logger.warning("Brave Search API key not set, returning mock results")
            return self._mock_results(query, count)

        params = {
            "q": query,
            "count": min(count, 20),
            "country": country,
            "search_lang": search_lang
        }

        if freshness:
            params["freshness"] = freshness

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key
        }

        try:
            logger.info(f"Brave Search: {query[:50]}... (count={count})")
            response = await self.client.get(
                self.base_url,
                params=params,
                headers=headers
            )
            response.raise_for_status()

            data = response.json()

            # Parse results
            results = []
            for item in data.get("web", {}).get("results", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    description=item.get("description", ""),
                    content=item.get("extra_snippets", [""])[0] if item.get("extra_snippets") else None,
                    published_date=item.get("age"),
                    source="brave_search",
                    relevance_score=0.9,  # Brave doesn't provide explicit scores
                    metadata={
                        "page_age": item.get("page_age"),
                        "page_fetched": item.get("page_fetched"),
                        "language": item.get("language")
                    }
                )
                results.append(result)

            logger.info(f"Brave Search returned {len(results)} results")
            return results

        except httpx.HTTPStatusError as e:
            logger.error(f"Brave Search HTTP error: {e.response.status_code}")
            if e.response.status_code == 429:
                logger.error("Rate limit exceeded")
            return []
        except Exception as e:
            logger.error(f"Brave Search error: {e}")
            return []

    def _mock_results(self, query: str, count: int) -> List[SearchResult]:
        """Generate mock results when API key is not available."""
        return [
            SearchResult(
                title=f"Result {i+1} for {query}",
                url=f"https://example.com/result{i+1}",
                description=f"Description of result {i+1} for query: {query}",
                source="brave_search_mock",
                relevance_score=0.9 - (i * 0.05)
            )
            for i in range(min(count, 5))
        ]

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class BraveAIGroundingClient:
    """
    Brave AI Grounding API client.

    Uses Brave's AI Grounding for answers backed by web sources.
    Achieves SOTA on SimpleQA benchmark.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Brave AI Grounding client.

        Args:
            api_key: Brave Search API key (same as search API)
        """
        self.api_key = api_key or os.getenv("BRAVE_SEARCH_API_KEY")
        if not self.api_key:
            logger.warning("No Brave Search API key found")

        self.base_url = "https://api.search.brave.com/res/v1/chat/completions"
        self.client = httpx.AsyncClient(timeout=60.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def answer(
        self,
        question: str,
        enable_research: bool = False,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Get AI-grounded answer with sources.

        Args:
            question: Question to answer
            enable_research: Allow multiple searches (slower but more thorough)
            stream: Stream the response

        Returns:
            Dict with answer, sources, and metadata
        """
        if not self.api_key:
            logger.warning("Brave AI Grounding API key not set, returning mock answer")
            return self._mock_answer(question)

        payload = {
            "stream": stream,
            "messages": [
                {"role": "user", "content": question}
            ]
        }

        if enable_research:
            payload["enable_research"] = "true"

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/json",
            "X-Subscription-Token": self.api_key
        }

        try:
            logger.info(f"Brave AI Grounding: {question[:50]}... (research={enable_research})")
            response = await self.client.post(
                self.base_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()

            data = response.json()

            # Parse response
            choices = data.get("choices", [])
            if not choices:
                return {"answer": "No answer generated", "sources": [], "metadata": {}}

            message = choices[0].get("message", {})
            content = message.get("content", "")

            # Try to parse if it's stringified JSON
            try:
                if content.startswith("{"):
                    parsed = json.loads(content)
                    return {
                        "answer": parsed.get("answer", content),
                        "sources": parsed.get("sources", []),
                        "searches_performed": parsed.get("searches", 1),
                        "confidence": parsed.get("confidence", 0.8),
                        "metadata": data
                    }
            except json.JSONDecodeError:
                pass

            # Return as plain text answer
            return {
                "answer": content,
                "sources": [],  # Sources may be embedded in content
                "searches_performed": 1,
                "metadata": data
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Brave AI Grounding HTTP error: {e.response.status_code}")
            return {"answer": "Error retrieving answer", "sources": [], "metadata": {}}
        except Exception as e:
            logger.error(f"Brave AI Grounding error: {e}")
            return {"answer": "Error retrieving answer", "sources": [], "metadata": {}}

    def _mock_answer(self, question: str) -> Dict[str, Any]:
        """Generate mock answer when API key is not available."""
        return {
            "answer": f"Mock AI-grounded answer for: {question}. This would contain comprehensive information backed by web sources.",
            "sources": [
                {"title": "Example Source 1", "url": "https://example.com/1"},
                {"title": "Example Source 2", "url": "https://example.com/2"}
            ],
            "searches_performed": 1,
            "confidence": 0.7,
            "metadata": {"mock": True}
        }

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class JinaSearchClient:
    """
    Jina AI Search client.

    Uses Jina's search API for reader-friendly content extraction.
    API Reference: https://jina.ai/search
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Jina Search client.

        Args:
            api_key: Jina API key (or set JINA_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        if not self.api_key:
            logger.warning("No Jina API key found. Set JINA_API_KEY")

        self.base_url = "https://s.jina.ai/"
        self.client = httpx.AsyncClient(timeout=30.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def search(
        self,
        query: str,
        max_results: int = 10,
        respond_with: str = "markdown"
    ) -> List[SearchResult]:
        """
        Search using Jina AI.

        Args:
            query: Search query
            max_results: Maximum results to return
            respond_with: Response format (markdown, html, text, no-content)

        Returns:
            List of SearchResult objects
        """
        if not self.api_key:
            logger.warning("Jina API key not set, returning mock results")
            return self._mock_results(query, max_results)

        # Jina uses query parameter
        url = f"{self.base_url}?q={query}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Respond-With": respond_with
        }

        try:
            logger.info(f"Jina Search: {query[:50]}...")
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()

            # Jina returns different formats based on X-Respond-With
            if respond_with == "no-content":
                # Returns JSON with metadata
                data = response.json()
                results = []
                for item in data.get("data", [])[:max_results]:
                    result = SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        description=item.get("description", ""),
                        source="jina_search",
                        relevance_score=item.get("score", 0.8)
                    )
                    results.append(result)
                return results
            else:
                # Returns formatted content (markdown/html/text)
                content = response.text
                # Create a single result with the formatted content
                return [
                    SearchResult(
                        title=f"Jina Search: {query}",
                        url=f"{self.base_url}?q={query}",
                        description=f"Reader-friendly search results for: {query}",
                        content=content,
                        source="jina_search",
                        relevance_score=0.9
                    )
                ]

        except httpx.HTTPStatusError as e:
            logger.error(f"Jina Search HTTP error: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Jina Search error: {e}")
            return []

    def _mock_results(self, query: str, count: int) -> List[SearchResult]:
        """Generate mock results when API key is not available."""
        return [
            SearchResult(
                title=f"Jina Result {i+1} for {query}",
                url=f"https://example.com/jina{i+1}",
                description=f"Reader-friendly content for: {query}",
                source="jina_search_mock",
                relevance_score=0.85
            )
            for i in range(min(count, 5))
        ]

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class SearchToolFactory:
    """
    Factory for creating search tool instances.

    Follows KayGraph pattern of centralizing tool creation.
    """

    @staticmethod
    def create_brave_search(api_key: Optional[str] = None) -> BraveSearchClient:
        """Create Brave Search client."""
        return BraveSearchClient(api_key)

    @staticmethod
    def create_brave_ai_grounding(api_key: Optional[str] = None) -> BraveAIGroundingClient:
        """Create Brave AI Grounding client."""
        return BraveAIGroundingClient(api_key)

    @staticmethod
    def create_jina_search(api_key: Optional[str] = None) -> JinaSearchClient:
        """Create Jina Search client."""
        return JinaSearchClient(api_key)

    @staticmethod
    def get_available_tools() -> Dict[str, type]:
        """Get all available search tools."""
        return {
            "brave_search": BraveSearchClient,
            "brave_ai_grounding": BraveAIGroundingClient,
            "jina_search": JinaSearchClient
        }


# Async context manager support
class SearchSession:
    """Context manager for search clients."""

    def __init__(self, tool_name: str = "brave_search", api_key: Optional[str] = None):
        """
        Initialize search session.

        Args:
            tool_name: Name of search tool to use
            api_key: API key for the tool
        """
        self.tool_name = tool_name
        self.api_key = api_key
        self.client = None

    async def __aenter__(self):
        """Enter async context."""
        tools = SearchToolFactory.get_available_tools()
        if self.tool_name not in tools:
            raise ValueError(f"Unknown tool: {self.tool_name}")

        self.client = tools[self.tool_name](self.api_key)
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        if self.client and hasattr(self.client, 'close'):
            await self.client.close()


# Example usage
if __name__ == "__main__":
    async def demo_search_tools():
        """Demo the search tools."""
        print("="*60)
        print("Search Tools Demo")
        print("="*60)

        # Demo Brave Search
        print("\n1. Brave Web Search")
        async with SearchSession("brave_search") as brave:
            results = await brave.search("quantum computing breakthroughs 2025", count=5)
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.title}")
                print(f"   URL: {result.url}")
                print(f"   Description: {result.description[:100]}...")

        # Demo Brave AI Grounding
        print("\n\n2. Brave AI Grounding")
        async with SearchSession("brave_ai_grounding") as brave_ai:
            answer = await brave_ai.answer(
                "What are the latest quantum computing breakthroughs?",
                enable_research=False
            )
            print(f"\nAnswer: {answer['answer'][:200]}...")
            print(f"Searches performed: {answer.get('searches_performed', 1)}")
            print(f"Sources: {len(answer.get('sources', []))}")

        # Demo Jina Search
        print("\n\n3. Jina Search")
        async with SearchSession("jina_search") as jina:
            results = await jina.search("AI research papers", max_results=3)
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.title}")
                if result.content:
                    print(f"   Content length: {len(result.content)} chars")

        print("\n" + "="*60)
        print("Demo complete!")

    # Run demo
    asyncio.run(demo_search_tools())