from unittest.mock import patch, MagicMock
import datetime

# --- Updated Imports ---
from personal_ai_trainer.database.models import (
    ReadinessMetrics as DBReadinessMetrics,
    KnowledgeBase as DBKnowledgeBase
)
from personal_ai_trainer.cli.main import app as cli_app
from personal_ai_trainer.utils.scheduler import Scheduler
from personal_ai_trainer.knowledge_base import repository as kb_repo

# --- Constants ---
TEST_USER_ID = "test-user-123"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_NAME = "Test User"

# Note: Fixtures are now provided by conftest.py

# --- Test Functions (Converted from unittest methods) ---

def test_01_database_interaction_mocking(mock_supabase_client, test_user_id):
    """Test basic interaction with the mocked Supabase client."""
    # Configure specific mock response for this test
    mock_user_data = {
        "user_id": TEST_USER_ID, "name": TEST_USER_NAME, "email": TEST_USER_EMAIL,
        "age": 30, "height": 180, "weight": 75
    }
    mock_user_response = MagicMock(name="UserResponseMock_test01")
    mock_user_response.data = [mock_user_data]
    mock_user_response.count = 1
    mock_user_response.error = None
    mock_supabase_client.table('user_profiles').select.return_value.eq.return_value.execute.return_value = mock_user_response

    # 1. Verify user profile fetch mock
    response = mock_supabase_client.table('user_profiles').select('*').eq('user_id', test_user_id).execute()
    mock_supabase_client.table.assert_called_with('user_profiles')
    mock_supabase_client.table('user_profiles').select.assert_called_with('*')
    mock_supabase_client.table('user_profiles').select('*').eq.assert_called_with('user_id', test_user_id)
    mock_supabase_client.table('user_profiles').select('*').eq().execute.assert_called()
    assert len(response.data) == 1
    assert response.data[0]['name'] == TEST_USER_NAME

    # 2. Test inserting a new record
    test_date = datetime.date(2025, 5, 6)
    metrics_data = DBReadinessMetrics(
        metrics_id="metrics-1", user_id=test_user_id, date=test_date,
        readiness_score=88.0, hrv=55.0
    )
    # Configure insert mock response for this specific call
    mock_generic_response = MagicMock(name="GenericExecuteResponseMock_test01_insert")
    mock_generic_response.data = [{'id': 'new-mock-id-test01'}]
    mock_generic_response.count = 1
    mock_generic_response.error = None
    mock_supabase_client.table('readiness_metrics').insert.return_value.execute.return_value = mock_generic_response

    insert_response = mock_supabase_client.table('readiness_metrics').insert(metrics_data.model_dump(exclude_unset=True)).execute()
    mock_supabase_client.table.assert_called_with('readiness_metrics')
    mock_supabase_client.table('readiness_metrics').insert.assert_called_with(metrics_data.model_dump(exclude_unset=True))
    mock_supabase_client.table('readiness_metrics').insert().execute.assert_called()
    assert insert_response.data[0]['id'] == 'new-mock-id-test01'

