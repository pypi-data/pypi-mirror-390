---
created: 2025-10-26
lastUpdated: 2025-10-26T03:41:00
contextDate: 2025-10-26
tags: [knowledge, langfuse, agentic-bots, testing, datasets, mcp-servers]
rank: 9.8
status: breakthrough
---

# 🧪 LangFuse Datasets for Agentic Bots - Complete Guide

> [!success] **Oct 26, 2025 - 3:41 AM Breakthrough**
> Complete systematic approach to testing and improving agentic chatbots with MCP servers using LangFuse datasets.

---

## 🎯 The Problem This Solves

### **Context: Troy's Struggle**
- Working on 3 agentic chatbots (Beemine.ai + 2 others)
- Using LangGraph + multiple MCP servers (Beeminder, ClickUp, RescueTime, Google Calendar)
- **Struggling with consistency**: "Getting different results every time"
- Looking for "the best practice" for training/prompting
- Stuck on product questions disguised as technical ones (e.g., "How many clarifying questions should it ask about an omelet?")

### **The False Problem**
Believed this was a **training/prompting problem** that needed the right technique to solve.

### **The Real Problem**
This is a **PRODUCT DESIGN problem**, not a training problem!

**Key Insight:** Agentic chatbots are SUPPOSED to be variable. The question isn't "How do I make them perfectly consistent?" - it's **"How do I make them consistently USEFUL?"**

---

## 💡 The Breakthrough Realization

### **Core Insights:**

1. **Agentic bots with LangGraph + MCP servers are inherently variable**
   - Different contexts → Different tool calls → Different responses
   - Complex decision graphs → More decision points → More variation
   - MCP server responses can vary (API changes, network issues, data updates)

2. **Conversation depth is a UX decision, not a prompt engineering problem**
   - "How many questions to ask about an omelet?" → **Product requirement**
   - Options: Minimal friction, accurate tracking, conversational depth, hybrid
   - **This must be DESIGNED and then ENFORCED in code**

3. **You can't build great datasets without real users**
   - Perfect testing before shipping = paralysis
   - Ship → Monitor → Fix → Test → Deploy (weekly cycle)
   - Real user failures → Best golden examples

4. **LangFuse datasets = Regression test suite for chatbot behavior**
   - Test **behavior** (tools, decisions, efficiency), not just text
   - Prevents fixing one thing and breaking three others
   - Quality gate for every deployment

---

## 🔬 The Solution: LangFuse Datasets Workflow

### **High-Level Workflow:**

```
┌─────────────────────────────────────────────────────────┐
│ 1. CREATE DATASET (One Time - 30 mins)                  │
│    → 15-20 golden examples                              │
│    → Covers: quick, detailed, errors, edge cases        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 2. SHIP YOUR BOT (Today)                                │
│    → Add @observe() decorator                           │
│    → Deploy to production                               │
│    → Real users start using it                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 3. MONITOR (Daily - 5 mins)                             │
│    → LangFuse Dashboard → Traces                        │
│    → Look for: Errors, long traces, high costs          │
│    → Note issues for weekly review                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ 4. WEEKLY IMPROVEMENT (Sunday - 30 mins)                │
│    → Review worst 10 conversations                      │
│    → Find pattern: "It keeps doing X"                   │
│    → Add failed examples to dataset                     │
│    → Fix that ONE issue in code                         │
│    → Run: python scripts/run_dataset_test.py           │
│    → If scores improve → Deploy                         │
└─────────────────────────────────────────────────────────┘
                          ↓
                     (Repeat weekly)
```

---

## 📝 Phase 1: Create Golden Dataset (30 mins)

### **What is a Golden Dataset?**
A collection of ideal conversation examples that define "good" behavior for your bot.

### **For Agentic Bots, Test BEHAVIOR, Not Just Text:**

```python
dataset.create_item(
    input={
        "user_message": "I had an omelet for breakfast",
        "conversation_history": [],
        "user_context": {
            "timezone": "America/New_York",
            "goals": ["lose_weight"],
            "tracking_preference": "quick"
        }
    },
    expected_output={
        # The response text
        "message": "Great! I'll log a veggie omelet with ~350 calories. Want to adjust that?",
        
        # The tool calls that SHOULD happen
        "tool_calls": [
            {
                "tool": "beeminder_add_datapoint",
                "parameters": {
                    "goal_slug": "calories",
                    "value": 350,
                    "comment": "veggie omelet"
                }
            }
        ],
        
        # The agent decisions
        "decisions": {
            "should_ask_clarification": False,
            "should_log_immediately": True,
            "confidence_level": "high"
        },
        
        # State expectations
        "final_state": {
            "logged": True,
            "needs_followup": False,
            "questions_asked": 0
        },
        
        # Efficiency
        "max_steps": 3  # Should complete in 3 steps max
    },
    metadata={
        "scenario": "quick_logging_with_mcp",
        "mcp_servers_used": ["beeminder"],
        "complexity": "simple_one_step"
    }
)
```

