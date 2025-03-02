import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import User
from .tasks import generate_ai_feedback, generate_rep_suggestions

@csrf_exempt
@require_http_methods(["GET"])
def get_ai_feedback(request, user_id):
    """
    API endpoint to get AI-generated feedback.
    This will use Huey to run the task asynchronously.
    """
    # Get the user from the database
    user = get_object_or_404(User, id=user_id)

    # Dummy session data for now (you can replace it with actual session data)
    user_sessions = [
        {"exercise_type": "push-up", "duration": 30, "reps": 15, "errors": 1, "created_at": "2025-02-16 10:00:00"},
        {"exercise_type": "squat", "duration": 40, "reps": 20, "errors": 0, "created_at": "2025-02-16 10:05:00"}
    ]

    # Enqueue the task to generate AI feedback asynchronously via Huey
    generate_ai_feedback(user.id, user_sessions)

    # Return a response indicating the feedback generation is in progress
    return JsonResponse({"message": "Feedback generation in progress."})


@csrf_exempt
@require_http_methods(["GET"])
def get_ai_rep_generation(request, user_id):
    """
    API endpoint to trigger AI rep suggestions.
    """
    # Get the user from the database
    user = get_object_or_404(User, id=user_id)

    # Enqueue the task to generate rep suggestions asynchronously via Huey
    generate_rep_suggestions(user.id)

    # Return a response indicating the rep suggestion generation is in progress
    return JsonResponse({"message": "Rep suggestion in progress."})

@csrf_exempt
@require_http_methods(["POST"])
def get_feedback_on_latest_exercise_session(request):
    """
    API endpoint to get feedback on the latest exercise session.
    """
    try:
        session_data = json.loads(request.body)
        required_fields = [
            "user_id",
            "rep_count",
            "duration",
            "errors",
            "created_at",
            "exercise_type"
        ]

        # Check for required fields
        for field in required_fields:
            if field not in session_data:
                return JsonResponse({"error": f"Field {field} is missing for single session feedback"}, status=400)

        user_id = session_data['user_id']
        user = get_object_or_404(User, id=user_id)

        # You can add the logic for analyzing session data here
        feedback = "Feedback based on the session data."

        return JsonResponse({"feedback_message": feedback})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except User.DoesNotExist:
        return JsonResponse({"error": "User does not exist!"}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)
