# 🚀 Agent Lightning - Complete Setup & Usage Guide

## ✨ What You Have

A complete **AI Agent Optimization Framework** with your original prompt optimization algorithm from `apo_custom_algorithm.py`, now fully functional with multiple execution options.

---

## 🎯 Quick Start (Choose One)

### Option 1: Simple Direct Optimization ⭐ RECOMMENDED
**Best for:** Learning, testing, quick runs

```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key-here"
python run_simple.py
```

✅ Works immediately
✅ No infrastructure needed
✅ Clear output
❌ Single-threaded

**Expected output:**
```
[Algo] Testing 3 prompts...
[Agent] Response: The capital of France is Paris...
🏆 Best prompt: You are knowledgeable...
🏆 Best score:  1.000
```

---

### Option 2: Full Agent Lightning Architecture
**Best for:** Production, multi-threaded, scalable

Open **3 separate terminals**:

**Terminal 1 - Training Server:**
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
python server_runner.py
```
Output: `[Server] ✓ Training Server started successfully! URL: http://127.0.0.1:4747`

**Terminal 2 - Agent Runner (wait for Terminal 1 ready):**
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key-here"
python agent_runner.py
```
Output: `[Runner] Waiting for tasks...`

**Terminal 3 - Algorithm (wait for Terminal 2 ready):**
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key-here"
python algorithm_runner.py
```

✅ Multi-threaded execution
✅ Scalable architecture
✅ Production-ready
❌ More complex setup

---

### Option 3: Interactive Menu
**Best for:** Choosing your preferred setup**

```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
bash run.sh
```

Then select option 1, 2, 3, 4, or 5 from the menu.

---

## 📁 Scripts Provided

| File | Purpose | Type |
|------|---------|------|
| **run_simple.py** ⭐ | Single-process prompt optimizer | Quick start |
| run_agent_complete.py | Full architecture in one file | Advanced |
| server_runner.py | Training server only | Component |
| agent_runner.py | Agent runner only | Component |
| algorithm_runner.py | Algorithm only | Component |
| run.sh | Interactive menu | Launcher |

### Documentation

| File | Content |
|------|---------|
| **GETTING_STARTED.md** | Quick guide with customization |
| **README_AGENT_LIGHTNING.md** | Complete overview |
| **SETUP_GUIDE.md** | Technical architecture |

---

## 🔑 API Key Setup

### Getting Your OpenAI Key
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (it starts with `sk-proj-`)

### Setting It Up

**Temporary (current session only):**
```bash
export OPENAI_API_KEY="sk-proj-your-actual-key"
```

**Permanent (add to ~/.bashrc or ~/.zshrc):**
```bash
echo 'export OPENAI_API_KEY="sk-proj-your-actual-key"' >> ~/.bashrc
source ~/.bashrc
```

**Verify it's set:**
```bash
echo $OPENAI_API_KEY  # Should print your key
```

---

## 🎨 Customization Examples

### Change the Task
Edit `run_simple.py`, line ~67:
```python
task_input = "What is the capital of France?"
```
Change to any question you want.

### Add More Prompts
Edit `run_simple.py`, line ~63:
```python
prompts_to_test = [
    "Your prompt 1: {any_question}",
    "Your prompt 2: {any_question}",
    "Your prompt 3: {any_question}",
    # Add more here!
]
```

### Use a Different Model
Edit `run_simple.py`, line ~41:
```python
model="gpt-4o-mini"  # Change this
```

Available models:
- `gpt-4o-mini` (cheapest - recommended)
- `gpt-4o` (more capable)
- `gpt-3.5-turbo` (budget option)
- `gpt-4` (most expensive)

### Customize Scoring
Edit `run_simple.py`, in the `evaluate_prompt()` function, ~line 47:

**Current scoring (based on response length):**
```python
score = min(1.0, len(llm_output) / 200.0)
```

**Better scoring (based on relevance):**
```python
def score_response(response, task):
    """Score based on relevance and quality."""
    # Check if response addresses the task
    relevance = 0.5 if "capital" in response.lower() else 0.2
    
    # Check length (more detail = higher score)
    length = min(1.0, len(response) / 200.0)
    
    # Combine scores
    return relevance * 0.6 + length * 0.4
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'agentlightning'"
**Problem:** Virtual environment not activated
**Solution:**
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
```

### "OPENAI_API_KEY environment variable not set"
**Problem:** API key not configured
**Solution:**
```bash
export OPENAI_API_KEY="sk-proj-your-key-here"
echo $OPENAI_API_KEY  # Verify it's set
```

### "Invalid API key"
**Problem:** Wrong or expired API key
**Solution:**
1. Go to https://platform.openai.com/api-keys
2. Create a new key
3. Set it: `export OPENAI_API_KEY="new-key"`

