# Sample Agent Lightning

Agent Lightning quick start and examples.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install agent-lightning openai
export OPENAI_API_KEY='your-key-here'
```

## Run

```bash
source .venv/bin/activate

# Quick start (interactive menu)
./run.sh

# Or run directly:
python run_agent_complete.py   # Single process
python run_simple.py           # Simple example

# Multi-terminal setup:
python server_runner.py        # Terminal 1
python agent_runner.py         # Terminal 2
python algorithm_runner.py     # Terminal 3
```
