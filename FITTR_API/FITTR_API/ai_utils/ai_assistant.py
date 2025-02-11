import json
import ollama
from typing import List
from FITTR_API.models import ExerciseSession, User
"""
Local Ollama AI assistant (very slow but free)
"""
class AIAssistant:
    def __init__(self,user:User):
        self.model_name = "mistral:latest"
        self.context = ""
        self.user = user
        greeting = "Ms." if self.user.gender == "female" else "Mr."
        self.history = [{"role": "system", 
                        "content": 
                        f"You are a fitness AI assistant for {greeting} {self.user.first_name}. {self.user.first_name} \
                        is {self.user.get_age()} years old and has the fitness goal of {self.user.fitness_goal}. \
                        {self.user.first_name} has a weight of {self.user.weight} kg and height of {self.user.height} meters. \
                        Use the information about {self.user.first_name} to provide fitness advice. "}]

    def populate_context(self, data:List[ExerciseSession])->None:
        """
        Formats exercise session data into structured context.
        """
        sessions = []
        for session in data:
            sessions.append({
                "exercise_type": session.exercise_type,
                "duration": session.duration,
                "reps": session.reps,
                "errors": session.errors,
                "created_at": session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
        
        self.context = json.dumps({
            "user_sessions": sessions
        }, indent=4)

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

class SingletonAIAssistant:
    _instance = None
    @staticmethod
    def get_instance(user:User):
        if SingletonAIAssistant._instance is None:
            SingletonAIAssistant._instance = AIAssistant(user=user)
        return SingletonAIAssistant._instance