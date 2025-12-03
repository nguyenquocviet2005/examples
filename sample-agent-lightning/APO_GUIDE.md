# 🚀 How to Run APO (Automatic Prompt Optimization)

APO is Agent Lightning's algorithm for automatically improving your agent's prompts through iterative optimization.

---

## ✅ Prerequisites

### 1. Environment Setup
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
```

### 2. Install APO Dependencies
```bash
pip install "agentlightning[apo]"
pip install "openai>=1.100.0"  # Required for TraceToMessages adapter
```

### 3. Set OpenAI API Key
```bash
export OPENAI_API_KEY="sk-proj-your-actual-key"
```

---

## 🎯 Quick Start (3 Steps)

### Step 1: Run the Quick Version
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key"
python apo_quick.py
```

**What it does:**
- Tests 2 simple Q&A tasks
- Optimizes a basic prompt
- Shows the improvement process
- Takes ~2-3 minutes

**Expected output:**
```
🚀 Starting APO Training...

Training...
Q: What is the capital of France?
A: Paris is the capital of France...
Score: 1.00

[APO] Generating textual gradient...
[APO] Applying edits to prompt...
[APO] New prompt: "Please provide a detailed answer to: {q}"

✅ Done!
```

---

### Step 2: Run the Full Version
```bash
python apo_training.py
```

**What it does:**
- Trains on 5 diverse questions
- Validates on 3 different questions
- Uses 4 parallel runners for speed
- Runs 1 full optimization round
- Takes ~5-10 minutes

**Expected output:**
```
====================================================================
APO (Automatic Prompt Optimization) Training
====================================================================

[Setup] Training samples: 5
[Setup] Validation samples: 3
[Setup] ✓ APO initialized

[Baseline] Initial prompt:
  'Answer this question: {question}'

====================================================================
Starting APO Training...
====================================================================

[Agent] Q: What is the capital of France?...
[Agent] A: The capital of France is Paris. It is not only the largest city...
[Agent] Reward: 0.920

... (training continues) ...

====================================================================
✅ Training Complete!
====================================================================
```

---

## 📊 Understanding the Output

### APO Training Process

```
1. Baseline Evaluation
   ├─ Tests initial prompt on validation set
   ├─ Calculates average reward
   └─ Records: "Baseline: 0.65"

2. Generate Textual Gradient
   ├─ Analyzes rollout traces
   ├─ Uses GPT-4 to critique the prompt
   └─ Output: "The prompt is too brief and doesn't encourage detailed answers"

3. Apply Edits
   ├─ Uses GPT-4 to rewrite prompt based on critique
   └─ New prompt: "You are an expert. Provide a detailed, accurate answer to: {question}"

4. Beam Search (if beam_width > 1)
   ├─ Keeps top N prompts
   ├─ Generates variations
   └─ Evaluates all candidates

5. Final Validation
   └─ Best prompt: Score 0.85 (+0.20 improvement!)
```

### Hyperparameters Explained

| Parameter | What It Does | Recommended |
|-----------|-------------|-------------|
| `val_batch_size` | Samples per validation | 3-10 |
| `gradient_batch_size` | Samples for critique | 2-4 |
| `beam_width` | Top prompts to keep | 1-3 |
| `branch_factor` | Variations per prompt | 1-3 |
| `beam_rounds` | Optimization rounds | 1-3 |
| `n_runners` | Parallel workers | 2-8 |

**For quick tests:** Use small values (1-2)
**For production:** Use larger values (4-8)

---

## 🎨 Customization Examples

### Example 1: Change the Task
Edit `apo_training.py`:

```python
train_dataset = [
    QuestionTask(
        question="Explain quantum computing",  # Your question
        expected_keywords=["quantum", "qubit", "superposition"]  # Expected terms
    ),
    # Add more...
]
```

### Example 2: Adjust APO Settings

**For faster testing:**
```python
algo = agl.APO(
    openai_client,
    val_batch_size=1,      # Fewer samples
    gradient_batch_size=1,
    beam_width=1,          # No beam search
    branch_factor=1,       # No branching
    beam_rounds=1,         # Single round
)
```

**For better optimization:**
```python
algo = agl.APO(
    openai_client,
    val_batch_size=10,     # More samples for stable metrics
    gradient_batch_size=5,
    beam_width=3,          # Keep top 3 prompts
    branch_factor=3,       # Generate 3 variations
    beam_rounds=3,         # 3 optimization rounds
)
```

### Example 3: Better Scoring Function

Current scoring in `apo_training.py`:
```python
def calculate_reward(answer: str, expected_keywords: list[str]) -> float:
    # Keyword matching + length bonus
    keyword_score = sum(1 for kw in expected_keywords if kw.lower() in answer.lower())
    keyword_score /= len(expected_keywords)
    
    length_score = min(1.0, len(answer) / 200.0)
    
    return keyword_score * 0.7 + length_score * 0.3
```

