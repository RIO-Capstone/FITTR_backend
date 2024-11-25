import asyncio
import websockets
import json
import ssl
import pandas as pd
from websockets.asyncio.server import serve
from src.utils import ExerciseSession, ExerciseType

IP = "192.168.0.170"

# async def handle_client(websocket):
#     client_ip = websocket.remote_address  # Get client IP and port info
#     print(f"Client connected: {client_ip}")
#     try:
#         while True:
#             # Wait for incoming messages from the client
#             message = await websocket.recv()
#             # Parse the received message as JSON
#             try:
#                 data = json.loads(message)  # Convert the message to a Python dictionary
#                 #print(f"Received message as JSON: {data}")
#                 # use calibrated data to segment data here
                
#                 # Access specific fields from the parsed JSON
#                 inference_time = data.get("inferenceTime", None)
#                 pose_landmarks = data.get("results",None)
#                 if not inference_time or not pose_landmarks:
#                     raise Exception(f"Invalid data received! inference time: {inference_time}, results: {pose_landmarks}")
#                 # use the received landmark position data to create a Response back to the client
#                 landmarks_df = process_raw_record(data)
#                 csv_file_path = "live_stream_test.csv"
#                 landmarks_df.to_csv(csv_file_path, mode='a', header=not pd.io.common.file_exists(csv_file_path), index=False)
#             except json.JSONDecodeError as e:
#                 print(f"Failed to parse JSON: {e}")

#     except websockets.exceptions.ConnectionClosed:
#         print("Client disconnected")

# Start the WebSocket server
# async def start_server():
#     ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#     #ssl_context.load_cert_chain(certfile="./cert.pem", keyfile="./key.pem")
#     async with serve(handle_client, "", 8001):
#         print("Starting...")
#         await asyncio.get_running_loop().create_future()  # run forever

#asyncio.run(start_server())
async def main():
    exercise_type = ExerciseType.ExerciseType.SQUATS  # Replace with the desired exercise type
    session = ExerciseSession.ExerciseSession(exercise_type=exercise_type)
    session_task = asyncio.create_task(session.start())  # Start the session asynchronously

    # Wait for 5 seconds for calibration
    await asyncio.sleep(5) 
    session.end_calibration() # TODO: Send a signal to the backend signalling the completion of the calibration
    print(session.calibration_max)
    print("Session calibrated.")
    print("Starting exercise")
    # TODO: Get a signal from the backend that terminates the session properly
    await asyncio.sleep(10)
    rep_count = await session.end()
    
    #print(session.exercise_data)
    #print()
    print("Rep count: {}".format(rep_count)) # TODO: Send this data to the backend

asyncio.run(main())
