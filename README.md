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
git clone https://github.com/AojdevStudio/pt-agent.git
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

Create a `.env` file with:
- `OPENAI_API_KEY`: Your OpenAI API key
- `OURA_PERSONAL_ACCESS_TOKEN`: Token for accessing Oura Ring data
- `DATABASE_URL`: Connection string for the database

## Usage

The Personal AI Training Agent provides a simple CLI interface:

### Plan Commands

```bash
# View today's workout
uv run python -m personal_ai_trainer.cli.main p today

# View weekly plan
uv run python -m personal_ai_trainer.cli.main p week

# View specific day
uv run python -m personal_ai_trainer.cli.main p day monday
```

### Log Commands

```bash
# Log a workout
uv run python -m personal_ai_trainer.cli.main l workout --notes "Felt strong today"

# Log exercises
uv run python -m personal_ai_trainer.cli.main l exercise --name "Bench Press" --sets 3 --reps 8 --weight 150

# View history
uv run python -m personal_ai_trainer.cli.main l history
```

### Research Commands

```bash
# Add research
uv run python -m personal_ai_trainer.cli.main r add --file path/to/document.pdf

# Search knowledge base
uv run python -m personal_ai_trainer.cli.main r search "hypertrophy training"
```

### Progress Commands

```bash
# View stats
uv run python -m personal_ai_trainer.cli.main pr stats

# View badges
uv run python -m personal_ai_trainer.cli.main pr badges

# View summary
uv run python -m personal_ai_trainer.cli.main pr summary
```

### Profile Commands

```bash
# Create a new user profile (interactive)
uv run python -m personal_ai_trainer.cli.main profile create

# List all profiles
uv run python -m personal_ai_trainer.cli.main profile list

# View an existing profile (uses default if not specified)
uv run python -m personal_ai_trainer.cli.main profile view [--user-id YOUR_USER_ID]

# Update an existing profile interactively
uv run python -m personal_ai_trainer.cli.main profile update [--user-id YOUR_USER_ID]
```

Profile data storage:
- To enable Supabase storage for profiles, set the following environment variables:
  ```bash
  export SUPABASE_URL=your_supabase_url
  export SUPABASE_KEY=your_supabase_key
  ```
- If Supabase is not configured or unavailable, profiles and default user ID are stored locally under `~/.pt-agent/`:
  - `profiles.json` contains all created profiles.
  - `config.json` stores the `default_user_id`.

After creating a profile with `profile create`, the `user_id` is set as the default, and subsequent plan commands will use it automatically:

```bash
pt p --goal strength
pt p today
```

## Troubleshooting

- **Commands not working?** Make sure your virtual environment is activated and you've installed the package with `uv pip install -e .`
- **Missing data?** Check your `.env` file to ensure all API keys are correctly set
- **Need help?** Run any command with `--help`:
  ```bash
  uv run python -m personal_ai_trainer.cli.main --help
  uv run python -m personal_ai_trainer.cli.main p --help
  ```

For more detailed information, see the original documentation or contact support.
