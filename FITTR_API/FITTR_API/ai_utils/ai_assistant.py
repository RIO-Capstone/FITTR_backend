import json
import ollama
from typing import Collection
"""
Local Ollama AI assistant (very slow but free)
"""
class AIAssistant:
    def __init__(self):
        self.model_name = "mistral:latest"
        self.context = ""
        self.history = [{"role": "system", "content": "You are a fitness AI assistant."}]

    def populate_context(self, data)->None:
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

    def reply(self,data)->str:
        self.populate_context(data)
        prompt = (
            "You are a personal trainer analyzing a user's workout history. " +
            "The data contains parameters such as duration, reps, exercise type etc." + 
            "Provide constructive feedback on their progress, including trends, improvements, " + 
            "and areas for enhancement using the session data provided. " + 
            "Apart from the session data also use the chat history to enhance your feedback." +
            " Use the following session data:\n" + self.context + "."
        )

        self.history.append({"role": "user", "content": prompt})
        print("Generating ai response...") # useless print statement just to see if the function was entered
        response = ollama.chat(
            model=self.model_name,
            messages=self.history
        )
        
        self.history.append({"role": "assistant", "content": response["message"]["content"]})

        return response["message"]["content"]

class SingletonAIAssistant:
    _instance = None
    @staticmethod
    def get_instance():
        if SingletonAIAssistant._instance is None:
            SingletonAIAssistant._instance = AIAssistant()
        return SingletonAIAssistant._instance