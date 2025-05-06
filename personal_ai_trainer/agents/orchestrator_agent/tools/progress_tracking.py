"""Tool for tracking workout progress and implementing gamification."""

from typing import Any, Dict, List
from agency_swarm.tools import BaseTool
from pydantic import Field
import datetime

# Placeholder for database interaction to store progress, badges, etc.
# from personal_ai_trainer.database.models import UserProgress, Badge
# from personal_ai_trainer.database.operations import log_workout, award_badge, get_user_progress

# --- Gamification Rules ---
POINTS_PER_WORKOUT = 10
POINTS_PER_PR = 50 # Personal Record

# Badge criteria (example)
BADGE_CRITERIA = {
    "first_workout": {"description": "Completed your first workout!", "condition": lambda progress: progress["total_workouts"] == 1},
    "consistency_1_week": {"description": "Completed workouts for 1 week straight!", "condition": lambda progress: progress["consecutive_weeks"] >= 1},
    "consistency_1_month": {"description": "Completed workouts for 1 month straight!", "condition": lambda progress: progress["consecutive_months"] >= 1},
    "first_pr": {"description": "Achieved your first Personal Record!", "condition": lambda progress: progress["total_prs"] >= 1},
    "strength_milestone_1": {"description": "Reached Strength Milestone 1!", "condition": lambda progress: progress["points"] >= 500},
}

class ProgressTrackingTool(BaseTool):
    """
    Tracks user workout completion, calculates points, awards badges based on achievements,
    and provides progress summaries. Interacts with the database to store and retrieve progress data.
    """
    user_id: str = Field(
        ...,
        description="The unique identifier for the user."
    )
    workout_log: Dict[str, Any] = Field(
        ...,
        description="Details of the completed workout. Should include date, exercises performed, sets, reps, weight used, and potentially RPE (Rate of Perceived Exertion)."
        # Example: {"date": "2025-05-05", "workout_type": "push", "exercises": [{"name": "Bench Press", "sets": [{"reps": 8, "weight": 90}, ...]}, ...], "duration_minutes": 60, "rpe": 8}
    )

    def _get_user_progress(self) -> Dict[str, Any]:
        """
        Retrieves the user's current progress data from the database.
        Placeholder: In a real system, this would query a database.
        """
        # Mock progress data
        mock_progress = {
            "user_id": self.user_id,
            "total_workouts": 5,
            "total_points": 50,
            "badges_earned": ["first_workout"],
            "last_workout_date": "2025-05-01",
            "consecutive_weeks": 1,
            "consecutive_months": 0,
            "total_prs": 0,
            # Add more fields as needed (e.g., weekly summaries)
        }
        print(f"Retrieved mock progress for user {self.user_id}: {mock_progress}")
        return mock_progress

    def _update_user_progress(self, progress_data: Dict[str, Any], points_earned: int, new_badges: List[str], is_pr: bool):
        """
        Updates the user's progress data in the database.
        Placeholder: In a real system, this would update database records.
        """
        progress_data["total_workouts"] += 1
        progress_data["total_points"] += points_earned
        progress_data["badges_earned"].extend(new_badges)
        progress_data["last_workout_date"] = self.workout_log.get("date", datetime.date.today().isoformat())
        if is_pr:
            progress_data["total_prs"] += 1

        # TODO: Implement logic to update consecutive weeks/months based on dates

        print(f"Updating mock progress for user {self.user_id}: {progress_data}")
        # In a real system: save_user_progress(self.user_id, progress_data)

    def _check_for_pr(self) -> bool:
        """
        Checks if the current workout log contains any personal records (PRs).
        Placeholder: Needs comparison against historical performance data.
        """
        # This requires fetching historical bests for the exercises performed
        # and comparing them to the current log.
        print("Checking for PRs (mock implementation)...")
        # Simulate finding a PR sometimes
        is_pr = any(ex.get("is_pr", False) for ex in self.workout_log.get("exercises", [])) # Check if log explicitly marks a PR
        if not is_pr and self.workout_log.get("rpe", 0) > 8: # Simple heuristic: high RPE might indicate PR attempt
             is_pr = (datetime.datetime.now().second % 5 == 0) # Randomly assign PR sometimes for testing

        if is_pr:
            print("PR detected!")
        return is_pr

    def _check_badge_conditions(self, progress_data: Dict[str, Any]) -> List[str]:
        """Checks if the user meets the criteria for any new badges."""
        newly_earned_badges = []
        current_badges = set(progress_data.get("badges_earned", []))

        for badge_id, criteria in BADGE_CRITERIA.items():
            if badge_id not in current_badges:
                condition_met = criteria["condition"](progress_data)
                if condition_met:
                    newly_earned_badges.append(badge_id)
                    print(f"User {self.user_id} earned badge: {badge_id} - {criteria['description']}")
                    # In a real system: award_badge(self.user_id, badge_id)

        return newly_earned_badges

    def run(self) -> Dict[str, Any]:
        """
        Executes the progress tracking logic: logs workout, calculates points, checks for PRs and badges.

        Returns:
            Dict[str, Any]: A summary of the progress update, including points earned and new badges.
                            Example: {"points_earned": 60, "new_badges": ["first_pr"], "message": "Workout logged successfully!"}
        """
        print(f"Tracking workout for user {self.user_id}: {self.workout_log.get('workout_type', 'Unknown type')} on {self.workout_log.get('date', 'Unknown date')}")

        # 1. Retrieve current progress
        current_progress = self._get_user_progress()

        # 2. Calculate points for this workout
        points_earned = POINTS_PER_WORKOUT
        is_pr = self._check_for_pr()
        if is_pr:
            points_earned += POINTS_PER_PR

        # 3. Check for new badges BEFORE updating totals (to capture 'first_workout', 'first_pr' etc.)
        # We need a temporary updated state to check conditions accurately
        temp_progress_for_badge_check = current_progress.copy()
        temp_progress_for_badge_check["total_workouts"] += 1
        temp_progress_for_badge_check["total_points"] += points_earned
        if is_pr:
             temp_progress_for_badge_check["total_prs"] += 1
        # TODO: Update consecutive counters in temp_progress_for_badge_check

        new_badges = self._check_badge_conditions(temp_progress_for_badge_check)

        # 4. Update progress in the database (placeholder)
        self._update_user_progress(current_progress, points_earned, new_badges, is_pr)

        # 5. Log the workout details (placeholder)
        # In a real system: log_workout(self.user_id, self.workout_log)
        print(f"Workout logged successfully for user {self.user_id}.")

        return {
            "points_earned": points_earned,
            "new_badges": new_badges,
            "is_pr": is_pr,
            "message": "Workout logged successfully!"
        }

