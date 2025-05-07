"""CLI commands for managing user profiles."""

import uuid
import json
import typer
from rich.console import Console
from rich.table import Table

from personal_ai_trainer.database.user_repository import (
    add_user_profile,
    get_user_profile,
    update_user_profile,
    list_user_profiles,
)
from personal_ai_trainer.database.models import UserProfile
from personal_ai_trainer.config.config import (
    set_default_user_id,
    get_default_user_id,
)

app = typer.Typer(help="Commands for managing user profiles.")
console = Console()

@app.command("create")
def create_profile():
    """Create a new user profile interactively."""
    name = typer.prompt("Name")
    age = typer.prompt("Age", type=int)
    height = typer.prompt("Height (cm)", type=float)
    weight = typer.prompt("Weight (kg)", type=float)
    fitness_level = typer.prompt(
        "Fitness level (e.g., beginner, intermediate, advanced)",
        default="",
    )
    goals = typer.prompt(
        "Primary fitness goals (e.g., strength, endurance)",
        default="",
    )
    days_per_week = typer.prompt(
        "Preferred workout days per week",
        type=int,
        default=3,
    )
    equipment = typer.prompt(
        "Available equipment (comma-separated)",
        default="",
    )

    preferences = {
        "days_per_week": days_per_week,
        "equipment": [e.strip() for e in equipment.split(",") if e.strip()],
    }

    user_id = str(uuid.uuid4())

    profile = UserProfile(
        user_id=user_id,
        name=name,
        age=age,
        height=height,
        weight=weight,
        fitness_level=fitness_level or None,
        goals=goals or None,
        preferences=json.dumps(preferences),
    )

    result = add_user_profile(profile)
    if result:
        typer.secho(f"User profile created with user_id: {user_id}", fg=typer.colors.GREEN)
        set_default_user_id(user_id)
        typer.secho("Set as default user profile.", fg=typer.colors.GREEN)
    else:
        typer.secho("Failed to create user profile.", fg=typer.colors.RED)

@app.command("view")
def view_profile(
    user_id: str = typer.Option(
        None, "--user-id", help="User ID of the profile to view"
    )
):
    """View an existing user profile."""
    if not user_id:
        user_id = get_default_user_id()
    if not user_id:
        typer.secho(
            "No user_id provided and no default set. Please create a profile first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    profile = get_user_profile(user_id)
    if not profile:
        typer.secho(f"No profile found for user_id: {user_id}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    table = Table(title=f"User Profile: {profile.name}")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("User ID", profile.user_id)
    table.add_row("Name", profile.name)
    table.add_row("Age", str(profile.age))
    table.add_row("Height (cm)", f"{profile.height}")
    table.add_row("Weight (kg)", f"{profile.weight}")
    table.add_row("Fitness Level", profile.fitness_level or "")
    table.add_row("Goals", profile.goals or "")

    # Parse preferences JSON
    try:
        prefs = json.loads(profile.preferences) if profile.preferences else {}
    except Exception:
        prefs = {}
    table.add_row("Days per Week", str(prefs.get("days_per_week", "")))
    table.add_row(
        "Equipment", ", ".join(prefs.get("equipment", []))
    )

    console.print(table)

@app.command("update")
def update_profile(
    user_id: str = typer.Option(
        None, "--user-id", help="User ID of the profile to update"
    )
):
    """Update an existing user profile interactively."""
    if not user_id:
        user_id = get_default_user_id()
    if not user_id:
        typer.secho(
            "No user_id provided and no default set. Please create a profile first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    profile = get_user_profile(user_id)
    if not profile:
        typer.secho(f"No profile found for user_id: {user_id}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    name = typer.prompt("Name", default=profile.name)
    age = typer.prompt("Age", type=int, default=profile.age)
    height = typer.prompt("Height (cm)", type=float, default=profile.height)
    weight = typer.prompt(
        "Weight (kg)", type=float, default=profile.weight
    )
    fitness_level = typer.prompt(
        "Fitness level (e.g., beginner, intermediate, advanced)",
        default=profile.fitness_level or "",
    )
    goals = typer.prompt(
        "Primary fitness goals (e.g., strength, endurance)",
        default=profile.goals or "",
    )

    # Parse existing preferences
    try:
        prefs = json.loads(profile.preferences) if profile.preferences else {}
    except Exception:
        prefs = {}
    days_per_week = typer.prompt(
        "Preferred workout days per week",
        type=int,
        default=prefs.get("days_per_week", 3),
    )
    equipment = typer.prompt(
        "Available equipment (comma-separated)",
        default=", ".join(prefs.get("equipment", [])),
    )

    new_prefs = {
        "days_per_week": days_per_week,
        "equipment": [
            e.strip() for e in equipment.split(",") if e.strip()
        ],
    }

    updates = {
        "name": name,
        "age": age,
        "height": height,
        "weight": weight,
        "fitness_level": fitness_level or None,
        "goals": goals or None,
        "preferences": json.dumps(new_prefs),
    }

    success = update_user_profile(user_id, updates)
    if success:
        typer.secho(
            f"User profile {user_id} updated successfully.",
            fg=typer.colors.GREEN,
        )
    else:
        typer.secho(
            f"Failed to update user profile {user_id}.",
            fg=typer.colors.RED,
        )

@app.command("list")
def list_profiles():
    """List all user profiles."""
    profiles = list_user_profiles()
    if not profiles:
        typer.secho(
            "No user profiles found.", fg=typer.colors.YELLOW
        )
        return

    table = Table(title="All User Profiles")
    table.add_column("User ID", style="bold")
    table.add_column("Name")
    table.add_column("Age")
    table.add_column("Height (cm)")
    table.add_column("Weight (kg)")

    for p in profiles:
        table.add_row(
            p.user_id,
            p.name,
            str(p.age),
            f"{p.height}",
            f"{p.weight}",
        )

    console.print(table)