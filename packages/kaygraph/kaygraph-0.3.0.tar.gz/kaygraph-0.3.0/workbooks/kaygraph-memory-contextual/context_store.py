"""
Context-aware memory storage and retrieval.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

from models import (
    ContextualMemory, ContextVector, ContextualQuery,
    TimeContext, ActivityContext, EmotionalContext,
    LocationContext, RelationshipContext, ContextHistory
)

logger = logging.getLogger(__name__)


class ContextualMemoryStore:
    """Store and retrieve memories with context awareness."""
    
    def __init__(self, db_path: str = "contextual_memories.db"):
        """Initialize contextual memory store."""
        self.db_path = db_path
        self.conn = None
        self.init_database()
        self.context_histories: Dict[str, ContextHistory] = {}
    
    def init_database(self):
        """Initialize SQLite database with context support."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create contextual memories table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS contextual_memories (
                memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                context_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                relevance_score REAL DEFAULT 1.0,
                importance REAL DEFAULT 0.5,
                valid_contexts TEXT,
                invalid_contexts TEXT
            )
        """)
        
        # Create context history table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS context_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                context_json TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Create indexes
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON contextual_memories(created_at)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_context 
            ON context_history(user_id, timestamp)
        """)
        
        self.conn.commit()
        logger.info(f"Initialized contextual memory database at {self.db_path}")
    
    def store_memory(self, memory: ContextualMemory) -> int:
        """Store a contextual memory."""
        cursor = self.conn.execute("""
            INSERT INTO contextual_memories (
                content, context_json, created_at, last_accessed,
                access_count, relevance_score, importance,
                valid_contexts, invalid_contexts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.content,
            self._context_to_json(memory.context),
            memory.created_at.isoformat(),
            memory.last_accessed.isoformat(),
            memory.access_count,
            memory.relevance_score,
            memory.importance,
            json.dumps([self._context_to_dict(c) for c in memory.valid_contexts]),
            json.dumps([self._context_to_dict(c) for c in memory.invalid_contexts])
        ))
        
        self.conn.commit()
        memory_id = cursor.lastrowid
        logger.info(f"Stored contextual memory {memory_id}")
        return memory_id
    
    def retrieve_memories(self, query: ContextualQuery) -> List[ContextualMemory]:
        """Retrieve memories based on context."""
        # Get all memories
        cursor = self.conn.execute("""
            SELECT * FROM contextual_memories 
            ORDER BY importance DESC, last_accessed DESC
        """)
        rows = cursor.fetchall()
        
        # Score and filter memories
        scored_memories = []
        for row in rows:
            memory = self._row_to_memory(row)
            
            # Calculate relevance score
            score = self._calculate_relevance(memory, query)
            
            if score > query.similarity_threshold:
                memory.relevance_score = score
                scored_memories.append((score, memory))
                
                # Update access count
                self.conn.execute("""
                    UPDATE contextual_memories 
                    SET access_count = access_count + 1,
                        last_accessed = ?
                    WHERE memory_id = ?
                """, (datetime.now().isoformat(), memory.memory_id))
        
        self.conn.commit()
        
        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        memories = [m for _, m in scored_memories[:query.max_results]]
        
        logger.info(f"Retrieved {len(memories)} contextual memories")
        return memories
    
    def update_context(self, user_id: str, context: ContextVector):
        """Update current context for a user."""
        # Update history
        if user_id not in self.context_histories:
            self.context_histories[user_id] = ContextHistory(user_id)
        
        self.context_histories[user_id].add_context(context)
        
        # Store in database
        self.conn.execute("""
            INSERT INTO context_history (user_id, context_json, timestamp)
            VALUES (?, ?, ?)
        """, (
            user_id,
            self._context_to_json(context),
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
        logger.info(f"Updated context for user {user_id}")
    
    def get_current_context(self, user_id: str) -> Optional[ContextVector]:
        """Get current context for a user."""
        # Check in-memory history first
        if user_id in self.context_histories:
            return self.context_histories[user_id].get_current_context()
        
        # Load from database
        cursor = self.conn.execute("""
            SELECT context_json FROM context_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        if row:
            return self._json_to_context(row['context_json'])
        
        # Return default context
        return ContextVector(
            time_context=TimeContext.from_time(datetime.now()),
            location_context=LocationContext.VIRTUAL
        )
    
    def get_context_patterns(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Analyze context patterns for a user."""
        cutoff = datetime.now() - timedelta(days=days)
        
        cursor = self.conn.execute("""
            SELECT context_json, timestamp FROM context_history 
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp
        """, (user_id, cutoff.isoformat()))
        
        rows = cursor.fetchall()
        
        patterns = {
            "total_contexts": len(rows),
            "time_distribution": {},
            "activity_distribution": {},
            "common_transitions": [],
            "peak_hours": [],
            "avg_energy_level": 0,
            "avg_cognitive_load": 0
        }
        
        if not rows:
            return patterns
        
        # Analyze patterns
        time_counts = {}
        activity_counts = {}
        energy_sum = 0
        cognitive_sum = 0
        
        for row in rows:
            context = self._json_to_context(row['context_json'])
            
            # Time distribution
            if context.time_context:
                time_counts[context.time_context.value] = time_counts.get(
                    context.time_context.value, 0) + 1
            
            # Activity distribution
            if context.activity_context:
                activity_counts[context.activity_context.value] = activity_counts.get(
                    context.activity_context.value, 0) + 1
            
            # Average levels
            energy_sum += context.energy_level
            cognitive_sum += context.cognitive_load
        
        patterns["time_distribution"] = time_counts
        patterns["activity_distribution"] = activity_counts
        patterns["avg_energy_level"] = energy_sum / len(rows)
        patterns["avg_cognitive_load"] = cognitive_sum / len(rows)
        
        # Find peak hours
        hour_counts = {}
        for row in rows:
            timestamp = datetime.fromisoformat(row['timestamp'])
            hour = timestamp.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        patterns["peak_hours"] = [h for h, _ in sorted_hours[:3]]
        
        return patterns
    
    def _calculate_relevance(self, memory: ContextualMemory, 
                           query: ContextualQuery) -> float:
        """Calculate relevance score for a memory."""
        # Base similarity
        base_score = memory.context.similarity(query.context)
        
        # Apply weighted components
        weighted_score = 0
        weights_sum = 0
        
        # Time relevance
        if memory.context.time_context and query.context.time_context:
            time_match = 1.0 if memory.context.time_context == query.context.time_context else 0.3
            weighted_score += time_match * query.time_weight
            weights_sum += query.time_weight
        
        # Activity relevance
        if memory.context.activity_context and query.context.activity_context:
            activity_match = 1.0 if memory.context.activity_context == query.context.activity_context else 0.2
            weighted_score += activity_match * query.activity_weight
            weights_sum += query.activity_weight
        
        # Emotional relevance
        if memory.context.emotional_context and query.context.emotional_context:
            emotion_match = 1.0 if memory.context.emotional_context == query.context.emotional_context else 0.4
            weighted_score += emotion_match * query.emotional_weight
            weights_sum += query.emotional_weight
        
        # Location relevance
        if memory.context.location_context and query.context.location_context:
            location_match = 1.0 if memory.context.location_context == query.context.location_context else 0.3
            weighted_score += location_match * query.location_weight
            weights_sum += query.location_weight
        
        # Relationship relevance
        if memory.context.relationship_context and query.context.relationship_context:
            relationship_match = 1.0 if memory.context.relationship_context == query.context.relationship_context else 0.2
            weighted_score += relationship_match * query.relationship_weight
            weights_sum += query.relationship_weight
        
        # Combine scores
        if weights_sum > 0:
            weighted_score = weighted_score / weights_sum
            final_score = (base_score + weighted_score) / 2
        else:
            final_score = base_score
        
        # Factor in importance and recency
        recency_factor = self._calculate_recency_factor(memory.last_accessed)
        final_score = final_score * (0.7 + 0.3 * memory.importance) * recency_factor
        
        return min(1.0, final_score)
    
    def _calculate_recency_factor(self, last_accessed: datetime) -> float:
        """Calculate recency factor for scoring."""
        age_hours = (datetime.now() - last_accessed).total_seconds() / 3600
        
        if age_hours < 1:
            return 1.0
        elif age_hours < 24:
            return 0.9
        elif age_hours < 168:  # 1 week
            return 0.7
        elif age_hours < 720:  # 1 month
            return 0.5
        else:
            return 0.3
    
    def _context_to_json(self, context: ContextVector) -> str:
        """Convert context to JSON."""
        return json.dumps(self._context_to_dict(context))
    
    def _context_to_dict(self, context: ContextVector) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "time_context": context.time_context.value if context.time_context else None,
            "activity_context": context.activity_context.value if context.activity_context else None,
            "emotional_context": context.emotional_context.value if context.emotional_context else None,
            "location_context": context.location_context.value if context.location_context else None,
            "relationship_context": context.relationship_context.value if context.relationship_context else None,
            "energy_level": context.energy_level,
            "cognitive_load": context.cognitive_load,
            "formality_level": context.formality_level,
            "urgency_level": context.urgency_level,
            "tags": list(context.tags),
            "metadata": context.metadata
        }
    
    def _json_to_context(self, json_str: str) -> ContextVector:
        """Convert JSON to context."""
        data = json.loads(json_str)
        
        context = ContextVector()
        
        if data.get("time_context"):
            context.time_context = TimeContext(data["time_context"])
        if data.get("activity_context"):
            context.activity_context = ActivityContext(data["activity_context"])
        if data.get("emotional_context"):
            context.emotional_context = EmotionalContext(data["emotional_context"])
        if data.get("location_context"):
            context.location_context = LocationContext(data["location_context"])
        if data.get("relationship_context"):
            context.relationship_context = RelationshipContext(data["relationship_context"])
        
        context.energy_level = data.get("energy_level", 0.5)
        context.cognitive_load = data.get("cognitive_load", 0.5)
        context.formality_level = data.get("formality_level", 0.5)
        context.urgency_level = data.get("urgency_level", 0.5)
        context.tags = set(data.get("tags", []))
        context.metadata = data.get("metadata", {})
        
        return context
    
    def _row_to_memory(self, row: sqlite3.Row) -> ContextualMemory:
        """Convert database row to ContextualMemory."""
        memory = ContextualMemory(
            memory_id=row['memory_id'],
            content=row['content'],
            context=self._json_to_context(row['context_json']),
            created_at=datetime.fromisoformat(row['created_at']),
            last_accessed=datetime.fromisoformat(row['last_accessed']),
            access_count=row['access_count'],
            relevance_score=row['relevance_score'],
            importance=row['importance']
        )
        
        # Parse valid/invalid contexts
        if row['valid_contexts']:
            valid_data = json.loads(row['valid_contexts'])
            memory.valid_contexts = [
                self._json_to_context(json.dumps(ctx)) for ctx in valid_data
            ]
        
        if row['invalid_contexts']:
            invalid_data = json.loads(row['invalid_contexts'])
            memory.invalid_contexts = [
                self._json_to_context(json.dumps(ctx)) for ctx in invalid_data
            ]
        
        return memory
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info(f"Closed contextual memory database")