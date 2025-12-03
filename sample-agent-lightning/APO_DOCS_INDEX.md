# APO Storage & Selection Documentation Index

## 📚 Complete Guide to How APO Selects Best Prompts

This folder now contains comprehensive documentation on how APO (Automatic Prompt Optimization) decides which prompt is best and where prompts are stored.

---

## 📖 Documentation Files

### 1. **APO_STORAGE_SUMMARY.md** ⭐ START HERE
**Best for:** Quick answers  
**Contains:**
- TL;DR summary
- Selection algorithm explained
- Data structure examples
- Console output explanation
- Quick reference table

**Read this first for a 2-minute overview!**

---

### 2. **APO_HOW_IT_WORKS.md**
**Best for:** Understanding the algorithm  
**Contains:**
- Complete APO workflow
- Reward system breakdown
- Beam search algorithm explanation
- Hyperparameter meanings
- How prompts are generated
- Training output interpretation

**Read this to understand the full algorithm!**

---

### 3. **APO_CODE_REFERENCE.md**
**Best for:** Developers, code-specific questions  
**Contains:**
- Exact line numbers in apo_training.py
- Code snippets for each section
- Step-by-step data flow
- Selection logic breakdown
- Memory usage analysis
- Common issues and solutions

**Read this when debugging or modifying code!**

---

### 4. **APO_STORAGE_DETAILS.md**
**Best for:** Technical deep dive  
**Contains:**
- Data flow diagrams
- Global state variables
- APO internal state
- Execution trace storage
- Information flow (forward & backward paths)
- Where information flows
- Storage diagram
- Lifecycle of prompts
- Persistence options

**Read this for comprehensive technical understanding!**

---

### 5. **APO_VISUALIZATION.md**
**Best for:** Visual learners  
**Contains:**
- Complete decision flow diagram
- Reward landscape visualization
- Selection algorithm visualization
- Beam search tree
- Memory snapshots
- Final selection process
- Convergence examples
- Before/after comparison

**Read this for visual explanations with ASCII diagrams!**

---

## 🎯 Quick Navigation

### I want to know...

**"How does APO decide the best prompt?"**
→ Read: `APO_STORAGE_SUMMARY.md` (Quick answer)  
→ Or: `APO_HOW_IT_WORKS.md` (Full explanation)  

**"Where are prompts stored?"**
→ Read: `APO_STORAGE_SUMMARY.md` (Quick reference)  
→ Or: `APO_STORAGE_DETAILS.md` (Technical details)  

**"Show me the code!"**
→ Read: `APO_CODE_REFERENCE.md` (Line numbers + snippets)  

**"Draw me a picture!"**
→ Read: `APO_VISUALIZATION.md` (ASCII diagrams)  

**"I want to understand everything"**
→ Read in order:
1. `APO_STORAGE_SUMMARY.md` (foundation)
2. `APO_HOW_IT_WORKS.md` (algorithm)
3. `APO_VISUALIZATION.md` (visual understanding)
4. `APO_CODE_REFERENCE.md` (implementation)
5. `APO_STORAGE_DETAILS.md` (deep dive)

---

## 🔑 Key Concepts

### Best Prompt Selection
APO selects the prompt with the **highest maximum reward** using:
```python
best_prompt = max(prompt_and_rewards, key=lambda x: x[1])
```

### Storage Locations
- **During training**: In-memory Python globals
  - `templates_tested` - list of all prompts tried
  - `rewards_by_template` - dict of prompts → rewards
- **After training**: Nowhere (must explicitly save)
- **Inside APO**: Internal beam state (hidden)

### Algorithm
Uses **Beam Search** with **GPT-4 critique**:
1. Test initial prompt → Get rewards
2. GPT-4 analyzes: "Why didn't this work better?"
3. GPT-4 generates variations
4. Test variations → Compare rewards
5. Keep best, repeat

---

## 💻 Code Locations

| Purpose | File | Location |
|---------|------|----------|
| Define storage | `apo_training.py` | Line ~30 |
| Add templates | `apo_training.py` | Line ~55 |
| Log rewards | `apo_training.py` | Line ~105 |
| Display summary | `apo_training.py` | Line ~240 |
| Show best | `apo_training.py` | Line ~272 |