### **What to Include (15-20 Examples):**

**Core Scenarios:**
1. **Quick logging** (3 examples) - User wants minimal friction
2. **Detailed logging** (3 examples) - User is engaged, wants precision
3. **Vague inputs** (2 examples) - "I ate today" needs guidance
4. **Error handling** (2 examples) - MCP server down, network issues
5. **Edge cases** (2 examples) - Corrections, unusual foods, emotional eating
6. **Multi-tool flows** (2 examples) - Log to Beeminder + create ClickUp task
7. **Efficiency tests** (2 examples) - Loop prevention, max questions

**Key Principle:** Cover your **decision tree**, not every possible input.

---

## 🚀 Phase 2: Ship Your Bot

### **Add LangFuse Observation:**

```python
from langfuse.decorators import observe

@observe()
def handle_user_message(message: str, user_id: str):
    """
    Your normal agentic bot handler
    Every conversation now logged to LangFuse automatically
    """
    result = your_langgraph_agent.invoke({
        "messages": [message],
        "user_id": user_id
    })
    return result
```

### **What This Gives You:**
- Every real conversation logged automatically
- Full trace: inputs, outputs, tool calls, decisions, timing, costs
- Foundation for weekly improvements

**Just ship it.** Don't wait for perfect testing.

---

## 📊 Phase 3: Monitor Daily (5 mins)

### **LangFuse Dashboard → Traces Tab:**

**Quick Scan Checklist:**
```
View: Last 24 hours
Sort by: Created (newest first)

Look for:
  🔴 Red X marks → Errors/crashes
  ⏱️ Super long traces → Loops or stuck conversations
  💸 High costs → Too many LLM calls
  👎 Negative feedback → User abandonment
```

**Action:** Note the top 1-2 issues for Sunday deep dive.

**Don't fix yet!** Just observe patterns.

---

## 🔧 Phase 4: Weekly Improvement (Sunday, 30 mins)

### **Step 1: Find Problem Conversations (15 mins)**

**LangFuse Dashboard → Traces Tab:**

```
Filters:
  ✅ Last 7 days
  ✅ Duration > 30 seconds (slow conversations)
  ✅ Or: Cost > $0.30 (expensive conversations)
  ✅ Or: Error = true (crashed conversations)
```

**Click on each trace and analyze:**
- What did user say?
- What did agent do?
- Which MCP tools were called?
- How many steps did it take?
- **Where did it go wrong?**

**Look for THE PATTERN:** Not individual failures, but recurring issues.

Examples:
- "It keeps asking 5+ questions before logging"
- "It's calling Beeminder twice for the same data"
- "It's not handling 'I ate lunch' properly"
- "It loops when MCP server is slow to respond"

### **Step 2: Add Failures to Dataset (5 mins)**

```python
# Grab the failed trace
trace = langfuse.get_trace("trace_id_from_ui")

# Create CORRECTED version
dataset.create_item(
    input=trace.input,
    expected_output={
        # What SHOULD have happened
        "message": "Great! Logged 350 calories.",
        "tool_calls": [{"tool": "beeminder", "params": {...}}],
        "decisions": {"should_ask_clarification": False},
        "max_steps": 3  # Should've been 3, not 15
    },
    metadata={
        "source": "production_failure",
        "date": "2025-10-26",
        "issue": "asked_too_many_questions",
        "original_trace_id": trace.id
    }
)
```

**Add 3-5 failed conversations each week.**

### **Step 3: Fix ONE Pattern (5 mins)**

**Don't fix everything.** Fix the **top issue only**.

Example: "Bot asks too many clarifying questions"

**Solution:** Add constraint in code:
```python
MAX_QUESTIONS = 2  # Hard limit

def should_ask_another_question(state):
    if state["questions_asked"] >= MAX_QUESTIONS:
        return "log_with_best_guess"
    if state["user_seems_annoyed"]:
        return "log_with_best_guess"
    if state["critical_info_missing"]:
        return "ask_one_more"
    return "log_with_best_guess"
```

### **Step 4: Test Against Dataset (5 mins)**

```bash
python scripts/run_dataset_test.py

# Output:
# 🧪 Testing against 20 golden examples...
# 
# Test 1/20: quick_food_log ✅ PASS
# Test 2/20: detailed_tracking ✅ PASS
# Test 3/20: vague_input ❌ FAIL: Too many steps
# ...
# 
# Results: 17/20 passed (85%)
```

**Key Questions:**
- Did score improve from last week?
- Did fixing one thing break others?
- Is 85% good enough to ship?

### **Step 5: Deploy If Improved**

