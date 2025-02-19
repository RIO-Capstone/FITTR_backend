import json
import ollama
<<<<<<< HEAD
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

=======
from typing import List
from FITTR_API.models import ExerciseSession, User
"""
Local Ollama AI assistant (very slow but free)
"""
>>>>>>> 4ffe75294f746b4fdf9646f278f48e6d517395c1
class AIAssistant:
    def __init__(self,user:User):
        self.model_name = "mistral:latest"
        self.context = ""
<<<<<<< HEAD
        self.history = [{"role": "system", "content": "You are a fitness AI assistant. Keep your responses short and concise."}]

    def populate_context(self, data) -> None:
=======
        self.user = user
        greeting = "Ms." if self.user.gender == "female" else "Mr."
        fitness_desc = self.getPersonaDescription(self.user.fitness_goal)
        self.history = [{"role": "system", 
                        "content": 
                        f"You are a fitness AI assistant for {greeting} {self.user.first_name}. {self.user.first_name} \
                        is {self.user.get_age()} years old and has the fitness goal of {fitness_desc}. \
                        {self.user.first_name} has a weight of {self.user.weight} kg and height of {self.user.height} meters. \
                        Use the information about {self.user.first_name} to provide fitness advice. "}]

    def populate_context(self, data:List[ExerciseSession])->None:
>>>>>>> 4ffe75294f746b4fdf9646f278f48e6d517395c1
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

<<<<<<< HEAD
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
=======
    def reply(self,data:List[ExerciseSession])->str:
        # data is always non-empty, logic handled in the get request
        self.populate_context(data)
        prompt = "You are a personal trainer analyzing a user's workout history. " + \
            "The data contains parameters such as duration, reps, exercise type etc." + \
            "Provide constructive feedback on their progress, including trends, improvements, " + \
            "and areas for enhancement using the session data provided. " + \
            "Apart from the session data also use the chat history to enhance your feedback." +\
            " Use the following session data:\n" + self.context + "."
        

        self.history.append({"role": "user", "content": prompt})
        print(f"Generating ai response...for user {self.user.id}") # useless print statement just to see if the function was entered
        response = ollama.chat(
            model=self.model_name,
            messages=self.history
        )
        
        self.history.append({"role": "assistant", "content": response["message"]["content"]})

        return response["message"]["content"]
    
    def getPersonaDescription(self,persona:str)->str:
        # ensure consistency with the persona profiles in the app
        fitnessGoalToDescription = {
            "Strength Seeker": "focused on improving overall strength and endurance through progressive overload in bodyweight and resistance exercises, such as push-ups, pull-ups, and compound lifts.",
            "Muscle Sculptor": "aims to build muscle definition and hypertrophy in targeted muscle groups by following a structured weight training program with progressive overload, proper recovery, and optimized nutrition."
        }
        if persona in fitnessGoalToDescription:
            return fitnessGoalToDescription[persona]
        else:
            return "undecided"
>>>>>>> 4ffe75294f746b4fdf9646f278f48e6d517395c1

class SingletonAIAssistant:
    _instance = None

    @staticmethod
    def get_instance(user:User):
        if SingletonAIAssistant._instance is None:
<<<<<<< HEAD
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
=======
            SingletonAIAssistant._instance = AIAssistant(user=user)
        return SingletonAIAssistant._instance
>>>>>>> 4ffe75294f746b4fdf9646f278f48e6d517395c1
