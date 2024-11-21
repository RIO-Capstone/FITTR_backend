from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import firebase_admin
from firebase_admin import credentials, auth, firestore
import json
from serializers import *   # Make sure this is correctly imported
import serializers

# Testing the API
def hello_world(request):
    return JsonResponse({"message": "Hello, World"})

# Firebase setup
# cred = credentials.Certificate('path/to/your/serviceAccountKey.json')  # Corrected path
# firebase_admin.initialize_app(cred)

# Firestore client 
db = firestore.client()

# Serializer for the user data response
class UserSerializer(serializers.Serializer):
    uid = serializers.CharField()
    email = serializers.EmailField()
    user_info = serializers.DictField(child=serializers.CharField())



## SAMPLE USER SIDE CODE JUST FOR CLARITY

# firebase.auth().signInWithEmailAndPassword(email, password)
#     .then((userCredential) => {
#         const user = userCredential.user;
#         return user.getIdToken();  // Get the Firebase ID token
#     })
#     .then((idToken) => {
#         // Send the ID token to your Django API
#         fetch('/api/login/', {
#             method: 'POST',
#             headers: {
#                 'Content-Type': 'application/json',
#             },
#             body: JSON.stringify({ idToken: idToken }),
#         })
#         .then(response => response.json())
#         .then(data => {
#             console.log('User data from Django API:', data);
#         })
#         .catch(error => {
#             console.error('Error during login:', error);
#         });
#     })
#     .catch((error) => {
#         console.error('Error logging in:', error);
#     });

##
#   Authentication is done on client side with Firebase and the ID token is sent to the Djangon API
##




# API view for Firebase login
class FirebaseLoginAPIView(APIView):
    def post(self, request):
        try:
            # Get Firebase ID Token from the request body
            body = json.loads(request.body.decode('utf-8'))
            id_token = body.get('idToken')

            if not id_token:
                return Response({"error": "ID token is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Verify the Firebase ID Token
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']  # Firebase User ID
            user = auth.get_user(uid)

            # Retrieve additional user info from Firestore (assuming 'users' collection)
            user_ref = db.collection('users').document(uid)
            user_data = user_ref.get()

            if user_data.exists:
                user_info = user_data.to_dict()
            else:
                user_info = {}

            
            response_data = {
                "uid": uid,
                "email": user.email,
                "user_info": user_info
            }

            # Serialize the response
            serializer = UserSerializer(response_data)

            # Return the response
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Authentication failed: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)



# URL patterns
urlpatterns = [
    path('api/hello/', hello_world),  
    path('api/login/', FirebaseLoginAPIView.as_view(), name='firebase_login'),
]
