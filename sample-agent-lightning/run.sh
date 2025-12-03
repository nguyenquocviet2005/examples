#!/bin/bash

# Agent Lightning - Quick Start Script
# Run this script to set up and execute the agent

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "============================================================"
echo "Agent Lightning - Quick Start"
echo "============================================================"
echo ""

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "❌ ERROR: .venv directory not found!"
    echo "   Please create a virtual environment first:"
    echo "   python3 -m venv .venv"
    exit 1
fi

# Activate venv
echo "[Setup] Activating virtual environment..."
source .venv/bin/activate

# Check OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: OPENAI_API_KEY not set!"
    echo "   Please set it with:"
    echo "   export OPENAI_API_KEY='your-openai-api-key-here'"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Show options
echo ""
echo "Select how to run Agent Lightning:"
echo ""
echo "1) Complete Runner (Single process - easier for testing)"
echo "2) Multi-Terminal Setup (Separate server, runner, algorithm)"
echo "3) Server Only (Run in Terminal 1 of 3)"
echo "4) Agent Runner Only (Run in Terminal 2 of 3)"
echo "5) Algorithm Only (Run in Terminal 3 of 3)"
echo ""
read -p "Enter your choice (1-5): " choice

echo ""

case $choice in
    1)
        echo "Running: Complete Agent Lightning Execution"
        echo "============================================================"
        python run_agent_complete.py
        ;;
    2)
        echo "Multi-Terminal Setup Instructions:"
        echo "============================================================"
        echo ""
        echo "Open 3 terminal windows and run these commands:"
        echo ""
        echo "Terminal 1 (Training Server):"
        echo "  cd $PROJECT_DIR"
        echo "  source .venv/bin/activate"
        echo "  python server_runner.py"
        echo ""
        echo "Terminal 2 (Agent Runner - wait for server to be ready):"
        echo "  cd $PROJECT_DIR"
        echo "  source .venv/bin/activate"
        echo "  export OPENAI_API_KEY='your-key-here'"
        echo "  python agent_runner.py"
        echo ""
        echo "Terminal 3 (Algorithm - wait for runner to be ready):"
        echo "  cd $PROJECT_DIR"
        echo "  source .venv/bin/activate"
        echo "  export OPENAI_API_KEY='your-key-here'"
        echo "  python algorithm_runner.py"
        echo ""
        ;;
    3)
        echo "Running: Training Server"
        echo "============================================================"
        python server_runner.py
        ;;
    4)
        echo "Running: Agent Runner"
        echo "============================================================"
        python agent_runner.py
        ;;
    5)
        echo "Running: Algorithm"
        echo "============================================================"
        python algorithm_runner.py
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "Done!"
echo "============================================================"
echo ""
