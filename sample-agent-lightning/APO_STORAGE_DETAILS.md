# Where APO Stores and Accesses Prompts - Technical Details

## Data Flow in Your Script

```
┌─────────────────────────────────────────────────────────────┐
│                    apo_training.py                          │
└─────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────────┐  ┌──────────────┐  ┌────────────────┐
   │ baseline()  │  │  qa_agent()  │  │  APO Algorithm │
   │  Returns:   │  │   Receives:  │  │  Maintains:    │
   │  Template   │  │  - task      │  │  - Beam state  │
   │  "Answer    │  │  - template  │  │  - Prompts     │
   │   this...{} │  │              │  │  - Rewards     │
   │             │  │  Returns:    │  │  - Best found  │
   │             │  │  - Reward    │  │                │
   └─────────────┘  └──────────────┘  └────────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
              ┌────────────────────────────────┐
              │      trainer.fit() runs         │
              │  - Client-Server execution     │
              │  - 4 parallel workers          │
              │  - APO generates prompts       │
              │  - Tracks rewards              │
              └────────────────────────────────┘
                           │
              ┌────────────┴────────────────────┐
              ▼                                 ▼
     ┌─────────────────────┐      ┌───────────────────────┐
     │  Global Lists       │      │  Output at End        │
     │  (In Memory)        │      │  - All templates      │
     │  - templates_tested │      │  - Best template      │
     │  - rewards_by_temp  │      │  - Best score         │
     └─────────────────────┘      └───────────────────────┘
```

---

## 1. Global State Variables

### In `apo_training.py`:

```python
# Track templates for summary
templates_tested = []          # All unique templates tried
rewards_by_template = {}       # Dict: template → list of rewards
```

**Accessed in:**
- `qa_agent()` function - appends tested templates
- End of main() - generates summary

### Lifecycle:

```
Initial State:
  templates_tested = []
  rewards_by_template = {}

During Training (each rollout):
  templates_tested.append(new_template)  # If not already present
  rewards_by_template[template].append(reward_score)

After Training:
  - Summary report generated
  - Best template identified
  - Report printed to console
```

---

## 2. Inside the APO Algorithm

