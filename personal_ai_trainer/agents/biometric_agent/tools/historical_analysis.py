"""Tool for analyzing trends in historical biometric data."""

from typing import List, Dict, Any

class HistoricalDataAnalysisTool:
    """
    Tool for analyzing trends in historical biometric data.
    """

    def analyze_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trends in a list of historical biometric data entries.

        Args:
            historical_data (List[Dict[str, Any]]): List of biometric data dictionaries (ordered by date).

        Returns:
            Dict[str, Any]: Summary of detected trends (e.g., average, min, max, trend direction).
        """
        if not historical_data:
            return {"message": "No historical data provided."}

        # Example: analyze readiness scores
        readiness_scores = [
            entry.get("readiness", {}).get("score")
            for entry in historical_data
            if entry.get("readiness", {}).get("score") is not None
        ]
        if not readiness_scores:
            return {"message": "No readiness scores found in historical data."}

        avg_score = sum(readiness_scores) / len(readiness_scores)
        min_score = min(readiness_scores)
        max_score = max(readiness_scores)
        trend = "increasing" if readiness_scores[-1] > readiness_scores[0] else "decreasing" if readiness_scores[-1] < readiness_scores[0] else "stable"

        return {
            "average_readiness": avg_score,
            "min_readiness": min_score,
            "max_readiness": max_score,
            "trend": trend,
            "history": readiness_scores,
        }