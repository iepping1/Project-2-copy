import os
import time
import datetime

from flask import Flask, render_template, request, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# list of all channels
channels = {'general': []}

# Counter for all messages
counter = 0

# Object for general messages
def message(message, username, timestamp, message_id):
    new_message = {}
    new_message["message"] = message
    new_message["username"] = username
    new_message["timestamp"] = timestamp
    new_message["id"] = message_id

    return new_message

# Opening page is the only page
@app.route("/")
def index():
    channel_list = list(channels)
    return render_template("displaychannel.html", channel_list=channel_list)

# Room can be any random string, only exists server side, broadcast and room id

# Make a new channel
@socketio.on("create new channel")
def add_channel(channel_name):
    created_channel = channel_name["channel_name"]

    # Check if new channel name doesn't already exist.
    if created_channel in channels:
        emit("channel_exists", created_channel = created_channel, broadcast=False)

    # Emit new channel to server.
    else:
        first_message = message(
            "Hello, this is my Channel",
            "Admin",
            channel_name["timestamp"],
            -1,
        )

        channels[created_channel] = []
        channels[created_channel].append(first_message)
        print("the name of the channel still is", created_channel)
        emit("channel_created", created_channel, broadcast=True)
            

# Join new channel
@socketio.on("join_channel")
def join_channel(data):
    # leave_room(data["old_channel"])
    join_room(data["new_channel"])

    # new_user = data['username']
    # room = data["current_channel"]
    # print(new_user, room)

    # join_room(room)

    # # If user not in channel, add user to channel
    # if new_user not in channels[room]['users']:
    #     channels[room]['users'].append(new_user)

    # #channel_info = channels[room]

    # # Emit new message to server
    # emit("joined_channel", { "channels": channels },room=room)
    # print("step 5 completed")

# # Leave the channel
# @socketio.on('leave_channel')
# def leave_channel(data):
#     leave_room(data["old_channel"])
#     # Emit departure to channel
#     emit("left channel", {'channels': channels}, room=room)


@socketio.on("message")
def new_message(data):

    global counter
    new_message = message(data["message"], data["username"], data["timestamp"], counter)
    counter += 1

    current_channel, new_message["current_channel"] = (
        data["current_channel"],
        data["current_channel"],
    )

    # Add new message to message list.
    try:
        channels[current_channel].append(new_message)

        # Ensure channel doesnt have over 100 messages
        channels[current_channel] = channels[current_channel][-100:]

        emit("new_message", new_message, room=current_channel)
    except KeyError:
        socketio.emit("channel_deleted", "Channel does not exist.")


@app.route("/showmessages", methods=["POST"])
def showmessages():
    # Get stored messages.
    # try:
    channel = request.form.get("new_channel")
    messages = channels[channel]
    # Get General messages if channel does not exist.
    # except KeyError:
    #     channel = "General"
    #     messages = channels[channel]
    #     # Warn that channel does not exist.
    #     socketio.emit("channel_deleted", "Channel does not exist.")

    # Return list of posts.
    return jsonify(channel, messages)
    

@socketio.on("deletemessage")
def deletemessage(data):
    current_channel = data["current_channel"]
    message_id = int(data["id"])

    for i, message in enumerate(channels[current_channel]):
        if message["id"] == message_id:
            del channels[current_channel][i]

            emit("deleted_message", message_id, room=current_channel)
            break