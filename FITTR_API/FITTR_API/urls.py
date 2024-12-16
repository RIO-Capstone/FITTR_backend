from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from .db_utils.user_utils import register_user, get_all_users
from .db_utils.product_utils import register_product, get_all_products

# Testing the API
def hello_world(request):
    return JsonResponse({"message": "Hello, World"})


# Firebase setup
# cred = credentials.Certificate('path/to/your/serviceAccountKey.json')  # Corrected path
# firebase_admin.initialize_app(cred)
user_paths = [
    path('user/register',register_user),
    path('users',get_all_users)
    #path('user/login')
]

product_paths = [
    path('product/register',register_product),
    path('products',get_all_products)
]

# URL patterns
urlpatterns = [
    path('api/hello/', hello_world),
    path('admin',admin.site.urls),
    #path('exercise/start/',) # TODO: Add a handling function
    *user_paths,
    *product_paths
    #path('api/end_exercise'),
    #path('api/end_calibration') #TODO: Add a handling function
]
# How do i run a singleton ExerciseSession class and handle real time feedback as well as HTTP requests from the user when 
# the state of the session changes?