APO maintains internal state (you can't directly access it):

```python
algo = agl.APO(
    openai_client,
    val_batch_size=3,        # ← Hyperparameter
    gradient_batch_size=2,   # ← Hyperparameter
    beam_width=2,            # ← BEAM SIZE (keeps best 2 prompts)
    branch_factor=2,         # ← VARIATIONS PER PROMPT
    beam_rounds=1,           # ← OPTIMIZATION ROUNDS
)
```

### What APO Tracks (Internal):

```python
# Conceptual - this is inside the APO class
class APO:
    def __init__(self, ...):
        self.beam = []  # Top N prompts by reward
        self.best_prompt = None
        self.best_reward = 0.0
        self.generation = 0
        
    def update_beam(self, new_prompts_and_rewards):
        # Keep best beam_width prompts
        self.beam = sorted(new_prompts_and_rewards, 
                          key=lambda x: x[1], 
                          reverse=True)[:beam_width]
        self.best_prompt = self.beam[0][0]
        self.best_reward = self.beam[0][1]
```

---

## 3. Trainer State Management

### Via the Trainer:

```python
trainer = agl.Trainer(
    algorithm=algo,
    n_runners=4,
    initial_resources={
        "prompt_template": baseline_prompt()  # ← Current prompt
    },
    adapter=agl.TraceToMessages(),
)
```

**State Updates:**
1. Trainer starts with baseline prompt
2. Each rollout updates resources with new prompt
3. APO algorithm selects next best prompt
4. Trainer broadcasts it to 4 parallel runners
5. They test it and return rewards

---

## 4. Execution Trace Storage

Each rollout creates a **Trace** in memory:

```python
# Conceptual trace structure
trace = {
    "rollout_id": "ro-xxxxx",
    "template": "Answer this question: {question}",
    "tasks": [
        {
            "question": "What is DNA?",
            "answer": "DNA is...",
            "reward": 0.825,
        },
        # ... more tasks
    ],
    "metadata": {
        "round": 1,
        "beam_index": 0,
        "prompt_version": 4,
    }
}
```

**Traces are:**
- Collected by the Trainer
- Processed by the adapter (`TraceToMessages`)
- Used by APO to compute gradients
- NOT persisted to disk by default

---

## 5. Where Information Flows

### Forward Path (Testing):

```
Trainer
  ↓
APO selects prompt from beam
  ↓
Updates initial_resources with new PromptTemplate
  ↓
Distributes to 4 parallel runners
  ↓
Each runner executes qa_agent()
  ↓
qa_agent() logs template (line: "🔥 TEMPLATE BEING TESTED")
  ↓
OpenAI called
  ↓
Reward calculated
  ↓
Reward logged with emoji
  ↓
Global dicts updated:
  - templates_tested.append(template)
  - rewards_by_template[template].append(reward)
```

### Backward Path (Feedback):

```
4 runners complete rollouts
  ↓
Traces collected by Trainer
  ↓
APO processes traces
  ↓
Calculates gradient (what makes rewards better?)
  ↓
Uses GPT-4 to generate improved prompts
  ↓
Updates beam with new candidates
  ↓
Next round begins with new prompts
```

---

## 6. How to Access the Best Prompt

### Option 1: From Console Output

Just look at the final summary:
```
🏆 BEST PROMPT FOUND:
======================================================================
Answer this question: {question} with clarity and depth.

✨ Best Reward Score: 0.895
======================================================================
```

### Option 2: From Global Dict After Training

```python
# In main() after trainer.fit() completes:

best_template_tuple = max(
    rewards_by_template.items(),
    key=lambda x: max(x[1])
)

best_template = best_template_tuple[0]  # The prompt string
best_rewards = best_template_tuple[1]   # List of all its rewards
best_score = max(best_rewards)          # Highest reward

print(f"Best Prompt: {best_template}")
print(f"Best Score: {best_score}")
```

### Option 3: Save to File

```python
import json

best_template = max(
    rewards_by_template.items(),
    key=lambda x: max(x[1])
)[0]

with open("best_prompt.json", "w") as f:
    json.dump({"template": best_template}, f, indent=2)
```

---

## 7. Prompt Lifecycle Example

### Initial Baseline:
```
Template: "Answer this question: {question}"
Rewards: [0.78, 0.82, 0.75]
Avg: 0.783
```

### GPT-4 Critique:
```
"This is too generic. Try being more specific about
what you want (clarity, depth, structure)."
```

### Generated Variant 1:
```
Template: "Answer this question: {question} with clarity and depth."
Test Results: [0.85, 0.89, 0.84]
Avg: 0.86 ✨ (Better! Stays in beam)
```

### Generated Variant 2:
```
Template: "Answer the question: {question}. Be thorough and precise."
Test Results: [0.81, 0.78, 0.79]
Avg: 0.793 (Worse than Variant 1, removed from beam)
```

### Beam After Round 1:
```
[
  ("Answer this question: {question} with clarity and depth.", 0.89),
  ("Answer this question: {question}", 0.82),
]
```

### Continue with Variant 1 as base...

---

## 8. What Gets Lost After Execution

⚠️ **Important:** These are NOT saved by default:

```python
# ❌ Lost after script completes:
- All intermediate prompts
- All individual rewards per task
- Execution traces
- Beam history
- GPT-4 critiques
- Gradients computed

# ✅ Available at end-of-training:
- templates_tested list (in-memory)
- rewards_by_template dict (in-memory)
- Console output (printed to stdout)
```

### To Persist Everything:

```python
import json
from datetime import datetime

# Save results
results = {
    "timestamp": datetime.now().isoformat(),
    "total_templates": len(templates_tested),
    "templates": [
        {
            "template": template,
            "rewards": rewards_by_template.get(template, []),
            "avg_reward": sum(rewards_by_template.get(template, [])) / max(len(rewards_by_template.get(template, [])), 1),
            "max_reward": max(rewards_by_template.get(template, []), default=0),
        }
        for template in templates_tested
    ]
}

with open("apo_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

## 9. Storage Diagram

```
┌─────────────────────────────────────────────────────┐
│              Memory (During Execution)              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  templates_tested = ["temp1", "temp2", "temp3"]   │
│                                                     │
│  rewards_by_template = {                           │
│    "temp1": [0.78, 0.82],                         │
│    "temp2": [0.85, 0.89],  ← BEST                │
│    "temp3": [0.71],                               │
│  }                                                 │
│                                                    │
│  APO Internal (Hidden):                           │
│  ├─ beam = [("temp2", 0.89), ("temp1", 0.82)]   │
│  ├─ best_prompt = "temp2"                        │
│  └─ best_reward = 0.89                           │
│                                                    │
│  Trainer State:                                   │
│  ├─ current_resources.prompt_template = temp2    │
│  └─ execution_traces = [trace1, trace2, ...]     │
│                                                    │
└─────────────────────────────────────────────────────┘
         ▼ (Script ends - all lost!)
┌─────────────────────────────────────────────────────┐
│         Disk (Only if Explicitly Saved)             │
├─────────────────────────────────────────────────────┤
│  apo_results.json (optional)                        │
│  best_prompt.json (optional)                        │
│  training_log.txt (optional)                        │
└─────────────────────────────────────────────────────┘
```

---

## 10. Summary Table

| Location | Content | Accessible | Persistent |
|----------|---------|------------|-----------|
| `templates_tested` list | All tested prompts | ✅ Yes (global) | ❌ No (in-memory) |
| `rewards_by_template` dict | Rewards per prompt | ✅ Yes (global) | ❌ No (in-memory) |
| APO.beam | Top N best prompts | ❌ No (internal) | ❌ No (internal) |
| Console output | Training progress | ✅ Yes (printed) | ⚠️ Terminal only |
| Execution traces | Trace objects | ⚠️ Partial access | ❌ No (in-memory) |
| Disk | N/A | ✅ Yes | ✅ Yes (if saved) |

