import json
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
from FITTR_API.live_stream_util import *
from FITTR_API.ExerciseType import ExerciseType
from FITTR_API.models import ExerciseSession, User, Product
from asgiref.sync import sync_to_async
from django.utils import timezone

class ExerciseSessionConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calibration_min = {}
        self.calibration_max = {}
        self.exercise_data = pd.DataFrame()
        self.test_data = pd.DataFrame()
        self.rep_count = 0
        self.is_calibrated = False
        self.start_time = None
        self.duration = 0

    async def connect(self):
        """
        Called when the WebSocket is handshaking as part of the connection.
        """
        await self.accept()
        self.exercise_type = self.scope['url_route']['kwargs'].get('exercise_type', ExerciseType.SQUATS)
        self.user_id = self.scope['url_route']['kwargs'].get('user_id', 0) # defaults to 0 
        self.product_id = self.scope['url_route']['kwargs'].get('product_id', 0)
        
        self.rep_function = exercise_to_algo_map(exercise_type=self.exercise_type)
        self.filter_function = exercise_to_filter_map(exercise_type=self.exercise_type)
        self.start_time = timezone.now()
        print(f"WebSocket connected: With exercise type {self.exercise_type}. For user with id: {self.user_id} and product id: {self.product_id}")

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        try:
            self.exercise_data.to_csv("testing_file.csv",index=False) # For visualisation purposes
            self.test_data.to_csv("testing_front_camera.csv",index=False) # For visualisation purposes
            self.duration = (timezone.now()-self.start_time).total_seconds()
            if(self.rep_count >= 1): # makes sense to only save the session if at least a rep was performed
                user_instance = await self.get_user_instance()
                product_instace = await self.get_product_instance()
                await self.store_exercise_session(user=user_instance,product=product_instace)
                print(f"Saved exercise session: Type: {self.exercise_type} for user: {self.user_id}")
            else:
                print(f"No reps performed discarding redundant session")
            print(f"WebSocket disconnected with code {close_code}")
        except User.DoesNotExist:
            print(f"WebSocket connection error because user with id {self.user_id} does not exist")
        except Product.DoesNotExist:
            print(f"WebSocket connection error because product with id {self.product_id} does not exist")
        except Exception as e:
            print("WebSocket connection error:",end=" ")
            print(e)

    async def receive(self, text_data):
        """
        Called when a WebSocket message is received.
        """
        data = json.loads(text_data)
        pose_landmarks = data['results'].get("results", None)
        if not pose_landmarks:
            await self.send(json.dumps({"error": "Neither inference time nor pose_landmarks received: {}!".format(text_data)}))
            return

        # Process landmarks
        landmark_data = pd.Series(pose_landmarks[0]["landmarks"])  # Assuming data structure matches
        if not landmark_data.empty:
            landmark_data = landmark_data[0]
            # filter out all the columns that are not required for this particular exercise
            processed_record = process_raw_record(landmark_data)
            if self.test_data.empty:
                self.test_data = pd.DataFrame(columns=processed_record.index)
                assert len(self.test_data.columns) == len(landmark_labels), f"Columns do not match. {self.test_data.columns} vs {landmark_labels}"
            self.test_data = pd.concat([self.test_data, processed_record.to_frame().T], ignore_index=True)
            current_record:pd.Series = self.filter_function(processed_record)
            past_record = self.exercise_data.iloc[-1] if not self.exercise_data.empty else None
            if self.exercise_data.empty:
                self.exercise_data = pd.DataFrame(columns=current_record.index)
            if self.exercise_type == ExerciseType.SQUATS:
                left_knee_angle_joints = ("LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE")
                right_knee_angle_joints = ("RIGHT_HIP", "RIGHT_KNEE", "RIGHT_ANKLE")
                angle_left_knee = joint_angles_per_record(current_record,left_knee_angle_joints)
                angle_right_knee = joint_angles_per_record(current_record,right_knee_angle_joints)
                angle_record = pd.Series([angle_left_knee,angle_right_knee],index=["LEFT_ANGLE","RIGHT_ANGLE"])
                angle_record = ema_smoothing(angle_record,past_record)
                self.add_exercise_point(angle_record,past_record)
            elif self.exercise_type == ExerciseType.LEFT_BICEP_CURLS:
                """
                Use wrist/index finger y (index 1) scalar coordinate for measuring reps
                """
                # TODO: Add more joints for comparison
                left_index = pd.Series(current_record["LEFT_INDEX"][1],index=["LEFT_INDEX"])
                left_index = ema_smoothing(left_index,past_record)
                self.add_exercise_point(left_index,past_record)
            elif self.exercise_type == ExerciseType.RIGHT_BICEP_CURLS:
                right_index = pd.Series(current_record["RIGHT_INDEX"][1],index=["RIGHT_INDEX"])
                right_index = ema_smoothing(right_index,past_record,alpha=0.5)
                self.add_exercise_point(right_index,past_record)
            else: # Exercise Type UNKNOWN
                pass
            await self.send(json.dumps({"rep_count": self.rep_count}))

    def add_exercise_point(self, current_record:pd.Series,past_record:pd.Series|None):
        self.rep_count += self.rep_function(current_record, past_record)
        self.exercise_data = pd.concat([self.exercise_data, current_record.to_frame().T], axis=0)
    
    @sync_to_async
    def get_user_instance(self):
        return User.objects.get(id=self.user_id)
    @sync_to_async
    def get_product_instance(self):
        return Product.objects.get(id=self.product_id)
    @sync_to_async
    def store_exercise_session(self,user,product):
        ExerciseSession.objects.create(
            user_id=user,
            product_id=product,
            exercise_type=self.exercise_type,
            duration=self.duration,
            reps=self.rep_count,
            errors=0
        )