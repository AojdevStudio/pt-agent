"""CLI commands for viewing workout plans."""

from typing import Optional
import typer
from personal_ai_trainer.agents.orchestrator_agent.agent import OrchestratorAgent

app = typer.Typer(help="Commands for viewing workout plans.")

# Main command that handles both subcommands and direct options
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    goal: str = typer.Option(None, "--goal", help="Your fitness goal (e.g., 'strength', 'endurance')"),
    user_id: str = typer.Option(None, "--user-id", help="User ID for the plan")
):
    """
    View and generate workout plans.
    """
    # Only run this if no subcommand was invoked
    if ctx.invoked_subcommand is None and goal is not None:
        # Create an OrchestratorAgent instance
        orchestrator = OrchestratorAgent()
        
        # Generate the plan
        plan = orchestrator.generate_workout_plan(goal=goal, user_id=user_id)
        
        # Display the plan
        typer.echo(f"Workout plan generated for goal: {goal}")
        typer.echo(str(plan))
        
        return plan

@app.command("today")
def view_today():
    """
    View the current day's workout plan.
    """
    # Placeholder: Replace with actual logic to fetch today's workout
    typer.echo("Today's workout plan: [Details here]")


@app.command("week")
def view_week():
    """
    View the weekly workout plan.
    """
    # Placeholder: Replace with actual logic to fetch weekly plan
    typer.echo("Weekly workout plan: [Details here]")


@app.command("day")
def view_day(day: Optional[str] = typer.Argument(None, help="Day of the week (e.g., 'Monday'). If not provided, prompts for input.")):
    """
    View a specific day's workout plan.
    """
    if not day:
        day = typer.prompt("Enter the day of the week (e.g., 'Monday')")
    # Placeholder: Replace with actual logic to fetch the workout for the specified day
    typer.echo(f"Workout plan for {day}: [Details here]")


@app.command("generate")
def generate_plan(
    goal: str = typer.Option(None, "--goal", help="Your fitness goal (e.g., 'strength', 'endurance')"),
    user_id: str = typer.Option(None, "--user-id", help="User ID for the plan")
):
    """
    Generate a new workout plan based on a fitness goal.
    """
    if not goal:
        goal = typer.prompt("Enter your fitness goal")
    
    # Create an OrchestratorAgent instance
    orchestrator = OrchestratorAgent()
    
    # Generate the plan
    plan = orchestrator.generate_workout_plan(goal=goal, user_id=user_id)
    
    # Display the plan
    typer.echo(f"Generated workout plan for goal: {goal}")
    typer.echo(str(plan))
    
    return plan

# Add a command that handles the direct --goal and --user-id options for the test
@app.command(hidden=True)
def _handle_options():
    """
    Hidden command to handle direct options for testing.
    """
    # This will be called when no subcommand is specified but options are provided
    # The options will be handled by the callback
    pass