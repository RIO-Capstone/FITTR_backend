from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

# Testing the API
def hello_world(request):
    return JsonResponse({"message": "Hello, World"})

# Firebase setup
# cred = credentials.Certificate('path/to/your/serviceAccountKey.json')  # Corrected path
# firebase_admin.initialize_app(cred)


# URL patterns
urlpatterns = [
    path('api/hello/', hello_world),
]
