from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from FITTR_API.models import Product
import json

@csrf_exempt
@require_http_methods(["POST"])
def register_product(request):
    try:
        print("Registering Product")
        data = json.loads(request.body)
        print("Parsed data:", data)
        required_fields = ["version"]
        for field in required_fields:
            if field not in data:
                return JsonResponse({"error": f"{field} is required."}, status=400)
        product = Product.objects.create(
            version = data['version']
        )
        return JsonResponse({"message": "Registration successfull.", "product_id": product.id}, status=201)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({"Server Error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_all_products(request):
    try:
        # Fetch all products from the database
        products = Product.objects.all()
        product_list = [{"id": product.id, "version": product.version} for product in products]
        return JsonResponse({"products": product_list}, status=200)
    
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Server Error", "message": str(e)}, status=500)
