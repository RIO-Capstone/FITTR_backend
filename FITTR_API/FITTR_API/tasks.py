# FITTR_API/tasks.py

from celery import shared_task
from .ai_assistant import AIAssistant  # Assuming AIAssistant class is imported from your code

@shared_task
def generate_ai_feedback_task(user_id, user_sessions):
    ai_assistant = AIAssistant()
    feedback = ai_assistant.generate_feedback(user_sessions)
    return feedback
