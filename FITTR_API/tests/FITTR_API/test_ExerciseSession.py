# import pytest
# import json
# import pandas as pd
# from channels.testing import WebsocketCommunicator
# from FITTR_API.ExerciseSession import ExerciseSessionConsumer
# from FITTR_API.models import User, Product, ExerciseSession
# from django.utils import timezone
# from unittest.mock import AsyncMock, patch


# @pytest.mark.asyncio
# async def test_websocket_connect():
#     """
#     Test that the WebSocket connects and initializes properly.
#     """
#     user_id = 1
#     product_id = 1
#     exercise_type = "SQUATS"

#     communicator = WebsocketCommunicator(
#         ExerciseSessionConsumer.as_asgi(), f"/ws/exercise/{user_id}/{product_id}/{exercise_type}/"
#     )

#     try:
#         connected, _ = await communicator.connect()
#         assert connected
#     finally:
#         await communicator.disconnect()  # Ensure proper cleanup

