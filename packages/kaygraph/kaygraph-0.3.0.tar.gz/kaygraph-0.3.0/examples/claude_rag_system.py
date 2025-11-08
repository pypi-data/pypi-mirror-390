#!/usr/bin/env python3
"""Claude-powered RAG System with Embeddings and KayGraph.

This example demonstrates a Retrieval-Augmented Generation (RAG) system using Claude
for generation and external embedding APIs for document retrieval.

Examples:
    basic_rag - Simple document Q&A
    multi_source_rag - Multi-document source synthesis
    semantic_search - Advanced semantic search with embeddings
    knowledge_graph - Knowledge graph-based RAG

Usage:
./examples/claude_rag_system.py - List the examples
./examples/claude_rag_system.py all - Run all examples
./examples/claude_rag_system.py basic_rag - Run specific example

Environment Setup:
# For io.net models and embeddings:
export API_KEY="your-io-net-api-key"
export ANTHROPIC_MODEL="glm-4.6"

# For Z.ai models:
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-z-auth-token"
export ANTHROPIC_MODEL="glm-4.6"

# For embeddings (using io.net):
export EMBEDDING_MODEL="BAAI/bge-multilingual-gemma2"
"""

import anyio
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from kaygraph import Graph, AsyncNode
from kaygraph_claude_base import AsyncClaudeNode, ClaudeConfig


@dataclass
class Document:
    """Represents a document in the RAG system."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class RetrievalResult:
    """Result from document retrieval."""
    documents: List[Document]
    query_embedding: List[float]
    similarity_scores: List[float]


class EmbeddingService:
    """Service for generating embeddings using external APIs."""

    def __init__(self, api_key: str, base_url: str = "https://api.intelligence.io.solutions/api/v1", model: str = "BAAI/bge-multilingual-gemma2"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "input": text,
                "encoding_format": "float"
            }

            async with session.post(f"{self.base_url}/embeddings", json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["data"][0]["embedding"]
                else:
                    error_text = await response.text()
                    raise Exception(f"Embedding API error: {response.status} - {error_text}")

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts (batch processing)."""
        # Process in parallel for better performance
        tasks = [self.get_embedding(text) for text in texts]
        return await asyncio.gather(*tasks)


class DocumentStore:
    """In-memory document store with embedding support."""

    def __init__(self, embedding_service: EmbeddingService):
        self.documents: Dict[str, Document] = {}
        self.embedding_service = embedding_service

    async def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None) -> Document:
        """Add a document to the store."""
        embedding = await self.embedding_service.get_embedding(content)

        document = Document(
            id=doc_id,
            content=content,
            metadata=metadata or {},
            embedding=embedding
        )

        self.documents[doc_id] = document
        return document

    async def add_documents(self, documents: List[Tuple[str, str, Dict[str, Any]]]) -> List[Document]:
        """Add multiple documents to the store."""
        tasks = []
        for doc_id, content, metadata in documents:
            task = self.add_document(doc_id, content, metadata)
            tasks.append(task)

        return await asyncio.gather(*tasks)

    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> RetrievalResult:
        """Search for similar documents using cosine similarity."""
        if not self.documents:
            return RetrievalResult([], query_embedding, [])

        # Get all document embeddings
        doc_embeddings = []
        doc_list = []

        for doc in self.documents.values():
            if doc.embedding:
                doc_embeddings.append(doc.embedding)
                doc_list.append(doc)

        if not doc_embeddings:
            return RetrievalResult([], query_embedding, [])

        # Calculate cosine similarities
        query_embedding_np = np.array(query_embedding).reshape(1, -1)
        doc_embeddings_np = np.array(doc_embeddings)

        similarities = cosine_similarity(query_embedding_np, doc_embeddings_np)[0]

        # Sort by similarity and get top_k
        sorted_indices = np.argsort(similarities)[::-1][:top_k]

        retrieved_docs = []
        similarity_scores = []

        for idx in sorted_indices:
            retrieved_docs.append(doc_list[idx])
            similarity_scores.append(float(similarities[idx]))

        return RetrievalResult(retrieved_docs, query_embedding, similarity_scores)


