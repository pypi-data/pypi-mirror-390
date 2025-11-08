"""
KayGraph nodes for collaborative memory workflows.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from kaygraph import Node
from models import (
    TeamMember, TeamMemory, TeamMemoryQuery, CrossTeamInsight,
    MemoryType, MemoryScope, TeamRole, MemoryPermission
)
from team_store import CollaborativeMemoryStore

logger = logging.getLogger(__name__)


class TeamMemoryRetrievalNode(Node):
    """Retrieve memories for team collaboration."""
    
    def __init__(self, store: CollaborativeMemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> TeamMemoryQuery:
        """Prepare team memory query."""
        return TeamMemoryQuery(
            query=shared.get("query", shared.get("message", "")),
            requester_id=shared.get("user_id", "unknown"),
            team_id=shared.get("team_id"),
            project_id=shared.get("project_id"),
            memory_types=[MemoryType(t) for t in shared.get("memory_types", [])],
            scopes=[MemoryScope(s) for s in shared.get("scopes", [])],
            tags=set(shared.get("tags", [])),
            expertise_areas=set(shared.get("expertise_areas", [])),
            min_quality=shared.get("min_quality", 0.0),
            only_validated=shared.get("only_validated", False),
            exclude_author=shared.get("exclude_author", False),
            max_results=shared.get("max_results", 10),
            similarity_threshold=shared.get("similarity_threshold", 0.3),
            include_cross_team=shared.get("include_cross_team", True),
            prefer_team_memories=shared.get("prefer_team_memories", True),
            prefer_recent=shared.get("prefer_recent", False),
            prefer_popular=shared.get("prefer_popular", False)
        )
    
    def exec(self, query: TeamMemoryQuery) -> List[TeamMemory]:
        """Retrieve team memories."""
        memories = self.store.retrieve_team_memories(query)
        
        logger.info(f"Retrieved {len(memories)} team memories for {query.requester_id}")
        for mem in memories[:3]:  # Log top 3
            logger.debug(f"  - {mem.title or mem.content[:50]}... (score: {mem.relevance_score:.2f})")
        
        return memories
    
    def post(self, shared: Dict[str, Any], prep_res: TeamMemoryQuery, 
             exec_res: List[TeamMemory]) -> Optional[str]:
        """Store retrieved memories."""
        shared["team_memories"] = exec_res
        shared["memory_summaries"] = [
            {
                "id": m.memory_id,
                "title": m.title,
                "content": m.content[:200] + "..." if len(m.content) > 200 else m.content,
                "author": m.author_id,
                "type": m.memory_type.value,
                "score": m.relevance_score,
                "team": m.team_id,
                "validated": m.validated
            }
            for m in exec_res
        ]
        return None


class TeamMemoryStorageNode(Node):
    """Store new team memories."""
    
    def __init__(self, store: CollaborativeMemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> Optional[TeamMemory]:
        """Prepare team memory for storage."""
        content = shared.get("memory_content") or shared.get("message", "")
        if not content:
            return None
        
        user_id = shared.get("user_id", "unknown")
        
        # Extract or generate metadata
        memory = TeamMemory(
            content=content,
            memory_type=MemoryType(shared.get("memory_type", "experience")),
            scope=MemoryScope(shared.get("scope", "team")),
            author_id=user_id,
            team_id=shared.get("team_id"),
            project_id=shared.get("project_id"),
            title=shared.get("title", ""),
            summary=shared.get("summary", ""),
            tags=set(shared.get("tags", [])),
            importance=shared.get("importance", 0.5),
            confidence=shared.get("confidence", 1.0),
            expertise_areas=set(shared.get("expertise_areas", [])),
            context_tags=set(shared.get("context_tags", [])),
            modified_by=user_id
        )
        
        # Auto-detect memory type if not specified
        if not shared.get("memory_type"):
            memory.memory_type = self._detect_memory_type(content)
        
        # Auto-generate title if not provided
        if not memory.title:
            memory.title = self._generate_title(content)
        
        return memory
    
    def exec(self, memory: Optional[TeamMemory]) -> Optional[int]:
        """Store team memory."""
        if not memory:
            return None
        
        memory_id = self.store.store_team_memory(memory, memory.author_id)
        
        if memory_id:
            logger.info(f"Stored team memory {memory_id}: {memory.title}")
        else:
            logger.warning(f"Failed to store team memory by {memory.author_id}")
        
        return memory_id
    
    def post(self, shared: Dict[str, Any], prep_res: Optional[TeamMemory], 
             exec_res: Optional[int]) -> Optional[str]:
        """Update shared state."""
        if exec_res:
            shared["stored_memory_id"] = exec_res
            shared["memory_stored"] = True
        else:
            shared["memory_stored"] = False
        return None
    
    def _detect_memory_type(self, content: str) -> MemoryType:
        """Auto-detect memory type from content."""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["decided", "decision", "chose", "agreed"]):
            return MemoryType.DECISION
        elif any(word in content_lower for word in ["learned", "discovered", "found out"]):
            return MemoryType.LESSON_LEARNED
        elif any(word in content_lower for word in ["should", "recommend", "best practice"]):
            return MemoryType.BEST_PRACTICE
        elif any(word in content_lower for word in ["problem", "issue", "bug", "error"]):
            return MemoryType.ISSUE
        elif any(word in content_lower for word in ["solution", "fixed", "resolved"]):
            return MemoryType.SOLUTION
        elif any(word in content_lower for word in ["pattern", "always", "usually"]):
            return MemoryType.PATTERN
        elif any(word in content_lower for word in ["insight", "realized", "understand"]):
            return MemoryType.INSIGHT
        else:
            return MemoryType.EXPERIENCE
    
    def _generate_title(self, content: str) -> str:
        """Generate title from content."""
        # Simple title generation - take first sentence or first 50 chars
        sentences = content.split('.')
        if sentences:
            title = sentences[0].strip()
            if len(title) > 50:
                title = title[:47] + "..."
            return title
        
        return content[:47] + "..." if len(content) > 50 else content


class CrossTeamSharingNode(Node):
    """Share insights across teams."""
    
    def __init__(self, store: CollaborativeMemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> Optional[CrossTeamInsight]:
        """Prepare cross-team insight."""
        source_memories = shared.get("team_memories", [])
        if not source_memories:
            return None
        
        # Select high-value memories for sharing
        shareable_memories = [
            m for m in source_memories 
            if m.quality_score > 0.7 and m.importance > 0.6 and m.validated
        ]
        
        if not shareable_memories:
            return None
        
        # Create insight from top memories
        top_memory = max(shareable_memories, key=lambda m: m.quality_score + m.importance)
        
        insight = CrossTeamInsight(
            title=f"Insight from {shared.get('team_id', 'team')}: {top_memory.title}",
            content=self._synthesize_insight(shareable_memories),
            source_team_id=shared.get("team_id", "unknown"),
            source_memory_ids=[m.memory_id for m in shareable_memories],
            target_teams=set(shared.get("target_teams", [])),
            created_by=shared.get("user_id", "unknown"),
            relevance_score=sum(m.quality_score for m in shareable_memories) / len(shareable_memories)
        )
        
        return insight
    
    def exec(self, insight: Optional[CrossTeamInsight]) -> Optional[int]:
        """Share insight across teams."""
        if not insight:
            return None
        
        insight_id = self.store.create_cross_team_insight(insight, insight.created_by)
        
        if insight_id:
            logger.info(f"Created cross-team insight {insight_id}")
        else:
            logger.warning(f"Failed to create cross-team insight")
        
        return insight_id
    
    def post(self, shared: Dict[str, Any], prep_res: Optional[CrossTeamInsight], 
             exec_res: Optional[int]) -> Optional[str]:
        """Store sharing result."""
        if exec_res:
            shared["shared_insight_id"] = exec_res
            shared["insight_shared"] = True
        else:
            shared["insight_shared"] = False
        return None
    
    def _synthesize_insight(self, memories: List[TeamMemory]) -> str:
        """Synthesize multiple memories into an insight."""
        from utils.call_llm import call_llm
        
        # Build context from memories
        memory_context = ""
        for i, memory in enumerate(memories, 1):
            memory_context += f"\n{i}. [{memory.memory_type.value}] {memory.content}"
        
        prompt = f"""Synthesize the following team memories into a valuable cross-team insight:
{memory_context}

