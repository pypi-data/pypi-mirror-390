"""
Node implementations for retrieval workflows.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

from kaygraph import Node, Graph
from utils import call_llm
from utils.kb_tools import search_kb, KnowledgeBase

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


class QueryType(Enum):
    """Types of queries that can be handled."""
    FAQ = "faq"
    PRODUCT = "product"
    POLICY = "policy"
    GENERAL = "general"
    OUT_OF_SCOPE = "out_of_scope"


# ============== Query Analysis Nodes ==============

class QueryAnalyzerNode(Node):
    """Analyze user query to determine if KB search is needed."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get user query."""
        return shared.get("query", "")
    
    def exec(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine retrieval needs."""
        if not query:
            return {"error": "No query provided"}
        
        prompt = f"""Analyze this user query and determine if it requires searching our knowledge base.

User query: {query}

Our knowledge base contains:
- FAQ: Common questions about returns, shipping, payments, orders
- Products: Electronics, clothing, fitness items, accessories
- Policies: Privacy policy, terms of service, warranty information

Return a JSON object with:
{{
  "needs_search": true/false,
  "query_type": "faq/product/policy/general/out_of_scope",
  "reasoning": "why this decision was made",
  "search_query": "refined query for search if needed"
}}

Examples:
- "What's the weather?" -> needs_search: false, query_type: "out_of_scope"
- "What's your return policy?" -> needs_search: true, query_type: "faq"
- "Tell me about wireless headphones" -> needs_search: true, query_type: "product"

Output JSON only:"""
        
        system = "You are a query analyzer. Determine if knowledge base search is needed."
        
        try:
            response = call_llm(prompt, system, temperature=0.1)
            cleaned = _clean_json_response(response)
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Query analysis error: {e}")
            return {
                "needs_search": True,  # Default to searching
                "query_type": "general",
                "reasoning": "Error in analysis, defaulting to search",
                "error": str(e)
            }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> Optional[str]:
        """Store analysis and route accordingly."""
        shared["query_analysis"] = exec_res
        
        if exec_res.get("needs_search", True):
            shared["search_query"] = exec_res.get("search_query", prep_res)
            return "needs_search"
        else:
            return "direct_answer"


class QueryRouterNode(Node):
    """Route queries to appropriate KB search based on type."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get query analysis."""
        return shared.get("query_analysis", {})
    
    def exec(self, analysis: Dict[str, Any]) -> str:
        """Determine routing based on query type."""
        query_type = analysis.get("query_type", "general")
        
        # Map to QueryType enum
        try:
            return QueryType(query_type).value
        except ValueError:
            return QueryType.GENERAL.value
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Optional[str]:
        """Route to appropriate search."""
        shared["kb_type"] = exec_res
        return exec_res  # Route based on query type


# ============== Retrieval Nodes ==============

class KBSearchNode(Node):
    """Search knowledge base using the search tool."""
    
    def __init__(self, kb_type: Optional[str] = None, **kwargs):
        self.kb_type = kb_type
        super().__init__(**kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get search parameters."""
        return {
            "query": shared.get("search_query", shared.get("query", "")),
            "kb_type": self.kb_type or shared.get("kb_type", "all")
        }
    
    def exec(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute KB search."""
        query = params.get("query", "")
        kb_type = params.get("kb_type", "all")
        
        if not query:
            return {"error": "No search query provided"}
        
        try:
            # Use the search_kb tool
            result = search_kb(query, kb_type)
            
            logger.info(f"KB search for '{query}' in {kb_type}: found={result.get('found')}")
            
            return result
        except Exception as e:
            logger.error(f"KB search error: {e}")
            return {
                "found": False,
                "error": str(e)
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> Optional[str]:
        """Store search results."""
        shared["kb_search_result"] = exec_res
        
        if exec_res.get("found"):
            return "found"
        else:
            return "not_found"


class MultiKBSearchNode(Node):
    """Search multiple KB types and aggregate results."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get search query."""
        return shared.get("search_query", shared.get("query", ""))
    
    def exec(self, query: str) -> Dict[str, Any]:
        """Search all KB types."""
        if not query:
            return {"error": "No search query provided"}
        
        # Search all KB types
        results = {}
        kb_types = ["faq", "product", "policy"]
        
        for kb_type in kb_types:
            try:
                result = search_kb(query, kb_type)
                if result.get("found"):
                    results[kb_type] = result
            except Exception as e:
                logger.error(f"Error searching {kb_type}: {e}")
        
        if results:
            return {
                "found": True,
                "results": results,
                "source": "Multiple Knowledge Bases"
            }
        else:
            return {
                "found": False,
                "message": "No information found in any knowledge base"
            }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> Optional[str]:
        """Store multi-search results."""
        shared["multi_kb_results"] = exec_res
        
        if exec_res.get("found"):
            return "found"
        else:
            return "not_found"


# ============== Response Generation Nodes ==============

class RetrievalResponseNode(Node):
    """Generate response using retrieved information."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather query and search results."""
        return {
            "query": shared.get("query", ""),
            "search_result": shared.get("kb_search_result") or shared.get("multi_kb_results"),
            "query_analysis": shared.get("query_analysis", {})
        }
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Generate response with source attribution."""
        query = data.get("query", "")
        search_result = data.get("search_result", {})
        
        if not search_result or not search_result.get("found"):
            return "I couldn't find information about that in our knowledge base. Please try rephrasing your question or contact our support team for assistance."
        
        # Format search results for LLM
        if "results" in search_result and isinstance(search_result["results"], dict):
            # Multi-KB results
            context_parts = []
            for kb_type, result in search_result["results"].items():
                if result.get("found"):
                    context_parts.append(f"{kb_type.upper()}: {json.dumps(result, indent=2)}")
            context = "\n\n".join(context_parts)
        else:
            # Single KB result
            context = json.dumps(search_result, indent=2)
        
        prompt = f"""Generate a helpful response to the user's question using the information retrieved from our knowledge base.

User question: {query}

Retrieved information:
{context}

Instructions:
1. Answer the user's question directly using the retrieved information
2. Include relevant details from the search results
3. Mention the source (e.g., "According to our FAQ..." or "Based on our return policy...")
4. If multiple sources were found, synthesize the information
5. Be concise but complete
6. If the information doesn't fully answer the question, acknowledge that

Response:"""
        
        system = "You are a helpful customer service assistant. Provide accurate answers based on the retrieved information."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            
            # Add source attribution if not already included
            source = search_result.get("source", "our knowledge base")
            if source not in response:
                response += f"\n\n[Source: {source}]"
            
            return response
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            # Fallback to simple formatting
            if "result" in search_result:
                result = search_result["result"]
                if isinstance(result, dict) and "answer" in result:
                    return f"{result['answer']}\n\n[Source: {search_result.get('source', 'Knowledge Base')}]"
            
            return "I found relevant information but had trouble formatting the response. Please try again."
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Optional[str]:
        """Store generated response."""
        shared["response"] = exec_res
        return None


class DirectResponseNode(Node):
    """Generate response without KB search for out-of-scope queries."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get query and analysis."""
        return {
            "query": shared.get("query", ""),
            "analysis": shared.get("query_analysis", {})
        }
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Generate direct response."""
        query = data.get("query", "")
        analysis = data.get("analysis", {})
        
        reasoning = analysis.get("reasoning", "")
        query_type = analysis.get("query_type", "out_of_scope")
        
        if query_type == "out_of_scope":
            return f"I can help you with questions about our products, shipping, returns, and policies. Your question seems to be outside my area of expertise. {reasoning}"
        else:
            # General response without KB search
            prompt = f"""Generate a helpful response to this query without using specific knowledge base information.

Query: {query}
Analysis: {reasoning}

Provide a general, helpful response that guides the user appropriately."""
            
            system = "You are a helpful assistant. Provide general guidance without specific product or policy details."
            
            try:
                response = call_llm(prompt, system, temperature=0.5)
                return response
            except:
                return "I'm here to help with questions about our products and services. Please feel free to ask about our inventory, policies, or any other information you need."
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Optional[str]:
        """Store response."""
        shared["response"] = exec_res
        return None


class NotFoundResponseNode(Node):
    """Generate helpful response when information is not found."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get query and search attempts."""
        return {
            "query": shared.get("query", ""),
            "search_query": shared.get("search_query", ""),
            "kb_type": shared.get("kb_type", "all"),
            "search_result": shared.get("kb_search_result") or shared.get("multi_kb_results")
        }
    
    def exec(self, data: Dict[str, Any]) -> str:
        """Generate helpful not-found response."""
        query = data.get("query", "")
        kb_type = data.get("kb_type", "all")
        
        suggestions = []
        
        if kb_type == "faq":
            suggestions = [
                "Try searching for 'shipping' or 'returns' for common questions",
                "Check our product catalog for specific item information",
                "Review our policies for terms and conditions"
            ]
        elif kb_type == "product":
            suggestions = [
                "Browse by category: electronics, clothing, fitness, accessories",
                "Try searching for general product types instead of specific models",
                "Check our FAQ for product-related questions"
            ]
        elif kb_type == "policy":
            suggestions = [
                "Look for 'privacy policy', 'terms of service', or 'warranty'",
                "Check our FAQ for policy-related questions",
                "Contact support for specific policy clarifications"
            ]
        else:
            suggestions = [
                "Try rephrasing your question",
                "Browse our FAQ for common questions",
                "Search our product catalog",
                "Review our policies"
            ]
        
        response = f"I couldn't find specific information about '{query}' in our knowledge base.\n\n"
        response += "Here are some suggestions:\n"
        for i, suggestion in enumerate(suggestions, 1):
            response += f"{i}. {suggestion}\n"
        response += "\nIf you need more help, please contact our customer support team."
        
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Optional[str]:
        """Store response."""
        shared["response"] = exec_res
        return None


# ============== Caching and Optimization Nodes ==============

class CacheCheckNode(Node):
    """Check if query result is cached."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache = {}  # Simple in-memory cache
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get query for cache check."""
        return shared.get("query", "").lower().strip()
    
    def exec(self, query: str) -> Dict[str, Any]:
        """Check cache for query."""
        if query in self.cache:
            logger.info(f"Cache hit for query: {query}")
            return {
                "cached": True,
                "result": self.cache[query]
            }
        else:
            return {
                "cached": False
            }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> Optional[str]:
        """Route based on cache status."""
        if exec_res.get("cached"):
            shared["response"] = exec_res["result"]
            return "cache_hit"
        else:
            shared["cache_key"] = prep_res
            return "cache_miss"


class CacheStoreNode(Node):
    """Store successful responses in cache."""
    
    def __init__(self, cache_node: CacheCheckNode, **kwargs):
        super().__init__(**kwargs)
        self.cache_node = cache_node
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get cache key and response."""
        return {
            "key": shared.get("cache_key", ""),
            "response": shared.get("response", "")
        }
    
    def exec(self, data: Dict[str, Any]) -> None:
        """Store in cache."""
        key = data.get("key")
        response = data.get("response")
        
        if key and response and len(response) > 10:  # Only cache meaningful responses
            self.cache_node.cache[key] = response
            logger.info(f"Cached response for: {key}")
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: None) -> Optional[str]:
        """Complete caching."""
        return None