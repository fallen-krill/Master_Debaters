# Using code from https://www.geeksforgeeks.org/python/flask-web-sockets/ as starter code

from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import os
import random

class Room():
    def __init__(self, room_id):
        self.debaters = [room_id]
        self.spectators = []
        self.room_id = room_id # first person's id determines room ID
        self.prompt = "[prompt]"


# taken from task4-exploit.py from CPSC 525 F25 with Dr. Federl -----------------
DEBUG = os.environ.get("DEBUG", "0").lower() in ["1", "y", "yes", "true", "on"]
# -------------------------------------------------------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

socketio = SocketIO(app)


# Dictionary to store users and their assigned rooms
rooms = {} # store room objects by room id
user_room = {} # store the room id the user is currently in, by username
usernames = {} # store username by user id

@app.route('/queue')
def queue():
    image = "static/debate.png"
    return render_template('debate.html', imageurl = image, prompttext="abcd")
    
@app.route('/')
def index():
    image = "static/logo.png"
    return render_template('index.html', imageurl = image)

# Handle new user joining
@socketio.on('join')
def handle_join(username):
    usernames[request.sid] = username  # Store username by session ID

    print(f"Debug={DEBUG}")
    if DEBUG:
        print(f"\n\nUsername: {username}, request.sid: {request.sid}\n\n")
    room_assigned = None
    for room in rooms.values():
        if DEBUG:
            print(f"\n\n{room.room_id}'s room has {len(room.debaters)} people.\n\n")
        if len(room.debaters) == 1:

            room_assigned = room # add this user to list of debaters
            join_room(room_assigned.room_id)
            room.debaters.append(username)
            rooms[room_assigned.room_id] = room_assigned
            user_room[username] = room_assigned.room_id

            if DEBUG:
                print(f"\n\n{username} joining existing room ({room_assigned.room_id}).\n\n")

            break
            
    if room_assigned is None: # if there is nobody waiting for a match
        room_assigned = Room(username) # create new room and make this user the first debater in it
        rooms[username] = room_assigned
        join_room(username)
        user_room[username] = username
        if DEBUG:
                print(f"\n\n{username} joining new room ({username}).\n\n")

    send(f"{username} joined the chat", to=room_assigned.room_id)

# Handle user messages
@socketio.on('message')
def handle_message(data):
    username = usernames.get(request.sid, "Anonymous")  # Get the user's name
    room_id = user_room[username]
    send(f"{username}: {data}", to=room_id)  # Send to everyone

# Handle disconnects
@socketio.on('disconnect')
def handle_disconnect(data):
    username = usernames.pop(request.sid, "Anonymous")
    
    room_id = user_room.get(username, None)

    if room_id != None:
        
        send(f"{username} left the chat", to=room_id)

        if DEBUG:
            print(f"{username} left the chat")
        
            rooms[room_id].debaters.remove(username)
            if len(rooms[room_id].debaters == 0):
                del rooms[room_id]
    

if __name__ == '__main__':
    socketio.run(app, debug=True)
