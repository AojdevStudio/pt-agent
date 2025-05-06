# personal_ai_trainer/tests/conftest.py
import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

# Import Real Agent classes
from personal_ai_trainer.agents.research_agent.agent import ResearchAgent
from personal_ai_trainer.agents.biometric_agent.agent import BiometricAgent
from personal_ai_trainer.agents.orchestrator_agent.agent import OrchestratorAgent
from personal_ai_trainer.agents.biometric_agent.oura_client import OuraClientWrapper
# Import the class whose method we need to patch
# Import database models needed within fixtures

# Constants
TEST_USER_ID = "test-user-123"
TEST_USER_NAME = "Test User"
TEST_USER_EMAIL = "test@example.com"

# --- Mock External Clients ---
@pytest.fixture
def mock_supabase_client():
    """Provides a VERY basic mocked Supabase client. Specific behaviors must be mocked in tests."""
    mock_client = MagicMock(name="SupabaseClientMock")

    # Configure a generic successful response object for execute()
    mock_execute_response = MagicMock(name="ExecuteResponseMock")
    mock_execute_response.data = [{'id': 'generic-mock-id'}] # Default data
    mock_execute_response.count = 1
    mock_execute_response.error = None

    # --- Generic Mocks for common chains ---
    # Mock the final execute() call for common chains
    mock_client.table.return_value.select.return_value.execute.return_value = mock_execute_response
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_execute_response
    mock_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_execute_response
    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_execute_response
    mock_client.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_execute_response

    # Mock the insert() method to return an object that has a mock execute() method
    mock_insert_builder = MagicMock(name="InsertBuilderMock")
    mock_insert_builder.execute.return_value = mock_execute_response
    mock_client.table.return_value.insert.return_value = mock_insert_builder

    return mock_client

@pytest.fixture
def mock_openai_client():
    """Provides a mocked OpenAI client."""
    mock_client = MagicMock(name="OpenAIClientMock")
    # Configure default mock responses
    mock_completion = MagicMock(name="CompletionMock")
    mock_message = MagicMock(name="MessageMock")
    mock_message.content = '{"plan": "Default Mocked AI Plan"}'
    mock_choice = MagicMock(name="ChoiceMock")
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client

@pytest.fixture
def mock_oura_wrapper_instance():
    """Provides a mocked OuraClientWrapper instance."""
    mock_instance = MagicMock(spec=OuraClientWrapper, name="OuraWrapperInstanceMock")
    # Configure default mock responses
    mock_instance.get_sleep_data.return_value = [{'score': 85, 'summary_date': '2025-05-05'}]
    mock_instance.get_readiness_data.return_value = [{'score': 90, 'summary_date': '2025-05-05'}]
    mock_instance.get_activity_data.return_value = [{'score': 75, 'summary_date': '2025-05-05'}]
    return mock_instance

@pytest.fixture
def mock_get_embedding():
    """Provides a mocked get_embedding function."""
    with patch('personal_ai_trainer.knowledge_base.embeddings.get_embedding') as mock_func:
        mock_func.return_value = [0.1] * 1536 # Default embedding
        yield mock_func

# --- Mock DI Container Setup ---
@pytest.fixture(autouse=True)
def mock_di_setup(mock_supabase_client, mock_openai_client, mock_oura_wrapper_instance):
    """
    Mocks the dependency creation functions used by the DI provider.
    This ensures that any attempt to get these clients uses the mocks.
    """
    # Use the mock_supabase_client fixture which now includes the execute patch
    with patch('personal_ai_trainer.di.provider.get_supabase_client', return_value=mock_supabase_client), \
         patch('personal_ai_trainer.di.provider.get_openai_client', return_value=mock_openai_client), \
         patch('personal_ai_trainer.agents.biometric_agent.oura_client.OuraClientWrapper', return_value=mock_oura_wrapper_instance):
        yield # Allow tests to run with these patches active

# --- Fixtures providing REAL Agent instances with MOCKED clients ---
@pytest.fixture
def research_agent(mock_supabase_client): # Depends on mocked client
    """Provides a REAL ResearchAgent instance with a mocked Supabase client."""
    agent = ResearchAgent(supabase_client=mock_supabase_client)
    return agent

@pytest.fixture
def biometric_agent(mock_supabase_client, mock_oura_wrapper_instance, test_user_id): # Depends on mocked clients
    """Provides a REAL BiometricAgent instance with mocked clients."""
    agent = BiometricAgent(
        supabase_client=mock_supabase_client,
        oura_client=mock_oura_wrapper_instance, # Pass the mocked instance
        user_id=test_user_id
    )
    return agent

@pytest.fixture
def orchestrator_agent(research_agent, biometric_agent, mock_supabase_client, test_user_id): # Depends on other agent fixtures
    """Provides a REAL OrchestratorAgent instance with mocked sub-agents and clients."""
    agent = OrchestratorAgent(
        research_agent=research_agent,
        biometric_agent=biometric_agent,
        supabase_client=mock_supabase_client,
        user_id=test_user_id
    )
    return agent

# Fixture for CLI Runner
@pytest.fixture
def runner():
    """Provides a Typer CliRunner instance."""
    return CliRunner()

# Fixture for Test User ID
@pytest.fixture
def test_user_id():
    return TEST_USER_ID

# Fixture providing the original Oura mock (less commonly needed now)
@pytest.fixture
def mock_oura_client():
    """Provides the original mocked Oura client (less commonly needed)."""
    mock_client = MagicMock(name="OriginalOuraClientMock")
    mock_client.get_sleep_data.return_value = [{'score': 85, 'summary_date': '2025-05-05'}]
    mock_client.get_readiness_data.return_value = [{'score': 90, 'summary_date': '2025-05-05'}]
    mock_client.get_activity_data.return_value = [{'score': 75, 'summary_date': '2025-05-05'}]
    return mock_client