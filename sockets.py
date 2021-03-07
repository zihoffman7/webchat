from flask_socketio import SocketIO, emit, join_room, leave_room
from subprocess import call
from main import session, upload
import database as db
import datetime, json

# The file types that will preview on the page
# Other file types will show a download link instead
file_types = {
    "image" : ["png", "jpg", "gif", "jpeg"],
    "audio" : ["mp3", "ogg", "wav"],
    "video" : ["mov", "mp4"],
    "other" : ["pdf", "cpp", "py", "txt", "js", "css", "json", "xml", "java", "h", "c"]
}

# Gets formatted string time
def now():
    return str(datetime.datetime.now().strftime("%a, %b %d, %Y, %I:%M %p"))

# Get socketio instance
socketio = SocketIO()

@socketio.on("connect")
def connect():
    join_room(session["room"])
    # Join room associated with session id for private messages
    join_room(session["id"])
    # Get the last 75 messages addressed to the user
    data = db.get_messages(session["room"], session["id"])
    socketio.emit("clear", room=session["id"])
    messages = []
    for i in data[-100:]:
        if i[3] == "all":
            messages.append([i[0], i[1], i[2], db.get_color(session["room"], i[4])]);
        else:
            messages.append([i[0], i[1], i[2], db.get_color(session["room"], i[4]), "private"])
    # Send the messages to client
    socketio.emit("mass message", messages, room=session["id"])

@socketio.on("disconnect")
def disconnect():
    try:
        leave_room(session["room"])
        session.pop("room", None)
    except KeyError:
        pass
    leave_room(session["id"])

@socketio.on("message")
def message(data):
    # If private message detected, do private message
    if " @" in data or "@" == data[0]:
        # Get the usernames of all recipients specified
        sendee = [i for i in list(data.split(" ")) if not i == ""]
        # Send message to sender
        socketio.emit("message", [session["user"], now(), data, db.get_color(session["room"], session["id"]), "private"], broadcast=True, room=session["id"])
        db.log_message(session["room"], session["user"], now(), data, session["id"], session["id"])
        sent_to = []
        # Iterate through recipients and attempt to send message to them
        for i in sendee:
            i = i.replace(",", "").replace(".", "")
            if i[0]:
                if i[0] == "@":
                    # Send message privately to all specified users
                    if i[1:] not in sent_to and not i[1:] == session["user"]:
                        sent_to.append(i[1:])
                        # If user exists, send private message and log it
                        if db.get_id(i[1:], session["room"]):
                            socketio.emit("message", [session["user"], now(), data, db.get_color(session["room"], session["id"]), "private"], broadcast=True, room=db.get_id(i[1:], session["room"])[0])
                            db.log_message(session["room"], session["user"], now(), data, session["id"], db.get_id(i[1:], session["room"])[0])
                        # If selected recipient doesn't exist, notify sender
                        else:
                            socketio.emit("message", ["server", now(), "User " + i[1:] + " doesn't exist", "server", "private"], broadcast=True, room=session["id"])
    # If message isn't a private message, send it normally
    else:
        db.log_message(session["room"], session["user"], now(), data, session["id"])
        socketio.emit("message", [session["user"], now(), data, db.get_color(session["room"], session["id"])], broadcast=True, room=session["room"])

@socketio.on("file")
def file(data):
    # Upload file to server
    file = upload(data)
    # Send correct html depending on the type of file
    if data[1].lower() in file_types["image"]:
        db.log_message(session["room"], session["user"], now(), "<img src='" + file + "' alt='file deleted' class='chatimg'>", session["id"])
        socketio.emit("message", [session["user"], now(), "<img src='" + file + "' alt='file deleted' class='chatimg'>", db.get_color(session["room"], session["id"])], broadcast=True, room=session["room"])
    elif data[1].lower() in file_types["audio"]:
        db.log_message(session["room"], session["user"], now(), data[2] + "<br /><br /><audio controls><source src=" + file + ">Your browser does not support the audio element</audio>", session["id"])
        socketio.emit("message", [session["user"], now(), data[2] + "<br /><br /><audio controls><source src=" + file + ">Your browser does not support the audio element</audio>", db.get_color(session["room"], session["id"])], broadcast=True, room=session["room"])
    elif data[1].lower() in file_types["video"]:
        db.log_message(session["room"], session["user"], now(), data[2] + "<br /><br /><video controls><source src=" + file + ">Your browser does not support the video element</video>", session["id"])
        socketio.emit("message", [session["user"], now(), data[2] + "<br /><br /><video controls><source src=" + file + ">Your browser does not support the video element</video><br />", db.get_color(session["room"], session["id"])], broadcast=True, room=session["room"])
    elif data[1].lower() in file_types["other"]:
        db.log_message(session["room"], session["user"], now(), "<embed src='" + file + "'><br /><br /><a href='" + file + "' download='" + data[2] + "' alt='file deleted' class='download'><img src='/static/downloadIcon.png' height='12' id='downloadImg'>" + data[2] + "</a>", session["id"])
        socketio.emit("message", [session["user"], now(), "<embed src='" + file + "'><br /><br /><a href='" + file + "' download='" + data[2] + "' alt='file deleted' class='download'><img src='/static/downloadIcon.png' height='12' id='downloadImg'>" + data[2] + "</a>", db.get_color(session["room"], session["id"])], broadcast=True, room=session["room"])
    # If uploaded file can't be previewed, just send download link
    else:
        db.log_message(session["room"], session["user"], now(), "<a href='" + file + "' download='" + data[2] + "' alt='file deleted' class='download'><img src='/static/downloadIcon.png' height='12' id='downloadImg'>" + data[2] + "</a>", session["id"])
        socketio.emit("message", [session["user"], now(), "<a href='" + file + "' download='" + data[2] + "' alt='file deleted' class='download'><img src='/static/downloadIcon.png' height='12' id='downloadImg'>" + data[2] + "</a>", db.get_color(session["room"], session["id"])], broadcast=True, room=session["room"])
    # Ensure that the user hasn't exceeded their file storage limit
    call(["php", "dirs.php", json.dumps({"task" : "check filelimit", "user" : session["id"]})])
