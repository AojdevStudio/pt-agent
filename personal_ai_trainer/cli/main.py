"""Main CLI entry point for the Personal AI Training Agent.

This CLI allows users to interact with the system, view workout plans, log workouts, add research documents, and view progress.
"""

import typer
from personal_ai_trainer.cli.commands import plan, log, research, progress

app = typer.Typer(help="Personal AI Training Agent CLI. Your personalized fitness assistant.")

# Register subcommands
app.add_typer(plan.app, name="plan", help="View workout plans.")
app.add_typer(log.app, name="log", help="Log workouts and view workout history.")
app.add_typer(research.app, name="research", help="Manage research documents and search the knowledge base.")
app.add_typer(progress.app, name="progress", help="View progress statistics, badges, and summaries.")


def main():
    """Entry point for the CLI."""
    try:
        app()
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    main()