class QueryEmbeddingNode(AsyncNode):
    """Generates embeddings for user queries."""

    def __init__(self, embedding_service: EmbeddingService, **kwargs):
        super().__init__(**kwargs)
        self.embedding_service = embedding_service

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Extract query from shared context."""
        return shared.get("query", "")

    async def exec(self, query: str) -> List[float]:
        """Generate embedding for the query."""
        return await self.embedding_service.get_embedding(query)

    async def post(self, shared: Dict[str, Any], prep_res: str, exec_res: List[float]) -> str:
        """Store query embedding."""
        shared["query_embedding"] = exec_res
        return "retrieve_documents"


class DocumentRetrievalNode(AsyncNode):
    """Retrieves relevant documents based on query embedding."""

    def __init__(self, document_store: DocumentStore, top_k: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.document_store = document_store
        self.top_k = top_k

    async def prep(self, shared: Dict[str, Any]) -> List[float]:
        """Get query embedding from shared context."""
        return shared.get("query_embedding", [])

    async def exec(self, query_embedding: List[float]) -> RetrievalResult:
        """Retrieve similar documents."""
        return self.document_store.search_similar(query_embedding, self.top_k)

    async def post(self, shared: Dict[str, Any], prep_res: List[float], exec_res: RetrievalResult) -> str:
        """Store retrieval results."""
        shared["retrieval_results"] = exec_res
        shared["retrieved_documents"] = exec_res.documents
        shared["similarity_scores"] = exec_res.similarity_scores
        return "generate_answer"


class ContextualAnswerNode(AsyncClaudeNode):
    """Generates answers based on retrieved documents."""

    def __init__(self, max_context_length: int = 4000, **kwargs):
        self.max_context_length = max_context_length
        prompt_template = """You are a helpful AI assistant that answers questions based on provided context. Use only the information from the retrieved documents to answer the question.

Question: {query}

Context Documents:
{context}

Please provide a comprehensive answer based on the context above. If the context doesn't contain enough information to fully answer the question, say so explicitly.

