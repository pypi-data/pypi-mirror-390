"""
Database models for conversation memory management.

This module provides SQLAlchemy models for persistent storage of conversations,
messages, user preferences, and context using SQLite or PostgreSQL.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import hashlib

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime,
    Float, Boolean, JSON, ForeignKey, Index, UniqueConstraint,
    select, and_, or_, desc
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
import numpy as np

logger = logging.getLogger(__name__)

Base = declarative_base()


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ConversationStatus(str, Enum):
    """Conversation status types."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Conversation(Base):
    """Conversation model for tracking conversation sessions."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    title = Column(String(500))
    status = Column(String(50), default=ConversationStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default=dict)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    context_windows = relationship("ContextWindow", back_populates="conversation", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
            "message_count": len(self.messages) if self.messages else 0
        }


class Message(Base):
    """Message model for storing individual messages."""
    __tablename__ = "messages"
    __table_args__ = (
        Index("idx_conversation_timestamp", "conversation_id", "timestamp"),
        Index("idx_content_hash", "content_hash"),
    )

    id = Column(Integer, primary_key=True)
    message_id = Column(String(255), unique=True, index=True, nullable=False)
    conversation_id = Column(String(255), ForeignKey("conversations.conversation_id"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64))  # SHA-256 hash for deduplication
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    token_count = Column(Integer)
    embedding = Column(JSON)  # Store as JSON array for simplicity
    metadata = Column(JSON, default=dict)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.content and not self.content_hash:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "token_count": self.token_count,
            "metadata": self.metadata
        }


class UserPreference(Base):
    """User preferences and settings."""
    __tablename__ = "user_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", "key", name="unique_user_key"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), index=True, nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(JSON)
    category = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ContextWindow(Base):
    """Context window for managing conversation context."""
    __tablename__ = "context_windows"
    __table_args__ = (
        Index("idx_conversation_active", "conversation_id", "is_active"),
    )

    id = Column(Integer, primary_key=True)
    window_id = Column(String(255), unique=True, index=True, nullable=False)
    conversation_id = Column(String(255), ForeignKey("conversations.conversation_id"), nullable=False)
    messages = Column(JSON)  # List of message IDs in the window
    summary = Column(Text)  # Summarized context if messages are compressed
    token_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversation = relationship("Conversation", back_populates="context_windows")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "window_id": self.window_id,
            "conversation_id": self.conversation_id,
            "messages": self.messages,
            "summary": self.summary,
            "token_count": self.token_count,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MemoryIndex(Base):
    """Semantic memory index for efficient retrieval."""
    __tablename__ = "memory_index"
    __table_args__ = (
        Index("idx_user_category", "user_id", "category"),
        Index("idx_importance_timestamp", "importance_score", "timestamp"),
    )

    id = Column(Integer, primary_key=True)
    memory_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50))  # fact, preference, context, etc.
    category = Column(String(100))
    embedding = Column(JSON)  # Vector embedding
    importance_score = Column(Float, default=0.5)
    access_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "memory_id": self.memory_id,
            "user_id": self.user_id,
            "content": self.content,
            "content_type": self.content_type,
            "category": self.category,
            "importance_score": self.importance_score,
            "access_count": self.access_count,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }


class DatabaseManager:
    """Database manager for handling connections and operations."""

    def __init__(self, database_url: str = "sqlite:///conversation_memory.db"):
        """
        Initialize database manager.

        Args:
            database_url: Database connection URL (SQLite or PostgreSQL)
        """
        self.database_url = database_url

        # Configure engine based on database type
        if database_url.startswith("sqlite"):
            # SQLite specific configuration
            connect_args = {"check_same_thread": False}
            poolclass = StaticPool
            self.engine = create_engine(
                database_url,
                connect_args=connect_args,
                poolclass=poolclass,
                echo=False
            )
        else:
            # PostgreSQL configuration
            self.engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                echo=False
            )

        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create tables
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Database initialized: {database_url}")

    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()

    def create_conversation(
        self,
        conversation_id: str,
        user_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """Create a new conversation."""
        with self.get_session() as session:
            conversation = Conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                title=title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                metadata=metadata or {}
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation

    def add_message(
        self,
        conversation_id: str,
        message_id: str,
        role: str,
        content: str,
        token_count: Optional[int] = None,
        embedding: Optional[List[float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """Add a message to a conversation."""
        with self.get_session() as session:
            message = Message(
                message_id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                token_count=token_count,
                embedding=embedding,
                metadata=metadata or {}
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            return message

    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for a conversation."""
        with self.get_session() as session:
            query = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()

    def search_memories(
        self,
        user_id: str,
        query_embedding: Optional[List[float]] = None,
        category: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryIndex]:
        """Search memories with optional semantic similarity."""
        with self.get_session() as session:
            query = session.query(MemoryIndex).filter(
                MemoryIndex.user_id == user_id
            )

            if category:
                query = query.filter(MemoryIndex.category == category)
            if content_type:
                query = query.filter(MemoryIndex.content_type == content_type)

            # Sort by importance and recency
            query = query.order_by(
                desc(MemoryIndex.importance_score),
                desc(MemoryIndex.timestamp)
            )

            memories = query.limit(limit * 2).all()  # Get more for embedding filtering

            # If embedding provided, calculate similarities
            if query_embedding and memories:
                similarities = []
                for memory in memories:
                    if memory.embedding:
                        # Calculate cosine similarity
                        mem_emb = np.array(memory.embedding)
                        query_emb = np.array(query_embedding)
                        similarity = np.dot(mem_emb, query_emb) / (
                            np.linalg.norm(mem_emb) * np.linalg.norm(query_emb)
                        )
                        similarities.append((memory, similarity))

                # Sort by similarity and return top results
                similarities.sort(key=lambda x: x[1], reverse=True)
                return [mem for mem, _ in similarities[:limit]]

            return memories[:limit]

    def update_user_preference(
        self,
        user_id: str,
        key: str,
        value: Any,
        category: Optional[str] = None
    ) -> UserPreference:
        """Update or create user preference."""
        with self.get_session() as session:
            preference = session.query(UserPreference).filter(
                and_(
                    UserPreference.user_id == user_id,
                    UserPreference.key == key
                )
            ).first()

            if preference:
                preference.value = value
                preference.updated_at = datetime.utcnow()
            else:
                preference = UserPreference(
                    user_id=user_id,
                    key=key,
                    value=value,
                    category=category
                )
                session.add(preference)

            session.commit()
            session.refresh(preference)
            return preference

    def get_user_preferences(
        self,
        user_id: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user preferences as a dictionary."""
        with self.get_session() as session:
            query = session.query(UserPreference).filter(
                UserPreference.user_id == user_id
            )
            if category:
                query = query.filter(UserPreference.category == category)

            preferences = query.all()
            return {pref.key: pref.value for pref in preferences}

    def create_context_window(
        self,
        conversation_id: str,
        window_id: str,
        message_ids: List[str],
        summary: Optional[str] = None,
        token_count: int = 0
    ) -> ContextWindow:
        """Create or update context window."""
        with self.get_session() as session:
            # Deactivate previous windows
            session.query(ContextWindow).filter(
                and_(
                    ContextWindow.conversation_id == conversation_id,
                    ContextWindow.is_active == True
                )
            ).update({"is_active": False})

            window = ContextWindow(
                window_id=window_id,
                conversation_id=conversation_id,
                messages=message_ids,
                summary=summary,
                token_count=token_count,
                is_active=True
            )
            session.add(window)
            session.commit()
            session.refresh(window)
            return window

    def get_active_context(self, conversation_id: str) -> Optional[ContextWindow]:
        """Get active context window for a conversation."""
        with self.get_session() as session:
            return session.query(ContextWindow).filter(
                and_(
                    ContextWindow.conversation_id == conversation_id,
                    ContextWindow.is_active == True
                )
            ).first()

    def cleanup_old_conversations(self, days: int = 30) -> int:
        """Archive old conversations."""
        with self.get_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            updated = session.query(Conversation).filter(
                and_(
                    Conversation.updated_at < cutoff_date,
                    Conversation.status == ConversationStatus.ACTIVE.value
                )
            ).update({"status": ConversationStatus.ARCHIVED.value})
            session.commit()
            return updated


# Singleton instance for easy access
_db_manager = None


def get_db_manager(database_url: Optional[str] = None) -> DatabaseManager:
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(database_url or "sqlite:///conversation_memory.db")
    return _db_manager


# Example usage
if __name__ == "__main__":
    from datetime import timedelta
    import uuid

    # Initialize database
    db = get_db_manager()

    # Create a conversation
    conv = db.create_conversation(
        conversation_id=str(uuid.uuid4()),
        user_id="user123",
        title="Test Conversation",
        metadata={"source": "test"}
    )
    print(f"Created conversation: {conv.to_dict()}")

    # Add messages
    msg = db.add_message(
        conversation_id=conv.conversation_id,
        message_id=str(uuid.uuid4()),
        role=MessageRole.USER.value,
        content="Hello, how are you?",
        token_count=5
    )
    print(f"Added message: {msg.to_dict()}")

    # Update preferences
    pref = db.update_user_preference(
        user_id="user123",
        key="language",
        value="en",
        category="system"
    )
    print(f"Updated preference: {pref.to_dict()}")

    # Get preferences
    prefs = db.get_user_preferences("user123")
    print(f"User preferences: {prefs}")