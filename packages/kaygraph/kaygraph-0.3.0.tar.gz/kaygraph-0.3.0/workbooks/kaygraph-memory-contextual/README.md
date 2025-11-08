# KayGraph Memory Contextual

Context-aware memory patterns that adapt based on situation, time, and environment.

## Overview

This workbook demonstrates how to build memory systems that understand and adapt to context, providing relevant information based on the current situation, temporal factors, and environmental conditions. Unlike simple persistent memory, contextual memory knows when and how to apply stored information.

## Features

- **Temporal Context** - Time-based memory relevance (morning routines, seasonal preferences)
- **Situational Awareness** - Adapt memory based on current task or activity
- **Location Context** - Location-aware memory retrieval
- **Emotional Context** - Consider emotional state in memory application
- **Task Context** - Project/task-specific memory isolation
- **Relationship Context** - Different memory access for different relationships
- **Dynamic Prioritization** - Context-based memory importance adjustment

## Quick Start

```bash
# Install dependencies
pip install kaygraph

# Run examples
python main.py

# Interactive mode
python main.py --interactive
```

## Architecture

```
Context Analysis → Memory Filtering → Relevance Scoring → Context Application
        ↓                  ↓                  ↓                    ↓
   Time/Location      Task/Project      Importance         Personalized
     Factors           Isolation         Adjustment          Response
```

## Examples

### Time-Based Context
```python
# Morning context
"Good morning!" 
→ Retrieves: morning routine preferences, coffee preferences, daily schedule

# Evening context  
"What should I do now?"
→ Retrieves: evening activities, dinner preferences, relaxation habits
```

### Task-Based Context
```python
# In coding context
"How should I handle this?"
→ Retrieves: coding best practices, project conventions, debugging tips

# In meeting context
"How should I handle this?"
→ Retrieves: meeting etiquette, presentation tips, stakeholder preferences
```

## Context Types

1. **Temporal Context**
   - Time of day
   - Day of week
   - Season
   - Special dates

2. **Activity Context**
   - Current task
   - Project scope
   - Work vs personal
   - Learning vs applying

3. **Environmental Context**
   - Location
   - Device being used
   - Network conditions
   - Available resources

4. **Social Context**
   - Who you're interacting with
   - Formality level
   - Relationship type
   - Communication channel

5. **Cognitive Context**
   - Mental load
   - Expertise level
   - Learning style
   - Current focus

## Use Cases

1. **Smart Assistants** - Provide context-appropriate suggestions
2. **Learning Systems** - Adapt to student's current learning context
3. **Productivity Tools** - Surface relevant information based on current work
4. **Health Applications** - Consider time, location, and activity for recommendations
5. **Customer Service** - Adapt responses based on customer context

## Implementation Details

- Context detection and classification
- Multi-dimensional relevance scoring
- Context-based memory filtering
- Temporal decay with context modifiers
- Context switching and preservation
- Context inheritance hierarchies

## Testing

```bash
# Run all tests
python main.py

# Test specific contexts
python main.py --example temporal
python main.py --example situational
python main.py --example emotional
```

## Context Management

- Automatic context detection
- Manual context override
- Context stacking (multiple active contexts)
- Context transitions
- Context history tracking

## Dependencies

- `kaygraph` - Core orchestration framework
- `sqlite3` - Context and memory storage
- `datetime` - Temporal context handling