@patch('personal_ai_trainer.knowledge_base.repository.get_supabase_client')
def test_02_knowledge_base_integration(mock_kb_get_supabase, mock_supabase_client, mock_get_embedding):
    """Test adding documents and searching the knowledge base via repository functions."""
    mock_kb_get_supabase.return_value = mock_supabase_client
    mock_supabase_client.reset_mock()
    mock_get_embedding.reset_mock()

    # 1. Test adding a document
    doc_content = "Research about optimal running cadence."
    doc_source = "Test Journal"
    doc_id = "doc-123"
    mock_embedding_val = [0.1] * 1536
    mock_get_embedding.return_value = mock_embedding_val
    new_doc = DBKnowledgeBase(
        document_id=doc_id, title="Running Cadence", content=doc_content,
        source=doc_source, embedding=mock_embedding_val, date_added=datetime.date.today()
    )
    mock_insert_response = MagicMock(name="InsertResponseMock_test02")
    mock_insert_response.data = [{"document_id": doc_id}]
    mock_insert_response.error = None
    mock_supabase_client.table(kb_repo.TABLE_NAME).insert.return_value.execute.return_value = mock_insert_response

    returned_id = kb_repo.add_document(new_doc)
    mock_supabase_client.table.assert_called_with(kb_repo.TABLE_NAME)
    # Use model_dump(mode='json') to match repository code
    mock_supabase_client.table(kb_repo.TABLE_NAME).insert.assert_called_with(new_doc.model_dump(mode='json'))
    mock_supabase_client.table(kb_repo.TABLE_NAME).insert().execute.assert_called_once()
    assert returned_id == doc_id

    # 2. Test searching for similar documents
    query_embedding = [0.11] * 1536
    mock_get_embedding.return_value = query_embedding
    mock_search_response = MagicMock(name="SearchResponseMock_test02")
    mock_search_response.data = [new_doc.model_dump()]
    mock_search_response.error = None
    mock_supabase_client.table(kb_repo.TABLE_NAME).select.return_value.execute.return_value = mock_search_response

    results = kb_repo.query_similar_documents(query_embedding=query_embedding, top_k=1)
    mock_supabase_client.table.assert_called_with(kb_repo.TABLE_NAME)
    mock_supabase_client.table(kb_repo.TABLE_NAME).select.assert_called_with("*")
    assert mock_supabase_client.table(kb_repo.TABLE_NAME).select().execute.call_count == 1
    assert len(results) == 1
    assert results[0].document_id == doc_id

@patch('personal_ai_trainer.agents.openai_integration.get_openai_client')
@patch('personal_ai_trainer.knowledge_base.repository.add_document') # Patch add_document directly
@patch('personal_ai_trainer.knowledge_base.repository.get_supabase_client') # Patch select call
def test_03_research_agent_integration(mock_kb_get_supabase, mock_add_doc, mock_agent_get_openai, research_agent, mock_supabase_client, mock_openai_client, mock_get_embedding):
    """Test Research Agent processing document and querying KB."""
    mock_kb_get_supabase.return_value = mock_supabase_client
    mock_agent_get_openai.return_value = mock_openai_client
    mock_supabase_client.reset_mock()
    mock_openai_client.reset_mock()
    mock_get_embedding.reset_mock()

    # 1. Test processing a research document
    doc_content = "Study on strength training frequency."
    doc_source = "Strength Journal"
    doc_title = "Strength Frequency Study"
    doc_id = "doc-456"
    mock_embedding_val = [0.2] * 1536
    mock_get_embedding.return_value = mock_embedding_val
    mock_process_response = MagicMock(choices=[MagicMock(message=MagicMock(content='{"summary": "Strength training 2-3 times/week is optimal."}'))])
    mock_openai_client.chat.completions.create.return_value = mock_process_response
    mock_add_doc.return_value = doc_id # Configure patched add_document

    summary = research_agent.process_research_document(doc_content, doc_source, doc_title)
    mock_openai_client.chat.completions.create.assert_called()
    mock_add_doc.assert_called_once() # Verify patched function was called
    call_args = mock_add_doc.call_args[0][0]
    assert isinstance(call_args, DBKnowledgeBase)
    assert call_args.content == doc_content
    assert "optimal" in summary

    # 2. Test querying the knowledge base
    query_text = "how often strength train?"
    query_embedding = [0.21] * 1536
    mock_get_embedding.return_value = query_embedding
    mock_search_response = MagicMock(name="SearchResponseMock_test03")
    mock_search_response.data = [DBKnowledgeBase(document_id=doc_id, title=doc_title, content=doc_content, source=doc_source, embedding=mock_embedding_val).model_dump()]
    mock_search_response.error = None
    mock_supabase_client.table(kb_repo.TABLE_NAME).select.return_value.execute.return_value = mock_search_response
    mock_query_response = MagicMock(choices=[MagicMock(message=MagicMock(content='{"answer": "Based on KB: Strength training 2-3 times/week is optimal."}'))])
    mock_openai_client.chat.completions.create.reset_mock()
    mock_openai_client.chat.completions.create.return_value = mock_query_response

    answer = research_agent.query_knowledge_base(query_text)
    mock_supabase_client.table(kb_repo.TABLE_NAME).select.assert_called_with("*")
    assert mock_supabase_client.table(kb_repo.TABLE_NAME).select().execute.call_count == 1
    mock_openai_client.chat.completions.create.assert_called_once()
    assert "2-3 times/week" in answer