### "Model not found: gpt-4o-mini"
**Problem:** Your account doesn't have access to this model
**Solution:** Edit `run_simple.py` and use:
```python
model="gpt-3.5-turbo"
```

### "Connection refused" on port 4747
**Problem:** Server not running in multi-terminal setup
**Solution:** Make sure Terminal 1 has the server running:
```bash
python server_runner.py
```

### Timeout errors
**Problem:** Taking too long to get API response
**Solution:** Wait a moment and try again, or check your internet connection

---

## 💡 Architecture Explanation

### Simple Version Flow
```
Your Task
    ↓
For Each Prompt:
    ├─ Format: prompt + task
    ├─ Call OpenAI API
    ├─ Get response
    └─ Score response
    ↓
Find Best Prompt
    ↓
Display Results
```

### Full Agent Lightning Flow
```
Your Task
    ↓
Training Server (Central Hub)
    ├─ Manages prompts/resources
    ├─ Queues tasks
    └─ Collects results
    ↓
Agent Runner(s) (Workers)
    ├─ Pick up tasks
    ├─ Call OpenAI
    └─ Return scores
    ↓
Algorithm (Orchestrator)
    ├─ Queues prompts as tasks
    ├─ Waits for results
    └─ Finds best prompt
    ↓
Display Results
```

**Why use full version?**
- Can run multiple agent runners in parallel
- Better for testing hundreds of prompts
- More robust error handling
- Production-ready infrastructure

---

## 📊 Cost Estimation

### Using gpt-4o-mini (Current)
Per evaluation:
- Prompt tokens: ~100 tokens × $0.00003/1K = $0.000003
- Response tokens: ~50 tokens × $0.00015/1K = $0.0000075
- **Total per prompt: ~$0.000001 to $0.0003**

### Examples
- 10 prompts: ~$0.003
- 100 prompts: ~$0.03
- 1000 prompts: ~$0.30

### Save Money
1. Use `gpt-3.5-turbo` (~5x cheaper)
2. Limit `max_tokens` parameter
3. Batch similar evaluations
4. Use simpler scoring logic

---

## 📈 What's Next?

### 1. Learn Phase
- ✅ Run `run_simple.py`
- ✅ Modify the task
- ✅ Add custom prompts
- ✅ Improve scoring logic

### 2. Develop Phase
- Test with your real use case
- Implement production scoring
- Add logging and monitoring
- Test edge cases

### 3. Production Phase
- Switch to full Agent Lightning setup
- Scale to multiple workers
- Integrate with your application
- Set up monitoring/alerting

---

## 🎓 Code Structure

### PromptTemplate (from Agent Lightning)
```python
# Create a template with placeholder
prompt = PromptTemplate(
    template="You are an expert. Answer: {any_question}",
    engine="f-string"
)

# Format with actual question
formatted = prompt.format(any_question="What is 2+2?")
# Result: "You are an expert. Answer: What is 2+2?"
```

### Scoring Function
```python
def evaluate_prompt(task, prompt_template):
    """Score a prompt by running it and rating response."""
    # 1. Format the prompt
    prompt_text = prompt_template.format(any_question=task)
    
    # 2. Send to OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_text}],
        max_tokens=100,
    )
    
    # 3. Get the response text
    llm_output = response.choices[0].message.content
    
    # 4. Calculate score
    score = min(1.0, len(llm_output) / 200.0)
    
    # 5. Return the score
    return score
```

### Main Algorithm
```python
async def find_best_prompt(prompts_to_test, task_input):
    """Test all prompts and find the best one."""
    results = []
    
    # Test each prompt
    for prompt in prompts_to_test:
        score = evaluate_prompt(task_input, prompt)
        results.append((prompt, score))
    
    # Find best
    best_prompt, best_score = max(results, key=lambda x: x[1])
    
    return best_prompt, best_score
```

---

## 📚 Resources

- **Agent Lightning GitHub:** https://github.com/microsoft/agent-lightning
- **OpenAI API Docs:** https://platform.openai.com/docs/api-reference
- **Prompt Engineering Guide:** https://platform.openai.com/docs/guides/prompt-engineering
- **Python Async Tutorial:** https://realpython.com/async-io-python/

---

## ✅ Checklist

Before running:
- [ ] API key from openai.com
- [ ] Virtual environment activated (`source .venv/bin/activate`)
- [ ] Environment variable set (`export OPENAI_API_KEY=...`)
- [ ] Script chosen (`run_simple.py` recommended)

Ready to run:
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key"
python run_simple.py
```

---

## 🎉 Summary

**You now have:**
- ✅ Full working prompt optimization system
- ✅ Simple version for quick testing
- ✅ Full Agent Lightning architecture for production
- ✅ Complete documentation and examples
- ✅ Cost-effective implementation

**Next step:** Run `python run_simple.py` and optimize your prompts!

---

**Happy optimizing! 🚀**
