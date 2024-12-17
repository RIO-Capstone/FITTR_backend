from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password, check_password
from FITTR_API.models import User, Product
import json
from datetime import datetime

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
        if not check_password(password, user.password):
            return JsonResponse({"error": "Invalid credentials. Incorrect password."}, status=401)
        # Login success
        return JsonResponse({
            "message": "Login successful.",
            "user": {
                "user_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "weight": user.weight,
                "height":user.height,
                "email":user.email
            }
        }, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except User.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials. User not found."}, status=401)
    except Exception as e:
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
            "product_id"
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
            return JsonResponse({"eror": f"Product with given ID {data['product_id']} does not exist."}, status=400)
        
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
def get_user(request, id):
    try:
        # Fetch user
        user_obj = User.objects.get(id=id)
        
        user_data = {
            "id": user_obj.id,
            "first_name": user_obj.first_name,
            "last_name": user_obj.last_name,
            "email": user_obj.email,
            "weight": user_obj.weight,
            "height": user_obj.height,
            "phone_number": user_obj.phone_number,
            "gender": user_obj.gender,
            "date_of_birth": user_obj.date_of_birth.strftime("%d-%m-%Y"),
            "product_id": user_obj.product_id.id,
        }
        
        return JsonResponse({"user": user_data}, status=200)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": "Server Error", "message": str(e)}, status=500)
