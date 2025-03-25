import pytest
import json
from unittest.mock import Mock, patch
from django.http import JsonResponse
from django.test import RequestFactory
from FITTR_API.models import User, ExerciseSession
from FITTR_API.ai_utils.ai_assistant import (
    AIAssistant, 
    SingletonAIAssistant, 
    get_ai_feedback, 
    task_ai_feedback, 
    get_feedback_on_latest_exercise_session,
    task_feedback_on_latest_exercise_session,
    get_ai_rep_generation,
    process_ai_rep_generation
)
from FITTR_API.ExerciseType import ExerciseType

@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return Mock(
        spec=User,
        id=1,
        first_name="John",
        gender="male",
        fitness_goal="Strength Seeker",
        weight=75,
        height=1.80,
        get_age=lambda: 30,
        get_bmr_description=lambda: "has a moderate BMR",
        get_bmi_description=lambda: "within normal range"
    )

@pytest.fixture
def mock_exercise_sessions():
    """Create mock exercise sessions."""
    return [
        {
            "exercise_type": "PUSH_UP",
            "duration": 300,
            "reps": 20,
            "errors": "None",
            "created_at": Mock(strftime=lambda x: "01-01-2024 12:00:00")
        }
    ]

def test_ai_assistant_initialization(mock_user):
    """Test AIAssistant initialization."""
    assistant = AIAssistant(mock_user)
    
    assert len(assistant.history) == 1
    assert assistant.history[0]['role'] == 'system'
    assert 'Mr. John' in assistant.history[0]['content']

def test_populate_context(mock_user, mock_exercise_sessions):
    """Test populate_context method."""
    assistant = AIAssistant(mock_user)
    context = assistant.populate_context(mock_exercise_sessions)
    
    context_dict = json.loads(context)
    assert 'user_sessions' in context_dict
    assert len(context_dict['user_sessions']) == 1
    assert context_dict['user_sessions'][0]['exercise_type'] == 'PUSH_UP'

def test_getPersonaDescription():
    """Test getPersonaDescription method."""
    assistant = AIAssistant(Mock())
    
    assert "focused on improving overall strength" in assistant.getPersonaDescription("Strength Seeker")
    assert "aims to build muscle definition" in assistant.getPersonaDescription("Muscle Sculptor")
    assert assistant.getPersonaDescription("Unknown") == "undecided"

def test_singleton_ai_assistant(mock_user):
    """Test SingletonAIAssistant pattern."""
    assistant1 = SingletonAIAssistant.get_instance(mock_user)
    assistant2 = SingletonAIAssistant.get_instance(mock_user)
    
    assert assistant1 is assistant2  # Same instance for same user

@patch('FITTR_API.ai_utils.ai_assistant.task_ai_feedback')
def test_get_ai_feedback(mock_task, mock_user):
    """Test get_ai_feedback endpoint."""
    mock_task.return_value.return_value = {"feedback": "Great job!"}
    
    request = RequestFactory().get(f'/ai-feedback/{mock_user.id}')
    response = get_ai_feedback(request, mock_user.id)
    
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data['user_id'] == mock_user.id

# @patch('FITTR_API.ai_utils.ai_assistant.User.objects.get')
# @patch('FITTR_API.ai_utils.ai_assistant.ExerciseSession.objects.filter')
# def test_task_ai_feedback(mock_sessions, mock_user_get, mock_user, mock_exercise_sessions):
#     """Test task_ai_feedback task."""
#     mock_user_get.return_value = mock_user
#     mock_sessions.return_value.values.return_value = mock_exercise_sessions
    
#     with patch.object(AIAssistant, 'ai_reply_json') as mock_ai_reply:
#         mock_ai_reply.return_value = json.dumps({
#             "summary_advice": "Great workout!",
#             "form_score": 85,
#             "stability_score": 90,
#             "range_of_motion_score": 88
#         })
        
#         result = task_ai_feedback(mock_user.id)
        
#         assert result['summary_advice'] == "Great workout!"
#         assert result['form_score'] == 85

def test_get_feedback_on_latest_exercise_session(mock_user):
    """Test get_feedback_on_latest_exercise_session endpoint."""
    session_data = {
        "user_id": mock_user.id,
        "rep_count": 20,
        "duration": 300,
        "errors": "None",
        "created_at": "2024-01-01T12:00:00",
        "exercise_type": "PUSH_UP"
    }
    
    with patch('FITTR_API.ai_utils.ai_assistant.task_feedback_on_latest_exercise_session') as mock_task:
        mock_task.return_value.return_value = "Great session feedback!"
        
        request = RequestFactory().post('/exercise-feedback', 
                                        content_type='application/json', 
                                        data=json.dumps(session_data))
        response = get_feedback_on_latest_exercise_session(request)
        
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['feedback_message'] == "Great session feedback!"

# def test_process_ai_rep_generation(mock_user):
#     """Test process_ai_rep_generation task."""
#     exercise_types = [attr for attr in dir(ExerciseType) if not callable(getattr(ExerciseType, attr)) and not attr.startswith("__") and not attr.endswith("_THRESHOLD")]
    
#     with patch.object(AIAssistant, 'ai_reply_json') as mock_ai_reply:
#         mock_rep_counts = {exercise: 15 for exercise in exercise_types}
#         mock_ai_reply.return_value = json.dumps(mock_rep_counts)
        
#         result = process_ai_rep_generation(mock_user.id)
        
#         assert all(result[exercise] == 15 for exercise in exercise_types)

@pytest.mark.parametrize("input_persona,expected_description", [
    ("Strength Seeker", "focused on improving overall strength"),
    ("Muscle Sculptor", "aims to build muscle definition"),
    ("Lean Machine", "aims to lose fat and gain muscle mass"),
    ("Unknown", "undecided")
])
def test_persona_description_variations(input_persona, expected_description):
    """Test variations of persona descriptions."""
    assistant = AIAssistant(Mock())
    assert expected_description in assistant.getPersonaDescription(input_persona)