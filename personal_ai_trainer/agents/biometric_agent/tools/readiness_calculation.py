"""Tool for calculating overall readiness based on biometric data."""

from typing import Dict, Any

class ReadinessCalculationTool:
    """
    Tool for calculating an overall readiness score from biometric data.
    """

    def calculate_readiness(self, biometric_data: Dict[str, Any]) -> float:
        """
        Calculate a readiness score based on biometric data.

        Args:
            biometric_data (Dict[str, Any]): Dictionary containing biometric data (sleep, activity, readiness).

        Returns:
            float: Calculated readiness score (0-100).
        """
        readiness = biometric_data.get("readiness", {})
        # Use Oura's readiness score if available, else compute a simple average
        score = readiness.get("score")
        if score is not None:
            return float(score)
        # Fallback: average sleep and activity scores if present
        sleep_score = biometric_data.get("sleep", {}).get("score")
        activity_score = biometric_data.get("activity", {}).get("score")
        scores = [s for s in [sleep_score, activity_score] if s is not None]
        if scores:
            return float(sum(scores)) / len(scores)
        return 0.0