Improve it:
```python
def calculate_reward(answer: str, expected_keywords: list[str]) -> float:
    """Advanced scoring with multiple criteria."""
    
    # 1. Keyword coverage (most important)
    keyword_score = sum(1 for kw in expected_keywords if kw.lower() in answer.lower())
    keyword_score /= len(expected_keywords)
    
    # 2. Length (detailed answers)
    length_score = min(1.0, len(answer) / 200.0)
    
    # 3. Structure (has sentences)
    structure_score = min(1.0, answer.count('.') / 3)
    
    # 4. Clarity (not too repetitive)
    words = answer.lower().split()
    unique_ratio = len(set(words)) / max(len(words), 1)
    clarity_score = min(1.0, unique_ratio)
    
    # Weighted combination
    final = (
        keyword_score * 0.5 +    # Most important
        length_score * 0.2 +
        structure_score * 0.2 +
        clarity_score * 0.1
    )
    
    return final
```

### Example 4: Different Initial Prompt

Edit `apo_training.py`:
```python
def baseline_prompt() -> agl.PromptTemplate:
    return agl.PromptTemplate(
        # Try different starting points
        template="You are a helpful assistant. Question: {question}\nProvide a clear answer.",
        engine="f-string"
    )
```

---

## 🔧 Advanced: Understanding the Architecture

### How APO Works Internally

```
┌─────────────────────────────────────────────────┐
│               APO Algorithm                     │
│  (Uses GPT-4 for prompt optimization)           │
└────────┬────────────────────────────────────────┘
         │
    ┌────▼─────┐
    │ Trainer  │ (Coordinates everything)
    └────┬─────┘
         │
    ┌────▼────────────────────────────────┐
    │ Execution Strategy (Client-Server)  │
    └────┬─────────────────────────────────┘
         │
    ┌────▼────────┐
    │ Store Server│ (Manages tasks & results)
    └────┬────────┘
         │
    ┌────▼─────────┐
    │ N Runners    │ (Execute your agent in parallel)
    │ (Processes)  │
    └──────────────┘
```

### What Happens During Training

1. **Trainer starts**: Spawns store server + N runner processes
2. **Algorithm enqueues tasks**: Puts tasks in the store queue
3. **Runners dequeue**: Each runner picks up a task
4. **Agent executes**: Your `@rollout` function runs with current prompt
5. **Spans collected**: Execution trace sent back to store
6. **Algorithm analyzes**: APO critiques the prompt using traces
7. **Prompt updated**: New prompt generated and pushed to store
8. **Repeat**: Steps 2-7 repeat for each optimization round

---

## 💰 Cost Estimation

### APO Uses Two Models

1. **Your agent model** (e.g., `gpt-4o-mini`): $0.0002 per call
2. **APO's optimizer** (GPT-4): $0.01-0.03 per optimization round

### Example Costs

**Quick test (apo_quick.py):**
- 2 training tasks × 2 runs = 4 agent calls
- 1 optimization round = 1 APO call
- **Total: ~$0.02**

**Full training (apo_training.py):**
- 5 training tasks × 4 samples × 2 rounds = 40 agent calls
- 3 validation tasks × 3 evaluations = 9 agent calls
- 1 optimization round = 1 APO call
- **Total: ~$0.03-0.05**

**Production (10 rounds, 100 tasks):**
- ~1000 agent calls = $0.20
- ~10 APO calls = $0.30
- **Total: ~$0.50**

### Save Money
1. Use `gpt-3.5-turbo` for agent (5x cheaper)
2. Reduce `beam_rounds` and `beam_width`
3. Start with small datasets for testing

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'agentlightning'"
```bash
source .venv/bin/activate
pip install "agentlightning[apo]"
```

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY="sk-proj-your-key"
echo $OPENAI_API_KEY  # Verify
```

### "TraceToMessages requires openai>=1.100.0"
```bash
pip install --upgrade "openai>=1.100.0"
```

### Training is too slow
1. Reduce `n_runners` if you're rate-limited
2. Reduce dataset size for testing
3. Lower APO hyperparameters

### Training fails with timeout
1. Increase timeout in trainer config
2. Use fewer samples per batch
3. Check internet connection

### Prompts not improving
1. Make sure reward function is working correctly
2. Increase `gradient_batch_size` for better critiques
3. Run more `beam_rounds`
4. Check if initial prompt is already good

---

## 📚 What Each File Does

| File | Purpose |
|------|---------|
| `apo_quick.py` | Minimal working example (~2 min) |
| `apo_training.py` | Full-featured training (~10 min) |
| `APO_GUIDE.md` | This guide |

---

## ✨ Next Steps

1. **Start simple**: Run `apo_quick.py` first
2. **Understand output**: Watch how prompts improve
3. **Customize**: Edit tasks and scoring
4. **Scale up**: Use `apo_training.py` with your data
5. **Optimize**: Tune hyperparameters for best results

---

## 📞 Resources

- **APO Docs**: `/home/viet2005/workspace/fsoft/agent-lightning/docs/algorithm-zoo/apo.md`
- **Tutorial**: `/home/viet2005/workspace/fsoft/agent-lightning/docs/how-to/train-first-agent.md`
- **Agent Lightning**: https://github.com/microsoft/agent-lightning
- **OpenAI API**: https://platform.openai.com/docs/

---

## 🎉 Ready to Run!

```bash
# Quick test (2 minutes)
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key"
python apo_quick.py
```

**That's it! Watch APO automatically improve your prompts!** 🚀
