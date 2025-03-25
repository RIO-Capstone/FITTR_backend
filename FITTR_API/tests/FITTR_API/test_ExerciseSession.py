import pytest
import json
import asyncio
import pandas as pd
from unittest.mock import AsyncMock, patch, MagicMock
from channels.testing import WebsocketCommunicator
from django.utils import timezone
from FITTR_API.ExerciseType import ExerciseType
from FITTR_API.models import User, Product, ExerciseSession
from FITTR_API.ExerciseSession import ExerciseSessionConsumer

@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = MagicMock(spec=User)
    user.id = 1
    return user

@pytest.fixture
def mock_product():
    """Create a mock product for testing."""
    product = MagicMock(spec=Product)
    product.id = 1
    return product

@pytest.fixture
def sample_landmarks():
    """Generate sample pose landmarks for testing."""
    return {
        'results': {
            'results': [{
                'landmarks': [{
                    'LEFT_HIP': [0.5, 0.5, 0.5],
                    'LEFT_KNEE': [0.6, 0.6, 0.6],
                    'LEFT_ANKLE': [0.7, 0.7, 0.7],
                    'RIGHT_HIP': [0.4, 0.4, 0.4],
                    'RIGHT_KNEE': [0.5, 0.5, 0.5],
                    'RIGHT_ANKLE': [0.6, 0.6, 0.6],
                    'LEFT_INDEX': [0.3, 0.3, 0.3],
                    'RIGHT_INDEX': [0.2, 0.2, 0.2]
                }]
            }]
        }
    }

@pytest.mark.asyncio
async def test_websocket_connection(mock_user, mock_product):
    """Test WebSocket connection."""
    # Mock the necessary methods to allow connection
    with patch('FITTR_API.ExerciseSession.ExerciseSessionConsumer.accept', new_callable=AsyncMock) as mock_accept:
        consumer = ExerciseSessionConsumer()
        consumer.scope = {
            'url_route': {
                'kwargs': {
                    'exercise_type': ExerciseType.SQUATS, 
                    'user_id': mock_user.id, 
                    'product_id': mock_product.id
                }
            }
        }
        
        # Manually set up async methods
        consumer.accept = mock_accept
        consumer.send = AsyncMock()
        
        # Simulate connection
        await consumer.connect()
        mock_accept.assert_called_once()

# @pytest.mark.asyncio
# async def test_receive_landmarks(mock_user, mock_product, sample_landmarks):
#     """Test receiving landmarks and processing exercise data."""
#     consumer = ExerciseSessionConsumer()
#     consumer.scope = {
#         'url_route': {
#             'kwargs': {
#                 'exercise_type': ExerciseType.SQUATS, 
#                 'user_id': mock_user.id, 
#                 'product_id': mock_product.id
#             }
#         }
#     }
    
#     # Mock required methods
#     consumer.send = AsyncMock()
#     consumer.accept = AsyncMock()
    
#     # Mock processing methods
#     consumer.filter_function = lambda x: x
#     consumer.rep_function = lambda current, past: 1 if current['LEFT_INDEX'][1] > 0.5 else 0
    
#     # Prepare mock methods
#     consumer.add_exercise_point = MagicMock()
    
#     # Simulate connection and landmark processing
#     await consumer.connect()
#     await consumer.receive(text_data=json.dumps(sample_landmarks))
    
#     # Assert add_exercise_point was called
#     consumer.add_exercise_point.assert_called()

