import os
import django

# Ensure Django is set up before executing tasks
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FITTR_API.settings')
django.setup()

from huey import RedisHuey
from .models import User

huey = RedisHuey('fittr_huey', host='localhost', port=6379)

@huey.task()
def generate_ai_feedback(user_id, session_data):
    """
    Task to asynchronously generate AI feedback.
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Import AIAssistant here to avoid circular import
        from .views import AIAssistant
        assistant = AIAssistant(user=user)
        
        # Generate feedback
        feedback = assistant.generate_texts(session_data)
        
        print(f"AI Feedback for User {user_id}: {feedback}")
        return feedback
    
    except User.DoesNotExist:
        print(f"User {user_id} does not exist.")
    except Exception as e:
        print(f"Error in generate_ai_feedback: {e}")


@huey.task()
def generate_rep_suggestions(user_id):
    """
    Task to asynchronously generate rep suggestions.
    """
    try:
        user = User.objects.get(id=user_id)

        # Import AIAssistant here to avoid circular import
        from .views import AIAssistant
        assistant = AIAssistant(user=user)
        
        prompt = (
            "You are a personal trainer. Based on the user's history, "
            "suggest the number of reps they should aim for next session."
        )
        
        output_format = {"rep_suggestions": dict}
        response = assistant.ai_reply_json(prompt, output_format)
        
        print(f"Rep suggestions for User {user_id}: {response}")
        return response
    
    except User.DoesNotExist:
        print(f"User {user_id} does not exist.")
    except Exception as e:
        print(f"Error in generate_rep_suggestions: {e}")
