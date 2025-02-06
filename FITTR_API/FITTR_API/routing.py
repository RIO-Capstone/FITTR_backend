from django.urls import path
from FITTR_API.ExerciseSession import ExerciseSessionConsumer
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
websocket_urlpatterns = [
    path("ws/exercise/<int:user_id>/<int:product_id>/<str:exercise_type>", ExerciseSessionConsumer.as_asgi()),
]
