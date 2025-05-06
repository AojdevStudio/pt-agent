# Personal AI Training Agent

## Overview

The Personal AI Training Agent is your personalized fitness coach that creates workout plans based on your body's readiness and fitness goals. It uses data from your Oura Ring (if you have one) and adapts your workouts to ensure optimal performance and recovery.

## What It Does

- Creates personalized workout plans that adjust to your body's needs
- Tracks your progress and keeps you motivated
- Uses scientific research to inform workout recommendations
- Integrates with Oura Ring to measure your recovery status
- Calculates the right weights and intensity for your exercises

## Quick Start Guide

### 1. Set Up Your Environment

```bash
# Clone the repository
git clone <repository-url>
cd pt-agent

# Create and activate a virtual environment (optional but recommended)
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install the package in development mode
uv pip install -e .

# Set up your configuration
cp .env.example .env
# Edit .env with your API keys and settings
```

### 2. Configure Your Settings

Edit the `.env` file with:
- Your OpenAI API key
- Oura Ring access token (if you have one)
- Database connection details

### 3. Try These Commands

```bash
# View today's workout plan
uv run python -m personal_ai_trainer.cli.main plan today

# View your weekly workout plan
uv run python -m personal_ai_trainer.cli.main plan week

# Log a completed workout
uv run python -m personal_ai_trainer.cli.main log workout --date 2023-05-05 --notes "Felt great today"

# Check your progress
uv run python -m personal_ai_trainer.cli.main progress summary
```

## Common Tasks

### Workout Planning

```bash
# Generate a new workout plan with a specific goal
uv run python -m personal_ai_trainer.cli.main plan generate --goal "Improve 5k time"

# View plan for a specific date
uv run python -m personal_ai_trainer.cli.main plan day --date 2023-05-10
```

### Logging Your Workouts

```bash
# Log a workout
uv run python -m personal_ai_trainer.cli.main log workout --date 2023-05-05 --notes "Felt strong"

# Log specific exercises
uv run python -m personal_ai_trainer.cli.main log exercise --name "Bench Press" --sets 3 --reps 10 --weight 50.5

# View your workout history
uv run python -m personal_ai_trainer.cli.main log history
```

### Adding Research

```bash
# Add a research document to improve your plans
uv run python -m personal_ai_trainer.cli.main research add --file path/to/document.pdf

# Search the knowledge base
uv run python -m personal_ai_trainer.cli.main research search --query "strength training"
```

## Troubleshooting

- **Commands not working?** Make sure your virtual environment is activated and you've installed the package with `uv pip install -e .`

- **Missing data?** Check your `.env` file to ensure all API keys are correctly set

- **Need more help?** Run any command with `--help` for more information:
  ```bash
  uv run python -m personal_ai_trainer.cli.main --help
  ```

For more detailed information, see the original documentation or contact support.
