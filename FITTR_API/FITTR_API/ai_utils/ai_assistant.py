import json
import ollama
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from FITTR_API.models import User

class AIAssistant:
    def __init__(self,user:User):
        self.model_name = "mistral:latest"
        self.context = ""
        self.history = [{"role": "system", "content": "You are a fitness AI assistant. Keep your responses short and concise."}]

    def populate_context(self, data) -> None:
        """
        Formats exercise session data into structured context.
        """
        sessions = []
        for session in data:
            sessions.append({
                "exercise_type": session["exercise_type"],
                "duration": session["duration"],
                "reps": session["reps"],
                "errors": session["errors"],
                "created_at": session["created_at"],
            })
        
        self.context = json.dumps({
            "user_sessions": sessions
        }, indent=4)

    def generate_texts(self, data):
        self.populate_context(data)
        prompts = {
            "summary_advice": "Provide a concise summary of the user's workout performance and key takeaways.",
            "summary_analysis": "Analyze the user's workout trends, improvements, and areas needing attention.",
            "future_advice": "Give specific and actionable advice for improving future workouts based on past performance."
        }
        
        results = {}
        for key, prompt in prompts.items():
            full_prompt = (
                f"You are a personal trainer analyzing a user's workout history. Use the session data provided to {prompt} "
                f"Here is the session data:\n"
                f"{self.context}"
            )
            self.history.append({"role": "user", "content": full_prompt})
            response = ollama.chat(model=self.model_name, messages=self.history)
            self.history.append({"role": "assistant", "content": response["message"]["content"]})
            results[key] = response["message"]["content"]
        
        return results

class SingletonAIAssistant:
    _instance = None

    @staticmethod
    def get_instance(user:User):
        if SingletonAIAssistant._instance is None:
            SingletonAIAssistant._instance = AIAssistant()
        return SingletonAIAssistant._instance

@csrf_exempt
def get_ai_feedback(request, user_id):
    """
    API endpoint to get AI-generated feedback.
    """
    user_sessions = [
        {"exercise_type": "push-up", "duration": 30, "reps": 15, "errors": 1, "created_at": "2025-02-16 10:00:00"},
        {"exercise_type": "squat", "duration": 40, "reps": 20, "errors": 0, "created_at": "2025-02-16 10:05:00"}
    ]  # Dummy data for now
    
    print("Collecting AI feedback...")
    print("Registered user ID:", user_id)
    ai_assistant = SingletonAIAssistant.get_instance()
    feedback = ai_assistant.generate_texts(user_sessions)
    response = {
        "user_id": user_id,
        "feedback": feedback
    }
    return JsonResponse(response)
