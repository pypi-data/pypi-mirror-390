# 📊 ClickUp Custom Fields & Processes

**Purpose:** Comprehensive guide to ClickUp custom fields, scoring systems, and task management processes for effective project prioritization and execution.

---

## 🎯 **Required Fields for Task Creation**

### **Priority Scoring System (Required)**

#### **🟣 | Business Impact Level**
- **Purpose:** Measures the business value and criticality of the task
- **Options:**
  - **Critical Path (5)** - Essential for business operations
  - **Major Workflow (4)** - Significant business impact
  - **Moderate Feature (3)** - Moderate business value
  - **Minor (2)** - Small business impact
  - **Cosmetic (1)** - Minimal business value
- **Usage:** Always required for proper prioritization

#### **🟣 | Customer Reach Scale**
- **Purpose:** Measures how many people will be affected by this task
- **Options:**
  - **1-10 People (1)** - Very limited reach
  - **11-50 People (2)** - Small group impact
  - **51-200 People (3)** - Medium group impact
  - **201-1k People (4)** - Large group impact
  - **1k-5k People (5)** - Very large group impact
  - **5k+ People (6)** - Massive reach
- **Usage:** Helps prioritize tasks that affect more users

#### **🟣 | Evidence Confidence**
- **Purpose:** Measures how confident we are in the data/assumptions
- **Options:**
  - **Measured (1.0)** - Reproducible with logs/specs approved
  - **Observed (.8)** - Pilot/SME with logs
  - **Inferred (.6)** - Proxies/analogs
  - **Assumed (.4)** - No data yet
  - **Speculative (.2)** - Unknown/new
- **Usage:** Helps assess risk and uncertainty

#### **🟣 | Effort Time Band**
- **Purpose:** Estimates the time required to complete the task
- **Options:**
  - **XS (≤0.5d) (.5)** - Very quick tasks
  - **S (1-2d) (1.5)** - Small tasks
  - **M (3-5d) (4)** - Medium tasks
  - **L (6-10d) (8)** - Large tasks
  - **XL (11-20d) (15)** - Very large tasks
- **Usage:** Critical for capacity planning and scheduling

#### **🟣 | Client Revenue Risk**
- **Purpose:** Assesses the financial impact if this task fails
- **Options:**
  - **High Risk ($5k+ monthly) (3)** - Major revenue impact
  - **Medium Risk ($1k-5k monthly) (2)** - Moderate revenue impact
  - **Low Risk (<$1k monthly) (0)** - Minimal revenue impact
- **Usage:** Prioritizes tasks that protect revenue

### **Scheduling (Required)**

#### **Work On Date**
- **Purpose:** When to work on this task
- **Type:** Date field
- **Usage:** Essential for time blocking and daily planning
- **Rule:** Must be set for all tasks to ensure proper scheduling

---

## 🧮 **Scoring Methods**

### **ICE Scoring (Impact, Confidence, Ease)**
- **Formula:** `Business Impact × Evidence Confidence × (6 - Effort Time Band)`
- **Use Case:** Operations/Admin tasks
- **Range:** 0-30 (higher is better)

### **RICE Scoring (Reach, Impact, Confidence, Effort)**
- **Formula:** `(Customer Reach × Business Impact × Evidence Confidence) / Effort Time Band`
- **Use Case:** Business Growth tasks
- **Range:** 0-20 (higher is better)

### **HYBRID Scoring**
- **Formula:** `MAX(ICE Score, RICE Score)`
- **Use Case:** Client Delivery tasks
- **Range:** 0-30 (higher is better)

### **Final Priority Score**
- **Emergency Override:** 999 points
- **This Week Override:** 500 points
- **Normal Calculation:** Based on scoring method
- **Range:** 0-100 (higher is better)

---

## 📋 **Task Creation Process**

### **Step 1: Basic Information**
1. **Task Name** - Clear, actionable description
2. **Description** - Detailed context and requirements
3. **Assignee** - Who will work on this
4. **Due Date** - When it needs to be completed

