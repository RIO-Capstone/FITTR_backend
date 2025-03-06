from django.views.decorators.http import require_http_methods
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password, check_password
from FITTR_API.models import User, Product, ExerciseSession
import json
from datetime import datetime, timedelta
import math
from FITTR_API.ai_utils.ai_assistant import SingletonAIAssistant

@csrf_exempt # Cross-Site Request Forgery (CSRF)
@require_http_methods(["POST"])
def login_user(request):
    try:
        data = json.loads(request.body)
        for field in ["email","password"]:
            if field not in data:
                return JsonResponse({"error": f"{field} is required."}, status=400) 
        email = data["email"]
        password = data["password"]
        user = User.objects.get(email=email)
        # if not check_password(password, user.password):
        #     return JsonResponse({"error": "Invalid credentials. Incorrect password."}, status=401)
        # Login success
        return JsonResponse({
            "message": "Login successful.",
            "user": {
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "weight": user.weight,
                "height":user.height,
                "email":user.email,
                "product_id":user.product_id.id
            }
        }, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except User.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials. User not found."}, status=401)
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Login Failed", "message": str(e)}, status=500)

@csrf_exempt # Cross-Site Request Forgery (CSRF)
@require_http_methods(["POST"])
def register_user(request):
    try:
        # Parse JSON body
        data = json.loads(request.body)
        #print("Received request to create a new user: " + json.dumps(data))
        # Validate input fields
        required_fields = [
            "first_name", 
            "last_name", 
            "email", 
            "password", 
            "weight", 
            "height", 
            "phone_number", 
            "gender", 
            "date_of_birth", 
            "product_id",
            "fitness_goal"
        ]

        for field in required_fields:
            if field not in data:
                return JsonResponse({"error": f"{field} is required."}, status=400)
        # date of birth validation
        try:
            date_of_birth = datetime.strptime(data["date_of_birth"], "%d-%m-%Y").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format. Use DD/MM/YYYY."}, status=400)
        
        # Fetch the Product instance from the database
        try:
            product = Product.objects.get(id=data["product_id"])
        except Product.DoesNotExist:
            return JsonResponse({"error": f"Product with given ID {data['product_id']} does not exist."}, status=400)

        if User.objects.filter(email=data['email']).exists():
            return JsonResponse({"error": f"User with email {data['email']} already exists."}, status=400)
        # Create user with hashed password
        user = User.objects.create(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=make_password(data["password"]),
            weight=data["weight"],
            height=data["height"],
            phone_number=data["phone_number"],
            gender=data["gender"],
            date_of_birth=date_of_birth, 
            product_id=product, # Foreign Key
            fitness_goal=data["fitness_goal"]
        )
        
        return JsonResponse({"message": "Registration successfull.", "user_id": user.id}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)

    except Exception as e:
        print(e)
        return JsonResponse({"Server Error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_all_users(request):
    try:
        # Fetch all products from the database
        users = User.objects.all()
        users_list = [{"id": user.id, "full_name": user.first_name + " " + user.last_name} for user in users]
        return JsonResponse({"users": users_list}, status=200) 
    except Exception as e:
        return JsonResponse({"error": "Server Error", "message": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_users_by_product(request, product_id):
    try:
        # Fetch all users with the given product_id_id (column name in the database)
        users = User.objects.filter(product_id_id=product_id)
        
        if not users:
            return JsonResponse({"error": f"No users found for product ID {product_id}"}, status=404)
        
        # Prepare a list of users to return
        users_list = [{"id": user.id, "full_name": user.first_name + " " + user.last_name} for user in users]
        
        return JsonResponse({"users": users_list}, status=200)
    
    except Exception as e:
        return JsonResponse({"error": "Server Error", "message": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_user(request, id):
    try:
        # Fetch user
        user_obj = User.objects.get(id=id)
        
        user_data = {
            "user_id": user_obj.id,
            "first_name": user_obj.first_name,
            "last_name": user_obj.last_name,
            "email": user_obj.email,
            "weight": user_obj.weight,
            "height": user_obj.height,
            "product_id":user_obj.product_id.id
        }
        
        return JsonResponse({"user": user_data}, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": "Server Error", "message": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_user_history(request,id):
    try:
        # filter out all the exercise sessions that belong to this user
        # sort them based on date and calculate streak
        # TODO: Once a user completes an exercise session, this function needs to be called again to update the UI
        unique_dates = (
            ExerciseSession.objects.filter(user_id=id)
            .annotate(date_only=F('created_at__date'))
            .values_list('date_only', flat=True)
            .distinct()
            .order_by('-date_only') # '-' means descending order
        )
        curr = unique_dates.first()
        one_day = timedelta(days=1)
        today = datetime.now().date()
        yesterday = today-one_day
        streak = 0
        # if curr isn't yesterday or today means the streak broke, no need for streak calculation
        if curr and (curr == today or curr == yesterday):
            streak += 1
            curr -= one_day
            for i in range(1,len(unique_dates)):
                if unique_dates[i] == curr:
                    streak += 1
                    curr -= one_day
        # sessions in the last 5 days (HARD CODED)
        # TODO: Future improvement could introduce a filter parameter in the endpoint for dynamic querying
        five_days_ago = today-timedelta(days=5)
        sessions_in_last_5_days = ExerciseSession.objects.filter(
            user_id=id, created_at__date__gte=five_days_ago
        ).order_by('-created_at')
        # just returning the duration of the exercise
        # TODO: Could work out logic for calculating exercise accuracy in the future (based on reps/errors)
        session_data = [
            {
                "duration": math.ceil(session.duration/60), # seconds to minutes
                "date":format_date_with_suffix(session.created_at)
            }
            for session in sessions_in_last_5_days
        ]
        return JsonResponse({"streak":streak,"session_data":session_data})
            
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except User.DoesNotExist:
        return JsonResponse({"error":"User not found"},status=404)
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Server Error", "message": str(e)}, status=500)

def format_date_with_suffix(date_obj)->str:
    # Helper function to get the ordinal suffix
    def get_ordinal_suffix(day):
        if 11 <= day <= 13:  # Handle special cases for 11th, 12th, and 13th
            return "th"
        last_digit = day % 10
        if last_digit == 1:
            return "st"
        elif last_digit == 2:
            return "nd"
        elif last_digit == 3:
            return "rd"
        else:
            return "th"

    # Extract day and month
    day = date_obj.day
    month = date_obj.strftime("%b")  # Short month name (e.g., "Feb")

    # Add the ordinal suffix to the day
    suffix = get_ordinal_suffix(day)

    return f"{day}{suffix} {month}"