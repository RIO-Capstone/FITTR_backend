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
from ..ExerciseType import ExerciseType
from huey.contrib import djhuey as huey

load_dotenv()

class AIAssistant:
    def __init__(self, user: User):
        self.api_key = os.getenv('MISTRAL_API_KEY')
        self.model_name = "mistral-tiny"
        self.client = Mistral(api_key=self.api_key)
        greeting = "Ms." if user.gender == "female" else "Mr."
        fitness_desc = self.getPersonaDescription(user.fitness_goal)
        self.bmr_description = user.get_bmr_description()
        self.bmi_description = user.get_bmi_description()


        self.history = [{"role": "system", 
                        "content": 
                        f"You are a personal fitness assistant for {greeting} {user.first_name}. {user.first_name} \
                        is {user.get_age()} years old and has the fitness goal of {fitness_desc}. \
                        {user.first_name} has a weight of {user.weight} kg and height of {user.height} meters. \
                        In terms of BMI, {user.first_name} is {self.bmi_description} and in terms of BMR {user.first_name} has {self.bmr_description} \
                        Use the information about {user.first_name} to provide fitness advice. "}]
        
        self.squatMET = 5.5
        self.bicepCurlMET = 3.8
        
        
        self.userWeight = user.weight
        self.userHeight = user.height
        self.userAge = user.get_age()
        self.userBMR = user.get_bmr()

    def calculate_calories_burned(self, exercise_type: str, exercise_reps) -> float:
        """
        Calculate calories burned based on exercise type and reps.
        """
        MET = 0
        if exercise_type == "RIGHT_BICEP_CURLS" or exercise_type == "LEFT_BICEP_CURLS":
            MET = self.squatMET
        elif exercise_type == "Bicep Curl":
            MET = self.bicepCurlMET
        else:
            return 0.0
        
        duration_hours = (exercise_reps * 2.5) / 3600
        calories_burnt =  (MET * self.userBMR/24)*duration_hours

        return calories_burnt


    def populate_context(self, data:List[ExerciseSession]) -> str:
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
                "created_at": session["created_at"].strftime("%d-%m-%Y %H:%M:%S"),
            })

        return json.dumps({
            "user_sessions": sessions
        }, indent=4)

    def ai_reply_json(self, prompt: str, desired_output_format: dict) -> str:

        format_description = "Return a JSON object with the following structure:\n"
        for key, data_type in desired_output_format.items():
            format_description += f"- '{key}': {data_type.__name__}\n" #getting the name of the datatype

        full_prompt = f"{prompt}\n\n{format_description}\nEnsure the response is a valid JSON object."

        self.history.append({"role": "user", "content": full_prompt})

        response_format = {"type": "json_object"}

        ai_response = self.client.chat.complete(
            model=self.model_name,
            messages=self.history,
            response_format=response_format,
        )

        reply: str = ai_response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})

        return reply
    
    def getPersonaDescription(self,persona:str)->str:
        # ensure consistency with the persona profiles in the app
        fitnessGoalToDescription = {
            "Strength Seeker": "focused on improving overall strength and endurance through progressive overload in bodyweight and resistance exercises, such as push-ups, pull-ups, and compound lifts.",
            "Muscle Sculptor": "aims to build muscle definition and hypertrophy in targeted muscle groups by following a structured weight training program with progressive overload, proper recovery, and optimized nutrition.",
            "Lean Machine":"aims to lose fat and gain muscle mass through a combination of strength training, and a balanced diet to achieve a lean and toned physique.",
        }
        if persona in fitnessGoalToDescription:
            return fitnessGoalToDescription[persona]
        else:
            return "undecided"

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
    try:
        feedback_json = task_ai_feedback(user_id)(blocking=True, timeout=10)  # Blocking task
        return JsonResponse({"user_id":user_id,"feedback_message": feedback_json}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Internal server error"}, status=500)

@huey.task()
def task_ai_feedback(user_id, top_sessions=7):
    try:
        # Fetch user and session data
        user = User.objects.get(id=user_id)
        user_sessions = ExerciseSession.objects.filter(user_id=user_id) \
            .order_by('-created_at')[:top_sessions] \
            .values('exercise_type', 'duration', 'reps', 'errors', 'created_at')
        

        for session in user_sessions:
            print("Execise Type:",session["exercise_type"],"  Date:",session["created_at"])

        latest_exercise_type = user_sessions[0]["exercise_type"]
        latest_reps = user_sessions[0]["reps"]




        if not user_sessions:
            print(f"No sessions found for user {user_id}")
            # Generate default output
            return {
                "summary_advice": "No exercise session performed yet.",
                "summary_analysis": "No data available to analyze workout trends or performance.",
                "future_advice": "Start logging your exercise sessions to receive personalized feedback and advice.",
                "form_score": 0,
                "stability_score": 0,
                "range_of_motion_score": 0,
                "calories_burnt": 0
            }

        print(f"Generating feedback for user {user_id}...")
        ai_assistant = SingletonAIAssistant.get_instance(user)
        context = ai_assistant.populate_context(user_sessions)
        desired_output_format = {
            "summary_advice": str,
            "summary_analysis": str,
            "future_advice": str,
            "form_score": int,
            "stability_score": int,
            "range_of_motion_score": int
        }
        prompt = (
            "You are a personal trainer analyzing a user's workout history. Based on the following session data, "
            "provide a JSON response with these fields: \n"
            "- summary_advice: A concise summary of the user's workout performance and key takeaways. The summary advice should not be more than 30 words.\n"
            "- summary_analysis: An analysis of workout trends, improvements, and areas needing attention.\n"
            "- future_advice: Specific and actionable advice for improving future workouts. Future advice should not be more than 50 words.\n"
            "- form_score: An integer between 1-100 representing the user's form score.\n"
            "- stability_score: An integer between 1-100 representing the user's stability score.\n"
            "- range_of_motion_score: An integer between 1-100 representing the user's range of motion score.\n"
            "Return a valid JSON response. Ensure that none of the integer fields are set to null!\n"
            f"Here is the session data:\n{context}"
        )
        
        feedback_str = ai_assistant.ai_reply_json(prompt, desired_output_format)
        feedback_json = json.loads(feedback_str)

        calories_burnt = ai_assistant.calculate_calories_burned(latest_exercise_type, latest_reps)
        feedback_json["calories_burnt"] = round(calories_burnt, 2)


        # You can log the feedback to the database or notify the user
        print(f"Queue Task complete for user {user_id} for dashboard feedback")
        return feedback_json

    except User.DoesNotExist:
        print(f"QUEUE EXCEPTION: User with ID {user_id} does not exist.")
    except Exception as e:
        print(e)
        print(f"Error generating AI feedback for user {user_id}: {str(e)}")

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
            # QUEUE AND BEGIN TASK
        feedback = task_feedback_on_latest_exercise_session(session_data)(blocking=True, timeout=5)
        return JsonResponse({"feedback_message":feedback})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({"error":"Internal server error"},500)
    
@huey.task()
def task_feedback_on_latest_exercise_session(session_data):
    try:
        user_id = session_data['user_id']
        user = User.objects.get(id=user_id)
        ai_assistant = SingletonAIAssistant.get_instance(user=user)
        session_data["duration"] = str(session_data["duration"]) + " seconds"
        full_prompt = (
            f"You are a personal trainer analyzing a user's workout session. Use the session data provided to \
            give specific and actionable advice for improving future workouts in an encouraging way."
            f"Here is the session data:\n"
            f"{json.dumps(session_data)}"
        )
        output_format = {"feedback_message":str}
        feedback_response = ai_assistant.ai_reply_json(prompt=full_prompt,desired_output_format=output_format)
        feedback_json = json.loads(feedback_response)
        feedback = feedback_json.get("feedback_message","")
        return feedback
    except User.DoesNotExist:
        print("User does not exist!")

@csrf_exempt
@require_http_methods(["GET"])
def get_ai_rep_generation(request, user_id):
    try:
        rep_counts_json = process_ai_rep_generation(user_id)(blocking=True, timeout=5) # Blocking call for 5 seconds
        print(f"Queue task completed with response: {rep_counts_json}")
        return JsonResponse({"feedback_message":rep_counts_json})
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Internal server error"}, status=500)

@huey.task()
def process_ai_rep_generation(user_id):
    try:
        user = User.objects.get(id=user_id)
        ai_assistant = SingletonAIAssistant.get_instance(user)
        
        exercise_types = [attr for attr in dir(ExerciseType) if not callable(getattr(ExerciseType, attr)) and not attr.startswith("__") and not attr.endswith("_THRESHOLD")]
        exercise_list = ", ".join(exercise_types)
        
        prompt = (
            f"You are a personal trainer analyzing a user's workout history..."
            f"Generate a number of reps for each of the following exercises: {exercise_list}."
        )
        
        desired_output_format = {exercise: int for exercise in exercise_types}
        rep_counts_json = ai_assistant.ai_reply_json(prompt, desired_output_format)
        rep_counts_dict = json.loads(rep_counts_json)
        
        reply = {exercise: rep_counts_dict.get(exercise, 0) for exercise in exercise_types}

        return reply  # No JSON response inside a task
    
    except User.DoesNotExist:
        return {"error": f"User with id {user_id} does not exist"}
    
    except Exception as e:
        return {"error": "Internal server error"}

