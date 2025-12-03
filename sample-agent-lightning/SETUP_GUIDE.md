# Agent Lightning Setup & Execution Guide

## Overview
Your `apo_custom_algorithm.py` script implements a **Prompt Optimization** system using Agent Lightning. It consists of:

1. **`simple_agent`** - An LLM agent that answers questions using a prompt template
2. **`find_best_prompt`** - An optimization algorithm that tests multiple prompts and finds the best one

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           RL Framework / Training Algorithm             │
│              (find_best_prompt function)                 │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
   ┌────▼────────────┐         ┌─────▼──────────┐
   │ Training Server │         │ Agent Clients  │
   │ (Port 4747)     │◄───────►│ (Runners)      │
   └────────────────┘         └────────────────┘
        │                             │
        │                             │
   ┌────▼────────────────────────────▼───┐
   │    LightningStoreClient              │
   │ - Manages prompts/resources          │
   │ - Enqueues rollouts (tasks)          │
   │ - Collects results & rewards         │
   └─────────────────────────────────────┘
```

## Prerequisites

### 1. Environment Setup ✓ (Already installed)
```bash
source .venv/bin/activate  # Activate the venv
```

### 2. API Keys Required
You need valid API credentials for:
- **OpenAI API Key** (for GPT model calls)

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
# Optional: if using custom endpoint
export OPENAI_API_BASE="https://api.openai.com/v1"
```

## How to Run

### Option 1: Complete End-to-End Execution (Recommended for Testing)

Run all components together in one session:

```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key-here"

# Use the complete runner script
python run_agent_complete.py
```

### Option 2: Manual Multi-Terminal Setup (For Development/Debugging)

**Terminal 1 - Start the Training Server:**
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
python server_runner.py
# Output: Server started at http://localhost:4747
```

**Terminal 2 - Start Agent Runner(s):**
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key-here"
python agent_runner.py
# Output: [Runner] Waiting for tasks...
```

**Terminal 3 - Execute the Algorithm:**
```bash
cd /home/viet2005/workspace/fsoft/sample-agent-lightning
source .venv/bin/activate
export OPENAI_API_KEY="your-key-here"
python algorithm_runner.py
# Output: [Algo] Starting prompt optimization...
```

## Files Generated

Files created in this folder:

1. **run_agent_complete.py** - Complete single-script runner (easiest to use)
2. **server_runner.py** - Training server component
3. **agent_runner.py** - Agent client/runner component
4. **algorithm_runner.py** - Algorithm execution component
5. **SETUP_GUIDE.md** - This guide

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Make sure you activated the venv:
```bash
source .venv/bin/activate
pip list | grep agentlightning  # Should show version
```

### Issue: OpenAI API Error
**Solution:** Check your API key:
```bash
echo $OPENAI_API_KEY  # Should show your key, not empty
```

### Issue: "Connection refused" on localhost:4747
**Solution:** Make sure the server is running in Terminal 1 before starting clients

### Issue: Model not found "gpt-4.1-nano"
**Solution:** Update the model name in `apo_custom_algorithm.py` to a valid model:
- `gpt-4o-mini` (recommended, cheaper)
- `gpt-4` (if you have access)
- `gpt-3.5-turbo` (oldest, but works)

## Expected Output

When running successfully, you should see:
```
[Server] Training Server started on http://127.0.0.1:4747
[Runner] Agent runner initialized, waiting for tasks...
[Algo] Updating prompt template to: 'You are a helpful assistant.'
[Algo] Queuing task for clients...
[Algo] Task 'rollout-123' is now available for clients.
[Rollout] LLM returned: "The capital of France is Paris..."
[Algo] Final reward: 0.75
[Algo] All prompts and their rewards: [(...), (...), ...]
[Algo] Best prompt found: '...' with reward 0.89
```

## Next Steps

1. **Update the scoring logic** - Currently uses random.uniform(0, 1), implement actual scoring
2. **Add more prompts** - Modify `prompts_to_test` in the algorithm
3. **Change the task** - Modify `task_input` to test different scenarios
4. **Tune hyperparameters** - Adjust server/runner configurations as needed

## Resources

- [Agent Lightning Docs](https://github.com/microsoft/agent-lightning)
- [OpenAI API Docs](https://platform.openai.com/docs/)
