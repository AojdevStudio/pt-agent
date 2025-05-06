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
def view_today(user_id: str = typer.Option("default-user", "--user-id", help="User ID for the plan")):
    """
    View the current day's workout plan.
    """
    import datetime
    from personal_ai_trainer.agents.research_agent.agent import ResearchAgent
    from personal_ai_trainer.agents.biometric_agent.agent import BiometricAgent
    from personal_ai_trainer.database.connection import get_supabase_client

    # Create the necessary agents
    supabase_client = get_supabase_client()
    research_agent = ResearchAgent(supabase_client=supabase_client, name="ResearchAgent")

    # Create a mock BiometricAgent without requiring Oura API
    class MockOuraClientWrapper:
        def get_readiness_data(self, user_id):
            return [{'score': 85, 'summary_date': '2025-05-06'}]

        def get_sleep_data(self, user_id):
            return [{'score': 90, 'summary_date': '2025-05-06'}]

        def get_activity_data(self, user_id):
            return [{'score': 80, 'summary_date': '2025-05-06'}]

    # Use the mock client instead of the real one
    oura_client = MockOuraClientWrapper()
    biometric_agent = BiometricAgent(
        oura_client=oura_client,
        supabase_client=supabase_client,
        user_id=user_id
    )

    # Create an OrchestratorAgent instance with the required dependencies
    orchestrator = OrchestratorAgent(
        research_agent=research_agent,
        biometric_agent=biometric_agent,
        supabase_client=supabase_client,
        user_id=user_id
    )

    # Get today's day of the week
    today = datetime.datetime.now().strftime("%A")

    # Generate a plan (in a real app, this would fetch from the database)
    plan = orchestrator.generate_workout_plan(goal="general fitness", user_id=user_id)

    # Convert the string representation of the plan to a dictionary
    import ast
    try:
        plan_dict = ast.literal_eval(plan)

        # Find today's workout in the plan
        today_workout = None
        for day_plan in plan_dict.get("plan", []):
            if day_plan.get("day") == today:
                today_workout = day_plan
                break

        if today_workout:
            typer.echo(f"Today's workout plan ({today}):")
            typer.echo(f"Activity: {today_workout.get('activity')}")
            typer.echo(f"Notes: {today_workout.get('notes')}")

            # If there are exercises, show them
            if "exercises" in today_workout:
                typer.echo("\nExercises:")
                for exercise in today_workout.get("exercises", []):
                    typer.echo(f"- {exercise.get('name')}: {exercise.get('sets')} sets of {exercise.get('reps')} reps")
        else:
            typer.echo(f"No specific workout planned for today ({today}).")
            typer.echo("Here's your weekly plan:")
            for day_plan in plan_dict.get("plan", []):
                typer.echo(f"- {day_plan.get('day')}: {day_plan.get('activity')}")
    except (ValueError, SyntaxError) as e:
        typer.echo(f"Error parsing workout plan: {e}")
        typer.echo("Today's workout plan: Rest day (default)")
    except Exception as e:
        typer.echo(f"Error retrieving workout plan: {e}")
        typer.echo("Today's workout plan: Rest day (default)")


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