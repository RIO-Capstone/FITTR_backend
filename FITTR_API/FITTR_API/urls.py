from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from .db_utils.user_utils import register_user, get_all_users, get_user, login_user, get_user_history
from .db_utils.product_utils import register_product, get_all_products, get_product
# from .ai_utils.ai_assistant import generate_ai_feedback, get_feedback_on_latest_exercise_session, get_ai_rep_generation

from .views import get_ai_feedback, get_ai_rep_generation, get_feedback_on_latest_exercise_session



# Testing the API
def hello_world(request):
    return JsonResponse({"message": "Hello, World"})


# Firebase setup
# cred = credentials.Certificate('path/to/your/serviceAccountKey.json')  # Corrected path
# firebase_admin.initialize_app(cred)
user_paths = [
    path('user/register', register_user),
    path('users', get_all_users),
    path('user/<int:id>', get_user),
    path('user/login', login_user),
    path('user/<int:id>/history', get_user_history),
    path('user/latest_exercise_session_feedback', get_feedback_on_latest_exercise_session),
    path('user/<int:user_id>/ai_rep_generation', get_ai_rep_generation),
    path('user/<int:user_id>/ai_feedback', get_ai_feedback),
]


product_paths = [
    path('product/register',register_product),
    path('products',get_all_products),
    path('product/<int:id>',get_product)
]


# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/hello/', hello_world),
    path('generate_ai_feedback/<int:user_id>/', get_ai_feedback, name='get_ai_feedback'),
    path('ai-feedback/<int:user_id>/', get_ai_feedback, name='get_ai_feedback'),
    path('ai-rep-generation/<int:user_id>/', get_ai_rep_generation, name='get_ai_rep_generation'),
    #path('api/', include('FITTR_API.urls')),  # Ensure no loop here
]