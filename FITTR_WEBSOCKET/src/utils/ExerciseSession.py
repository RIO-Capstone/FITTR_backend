import numpy as np
import asyncio
from typing import List
import json
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)).rsplit("src", 1)[0])
from src.utils.live_stream_util import exercise_to_algo_map, exercise_to_filter_map, process_raw_record, smooth_gaussian
from websockets.server import serve


class ExerciseSession:
    def __init__(self, exercise_type: str, host_address: str = "", socket_port: int = 8001) -> None:
        # exercise properties
        self.calibration_min = {}
        self.calibration_max = {}
        self.exercise_data = pd.DataFrame()
        self.rep_function = exercise_to_algo_map(exercise_type=exercise_type)
        self.filter_function = exercise_to_filter_map(exercise_type=exercise_type)
        self.rep_count = 0
        self.is_calibrated = False
        # web socket properties
        self._running_task = None  # Control the server lifecycle
        self._stop_event = asyncio.Event()  # Event to signal stopping the session
        self.host_address = host_address
        self.socket_port = socket_port
        

    def update_calibrated_data(self, filtered_record: pd.Series):
        for col in filtered_record.index:
            cur_max = self.calibration_max.get(col, -np.inf)
            cur_min = self.calibration_min.get(col, np.inf)
            self.calibration_max[col] = np.max([filtered_record[col], cur_max])
            self.calibration_min[col] = np.min([filtered_record[col], cur_min])

    def end_calibration(self):
        self.is_calibrated = True

    async def handle_client(self, websocket):
        """
        Handle individual WebSocket clients for the exercise session.
        """
        print("Client connected to websocket!")
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                inference_time = data.get("inferenceTime", None)
                pose_landmarks = data.get("results", None)
                
                if not inference_time or not pose_landmarks:
                    raise Exception(f"Invalid data received! inference time: {inference_time}, results: {pose_landmarks}")
                
                landmark_data = data["results"][0]["landmarks"]
                
                if not landmark_data:
                    print("Invalid landmark: {}".format(landmark_data))
                    continue
                    #raise Exception(f"Invalid landmark data received during exercise session: Landmarks --> {landmark_data}")
                landmark_data = pd.Series(landmark_data[0]) # an array of objects {presence:{},visibility:{},x:float,y:float,z:float}
                
                # Filter out unrelated columns and extract x, y, z coordinates
                current_record = self.filter_function(process_raw_record(landmark_data))
                if not self.is_calibrated:
                    self.update_calibrated_data(filtered_record=current_record)
                else:
                    scaled_record = self.min_max_scaler(current_record)
                    smooth_record = smooth_gaussian(scaled_record)
                    self.add_exercise_point(current_record=smooth_record)
        except Exception as e:
            print(f"Error while handling client: {e.with_traceback(e.__traceback__)}")
        finally:
            print("Client disconnected.")

    async def start(self):
        """
        Start the WebSocket server and listen for connections.
        """
        print(f"Starting Exercise Session on {self.host_address}:{self.socket_port}")
        self._running_task = asyncio.create_task(self._run_server())  # Create the server task
        await self._stop_event.wait()  # Wait until `end` is called

    async def _run_server(self):
        async with serve(self.handle_client, self.host_address, self.socket_port):
            await self._stop_event.wait()  # Keep running until the stop event is set

    async def end(self):
        """
        Signal to end the session and clean up resources.
        """
        print("Stopping Exercise Session...")
        self._stop_event.set()  # Trigger the stop event to end the session
        if self._running_task:
            await self._running_task  # Ensure the server task finishes
        return self.rep_count

    def add_exercise_point(self, current_record: pd.Series) -> None:
        """
        Use this live stream data record to determine whether a rep has been performed.
        """
        past_record = None
        # update the columns in the exercise_data 
        if self.exercise_data.empty:
            self.exercise_data = pd.DataFrame(columns=current_record.index)

        if not self.exercise_data.empty:
            past_record = self.exercise_data.iloc[-1]
        self.rep_count += self.rep_function(current_record, past_record)
        self.exercise_data = pd.concat([self.exercise_data, current_record.to_frame().T], axis=0)

    def min_max_scaler(self, record: pd.Series) -> pd.Series:
        """
        Scales data using min-max scaling based on calibration data.
        """

        for col in record.index:
            min_val = self.calibration_min.get(col,0)
            max_val = self.calibration_max.get(col,1)
            record[col] = (record[col]-min_val)/(max_val-min_val)
        return record
        
