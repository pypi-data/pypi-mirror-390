---
created: 2025-10-26
lastUpdated: 2025-10-26T04:30:00
contextDate: 2025-10-26
tags: [spec, langfuse, testing, agentic-bots, implementation, dataset]
type: specification
status: active
version: 1.0.0
---

# ⚙️ SPECIFICATION: LangFuse Dataset Testing for Agentic Bots

> [!spec] **Implementation Specification**
> Complete specification for implementing LangFuse dataset-based testing and continuous improvement workflow for agentic chatbots with MCP servers.

**Version:** 1.0.0  
**Created:** October 26, 2025  
**Author:** Troy Larson  
**Purpose:** Enable systematic testing and weekly improvement of agentic chatbots

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Directory Structure](#directory-structure)
4. [Implementation Steps](#implementation-steps)
5. [Code Specifications](#code-specifications)
6. [Testing Procedures](#testing-procedures)
7. [Weekly Workflow](#weekly-workflow)
8. [Success Criteria](#success-criteria)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### **Problem Statement**
Agentic chatbots using LangGraph and MCP servers are inherently variable in their behavior. Traditional prompt engineering and "training" approaches fail because conversation depth and tool usage are **product design decisions**, not training problems.

### **Solution**
Implement a LangFuse dataset-based regression testing system that:
1. Defines expected behavior through golden examples
2. Tests agent behavior (not just text output) before deployment
3. Enables weekly improvement cycles based on real user failures
4. Provides objective quality gates for code changes

### **Target Systems**
- Agentic chatbots built with LangGraph
- Systems using MCP (Model Context Protocol) servers
- AI agents making tool calls (Beeminder, ClickUp, RescueTime, etc.)
- Any chatbot where consistent behavior matters more than consistent wording

---

## 💻 System Requirements

### **Dependencies**
```bash
# Required Python packages
langfuse>=2.0.0
langgraph>=0.1.0
pydantic>=2.0.0
pytest>=7.0.0
python-dotenv>=1.0.0
```

### **Environment Variables**
```bash
# .env file
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com  # or self-hosted URL

# Your AI provider
OPENAI_API_KEY=sk-...  # or ANTHROPIC_API_KEY, etc.

# MCP Server credentials (as needed)
BEEMINDER_AUTH_TOKEN=...
CLICKUP_API_KEY=...
# etc.
```

### **Project Structure Assumptions**
- Python 3.10+
- Git version control
- CI/CD pipeline (GitHub Actions, GitLab CI, etc.)
- Deployed on AWS, Vercel, or similar

---

## 📁 Directory Structure

```
your-agentic-bot/
├── .env                          # Environment variables
├── .env.example                  # Template for environment variables
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
│
├── src/                          # Source code
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── graph.py              # LangGraph agent definition
│   │   ├── nodes.py              # Agent nodes (functions)
│   │   ├── tools.py              # MCP tool definitions
│   │   └── prompts.py            # System prompts and few-shot examples
│   │
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── beeminder.py          # Beeminder MCP client
│   │   ├── clickup.py            # ClickUp MCP client
│   │   └── mocks.py              # Mock MCP responses for testing
│   │
│   └── config/
│       ├── __init__.py
│       ├── constants.py          # Constants (MAX_QUESTIONS, etc.)
│       └── schemas.py            # Pydantic models for structured outputs
│
├── scripts/                      # Utility scripts
│   ├── create_golden_dataset.py  # ✨ NEW: Create initial dataset
│   ├── run_dataset_test.py       # ✨ NEW: Test against dataset
│   ├── add_failures_to_dataset.py # ✨ NEW: Add production failures
│   ├── find_golden_candidates.py  # ✨ NEW: Find feedback-based candidates
│   └── deploy.sh                 # Deployment script
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_agent.py             # Agent unit tests
│   ├── test_tools.py             # Tool unit tests
│   └── fixtures/
│       └── mock_responses.py     # Mock MCP responses
│
└── datasets/                     # ✨ NEW: Dataset definitions
    ├── golden_examples.json      # Golden example definitions
    ├── README.md                 # Dataset documentation
    └── weekly_updates/           # Weekly additions
        ├── 2025-10-26.json
        ├── 2025-11-02.json
        └── ...
```

---

## 🔧 Implementation Steps

### **Phase 1: Setup LangFuse Integration (Day 1)**

#### **Step 1.1: Install Dependencies**

```bash
# Add to requirements.txt
langfuse>=2.0.0
python-dotenv>=1.0.0

# Install
pip install -r requirements.txt
```

#### **Step 1.2: Configure Environment**

```bash
# .env
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

#### **Step 1.3: Add Observation Decorator**

**File:** `src/agent/graph.py`

```python
from langfuse.decorators import observe, langfuse_context
from typing import TypedDict

class AgentState(TypedDict):
    messages: list
    user_id: str
    questions_asked: int
    logged: bool

@observe()
def handle_user_message(message: str, user_id: str) -> dict:
    """
    Main entry point for agent with LangFuse observation
    Every conversation automatically logged to LangFuse
    """
    # Initialize agent state
    state = AgentState(
        messages=[message],
        user_id=user_id,
        questions_asked=0,
        logged=False
    )
    
    # Run LangGraph agent
    result = your_langgraph_agent.invoke(state)
    
    # Add custom scores
    langfuse_context.score_current_trace(
        name="questions_asked",
        value=result["questions_asked"]
    )
    
    langfuse_context.score_current_trace(
        name="logged_successfully",
        value=result["logged"]
    )
    
    return result
```

**Acceptance Criteria:**
- ✅ Every conversation appears in LangFuse Dashboard → Traces
- ✅ Can view full conversation history
- ✅ Can see tool calls made
- ✅ Custom scores appear on traces

---

### **Phase 2: Define Product Constraints (Day 1)**

#### **Step 2.1: Create Constants File**

**File:** `src/config/constants.py`

```python
"""
Product design decisions enforced as constants
These are UX decisions, not training parameters
"""

# Conversation behavior
MAX_QUESTIONS = 2  # Maximum clarifying questions before action
MAX_AGENT_STEPS = 10  # Prevent infinite loops

# Tool call limits
MAX_RETRIES_PER_TOOL = 2  # Retry failed tool calls
TOOL_TIMEOUT_SECONDS = 30

# Response constraints
MIN_RESPONSE_LENGTH = 10  # Minimum characters in response
MAX_RESPONSE_LENGTH = 500  # Maximum characters in response

# Confidence thresholds
HIGH_CONFIDENCE = 0.8  # Log immediately
LOW_CONFIDENCE = 0.4  # Ask for clarification
```

**Acceptance Criteria:**
- ✅ All constants documented with purpose
- ✅ Constants imported and used in agent code
- ✅ Constants enforced in graph logic (not just prompts)

#### **Step 2.2: Implement User Feedback Mechanism** ⭐ **CRITICAL**

> [!warning] **Missing Component - Must Implement**
> User feedback is REQUIRED to identify which conversations should become golden examples. Without feedback, you're guessing which conversations were good.

**Why Feedback is Essential:**
1. **Dataset Curation** - Know which conversations to add as golden examples
2. **Quality Scoring** - Objective measure of agent performance
3. **Priority Bugs** - Users tell you what frustrates them
4. **Success Validation** - Prove improvements actually help users

##### **Option A: Simple Thumbs Up/Down (Recommended to Start)**

**Frontend (React/HTML):**

```typescript
// components/FeedbackButtons.tsx
import React, { useState } from 'react';
import { submitFeedback } from '../api/feedback';

interface FeedbackButtonsProps {
  conversationId: string;
  messageId: string;
}

export const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({ 
  conversationId, 
  messageId 
}) => {
  const [feedback, setFeedback] = useState<'positive' | 'negative' | null>(null);
  const [comment, setComment] = useState('');
  const [showComment, setShowComment] = useState(false);

  const handleFeedback = async (value: 'positive' | 'negative') => {
    setFeedback(value);
    
    if (value === 'negative') {
      setShowComment(true);
    } else {
      await submitFeedback({
        conversationId,
        messageId,
        value,
        comment: ''
      });
    }
  };

  const handleSubmitComment = async () => {
    await submitFeedback({
      conversationId,
      messageId,
      value: feedback!,
      comment
    });
    setShowComment(false);
  };

  return (
    <div className="feedback-container">
      {!feedback ? (
        <div className="feedback-buttons">
          <button 
            onClick={() => handleFeedback('positive')}
            className="feedback-btn feedback-positive"
            title="This response was helpful"
          >
            👍
          </button>
          <button 
            onClick={() => handleFeedback('negative')}
            className="feedback-btn feedback-negative"
            title="This response needs improvement"
          >
            👎
          </button>
        </div>
      ) : (
        <div className="feedback-submitted">
          {feedback === 'positive' ? '✅ Thanks!' : '⚠️ Thanks for the feedback'}
        </div>
      )}

      {showComment && (
        <div className="feedback-comment">
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="What could be better? (optional)"
            rows={3}
          />
          <button onClick={handleSubmitComment}>Submit</button>
          <button onClick={() => setShowComment(false)}>Skip</button>
        </div>
      )}
    </div>
  );
};
```

**Backend API Endpoint:**

```python
# api/feedback.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()
langfuse = Langfuse()

class FeedbackRequest(BaseModel):
    conversation_id: str
    message_id: str
    value: str  # 'positive' or 'negative'
    comment: str = ""

@router.post("/api/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback for a conversation
    Stored in LangFuse as a score on the trace
    """
    try:
        # Map feedback to numeric score
        score_value = 1.0 if feedback.value == 'positive' else 0.0
        
        # Submit to LangFuse
        langfuse.score(
            trace_id=feedback.conversation_id,
            name="user_satisfaction",
            value=score_value,
            comment=feedback.comment if feedback.comment else None,
            data_type="NUMERIC"
        )
        
        # Also tag the trace for easy filtering
        if feedback.value == 'negative':
            langfuse.trace(
                id=feedback.conversation_id,
                tags=["negative_feedback", "needs_review"]
            )
        else:
            langfuse.trace(
                id=feedback.conversation_id,
                tags=["positive_feedback", "potential_golden_example"]
            )
        
        return {
            "success": True,
            "message": "Feedback recorded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

##### **Option B: 5-Star Rating (More Granular)**

```typescript
// components/StarRating.tsx
import React, { useState } from 'react';

export const StarRating: React.FC<{ conversationId: string }> = ({ 
  conversationId 
}) => {
  const [rating, setRating] = useState<number | null>(null);
  const [hover, setHover] = useState<number | null>(null);

  const handleRating = async (value: number) => {
    setRating(value);
    await submitFeedback({
      conversationId,
      rating: value,
      maxRating: 5
    });
  };

  return (
    <div className="star-rating">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => handleRating(star)}
          onMouseEnter={() => setHover(star)}
          onMouseLeave={() => setHover(null)}
          className={`star ${(hover || rating || 0) >= star ? 'filled' : ''}`}
        >
          ⭐
        </button>
      ))}
      {rating && <span className="rating-text">Thanks for rating!</span>}
    </div>
  );
};
```

##### **Option C: Issue-Specific Feedback (Best for Debugging)**

```typescript
// components/DetailedFeedback.tsx
export const DetailedFeedback: React.FC = ({ conversationId }) => {
  const [selectedIssues, setSelectedIssues] = useState<string[]>([]);
  
  const issues = [
    { id: 'too_many_questions', label: 'Asked too many questions' },
    { id: 'wrong_answer', label: 'Answer was incorrect' },
    { id: 'didnt_log', label: "Didn't log my data" },
    { id: 'misunderstood', label: 'Misunderstood what I wanted' },
    { id: 'too_slow', label: 'Took too long to respond' },
    { id: 'other', label: 'Other issue' }
  ];

  const handleSubmit = async () => {
    await submitFeedback({
      conversationId,
      issues: selectedIssues,
      value: 'negative'
    });
  };

  return (
    <div className="detailed-feedback">
      <p>What went wrong?</p>
      {issues.map(issue => (
        <label key={issue.id}>
          <input
            type="checkbox"
            checked={selectedIssues.includes(issue.id)}
            onChange={(e) => {
              if (e.target.checked) {
                setSelectedIssues([...selectedIssues, issue.id]);
              } else {
                setSelectedIssues(selectedIssues.filter(i => i !== issue.id));
              }
            }}
          />
          {issue.label}
        </label>
      ))}
      <button onClick={handleSubmit}>Submit Feedback</button>
    </div>
  );
};
```

##### **Integration with Agent Handler**

**File:** `src/agent/graph.py`

```python
from langfuse.decorators import observe, langfuse_context

@observe()
def handle_user_message(message: str, user_id: str) -> dict:
    """
    Main entry point with feedback tracking
    """
    # Run agent
    result = your_langgraph_agent.invoke(state)
    
    # Add metadata for feedback UI
    result["feedback_enabled"] = True
    result["conversation_id"] = langfuse_context.get_current_trace_id()
    result["message_id"] = langfuse_context.get_current_observation_id()
    
    return result
```

##### **Using Feedback in Weekly Workflow**

**File:** `scripts/find_golden_candidates.py`

```python
#!/usr/bin/env python3
"""
Find conversations that should become golden examples
Uses user feedback to identify best and worst conversations
"""

from langfuse import Langfuse
from datetime import datetime, timedelta

def find_golden_candidates(days: int = 7):
    """
    Find conversations from last N days that should be added to dataset
    """
    langfuse = Langfuse()
    
    # Date range
    start_date = datetime.now() - timedelta(days=days)
    
    # Get traces from last week
    traces = langfuse.get_traces(
        from_timestamp=start_date,
        tags=["positive_feedback"]  # Start with positive examples
    )
    
    print(f"\n🌟 Positive Feedback Conversations (Last {days} days)\n")
    
    for trace in traces[:10]:  # Top 10
        feedback_score = trace.scores.get("user_satisfaction", {}).get("value")
        
        if feedback_score and feedback_score >= 1.0:
            print(f"✅ Trace: {trace.id}")
            print(f"   Input: {trace.input.get('message', 'N/A')[:60]}...")
            print(f"   Score: {feedback_score}")
            print(f"   Duration: {trace.duration_ms}ms")
            print(f"   🔗 https://cloud.langfuse.com/trace/{trace.id}\n")
    
    # Also find negative feedback (bugs to fix)
    traces = langfuse.get_traces(
        from_timestamp=start_date,
        tags=["negative_feedback"]
    )
    
    print(f"\n⚠️  Negative Feedback Conversations (Last {days} days)\n")
    
    for trace in traces[:10]:  # Top 10 issues
        feedback_score = trace.scores.get("user_satisfaction", {}).get("value")
        comment = trace.scores.get("user_satisfaction", {}).get("comment")
        
        print(f"❌ Trace: {trace.id}")
        print(f"   Input: {trace.input.get('message', 'N/A')[:60]}...")
        print(f"   Score: {feedback_score}")
        print(f"   Comment: {comment or 'No comment'}")
        print(f"   🔗 https://cloud.langfuse.com/trace/{trace.id}\n")

if __name__ == "__main__":
    find_golden_candidates()
```

**Usage in Sunday Workflow:**
```bash
# Step 1: Find candidates
python scripts/find_golden_candidates.py

# Step 2: Review in LangFuse
# Click links to see full conversations

# Step 3: Add best/worst to dataset
python scripts/add_failures_to_dataset.py
```

##### **Acceptance Criteria:**
- ✅ Feedback UI added to chatbot interface
- ✅ Feedback stored in LangFuse as scores
- ✅ Positive feedback tagged for golden examples
- ✅ Negative feedback tagged for bug fixes
- ✅ Can filter LangFuse traces by feedback
- ✅ Script to find golden candidates works
- ✅ Feedback appears in weekly workflow

##### **Recommended Implementation Order:**

**Week 1:** Start with simple thumbs up/down
- Quick to implement
- Gets you 80% of the value
- Low friction for users

**Week 2-3:** Add optional comment field
- Only on negative feedback
- Helps understand what went wrong
- Still low friction

**Later:** Add detailed issue selection or star ratings
- Only if simple feedback isn't enough
- Can be A/B tested

#### **Step 2.3: Create Structured Output Schemas**

**File:** `src/config/schemas.py`

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import Enum

class ActionType(str, Enum):
    """Possible agent actions"""
    ASK_CLARIFICATION = "ask_clarification"
    LOG_WITH_DEFAULTS = "log_with_defaults"
    LOG_WITH_DATA = "log_with_data"
    ERROR_RESPONSE = "error_response"

class FoodLogDecision(BaseModel):
    """
    Structured decision from agent about food logging
    Forces consistency in agent responses
    """
    action: ActionType
    question: Optional[str] = Field(
        None, 
        description="Clarifying question to ask user (if action=ASK_CLARIFICATION)"
    )
    food_item: Optional[str] = Field(
        None,
        description="Food item to log (if logging)"
    )
    calories: Optional[int] = Field(
        None,
        description="Estimated calories (if logging)",
        ge=0,
        le=10000
    )
    confidence: float = Field(
        description="Confidence in this decision",
        ge=0.0,
        le=1.0
    )
    reasoning: str = Field(
        description="Brief explanation of decision"
    )

class ToolCallDecision(BaseModel):
    """Which MCP tool to call"""
    tool_name: Literal["beeminder", "clickup", "rescuetime", "none"]
    parameters: dict
    reason: str

class AgentResponse(BaseModel):
    """Final agent response structure"""
    message: str = Field(description="Message to user")
    action_taken: ActionType
    tools_called: list[str] = Field(default_factory=list)
    state_updates: dict = Field(default_factory=dict)
```

**Acceptance Criteria:**
- ✅ All agent decisions use Pydantic models
- ✅ LLM forced to return structured outputs (not freeform text)
- ✅ Invalid outputs caught at runtime with clear errors

#### **Step 2.3: Enforce Constraints in Graph**

**File:** `src/agent/nodes.py`

```python
from src.config.constants import MAX_QUESTIONS, HIGH_CONFIDENCE, LOW_CONFIDENCE
from src.config.schemas import FoodLogDecision, ActionType
from langchain_core.messages import HumanMessage

def should_ask_question_node(state: AgentState) -> str:
    """
    Decision node: Ask question or log?
    Enforces MAX_QUESTIONS constraint
    """
    # Hard constraint: Never exceed MAX_QUESTIONS
    if state["questions_asked"] >= MAX_QUESTIONS:
        return "log_with_best_guess"
    
    # Get structured decision from LLM
    decision = llm.with_structured_output(FoodLogDecision).invoke(
        state["messages"]
    )
    
    # Enforce confidence thresholds
    if decision.confidence >= HIGH_CONFIDENCE:
        return "log_immediately"
    elif decision.confidence <= LOW_CONFIDENCE:
        if state["questions_asked"] < MAX_QUESTIONS:
            return "ask_clarification"
        else:
            return "log_with_best_guess"
    else:
        return "log_with_data"

def ask_clarification_node(state: AgentState) -> AgentState:
    """
    Ask ONE clarifying question
    Updates questions_asked counter
    """
    decision = llm.with_structured_output(FoodLogDecision).invoke(
        state["messages"]
    )
    
    if not decision.question:
        raise ValueError("Decision was ASK_CLARIFICATION but no question provided")
    
    # Increment counter
    state["questions_asked"] += 1
    
    # Add question to conversation
    state["messages"].append(HumanMessage(content=decision.question))
    
    return state
```

**Acceptance Criteria:**
- ✅ MAX_QUESTIONS enforced in code (not prompt)
- ✅ Impossible for agent to exceed limits
- ✅ Structured outputs used throughout
- ✅ State properly updated

---

### **Phase 3: Create Golden Dataset (Day 1, 30 mins)**

#### **Step 3.1: Define Golden Examples**

**File:** `datasets/golden_examples.json`

```json
{
  "dataset_name": "beemine_golden_conversations",
  "version": "1.0.0",
  "created": "2025-10-26",
  "examples": [
    {
      "id": "quick_log_01",
      "scenario": "quick_food_logging",
      "complexity": "simple",
      "input": {
        "user_message": "I had an omelet for breakfast",
        "conversation_history": [],
        "user_context": {
          "timezone": "America/New_York",
          "tracking_preference": "quick"
        }
      },
      "expected_output": {
        "message_contains": ["logged", "calories"],
        "message_not_contains": ["what kind", "ingredients"],
        "tool_calls": [
          {
            "tool": "beeminder_add_datapoint",
            "required_params": ["goal_slug", "value", "comment"]
          }
        ],
        "decisions": {
          "should_ask_clarification": false,
          "should_log_immediately": true
        },
        "state": {
          "questions_asked": 0,
          "logged": true
        },
        "max_steps": 3,
        "max_duration_seconds": 5
      },
      "metadata": {
        "mcp_servers": ["beeminder"],
        "tags": ["quick_log", "breakfast", "single_step"]
      }
    },
    {
      "id": "detailed_log_01",
      "scenario": "detailed_food_tracking",
      "complexity": "medium",
      "input": {
        "user_message": "I want to track my breakfast - I had a really healthy omelet",
        "conversation_history": [],
        "user_context": {
          "timezone": "America/New_York",
          "tracking_preference": "detailed"
        }
      },
      "expected_output": {
        "message_contains": ["what", "?"],
        "tool_calls": [],
        "decisions": {
          "should_ask_clarification": true,
          "max_questions_asked": 2
        },
        "state": {
          "questions_asked": 1,
          "logged": false
        },
        "max_steps": 5
      },
      "metadata": {
        "mcp_servers": [],
        "tags": ["detailed_log", "breakfast", "multi_turn"]
      }
    },
    {
      "id": "vague_input_01",
      "scenario": "vague_user_input",
      "complexity": "high",
      "input": {
        "user_message": "I ate a lot today",
        "conversation_history": []
      },
      "expected_output": {
        "message_contains": ["tell me", "meals", "help"],
        "tool_calls": [],
        "decisions": {
          "should_ask_clarification": true
        },
        "state": {
          "questions_asked": 1,
          "logged": false
        },
        "max_steps": 4
      },
      "metadata": {
        "mcp_servers": [],
        "tags": ["vague_input", "guidance_needed"]
      }
    },
    {
      "id": "error_handling_01",
      "scenario": "mcp_server_error",
      "complexity": "high",
      "input": {
        "user_message": "Log 350 calories for breakfast",
        "conversation_history": [],
        "simulate_error": "beeminder_api_timeout"
      },
      "expected_output": {
        "message_contains": ["trouble", "try again", "noted"],
        "graceful_degradation": true,
        "fallback_action": "store_locally_or_apologize",
        "max_steps": 5
      },
      "metadata": {
        "mcp_servers": ["beeminder"],
        "tags": ["error_handling", "resilience"]
      }
    },
    {
      "id": "loop_prevention_01",
      "scenario": "prevent_infinite_questions",
      "complexity": "medium",
      "input": {
        "user_message": "I had food",
        "conversation_history": [],
        "user_context": {
          "tracking_preference": "detailed"
        }
      },
      "expected_output": {
        "decisions": {
          "max_questions_asked": 2
        },
        "state": {
          "questions_asked": {"<=": 2},
          "logged": true
        },
        "max_steps": 7
      },
      "metadata": {
        "mcp_servers": ["beeminder"],
        "tags": ["loop_prevention", "max_questions"]
      }
    }
  ]
}
```

**Acceptance Criteria:**
- ✅ 15-20 golden examples defined
- ✅ Cover: quick log (3), detailed log (3), vague input (2), errors (2), edge cases (2), multi-tool (2), efficiency (2)
- ✅ Each example has clear expected behavior
- ✅ Examples test behavior, not just text matching

#### **Step 3.2: Create Dataset Creation Script**

**File:** `scripts/create_golden_dataset.py`

```python
#!/usr/bin/env python3
"""
Create golden dataset in LangFuse from JSON definition
Run once to set up initial dataset
"""

import json
from pathlib import Path
from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()

def create_golden_dataset():
    """Create dataset from golden_examples.json"""
    
    # Load examples
    examples_file = Path("datasets/golden_examples.json")
    with open(examples_file) as f:
        data = json.load(f)
    
    # Initialize LangFuse
    langfuse = Langfuse()
    
    # Create or get dataset
    dataset_name = data["dataset_name"]
    print(f"📊 Creating dataset: {dataset_name}")
    
    dataset = langfuse.create_dataset(
        name=dataset_name,
        description=f"Golden examples for agentic bot testing (v{data['version']})"
    )
    
    # Add each example
    for example in data["examples"]:
        print(f"  ✨ Adding: {example['id']} ({example['scenario']})")
        
        dataset.create_item(
            input=example["input"],
            expected_output=example["expected_output"],
            metadata={
                "id": example["id"],
                "scenario": example["scenario"],
                "complexity": example["complexity"],
                **example["metadata"]
            }
        )
    
    print(f"\n✅ Created dataset with {len(data['examples'])} examples")
    print(f"🔗 View at: https://cloud.langfuse.com/datasets")
    
    return dataset

if __name__ == "__main__":
    create_golden_dataset()
```

**Usage:**
```bash
python scripts/create_golden_dataset.py
```

**Acceptance Criteria:**
- ✅ Script creates dataset in LangFuse
- ✅ All examples uploaded successfully
- ✅ Can view dataset in LangFuse Dashboard
- ✅ Script idempotent (can run multiple times safely)

---

### **Phase 4: Implement Dataset Testing (Day 1-2)**

#### **Step 4.1: Create Mock MCP Servers**

**File:** `src/mcp/mocks.py`

```python
"""
Mock MCP server responses for testing
Don't hit real APIs during test runs
"""

from typing import Dict, Any
from enum import Enum

class MockResponse(Enum):
    """Standard mock responses"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    INVALID_PARAMS = "invalid_params"

MOCK_RESPONSES: Dict[str, Dict[MockResponse, Any]] = {
    "beeminder_add_datapoint": {
        MockResponse.SUCCESS: {
            "success": True,
            "id": "mock_datapoint_123",
            "timestamp": 1698364800,
            "value": 350,
            "comment": "veggie omelet"
        },
        MockResponse.TIMEOUT: TimeoutError("Connection timeout"),
        MockResponse.ERROR: Exception("API error: Rate limit exceeded"),
        MockResponse.INVALID_PARAMS: ValueError("Missing required parameter: goal_slug")
    },
    "clickup_create_task": {
        MockResponse.SUCCESS: {
            "id": "mock_task_456",
            "name": "Log breakfast calories",
            "status": "to do",
            "url": "https://app.clickup.com/t/mock_task_456"
        },
        MockResponse.TIMEOUT: TimeoutError("Connection timeout"),
        MockResponse.ERROR: Exception("API error: Unauthorized")
    }
}

def get_mock_response(tool_name: str, response_type: MockResponse = MockResponse.SUCCESS):
    """
    Get mock response for a tool call
    
    Args:
        tool_name: Name of MCP tool
        response_type: Type of response to return
    
    Returns:
        Mock response or raises exception
    """
    if tool_name not in MOCK_RESPONSES:
        raise ValueError(f"No mock defined for tool: {tool_name}")
    
    response = MOCK_RESPONSES[tool_name][response_type]
    
    if isinstance(response, Exception):
        raise response
    
    return response
```

**Acceptance Criteria:**
- ✅ Mocks defined for all MCP tools
- ✅ Can simulate success, timeout, error, invalid params
- ✅ Mocks return realistic data structures

#### **Step 4.2: Create Test Runner**

**File:** `scripts/run_dataset_test.py`

```python
#!/usr/bin/env python3
"""
Test agentic bot against golden dataset
Run before every deploy to prevent regressions
"""

import sys
from typing import Dict, Any
from unittest.mock import patch
from langfuse import Langfuse
from dotenv import load_dotenv

from src.agent.graph import handle_user_message
from src.mcp.mocks import get_mock_response, MockResponse

load_dotenv()

def check_result(actual: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare actual agent behavior to expected
    
    Returns dict with:
        - overall_pass: bool
        - scores: dict of individual checks
        - reason: str (if failed)
    """
    scores = {}
    
    # Check 1: Message contains expected phrases
    if "message_contains" in expected:
        message = actual.get("message", "")
        scores["message_contains"] = all(
            phrase.lower() in message.lower()
            for phrase in expected["message_contains"]
        )
    
    # Check 2: Message doesn't contain unwanted phrases
    if "message_not_contains" in expected:
        message = actual.get("message", "")
        scores["message_not_contains"] = all(
            phrase.lower() not in message.lower()
            for phrase in expected["message_not_contains"]
        )
    
    # Check 3: Correct tools called
    if "tool_calls" in expected:
        actual_tools = set(actual.get("tools_called", []))
        expected_tools = set(t["tool"] for t in expected["tool_calls"])
        scores["correct_tools"] = actual_tools == expected_tools
    
    # Check 4: Stayed within step limit
    if "max_steps" in expected:
        actual_steps = actual.get("steps", 0)
        scores["within_step_limit"] = actual_steps <= expected["max_steps"]
    
    # Check 5: Questions asked within limit
    if "decisions" in expected and "max_questions_asked" in expected["decisions"]:
        max_questions = expected["decisions"]["max_questions_asked"]
        actual_questions = actual.get("questions_asked", 0)
        scores["questions_limit"] = actual_questions <= max_questions
    
    # Check 6: Final state matches
    if "state" in expected:
        for key, expected_value in expected["state"].items():
            actual_value = actual.get(key)
            
            # Handle comparison operators
            if isinstance(expected_value, dict):
                if "<=" in expected_value:
                    scores[f"state_{key}"] = actual_value <= expected_value["<="]
                elif ">=" in expected_value:
                    scores[f"state_{key}"] = actual_value >= expected_value[">="]
                else:
                    scores[f"state_{key}"] = False
            else:
                scores[f"state_{key}"] = actual_value == expected_value
    
    # Overall pass
    overall_pass = all(scores.values())
    
    # Reason for failure
    reason = None
    if not overall_pass:
        failed_checks = [k for k, v in scores.items() if not v]
        reason = f"Failed checks: {', '.join(failed_checks)}"
    
    return {
        "overall_pass": overall_pass,
        "scores": scores,
        "reason": reason
    }

def run_dataset_test(dataset_name: str = "beemine_golden_conversations", use_real_mcp: bool = False):
    """
    Run all tests in dataset
    
    Args:
        dataset_name: Name of LangFuse dataset
        use_real_mcp: If True, use real MCP servers (careful!)
    
    Returns:
        Exit code (0 = all passed, 1 = some failed)
    """
    langfuse = Langfuse()
    
    # Load dataset
    print(f"\n🧪 Loading dataset: {dataset_name}")
    dataset = langfuse.get_dataset(dataset_name)
    
    if not dataset or not dataset.items:
        print(f"❌ Dataset not found or empty: {dataset_name}")
        return 1
    
    print(f"📊 Testing against {len(dataset.items)} golden examples\n")
    
    # Track results
    passed = 0
    failed = 0
    results = []
    
    # Run each test
    for i, item in enumerate(dataset.items, 1):
        scenario = item.metadata.get("scenario", "unknown")
        print(f"Test {i}/{len(dataset.items)}: {scenario}")
        
        try:
            if use_real_mcp:
                # Use real MCP servers (use sparingly!)
                result = handle_user_message(
                    message=item.input["user_message"],
                    user_id="test_user"
                )
            else:
                # Mock MCP servers
                with patch('src.mcp.beeminder.call_tool') as mock_beeminder:
                    with patch('src.mcp.clickup.call_tool') as mock_clickup:
                        # Setup mocks
                        mock_beeminder.side_effect = lambda tool, **kwargs: get_mock_response(tool)
                        mock_clickup.side_effect = lambda tool, **kwargs: get_mock_response(tool)
                        
                        # Simulate error if specified
                        if "simulate_error" in item.input:
                            error_type = item.input["simulate_error"]
                            if "timeout" in error_type:
                                mock_beeminder.side_effect = lambda *args: get_mock_response(
                                    "beeminder_add_datapoint", MockResponse.TIMEOUT
                                )
                        
                        # Run agent
                        result = handle_user_message(
                            message=item.input["user_message"],
                            user_id="test_user"
                        )
            
            # Check result
            evaluation = check_result(result, item.expected_output)
            
            if evaluation["overall_pass"]:
                print(f"  ✅ PASS")
                passed += 1
            else:
                print(f"  ❌ FAIL: {evaluation['reason']}")
                failed += 1
            
            results.append({
                "test": scenario,
                "evaluation": evaluation,
                "result": result
            })
            
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            failed += 1
            results.append({
                "test": scenario,
                "error": str(e)
            })
    
    # Summary
    total = len(dataset.items)
    pass_rate = (passed / total) * 100
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} passed ({pass_rate:.0f}%)")
    print(f"{'='*60}\n")
    
    # Detailed failures
    if failed > 0:
        print("❌ Failed tests:")
        for r in results:
            if "error" in r or not r.get("evaluation", {}).get("overall_pass"):
                print(f"  - {r['test']}")
                if "error" in r:
                    print(f"    Error: {r['error']}")
                elif "evaluation" in r:
                    print(f"    Reason: {r['evaluation']['reason']}")
        print()
    
    # Exit code for CI/CD
    return 0 if passed == total else 1

if __name__ == "__main__":
    # Parse arguments
    use_real_mcp = "--real-mcp" in sys.argv
    
    if use_real_mcp:
        print("⚠️  WARNING: Using REAL MCP servers (API costs apply)")
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            sys.exit(0)
    
    exit_code = run_dataset_test(use_real_mcp=use_real_mcp)
    sys.exit(exit_code)
```

**Usage:**
```bash
# Normal testing (with mocks)
python scripts/run_dataset_test.py

# Test with real MCP servers (careful!)
python scripts/run_dataset_test.py --real-mcp
```

**Acceptance Criteria:**
- ✅ Tests all examples in dataset
- ✅ Uses mocks by default
- ✅ Compares behavior, not just text
- ✅ Returns exit code 0 if all pass, 1 if any fail
- ✅ Shows clear failure reasons
- ✅ Works in CI/CD pipelines

---

### **Phase 5: Weekly Improvement Workflow (Ongoing)**

#### **Step 5.1: Add Production Failures to Dataset**

**File:** `scripts/add_failures_to_dataset.py`

```python
#!/usr/bin/env python3
"""
Add production failures to golden dataset
Run weekly during improvement cycle
"""

import json
from datetime import datetime
from pathlib import Path
from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()

def add_failure_to_dataset(
    trace_id: str,
    scenario: str,
    issue: str,
    corrected_output: dict
):
    """
    Add a production failure as a golden example
    
    Args:
        trace_id: LangFuse trace ID of failed conversation
        scenario: Description of scenario
        issue: What went wrong
        corrected_output: What SHOULD have happened
    """
    langfuse = Langfuse()
    
    # Get the failed trace
    trace = langfuse.get_trace(trace_id)
    
    if not trace:
        print(f"❌ Trace not found: {trace_id}")
        return False
    
    # Extract input from trace
    input_data = {
        "user_message": trace.input.get("message", ""),
        "conversation_history": trace.input.get("history", [])
    }
    
    # Create new example
    example = {
        "id": f"prod_failure_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "scenario": scenario,
        "complexity": "high",  # Production failures are usually complex
        "input": input_data,
        "expected_output": corrected_output,
        "metadata": {
            "source": "production_failure",
            "original_trace_id": trace_id,
            "date_added": datetime.now().isoformat(),
            "issue": issue,
            "tags": ["prod_failure", issue.replace(" ", "_")]
        }
    }
    
    # Add to dataset
    dataset = langfuse.get_dataset("beemine_golden_conversations")
    
    dataset.create_item(
        input=example["input"],
        expected_output=example["expected_output"],
        metadata=example["metadata"]
    )
    
    # Save to weekly updates file
    weekly_file = Path(f"datasets/weekly_updates/{datetime.now().strftime('%Y-%m-%d')}.json")
    weekly_file.parent.mkdir(exist_ok=True)
    
    if weekly_file.exists():
        with open(weekly_file) as f:
            weekly_data = json.load(f)
    else:
        weekly_data = {"examples": []}
    
    weekly_data["examples"].append(example)
    
    with open(weekly_file, "w") as f:
        json.dump(weekly_data, f, indent=2)
    
    print(f"✅ Added failure to dataset: {example['id']}")
    print(f"📁 Saved to: {weekly_file}")
    
    return True

# Example usage
if __name__ == "__main__":
    # Example: Adding a "too many questions" failure
    add_failure_to_dataset(
        trace_id="trace_abc123xyz",
        scenario="loop_prevention_real_case",
        issue="asked_too_many_questions",
        corrected_output={
            "message_contains": ["logged"],
            "decisions": {
                "max_questions_asked": 2
            },
            "state": {
                "questions_asked": {"<=": 2},
                "logged": True
            },
            "max_steps": 7
        }
    )
```

**Usage:**
```bash
# Interactive mode (asks for details)
python scripts/add_failures_to_dataset.py

# Or use programmatically
```

**Acceptance Criteria:**
- ✅ Can add production failures to dataset
- ✅ Saves both to LangFuse and local JSON
- ✅ Creates weekly update files
- ✅ Includes metadata about issue

---

## ✅ Success Criteria

### **Phase 1 Complete:**
- [ ] LangFuse installed and configured
- [ ] Every conversation logged to LangFuse
- [ ] Can view full traces in dashboard
- [ ] Custom scores appear on traces

### **Phase 2 Complete:**
- [ ] Constants file with all product decisions
- [ ] **User feedback mechanism implemented** ⭐
- [ ] Feedback UI in chatbot (thumbs up/down minimum)
- [ ] Feedback stored in LangFuse as scores
- [ ] Can filter traces by positive/negative feedback
- [ ] Structured output schemas (Pydantic models)
- [ ] Constraints enforced in graph logic
- [ ] Impossible to violate MAX_QUESTIONS

### **Phase 3 Complete:**
- [ ] Golden dataset created in LangFuse
- [ ] 15-20 examples covering all scenarios
- [ ] Dataset visible in LangFuse dashboard
- [ ] Examples test behavior, not just text

### **Phase 4 Complete:**
- [ ] Mock MCP servers implemented
- [ ] Test runner script works
- [ ] Can run `python scripts/run_dataset_test.py`
- [ ] Shows pass/fail for each example
- [ ] Returns proper exit codes

### **Phase 5 Complete:**
- [ ] Script to add failures to dataset
- [ ] Weekly update files created
- [ ] Can easily add production failures

### **Overall System:**
- [ ] Baseline test score documented
- [ ] Weekly improvement process defined
- [ ] CI/CD integration (optional but recommended)
- [ ] Team trained on workflow

---

## 🔁 Weekly Workflow

### **Every Sunday (30 minutes):**

```bash
# 1. Find golden candidates with feedback (5 mins)
python scripts/find_golden_candidates.py

# Review conversations with:
# ✅ Positive feedback → Potential golden examples
# ❌ Negative feedback → Bugs to fix

# 2. Review last week's conversations (10 mins)
# Open LangFuse Dashboard → Traces
# Filter: Last 7 days, user_satisfaction score
# Find top 3 patterns

# 2. Add failures to dataset (5 mins)
python scripts/add_failures_to_dataset.py

# 3. Fix ONE pattern (5 mins)
# Edit code to fix the top issue
# Example: Add MAX_QUESTIONS constraint

# 4. Test against dataset (2 mins)
python scripts/run_dataset_test.py

# Output shows improvement:
# Before: 12/20 passed (60%)
# After:  17/20 passed (85%)

# 5. Deploy if improved (3 mins)
git add .
git commit -m "Fix: Limit clarifying questions to MAX_QUESTIONS=2"
git push origin main

# Deploy via your normal process
./scripts/deploy.sh
```

### **Daily (5 minutes):**

```bash
# Quick scan of LangFuse dashboard
# Look for:
# - Red X marks (errors)
# - Super long traces (loops)
# - High costs (too many LLM calls)

# Just note issues - don't fix yet
# Fix on Sunday
```

---

## 🐛 Troubleshooting

### **Problem: Dataset tests failing locally but passing in CI**
**Cause:** Different environment variables or mock behavior  
**Solution:** Ensure `.env.test` file with consistent test config

### **Problem: Mocks not working correctly**
**Cause:** Import path issues or missing patches  
**Solution:** Check that patches match actual import paths in agent code

### **Problem: LangFuse not logging conversations**
**Cause:** Missing `@observe()` decorator or env vars not set  
**Solution:** Verify LANGFUSE_SECRET_KEY in `.env` and decorator on handler

### **Problem: Tests pass but real usage fails**
**Cause:** Mocks too simple or missing edge cases  
**Solution:** Add more realistic mocks based on actual API responses

### **Problem: Dataset score not improving**
**Cause:** Fixing symptoms not causes, or no real product decisions made  
**Solution:** Make clear product decisions FIRST, then enforce in code

---

## 📚 References

- [LangFuse Datasets Documentation](https://langfuse.com/docs/datasets)
- [LangFuse Python SDK](https://langfuse.com/docs/sdk/python)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [[🧪 LangFuse Datasets for Agentic Bots - Complete Guide]] - Full knowledge guide
- [[🏢 Beemine.ai]] - Implementation example

---

> [!success] **Implementation Checklist**
> Use this spec to implement the complete LangFuse dataset testing system. Follow phases in order. Test at each step. Ship with Phase 4 complete, then improve weekly with Phase 5.

**Version History:**
- v1.0.0 (2025-10-26): Initial specification based on breakthrough session

---

*This specification written during Oct 26, 2025 breakthrough session. Implemented for Beemine.ai launch.*

