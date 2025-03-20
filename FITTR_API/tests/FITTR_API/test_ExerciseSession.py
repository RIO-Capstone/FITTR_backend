# import pytest
# import json
# from unittest.mock import patch, MagicMock
# from channels.testing import WebsocketCommunicator
# from FITTR_API.ExerciseSession import ExerciseSessionConsumer
# from FITTR_API.models import User, Product, ExerciseSession
# from django.utils import timezone
# from asgiref.sync import sync_to_async

# @pytest.mark.asyncio
# async def test_websocket_connect():
#     """
#     Test that the WebSocket connects and initializes properly.
#     """
#     communicator = WebsocketCommunicator(
#         ExerciseSessionConsumer.as_asgi(),
#         {"type": "websocket", "path": "/ws/exercise/1/1/SQUATS", "url_route": {"kwargs": {"user_id": 1, "product_id": 1, "exercise_type": "SQUATS"}}}
#     )

#     connected, _ = await communicator.connect()
#     assert connected
#     await communicator.disconnect()

# @pytest.mark.asyncio
# async def test_websocket_receive():
#     """
#     Test receiving a valid message over WebSocket.
#     """
#     communicator = WebsocketCommunicator(
#         ExerciseSessionConsumer.as_asgi(),
#         {"type": "websocket", "path": "/ws/exercise/1/1/SQUATS", "url_route": {"kwargs": {"user_id": 1, "product_id": 1, "exercise_type": "SQUATS"}}}
#     )

#     await communicator.connect()
    
#     test_data = {"results": {"results": [{"landmarks": [1, 2, 3]}]}}
#     await communicator.send_json_to(test_data)

#     response = await communicator.receive_json_from()
#     assert "rep_count" in response

#     await communicator.disconnect()

# @pytest.mark.asyncio
# async def test_websocket_disconnect():
#     """
#     Test that the WebSocket disconnects properly.
#     """
#     communicator = WebsocketCommunicator(
#         ExerciseSessionConsumer.as_asgi(),
#         {"type": "websocket", "path": "/ws/exercise/1/1/SQUATS", "url_route": {"kwargs": {"user_id": 1, "product_id": 1, "exercise_type": "SQUATS"}}}
#     )

#     await communicator.connect()
#     await communicator.disconnect()

# @pytest.mark.django_db
# def test_store_exercise_session():
#     """
#     Test storing an exercise session.
#     """
#     user = User.objects.create(id=1, email="test@example.com", weight=75)
#     product = Product.objects.create(id=1)
#     session = ExerciseSession.objects.create(user_id=user, product_id=product, exercise_type="SQUATS", duration=30, reps=10, errors=2)

#     assert session.user_id == user
#     assert session.product_id == product
#     assert session.exercise_type == "SQUATS"
#     assert session.reps == 10
