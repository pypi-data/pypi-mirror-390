"""
SQLite-based persistent memory storage.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

from models import (
    Memory, MemoryQuery, MemoryUpdate, MemoryStats,
    MemoryType, MemoryImportance, MemoryDecayConfig
)

logger = logging.getLogger(__name__)


class MemoryStore:
    """Persistent memory storage using SQLite."""
    
    def __init__(self, db_path: str = "memories.db"):
        """Initialize memory store."""
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create memories table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                importance INTEGER NOT NULL,
                metadata TEXT,
                embedding TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                accessed_at TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                decay_rate REAL DEFAULT 0.0,
                confidence REAL DEFAULT 1.0
            )
        """)
        
        # Create indexes for efficient queries
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id 
            ON memories(user_id)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type 
            ON memories(memory_type)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_importance 
            ON memories(importance)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON memories(created_at)
        """)
        
        self.conn.commit()
        logger.info(f"Initialized memory database at {self.db_path}")
    
    def store(self, memory: Memory) -> int:
        """Store a new memory."""
        # Check for duplicates
        existing = self._find_duplicate(memory)
        if existing:
            logger.info(f"Found duplicate memory {existing['memory_id']}, updating instead")
            return self.update(MemoryUpdate(
                memory_id=existing['memory_id'],
                content=memory.content,
                importance=memory.importance,
                metadata=memory.metadata
            ))
        
        # Insert new memory
        cursor = self.conn.execute("""
            INSERT INTO memories (
                user_id, content, memory_type, importance, metadata,
                embedding, created_at, updated_at, accessed_at,
                access_count, decay_rate, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.user_id,
            memory.content,
            memory.memory_type.value,
            memory.importance.value,
            json.dumps(memory.metadata),
            json.dumps(memory.embedding) if memory.embedding else None,
            memory.created_at.isoformat(),
            memory.updated_at.isoformat(),
            memory.accessed_at.isoformat(),
            memory.access_count,
            memory.decay_rate,
            memory.confidence
        ))
        
        self.conn.commit()
        memory_id = cursor.lastrowid
        logger.info(f"Stored memory {memory_id} for user {memory.user_id}")
        return memory_id
    
    def retrieve(self, query: MemoryQuery) -> List[Memory]:
        """Retrieve memories based on query."""
        # Build SQL query
        conditions = ["user_id = ?"]
        params = [query.user_id]
        
        if query.memory_types:
            placeholders = ",".join("?" * len(query.memory_types))
            conditions.append(f"memory_type IN ({placeholders})")
            params.extend([t.value for t in query.memory_types])
        
        if query.min_importance != MemoryImportance.TRIVIAL:
            conditions.append("importance >= ?")
            params.append(query.min_importance.value)
        
        if query.max_age_days:
            cutoff = datetime.now() - timedelta(days=query.max_age_days)
            conditions.append("created_at >= ?")
            params.append(cutoff.isoformat())
        
        where_clause = " AND ".join(conditions)
        
        # Execute query
        sql = f"""
            SELECT * FROM memories 
            WHERE {where_clause}
            ORDER BY importance DESC, accessed_at DESC
            LIMIT ?
        """
        params.append(query.limit)
        
        cursor = self.conn.execute(sql, params)
        rows = cursor.fetchall()
        
        # Convert to Memory objects
        memories = []
        for row in rows:
            memory = self._row_to_memory(row)
            
            # Update access count and time
            self.conn.execute("""
                UPDATE memories 
                SET access_count = access_count + 1,
                    accessed_at = ?
                WHERE memory_id = ?
            """, (datetime.now().isoformat(), memory.memory_id))
            
            memories.append(memory)
        
        self.conn.commit()
        
        # Apply semantic search if query text provided
        if query.query and memories:
            memories = self._semantic_filter(memories, query.query, query.semantic_threshold)
        
        logger.info(f"Retrieved {len(memories)} memories for user {query.user_id}")
        return memories
    
    def update(self, update: MemoryUpdate) -> int:
        """Update existing memory."""
        # Get current memory
        cursor = self.conn.execute(
            "SELECT * FROM memories WHERE memory_id = ?",
            (update.memory_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"Memory {update.memory_id} not found")
        
        # Build update
        updates = ["updated_at = ?"]
        params = [datetime.now().isoformat()]
        
        if update.content is not None:
            updates.append("content = ?")
            params.append(update.content)
        
        if update.importance is not None:
            updates.append("importance = ?")
            params.append(update.importance.value)
        
        if update.metadata is not None:
            if update.merge_metadata:
                # Merge with existing metadata
                current_metadata = json.loads(row['metadata'] or '{}')
                current_metadata.update(update.metadata)
                updates.append("metadata = ?")
                params.append(json.dumps(current_metadata))
            else:
                updates.append("metadata = ?")
                params.append(json.dumps(update.metadata))
        
        if update.increment_access:
            updates.append("access_count = access_count + 1")
            updates.append("accessed_at = ?")
            params.append(datetime.now().isoformat())
        
        # Execute update
        params.append(update.memory_id)
        sql = f"UPDATE memories SET {', '.join(updates)} WHERE memory_id = ?"
        self.conn.execute(sql, params)
        self.conn.commit()
        
        logger.info(f"Updated memory {update.memory_id}")
        return update.memory_id
    
    def delete(self, memory_id: int) -> bool:
        """Delete a memory."""
        cursor = self.conn.execute(
            "DELETE FROM memories WHERE memory_id = ?",
            (memory_id,)
        )
        self.conn.commit()
        
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Deleted memory {memory_id}")
        return deleted
    
    def consolidate(self, user_id: str, similarity_threshold: float = 0.8) -> int:
        """Consolidate similar memories."""
        # Get all memories for user
        cursor = self.conn.execute(
            "SELECT * FROM memories WHERE user_id = ? ORDER BY importance DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        
        if len(rows) < 2:
            return 0
        
        consolidated_count = 0
        processed = set()
        
        for i, row1 in enumerate(rows):
            if row1['memory_id'] in processed:
                continue
            
            memory1 = self._row_to_memory(row1)
            similar_memories = []
            
            for j, row2 in enumerate(rows[i+1:], i+1):
                if row2['memory_id'] in processed:
                    continue
                
                memory2 = self._row_to_memory(row2)
                
                # Simple similarity check (can be enhanced with embeddings)
                similarity = self._calculate_similarity(memory1.content, memory2.content)
                
                if similarity >= similarity_threshold:
                    similar_memories.append(memory2)
                    processed.add(row2['memory_id'])
            
            if similar_memories:
                # Consolidate memories
                consolidated = self._merge_memories(memory1, similar_memories)
                
                # Update original memory
                self.update(MemoryUpdate(
                    memory_id=memory1.memory_id,
                    content=consolidated.content,
                    importance=consolidated.importance,
                    metadata=consolidated.metadata
                ))
                
                # Delete duplicates
                for mem in similar_memories:
                    self.delete(mem.memory_id)
                
                consolidated_count += len(similar_memories)
        
        logger.info(f"Consolidated {consolidated_count} memories for user {user_id}")
        return consolidated_count
    
    def apply_decay(self, config: MemoryDecayConfig) -> int:
        """Apply decay to memories and prune low-confidence ones."""
        if not config.enable_decay:
            return 0
        
        now = datetime.now()
        pruned_count = 0
        
        # Get all memories
        cursor = self.conn.execute("SELECT * FROM memories")
        rows = cursor.fetchall()
        
        for row in rows:
            memory = self._row_to_memory(row)
            
            # Calculate age in days
            age_days = (now - memory.created_at).days
            if age_days < 1:
                continue
            
            # Calculate decay
            importance_mult = config.importance_multipliers.get(
                memory.importance.value, 1.0
            )
            access_reduction = config.access_bonus * memory.access_count
            
            decay = config.base_decay_rate * importance_mult * age_days
            decay = max(0, decay + access_reduction)
            
            # Update confidence
            new_confidence = max(config.min_confidence, memory.confidence - decay)
            
            if new_confidence <= config.min_confidence:
                # Prune memory
                self.delete(memory.memory_id)
                pruned_count += 1
            else:
                # Update confidence
                self.conn.execute(
                    "UPDATE memories SET confidence = ?, decay_rate = ? WHERE memory_id = ?",
                    (new_confidence, decay, memory.memory_id)
                )
        
        self.conn.commit()
        logger.info(f"Applied decay, pruned {pruned_count} memories")
        return pruned_count
    
    def get_stats(self) -> MemoryStats:
        """Get statistics about memory storage."""
        stats = MemoryStats()
        
        # Total memories
        cursor = self.conn.execute("SELECT COUNT(*) as count FROM memories")
        stats.total_memories = cursor.fetchone()['count']
        
        # By type
        cursor = self.conn.execute("""
            SELECT memory_type, COUNT(*) as count 
            FROM memories 
            GROUP BY memory_type
        """)
        for row in cursor:
            stats.memories_by_type[row['memory_type']] = row['count']
        
        # By user
        cursor = self.conn.execute("""
            SELECT user_id, COUNT(*) as count 
            FROM memories 
            GROUP BY user_id
        """)
        for row in cursor:
            stats.memories_by_user[row['user_id']] = row['count']
        
        # Averages
        cursor = self.conn.execute("""
            SELECT 
                AVG(access_count) as avg_access,
                AVG(confidence) as avg_confidence,
                MIN(created_at) as oldest,
                MAX(created_at) as newest
            FROM memories
        """)
        row = cursor.fetchone()
        if row:
            stats.average_access_count = row['avg_access'] or 0
            stats.average_confidence = row['avg_confidence'] or 0
            if row['oldest']:
                stats.oldest_memory = datetime.fromisoformat(row['oldest'])
            if row['newest']:
                stats.newest_memory = datetime.fromisoformat(row['newest'])
        
        # Database size
        stats.total_size_bytes = Path(self.db_path).stat().st_size
        
        return stats
    
    def _row_to_memory(self, row: sqlite3.Row) -> Memory:
        """Convert database row to Memory object."""
        data = dict(row)
        
        # Parse JSON fields
        if data['metadata']:
            data['metadata'] = json.loads(data['metadata'])
        else:
            data['metadata'] = {}
        
        if data['embedding']:
            data['embedding'] = json.loads(data['embedding'])
        
        # Parse datetime fields
        for field in ['created_at', 'updated_at', 'accessed_at']:
            if data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        # Parse enums
        data['memory_type'] = MemoryType(data['memory_type'])
        data['importance'] = MemoryImportance(data['importance'])
        
        return Memory(**data)
    
    def _find_duplicate(self, memory: Memory) -> Optional[Dict]:
        """Find duplicate memory."""
        # Simple duplicate check - can be enhanced
        cursor = self.conn.execute("""
            SELECT memory_id, content FROM memories 
            WHERE user_id = ? AND memory_type = ?
            ORDER BY created_at DESC
            LIMIT 20
        """, (memory.user_id, memory.memory_type.value))
        
        for row in cursor:
            similarity = self._calculate_similarity(memory.content, row['content'])
            if similarity > 0.9:  # High similarity threshold for duplicates
                return dict(row)
        
        return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts."""
        # Simple word overlap - can be enhanced with embeddings
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _semantic_filter(self, memories: List[Memory], query: str, 
                        threshold: float) -> List[Memory]:
        """Filter memories by semantic similarity to query."""
        # Simple keyword matching - can be enhanced with embeddings
        query_words = set(query.lower().split())
        
        scored_memories = []
        for memory in memories:
            memory_words = set(memory.content.lower().split())
            similarity = len(query_words & memory_words) / max(len(query_words), 1)
            
            if similarity >= threshold:
                scored_memories.append((similarity, memory))
        
        # Sort by similarity and return
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored_memories]
    
    def _merge_memories(self, primary: Memory, 
                       similar: List[Memory]) -> Memory:
        """Merge similar memories into one."""
        # Combine content
        all_content = [primary.content]
        all_content.extend([m.content for m in similar])
        
        # Create consolidated content
        consolidated_content = primary.content
        
        # Merge metadata
        merged_metadata = primary.metadata.copy()
        for mem in similar:
            merged_metadata.update(mem.metadata)
        
        # Use highest importance
        max_importance = max([primary.importance] + [m.importance for m in similar])
        
        # Calculate combined confidence
        total_confidence = primary.confidence
        for mem in similar:
            total_confidence += mem.confidence
        avg_confidence = total_confidence / (len(similar) + 1)
        
        return Memory(
            memory_id=primary.memory_id,
            user_id=primary.user_id,
            content=consolidated_content,
            memory_type=primary.memory_type,
            importance=max_importance,
            metadata=merged_metadata,
            confidence=avg_confidence
        )
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info(f"Closed memory database at {self.db_path}")