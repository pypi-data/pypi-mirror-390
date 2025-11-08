"""
Conversation Memory Workbook - Database-backed memory management for AI conversations.

This workbook provides production-ready components for managing conversation
history, context, and user preferences with SQLite/PostgreSQL persistence.
"""

from .nodes import (
    ConversationInitNode,
    MemoryRetrievalNode,
    ContextBuilderNode,
    ResponseGenerationNode,
    MemoryStorageNode,
    PreferenceUpdateNode,
    SessionManagementNode,
    SemanticSearchNode
)

from .graphs import (
    create_conversation_workflow,
    create_memory_search_workflow,
    create_context_refresh_workflow,
    create_session_recovery_workflow
)

from .models import (
    Conversation,
    Message,
    UserPreference,
    ContextWindow,
    DatabaseManager
)

__version__ = "0.1.0"

__all__ = [
    # Nodes
    "ConversationInitNode",
    "MemoryRetrievalNode",
    "ContextBuilderNode",
    "ResponseGenerationNode",
    "MemoryStorageNode",
    "PreferenceUpdateNode",
    "SessionManagementNode",
    "SemanticSearchNode",

    # Graphs
    "create_conversation_workflow",
    "create_memory_search_workflow",
    "create_context_refresh_workflow",
    "create_session_recovery_workflow",

    # Models
    "Conversation",
    "Message",
    "UserPreference",
    "ContextWindow",
    "DatabaseManager"
]