```bash
# If dataset score improved OR stayed same
git commit -m "Fix: Limit clarifying questions to MAX_QUESTIONS=2"
git push origin main

# Deploy to production
# Monitor for 24 hours
```

**Next week:** Find the NEW top issue. Repeat.

---

## 🛠️ Key Implementation Strategies

### **1. State Machine Constraints (Not Prompts)**

**DON'T rely on prompts:**
```
System: "Please ask no more than 2 clarifying questions"
```
❌ This will be ignored ~30% of the time

**DO enforce in code:**
```python
MAX_QUESTIONS = 2  # Hard limit in LangGraph state

def should_ask_another_question(state):
    if state["questions_asked"] >= MAX_QUESTIONS:
        return "log_with_best_guess"  # Force this path
    if state["user_engagement"] == "low":
        return "quick_log"
    return "ask_one_question"
```
✅ This will NEVER be violated

### **2. Structured Outputs (Force Consistency)**

**DON'T rely on freeform text:**
```python
response = llm.invoke("What should I do next?")
# Response: "Well, I think maybe you should log it..."
```
❌ Parsing this is unreliable

**DO use structured outputs:**
```python
from pydantic import BaseModel

class FoodLogDecision(BaseModel):
    action: Literal["ask_clarification", "log_with_defaults", "ask_preferences"]
    question: Optional[str]
    confidence: float
    reasoning: str

# Force the model to return this structure
response = llm.with_structured_output(FoodLogDecision).invoke(...)
```
✅ Always parseable, always consistent

### **3. Few-Shot Examples (Underrated)**

```python
system_prompt = """
You are a food logging assistant.

Examples:

USER: I had an omelet
ASSISTANT: Great! I'll log a veggie omelet with ~350 calories. Want to adjust that?

USER: I had pizza
ASSISTANT: Got it! How many slices?

USER: I ate a lot today
ASSISTANT: Tell me about your meals and I'll help you track them.
"""
```

**5-10 examples dramatically improve consistency.**

### **4. Mock MCP Servers (Fast Testing)**

**DON'T hit real APIs during testing:**
```python
# This is slow and uses API quota
result = beeminder_mcp.create_datapoint(...)
```

**DO use mocks:**
```python
from unittest.mock import patch

with patch('your_mcp_client.call_tool') as mock_mcp:
    mock_mcp.return_value = {"success": True, "id": "mock123"}
    
    # Test your agent against dataset
    result = your_agent.invoke(test_input)
```

**Benefits:**
- Tests run in seconds, not minutes
- No API costs during testing
- Can simulate errors and edge cases

---

## 📈 Scoring Agentic Behavior

### **What to Score (Not Just "Was the response good?"):**

```python
from langfuse.decorators import langfuse_context

# 1. Did it call the right tools?
langfuse_context.score_current_trace(
    name="correct_mcp_servers_used",
    value=check_mcp_servers_match(result, expected),
    comment=f"Expected: {expected['tools']}, Got: {result.tools}"
)

# 2. Did it stop at the right time? (Critical for loops!)
langfuse_context.score_current_trace(
    name="agent_efficiency",
    value=len(result.steps) <= expected["max_steps"],
    comment=f"Took {len(result.steps)} steps (max: {expected['max_steps']})"
)

# 3. Did it make the right decisions?
langfuse_context.score_current_trace(
    name="decision_tree_accuracy",
    value=check_decisions_match(result, expected),
    comment="Did the agent reason correctly?"
)

# 4. Did it handle errors gracefully?
langfuse_context.score_current_trace(
    name="error_handling",
    value=not result.had_unhandled_errors,
    comment="No crashes or unhandled exceptions"
)

# 5. Tool parameter correctness
langfuse_context.score_current_trace(
    name="mcp_parameters_correct",
    value=check_tool_params(result, expected),
    comment="Did it pass correct params to MCP tools?"
)

# 6. Didn't call unnecessary tools
langfuse_context.score_current_trace(
    name="no_wasted_calls",
    value=len(result.mcp_calls) <= len(expected["tool_calls"]),
    comment="Efficiency: only needed tool calls"
)
```

---

## 🧪 The Testing Script

### **`scripts/run_dataset_test.py`:**