# Example Usage (for testing purposes)
if __name__ == "__main__":
    test_log = {
        "date": datetime.date.today().isoformat(),
        "workout_type": "push",
        "exercises": [
            {"name": "Bench Press", "sets": [{"reps": 5, "weight": 105}], "is_pr": True}, # Marked as PR
            {"name": "Overhead Press", "sets": [{"reps": 8, "weight": 60}]},
        ],
        "duration_minutes": 55,
        "rpe": 9
    }

    tool = ProgressTrackingTool(
        user_id="test_user_badge_check",
        workout_log=test_log
    )
    progress_update = tool.run()
    import json
    print("\nProgress Update Summary:")
    print(json.dumps(progress_update, indent=2))

    # Simulate first workout
    first_workout_log = {
        "date": datetime.date.today().isoformat(),
        "workout_type": "legs",
        "exercises": [{"name": "Squats", "sets": [{"reps": 10, "weight": 50}]}],
        "duration_minutes": 45,
        "rpe": 7
    }
    # Need a way to reset mock progress for this user or use a different user ID
    # For now, assume a fresh user by implication or modify _get_user_progress for testing
    print("\nSimulating first workout (requires fresh mock progress state):")
    # tool_first = ProgressTrackingTool(user_id="new_user_test", workout_log=first_workout_log)
    # progress_first = tool_first.run()
    # print(json.dumps(progress_first, indent=2))