# Patch the insert().execute() call directly within the test
def test_04_biometric_agent_integration(biometric_agent, mock_supabase_client, mock_oura_wrapper_instance, mock_openai_client, test_user_id):
    """Test Biometric Agent fetching (mocked) data, storing, and calculations."""
    mock_supabase_client.reset_mock()
    mock_oura_wrapper_instance.reset_mock()
    mock_openai_client.reset_mock()

    # 1. Test fetching latest biometrics
    readiness_table = 'readiness_metrics'
    # Mock the insert call specifically for this test
    mock_insert_response = MagicMock(name="InsertResponseMock_test04")
    mock_insert_response.data = [{"metrics_id": "metrics-xyz"}]
    mock_insert_response.error = None
    # Patch the execute method on the object returned by insert()
    with patch.object(mock_supabase_client.table(readiness_table).insert.return_value, 'execute', return_value=mock_insert_response) as mock_execute:

        biometric_summary = biometric_agent.get_latest_biometrics()

        biometric_agent.oura_client.get_readiness_data.assert_called_once()
        biometric_agent.oura_client.get_sleep_data.assert_called_once()
        biometric_agent.oura_client.get_activity_data.assert_called_once()
        assert 'readiness' in biometric_summary and biometric_summary['readiness']['score'] == 90

        # Verify insert call chain
        mock_supabase_client.table.assert_called_with(readiness_table)
        mock_supabase_client.table(readiness_table).insert.assert_called_once()
        insert_call_args = mock_supabase_client.table(readiness_table).insert.call_args[0][0]
        assert insert_call_args['user_id'] == test_user_id
        assert insert_call_args['readiness_score'] == 90
        assert insert_call_args['date'] == '2025-05-05'
        mock_execute.assert_called_once() # Verify execute was called on the insert builder

    # 2. Test readiness calculation
    mock_data = {'user_id': test_user_id, 'readiness_score': 90, 'sleep_score': 85, 'date': datetime.date(2025, 5, 5)}
    mock_select_response = MagicMock(data=[mock_data])
    mock_select_response.error = None
    mock_supabase_client.table(readiness_table).select.return_value.order.return_value.limit.return_value.execute.return_value = mock_select_response
    mock_advice_response = MagicMock(choices=[MagicMock(message=MagicMock(content='{"readiness_level": "Optimal", "advice": "Go for it!"}'))])
    mock_openai_client.chat.completions.create.reset_mock()
    mock_openai_client.chat.completions.create.return_value = mock_advice_response

    readiness_advice = biometric_agent.calculate_readiness(biometric_data=mock_data)
    mock_openai_client.chat.completions.create.assert_called_once()
    assert isinstance(readiness_advice, dict)
    assert readiness_advice['readiness_level'] == "Optimal"

