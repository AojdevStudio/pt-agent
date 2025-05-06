"""CLI commands for logging workouts and viewing workout history."""

from typing import Optional
import typer

app = typer.Typer(help="Commands for logging workouts and viewing workout history.")

@app.command("workout")
def log_workout(date: Optional[str] = typer.Option(None, help="Date of the workout (YYYY-MM-DD). If not provided, uses today."),
                notes: Optional[str] = typer.Option(None, help="Optional notes for the workout.")):
    """
    Log a completed workout.
    """
    if not date:
        date = typer.prompt("Enter the date of the workout (YYYY-MM-DD)", default=None)
    if not notes:
        notes = typer.prompt("Enter any notes for the workout (optional)", default="")
    # Placeholder: Replace with actual logic to log the workout
    typer.echo(f"Logged workout for {date}. Notes: {notes}")


@app.command("exercise")
def log_exercise(name: str = typer.Option(..., prompt=True, help="Name of the exercise."),
                 sets: int = typer.Option(..., prompt=True, help="Number of sets."),
                 reps: int = typer.Option(..., prompt=True, help="Number of reps per set."),
                 weight: Optional[float] = typer.Option(None, help="Weight used (if applicable).")):
    """
    Log an individual exercise.
    """
    # Placeholder: Replace with actual logic to log the exercise
    typer.echo(f"Logged exercise: {name}, Sets: {sets}, Reps: {reps}, Weight: {weight if weight is not None else 'N/A'}")


@app.command("history")
def history(limit: int = typer.Option(10, help="Number of recent workouts to display.")):
    """
    View workout history.
    """
    # Placeholder: Replace with actual logic to fetch workout history
    typer.echo(f"Showing the last {limit} workouts: [Workout history details here]")