Create a concise insight that:
1. Identifies the key pattern or learning
2. Explains why it's valuable to other teams
3. Provides actionable guidance

Keep it under 300 words and focus on transferable knowledge."""
        
        system = "You are a knowledge synthesis expert helping teams share valuable insights."
        
        try:
            insight = call_llm(prompt, system)
            return insight
        except Exception as e:
            logger.warning(f"Failed to synthesize insight with LLM: {e}")
            # Fallback to simple synthesis
            return f"Key insight from {len(memories)} team experiences: " + \
                   " | ".join([m.content[:100] for m in memories[:3]])


class MemoryValidationNode(Node):
    """Validate and review team memories."""
    
    def __init__(self, store: CollaborativeMemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare validation data."""
        memories = shared.get("team_memories", [])
        return {
            "memories": memories,
            "validator_id": shared.get("user_id", "unknown"),
            "validation_type": shared.get("validation_type", "quality_check")
        }
    
    def exec(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate memories."""
        validations = []
        
        for memory in data["memories"]:
            validation = self._validate_memory(memory, data["validation_type"])
            validation["memory_id"] = memory.memory_id
            validation["validator_id"] = data["validator_id"]
            validations.append(validation)
        
        return validations
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: List[Dict[str, Any]]) -> Optional[str]:
        """Store validation results."""
        shared["memory_validations"] = exec_res
        
        # Count validations
        passed = sum(1 for v in exec_res if v["passed"])
        failed = len(exec_res) - passed
        
        shared["validation_summary"] = {
            "total": len(exec_res),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(exec_res) if exec_res else 0
        }
        
        logger.info(f"Validated {len(exec_res)} memories: {passed} passed, {failed} failed")
        return None
    
    def _validate_memory(self, memory: TeamMemory, validation_type: str) -> Dict[str, Any]:
        """Validate a single memory."""
        validation = {
            "type": validation_type,
            "passed": True,
            "issues": [],
            "score": 1.0,
            "recommendations": []
        }
        
        # Quality checks
        if validation_type == "quality_check":
            # Content length check
            if len(memory.content) < 20:
                validation["issues"].append("Content too short")
                validation["score"] -= 0.2
            
            # Title check
            if not memory.title:
                validation["issues"].append("Missing title")
                validation["score"] -= 0.1
            
            # Tags check
            if len(memory.tags) == 0:
                validation["issues"].append("No tags provided")
                validation["score"] -= 0.1
            
            # Expertise areas
            if len(memory.expertise_areas) == 0:
                validation["recommendations"].append("Consider adding expertise areas")
        
        # Completeness check
        elif validation_type == "completeness_check":
            required_fields = ["content", "title", "author_id", "memory_type"]
            for field in required_fields:
                if not getattr(memory, field, None):
                    validation["issues"].append(f"Missing {field}")
                    validation["score"] -= 0.25
        
        # Relevance check
        elif validation_type == "relevance_check":
            if memory.importance < 0.3:
                validation["issues"].append("Low importance score")
                validation["score"] -= 0.2
            
            if memory.quality_score < 0.5:
                validation["issues"].append("Low quality score")
                validation["score"] -= 0.2
        
        # Set overall pass/fail
        validation["passed"] = validation["score"] >= 0.7 and len(validation["issues"]) == 0
        
        return validation


class TeamStatsNode(Node):
    """Generate team memory statistics."""
    
    def __init__(self, store: CollaborativeMemoryStore, **kwargs):
        super().__init__(**kwargs)
        self.store = store
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare stats query."""
        return {
            "team_id": shared.get("team_id", ""),
            "requester_id": shared.get("user_id", "unknown")
        }
    
    def exec(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get team statistics."""
        if not data["team_id"]:
            return None
        
        stats = self.store.get_team_stats(data["team_id"], data["requester_id"])
        
        if stats:
            # Convert to dict for easier handling
            stats_dict = {
                "team_id": stats.team_id,
                "total_memories": stats.total_memories,
                "memories_by_type": stats.memories_by_type,
                "memories_by_member": stats.memories_by_member,
                "avg_quality_score": stats.avg_quality_score,
                "validated_percentage": stats.validated_percentage,
                "total_accesses": stats.total_accesses,
                "active_contributors": stats.active_contributors,
                "memories_this_week": stats.memories_this_week,
                "memories_this_month": stats.memories_this_month
            }
            
            logger.info(f"Generated stats for team {data['team_id']}: {stats.total_memories} memories")
            return stats_dict
        
        return None
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: Optional[Dict[str, Any]]) -> Optional[str]:
        """Store team statistics."""
        if exec_res:
            shared["team_stats"] = exec_res
            
            # Create summary text
            shared["stats_summary"] = self._format_stats_summary(exec_res)
        else:
            shared["team_stats"] = {}
            shared["stats_summary"] = "No statistics available"
        
        return None
    
    def _format_stats_summary(self, stats: Dict[str, Any]) -> str:
        """Format statistics for display."""
        summary = f"""Team Memory Statistics for {stats['team_id']}:

📊 Overview:
• Total memories: {stats['total_memories']}
• Active contributors: {stats['active_contributors']}
• Average quality: {stats['avg_quality_score']:.1f}/5.0
• Validated: {stats['validated_percentage']:.1f}%

📈 Activity:
• This week: {stats['memories_this_week']} new memories
• This month: {stats['memories_this_month']} new memories

🏷️ Memory Types:"""
        
        for mem_type, count in stats['memories_by_type'].items():
            summary += f"\n• {mem_type.replace('_', ' ').title()}: {count}"
        
        return summary


class MemoryExtractionNode(Node):
    """Extract memories from conversation or content."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare content for memory extraction."""
        return {
            "content": shared.get("message", "") or shared.get("content", ""),
            "user_id": shared.get("user_id", "unknown"),
            "context": shared.get("conversation_context", ""),
            "team_id": shared.get("team_id"),
            "project_id": shared.get("project_id")
        }
    
    def exec(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract potential memories from content."""
        from utils.call_llm import call_llm
        
        if not data["content"]:
            return []
        
        prompt = f"""Analyze this content and extract valuable team memories:

Content: {data['content']}
Context: {data['context']}

Extract memories that would be valuable for a team to remember, such as:
- Decisions made and reasoning
- Lessons learned from experiences
- Best practices discovered
- Problems encountered and solutions
- Insights or patterns identified
- Important facts or information

For each memory, provide:
1. Content (the actual memory text)
2. Type (decision, lesson_learned, best_practice, issue, solution, pattern, insight, experience)
3. Title (short descriptive title)
4. Importance (0.1-1.0 scale)
5. Tags (relevant keywords)

Return as a JSON list. Only extract memories that would be genuinely useful for future reference."""
        
        system = "You are a memory extraction expert. Extract only high-value, actionable memories that teams would benefit from remembering."
        
        try:
            response = call_llm(prompt, system)
            
            # Try to parse JSON response
            import json
            # Clean response if it has markdown formatting
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1]
            
            memories = json.loads(response.strip())
            
            # Validate and enhance extracted memories
            processed_memories = []
            for memory in memories:
                if isinstance(memory, dict) and "content" in memory:
                    processed_memory = {
                        "content": memory.get("content", ""),
                        "memory_type": memory.get("type", "experience"),
                        "title": memory.get("title", ""),
                        "importance": float(memory.get("importance", 0.5)),
                        "tags": memory.get("tags", []),
                        "user_id": data["user_id"],
                        "team_id": data["team_id"],
                        "project_id": data["project_id"]
                    }
                    processed_memories.append(processed_memory)
            
            logger.info(f"Extracted {len(processed_memories)} memories from content")
            return processed_memories
            
        except Exception as e:
            logger.warning(f"Failed to extract memories with LLM: {e}")
            
            # Fallback: simple rule-based extraction
            return self._simple_memory_extraction(data)
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], 
             exec_res: List[Dict[str, Any]]) -> Optional[str]:
        """Store extracted memories."""
        shared["extracted_memories"] = exec_res
        shared["extraction_count"] = len(exec_res)
        
        if exec_res:
            logger.info(f"Extracted {len(exec_res)} potential memories")
        
        return None
    
    def _simple_memory_extraction(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simple rule-based memory extraction."""
        content = data["content"].lower()
        memories = []
        
        # Look for decision patterns
        if any(word in content for word in ["decided", "chose", "agreed", "conclusion"]):
            memories.append({
                "content": data["content"],
                "memory_type": "decision",
                "title": "Team Decision",
                "importance": 0.7,
                "tags": ["decision"],
                "user_id": data["user_id"],
                "team_id": data["team_id"],
                "project_id": data["project_id"]
            })
        
        # Look for lesson patterns
        if any(word in content for word in ["learned", "mistake", "next time"]):
            memories.append({
                "content": data["content"],
                "memory_type": "lesson_learned",
                "title": "Lesson Learned",
                "importance": 0.8,
                "tags": ["lesson", "learning"],
                "user_id": data["user_id"],
                "team_id": data["team_id"],
                "project_id": data["project_id"]
            })
        
        return memories