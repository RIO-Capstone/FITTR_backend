import json
import ollama
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from FITTR_API.models import User
from celery import shared_task

class AIAssistant:
    def __init__(self):
        self.model_name = "mistral:7b"
        self.history = [{"role": "system", "content": "You are a fitness AI assistant. Keep your responses short and concise."}]
    
    def populate_context(self, data) -> str:
        sessions = [
            {
                "exercise_type": session["exercise_type"],
                "duration": session["duration"],
                "reps": session["reps"],
                "errors": session["errors"],
                "created_at": session["created_at"],
            }
            for session in data
        ]
        return json.dumps({"user_sessions": sessions}, indent=4)
    
    def generate_feedback(self, data):
        context = self.populate_context(data)
        prompt = (
            "You are a personal trainer analyzing a user's workout history. Based on the following session data, "
            "provide a JSON response with these fields: \n"
            "- summary_advice: A concise summary of the user's workout performance and key takeaways.\n"
            "- summary_analysis: An analysis of workout trends, improvements, and areas needing attention.\n"
            "- future_advice: Specific and actionable advice for improving future workouts.\n"
            "- form_score: An integer between 1-100 representing the user's form score.\n"
            "- stability_score: An integer between 1-100 representing the user's stability score.\n"
            "- range_of_motion_score: An integer between 1-100 representing the user's range of motion score.\n"
            "Return only valid JSON with these fields and nothing else.\n"
            f"Here is the session data:\n{context}"
        )

        self.history.append({"role": "user", "content": prompt})
        response = ollama.chat(model=self.model_name, messages=self.history)

        try:
            result = json.loads(response["message"]["content"])
        except (json.JSONDecodeError, KeyError):
            result = {
                "summary_advice": "Error generating advice.",
                "summary_analysis": "Error generating analysis.",
                "future_advice": "Error generating future advice.",
                "form_score": 0,
                "stability_score": 0,
                "range_of_motion_score": 0,
            }
        
        self.history.append({"role": "assistant", "content": json.dumps(result)})
        return result

@shared_task
def generate_ai_feedback_task(user_id, user_sessions):
    ai_assistant = AIAssistant()
    feedback = ai_assistant.generate_feedback(user_sessions)
    return feedback

@csrf_exempt
def get_ai_feedback(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_sessions = [
        {"exercise_type": "push-up", "duration": 30, "reps": 15, "errors": 1, "created_at": "2025-02-16 10:00:00"},
        {"exercise_type": "squat", "duration": 40, "reps": 20, "errors": 0, "created_at": "2025-02-16 10:05:00"}
    ]
    
    task = generate_ai_feedback_task.delay(user.id, user_sessions)
    
    response = {
        "user_id": user.id,
        "task_id": task.id,
        "status": "Processing AI feedback..."
    }
    return JsonResponse(response)
