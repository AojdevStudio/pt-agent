<!--
Phase 2 Detailed Plan: Interactive Onboarding & Enhanced CLI UX
-->
# Phase 2 Detailed Plan: Interactive Onboarding & Enhanced CLI UX

## 1. Overview
This document outlines the detailed tasks, timeline, and deliverables for Phase 2, focusing on:
- Interactive user onboarding and profile persistence
- A richer, stateful CLI experience using Rich and interactive prompts
- Multi-turn conversational hooks for workout plan generation
- UI abstraction to enable future TUI or Web integrations

## 2. Goals & Scope
- Capture and persist a real UserProfile via CLI
- Enhance CLI with tables, progress bars, and multi-step flows
- Introduce `--interactive` conversational mode in the OrchestratorAgent
- Keep business logic UI-agnostic to support future frontends

## 3. Detailed Tasks

### 3.1 Interactive Onboarding & Profile Management
- Create `cli/commands/profile.py` with subcommands:
  - `profile create`: prompt for name, age, height, weight, fitness level, goals, days/week, equipment
  - `profile view [--user-id]`: display stored UserProfile as a Rich table
  - `profile update [--user-id]`: allow modifying individual fields via prompts
- Implement `database/user_repository.py` CRUD functions using `UserProfile` model
- Add `user_profiles` table migration in Supabase (SQL or via existing script)
- Store default `user_id` in a local config file (`~/.pt-agent/config.json`)
- Update all CLI commands to use the persisted `user_id` when none is provided

### 3.2 Rich CLI UX
- Add dependency on `rich` and optionally `questionary` or `InquirerPy`
- Refactor plan/log/progress/research commands to:
  - Display workouts as Rich tables (Day, Activity, Sets, Reps, Load)
  - Show progress bars or sparklines for weekly progress
  - Use list prompts and confirmations for choices and overrides
- Implement a session context to share state (e.g., user profile, last plan)
- Update `README.md` to document new flags and interactive flows

### 3.3 Conversational Agent Hooks
- Extend `OrchestratorAgent.generate_workout_plan(interactive=True)`:
  - Multi-turn OpenAI chat to collect missing preferences
  - Validate and store each response before proceeding
- Expose `--interactive` flag on `plan generate` and `plan today`
- Log all prompts/responses in `~/.pt-agent/logs/` for audit/debugging

### 3.4 TUI / Web UI Preparation
- Extract Typer/Rich calls into a thin `cli_adapter.py` interface
- Sketch a minimal FastAPI app in `api/app.py`:
  - `POST /profiles`, `GET /profiles/{id}`
  - `GET /plans/today`, `POST /plans/generate`
  - Inject agents via DIContainer
- Write integration tests for API routes using pytest and TestClient

## 4. Timeline & Milestones
- **Weeks 1–2**: Profile onboarding + repository + DB migration + config file
- **Weeks 3–4**: Rich CLI UX (tables, prompts, session state) + docs
- **Weeks 5–6**: Interactive conversational flows + logging
- **Weeks 7–8**: UI abstraction + FastAPI scaffolding + API tests

## 5. Dependencies & Prerequisites
- Supabase schema updated for `user_profiles`
- New packages: `rich`, `questionary` (or `InquirerPy`)
- ENV var `PT_AGENT_CONFIG_DIR` (optional override)

## 6. Deliverables
- `cli/commands/profile.py`, `database/user_repository.py`
- Enhanced CLI commands leveraging Rich and interactive prompts
- `OrchestratorAgent` interactive mode implementation
- `phase_2_plan.md` (this file) and updated `README.md`
- FastAPI skeleton in `api/app.py` + integration tests

## 7. Future Considerations
- Build a full TUI with Textual
- Develop a PWA front end with Next.js + FastAPI
- Voice command support and additional biometrics
- In-app notifications and scheduling