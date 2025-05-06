"""Tool for generating personalized PPL workout plans."""

from typing import Any, Dict, List, ClassVar # Added ClassVar
from agency_swarm.tools import BaseTool
from pydantic import Field

# Placeholder for potential database models or utility functions if needed later
# from personal_ai_trainer.database.models import User, Exercise
# from personal_ai_trainer.utils.exercise_database import fetch_exercises

class WorkoutGenerationTool(BaseTool):
    """
    Generates a personalized 4-week Push-Pull-Legs (PPL) workout plan
    based on user preferences, goals, experience level, and research insights.
    """
    user_preferences: Dict[str, Any] = Field(
        ...,
        description="User's profile including goals (e.g., hypertrophy, strength), experience level (beginner, intermediate, advanced), available equipment, time commitment."
    )
    research_insights: Dict[str, Any] = Field(
        ...,
        description="Synthesized research findings relevant to the user's goals and profile, provided by the Research Agent. Includes exercise recommendations, optimal frequency, volume, etc."
    )
    current_week: int = Field(
        default=1,
        description="The current week number in the 4-week cycle (1-4). Used for progressive overload adjustments."
    )

    # --- PPL Template Structure ---
    # This is a simplified example. A real implementation would be more dynamic,
    # potentially pulling exercises from a database based on research_insights and user_preferences.
    PPL_TEMPLATE: ClassVar[Dict[str, Dict[str, List[str]]]] = { # Added ClassVar annotation
        "beginner": {
            "push": ["Bench Press (Barbell/Dumbbell)", "Overhead Press (Barbell/Dumbbell)", "Incline Dumbbell Press", "Lateral Raises", "Triceps Pushdowns"],
            "pull": ["Pull-ups/Lat Pulldowns", "Barbell Rows/Dumbbell Rows", "Face Pulls", "Bicep Curls"],
            "legs": ["Barbell Squats", "Romanian Deadlifts", "Leg Press", "Leg Curls", "Calf Raises"]
        },
        "intermediate": {
            "push": ["Barbell Bench Press", "Overhead Press", "Incline Dumbbell Press", "Lateral Raises", "Triceps Pushdowns", "Chest Flyes"],
            "pull": ["Weighted Pull-ups/Lat Pulldowns", "Barbell Rows", "T-Bar Rows", "Face Pulls", "Hammer Curls", "Bicep Curls"],
            "legs": ["Barbell Squats", "Deadlifts (Conventional/Sumo - 1x/week)", "Leg Press", "Hamstring Curls", "Quad Extensions", "Calf Raises"]
        },
        "advanced": {
            # Advanced template would likely involve more exercise variation, specific periodization, etc.
            "push": ["Barbell Bench Press", "Incline Barbell Press", "Seated Dumbbell Press", "Lateral Raises", "Overhead Triceps Extensions", "Dips"],
            "pull": ["Weighted Pull-ups", "Pendlay Rows", "Single-Arm Dumbbell Rows", "Rear Delt Flyes", "Preacher Curls", "Concentration Curls"],
            "legs": ["Barbell Squats (High/Low Bar)", "Deadlifts (Heavy)", "Front Squats", "Glute Ham Raises", "Leg Extensions", "Seated Calf Raises"]
        }
    }

    # --- Progression Logic (Simplified) ---
    # A real system would have more sophisticated progression based on performance, RPE, etc.
    PROGRESSION: ClassVar[Dict[int, Dict[str, Any]]] = { # Added ClassVar annotation
        1: {"sets": 3, "reps": "8-12", "intensity_modifier": 0.95}, # Base week
        2: {"sets": 3, "reps": "8-12", "intensity_modifier": 1.0},  # Increase intensity slightly
        3: {"sets": 4, "reps": "6-10", "intensity_modifier": 1.02}, # Increase volume and intensity
        4: {"sets": 3, "reps": "10-15", "intensity_modifier": 0.9}, # Deload week
    }

    def _get_template_for_level(self, level: str) -> Dict[str, List[str]]:
        """Selects the appropriate PPL template based on experience level."""
        level = level.lower()
        if level in self.PPL_TEMPLATE:
            return self.PPL_TEMPLATE[level]
        else:
            print(f"Warning: Unknown experience level '{level}'. Defaulting to intermediate.")
            return self.PPL_TEMPLATE["intermediate"] # Default to intermediate

    def _apply_progression(self, week_plan: Dict[str, List[str]], week_num: int) -> Dict[str, List[Dict[str, Any]]]:
        """Applies sets, reps, and intensity modifiers based on the week number."""
        if week_num not in self.PROGRESSION:
            print(f"Warning: Invalid week number {week_num}. Using week 1 progression.")
            week_num = 1

        prog_params = self.PROGRESSION[week_num]
        progressed_plan = {}
        for day_type, exercises in week_plan.items():
            progressed_plan[day_type] = []
            for exercise in exercises:
                progressed_plan[day_type].append({
                    "exercise": exercise,
                    "sets": prog_params["sets"],
                    "reps": prog_params["reps"],
                    "intensity_modifier": prog_params["intensity_modifier"],
                    # Load calculation will happen in a separate tool
                    "calculated_load": None
                })
        return progressed_plan


    def run(self) -> Dict[str, Any]:
        """
        Executes the workout plan generation logic.

        Returns:
            Dict[str, Any]: The generated 4-week PPL workout plan structure.
                            Example: {"week_1": {"push": [{"exercise": "Bench Press", "sets": 3, ...}], ...}, ...}
        """
        print(f"Generating PPL plan for preferences: {self.user_preferences}")
        print(f"Using research insights: {self.research_insights}") # Log insights used

        experience_level = self.user_preferences.get("experience", "intermediate")
        base_template = self._get_template_for_level(experience_level)

        # TODO: Incorporate research_insights to potentially modify the base_template
        # e.g., swap exercises based on recommendations or equipment availability

        full_plan = {}
        for week in range(1, 5):
             # Apply progression for the specific week
            weekly_progressed_plan = self._apply_progression(base_template, week)
            full_plan[f"week_{week}"] = weekly_progressed_plan

        print(f"Generated 4-week plan structure.")
        return full_plan

# Example Usage (for testing purposes)
if __name__ == "__main__":
    tool = WorkoutGenerationTool(
        user_preferences={"experience": "intermediate", "goal": "hypertrophy"},
        research_insights={"summary": "Focus on compound lifts, 8-12 rep range.", "recommendations": []}
    )
    plan = tool.run()
    import json
    print(json.dumps(plan, indent=2))

    tool_beginner = WorkoutGenerationTool(
        user_preferences={"experience": "beginner", "goal": "strength"},
        research_insights={"summary": "Start with basics, focus on form.", "recommendations": []},
        current_week=3 # Test progression
    )
    plan_beginner_w3 = tool_beginner.run()
    # We only care about week 3 structure here for testing progression logic directly
    print("\nBeginner Plan (Week 3 Progression Applied):")
    print(json.dumps(plan_beginner_w3["week_3"], indent=2))