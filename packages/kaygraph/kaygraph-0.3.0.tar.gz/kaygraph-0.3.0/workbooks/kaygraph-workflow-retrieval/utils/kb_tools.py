"""
Knowledge base tools for retrieval.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class KnowledgeBase:
    """Simple knowledge base with search capabilities."""
    
    def __init__(self, kb_path: str = None):
        """Load knowledge base from JSON file."""
        if kb_path is None:
            kb_path = Path(__file__).parent.parent / "data" / "kb.json"
        
        with open(kb_path, 'r') as f:
            self.data = json.load(f)
        
        # Index for faster search
        self._build_indices()
    
    def _build_indices(self):
        """Build search indices for efficient retrieval."""
        # FAQ index by keywords
        self.faq_keyword_index = {}
        for faq in self.data.get("faq", []):
            for keyword in faq.get("keywords", []):
                keyword_lower = keyword.lower()
                if keyword_lower not in self.faq_keyword_index:
                    self.faq_keyword_index[keyword_lower] = []
                self.faq_keyword_index[keyword_lower].append(faq)
        
        # Product index by category
        self.product_category_index = {}
        for product in self.data.get("products", []):
            category = product.get("category", "").lower()
            if category not in self.product_category_index:
                self.product_category_index[category] = []
            self.product_category_index[category].append(product)
        
        # Policy index by title words
        self.policy_title_index = {}
        for policy in self.data.get("policies", []):
            title_words = policy.get("title", "").lower().split()
            for word in title_words:
                if word not in self.policy_title_index:
                    self.policy_title_index[word] = []
                self.policy_title_index[word].append(policy)
    
    def search_faq(self, question: str) -> Dict[str, Any]:
        """Search FAQ by question keywords."""
        question_lower = question.lower()
        
        # First try exact question match
        for faq in self.data.get("faq", []):
            if question_lower in faq.get("question", "").lower():
                return {
                    "found": True,
                    "result": faq,
                    "source": f"FAQ #{faq['id']}"
                }
        
        # Then try keyword match
        words = question_lower.split()
        matches = []
        
        for word in words:
            if word in self.faq_keyword_index:
                matches.extend(self.faq_keyword_index[word])
        
        # Return most relevant (first) match
        if matches:
            # Remove duplicates while preserving order
            seen = set()
            unique_matches = []
            for match in matches:
                if match['id'] not in seen:
                    seen.add(match['id'])
                    unique_matches.append(match)
            
            return {
                "found": True,
                "result": unique_matches[0],
                "source": f"FAQ #{unique_matches[0]['id']}",
                "confidence": "high" if len(unique_matches) == 1 else "medium"
            }
        
        return {
            "found": False,
            "message": "No FAQ found for this question"
        }
    
    def search_products(self, query: str) -> Dict[str, Any]:
        """Search products by name or category."""
        query_lower = query.lower()
        
        # Search by name
        name_matches = []
        for product in self.data.get("products", []):
            if query_lower in product.get("name", "").lower():
                name_matches.append(product)
        
        if name_matches:
            return {
                "found": True,
                "results": name_matches,
                "source": "Product Catalog",
                "match_type": "name"
            }
        
        # Search by category
        if query_lower in self.product_category_index:
            category_matches = self.product_category_index[query_lower]
            return {
                "found": True,
                "results": category_matches,
                "source": "Product Catalog",
                "match_type": "category"
            }
        
        # Search in descriptions
        desc_matches = []
        for product in self.data.get("products", []):
            if query_lower in product.get("description", "").lower():
                desc_matches.append(product)
        
        if desc_matches:
            return {
                "found": True,
                "results": desc_matches,
                "source": "Product Catalog",
                "match_type": "description"
            }
        
        return {
            "found": False,
            "message": "No products found matching your query"
        }
    
    def search_policies(self, query: str) -> Dict[str, Any]:
        """Search policies by title or content."""
        query_lower = query.lower()
        
        # Search by title words
        words = query_lower.split()
        matches = []
        
        for word in words:
            if word in self.policy_title_index:
                matches.extend(self.policy_title_index[word])
        
        if matches:
            # Remove duplicates
            seen = set()
            unique_matches = []
            for match in matches:
                if match['id'] not in seen:
                    seen.add(match['id'])
                    unique_matches.append(match)
            
            return {
                "found": True,
                "results": unique_matches,
                "source": "Policy Documents"
            }
        
        # Search in content
        content_matches = []
        for policy in self.data.get("policies", []):
            if query_lower in policy.get("content", "").lower():
                content_matches.append(policy)
        
        if content_matches:
            return {
                "found": True,
                "results": content_matches,
                "source": "Policy Documents",
                "match_type": "content"
            }
        
        return {
            "found": False,
            "message": "No policies found matching your query"
        }
    
    def get_all_faqs(self) -> List[Dict[str, Any]]:
        """Get all FAQs."""
        return self.data.get("faq", [])
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products."""
        return self.data.get("products", [])
    
    def get_all_policies(self) -> List[Dict[str, Any]]:
        """Get all policies."""
        return self.data.get("policies", [])


# Tool functions for node integration

def search_kb(question: str, kb_type: str = "all") -> Dict[str, Any]:
    """
    Search knowledge base tool function.
    
    Args:
        question: The search query
        kb_type: Type of KB to search (faq, product, policy, all)
    
    Returns:
        Search results with source attribution
    """
    kb = KnowledgeBase()
    
    if kb_type == "faq":
        return kb.search_faq(question)
    elif kb_type == "product":
        return kb.search_products(question)
    elif kb_type == "policy":
        return kb.search_policies(question)
    else:
        # Search all KBs
        results = {
            "faq": kb.search_faq(question),
            "products": kb.search_products(question),
            "policies": kb.search_policies(question)
        }
        
        # Aggregate results
        found_any = any(r.get("found", False) for r in results.values())
        
        return {
            "found": found_any,
            "results": results,
            "source": "Multiple Knowledge Bases"
        }


# Tool metadata for registration
SEARCH_KB_METADATA = {
    "name": "search_kb",
    "description": "Search the knowledge base for answers to questions",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question or search query"
            },
            "kb_type": {
                "type": "string",
                "enum": ["faq", "product", "policy", "all"],
                "description": "Type of knowledge base to search",
                "default": "all"
            }
        },
        "required": ["question"]
    }
}


if __name__ == "__main__":
    # Test the knowledge base
    kb = KnowledgeBase()
    
    print("Testing FAQ search:")
    result = kb.search_faq("What is the return policy?")
    print(json.dumps(result, indent=2))
    
    print("\nTesting product search:")
    result = kb.search_products("headphones")
    print(json.dumps(result, indent=2))
    
    print("\nTesting policy search:")
    result = kb.search_policies("privacy")
    print(json.dumps(result, indent=2))
    
    print("\nTesting integrated search:")
    result = search_kb("return policy", "all")
    print(json.dumps(result, indent=2))