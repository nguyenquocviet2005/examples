# 🎉 Agent Lightning - Complete Working Setup

## ✅ Success! Your Script is Running

Your Agent Lightning prompt optimization system is now **fully functional and working**.

---

## 🚀 Quick Start (30 seconds)

### Step 1: Set OpenAI API Key
```bash
export OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

### Step 2: Run the Optimizer
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
python run_simple.py
```

**Output Example:**
```
[Algo] Testing 3 prompts...
[Algo] Test 1/3: You are a helpful assistant...
  [Agent] Response: The capital of France is Paris.
  [Agent] Score: 0.155

[Algo] Test 3/3: You are knowledgeable. Provide a detailed answer...
  [Agent] Response: The capital of France is Paris. It is not only...
  [Agent] Score: 1.000

🏆 Best prompt: You are knowledgeable...
🏆 Best score:  1.000
```

---

## 📁 Available Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| **run_simple.py** ⭐ | Simple, direct optimization | **Start here - easiest way** |
| run_agent_complete.py | Full Agent Lightning architecture | Advanced: server + client setup |
| server_runner.py | Just the training server | Advanced: multi-terminal setup |
| agent_runner.py | Just the agent runner | Advanced: multi-terminal setup |
| algorithm_runner.py | Just the algorithm | Advanced: multi-terminal setup |
| run.sh | Interactive menu | Choose your setup preference |

---

## 📊 What Your System Does

### The Algorithm
```
Input: 3 different prompts
  ↓
For each prompt:
  ├─ Format with task: "What is the capital of France?"
  ├─ Send to OpenAI gpt-4o-mini
  ├─ Get response: "The capital of France is Paris..."
  └─ Score based on response quality
  ↓
Output: Best prompt with score
```

### Current Scoring
Based on response length (you can customize this):
```python
score = min(1.0, len(response) / 200.0)
# Longer, more detailed responses = higher scores
```

---

## 🎯 Customization Examples

### Example 1: Change the Task
Edit `run_simple.py`:
```python
# Change this line:
task_input = "What is the capital of France?"

# To this:
task_input = "What are the benefits of renewable energy?"
```

### Example 2: Add More Prompts
Edit `run_simple.py`:
```python
prompts_to_test = [
    "You are a helpful assistant. Answer: {any_question}",
    "You are an expert. Be concise: {any_question}",
    "You are friendly. Explain simply: {any_question}",
    "You are technical. Be precise: {any_question}",  # New!
]
```

### Example 3: Use a Different Model
Edit `run_simple.py`, find this line:
```python
model="gpt-4o-mini"
```

Available options:
- `gpt-4o-mini` (cheapest ✓ recommended)
- `gpt-4o` (more powerful)
- `gpt-3.5-turbo` (older, still works)
- `gpt-4` (if you have access)

### Example 4: Improve Scoring Logic
Edit `run_simple.py`, replace this function:
```python
def evaluate_prompt(task: str, prompt_template: PromptTemplate) -> float:
    """Evaluate a prompt by calling OpenAI and generating a reward score."""
    # ... get llm_output ...
    
    # REPLACE THIS:
    score = min(1.0, len(llm_output) / 200.0)
    
    # WITH THIS (example):
    # Score based on multiple factors
    length_score = min(1.0, len(llm_output) / 200.0)  # Length bonus
    quality_score = 0.8 if "capital" in llm_output.lower() else 0.5  # Relevance
    score = (length_score * 0.4) + (quality_score * 0.6)  # Weighted average
    
    return score
```

---

## 🔄 Architecture Comparison

### Simple Version (Recommended for Testing)
```
Algorithm (find_best_prompt)
    ↓
For each prompt:
    ├─ OpenAI API Call
    ├─ Evaluate Response
    └─ Return Score
    ↓
Best Prompt & Score
```
✅ **Pros:** Simple, direct, no infrastructure needed
❌ **Cons:** Single-threaded, slow for many prompts

