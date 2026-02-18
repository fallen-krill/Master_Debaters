# Using code from https://www.geeksforgeeks.org/python/flask-web-sockets/ as starter code

import json
import os
import random

from dataclasses import dataclass, field

from flask import Flask, render_template, request
from flask_socketio import SocketIO, close_room, emit, join_room, send
from questions import TOPICS_FILENAME

DEFAULT_PROMPT = "[prompt]"
DEFAULT_USERNAME = "Anonymous"

# taken from task4-exploit.py from CPSC 525 F25 with Dr. Federl -----------------
DEBUG = os.environ.get("DEBUG", "0").lower() in ["1", "y", "yes", "true", "on"]
# -------------------------------------------------------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"

socketio = SocketIO(app)

prompts: list[str] = []

# Dictionary to store users and their assigned rooms
rooms = {}  # store room objects by room id
user_room = {}  # store the room id the user is currently in, by username
usernames = {}  # store username by user id

# (main doesn't run if you start server with flask run)
with open(TOPICS_FILENAME, "r") as f:
    prompts = json.load(f)

@dataclass
class Room:
    room_id: str = field()
    debaters: list = field(default_factory=list)
    spectators: list = field(default_factory=list)
    prompt: str = field(init=False, default=DEFAULT_PROMPT)
    chat_log: list[str] = field(init=False, default_factory=list)

    def new_prompt(self) -> None:
        self.prompt = random.choice(prompts)


@app.route("/debate")
def debate():
    return render_template("debate.html")


@app.route("/")
def index():
    image = "static/logo.png"
    return render_template("index.html", imageurl=image)


# Handle new user joining
@socketio.on("join")
def handle_join(username):
    usernames[request.sid] = username  # Store username by session ID

    room_assigned = None
    position = ""

    for room in rooms.values():
        if len(room.debaters) == 1:
            room_assigned = room  # add this user to list of debaters
            join_room(room_assigned.room_id)
            room.debaters.append(username)
            rooms[room_assigned.room_id] = room_assigned
            user_room[username] = room_assigned.room_id
            position = "No."
            break

    if room_assigned is None:  # if there is nobody waiting for a match
        position = "Yes."
        # create new room and make this user the first debater in it
        room_assigned = Room(username)
        rooms[username] = room_assigned
        room_assigned.new_prompt()
        join_room(username)
        user_room[username] = username

    # Runs regardless
    send(f"{username} joined the chat.", to=room_assigned.room_id)
    emit("prompt_update", room_assigned.prompt)  # trigger "prompt_update" event
    emit("position_update", position)


# Handle user messages
@socketio.on("message")
def handle_message(data):
    username = usernames.get(request.sid, DEFAULT_USERNAME)  # Get the user's name
    room_id = user_room[username]
    message = f"{username}: {data}"
    send(message, to=room_id)  # Send to everyone, event is "message"
    # rooms[user_room[username]].chat_log.append(message)


# Handle disconnects
@socketio.on("disconnect")
def handle_disconnect(data):
    username = usernames.pop(request.sid, DEFAULT_USERNAME)
    room_id = user_room.get(username)
    if room_id is not None:
        send(f"{username} left the chat. Please refresh the page.", to=room_id)
        close_room(room_id)
        del rooms[room_id]


if __name__ == "__main__":
    socketio.run(app, debug=True)
