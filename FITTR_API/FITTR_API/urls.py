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
    #path('api/start_exercise/'), # TODO: Add a handling function
    #path('api/end_exercise'),
    #path('api/end_calibration') #TODO: Add a handling function
]
# How do i run a singleton ExerciseSession class and handle real time feedback as well as HTTP requests from the user when 
# the state of the session changes?