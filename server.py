import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

# Create a Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI()

# Add CORS middleware to allow requests from your Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach Socket.IO server to FastAPI
app = socketio.ASGIApp(sio, other_asgi_app=app)

# Store the session ID of the client that sends the 'Chat connected' message
connected_client_sid = None

@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

@sio.event
async def message(sid, data):
    global connected_client_sid
    print(f"Message from {sid}: {data}")
    
    if data == "Chat connected":
        connected_client_sid = sid  # Store the session ID of the connected client
        await sio.send("Server acknowledges connection", to=sid)  # Send acknowledgment to the connected client
    else:
        await sio.send(f"Server received: {data}", to=sid)  # Respond to the client

# Function to send messages from the server terminal to the specific client
async def send_terminal_messages():
    global connected_client_sid
    while True:
        if connected_client_sid:
            message = input("Enter a message to send to the connected client: ")
            await sio.send(message, to=connected_client_sid)  # Send the message only to the stored client
        else:
            print("No client has connected yet...")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # Ensure the send_terminal_messages runs in the background
    loop.create_task(send_terminal_messages())

    # Run the FastAPI app within the existing loop
    uvicorn.run(app, host="0.0.0.0", port=8000, loop=loop)
