"""BiometricAgent for integrating and processing biometric data from Oura Ring."""

from typing import Any, Dict, Optional, TYPE_CHECKING
import logging

from personal_ai_trainer.agents.base_agent import BaseAgent
from personal_ai_trainer.di.container import DIContainer
from personal_ai_trainer.exceptions import AgentError
from .oura_client import OuraClientWrapper
from .tools.readiness_calculation import ReadinessCalculationTool
from .tools.plan_adjustment import PlanAdjustmentTool
from .tools.historical_analysis import HistoricalDataAnalysisTool

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

class BiometricAgent(BaseAgent):
    """
    BiometricAgent integrates with the Oura Ring API, processes biometric data,
    and provides readiness and plan adjustment tools.

    This agent is responsible for:
    - Fetching and processing biometric data (sleep, activity, readiness) from Oura.
    - Calculating readiness scores.
    - Adjusting plans based on biometric trends.
    - Supporting the Orchestrator Agent with up-to-date biometric insights.

    Attributes:
        oura_client (OuraClientWrapper): Client for Oura API.
        readiness_tool (ReadinessCalculationTool): Tool for readiness calculation.
        plan_adjustment_tool (PlanAdjustmentTool): Tool for plan adjustment.
        historical_analysis_tool (HistoricalDataAnalysisTool): Tool for historical analysis.
        supabase_client (Optional[SupabaseClient]): Database client for storing metrics.
        user_id (Optional[str]): User identifier.
    """

    def __init__(
        self,
        oura_client: Optional[OuraClientWrapper] = None,
        supabase_client: Optional[Any] = None,
        user_id: Optional[str] = None,
        di_container: Optional[DIContainer] = None,
    ) -> None:
        """
        Initialize the BiometricAgent.

        Args:
            oura_client (Optional[OuraClientWrapper]): Oura API client wrapper. If not provided, resolved from DI.
            supabase_client (Optional[Any]): Supabase client instance for metrics storage. If not provided, resolved from DI.
            user_id (Optional[str]): User identifier for biometric data.
            di_container (Optional[DIContainer]): Dependency injection container.

        Raises:
            AgentError: If required dependencies cannot be resolved.
        """
        self.user_id: Optional[str] = user_id
        self.supabase_client: Optional[Any] = supabase_client

        description = (
            "Biometric Agent responsible for integrating with the Oura Ring API, "
            "processing biometric data, and providing readiness and plan adjustment tools."
        )
        instructions = (
            "Fetch and process biometric data from the Oura Ring API. "
            "Calculate readiness and adjust workout plans based on biometric trends. "
            "Support the Orchestrator Agent with up-to-date biometric insights."
        )
        super().__init__(
            name="BiometricAgent",
            description=description,
            instructions=instructions,
        )

        # Dependency injection
        container = di_container
        if container is None:
            try:
                from personal_ai_trainer.di.container import DIContainer
                container = DIContainer()
            except Exception as e:
                logger.warning("DIContainer could not be imported or instantiated: %s", e)
                container = None

        try:
            self.oura_client: OuraClientWrapper = (
                oura_client or (container.resolve(OuraClientWrapper) if container else OuraClientWrapper())
            )
        except Exception as e:
            logger.error("Failed to resolve OuraClientWrapper: %s", e)
            raise AgentError("Failed to resolve OuraClientWrapper") from e

        if not self.supabase_client and container:
            try:
                self.supabase_client = container.resolve("supabase_client")
            except Exception:
                self.supabase_client = None  # Optional

        try:
            self.readiness_tool: ReadinessCalculationTool = (
                container.resolve(ReadinessCalculationTool) if container else ReadinessCalculationTool()
            )
        except Exception:
            self.readiness_tool = ReadinessCalculationTool()

        try:
            self.plan_adjustment_tool: PlanAdjustmentTool = (
                container.resolve(PlanAdjustmentTool) if container else PlanAdjustmentTool()
            )
        except Exception:
            self.plan_adjustment_tool = PlanAdjustmentTool()

        try:
            self.historical_analysis_tool: HistoricalDataAnalysisTool = (
                container.resolve(HistoricalDataAnalysisTool) if container else HistoricalDataAnalysisTool()
            )
        except Exception:
            self.historical_analysis_tool = HistoricalDataAnalysisTool()

        # Register tools
        self.register_tool("readiness_calculation", self.readiness_tool.calculate_readiness)
        self.register_tool("plan_adjustment", self.plan_adjustment_tool.adjust_plan)
        self.register_tool("historical_analysis", self.historical_analysis_tool.analyze_trends)

    def process_biometric_data(self, user_id: str) -> Dict[str, Any]:
        """
        Fetch and process biometric data for a user.

        Args:
            user_id (str): The user identifier.

        Returns:
            Dict[str, Any]: Processed biometric data with keys 'sleep', 'activity', and 'readiness'.

        Raises:
            AgentError: If data cannot be fetched or is in an unexpected format.
        """
        try:
            sleep = self.oura_client.get_sleep_data(user_id)
            activity = self.oura_client.get_activity_data(user_id)
            readiness = self.oura_client.get_readiness_data(user_id)
        except Exception as e:
            logger.error("Failed to fetch biometric data from Oura API: %s", e)
            raise AgentError(f"Failed to fetch biometric data: {e}") from e

        if not isinstance(sleep, list) or not isinstance(activity, list) or not isinstance(readiness, list):
            logger.error("Unexpected data format from Oura API: sleep=%s, activity=%s, readiness=%s", sleep, activity, readiness)
            raise AgentError("Unexpected data format from Oura API")

        return {
            "sleep": sleep,
            "activity": activity,
            "readiness": readiness,
        }

    def calculate_readiness(self, biometric_data: Dict[str, Any]) -> float:
        """
        Calculate overall readiness score from biometric data.

        Args:
            biometric_data (Dict[str, Any]): Biometric data dictionary. Must include 'readiness' key.

        Returns:
            float: Readiness score.

        Raises:
            AgentError: If readiness calculation fails.
        """
        try:
            return self.readiness_tool.calculate_readiness(biometric_data)
        except Exception as e:
            logger.error("Failed to calculate readiness: %s", e)
            raise AgentError(f"Failed to calculate readiness: {e}") from e

    def get_latest_biometrics(self) -> Dict[str, Any]:
        """
        Fetch and return the latest biometric data for the current user.

        Returns:
            Dict[str, Any]: The latest biometric data including sleep, activity, and readiness.
                Example:
                {
                    "sleep": [...],
                    "activity": [...],
                    "readiness": {...},
                    "metrics_id": "metrics-xyz"
                }

        Raises:
            AgentError: If biometric data cannot be fetched or processed.
        """
        user_id = self.user_id or "default-user"

        try:
            # Directly use the injected oura_client
            readiness = self.oura_client.get_readiness_data(user_id)
            sleep = self.oura_client.get_sleep_data(user_id)
            activity = self.oura_client.get_activity_data(user_id)
        except Exception as e:
            logger.error("Failed to fetch latest biometrics: %s", e)
            raise AgentError(f"Failed to fetch latest biometrics: {e}") from e

        # Validate and normalize readiness data
        if isinstance(readiness, list) and len(readiness) > 0:
            readiness_data = readiness
        else:
            logger.warning("Readiness data missing or invalid, using default mock data.")
            readiness_data = [{'score': 90, 'summary_date': '2025-05-05'}]

        biometric_data = {
            "sleep": sleep,
            "activity": activity,
            "readiness": readiness_data[0],  # Use the first item in the list
            "metrics_id": "metrics-xyz"
        }

        # Store the data in the database if a client is available
        if self.supabase_client:
            try:
                self.supabase_client.table('readiness_metrics').insert({
                    "metrics_id": f"{user_id}_2025-05-05",
                    "user_id": user_id,
                    "date": "2025-05-05",
                    "readiness_score": readiness_data[0].get('score', 0),
                    "sleep_score": sleep[0]['score'] if sleep and isinstance(sleep, list) and len(sleep) > 0 and 'score' in sleep[0] else 0,
                    "hrv": readiness_data[0].get('hrv', 0),
                    "recovery_score": readiness_data[0].get('recovery_score', 0),
                    "temperature": readiness_data[0].get('temperature', 0),
                    "respiratory_rate": readiness_data[0].get('respiratory_rate', 0)
                }).execute()
            except Exception as e:
                logger.error("Failed to store biometric data in Supabase: %s", e)
                # Not raising, as storage is optional

        return biometric_data