# Patch get_openai_client where the agent/tools likely import it
# Patch the insert call directly within the test
@patch('personal_ai_trainer.agents.openai_integration.get_openai_client')
def test_05_orchestrator_agent_integration(mock_agent_get_openai, orchestrator_agent, mock_supabase_client, mock_openai_client, research_agent, biometric_agent):
    """Test Orchestrator Agent generating and storing a workout plan."""
    mock_agent_get_openai.return_value = mock_openai_client
    mock_supabase_client.reset_mock()
    mock_openai_client.reset_mock()

    goal = "Improve 5k time"
    plan_table = 'workout_plans'
    plan_id = "plan-abc"

    # Mock the internal helper methods using patch.object
    with patch.object(orchestrator_agent, '_get_research_insights', return_value={"summary": "Mock research summary"}) as mock_get_research, \
         patch.object(orchestrator_agent, '_get_biometric_readiness', return_value={"readiness_score": 90}) as mock_get_readiness:

        # Mock the direct OpenAI call within generate_workout_plan
        mock_plan_content = {"plan": [{"day": "Mon", "activity": "Run"}]}
        mock_plan_response = MagicMock(choices=[MagicMock(message=MagicMock(content=str(mock_plan_content)))])
        mock_openai_client.chat.completions.create.return_value = mock_plan_response

        # Mock Supabase insert specifically for this test
        mock_insert_response = MagicMock(name="InsertResponseMock_test05")
        mock_insert_response.data = [{"plan_id": plan_id}]
        mock_insert_response.error = None
        # Patch the execute method on the object returned by insert()
        with patch.object(mock_supabase_client.table(plan_table).insert.return_value, 'execute', return_value=mock_insert_response) as mock_execute:

            plan_result_str = orchestrator_agent.generate_workout_plan(goal=goal)

            mock_get_research.assert_called_once()
            mock_get_readiness.assert_called_once()
            mock_openai_client.chat.completions.create.assert_called_once() # Verify direct call
            assert "Run" in plan_result_str

            # Verify Supabase insert call chain
            mock_supabase_client.table.assert_called_with(plan_table)
            mock_supabase_client.table(plan_table).insert.assert_called_once()
            insert_call_args = mock_supabase_client.table(plan_table).insert.call_args[0][0]
            assert insert_call_args['user_id'] == TEST_USER_ID
            assert "Run" in insert_call_args.get('plan_data', '')
            mock_execute.assert_called_once() # Verify execute was called

def test_06_cli_integration(runner, test_user_id):
    """Test basic CLI commands interacting with the system (using mocks)."""
    # 1. Test 'plan' command
    goal = "Triathlon prep"
    mock_plan_output = '{"plan": [{"day": "Wednesday", "activity": "Swim"}]}'
    with patch('personal_ai_trainer.cli.commands.plan.OrchestratorAgent') as MockOrchestratorPlan:
        mock_instance = MockOrchestratorPlan.return_value
        mock_instance.generate_workout_plan.return_value = mock_plan_output
        result = runner.invoke(cli_app, ["plan", "--goal", goal, "--user-id", test_user_id])
        assert result.exit_code == 0, f"CLI Error: {result.stdout}"
        assert "Workout plan generated" in result.stdout
        assert "Swim" in result.stdout
        mock_instance.generate_workout_plan.assert_called_once_with(goal=goal, user_id=test_user_id)

    # 2. Test 'log exercise' command (placeholder check)
    result = runner.invoke(cli_app, ["log", "exercise", "--name", "Bench Press", "--sets", "3", "--reps", "10", "--weight", "50.5"])
    assert result.exit_code == 0, f"CLI Error: {result.stdout}"
    assert "Logged exercise" in result.stdout

    # 3. Test 'progress summary' command (placeholder check)
    result = runner.invoke(cli_app, ["progress", "summary"])
    assert result.exit_code == 0, f"CLI Error: {result.stdout}"
    assert "Weekly summary" in result.stdout

