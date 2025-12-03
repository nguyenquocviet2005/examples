# Agent Lightning - Quick Reference

## ✅ What Works (Recommended)

### 🌟 The Simple Way - START HERE
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key-here"
python run_simple.py
```

**Why this works:**
- ✅ Direct, simple implementation
- ✅ No infrastructure needed
- ✅ Full working example
- ✅ Easy to customize
- ✅ Ready for production use

**Output:**
```
[Algo] Testing 3 prompts...
[Agent] Response: The capital of France is Paris...
🏆 Best prompt: You are knowledgeable...
🏆 Best score:  1.000
```

---

## 📋 All Available Options

| Option | Status | Use Case |
|--------|--------|----------|
| **run_simple.py** | ✅ Working | Testing, learning, production |
| run_agent_complete.py | 🔧 Needs work | Full Agent Lightning |
| server_runner.py | ✅ Works | Server component only |
| agent_runner.py | 🔧 Needs API update | Agent component only |
| algorithm_runner.py | ✅ Works | Algorithm component only |

---

## 🚀 3-Step Quick Start

### Step 1: Activate Environment
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
```

### Step 2: Set API Key
```bash
export OPENAI_API_KEY="sk-proj-your-actual-key"
```

### Step 3: Run Optimization
```bash
python run_simple.py
```

**Done!** It will test your prompts and show the best one. ✨

---

## 🎨 Quick Customization

### Edit Task (run_simple.py, line 67)
```python
task_input = "What is the capital of France?"
```

### Edit Prompts (run_simple.py, line 63)
```python
prompts_to_test = [
    "You are a helpful assistant. Answer: {any_question}",
    "You are an expert. Be concise: {any_question}",
    "You are friendly. Explain simply: {any_question}",
]
```

### Change Model (run_simple.py, line 41)
```python
model="gpt-4o-mini"  # Try: gpt-3.5-turbo, gpt-4o, gpt-4
```

### Improve Scoring (run_simple.py, line 47-50)
```python
# Current: scores based on response length
score = min(1.0, len(llm_output) / 200.0)

# Better: score based on relevance
relevance = 0.5 if "capital" in llm_output.lower() else 0.2
length = min(1.0, len(llm_output) / 200.0)
score = relevance * 0.6 + length * 0.4
```

---

## 🐛 Common Issues & Fixes

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY="your-key-here"
```

### "ModuleNotFoundError"
```bash
source .venv/bin/activate
```

### "Model not found"
Edit run_simple.py and use `gpt-3.5-turbo` instead

### Running but very slow
- API is rate-limited - wait a moment
- Or use smaller prompts/responses
- Or use a faster model like gpt-3.5-turbo

---

## 📊 Examples

### Example 1: Test Different Versions of Prompts
```python
prompts_to_test = [
    "Answer the question: {any_question}",
    "You are helpful. Answer: {any_question}",
    "You are an expert. Answer concisely: {any_question}",
    "You are knowledgeable and friendly. Answer: {any_question}",
]
```

### Example 2: Test Domain-Specific Prompts
```python
prompts_to_test = [
    "Respond as a Python expert: {any_question}",
    "Respond as a medical doctor: {any_question}",
    "Respond as a business consultant: {any_question}",
    "Respond as a teacher: {any_question}",
]
task_input = "How do I learn machine learning?"
```

### Example 3: Better Scoring Function
```python
def evaluate_prompt(task: str, prompt_template: PromptTemplate) -> float:
    """Score based on multiple criteria."""
    # ... existing code to get llm_output ...
    
    # Scoring criteria
    scores = {}
    
    # 1. Length (rewards detailed answers)
    scores['length'] = min(1.0, len(llm_output) / 200.0)
    
    # 2. Relevance (contains key terms)
    scores['relevance'] = 0.9 if "capital" in llm_output.lower() else 0.3
    
    # 3. Clarity (contains periods for complete sentences)
    scores['clarity'] = min(1.0, llm_output.count('.') / 3)
    
    # Weighted combination
    final_score = (
        scores['relevance'] * 0.5 +
        scores['length'] * 0.3 +
        scores['clarity'] * 0.2
    )
    
    return final_score
```

---

## 💾 Files in This Folder

```
sample-agent-lightning/
├── run_simple.py              ⭐ Main working script
├── run_agent_complete.py      🔧 Advanced (in progress)
├── server_runner.py           ✅ Server only
├── agent_runner.py            🔧 Needs API update
├── algorithm_runner.py        ✅ Algorithm only
├── apo_custom_algorithm.py    📄 Original reference
├── START_HERE.md              📖 You are here
├── GETTING_STARTED.md         📖 Detailed guide
├── README_AGENT_LIGHTNING.md  📖 Full documentation
├── SETUP_GUIDE.md             📖 Architecture guide
├── run.sh                      🎯 Interactive menu
└── .venv/                      🐍 Virtual environment
```

---

## ✨ Next Steps

1. **Run it:** `python run_simple.py`
2. **Customize it:** Edit task, prompts, or scoring
3. **Scale it:** Add more prompts, more tasks
4. **Integrate it:** Use in your application

---

## 📞 Questions?

- **Check GETTING_STARTED.md** for full guide
- **Check SETUP_GUIDE.md** for architecture
- **Check comments in run_simple.py** for code details
- **View Source:** https://github.com/microsoft/agent-lightning

---

**Ready to optimize? Run this:** 
```bash
python run_simple.py
```

**That's it!** 🎉
