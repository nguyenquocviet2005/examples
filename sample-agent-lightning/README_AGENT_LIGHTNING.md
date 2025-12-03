# 🚀 Agent Lightning - Complete Setup Guide

Welcome! This guide will help you run the Agent Lightning prompt optimization system.

## 📋 What This Does

Your script implements an **AI Agent Optimization System** that:
1. Tests multiple LLM prompts
2. Measures their effectiveness with rewards
3. Identifies the best prompt based on performance

## ✅ Prerequisites

### Already Installed ✓
- ✓ Agent Lightning framework
- ✓ OpenAI Python client
- ✓ All required dependencies
- ✓ Virtual environment (`.venv`)

### What You Need to Provide
- 🔑 **OpenAI API Key** - Get from https://platform.openai.com/api-keys

## 🚀 Quick Start (2 Steps)

### Step 1: Set Your OpenAI API Key
```bash
export OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

### Step 2: Run the Agent
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
python run_agent_complete.py
```

That's it! The system will run completely in one process.

---

## 📊 Output Explanation

When running, you'll see output like:

```
[Main] Agent Lightning Complete Runner Starting...
[Main] Step 1: Initializing Training Server on 127.0.0.1:4747
[Main] ✓ Training Server started successfully!

[Main] Step 2: Creating Store Client
[Main] ✓ Store Client created!

[Main] Step 3: Running Prompt Optimization Algorithm
[Main] Task: What is the capital of France?
[Main] Testing 3 prompts...

[Algo] Testing prompt 1/3
[Algo] Updating prompt template to: 'You are a helpful assistant...'
[Agent] Using prompt: 'You are a helpful assistant...'
[Agent] LLM returned: 'The capital of France is Paris...'
[Agent] Assigned score: 0.87

[Algo] Final reward: 0.87

...

[Algo] Best prompt found: 'You are an expert...' with reward 0.92
```

---

## 🔄 Alternative: Multi-Terminal Setup

For development/debugging, run components separately:

### Terminal 1: Training Server
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
python server_runner.py
```

### Terminal 2: Agent Runner (wait for Terminal 1 ready)
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key-here"
python agent_runner.py
```

### Terminal 3: Algorithm (wait for Terminal 2 ready)
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key-here"
python algorithm_runner.py
```

---

## 📁 Files Explained

| File | Purpose |
|------|---------|
| `apo_custom_algorithm.py` | Your original algorithm (reference) |
| `run_agent_complete.py` | ⭐ **Use this** - Complete all-in-one runner |
| `server_runner.py` | Training server component (for multi-terminal) |
| `agent_runner.py` | Agent runner component (for multi-terminal) |
| `algorithm_runner.py` | Algorithm component (for multi-terminal) |
| `run.sh` | Interactive menu script |
| `SETUP_GUIDE.md` | Detailed technical guide |
| `README.md` | This file |

---

## 🎯 How It Works

### Architecture Diagram
```
┌─────────────────────────────────────────┐
│     Optimization Algorithm              │
│  (Testing different prompts)            │
└──────────────┬──────────────────────────┘
               │
        ┌──────▼──────────┐
        │ Training Server │ (Port 4747)
        └──────┬──────────┘
               │
        ┌──────▼──────────┐
        │  Agent Runner   │
        │ (Executes tasks)│
        └─────────────────┘
               │
        ┌──────▼──────────┐
        │  OpenAI API     │ (gpt-4o-mini)
        └─────────────────┘
```

### Execution Flow
1. **Algorithm** sends prompts to server
2. **Server** enqueues them as tasks
3. **Agent** picks up tasks and calls OpenAI API
4. **OpenAI** returns responses
5. **Agent** scores the responses and returns rewards
6. **Algorithm** finds the best prompt from rewards

---

## 🛠️ Customization

### Change the Task
Edit `run_agent_complete.py`, find this line:
```python
task_input = "What is the capital of France?"
```
Change to any question you want to test.

### Add More Prompts
In `run_agent_complete.py`, modify:
```python
prompts_to_test = [
    "Your prompt 1 here: {any_question}",
    "Your prompt 2 here: {any_question}",
    "Your prompt 3 here: {any_question}",
    # Add more prompts...
]
```

### Change the Model
In `run_agent_complete.py`, find:
```python
model="gpt-4o-mini"
```

Available models:
- `gpt-4o-mini` (cheapest, ✓ recommended)
- `gpt-4o` (more capable)
- `gpt-3.5-turbo` (older, still works)

### Improve Scoring
Currently uses random scores. Replace in `simple_agent()`:
```python
# Replace this:
score = random.uniform(0.5, 1.0)

# With actual scoring logic:
score = evaluate_response_quality(llm_output, task_input)
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused on localhost:4747"
**Cause:** Server isn't running
**Fix:** Make sure all components start in order

### Issue: "ModuleNotFoundError: agentlightning"
**Cause:** Virtual environment not activated
**Fix:** 
```bash
source .venv/bin/activate
```

### Issue: "OpenAI API Error: Invalid API key"
**Cause:** API key not set or incorrect
**Fix:**
```bash
export OPENAI_API_KEY="sk-proj-your-actual-key"
# Verify:
echo $OPENAI_API_KEY
```

### Issue: "Model not found gpt-4o-mini"
**Cause:** API key doesn't have access to that model
**Fix:** Try `gpt-3.5-turbo` instead in the code

### Issue: Timeouts waiting for rollouts
**Cause:** Agent runner not running or not receiving tasks
**Fix:** In multi-terminal setup, ensure Terminal 2 shows "Waiting for tasks"

---

## 📚 Learning Resources

- **Agent Lightning Docs:** https://github.com/microsoft/agent-lightning
- **OpenAI API Docs:** https://platform.openai.com/docs/
- **Prompt Engineering:** https://platform.openai.com/docs/guides/prompt-engineering

---

## ✨ Next Steps

1. **Get your API key** from OpenAI dashboard
2. **Run the basic example** to verify everything works
3. **Customize prompts** for your use case
4. **Implement real scoring** based on response quality
5. **Scale up** with more prompts and test cases

---

## 💡 Tips

- Monitor the output carefully to understand each step
- Start with fewer prompts (3-5) for testing
- Use `gpt-4o-mini` for cost-effective experimentation
- Check your OpenAI usage/billing to avoid surprises

---

## 🆘 Need Help?

1. **Check SETUP_GUIDE.md** for technical details
2. **Read output messages** carefully - they're descriptive
3. **Try multi-terminal setup** if single-process has issues
4. **Verify API key** is set correctly

---

**Happy optimizing! 🎉**
