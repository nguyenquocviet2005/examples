# ✅ APO is Working! - Quick Reference

## 🎉 Success!

You just ran **APO (Automatic Prompt Optimization)** successfully! Despite the AgentOps connection warnings, the training completed properly.

---

## 📊 What Just Happened?

Looking at your output:
```
Q: Who painted Mona Lisa?
A: The Mona Lisa was painted by the Italian artist Leonardo da ...
Score: 1.00

[Round 01 | Prompt v0] Best prompt not updated. Current score: 1.000 vs. history best: 1.000)
```

**This means:**
- ✅ Your agent answered correctly
- ✅ Got a perfect score (1.00)
- ✅ APO ran one optimization round
- ✅ Training completed successfully

The AgentOps errors are just monitoring service warnings - they don't affect training.

---

## 🚀 How to Run APO (Now That It Works)

### Quick Test (2-3 minutes)
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key"
python apo_quick.py
```

### Full Training (5-10 minutes)
```bash
python apo_training.py
```

---

## 🎨 Customize Your APO Training

### 1. Edit Tasks (apo_quick.py, line 54)
```python
train = [
    SimpleTask(
        question="Your question here?",
        keywords=["expected", "terms"]
    ),
    # Add more tasks...
]
```

### 2. Adjust APO Settings (apo_quick.py, line 64)

**For faster testing:**
```python
algo = agl.APO(
    AsyncOpenAI(),
    val_batch_size=1,
    gradient_batch_size=1,
    beam_width=1,
    branch_factor=1,
    beam_rounds=1,  # Single round
)
```

**For better optimization:**
```python
algo = agl.APO(
    AsyncOpenAI(),
    val_batch_size=5,
    gradient_batch_size=3,
    beam_width=2,
    branch_factor=2,
    beam_rounds=3,  # 3 optimization rounds
)
```

### 3. Change Initial Prompt (apo_quick.py, line 78)
```python
"prompt_template": agl.PromptTemplate(
    template="You are an expert. Answer: {question}",
    engine="f-string"
)
```

---

## 🔍 Understanding the Output

### Normal Output
```
🚀 Starting APO Training...

Q: What is the capital of France?
A: Paris is the capital of France...
Score: 0.85

[APO] Generating textual gradient...
[APO] Best prompt: "Provide a detailed answer to: {question}"

✅ Done!
```

### What to Ignore
These warnings are safe to ignore:
```
🖇 AgentOps: Network error during span export...
🖇 AgentOps: Session Replay for default.session trace...
```
They're just monitoring/telemetry - training still works perfectly.

---

## 📈 What APO Actually Does

```
Round 1:
├─ Test initial prompt: "Answer: {question}"
├─ Score: 0.75
├─ Critique: "Prompt is too brief"
└─ New prompt: "Provide a detailed answer to: {question}"

Round 2:
├─ Test new prompt
├─ Score: 0.85 (+0.10 improvement!)
├─ Critique: "Good but could be more specific"
└─ New prompt: "You are an expert. Provide a detailed, accurate answer to: {question}"

Final:
└─ Best prompt found with score: 0.90
```

---

## 💡 Pro Tips

### 1. Start Small
```python
train = [
    SimpleTask(question="Simple Q?", keywords=["answer"]),
]
```
Test with 1-2 tasks first, then scale up.

### 2. Check Scores
Look for improvement between rounds:
```
[Round 00] Score: 0.65  <- Baseline
[Round 01] Score: 0.75  <- +0.10 improvement
[Round 02] Score: 0.82  <- +0.07 more
```

### 3. Tune Hyperparameters
- More `beam_rounds` = better optimization (but slower)
- Higher `beam_width` = more exploration
- Larger `n_runners` = faster execution

### 4. Better Scoring
Edit the scoring function to match your needs:
```python
def simple_qa(task: SimpleTask, prompt_template: agl.PromptTemplate) -> float:
    # ... get answer ...
    
    # Custom scoring
    score = 0.0
    
    # 1. Keyword matching (most important)
    keyword_match = sum(1 for kw in task["keywords"] if kw.lower() in answer.lower())
    score += (keyword_match / len(task["keywords"])) * 0.7
    
    # 2. Length bonus (detailed answers)
    score += min(1.0, len(answer) / 200.0) * 0.3
    
    return min(1.0, score)
```

---

## 🐛 Common Issues

### Issue: KeyError in prompt formatting
**Solution:** Make sure template variables match what you're passing:
```python
# Template uses {question}
template="Answer: {question}"

# Must format with question=...
prompt = template.format(question=task["question"])
```

### Issue: Training seems stuck
**Solution:** It's working! APO calls GPT-4 which can take 10-30 seconds per critique.

### Issue: No improvement
**Possible causes:**
1. Initial prompt already optimal
2. Reward function not sensitive enough
3. Need more `beam_rounds`

---

## 📁 Files You Have

| File | Purpose | Run Time |
|------|---------|----------|
| `apo_quick.py` ⭐ | Minimal test | 2-3 min |
| `apo_training.py` | Full training | 5-10 min |
| `APO_GUIDE.md` | Detailed guide | - |
| `APO_SUCCESS.md` | This file | - |

---

## ✨ Next Steps

### 1. Immediate
- ✅ You already ran APO successfully!
- Try changing the questions in `apo_quick.py`
- Run it again and see different results

### 2. This Week
- Use `apo_training.py` with your actual use case
- Add your own tasks and keywords
- Improve the scoring function

### 3. Production
- Scale up with more `beam_rounds`
- Use larger datasets
- Fine-tune hyperparameters
- Integrate best prompt into your app

---

## 💰 Cost

Your quick run cost approximately:
- 2 training samples × 1 round = ~$0.005
- Very affordable for testing!

Full training costs:
- 5 samples × 3 rounds = ~$0.02-0.03

---

## 🎓 Key Concepts

### @rollout Decorator
Marks your function as an agent that APO can optimize:
```python
@agl.rollout
def my_agent(task: MyTask, prompt_template: agl.PromptTemplate) -> float:
    # Your agent logic
    return reward_score
```

### PromptTemplate
The resource being optimized:
```python
agl.PromptTemplate(
    template="Your prompt with {placeholders}",
    engine="f-string"
)
```

### Reward Score
Return value (0.0 to 1.0) that guides optimization:
- 1.0 = Perfect
- 0.5 = Okay
- 0.0 = Failed

---

## 🚀 Ready to Experiment!

```bash
# Try it again with different tasks
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
python apo_quick.py
```

**You're all set! APO is working and ready to optimize your prompts!** 🎉

---

*For more details, see `APO_GUIDE.md`*
