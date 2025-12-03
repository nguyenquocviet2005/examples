# APO Prompt Selection Visualization

## 🎯 Complete Decision Flow

```
START: APO Training Begins
│
├─────────────────────────────────────────────────────────┐
│         Initialize with Baseline Prompt                 │
│    "Answer this question: {question}"                  │
│         Reward Score: 0.783 (avg)                      │
└─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│  Round 1: Evaluate Baseline on Validation Set          │
│                                                         │
│  Test on 3 samples:                                    │
│  • "What is DNA?" → Answer → Reward: 0.82            │
│  • "What is photosynthesis?" → Answer → Reward: 0.78 │
│  • "What is machine learning?" → Answer → Reward: 0.75│
│                                                         │
│  Average: 0.78, Max: 0.82 ← Keep in BEAM             │
└─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│  Round 1: GPT-4 Critique & Generate                    │
│                                                         │
│  GPT-4 Input:                                          │
│  "Prompt: 'Answer this question: {question}'           │
│   Avg reward: 0.78                                     │
│   How can we improve?"                                 │
│                                                         │
│  GPT-4 Output: "Be more specific about clarity/depth" │
│                                                         │
│  Generate 2 Variations:                                │
│  V1: "Answer this question: {question}                │
│       with clarity and depth."                         │
│  V2: "Answer the question: {question}                 │
│       Be thorough and precise."                        │
└─────────────────────────────────────────────────────────┘
│
▼
┌──────────────────────┬───────────────────────────────────┐
│  Test Variant 1      │  Test Variant 2                   │
├──────────────────────┼───────────────────────────────────┤
│ • DNA: 0.85          │ • DNA: 0.81                       │
│ • Photosynthesis: 0.89 (↑ BETTER!) │ • Photosynthesis: 0.78 │
│ • ML: 0.88           │ • ML: 0.79                        │
│                      │                                    │
│ Avg: 0.87 ✨ GOOD   │ Avg: 0.79  (No improvement)      │
│ Max: 0.89 ✨ BEST    │ Max: 0.81                         │
└──────────────────────┴───────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│  BEAM UPDATE (beam_width = 2)                           │
│  Keep Top 2 Prompts:                                    │
│                                                         │
│  POSITION 1 (Best):                                    │
│  "Answer this question: {question} with clarity..."    │
│  Max Reward: 0.89 ✨                                   │
│                                                         │
│  POSITION 2:                                           │
│  "Answer this question: {question}"                    │
│  Max Reward: 0.82                                      │
│                                                         │
│  REMOVED (didn't make top 2):                          │
│  "Answer the question: {question} Be thorough..."      │
│  Max Reward: 0.81                                      │
└─────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│  [END OF beam_rounds=1]                                │
│  Training Complete!                                    │
│                                                         │
│  ✨ FINAL RESULT ✨                                    │
│  Best Prompt Found:                                    │
│  "Answer this question: {question} with clarity       │
│   and depth."                                          │
│                                                         │
│  Best Reward: 0.89 (vs baseline 0.78) ↑ 14% IMPROVED  │
└─────────────────────────────────────────────────────────┘
│
END: APO Training Complete
```

---

## 📊 Reward Landscape

```
                  Prompt Performance Distribution
                           
      0.95 │                    
      0.90 │              ✨ ← BEST FOUND: 0.89
      0.85 │         ◆     
      0.80 │    ◆ ✓ ◆      ← Baseline: 0.78
      0.75 │ ◆ ◆  ◆ ◆   
      0.70 │◆  ◆  ◆       
           └─────────────────────────────────
             Template Variations
             
Legend:
  ◆ = Template variation tested
  ✓ = Baseline prompt (starting point)
  ✨ = Best prompt found by APO
```

---

## 🔍 Selection Algorithm Visualization

### The `max()` function logic:

```python
# All templates and their maximum rewards
rewards_by_template = {
    "Template A": [0.75, 0.78, 0.71],      # max = 0.78
    "Template B": [0.82, 0.81, 0.79],      # max = 0.82
    "Template C": [0.89, 0.85, 0.87],      # max = 0.89 ← WINNER
    "Template D": [0.72, 0.74, 0.70],      # max = 0.74
    "Template E": [0.81, 0.80, 0.79],      # max = 0.81
}

                    ▼ max(x[1]) Applied ▼

Template A: max([0.75, 0.78, 0.71]) = 0.78 ┐
Template B: max([0.82, 0.81, 0.79]) = 0.82 │
Template C: max([0.89, 0.85, 0.87]) = 0.89 ┼─→ BEST: 0.89
Template D: max([0.72, 0.74, 0.70]) = 0.74 │
Template E: max([0.81, 0.80, 0.79]) = 0.81 ┘

Result: Template C (the one with 0.89)
```

---

## 📈 Training Convergence Example

