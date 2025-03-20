# import pytest
# import json
# from unittest.mock import patch, MagicMock
# from FITTR_API.models import User
# from FITTR_API.ai_utils.ai_assistant import AIAssistant, SingletonAIAssistant, get_ai_feedback


# @patch("FITTR_API.ai_utils.ai_assistant.Mistral")
# def test_ai_reply_json(mock_mistral, user_fixture):
#     """Test AI response formatting."""
#     assistant = AIAssistant(user_fixture)
    
#     mock_response = MagicMock()
#     mock_response.choices = [MagicMock()]
#     mock_response.choices[0].message.content = json.dumps({"feedback": "Good job!"})
    
#     mock_mistral.return_value.chat.complete.return_value = mock_response
    
#     output_format = {"feedback": str}
#     response = assistant.ai_reply_json("Give feedback", output_format)
    
#     assert isinstance(response, str)
#     assert json.loads(response) == {"feedback": "Good job!"}

# def test_get_persona_description(user_fixture):
#     """Test persona description mapping."""
#     assistant = AIAssistant(user_fixture)
#     assert assistant.getPersonaDescription("Strength Seeker") == (
#         "focused on improving overall strength and endurance through progressive overload in bodyweight and resistance exercises, such as push-ups, pull-ups, and compound lifts."
#     )
#     assert assistant.getPersonaDescription("Unknown") == "undecided"

# @patch("FITTR_API.ai_utils.ai_assistant.task_ai_feedback")
# def test_get_ai_feedback(mock_task, client):
#     """Test AI feedback API endpoint."""
#     mock_task.return_value = json.dumps({"summary_advice": "Great work!"})
    
#     response = client.get("/api/ai_feedback/1/")
#     assert response.status_code == 200
#     assert json.loads(response.content) == {"user_id": 1, "feedback_message": {"summary_advice": "Great work!"}}