@pytest.mark.asyncio
async def test_disconnect_and_store_session(mock_user, mock_product):
    """Test disconnection and session storage."""
    with patch('FITTR_API.ExerciseSession.ExerciseSessionConsumer.get_user_instance', return_value=mock_user), \
         patch('FITTR_API.ExerciseSession.ExerciseSessionConsumer.get_product_instance', return_value=mock_product):
        
        consumer = ExerciseSessionConsumer()
        consumer.scope = {
            'url_route': {
                'kwargs': {
                    'exercise_type': ExerciseType.SQUATS, 
                    'user_id': mock_user.id, 
                    'product_id': mock_product.id
                }
            }
        }
        
        # Mock async methods
        consumer.send = AsyncMock()
        consumer.store_exercise_session = AsyncMock()
        
        # Simulate exercise session
        consumer.rep_count = 5
        consumer.start_time = timezone.now() - timezone.timedelta(seconds=60)
        
        # Call disconnect
        await consumer.disconnect(close_code=1000)
        
        # Assert session was stored
        consumer.store_exercise_session.assert_called_once_with(user=mock_user, product=mock_product)

def test_add_exercise_point():
    """Test add_exercise_point method."""
    consumer = ExerciseSessionConsumer()
    consumer.rep_function = lambda current, past: 1 if current['LEFT_INDEX'][1] > 0.5 else 0
    consumer.exercise_data = pd.DataFrame()
    
    # Create test data
    current_record = pd.Series({'LEFT_INDEX': [0, 0.6, 0]}, index=['LEFT_INDEX'])
    past_record = None
    
    # Call method
    consumer.add_exercise_point(current_record, past_record)
    
    # Assertions
    assert consumer.rep_count == 1
    assert len(consumer.exercise_data) == 1

# @pytest.mark.asyncio
# @pytest.mark.parametrize("exercise_type", [
#     ExerciseType.SQUATS,
#     ExerciseType.LEFT_BICEP_CURLS,
#     ExerciseType.RIGHT_BICEP_CURLS
# ])
# async def test_exercise_type_handling(exercise_type, sample_landmarks):
#     """Test handling of different exercise types."""
#     consumer = ExerciseSessionConsumer()
#     consumer.exercise_type = exercise_type
    
#     # Mock required methods
#     consumer.send = AsyncMock()
#     consumer.accept = AsyncMock()
    
#     # Prepare mock methods
#     consumer.filter_function = lambda x: x
#     consumer.rep_function = lambda current, past: 1 if current['LEFT_INDEX'][1] > 0.5 else 0
#     consumer.add_exercise_point = AsyncMock()
    
#     # Simulate connection and landmark processing
#     await consumer.connect()
#     await consumer.receive(text_data=json.dumps(sample_landmarks))
    
#     # Assert add_exercise_point was called
#     consumer.add_exercise_point.assert_called()

# @pytest.mark.asyncio
# async def test_error_handling_no_landmarks():
#     """Test error handling when no landmarks are received."""
#     consumer = ExerciseSessionConsumer()
    
#     # Mock required methods
#     consumer.send = AsyncMock()
#     consumer.accept = AsyncMock()
    
#     # Simulate connection
#     await consumer.connect()
    
#     # Send invalid data
#     await consumer.receive(text_data=json.dumps({'results': {}}))
    
#     # Assert send was called with an error
#     consumer.send.assert_called_once()

# def test_error_handling_user_not_found(mock_user, mock_product):
#     """Test error handling when user or product is not found."""
#     with patch('FITTR_API.ExerciseSession.ExerciseSessionConsumer.get_user_instance', side_effect=User.DoesNotExist), \
#          patch('FITTR_API.ExerciseSession.ExerciseSessionConsumer.get_product_instance', side_effect=Product.DoesNotExist):
        
#         consumer = ExerciseSessionConsumer()
#         consumer.scope = {
#             'url_route': {
#                 'kwargs': {
#                     'exercise_type': ExerciseType.SQUATS, 
#                     'user_id': 999, 
#                     'product_id': 999
#                 }
#             }
#         }
        
#         # Mock async methods
#         consumer.send = AsyncMock()
        
#         # Use pytest.raises to check for specific exceptions
#         with pytest.raises((User.DoesNotExist, Product.DoesNotExist)):
#             # Note: This is a coroutine, so we use asyncio.run
#             asyncio.run(consumer.disconnect(close_code=1000))