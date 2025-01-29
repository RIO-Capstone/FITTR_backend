from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from .db_utils.user_utils import register_user, get_all_users, get_user, login_user, get_user_history
from .db_utils.product_utils import register_product, get_all_products, get_product

# Testing the API
def hello_world(request):
    return JsonResponse({"message": "Hello, World"})


# Firebase setup
# cred = credentials.Certificate('path/to/your/serviceAccountKey.json')  # Corrected path
# firebase_admin.initialize_app(cred)
user_paths = [
    path('user/register',register_user),
    path('users',get_all_users),
    path('user/<int:id>', get_user),
    path('user/login',login_user),
    path('user/<int:id>/history',get_user_history)
]

product_paths = [
    path('product/register',register_product),
    path('products',get_all_products),
    path('product/<int:id>',get_product)
]

# URL patterns
urlpatterns = [
    path('api/hello/', hello_world),
    path('admin',admin.site.urls),
    *user_paths,
    *product_paths
    #path('api/end_exercise'), TODO: ExerciseSession data needs to be stored to be used later
]