ANSWER:"""

        super().__init__(prompt_template=prompt_template, **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context from retrieved documents."""
        query = shared.get("query", "")
        retrieved_docs = shared.get("retrieved_documents", [])
        similarity_scores = shared.get("similarity_scores", [])

        # Format retrieved documents as context
        context_parts = []
        for i, (doc, score) in enumerate(zip(retrieved_docs, similarity_scores)):
            doc_text = f"Document {i+1} (Similarity: {score:.3f}):\n{doc.content}"
            if len(doc_text) > self.max_context_length // len(retrieved_docs):
                doc_text = doc_text[:self.max_context_length // len(retrieved_docs)] + "..."
            context_parts.append(doc_text)

        context = "\n\n".join(context_parts)

        return {
            "query": query,
            "context": context
        }

    async def exec(self, prepared_data: Dict[str, Any]) -> str:
        """Generate answer based on context."""
        formatted_prompt = self.prompt_template.format(**prepared_data)

        options = self.config.to_options()
        response_parts = []

        async for message in query(formatted_prompt, options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_parts.append(block.text)

        return "".join(response_parts)

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Store generated answer."""
        shared["answer"] = exec_res
        shared["context_used"] = prep_res["context"]
        return "default"


class SourceAttributionNode(AsyncNode):
    """Adds source attribution to the generated answer."""

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for source attribution."""
        return {
            "answer": shared.get("answer", ""),
            "documents": shared.get("retrieved_documents", []),
            "similarity_scores": shared.get("similarity_scores", [])
        }

    async def exec(self, data: Dict[str, Any]) -> str:
        """Add source attribution."""
        answer = data["answer"]
        documents = data["documents"]
        similarity_scores = data["similarity_scores"]

        # Create attribution section
        attribution = "\n\n--- Sources ---\n"
        for i, (doc, score) in enumerate(zip(documents, similarity_scores)):
            attribution += f"Source {i+1} (Similarity: {score:.3f}): {doc.metadata.get('title', doc.id)}\n"

        return answer + attribution

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> str:
        """Store attributed answer."""
        shared["attributed_answer"] = exec_res
        return "default"


async def example_basic_rag():
    """Example 1: Basic document Q&A system."""
    print("\n" + "="*60)
    print("Example 1: Basic RAG System")
    print("="*60)

    # Initialize services
    api_key = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjUwZjcxMTM1LTA4NDktNDcwMC04ZTkyLTgwMjllYWFhNzc0OSIsImV4cCI6NDkxNDkzNzMzNH0.HlbIBeZUwHyh9GZaWW1-oMro-vFu_TeHs748tRQ6wGxvJq-QvGB-H4tJjp2J3T7FpI0VdYEemGijDRawAGhK1A"

    embedding_service = EmbeddingService(
        api_key=api_key,
        model="BAAI/bge-multilingual-gemma2"
    )

    document_store = DocumentStore(embedding_service)

    # Sample documents
    sample_docs = [
        ("doc1", "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. Common techniques include supervised learning, unsupervised learning, and reinforcement learning.", {"title": "Introduction to Machine Learning", "category": "AI"}),
        ("doc2", "Deep learning uses neural networks with multiple layers to model complex patterns in data. Convolutional Neural Networks (CNNs) are particularly effective for image recognition tasks.", {"title": "Deep Learning Fundamentals", "category": "AI"}),
        ("doc3", "Natural Language Processing (NLP) enables computers to understand and generate human language. Modern NLP models like Transformers have revolutionized text understanding and generation.", {"title": "Natural Language Processing", "category": "NLP"}),
        ("doc4", "Computer vision allows machines to interpret and understand visual information from the world. Applications include facial recognition, object detection, and autonomous vehicles.", {"title": "Computer Vision Applications", "category": "CV"}),
        ("doc5", "Reinforcement learning involves training agents to make decisions by rewarding desired behaviors. It has been successfully applied to game playing, robotics, and control systems.", {"title": "Reinforcement Learning", "category": "AI"})
    ]

    try:
        print("Setting up document store...")
        # Add documents to the store
        await document_store.add_documents(sample_docs)
        print(f"Added {len(sample_docs)} documents to the store.\n")

        # Create RAG graph
        embedding_node = QueryEmbeddingNode(embedding_service)
        retrieval_node = DocumentRetrievalNode(document_store, top_k=3)
        answer_node = ContextualAnswerNode()
        attribution_node = SourceAttributionNode()

        rag_graph = Graph(nodes={
            "embed_query": embedding_node,
            "retrieve_docs": retrieval_node,
            "generate_answer": answer_node,
            "add_attribution": attribution_node
        })

        # Test queries
        test_queries = [
            "What is the difference between machine learning and deep learning?",
            "How do neural networks work in computer vision?",
            "What are the main types of machine learning?",
            "How is reinforcement learning used in real applications?"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Query {i} ---")
            print(f"Question: {query}")

            shared_context = {"query": query}

            # Run the RAG pipeline
            result = await rag_graph.run(
                start_node="embed_query",
                shared=shared_context
            )

            # Display results
            answer = shared_context.get("attributed_answer", shared_context.get("answer", "No answer generated"))
            retrieved_docs = shared_context.get("retrieved_documents", [])
            similarity_scores = shared_context.get("similarity_scores", [])

            print(f"\nAnswer: {answer}")

            print(f"\nRetrieved {len(retrieved_docs)} documents:")
            for j, (doc, score) in enumerate(zip(retrieved_docs, similarity_scores)):
                print(f"  {j+1}. {doc.metadata.get('title', doc.id)} (similarity: {score:.3f})")

    except Exception as e:
        print(f"Error in basic RAG example: {e}")


async def example_multi_source_rag():
    """Example 2: Multi-document source synthesis."""
    print("\n" + "="*60)
    print("Example 2: Multi-Source RAG System")
    print("="*60)

    # Initialize services
    api_key = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjUwZjcxMTM1LTA4NDktNDcwMC04ZTkyLTgwMjllYWFhNzc0OSIsImV4cCI6NDkxNDkzNzMzNH0.HlbIBeZUwHyh9GZaWW1-oMro-vFu_TeHs748tRQ6wGxvJq-QvGB-H4tJjp2J3T7FpI0VdYEemGijDRawAGhK1A"

    embedding_service = EmbeddingService(
        api_key=api_key,
        model="BAAI/bge-multilingual-gemma2"
    )

    document_store = DocumentStore(embedding_service)

    # Multi-source documents about climate change
    climate_docs = [
        ("climate1", "Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations are natural, human activities have been the main driver of climate change since the mid-20th century.", {"title": "Climate Change Overview", "source": "IPCC", "year": 2023}),
        ("climate2", "Greenhouse gases like carbon dioxide, methane, and nitrous oxide trap heat in the atmosphere. The burning of fossil fuels for energy is the largest source of greenhouse gas emissions.", {"title": "Greenhouse Gas Effect", "source": "NASA", "year": 2023}),
        ("climate3", "Renewable energy sources like solar, wind, and hydroelectric power can significantly reduce carbon emissions. Solar energy costs have decreased by 89% since 2010.", {"title": "Renewable Energy Solutions", "source": "IEA", "year": 2023}),
        ("climate4", "Electric vehicles produce zero tailpipe emissions and can reduce transportation emissions by up to 70% when powered by renewable energy.", {"title": "Electric Transportation", "source": "EPA", "year": 2023}),
        ("climate5", "Climate adaptation strategies include building sea walls, developing drought-resistant crops, and improving early warning systems for extreme weather events.", {"title": "Climate Adaptation", "source": "UNFCCC", "year": 2023}),
        ("climate6", "Carbon capture and storage technologies can remove CO2 from the atmosphere and store it underground, potentially removing up to 90% of CO2 emissions from power plants.", {"title": "Carbon Capture Technology", "source": "IEA", "year": 2023})
    ]

    try:
        print("Setting up multi-source document store...")
        await document_store.add_documents(climate_docs)
        print(f"Added {len(climate_docs)} climate-related documents.\n")

        # Create enhanced RAG graph with source synthesis
        class MultiSourceAnswerNode(AsyncClaudeNode):
            def __init__(self, **kwargs):
                prompt_template = """You are a climate science expert answering questions using multiple sources. Synthesize information from different sources to provide a comprehensive answer.

Question: {query}

Source Documents:
{context}

Provide a comprehensive answer that:
1. Directly addresses the question
2. Synthesizes information from multiple sources
3. Notes any consensus or disagreements between sources
4. Includes specific data or examples when available

ANSWER:"""
                super().__init__(prompt_template=prompt_template, **kwargs)

            async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
                query = shared.get("query", "")
                retrieved_docs = shared.get("retrieved_documents", [])
                similarity_scores = shared.get("similarity_scores", [])

                # Enhanced context with source information
                context_parts = []
                for i, (doc, score) in enumerate(zip(retrieved_docs, similarity_scores)):
                    source_info = f"Source: {doc.metadata.get('source', 'Unknown')} ({doc.metadata.get('title', doc.id)}, {doc.metadata.get('year', 'N/A')})"
                    doc_text = f"{source_info} (Relevance: {score:.3f}):\n{doc.content}"
                    context_parts.append(doc_text)

                context = "\n\n".join(context_parts)

                return {"query": query, "context": context}

        embedding_node = QueryEmbeddingNode(embedding_service)
        retrieval_node = DocumentRetrievalNode(document_store, top_k=4)
        answer_node = MultiSourceAnswerNode()

        multi_source_graph = Graph(nodes={
            "embed_query": embedding_node,
            "retrieve_docs": retrieval_node,
            "synthesize_answer": answer_node
        })

        # Complex multi-source queries
        complex_queries = [
            "What are the most effective strategies for combating climate change according to different sources?",
            "How do renewable energy and electric vehicles compare in their climate impact?",
            "What are the main causes of climate change and what solutions do different organizations propose?"
        ]

        for i, query in enumerate(complex_queries, 1):
            print(f"\n--- Complex Query {i} ---")
            print(f"Question: {query}")

            shared_context = {"query": query}

            result = await multi_source_graph.run(
                start_node="embed_query",
                shared=shared_context
            )

            answer = shared_context.get("answer", "No answer generated")
            retrieved_docs = shared_context.get("retrieved_documents", [])
            similarity_scores = shared_context.get("similarity_scores", [])

            print(f"\nSynthesized Answer: {answer}")

            print(f"\nSources Used:")
            unique_sources = set()
            for doc, score in zip(retrieved_docs, similarity_scores):
                source = doc.metadata.get('source', 'Unknown')
                if source not in unique_sources:
                    print(f"  • {doc.metadata.get('title', doc.id)} - {source} ({doc.metadata.get('year', 'N/A')})")
                    unique_sources.add(source)

    except Exception as e:
        print(f"Error in multi-source RAG example: {e}")


async def example_semantic_search():
    """Example 3: Advanced semantic search capabilities."""
    print("\n" + "="*60)
    print("Example 3: Advanced Semantic Search")
    print("="*60)

    # Initialize services
    api_key = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjUwZjcxMTM1LTA4NDktNDcwMC04ZTkyLTgwMjllYWFhNzc0OSIsImV4cCI6NDkxNDkzNzMzNH0.HlbIBeZUwHyh9GZaWW1-oMro-vFu_TeHs748tRQ6wGxvJq-QvGB-H4tJjp2J3T7FpI0VdYEemGijDRawAGhK1A"

    embedding_service = EmbeddingService(
        api_key=api_key,
        model="BAAI/bge-multilingual-gemma2"
    )

    document_store = DocumentStore(embedding_service)

    # Technical documents
    tech_docs = [
        ("tech1", "Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.", {"title": "Python Programming Language", "type": "programming", "difficulty": "beginner"}),
        ("tech2", "Machine learning algorithms can be categorized into supervised learning, unsupervised learning, and reinforcement learning. Each category has different applications and requirements.", {"title": "Machine Learning Categories", "type": "AI", "difficulty": "intermediate"}),
        ("tech3", "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes that process information using connectionist approaches.", {"title": "Neural Networks", "type": "AI", "difficulty": "advanced"}),
        ("tech4", "Data structures like arrays, linked lists, stacks, and queues are fundamental building blocks for organizing and storing data efficiently in computer programs.", {"title": "Data Structures", "type": "CS", "difficulty": "beginner"}),
        ("tech5", "Cloud computing provides on-demand access to computing resources over the internet. Major service models include IaaS, PaaS, and SaaS.", {"title": "Cloud Computing", "type": "infrastructure", "difficulty": "intermediate"}),
        ("tech6", "Blockchain technology enables secure, decentralized record-keeping through cryptographic hashing and distributed consensus mechanisms.", {"title": "Blockchain Technology", "type": "infrastructure", "difficulty": "advanced"})
    ]

    try:
        print("Setting up technical document store...")
        await document_store.add_documents(tech_docs)
        print(f"Added {len(tech_docs)} technical documents.\n")

        # Semantic search with different query types
        test_queries = [
            ("Simple concept", "What is Python programming?"),
            ("Complex technical query", "How do neural networks learn from data?"),
            ("Cross-domain query", "How can AI be used in cloud computing?"),
            ("Comparative query", "What's the difference between supervised and unsupervised learning?")
        ]

        for query_type, query in test_queries:
            print(f"\n--- {query_type.upper()} ---")
            print(f"Query: {query}")

            # Generate query embedding
            query_embedding = await embedding_service.get_embedding(query)

            # Retrieve similar documents
            results = document_store.search_similar(query_embedding, top_k=3)

            print(f"\nSemantic Search Results:")
            for i, (doc, score) in enumerate(zip(results.documents, results.similarity_scores)):
                print(f"  {i+1}. {doc.metadata.get('title', doc.id)}")
                print(f"     Type: {doc.metadata.get('type', 'Unknown')}")
                print(f"     Difficulty: {doc.metadata.get('difficulty', 'Unknown')}")
                print(f"     Similarity: {score:.3f}")
                print(f"     Preview: {doc.content[:100]}...")
                print()

    except Exception as e:
        print(f"Error in semantic search example: {e}")


async def main():
    """Run all examples."""
    examples = [
        ("basic_rag", "Basic RAG System"),
        ("multi_source_rag", "Multi-Source RAG System"),
        ("semantic_search", "Advanced Semantic Search"),
    ]

    # List available examples
    import sys
    if len(sys.argv) == 1:
        print("Available examples:")
        for example_id, description in examples:
            print(f"  {example_id} - {description}")
        print("\nUsage:")
        print("  python claude_rag_system.py all                    # Run all examples")
        print("  python claude_rag_system.py <example_name>       # Run specific example")
        print("\nNote: This example requires an io.net API key for embeddings.")
        return

    # Run specific example or all examples
    target = sys.argv[1] if len(sys.argv) > 1 else None

    if target == "all":
        for example_id, _ in examples:
            try:
                await globals()[f"example_{example_id}"]()
            except Exception as e:
                print(f"Error in {example_id}: {e}")
    elif target in [ex[0] for ex in examples]:
        try:
            await globals()[f"example_{target}"]()
        except Exception as e:
            print(f"Error in {target}: {e}")
    else:
        print(f"Unknown example: {target}")
        print("Available examples:", ", ".join([ex[0] for ex in examples]))


if __name__ == "__main__":
    anyio.run(main)