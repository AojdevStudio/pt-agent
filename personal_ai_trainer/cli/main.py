"""Main CLI entry point for the Personal AI Training Agent.

This CLI allows users to interact with the system, view workout plans, log workouts, add research documents, and view progress.
"""

import typer
from personal_ai_trainer.cli.commands import plan, log, research, progress, profile

app = typer.Typer(
    help="Personal AI Training Agent CLI",
    name="pt",  # Shorter base command name
    short_help="Your AI fitness assistant"
)

# Register subcommands with shorter aliases
app.add_typer(
    plan.app,
    name="p",  # Short alias
    help="View workout plans"
)

app.add_typer(
    log.app,
    name="l",  # Short alias
    help="Log workouts and view history"
)

app.add_typer(
    research.app,
    name="r",  # Short alias
    help="Manage research documents"
)

app.add_typer(
    progress.app,
    name="pr",  # Short alias
    help="View progress and stats"
)
app.add_typer(
    profile.app,
    name="profile",
    help="Manage user profiles"
)

def main():
    """Entry point for the CLI."""
    try:
        app()
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    main()