```
Round 0 (Baseline):
  Baseline Reward: 0.78
  Beam: [0.78]

Round 1:
  Baseline: 0.78
  Variant 1: 0.87 ↑
  Variant 2: 0.79
  Beam: [0.87, 0.78]
  ✓ Improvement found! (0.78 → 0.87)

Round 2 (if beam_rounds > 1):
  Top Prompt: 0.87
  New Variant 1: 0.88 ↑
  New Variant 2: 0.85
  Beam: [0.88, 0.87]
  ✓ Small improvement (0.87 → 0.88)

Round 3 (if beam_rounds > 2):
  Top Prompt: 0.88
  New Variant 1: 0.86 ↓
  New Variant 2: 0.87
  Beam: [0.88, 0.87]
  ✗ No improvement - optimization plateau reached

FINAL: Best = 0.88
```

---

## 🔀 Beam Search Tree

```
                    Baseline: "Answer this: {q}"
                          (0.78)
                           │
           ┌───────────────┼───────────────┐
           │               │               │
        Test1          Test2           Test3
        (0.82)         (0.75)          (0.80)
           │
           ▼
    Generate Variants
    (branch_factor=2)
           │
    ┌──────┴──────┐
    │             │
 V1.1         V1.2
 (0.87)      (0.79)
  ┌┐          └─ Dropped
  ││
  │└─ Select ← Beam position 1
  │
  └─ Top 2 kept in beam (beam_width=2)
     (0.87 moves to position 1 in next round)


Round 1 Beam: [(0.87, "with clarity..."), (0.78, baseline)]
↓
Round 2: Generate from best
           │
    ┌──────┴──────┐
    │             │
 V2.1         V2.2
 (0.88)      (0.85)
  ✓           └─ New beam position 2
  
Round 2 Beam: [(0.88, "with clarity and depth..."), (0.87, "with clarity...")]

Continue until beam_rounds exhausted or no improvement...
```

---

## 💾 Memory Snapshot During Training

```
After 3 test cases with baseline:
┌─────────────────────────────────────────┐
│ templates_tested = [                    │
│   "Answer this question: {question}"    │
│ ]                                       │
│                                         │
│ rewards_by_template = {                │
│   "Answer this question: {question}": [ │
│     0.82,  # DNA                        │
│     0.75,  # Photosynthesis             │
│     0.78   # Machine Learning           │
│   ]                                     │
│ }                                       │
└─────────────────────────────────────────┘

After testing variants:
┌─────────────────────────────────────────┐
│ templates_tested = [                    │
│   "Answer this question: {question}",   │
│   "Answer this question: {question} with│
│    clarity and depth.",                 │
│   "Answer the question: {question}      │
│    Be thorough and precise."            │
│ ]                                       │
│                                         │
│ rewards_by_template = {                │
│   "Answer this question: {question}": [ │
│     0.82, 0.75, 0.78                    │
│   ],                                    │
│   "Answer this question: {question} with│
│    clarity and depth.": [               │
│     0.85, 0.89, 0.88                    │ ← BEST
│   ],                                    │
│   "Answer the question: {question}      │
│    Be thorough and precise.": [         │
│     0.81, 0.78, 0.79                    │
│   ]                                     │
│ }                                       │
└─────────────────────────────────────────┘
```

---

## 🎯 Final Selection Process

```
All Candidates:
┌────────────────────────────────────────────┐
│ Template 1: max reward = 0.82              │
│ Template 2: max reward = 0.89  ← SELECT   │
│ Template 3: max reward = 0.81              │
└────────────────────────────────────────────┘

Selection Code:
best = max(rewards_by_template.items(), key=lambda x: max(x[1]))
       ↓
       Returns: (Template 2, [0.85, 0.89, 0.88])
       ↓
best_score = max([0.85, 0.89, 0.88]) = 0.89

Output:
┌─────────────────────────────────────────┐
│ 🏆 BEST PROMPT FOUND:                   │
│                                         │
│ "Answer this question: {question}       │
│  with clarity and depth."               │
│                                         │
│ ✨ Best Reward Score: 0.89             │
└─────────────────────────────────────────┘
```

---

## 📊 Comparison: Before vs After

```
Before APO:
  Baseline Prompt: "Answer this question: {question}"
  Average Performance: 0.78
  
  Q: "What is DNA?"
  A: "DNA is a molecule."
  Reward: 0.75 (short, missing keywords)

After APO:
  Optimized Prompt: "Answer this question: {question} 
                     with clarity and depth."
  Average Performance: 0.87 (+11% improvement!)
  
  Q: "What is DNA?"
  A: "DNA, or deoxyribonucleic acid, is the hereditary 
      material found in living organisms..."
  Reward: 0.89 (detailed, includes keywords)
```

---

## ⚡ Key Insights

1. **APO tests prompts methodically** - Not random, follows beam search
2. **Rewards guide selection** - Highest max reward wins
3. **Multiple tests per prompt** - Same prompt tested 3-8 times for stability
4. **Average vs Max** - Selection uses MAX (best case), summary shows both
5. **GPT-4 generates variants** - Not rule-based, uses LLM critique
6. **Convergence** - Training stops when beam rounds exhausted or no improvement

