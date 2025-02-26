import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from FITTR_API.models import User, Product, ExerciseSession
from django.shortcuts import get_object_or_404
from dotenv import load_dotenv
import os
from mistralai import Mistral
from typing import List, Mapping
load_dotenv()

class AIAssistant:
    def __init__(self, user: User):
        self.api_key = os.getenv('MISTRAL_API_KEY')
        self.model_name = "mistral-large-latest"
        self.client = Mistral(api_key=self.api_key)
        self.history = [{"role": "system", "content": "You are a fitness AI assistant. Keep your responses short and concise."}]

    def populate_context(self, data:List[ExerciseSession]) -> None:
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
        
        return json.dumps({
            "user_sessions": sessions
        }, indent=4)

    def generate_texts(self, data)->dict:
        context = self.populate_context(data)
        prompts = {
            "summary_advice": "Provide a concise summary of the user's workout performance and key takeaways.",
            "summary_analysis": "Analyze the user's workout trends, improvements, and areas needing attention.",
            "future_advice": "Give specific and actionable advice for improving future workouts based on past performance.",
            "form_score": "Provide only a number (no words) between 1-100 for the user's form score based on their workout performance.",
            "stability_score": "Provide only a number (no words) between 1-100 for the user's stability score based on their workout performance.",
            "range_of_motion_score": "Provide only a number (no words) between 1-100 for the user's range of motion score based on their workout performance."
        }

        results = {}
        for key, prompt in prompts.items():
            full_prompt = (
                f"You are a personal trainer analyzing a user's workout history. Use the session data provided to {prompt} "
                f"Here is the session data:\n"
                f"{context}"
            )
            self.history.append({"role": "user", "content": full_prompt})

            aiResponseObject = self.client.chat.complete(model=self.model_name,messages=self.history)
            reply = aiResponseObject.choices[0].message.content
            self.history.append({"role": "assistant", "content": reply})

            # Extract numeric values for score-related fields
            if key in ["form_score", "stability_score", "range_of_motion_score"]:
                results[key] = self.extract_numeric_value(reply)
            else:
                results[key] = reply
        
    def single_session_feedback(self,session:str):
        full_prompt = (
            f"You are a personal trainer analyzing a user's workout session. Use the session data provided to \
            give specific and actionable advice for improving future workouts in an encouraging way. It is \
            very important that you provide only 2 bullet points!" 
            f"Here is the session data:\n"
            f"{session}"
        )
        self.history.append({"role": "user", "content": full_prompt})
        ai_response = self.client.chat.complete(model=self.model_name,messages=self.history)
        reply = ai_response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply


    def extract_numeric_value(self,text):
        """
        Extracts the first numeric value from a text response.
        If no number is found, it defaults to 0.
        """
        match = re.search(r"\d+", text)
        return int(match.group()) if match else 0


class SingletonAIAssistant:
    _instances : Mapping[int,AIAssistant] = {}
    @staticmethod
    def get_instance(user: User)->AIAssistant:
        if user.id not in SingletonAIAssistant._instances:
            SingletonAIAssistant._instances[user.id] = AIAssistant(user)
        return SingletonAIAssistant._instances[user.id]


@csrf_exempt
@require_http_methods(["GET"])
def get_ai_feedback(request, user_id):
    """
    API endpoint to get AI-generated feedback.
    """
    user = get_object_or_404(User, id=user_id)

    user_sessions = [
        {"exercise_type": "push-up", "duration": 30, "reps": 15, "errors": 1, "created_at": "2025-02-16 10:00:00"},
        {"exercise_type": "squat", "duration": 40, "reps": 20, "errors": 0, "created_at": "2025-02-16 10:05:00"}
    ]  # Dummy data for now

    print("Collecting AI feedback...")
    print("Registered user ID:", user.id)

    ai_assistant = SingletonAIAssistant.get_instance(user)
    feedback = ai_assistant.generate_texts(user_sessions)

    response = {
        "user_id": user.id,
        "feedback_message": {
            "summary_advice": feedback.get("summary_advice", ""),
            "summary_analysis": feedback.get("summary_analysis", ""),
            "future_advice": feedback.get("future_advice", ""),
            "form_score": feedback.get("form_score", 0),
            "stability_score": feedback.get("stability_score", 0),
            "range_of_motion_score": feedback.get("range_of_motion_score", 0)
        }
    }
    return JsonResponse(response)

@csrf_exempt
@require_http_methods(["POST"])
def get_feedback_on_latest_exercise_session(request):
    try:
        # get the exercise session data from the App and return some feedback
        session_data = json.loads(request.body)
        print("Session data received: ", session_data)
        required_fields = [
            "user_id",
            "rep_count",
            "duration",
            "errors",
            "created_at", # should be the same format as the Exercise Session object created in the web socket connection
            "exercise_type"
        ]
        for field in required_fields:
            if field not in session_data:
                return JsonResponse({"error":f"Field {field} is missing for single session feedback"},500)
        user_id = session_data['user_id']
        user = User.objects.get(id=user_id)
        ai_assistant = SingletonAIAssistant.get_instance(user=user)
        session_data["duration"] += " seconds"
        feedback = ai_assistant.single_session_feedback(json.dumps(session_data))
        print(f"AI session feedback " + feedback)
        return JsonResponse({"feedback_message":feedback})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except User.DoesNotExist:
        return JsonResponse({"error":f"User does not exist!"},404)
    except Exception as e:
        print(e)
        return JsonResponse({"error":"Internal server error"},500)