import json
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
from FITTR_API.live_stream_util import exercise_to_algo_map, exercise_to_filter_map, process_raw_record, smooth_gaussian
from FITTR_API.ExerciseType import ExerciseType

class ExerciseSessionConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calibration_min = {}
        self.calibration_max = {}
        self.exercise_data = pd.DataFrame()
        self.rep_count = 0
        self.is_calibrated = False

    async def connect(self):
        """
        Called when the WebSocket is handshaking as part of the connection.
        """
        await self.accept()
        self.exercise_type = self.scope['url_route']['kwargs'].get('exercise_type', ExerciseType.SQUATS)
        self.rep_function = exercise_to_algo_map(exercise_type=self.exercise_type)
        self.filter_function = exercise_to_filter_map(exercise_type=self.exercise_type)
        print(f"WebSocket connected: With exercise type {self.exercise_type}")

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        self.exercise_data.to_csv("testing_file.csv",index=False)
        print(f"WebSocket disconnected with code {close_code}")

    async def receive(self, text_data):
        """
        Called when a WebSocket message is received.
        """
        data = json.loads(text_data)
        pose_landmarks = data['results'].get("results", None)
        calibration_check = data.get("is_calibrated",False)
        #if calibration_check: self.end_calibration()
        if not pose_landmarks:
            await self.send(json.dumps({"error": "Neither inference time nor pose_landmarks received: {}!".format(text_data)}))
            return

        # Process landmarks
        landmark_data = pd.Series(pose_landmarks[0]["landmarks"])  # Assuming data structure matches
        if not landmark_data.empty:
            landmark_data = landmark_data[0]
            current_record = self.filter_function(process_raw_record(landmark_data))

            if not calibration_check:
                self.update_calibrated_data(current_record)
                #await self.send(json.dumps({"message": "Calibrating..."}))
            else:
                #print("Exercise session beginning")
                scaled_record = self.min_max_scaler(current_record)
                smooth_record = smooth_gaussian(scaled_record)
                self.add_exercise_point(smooth_record)
                await self.send(json.dumps({"rep_count": self.rep_count}))

    def end_calibration(self):
        print("Ended Calibration")
        self.is_calibrated = True

    def update_calibrated_data(self, filtered_record):
        for col in filtered_record.index:
            cur_max = self.calibration_max.get(col, -float('inf'))
            cur_min = self.calibration_min.get(col, float('inf'))
            self.calibration_max[col] = max(filtered_record[col], cur_max)
            self.calibration_min[col] = min(filtered_record[col], cur_min)

    def add_exercise_point(self, current_record):
        if self.exercise_data.empty:
            self.exercise_data = pd.DataFrame(columns=current_record.index)

        past_record = self.exercise_data.iloc[-1] if not self.exercise_data.empty else None
        self.rep_count += self.rep_function(current_record, past_record)
        self.exercise_data = pd.concat([self.exercise_data, current_record.to_frame().T], axis=0)

    def min_max_scaler(self, record: pd.Series) -> pd.Series:
        for col in record.index:
            min_val = self.calibration_min.get(col, 0)
            max_val = self.calibration_max.get(col, 1)
            record[col] = (record[col] - min_val) / (max_val - min_val)
        return record