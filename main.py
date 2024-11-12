import asyncio
import websockets
import json
import ssl

from websockets.asyncio.server import serve

IP = "192.168.0.170"

async def handle_client(websocket):
    client_ip = websocket.remote_address  # Get client IP and port info
    print(f"Client connected: {client_ip}")
    try:
        while True:
            # Wait for incoming messages from the client
            message = await websocket.recv()
            # Parse the received message as JSON
            try:
                data = json.loads(message)  # Convert the message to a Python dictionary
                print(f"Received message as JSON: {data}")

                # Access specific fields from the parsed JSON
                inference_time = data.get("inferenceTime", None)
                pose_landmarks = data.get("results", None)
                if not inference_time or not pose_landmarks:
                    raise Exception(f"Invalid data received! inference time: {inference_time}, results: {pose_landmarks}")
                # use the received landmark position data to create a Response back to the client
                
                with open("datafile.json") as dataFile:
                    dataFile.write_through(data)

            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

# Start the WebSocket server
async def start_server():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile="./cert.pem", keyfile="./key.pem")
    async with serve(handle_client, "", 8001):
        await asyncio.get_running_loop().create_future()  # run forever

asyncio.run(start_server())
