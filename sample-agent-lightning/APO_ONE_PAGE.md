# One-Page Visual Summary: APO Prompt Selection & Storage

## 🎯 THE CORE ANSWER

```
┌─────────────────────────────────────────────────────────────────┐
│                 HOW APO SELECTS BEST PROMPT                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Test multiple prompts on validation data                   │
│  2. Calculate reward score (0.0 - 1.0) for each               │
│  3. Find MAX reward for each unique prompt                     │
│  4. Select the prompt with HIGHEST max reward                 │
│                                                                 │
│  CODE:  best = max(rewards_by_template.items(),              │
│                   key=lambda x: max(x[1]))                    │
│                                                                 │
│  EXAMPLE:                                                       │
│  • Template A max: 0.82                                        │
│  • Template B max: 0.89  ← WINNER                             │
│  • Template C max: 0.75                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 WHERE PROMPTS ARE STORED

```
DURING TRAINING (In Memory):
┌──────────────────────────────────┐
│  templates_tested = [            │
│    "Answer this: {q}",           │
│    "Answer clearly: {q}",        │
│    "Answer thoroughly: {q}",     │
│  ]                               │
│                                  │
│  rewards_by_template = {         │
│    "Answer this: {q}": [0.78...] │
│    "Answer clearly: {q}": [0.89] │ ← BEST
│    "Answer thoroughly: {q}": [0.81] │
│  }                               │
└──────────────────────────────────┘

AFTER TRAINING (Nowhere):
┌──────────────────────────────────┐
│  ❌ NOT saved to disk             │
│  ❌ NOT in database              │
│  ✅ Printed to console           │
│  ✅ Best shown in output         │
│                                  │
│  Must manually save with:        │
│  json.dump(..., "best.json")    │
└──────────────────────────────────┘

INSIDE APO (Hidden):
┌──────────────────────────────────┐
│  • Beam (top N prompts)         │
│  • Best found tracking          │
│  • Generation history           │
│  → Not directly accessible      │
└──────────────────────────────────┘
```

---

## 🔄 SIMPLIFIED PROCESS

```
START
  ↓
Test Baseline Prompt
  Reward: 0.78
  ↓
GPT-4: "This is generic, add 'clarity and depth'"
  ↓
Generate Variations (2 new prompts)
  ↓
Test V1: 0.87 ✅ BETTER   |  Test V2: 0.79 ❌ WORSE
  ↓
Keep V1 in beam (top 2 prompts)
  ↓
Continue? → NO (beam_rounds=1)
  ↓
SELECT: Prompt with max reward (0.89)
  ↓
OUTPUT: "Answer: {q} with clarity and depth." ← Best
  ↓
END
```

---

## 📊 DATA STRUCTURE AT A GLANCE

```
After running apo_training.py:

templates_tested:        rewards_by_template:
┌─────────────────┐     ┌──────────────────────┐
│ [               │     │ {                    │
│   "T1",         │ →   │   "T1": [0.78,0.75]  │
│   "T2",         │     │   "T2": [0.85,0.89]  │ ← Highest max
│   "T3"          │     │   "T3": [0.71,0.75]  │
│ ]               │     │ }                    │
└─────────────────┘     └──────────────────────┘

Selection: max([0.78, 0.85, 0.71]) = 0.85 from T2? NO!
          max([0.78], [0.89], [0.75]) = 0.89 from T2? YES! ✓
```

---

## 💻 CODE TIMELINE

```
Line 30:    Global storage initialized
            templates_tested = []
            rewards_by_template = {}
                     ↓
Line 55:    During each rollout - template tracked
            if template not in templates_tested:
                templates_tested.append(template)
                     ↓
Line 105:   Rewards logged after evaluation
            rewards_by_template[template].append(reward)
                     ↓
Line 250:   Best prompt selected at end
            best = max(rewards_by_template.items(),
                      key=lambda x: max(x[1]))
                     ↓
Line 272:   Best prompt displayed to user
            print("🏆 BEST PROMPT FOUND:")
            print(best_template)
```

---

## ✨ CONSOLE OUTPUT LAYOUT

```
During Each Test:
┌────────────────────────────────────────┐
│ 🔥 TEMPLATE BEING TESTED:             │
│ Answer: {question} with clarity       │
│ [Agent] 📝 Q: What is DNA?...         │
│ [Agent] 💬 A: DNA is a molecule...    │
│ [Agent] ✅ Reward: 0.825              │
└────────────────────────────────────────┘

End of Training:
┌────────────────────────────────────────┐
│ 📊 Summary: 3 templates tested        │
│                                        │
│ Template 1: "Answer: {q}"             │
│   Avg: 0.783 | Max: 0.82              │
│                                        │
│ Template 2: "Answer: {q} with..."     │
│   Avg: 0.873 | Max: 0.89              │
│                                        │
│ Template 3: "Answer {q} thoroughly"   │
│   Avg: 0.793 | Max: 0.81              │
│                                        │
│ 🏆 BEST PROMPT FOUND:                 │
│ Answer: {question} with clarity...    │
│ Score: 0.89 ✨                        │
└────────────────────────────────────────┘
```

---

## 🎯 KEY FORMULA

```
                  SELECT BEST PROMPT
                          ↓
        best = max(rewards_by_template.items(),
                   key=lambda x: max(x[1]))
                    ↓        ↓         ↓
            ┌───────┘        │         └────────┐
            ▼                ▼                   ▼
      For each template,  Find its max    Compare max values
      rewards is a list    reward value    & return highest
      
            Example:
            Template A: [0.78, 0.75, 0.82] max=0.82
            Template B: [0.85, 0.89, 0.88] max=0.89 ← SELECTED
            Template C: [0.71, 0.75, 0.70] max=0.75
```

---

## 📝 HOW TO USE BEST PROMPT

### Option 1: Copy from Console
```
Look for: 🏆 BEST PROMPT FOUND:
          Answer this question: {question} with clarity and depth.
Copy this and use it!
```

### Option 2: Get from Code
```python
# After training completes:
best_template = max(
    rewards_by_template.items(),
    key=lambda x: max(x[1])
)[0]
print(best_template)
```

### Option 3: Save to File
```python
import json
best_template = max(rewards_by_template.items(),
                   key=lambda x: max(x[1]))[0]
with open("best.json", "w") as f:
    json.dump({"prompt": best_template}, f)
```

---

## ⚠️ IMPORTANT NOTES

✅ **DO THIS:**
- Save best prompt to file when training completes
- Look at console output for highlighted templates
- Use max() function for selection

❌ **DON'T DO THIS:**
- Assume prompts are saved automatically (they're not)
- Try to access APO's internal beam state directly
- Use average reward for selection (use max!)

---

## 📚 FOR MORE DETAILS

| If you want... | Read this file |
|---|---|
| 5-min explanation | ANSWER_APO_STORAGE_SELECTION.md |
| Quick reference | APO_STORAGE_SUMMARY.md |
| Full algorithm | APO_HOW_IT_WORKS.md |
| Code locations | APO_CODE_REFERENCE.md |
| Visual diagrams | APO_VISUALIZATION.md |
| Technical deep dive | APO_STORAGE_DETAILS.md |
| Navigation guide | APO_DOCS_INDEX.md |

---

**TL;DR:** APO selects the prompt with highest max reward. Prompts are stored in memory during training. Save them manually before script ends!

