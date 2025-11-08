"""
Multi-tenant memory storage for collaborative teams.
"""

import sqlite3
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Set
from pathlib import Path

from models import (
    TeamMember, TeamMemory, TeamMemoryQuery, MemoryConflict,
    TeamMemoryStats, CrossTeamInsight, MemoryMigration,
    TeamRole, MemoryPermission, MemoryScope, MemoryType
)

logger = logging.getLogger(__name__)


class CollaborativeMemoryStore:
    """Multi-tenant memory store for team collaboration."""
    
    def __init__(self, db_path: str = "collaborative_memories.db"):
        """Initialize collaborative memory store."""
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with team support."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Team members table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS team_members (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                permissions TEXT NOT NULL,
                teams TEXT NOT NULL,
                projects TEXT NOT NULL,
                expertise_areas TEXT NOT NULL,
                joined_at TEXT NOT NULL,
                active BOOLEAN DEFAULT 1
            )
        """)
        
        # Team memories table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS team_memories (
                memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                scope TEXT NOT NULL,
                author_id TEXT NOT NULL,
                team_id TEXT,
                project_id TEXT,
                title TEXT DEFAULT '',
                summary TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                related_memories TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                last_modified TEXT NOT NULL,
                modified_by TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                confidence REAL DEFAULT 1.0,
                quality_score REAL DEFAULT 0.5,
                upvotes INTEGER DEFAULT 0,
                downvotes INTEGER DEFAULT 0,
                reviews TEXT DEFAULT '[]',
                validated BOOLEAN DEFAULT 0,
                validated_by TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed TEXT NOT NULL,
                shared_count INTEGER DEFAULT 0,
                context_tags TEXT DEFAULT '[]',
                expertise_areas TEXT DEFAULT '[]',
                similar_situations TEXT DEFAULT '[]'
            )
        """)
        
        # Memory conflicts table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_conflicts (
                conflict_id TEXT PRIMARY KEY,
                memory_ids TEXT NOT NULL,
                conflict_type TEXT NOT NULL,
                description TEXT NOT NULL,
                severity REAL NOT NULL,
                detected_at TEXT NOT NULL,
                resolved BOOLEAN DEFAULT 0,
                resolution TEXT DEFAULT '',
                resolver_id TEXT
            )
        """)
        
        # Cross-team insights table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cross_team_insights (
                insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_team_id TEXT NOT NULL,
                source_memory_ids TEXT NOT NULL,
                target_teams TEXT NOT NULL,
                shared_with TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                relevance_score REAL DEFAULT 0.5,
                impact_score REAL DEFAULT 0.0,
                acknowledgments TEXT DEFAULT '{}',
                implementations TEXT DEFAULT '[]',
                feedback TEXT DEFAULT '[]'
            )
        """)
        
        # Memory migrations table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_migrations (
                migration_id TEXT PRIMARY KEY,
                memory_id INTEGER NOT NULL,
                from_team TEXT NOT NULL,
                to_team TEXT NOT NULL,
                from_project TEXT,
                to_project TEXT,
                reason TEXT DEFAULT '',
                migrated_by TEXT NOT NULL,
                migrated_at TEXT NOT NULL,
                approved_by TEXT,
                original_scope TEXT NOT NULL,
                new_scope TEXT NOT NULL,
                access_preserved BOOLEAN DEFAULT 1
            )
        """)
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_team_memories_team ON team_memories(team_id)",
            "CREATE INDEX IF NOT EXISTS idx_team_memories_project ON team_memories(project_id)",
            "CREATE INDEX IF NOT EXISTS idx_team_memories_author ON team_memories(author_id)",
            "CREATE INDEX IF NOT EXISTS idx_team_memories_type ON team_memories(memory_type)",
            "CREATE INDEX IF NOT EXISTS idx_team_memories_scope ON team_memories(scope)",
            "CREATE INDEX IF NOT EXISTS idx_team_memories_created ON team_memories(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_team_members_teams ON team_members(teams)",
            "CREATE INDEX IF NOT EXISTS idx_cross_insights_team ON cross_team_insights(source_team_id)"
        ]
        
        for index in indexes:
            self.conn.execute(index)
        
        self.conn.commit()
        logger.info(f"Initialized collaborative memory database at {self.db_path}")
    
    def add_team_member(self, member: TeamMember) -> bool:
        """Add or update a team member."""
        try:
            self.conn.execute("""
                INSERT OR REPLACE INTO team_members (
                    user_id, name, role, permissions, teams, projects,
                    expertise_areas, joined_at, active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                member.user_id,
                member.name,
                member.role.value,
                json.dumps(list(p.value for p in member.permissions)),
                json.dumps(list(member.teams)),
                json.dumps(list(member.projects)),
                json.dumps(list(member.expertise_areas)),
                member.joined_at.isoformat(),
                member.active
            ))
            
            self.conn.commit()
            logger.info(f"Added team member: {member.name} ({member.user_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding team member: {e}")
            return False
    
    def get_team_member(self, user_id: str) -> Optional[TeamMember]:
        """Get team member by user ID."""
        cursor = self.conn.execute("""
            SELECT * FROM team_members WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return self._row_to_team_member(row)
    
    def store_team_memory(self, memory: TeamMemory, requester_id: str) -> Optional[int]:
        """Store a team memory with permissions check."""
        # Verify permissions
        member = self.get_team_member(requester_id)
        if not member or not member.active:
            logger.warning(f"Unauthorized memory storage attempt by {requester_id}")
            return None
        
        # Check if member can write to this scope
        if not self._can_write_to_scope(member, memory.scope, memory.team_id, memory.project_id):
            logger.warning(f"User {requester_id} cannot write to scope {memory.scope.value}")
            return None
        
        # Check for duplicates
        duplicate_id = self._find_duplicate_memory(memory)
        if duplicate_id:
            logger.info(f"Duplicate memory found: {duplicate_id}")
            return duplicate_id
        
        try:
            cursor = self.conn.execute("""
                INSERT INTO team_memories (
                    content, memory_type, scope, author_id, team_id, project_id,
                    title, summary, tags, related_memories, created_at,
                    last_modified, modified_by, importance, confidence,
                    quality_score, upvotes, downvotes, reviews, validated,
                    validated_by, access_count, last_accessed, shared_count,
                    context_tags, expertise_areas, similar_situations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory.content,
                memory.memory_type.value,
                memory.scope.value,
                memory.author_id,
                memory.team_id,
                memory.project_id,
                memory.title,
                memory.summary,
                json.dumps(list(memory.tags)),
                json.dumps(memory.related_memories),
                memory.created_at.isoformat(),
                memory.last_modified.isoformat(),
                memory.modified_by,
                memory.importance,
                memory.confidence,
                memory.quality_score,
                memory.upvotes,
                memory.downvotes,
                json.dumps(memory.reviews),
                memory.validated,
                memory.validated_by,
                memory.access_count,
                memory.last_accessed.isoformat(),
                memory.shared_count,
                json.dumps(list(memory.context_tags)),
                json.dumps(list(memory.expertise_areas)),
                json.dumps(memory.similar_situations)
            ))
            
            self.conn.commit()
            memory_id = cursor.lastrowid
            
            # Check for conflicts
            self._check_memory_conflicts(memory_id, memory)
            
            logger.info(f"Stored team memory {memory_id} by {requester_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Error storing team memory: {e}")
            return None
    
    def retrieve_team_memories(self, query: TeamMemoryQuery) -> List[TeamMemory]:
        """Retrieve memories based on team query."""
        # Verify permissions
        member = self.get_team_member(query.requester_id)
        if not member or not member.active:
            logger.warning(f"Unauthorized memory retrieval by {query.requester_id}")
            return []
        
        # Build SQL query
        where_conditions = []
        params = []
        
        # Scope filtering based on permissions
        accessible_scopes = self._get_accessible_scopes(member, query.team_id, query.project_id)
        if accessible_scopes:
            scope_placeholders = ",".join(["?" for _ in accessible_scopes])
            where_conditions.append(f"scope IN ({scope_placeholders})")
            params.extend(accessible_scopes)
        else:
            return []  # No accessible scopes
        
        # Team/project filtering
        if query.team_id:
            where_conditions.append("(team_id = ? OR scope IN ('cross_team', 'organization'))")
            params.append(query.team_id)
        
        if query.project_id:
            where_conditions.append("(project_id = ? OR scope IN ('cross_team', 'organization'))")
            params.append(query.project_id)
        
        # Memory type filtering
        if query.memory_types:
            type_placeholders = ",".join(["?" for _ in query.memory_types])
            where_conditions.append(f"memory_type IN ({type_placeholders})")
            params.extend([t.value for t in query.memory_types])
        
        # Quality filtering
        if query.min_quality > 0:
            where_conditions.append("quality_score >= ?")
            params.append(query.min_quality)
        
        # Validation filtering
        if query.only_validated:
            where_conditions.append("validated = 1")
        
        # Exclude author's own memories
        if query.exclude_author:
            where_conditions.append("author_id != ?")
            params.append(query.requester_id)
        
        # Build final query
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Order by preference
        order_by = "quality_score DESC, importance DESC"
        if query.prefer_recent:
            order_by = "created_at DESC, " + order_by
        elif query.prefer_popular:
            order_by = "access_count DESC, " + order_by
        
        sql = f"""
            SELECT * FROM team_memories 
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT ?
        """
        params.append(query.max_results)
        
        cursor = self.conn.execute(sql, params)
        rows = cursor.fetchall()
        
        # Convert to memory objects and score
        scored_memories = []
        for row in rows:
            memory = self._row_to_team_memory(row)
            
            # Calculate relevance score
            score = memory.get_relevance_score(query.tags, query.expertise_areas)
            
            if score >= query.similarity_threshold:
                memory.relevance_score = score
                scored_memories.append((score, memory))
                
                # Update access tracking
                self._update_access_tracking(memory.memory_id, query.requester_id)
        
        # Sort by relevance score and return
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        memories = [m for _, m in scored_memories]
        
        logger.info(f"Retrieved {len(memories)} team memories for {query.requester_id}")
        return memories
    
    def create_cross_team_insight(self, insight: CrossTeamInsight, requester_id: str) -> Optional[int]:
        """Create cross-team insight for knowledge sharing."""
        # Verify permissions
        member = self.get_team_member(requester_id)
        if not member or not member.active:
            return None
        
        # Check if member can share cross-team insights
        if member.role not in [TeamRole.CROSS_TEAM, TeamRole.TEAM_LEAD] and \
           MemoryPermission.MODERATE not in member.permissions:
            logger.warning(f"User {requester_id} cannot create cross-team insights")
            return None
        
        try:
            cursor = self.conn.execute("""
                INSERT INTO cross_team_insights (
                    title, content, source_team_id, source_memory_ids,
                    target_teams, shared_with, created_at, created_by,
                    relevance_score, impact_score, acknowledgments,
                    implementations, feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight.title,
                insight.content,
                insight.source_team_id,
                json.dumps(insight.source_memory_ids),
                json.dumps(list(insight.target_teams)),
                json.dumps(list(insight.shared_with)),
                insight.created_at.isoformat(),
                insight.created_by,
                insight.relevance_score,
                insight.impact_score,
                json.dumps({k: v.isoformat() for k, v in insight.acknowledgments.items()}),
                json.dumps(insight.implementations),
                json.dumps(insight.feedback)
            ))
            
            self.conn.commit()
            insight_id = cursor.lastrowid
            
            logger.info(f"Created cross-team insight {insight_id} by {requester_id}")
            return insight_id
            
        except Exception as e:
            logger.error(f"Error creating cross-team insight: {e}")
            return None
    
    def get_team_stats(self, team_id: str, requester_id: str) -> Optional[TeamMemoryStats]:
        """Get team memory statistics."""
        # Verify permissions
        member = self.get_team_member(requester_id)
        if not member or not member.active or team_id not in member.teams:
            return None
        
        try:
            # Basic counts
            cursor = self.conn.execute("""
                SELECT COUNT(*) as total FROM team_memories 
                WHERE team_id = ?
            """, (team_id,))
            total_memories = cursor.fetchone()['total']
            
            # Memory types distribution
            cursor = self.conn.execute("""
                SELECT memory_type, COUNT(*) as count FROM team_memories 
                WHERE team_id = ?
                GROUP BY memory_type
            """, (team_id,))
            memories_by_type = {row['memory_type']: row['count'] for row in cursor.fetchall()}
            
            # Memories by member
            cursor = self.conn.execute("""
                SELECT author_id, COUNT(*) as count FROM team_memories 
                WHERE team_id = ?
                GROUP BY author_id
            """, (team_id,))
            memories_by_member = {row['author_id']: row['count'] for row in cursor.fetchall()}
            
            # Quality metrics
            cursor = self.conn.execute("""
                SELECT AVG(quality_score) as avg_quality,
                       SUM(CASE WHEN validated = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as validated_pct
                FROM team_memories 
                WHERE team_id = ?
            """, (team_id,))
            row = cursor.fetchone()
            avg_quality = row['avg_quality'] or 0.0
            validated_pct = row['validated_pct'] or 0.0
            
            # Recent memories
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            cursor = self.conn.execute("""
                SELECT 
                    SUM(CASE WHEN created_at >= ? THEN 1 ELSE 0 END) as week_count,
                    SUM(CASE WHEN created_at >= ? THEN 1 ELSE 0 END) as month_count
                FROM team_memories 
                WHERE team_id = ?
            """, (week_ago, month_ago, team_id))
            row = cursor.fetchone()
            
            stats = TeamMemoryStats(
                team_id=team_id,
                total_memories=total_memories,
                memories_by_type=memories_by_type,
                memories_by_member=memories_by_member,
                avg_quality_score=avg_quality,
                validated_percentage=validated_pct,
                memories_this_week=row['week_count'] or 0,
                memories_this_month=row['month_count'] or 0,
                active_contributors=len(memories_by_member)
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting team stats: {e}")
            return None
    
    def _find_duplicate_memory(self, memory: TeamMemory) -> Optional[int]:
        """Find duplicate memory by content hash."""
        content_hash = hashlib.md5(memory.content.encode()).hexdigest()
        
        cursor = self.conn.execute("""
            SELECT memory_id FROM team_memories 
            WHERE team_id = ? AND memory_type = ? AND 
                  SUBSTR(HEX(content), 1, 32) = UPPER(?)
        """, (memory.team_id, memory.memory_type.value, content_hash))
        
        row = cursor.fetchone()
        return row['memory_id'] if row else None
    
    def _can_write_to_scope(self, member: TeamMember, scope: MemoryScope,
                          team_id: str = None, project_id: str = None) -> bool:
        """Check if member can write to given scope."""
        if MemoryPermission.WRITE not in member.permissions:
            return False
        
        return member.can_access(scope, team_id, project_id)
    
    def _get_accessible_scopes(self, member: TeamMember, team_id: str = None,
                              project_id: str = None) -> List[str]:
        """Get scopes accessible to member."""
        scopes = []
        
        for scope in MemoryScope:
            if member.can_access(scope, team_id, project_id):
                scopes.append(scope.value)
        
        return scopes
    
    def _check_memory_conflicts(self, memory_id: int, memory: TeamMemory):
        """Check for conflicts with existing memories."""
        # Simple conflict detection based on contradictory content
        # In a real implementation, this could use NLP techniques
        
        # Look for memories with similar content but different conclusions
        cursor = self.conn.execute("""
            SELECT memory_id, content FROM team_memories 
            WHERE team_id = ? AND memory_type = ? AND memory_id != ?
            AND scope IN ('team', 'project')
        """, (memory.team_id, memory.memory_type.value, memory_id))
        
        for row in cursor.fetchall():
            # Simple contradiction detection (could be enhanced)
            if self._detect_contradiction(memory.content, row['content']):
                conflict = MemoryConflict(
                    conflict_id=f"conflict_{memory_id}_{row['memory_id']}",
                    memory_ids=[memory_id, row['memory_id']],
                    conflict_type="contradiction",
                    description=f"Potential contradiction between memories {memory_id} and {row['memory_id']}",
                    severity=0.5
                )
                self._store_conflict(conflict)
    
    def _detect_contradiction(self, content1: str, content2: str) -> bool:
        """Simple contradiction detection."""
        # This is a placeholder - in practice, you'd use NLP
        negative_pairs = [
            ("should", "should not"),
            ("works", "doesn't work"),
            ("good", "bad"),
            ("effective", "ineffective")
        ]
        
        for pos, neg in negative_pairs:
            if pos in content1.lower() and neg in content2.lower():
                return True
            if neg in content1.lower() and pos in content2.lower():
                return True
        
        return False
    
    def _store_conflict(self, conflict: MemoryConflict):
        """Store memory conflict."""
        try:
            self.conn.execute("""
                INSERT INTO memory_conflicts (
                    conflict_id, memory_ids, conflict_type, description,
                    severity, detected_at, resolved, resolution, resolver_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conflict.conflict_id,
                json.dumps(conflict.memory_ids),
                conflict.conflict_type,
                conflict.description,
                conflict.severity,
                conflict.detected_at.isoformat(),
                conflict.resolved,
                conflict.resolution,
                conflict.resolver_id
            ))
            self.conn.commit()
            logger.warning(f"Stored memory conflict: {conflict.conflict_id}")
            
        except Exception as e:
            logger.error(f"Error storing conflict: {e}")
    
    def _update_access_tracking(self, memory_id: int, user_id: str):
        """Update memory access tracking."""
        self.conn.execute("""
            UPDATE team_memories 
            SET access_count = access_count + 1,
                last_accessed = ?
            WHERE memory_id = ?
        """, (datetime.now().isoformat(), memory_id))
        self.conn.commit()
    
    def _row_to_team_member(self, row: sqlite3.Row) -> TeamMember:
        """Convert database row to TeamMember."""
        return TeamMember(
            user_id=row['user_id'],
            name=row['name'],
            role=TeamRole(row['role']),
            permissions={MemoryPermission(p) for p in json.loads(row['permissions'])},
            teams=set(json.loads(row['teams'])),
            projects=set(json.loads(row['projects'])),
            expertise_areas=set(json.loads(row['expertise_areas'])),
            joined_at=datetime.fromisoformat(row['joined_at']),
            active=bool(row['active'])
        )
    
    def _row_to_team_memory(self, row: sqlite3.Row) -> TeamMemory:
        """Convert database row to TeamMemory."""
        return TeamMemory(
            memory_id=row['memory_id'],
            content=row['content'],
            memory_type=MemoryType(row['memory_type']),
            scope=MemoryScope(row['scope']),
            author_id=row['author_id'],
            team_id=row['team_id'],
            project_id=row['project_id'],
            title=row['title'],
            summary=row['summary'],
            tags=set(json.loads(row['tags'])),
            related_memories=json.loads(row['related_memories']),
            created_at=datetime.fromisoformat(row['created_at']),
            last_modified=datetime.fromisoformat(row['last_modified']),
            modified_by=row['modified_by'],
            importance=row['importance'],
            confidence=row['confidence'],
            quality_score=row['quality_score'],
            upvotes=row['upvotes'],
            downvotes=row['downvotes'],
            reviews=json.loads(row['reviews']),
            validated=bool(row['validated']),
            validated_by=row['validated_by'],
            access_count=row['access_count'],
            last_accessed=datetime.fromisoformat(row['last_accessed']),
            shared_count=row['shared_count'],
            context_tags=set(json.loads(row['context_tags'])),
            expertise_areas=set(json.loads(row['expertise_areas'])),
            similar_situations=json.loads(row['similar_situations'])
        )
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Closed collaborative memory database")