from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password, check_password
from FITTR_API.models import User, Product
import json

@csrf_exempt
@require_http_methods(["POST"])
def register_exercise(request):
    try:
        data = json.loads(request.body)
        for field in ["user_id","product_id"]:
            if field not in data:
                return JsonResponse({"error": f"{field} is required."}, status=400) 
        # TODO: Complete implementation
        # Side Note: Do we need this functionality? I'm thinking aren't exercises going to be added directly into a database?
        return JsonResponse({
            
        }, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except User.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials. User does not exist."}, status=401)
    except Product.DoesNotExist:
         return JsonResponse({"error":"Invalid input. Product does not exist",},status=401)
    except Exception as e:
        return JsonResponse({"error": "Login Failed", "message": str(e)}, status=500)