@patch('personal_ai_trainer.utils.scheduler.schedule')
@patch('personal_ai_trainer.utils.scheduler.time')
def test_07_scheduler_integration(mock_time, mock_schedule, test_user_id, mock_supabase_client, mock_oura_wrapper_instance, orchestrator_agent):
    """Test the scheduler setup and triggering the nightly job (mocked)."""
    mock_supabase_client.reset_mock() # Reset supabase mock for this test

    # Configure the mock for _get_all_users within this test
    mock_all_users_data = [{"user_id": test_user_id, "preferences": {"goal": "test goal"}}]
    mock_supabase_client.table('userprofile').select.return_value.execute.return_value.data = mock_all_users_data

    scheduler = Scheduler(
        supabase_client=mock_supabase_client,
        oura_client=mock_oura_wrapper_instance,
        orchestrator_agent=orchestrator_agent
    )

    # Patch the agent method called by the job
    with patch.object(orchestrator_agent, 'adjust_plan_based_on_biometrics') as mock_adjust_plan:
        # Call the scheduler setup method
        scheduler.schedule_nightly_job()
        mock_schedule.every.assert_called_once()
        mock_schedule.every().day.at.assert_called_once_with("02:00")
        mock_schedule.every().day.at().do.assert_called_once_with(scheduler.nightly_job)

        # Simulate the job execution
        scheduler.nightly_job()

        # Verify _get_all_users was called by the job
        mock_supabase_client.table('userprofile').select.assert_called_with('*')
        mock_supabase_client.table('userprofile').select('*').execute.assert_called()

        # Verify the agent method was called with correct args from nightly_job
        mock_adjust_plan.assert_called_once_with(test_user_id, 90) # Pass user_id string and readiness score