### Full Agent Lightning Version (For Production)
```
Algorithm (find_best_prompt)
    ↓
Training Server (localhost:4747)
    ↓
Task Queue
    ↓
Agent Runner(s) (can be multiple)
    ↓
OpenAI API Calls (parallel)
    ↓
Results aggregated back
```
✅ **Pros:** Parallel execution, scalable, production-ready
❌ **Cons:** More complex setup, more infrastructure

---

## 🛠️ Troubleshooting

### Issue: "No module named 'agentlightning'"
**Solution:**
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
```

### Issue: "OpenAI API Error: Invalid API key"
**Solution:** Check your API key:
```bash
echo $OPENAI_API_KEY  # Should print your key
```

If empty:
```bash
export OPENAI_API_KEY="sk-proj-your-actual-key"
```

### Issue: "Model not found: gpt-4o-mini"
**Solution:** Try a different model:
```python
model="gpt-3.5-turbo"  # Always available
```

### Issue: Rate limited (429 error)
**Solution:** Add delay between requests:
```python
import time
time.sleep(1)  # Add before API call
```

---

## 📚 Next Steps

### For Learning
1. **Run `run_simple.py`** to understand the basic flow
2. **Modify the task** to test different questions
3. **Add custom scoring** for your use case
4. **Read the code comments** - they explain each part

### For Production
1. Start with `run_simple.py` for small-scale testing
2. Move to `run_agent_complete.py` for multi-threaded execution
3. Scale to multi-terminal setup if needed
4. Add proper logging and monitoring

### For Advanced Usage
- Implement batch evaluation across multiple tasks
- Add A/B testing framework
- Integrate with your application
- Use Agent Lightning's distributed runner features

---

## 💰 Cost Estimation

### Using gpt-4o-mini
Per prompt evaluation:
- Avg prompt: ~100 tokens = $0.00003
- Avg response: ~50 tokens = $0.00015
- **Total per prompt: ~$0.0002**

Testing 100 prompts = ~$0.02

### Ways to Save Money
1. Use `gpt-3.5-turbo` (~5x cheaper)
2. Limit response tokens
3. Cache common responses
4. Use smaller tasks

---

## 🎓 Understanding the Code

### PromptTemplate
```python
# Define a template with a placeholder
template = "You are an expert. Answer: {any_question}"

# Create PromptTemplate object
prompt = PromptTemplate(template=template, engine="f-string")

# Format with actual question
formatted = prompt.format(any_question="What is 2+2?")
# Result: "You are an expert. Answer: What is 2+2?"
```

### Scoring Function
```python
def evaluate_prompt(task, prompt_template):
    # 1. Format the prompt
    prompt_text = prompt_template.format(any_question=task)
    
    # 2. Call OpenAI
    response = client.chat.completions.create(...)
    llm_output = response.choices[0].message.content
    
    # 3. Score the output
    score = calculate_score(llm_output)
    
    # 4. Return score
    return score
```

### Main Algorithm
```python
async def find_best_prompt(prompts_to_test, task_input):
    results = []
    
    for prompt in prompts_to_test:
        score = evaluate_prompt(task_input, prompt)
        results.append((prompt, score))
    
    best = max(results, key=lambda x: x[1])
    return best
```

---

## 📞 Support Resources

- **Agent Lightning Docs:** https://github.com/microsoft/agent-lightning
- **OpenAI API Docs:** https://platform.openai.com/docs/
- **Prompt Engineering Guide:** https://platform.openai.com/docs/guides/prompt-engineering

---

## ✨ Summary

✅ **Your Agent Lightning system is working!**

- **Quick run:** `python run_simple.py`
- **Customizable:** Edit prompts and scoring
- **Scalable:** Can upgrade to full agent architecture
- **Cost-effective:** Starting at ~$0.0002 per prompt

**Happy optimizing! 🚀**
