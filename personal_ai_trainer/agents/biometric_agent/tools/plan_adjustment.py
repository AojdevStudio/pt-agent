"""Tool for adjusting workout plans based on readiness score."""

from typing import Dict, Any

class PlanAdjustmentTool:
    """
    Tool for adjusting workout plans based on readiness score and biometric data.
    """

    def adjust_plan(self, readiness_score: float, workout_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjust the workout plan based on the user's readiness score.

        Args:
            readiness_score (float): The user's readiness score (0-100).
            workout_plan (Dict[str, Any]): The original workout plan.

        Returns:
            Dict[str, Any]: The adjusted workout plan.
        """
        adjusted_plan = workout_plan.copy()
        # Example logic: reduce intensity if readiness is low, increase if high
        if readiness_score < 60:
            adjusted_plan["intensity"] = "low"
            adjusted_plan["notes"] = "Reduced intensity due to low readiness."
        elif readiness_score > 85:
            adjusted_plan["intensity"] = "high"
            adjusted_plan["notes"] = "Increased intensity due to high readiness."
        else:
            adjusted_plan["intensity"] = "moderate"
            adjusted_plan["notes"] = "Standard intensity based on readiness."
        return adjusted_plan