```python
#!/usr/bin/env python3
"""
Test your agent against golden dataset
Run this before every deploy!
"""

from langfuse import Langfuse
from your_agent import your_agentic_bot
from unittest.mock import patch

def run_dataset_test():
    langfuse = Langfuse()
    dataset = langfuse.get_dataset("your_golden_dataset")
    
    print(f"\n🧪 Testing against {len(dataset.items)} golden examples...\n")
    
    passed = 0
    failed = 0
    
    for i, item in enumerate(dataset.items, 1):
        print(f"Test {i}/{len(dataset.items)}: {item.metadata.get('scenario', 'unknown')}")
        
        # Mock MCP servers (don't hit real APIs during testing)
        with patch('your_mcp.call') as mock_mcp:
            mock_mcp.return_value = {"success": True}
            
            # Run your agent
            result = your_agentic_bot.invoke(item.input)
            
            # Check if it matches expected behavior
            matches = check_result(result, item.expected_output)
            
            if matches["overall_pass"]:
                print(f"  ✅ PASS")
                passed += 1
            else:
                print(f"  ❌ FAIL: {matches['reason']}")
                failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{len(dataset.items)} passed ({passed/len(dataset.items)*100:.0f}%)")
    print(f"{'='*50}\n")
    
    # Exit code for CI/CD
    return 0 if passed == len(dataset.items) else 1

def check_result(actual, expected):
    """
    Compare actual result to expected behavior
    """
    # Did it call the right tools?
    tools_match = set(actual.tools_called) == set(expected.get("tool_calls", []))
    
    # Did it stay within step limit?
    efficient = len(actual.steps) <= expected.get("max_steps", 10)
    
    # Does message contain expected phrases?
    message_ok = all(
        phrase in actual.message 
        for phrase in expected.get("message_contains", [])
    )
    
    overall_pass = tools_match and efficient and message_ok
    
    return {
        "overall_pass": overall_pass,
        "tools_match": tools_match,
        "efficient": efficient,
        "message_ok": message_ok,
        "reason": "Tools wrong" if not tools_match 
                 else "Too many steps" if not efficient
                 else "Message wrong" if not message_ok
                 else None
    }

if __name__ == "__main__":
    exit(run_dataset_test())
```

**Usage:**
```bash
# Before every deploy
python scripts/run_dataset_test.py

# If it passes → Deploy with confidence
# If it fails → Fix before deploying
```

---

## 🎯 The Philosophy Shift

### **Old Approach (Paralysis):**
1. Build three bots at once
2. Find "the best practice" externally
3. Perfect consistency before shipping
4. Train until flawless
5. THEN ship

**Result:** Never ship. Perpetual perfectionism. Spinning wheels.

### **New Approach (Shipping):**
1. Pick ONE bot to focus on
2. Ship with known limitations
3. Monitor what actually breaks
4. Fix top issue weekly
5. Test changes against dataset
6. Deploy improvements continuously

**Result:** Learn fast. Improve weekly. Build great product.

---

## 💪 Why This Works

### **Psychological Benefits:**
- **Breaks perfectionism paralysis** - Permission to ship imperfect
- **Actionable feedback loop** - Know exactly what to fix next
- **Measurable progress** - Dataset scores show improvement
- **Focus on one thing** - ONE bot, ONE issue per week
- **Trust the process** - Ship → Learn → Fix → Repeat

### **Technical Benefits:**
- **Regression testing** - Don't break what works
- **Quality gate** - Objective measure before deploy
- **Fast iteration** - Weekly improvements compound
- **Real user data** - Best source of golden examples
- **Confidence** - Know your changes work before shipping

### **Business Benefits:**
- **Ship faster** - Launch today, not next month
- **User-driven roadmap** - Fix what actually matters
- **Sustainable pace** - 30 mins/week, not constant firefighting
- **Better product** - Built on real usage, not assumptions

---

## 📚 Resources

### **LangFuse Documentation:**
- [Datasets Overview](https://langfuse.com/docs/datasets)
- [Experiments & Testing](https://langfuse.com/docs/datasets/experiments)
- [Scoring Traces](https://langfuse.com/docs/scores)
- [Python SDK](https://langfuse.com/docs/sdk/python)

### **Related Notes:**
- [[🏢 Beemine.ai]] - Active project using this approach
- [[🧠 AI Development Patterns]] - Technical AI knowledge
- [[🤖 AI & Automation Thinking MOC]] - AI strategy
- [[🔧 Platform & Tool Building MOC]] - Development practices

---

## 🎉 The Impact

### **Troy's Breakthrough (Oct 26, 2025):**

**Before (3:41 AM):**
- "I'm spinning wheels and stuck"
- Working on 3 bots, struggling with consistency
- Looking for external "best practices"
- Perfectionism blocking shipping

**After (30 mins later):**
- **"I'm going to ship beemine.ai TODAY!"**
- Clear technical path forward
- Systematic improvement process
- Courage over perfection

**This isn't just technical clarity - it's breaking through the paralysis pattern.**

---

> [!tip] **The Core Principle**
> **"You can't build great datasets without real users. Ship first, fix what breaks."**
> 
> Your dataset is your regression test suite. Your weekly cycle is your improvement engine. Your real users are your best teachers.
> 
> **Ship it. Then fix it. Then ship again.** 🚀

---

*This knowledge captured during 3:41 AM breakthrough session on Oct 26, 2025. Applied immediately to Beemine.ai launch.*