---

## 📊 Understanding the Data

### templates_tested
```python
[
    "Answer this question: {question}",
    "Answer this question: {question} with clarity and depth.",
    "Answer the question: {question}. Be thorough..."
]
```
**Type:** `list[str]`  
**Purpose:** Track every unique prompt tested

### rewards_by_template
```python
{
    "Answer this question: {question}": [0.78, 0.75, 0.82],
    "Answer this question: {question} with clarity...": [0.85, 0.89, 0.88],
    # ...
}
```
**Type:** `dict[str, list[float]]`  
**Purpose:** Track rewards for each prompt (0-1 scale)

---

## 🚀 Next Steps

1. **Run the script**: `python apo_training.py` (set OPENAI_API_KEY first)
2. **Observe output**: Look for "🏆 BEST PROMPT FOUND:" section
3. **Read documentation**: Start with `APO_STORAGE_SUMMARY.md`
4. **Save the best**: Use provided code to persist to JSON
5. **Experiment**: Modify reward function or hyperparameters

---

## ❓ FAQ

**Q: How does APO know which prompt is best?**  
A: It compares maximum rewards. Highest wins!

**Q: Are prompts saved automatically?**  
A: No. Look at console output or add save code.

**Q: Can I see all tested prompts?**  
A: Yes! Check `templates_tested` list.

**Q: What's the scoring formula?**  
A: Keywords (70%) + length (30%) = 0-1 score

**Q: How many prompts does APO try?**  
A: Depends on hyperparameters (typically 5-15)

**Q: Can I change the selection method?**  
A: Yes, modify the `max()` logic at line 250.

---

## 📈 Learning Path

```
Start
  │
  ├─→ Read: APO_STORAGE_SUMMARY.md (5 min) ✅ QUICK START
  │   ↓
  │   Understand: Basic concepts, data locations
  │
  ├─→ Read: APO_HOW_IT_WORKS.md (10 min)
  │   ↓
  │   Understand: Algorithm, rewards, beam search
  │
  ├─→ Read: APO_VISUALIZATION.md (8 min)
  │   ↓
  │   Understand: Visual flowcharts and examples
  │
  ├─→ Read: APO_CODE_REFERENCE.md (10 min)
  │   ↓
  │   Understand: Exact code, line numbers
  │
  └─→ Read: APO_STORAGE_DETAILS.md (15 min)
      ↓
      Expert understanding! ✨

Total time: ~48 minutes for complete understanding
```

---

## 🎓 Documentation Summary

| Doc | Length | Complexity | Best For |
|-----|--------|-----------|----------|
| APO_STORAGE_SUMMARY.md | 3 pages | Beginner | Quick answers |
| APO_HOW_IT_WORKS.md | 6 pages | Intermediate | Understanding algorithm |
| APO_VISUALIZATION.md | 5 pages | Intermediate | Visual learners |
| APO_CODE_REFERENCE.md | 7 pages | Advanced | Developers |
| APO_STORAGE_DETAILS.md | 8 pages | Advanced | Deep understanding |

---

## 🔗 Related Files in This Folder

- **apo_training.py** - The actual training script
- **apo_quick.py** - Minimal APO example (2-3 min runtime)
- **APO_GUIDE.md** - How to use APO (quickstart guide)
- **APO_SUCCESS.md** - Success reference after first run

---

## 📞 Quick Reference

**Selection Algorithm:**
```python
best = max(rewards_by_template.items(), key=lambda x: max(x[1]))[0]
```

**Storage Location:**
```python
templates_tested = []
rewards_by_template = {}
```

**Save Best Prompt:**
```python
import json
best = max(rewards_by_template.items(), key=lambda x: max(x[1]))[0]
json.dump({"template": best}, open("best.json", "w"))
```

**Get Best Score:**
```python
best_template, best_rewards = max(rewards_by_template.items(), key=lambda x: max(x[1]))
best_score = max(best_rewards)
```

---

**Last Updated:** November 5, 2025  
**APO Version:** Demonstrated with Agent Lightning v0.2.1  
**Python Version:** 3.13+