@patch('personal_ai_trainer.knowledge_base.repository.get_supabase_client')
@patch('personal_ai_trainer.agents.openai_integration.get_openai_client') # Corrected patch target
def test_08_end_to_end_flow(mock_agent_get_openai, mock_kb_get_supabase, mock_supabase_client, mock_openai_client, mock_oura_wrapper_instance, mock_get_embedding, research_agent, biometric_agent, orchestrator_agent, test_user_id):
    """Test the full flow from research to adjusted plan using mocks."""
    # Ensure the agent and repo use the main mock clients provided by the fixtures
    mock_agent_get_openai.return_value = mock_openai_client
    # Ensure the kb_repo uses the main mock client provided by the fixture
    mock_kb_get_supabase.return_value = mock_supabase_client
    mock_supabase_client.reset_mock() # Reset mocks for this specific test
    mock_openai_client.reset_mock()
    mock_oura_wrapper_instance.reset_mock() # Reset wrapper instance
    mock_get_embedding.reset_mock()

    # Table names
    kb_table = kb_repo.TABLE_NAME
    readiness_table = 'readiness_metrics'
    plan_table = 'workout_plans'
    log_table = 'workout_logs'

    # --- 1. Add research ---
    doc_content = "Endurance training benefits."
    doc_source = "Endurance Today"
    doc_title = "Endurance Benefits"
    doc_id_1 = "doc-e2e-1"
    mock_embedding_1 = [0.3] * 1536
    mock_get_embedding.return_value = mock_embedding_1
    mock_process_resp = MagicMock(choices=[MagicMock(message=MagicMock(content='{"summary": "Endurance is key."}'))])
    mock_openai_client.chat.completions.create.return_value = mock_process_resp
    mock_insert_resp_kb = MagicMock(data=[{"document_id": doc_id_1}], error=None)
    # Patch the insert().execute() for this specific call
    with patch.object(mock_supabase_client.table(kb_table).insert.return_value, 'execute', return_value=mock_insert_resp_kb) as mock_kb_insert_execute:
        research_agent.process_research_document(doc_content, doc_source, doc_title)
        mock_supabase_client.table(kb_table).insert.assert_called_once()
        mock_kb_insert_execute.assert_called_once() # Verify execute was called
    mock_openai_client.chat.completions.create.assert_called_once()

    # --- 2. Fetch Biometrics (initial) ---
    mock_insert_resp_bio1 = MagicMock(data=[{"metrics_id": "metrics-e2e-1"}], error=None)
    # Patch the insert().execute() for this specific call
    with patch.object(mock_supabase_client.table(readiness_table).insert.return_value, 'execute', return_value=mock_insert_resp_bio1) as mock_bio_insert_execute:
        bio_summary = biometric_agent.get_latest_biometrics()
        assert bio_summary['readiness']['score'] == 90
        mock_supabase_client.table(readiness_table).insert.assert_called_once()
        mock_bio_insert_execute.assert_called_once()

    # --- 3. Generate initial plan ---
    goal = "Marathon Training"
    plan_id_1 = "plan-e2e-1"
    mock_kb_search_resp = MagicMock(data=[DBKnowledgeBase(document_id=doc_id_1, title=doc_title, content=doc_content, source=doc_source, embedding=mock_embedding_1).model_dump()], error=None)
    mock_supabase_client.table(kb_table).select.return_value.execute.return_value = mock_kb_search_resp
    mock_plan_resp_1 = MagicMock(choices=[MagicMock(message=MagicMock(content='{"plan": [{"day": "Fri", "activity": "Long Run 10k"}]}'))])
    mock_openai_client.chat.completions.create.reset_mock()
    mock_openai_client.chat.completions.create.return_value = mock_plan_resp_1
    mock_insert_resp_plan1 = MagicMock(data=[{"plan_id": plan_id_1}], error=None)
    # Patch the insert().execute() for this specific call
    with patch.object(mock_supabase_client.table(plan_table).insert.return_value, 'execute', return_value=mock_insert_resp_plan1) as mock_plan_insert_execute:
        initial_plan = orchestrator_agent.generate_workout_plan(goal=goal)
        assert "Long Run 10k" in initial_plan
        mock_supabase_client.table(plan_table).insert.assert_called_once()
        mock_plan_insert_execute.assert_called_once()
    mock_openai_client.chat.completions.create.assert_called_once()

    # --- 4. Log a workout ---
    log_date = datetime.date.today()
    log_id_1 = "log-e2e-1"
    mock_insert_resp_log = MagicMock(data=[{"log_id": log_id_1}], error=None)
    mock_supabase_client.table(log_table).insert.return_value.execute.return_value = mock_insert_resp_log
    workout_data = {
        "user_id": test_user_id, "date": log_date.isoformat(), "workout_type": "Run",
        "duration_minutes": 65, "intensity": "high", "notes": "Felt strong"
    }
    mock_supabase_client.table(log_table).insert(workout_data).execute()
    mock_supabase_client.table(log_table).insert.assert_called_with(workout_data)

    # --- 5. Generate progress report ---
    mock_log_select_resp = MagicMock(data=[workout_data], error=None)
    mock_supabase_client.table(log_table).select.return_value.eq.return_value.execute.return_value = mock_log_select_resp
    mock_report_resp = MagicMock(choices=[MagicMock(message=MagicMock(content='{"report": "Good progress on endurance."}'))])
    mock_openai_client.chat.completions.create.reset_mock()
    mock_openai_client.chat.completions.create.return_value = mock_report_resp

    report = orchestrator_agent.generate_progress_report()
    assert "Good progress" in str(report)
    mock_openai_client.chat.completions.create.assert_called_once()

    # --- 6. Simulate nightly adjustment ---
    mock_oura_wrapper_instance.get_readiness_data.return_value = [{'score': 60, 'summary_date': '2025-05-06'}]
    MagicMock(data=[{"metrics_id": "metrics-e2e-2"}], error=None)
    # Patch the insert().execute() for this specific call (if adjustment logic inserts)
    # with patch.object(mock_supabase_client.table(readiness_table).insert.return_value, 'execute', return_value=mock_insert_resp_bio2) as mock_bio2_insert_execute:
    #     pass # Call adjustment logic here if it inserts

    mock_adjust_resp = MagicMock(choices=[MagicMock(message=MagicMock(content='{"plan": [{"day": "Fri", "activity": "Easy Run 5k"}]}'))])
    mock_openai_client.chat.completions.create.reset_mock()
    mock_openai_client.chat.completions.create.return_value = mock_adjust_resp
    mock_update_resp_plan = MagicMock(data=[{"plan_id": plan_id_1}], error=None)
    mock_supabase_client.table(plan_table).update.return_value.eq.return_value.execute.return_value = mock_update_resp_plan

    # Add assertions for adjustment logic calls when implemented
    assert mock_oura_wrapper_instance.get_readiness_data() == [{'score': 60, 'summary_date': '2025-05-06'}]