### **Step 2: Required Scoring Fields**
1. **🟣 | Business Impact Level** - How critical is this?
2. **🟣 | Customer Reach Scale** - How many people affected?
3. **🟣 | Evidence Confidence** - How confident are we?
4. **🟣 | Effort Time Band** - How long will it take?
5. **🟣 | Client Revenue Risk** - What's the financial impact?

### **Step 3: Scheduling**
1. **Work On Date** - When to work on this task
2. **🟣 | Task Category Filter** - Business Growth/Operations/Client Delivery
3. **🟣 | Work Type** - Bug/Feature/Tech Debt/Architecture/Spike/Admin/Chore

### **Step 4: Additional Context**
1. **🟣 | Component** - API/Web App/Admin/Auth/Infrastructure
2. **🟣 | Next Step** - What's the immediate next action?
3. **🟣 | Blocked By** - Any dependencies?
4. **OKRs** - Which objective does this support?

---

## 🎯 **Priority Calculation Examples**

### **High Priority Task Example:**
- **Business Impact:** Critical Path (5)
- **Customer Reach:** 5k+ People (6)
- **Evidence Confidence:** Measured (1.0)
- **Effort Time Band:** S (1.5)
- **Client Revenue Risk:** High Risk (3)
- **ICE Score:** 5 × 1.0 × (6-1.5) = 22.5
- **RICE Score:** (6 × 5 × 1.0) / 1.5 = 20
- **Final Score:** 22.5 (High Priority)

### **Low Priority Task Example:**
- **Business Impact:** Cosmetic (1)
- **Customer Reach:** 1-10 People (1)
- **Evidence Confidence:** Speculative (.2)
- **Effort Time Band:** XL (15)
- **Client Revenue Risk:** Low Risk (0)
- **ICE Score:** 1 × .2 × (6-15) = -1.8
- **RICE Score:** (1 × 1 × .2) / 15 = 0.013
- **Final Score:** 0.013 (Low Priority)

---

## 📅 **Daily Workflow Integration**

### **Morning Planning:**
1. **Review Today's Tasks** - Check Work On Date = Today
2. **Sort by Final Priority Score** - Work on highest scores first
3. **Check Missing Data Flags** - Complete any incomplete scoring
4. **Update Work On Dates** - Schedule tasks for appropriate days

### **Task Execution:**
1. **Start with High Priority** - Focus on highest scoring tasks
2. **Update Progress** - Mark status changes
3. **Log Time** - Track actual vs. estimated effort
4. **Update Next Step** - Keep the next action clear

### **Evening Review:**
1. **Complete Tasks** - Mark finished tasks as complete
2. **Update Scores** - Adjust based on new information
3. **Plan Tomorrow** - Set Work On Dates for next day
4. **Review Blockers** - Address any blocked tasks

---

## 🚨 **Quality Control Flags**

### **Missing Data Flags:**
- **❓ Missing Work On Date** - Tasks without scheduling
- **❓ | Missing Priority Score** - Tasks without proper scoring
- **🟣 | Task Missing Data Flag** - Incomplete scoring data

### **Status Flags:**
- **🟣 | Today Focus Task** - Priority tasks for today
- **🔥 Is Active Task?** - Currently being worked on
- **🟣 | High Leverage Flag** - Tasks with ICE score ≥ 12

---

## 🔄 **Integration with LYT System**

### **LYT → ClickUp:**
1. **Create Dots** as ClickUp tasks with proper scoring
2. **Set Work On Dates** based on daily planning
3. **Use Priority Scores** to order daily tasks
4. **Update Status** as tasks progress

### **ClickUp → LYT:**
1. **Update Dots** with ClickUp task outcomes
2. **Reflect on scores** in daily journal
3. **Update MOCs** with new insights
4. **Track patterns** in task completion

---

## 📊 **Reporting & Analytics**

### **Key Metrics:**
- **Completion Rate** - % of tasks completed on time
- **Score Accuracy** - How well estimates match reality
- **Priority Distribution** - Balance of high/medium/low priority
- **Time Tracking** - Actual vs. estimated effort

### **Weekly Reviews:**
- **Top Priority Tasks** - What got the highest scores
- **Blocked Tasks** - What's preventing progress
- **Score Adjustments** - Refine scoring based on experience
- **Process Improvements** - How to make the system better

---

*Last updated: 2025-01-10*
