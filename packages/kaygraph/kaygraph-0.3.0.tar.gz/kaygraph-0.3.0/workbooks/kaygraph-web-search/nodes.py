"""
Node implementations for web search workflows.
"""

import json
import logging
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from kaygraph import Node
from models import (
    SearchProvider, SearchType, QueryIntent,
    SearchQuery, SearchResult, SearchResponse,
    QueryAnalysis, QueryRefinement,
    ProcessedResult, ResultCluster,
    AnswerSource, SynthesizedAnswer,
    ResearchTopic, ResearchResult,
    ComparisonItem, ComparisonResult,
    CachedSearch, SearchError
)
from utils import call_llm
from utils.search_providers import (
    search_serp_api, search_duckduckgo, search_mock,
    get_available_search_providers
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _clean_json_response(response: str) -> str:
    """Clean LLM response to extract JSON."""
    response = response.strip()
    
    # Remove thinking tags if present
    if "<think>" in response and "</think>" in response:
        parts = response.split("</think>")
        if len(parts) > 1:
            response = parts[-1].strip()
    
    # Remove markdown code blocks
    if response.startswith("```json"):
        response = response[7:]
    if response.endswith("```"):
        response = response[:-3]
    
    return response.strip()


# ============== Query Analysis Nodes ==============

class QueryAnalyzerNode(Node):
    """Analyzes search query to determine intent and optimize search."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get search query."""
        return shared.get("query", shared.get("search_query", ""))
    
    def exec(self, query: str) -> QueryAnalysis:
        """Analyze query to optimize search."""
        prompt = f"""Analyze this search query to optimize web search.

Query: {query}

Determine:
1. Search intent (informational/navigational/transactional/research/current_events/comparison)
2. Key entities to search for
3. Temporal markers (latest, 2024, yesterday, etc.)
4. Whether current/real-time info is needed
5. Suggested search filters

Return JSON:
{{
  "original_query": "{query}",
  "cleaned_query": "optimized query for search",
  "intent": "informational/navigational/etc",
  "entities": ["entity1", "entity2"],
  "temporal_markers": ["latest", "2024"],
  "requires_current": true/false,
  "suggested_filters": {{"site": "example.com", "filetype": "pdf"}},
  "related_queries": ["related query 1", "related query 2"]
}}

Output JSON only:"""
        
        system = "You are a search query analyst. Optimize queries for better search results."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            return QueryAnalysis(
                original_query=data.get("original_query", query),
                cleaned_query=data.get("cleaned_query", query),
                intent=QueryIntent(data.get("intent", "informational")),
                entities=data.get("entities", []),
                temporal_markers=data.get("temporal_markers", []),
                requires_current=data.get("requires_current", False),
                suggested_filters=data.get("suggested_filters", {}),
                related_queries=data.get("related_queries", [])
            )
        except Exception as e:
            logger.error(f"Query analysis error: {e}")
            # Simple fallback
            return QueryAnalysis(
                original_query=query,
                cleaned_query=query,
                intent=QueryIntent.INFORMATIONAL,
                requires_current="latest" in query.lower() or "today" in query.lower()
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: QueryAnalysis) -> Optional[str]:
        """Store analysis and determine search type."""
        shared["query_analysis"] = exec_res
        
        # Create search query
        search_query = SearchQuery(
            query=exec_res.cleaned_query,
            intent=exec_res.intent,
            filters=exec_res.suggested_filters
        )
        shared["search_query"] = search_query
        
        # Route based on intent
        if exec_res.intent == QueryIntent.RESEARCH:
            return "research"
        elif exec_res.intent == QueryIntent.COMPARISON:
            return "comparison"
        else:
            return None  # Default routing


# ============== Search Execution Nodes ==============

class WebSearchNode(Node):
    """Executes web search using available providers."""
    
    def __init__(self, provider: Optional[SearchProvider] = None, **kwargs):
        self.provider = provider
        super().__init__(**kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> SearchQuery:
        """Get search query."""
        return shared.get("search_query", SearchQuery(query=shared.get("query", "")))
    
    def exec(self, search_query: SearchQuery) -> SearchResponse:
        """Execute web search."""
        # Select provider
        if self.provider:
            provider = self.provider
        else:
            # For testing, prefer mock provider
            provider = SearchProvider.MOCK
        
        logger.info(f"Searching with {provider.value}: {search_query.query}")
        
        try:
            if provider == SearchProvider.SERP_API:
                return search_serp_api(search_query)
            elif provider == SearchProvider.DUCKDUCKGO:
                return search_duckduckgo(search_query)
            else:
                return search_mock(search_query)
        except Exception as e:
            logger.error(f"Search error with {provider.value}: {e}")
            return SearchResponse(
                query=search_query,
                provider=provider,
                results=[],
                error=str(e)
            )
    
    def post(self, shared: Dict[str, Any], prep_res: SearchQuery, 
             exec_res: SearchResponse) -> Optional[str]:
        """Store search results."""
        shared["search_response"] = exec_res
        
        if exec_res.error:
            return "error"
        elif exec_res.results:
            return "process"
        else:
            return "no_results"


class MultiSearchNode(Node):
    """Executes multiple searches in parallel."""
    
    def prep(self, shared: Dict[str, Any]) -> List[SearchQuery]:
        """Get multiple search queries."""
        queries = shared.get("search_queries", [])
        if not queries and shared.get("related_queries"):
            # Create queries from related queries
            analysis = shared.get("query_analysis")
            if analysis:
                queries = [
                    SearchQuery(query=q, intent=analysis.intent)
                    for q in analysis.related_queries[:3]
                ]
        return queries
    
    def exec(self, queries: List[SearchQuery]) -> List[SearchResponse]:
        """Execute multiple searches."""
        results = []
        provider = SearchProvider.MOCK  # Use mock for multiple searches
        
        for query in queries:
            try:
                if provider == SearchProvider.MOCK:
                    response = search_mock(query)
                else:
                    response = search_duckduckgo(query)
                results.append(response)
            except Exception as e:
                logger.error(f"Multi-search error: {e}")
                results.append(SearchResponse(
                    query=query,
                    provider=provider,
                    results=[],
                    error=str(e)
                ))
        
        return results
    
    def post(self, shared: Dict[str, Any], prep_res: List[SearchQuery], 
             exec_res: List[SearchResponse]) -> Optional[str]:
        """Store multi-search results."""
        shared["multi_search_responses"] = exec_res
        return None


# ============== Result Processing Nodes ==============

class ResultProcessorNode(Node):
    """Processes and enriches search results."""
    
    def prep(self, shared: Dict[str, Any]) -> SearchResponse:
        """Get search response to process."""
        return shared.get("search_response")
    
    def exec(self, response: SearchResponse) -> List[ProcessedResult]:
        """Process and score search results."""
        if not response or not response.results:
            return []
        
        processed = []
        for i, result in enumerate(response.results[:5]):  # Process top 5
            # Simple relevance scoring based on position
            relevance = 1.0 - (i * 0.15)
            
            # Mock credibility scoring
            credibility = 0.8
            if "wikipedia" in str(result.url).lower():
                credibility = 0.9
            elif "blog" in str(result.url).lower():
                credibility = 0.6
            
            # Extract key facts from snippet
            sentences = result.snippet.split(". ")
            key_facts = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
            
            processed.append(ProcessedResult(
                original=result,
                relevance_score=relevance,
                credibility_score=credibility,
                summary=result.snippet[:200],
                key_facts=key_facts
            ))
        
        return processed
    
    def post(self, shared: Dict[str, Any], prep_res: SearchResponse, 
             exec_res: List[ProcessedResult]) -> Optional[str]:
        """Store processed results."""
        shared["processed_results"] = exec_res
        return None


class ResultClusteringNode(Node):
    """Clusters related search results."""
    
    def prep(self, shared: Dict[str, Any]) -> List[ProcessedResult]:
        """Get processed results to cluster."""
        return shared.get("processed_results", [])
    
    def exec(self, results: List[ProcessedResult]) -> List[ResultCluster]:
        """Cluster results by topic."""
        if not results:
            return []
        
        # Simple clustering - in real implementation would use embeddings
        clusters = []
        
        # For now, create one main cluster
        if results:
            main_cluster = ResultCluster(
                topic="Main Topic",
                results=results,
                consensus="Multiple sources discuss this topic",
                confidence=0.8
            )
            clusters.append(main_cluster)
        
        return clusters
    
    def post(self, shared: Dict[str, Any], prep_res: List[ProcessedResult], 
             exec_res: List[ResultCluster]) -> Optional[str]:
        """Store clusters."""
        shared["result_clusters"] = exec_res
        return None


# ============== Answer Synthesis Nodes ==============

class AnswerSynthesisNode(Node):
    """Synthesizes coherent answer from search results."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather query and results."""
        return {
            "query": shared.get("query", ""),
            "analysis": shared.get("query_analysis"),
            "results": shared.get("processed_results", []),
            "clusters": shared.get("result_clusters", [])
        }
    
    def exec(self, data: Dict[str, Any]) -> SynthesizedAnswer:
        """Synthesize answer from search results."""
        query = data["query"]
        results = data["results"]
        
        if not results:
            return SynthesizedAnswer(
                query=query,
                answer="I couldn't find relevant information for your query.",
                confidence=0.0,
                sources=[]
            )
        
        # Prepare context from results
        context_parts = []
        sources = []
        
        for i, result in enumerate(results[:5]):
            context_parts.append(f"Source {i+1}: {result.summary}")
            sources.append(AnswerSource(
                url=result.original.url,
                title=result.original.title,
                snippet=result.original.snippet,
                relevance=result.relevance_score
            ))
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""Synthesize a comprehensive answer from these search results.

Query: {query}

Search Results:
{context}

Create a well-structured answer that:
1. Directly addresses the query
2. Synthesizes information from multiple sources
3. Notes any contradictions or disagreements
4. Suggests follow-up questions

Return JSON:
{{
  "answer": "Your synthesized answer with proper paragraphs",
  "confidence": 0.0-1.0,
  "key_points": ["key point 1", "key point 2"],
  "caveats": ["any limitations or caveats"],
  "follow_up_questions": ["suggested follow-up 1", "suggested follow-up 2"]
}}

Output JSON only:"""
        
        system = "You are a research assistant. Synthesize search results into clear, accurate answers."
        
        try:
            response = call_llm(prompt, system, temperature=0.4)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            return SynthesizedAnswer(
                query=query,
                answer=data.get("answer", "Unable to synthesize answer"),
                confidence=float(data.get("confidence", 0.7)),
                sources=sources,
                key_points=data.get("key_points", []),
                caveats=data.get("caveats", []),
                follow_up_questions=data.get("follow_up_questions", [])
            )
        except Exception as e:
            logger.error(f"Answer synthesis error: {e}")
            # Fallback to simple concatenation
            answer = "Based on the search results:\n\n"
            for i, result in enumerate(results[:3]):
                answer += f"{i+1}. {result.summary}\n\n"
            
            return SynthesizedAnswer(
                query=query,
                answer=answer,
                confidence=0.5,
                sources=sources
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: SynthesizedAnswer) -> Optional[str]:
        """Store synthesized answer."""
        shared["synthesized_answer"] = exec_res
        return None


# ============== Research Nodes ==============

class ResearchPlannerNode(Node):
    """Plans comprehensive research based on query."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get research query."""
        return shared.get("query", "")
    
    def exec(self, query: str) -> ResearchTopic:
        """Create research plan."""
        prompt = f"""Create a research plan for this topic.

Topic: {query}

Break it down into:
1. Main topic statement
2. 3-5 subtopics to explore
3. Key research questions
4. Number of sources needed

Return JSON:
{{
  "main_topic": "Clear topic statement",
  "subtopics": ["subtopic 1", "subtopic 2", "subtopic 3"],
  "research_questions": [
    "What is..?",
    "How does..?",
    "What are the implications..?"
  ],
  "required_sources": 10
}}

Output JSON only:"""
        
        system = "You are a research planner. Create comprehensive research plans."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            cleaned = _clean_json_response(response)
            data = json.loads(cleaned)
            
            return ResearchTopic(
                main_topic=data.get("main_topic", query),
                subtopics=data.get("subtopics", [query]),
                research_questions=data.get("research_questions", [f"What is {query}?"]),
                required_sources=data.get("required_sources", 5)
            )
        except Exception as e:
            logger.error(f"Research planning error: {e}")
            return ResearchTopic(
                main_topic=query,
                subtopics=[query],
                research_questions=[f"What is {query}?"],
                required_sources=5
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: ResearchTopic) -> Optional[str]:
        """Store research plan."""
        shared["research_topic"] = exec_res
        
        # Create search queries for subtopics
        queries = []
        for subtopic in exec_res.subtopics:
            queries.append(SearchQuery(
                query=f"{exec_res.main_topic} {subtopic}",
                intent=QueryIntent.RESEARCH
            ))
        shared["search_queries"] = queries
        
        return "multi_search"


class ResearchSynthesisNode(Node):
    """Synthesizes comprehensive research report."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather research data."""
        return {
            "topic": shared.get("research_topic"),
            "responses": shared.get("multi_search_responses", []),
            "query": shared.get("query", "")
        }
    
    def exec(self, data: Dict[str, Any]) -> ResearchResult:
        """Synthesize research findings."""
        topic = data["topic"]
        responses = data["responses"]
        
        if not topic:
            topic = ResearchTopic(
                main_topic=data["query"],
                subtopics=[],
                research_questions=[]
            )
        
        # Extract findings per subtopic
        findings = {}
        all_sources = []
        
        for i, response in enumerate(responses):
            if i < len(topic.subtopics):
                subtopic = topic.subtopics[i]
                findings[subtopic] = []
                
                for result in response.results[:3]:
                    findings[subtopic].append(result.snippet)
                    all_sources.append(AnswerSource(
                        url=result.url,
                        title=result.title,
                        snippet=result.snippet[:100],
                        relevance=0.8
                    ))
        
        # Create summary
        summary = f"Research on {topic.main_topic}:\n\n"
        for subtopic, facts in findings.items():
            summary += f"{subtopic}:\n"
            for fact in facts[:2]:
                summary += f"- {fact[:150]}...\n"
            summary += "\n"
        
        return ResearchResult(
            topic=topic,
            findings=findings,
            sources=all_sources[:10],
            summary=summary,
            conclusions=["Further research is recommended"],
            limitations=["Limited to web search results"],
            further_research=["Explore academic sources", "Conduct expert interviews"]
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: ResearchResult) -> Optional[str]:
        """Store research result."""
        shared["research_result"] = exec_res
        return None


# ============== Comparison Nodes ==============

class ComparisonPlannerNode(Node):
    """Plans comparison search."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get comparison query."""
        return shared.get("query", "")
    
    def exec(self, query: str) -> List[ComparisonItem]:
        """Extract items to compare."""
        # Simple extraction - look for "vs", "versus", "or", "compare"
        items = []
        
        if " vs " in query.lower() or " versus " in query.lower():
            parts = re.split(r'\s+v(?:s|ersus)\s+', query, flags=re.IGNORECASE)
            for part in parts:
                items.append(ComparisonItem(
                    name=part.strip(),
                    search_query=part.strip()
                ))
        else:
            # Assume single item comparison
            items.append(ComparisonItem(
                name=query,
                search_query=query
            ))
        
        return items
    
    def post(self, shared: Dict[str, Any], prep_res: str, 
             exec_res: List[ComparisonItem]) -> Optional[str]:
        """Store comparison items."""
        shared["comparison_items"] = exec_res
        
        # Create search queries
        queries = [
            SearchQuery(query=item.search_query, intent=QueryIntent.COMPARISON)
            for item in exec_res
        ]
        shared["search_queries"] = queries
        
        return "multi_search"


# ============== Output Formatting Nodes ==============

class SearchOutputNode(Node):
    """Formats final search output."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all results."""
        return {
            "answer": shared.get("synthesized_answer"),
            "research": shared.get("research_result"),
            "comparison": shared.get("comparison_result"),
            "error": shared.get("search_error")
        }
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Format comprehensive output."""
        if data["error"]:
            return f"Search Error: {data['error']}"
        
        output_parts = []
        
        # Synthesized answer
        if data["answer"]:
            answer = data["answer"]
            output_parts.append(answer.answer)
            
            if answer.key_points:
                output_parts.append("\nKey Points:")
                for point in answer.key_points:
                    output_parts.append(f"• {point}")
            
            if answer.sources:
                output_parts.append("\nSources:")
                for i, source in enumerate(answer.sources[:5]):
                    output_parts.append(f"{i+1}. {source.title}")
                    output_parts.append(f"   {source.url}")
            
            if answer.follow_up_questions:
                output_parts.append("\nSuggested follow-up questions:")
                for q in answer.follow_up_questions:
                    output_parts.append(f"• {q}")
        
        # Research report
        elif data["research"]:
            research = data["research"]
            output_parts.append(research.summary)
            
            if research.conclusions:
                output_parts.append("Conclusions:")
                for conclusion in research.conclusions:
                    output_parts.append(f"• {conclusion}")
            
            if research.sources:
                output_parts.append(f"\nBased on {len(research.sources)} sources")
        
        # Comparison result
        elif data["comparison"]:
            comparison = data["comparison"]
            output_parts.append(comparison.summary)
            
            if comparison.recommendation:
                output_parts.append(f"\nRecommendation: {comparison.recommendation}")
        
        else:
            output_parts.append("No results found for your search.")
        
        return "\n".join(output_parts)
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: str) -> Optional[str]:
        """Store final output."""
        shared["final_output"] = exec_res
        return None


# ============== Cache Node ==============

class SearchCacheNode(Node):
    """Caches search results to avoid repeated API calls."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache = {}  # Simple in-memory cache
    
    def prep(self, shared: Dict[str, Any]) -> SearchQuery:
        """Get search query to check cache."""
        return shared.get("search_query")
    
    def exec(self, query: SearchQuery) -> Optional[SearchResponse]:
        """Check cache for existing results."""
        if not query:
            return None
        
        # Create cache key
        cache_key = hashlib.md5(
            f"{query.query}:{query.search_type}:{query.filters}".encode()
        ).hexdigest()
        
        # Check cache
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            # Check if still valid (1 hour TTL)
            age = (datetime.now() - cached.timestamp).seconds
            if age < cached.ttl_seconds:
                logger.info(f"Cache hit for: {query.query}")
                return cached.response
        
        return None
    
    def post(self, shared: Dict[str, Any], prep_res: SearchQuery, 
             exec_res: Optional[SearchResponse]) -> Optional[str]:
        """Route based on cache status."""
        if exec_res:
            shared["search_response"] = exec_res
            return "cache_hit"
        else:
            shared["cache_key"] = hashlib.md5(
                f"{prep_res.query}:{prep_res.search_type}:{prep_res.filters}".encode()
            ).hexdigest()
            return "cache_miss"