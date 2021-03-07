from flask import redirect, url_for, render_template, request, session, Markup, Blueprint, send_from_directory
import uuid, string, random, json, re
from subprocess import call
import database as db

main = Blueprint("main", __name__)

# All colors that a user can choose from in a chat room
colors = [
    "#e0383e", "indianRed", "#d17e4d", "#f7821b", "#f5b342", "#dbd335",
    "darkGoldenrod", "olive", "#607d46", "#246b62", "green", "#62ba46",
    "#68ad7d", "#4dd18d", "#68ad92", "lightSeaGreen", "#56999c", "teal",
    "steelBlue", "#3399ff", "royalBlue", "#605ba3", "#8150c6", "mediumPurple",
    "#cf7fd4", "#b365b5", "#953d96", "#71268c"
]

@main.route("/", methods=["GET", "POST"])
def index():
    return redirect(url_for("main.dashboard"))

@main.route("/login", methods=["GET", "POST"])
def login():
    if not "user" in session:
        if request.method == "POST":
            # Get all form data
            username = request.form["username"]
            password = request.form["password"]
            # Check if username matches password
            data = db.check_username_password(re.sub("[^0-9a-zA-Z_]+", "", username.replace(" ", "_")), password)
            # If username isn't valid, check to see if it is their email
            if not data:
                data = db.check_username_email(username, password)
            # If user has correct credentials, initialize session and redirect
            if data:
                # Initialize session data
                session["user"] = data[0]
                session["id"] = data[3]
                return redirect(url_for("main.dashboard"))
            else:
                return render_template("login.html", flash="Account not found")
        else:
            return render_template("login.html")
    else:
        return redirect(url_for("main.dashboard"))

@main.route("/logout", methods=["GET", "POST"])
def logout():
    if "user" in session:
        # Remove session data
        session.pop("user", None)
        session.pop("id", None)
    return redirect(url_for("main.login"))

@main.route("/register", methods=["GET", "POST"])
def register():
    if not "user" in session:
        if request.method == "POST":
            # Remove any non-alphanumeric characters in username
            username = request.form["username"].replace(" ", "_")
            if not re.sub("[^0-9a-zA-Z_]+", "", username) == username:
                return render_template("register.html", flash="Please remove the special characters")
            # If confirmed password doesn't match password, notify user
            if not request.form["password"] == request.form["password2"]:
                return render_template("register.html", flash="Passwords don't match")
            # Get remaining account data
            password = request.form["password"]
            email = request.form["email"]
            # Ensure that user data doesn't already exist
            if db.check_username(username):
                return render_template("register.html", flash="A user with this name already exists")
            if db.check_email(email):
                return render_template("register.html", flash="Email taken")
            # If invalid email, notify user
            if not "@" in email or not "." in email:
                return render_template("register.html", flash="Invalid email")
            # Create random user id
            id = str(uuid.uuid4())
            # Create the account
            db.create_account(username, password, email, id)
            # Initialize session data
            session["user"] = username
            session["id"] = id
            return redirect(url_for("main.dashboard"))
        return render_template("register.html")
    else:
        return redirect(url_for("main.dashboard"))

@main.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" in session:
        if request.method == "POST":
            if "joinRoom" in request.form:
                # Join a room
                message = db.join_room(session["user"], session["id"], request.form["joinRoom"], random.choice(colors))
                return render_template("dashboard.html", name=session["user"], flash=Markup(message), rooms=db.get_rooms(session["id"]))
            if "createRoom" in request.form:
                # Remove all html tags from room name
                room_name = re.compile(r"<.*?>").sub("", request.form["cRoom"])
                # If room name isn't a blank string, allow creation
                if (len(room_name.strip()) > 0):
                    # Create room and generate join code
                    join_code = "".join(random.choice(string.ascii_uppercase + string.digits) for i in range(8))
                    db.create_room(room_name, join_code, session["id"], random.choice(colors))
                    return render_template("dashboard.html", name=session["user"], flash=room_name + " created", rooms=db.get_rooms(session["id"]), word="for")
                return render_template("dashboard.html", name=session["user"], flash="Invalid room name", rooms=db.get_rooms(session["id"]))
        else:
            return render_template("dashboard.html", name=session["user"], rooms=db.get_rooms(session["id"]))
    else:
        return redirect(url_for("main.login"))

@main.route("/settings", methods=["GET", "POST"])
def settings():
    if "user" in session:
        if request.method == "POST":
            if "changePassword" in request.form:
                password = request.form["password"]
                # If both passwords don't match, notify user
                if not request.form["password"] == request.form["password2"]:
                    return render_template("settings.html", name=session["user"], flash="Enter a valid password", rooms=db.get_rooms(session["id"]))
                # Execute the change
                db.change_password(session["id"], password)
                return render_template("settings.html", name=session["user"], flash="Password successfully changed", rooms=db.get_rooms(session["id"]))
            if "changeEmail" in request.form:
                email = request.form["email"]
                # If email already exists, notify user
                if db.check_email(email):
                    return render_template("settings.html", name=session["user"], flash="Email already exists", rooms=db.get_rooms(session["id"]))
                # If new email doesn't already exist and is valid, update it
                elif "@" in email and "." in email:
                    db.change_email(session["id"], email)
                    return render_template("settings.html", name=session["user"], flash="Email successfully changed", rooms=db.get_rooms(session["id"]))
                return render_template("settings.html", name=session["user"], flash="Invalid email", rooms=db.get_rooms(session["id"]))
            if "deleteAccount" in request.form:
                # Remove user's file directory if account is deleted
                call(["php", "dirs.php", json.dumps({"task" : "delete dir", "user" : session["id"]})])
                # Remove their data from the database
                db.delete_account(session["id"])
                return redirect(url_for("main.logout"))
        else:
            return render_template("settings.html", name=session["user"], rooms=db.get_rooms(session["id"]))
    else:
        return redirect(url_for("main.login"))

@main.route("/chat/<chatcode>", methods=["POST", "GET"])
def chat(chatcode):
    if "user" in session:
        if chatcode in [i[0] for i in db.get_codes()]:
            # If they are requesting a room they aren't in, join the room
            if not chatcode in db.get_my_codes(session["id"]):
                db.join_room(session["user"], session["id"], chatcode, random.choice(colors))
            session["room"] = chatcode
            return render_template("chat.html", name=session["user"], room=db.get_room_name(chatcode), status=db.is_owner(session["id"], chatcode), rooms=db.get_rooms(session["id"]), code=chatcode, people=["@" + i[0] for i in db.get_users(chatcode, session["id"])])
        else:
            return redirect(url_for("main.dashboard"))
    else:
        return redirect(url_for("main.login"))

@main.route("/chat/<chatcode>/leave", methods=["POST", "GET"])
def leave_room(chatcode):
    if "user" in session:
        # Remove user from the selected room
        db.leave_room(session["id"], chatcode)
        return redirect(url_for("main.dashboard"))
    else:
        return redirect(url_for("main.login"))

@main.route("/chat/<chatcode>/settings", methods=["POST", "GET"])
def chat_settings(chatcode):
    if "user" in session:
        if request.method == "POST":
            # If user is owner, allow entry
            if db.is_owner(session["id"], chatcode):
                if "removeUser" in request.form:
                    # Get all users queried to remove
                    users = request.form.getlist("user")
                    # If no users are specified, notify client
                    if len(users) == 0:
                        return render_template("roomsettings.html", name=session["user"], flash=Markup("Select a user to remove"), people=db.get_users(chatcode, session["id"]), code=chatcode, room=db.get_room_name(chatcode), rooms=db.get_rooms(session["id"]))
                    # Remove each user selected by client
                    for user in users:
                        db.remove_user(user, chatcode)
                    # Send message to client that deletion was success
                    if len(users) == 1:
                        return render_template("roomsettings.html", name=session["user"], flash=Markup("1 user removed"), people=db.get_users(chatcode, session["id"]), code=chatcode, room=db.get_room_name(chatcode), rooms=db.get_rooms(session["id"]))
                    return render_template("roomsettings.html", name=session["user"], flash=Markup(str(len(users)) + " users removed"), people=db.get_users(chatcode, session["id"]), code=chatcode, room=db.get_room_name(chatcode), rooms=db.get_rooms(session["id"]))
                elif "deleteRoom" in request.form:
                    # Delete room if prompted
                    db.delete_room(chatcode)
                    return redirect(url_for("main.dashboard"))
            else:
                return redirect("/chat/" + chatcode)
        else:
            # If user is owner, allow entry
            if db.is_owner(session["id"], chatcode):
                return render_template("roomsettings.html", name=session["user"], people=db.get_users(chatcode, session["id"]), code=chatcode, room=db.get_room_name(chatcode), rooms=db.get_rooms(session["id"]))
            # Otherwise, redirect them to the chat
            else:
                return redirect("/chat/" + chatcode)
    else:
        return redirect(url_for("main.login"))

@main.route("/chat/<chatcode>/members", methods=["POST", "GET"])
def chat_members(chatcode):
    if "user" in session:
        # Ensure the user isn't looking at a room they aren't in
        if chatcode in [i[0] for i in db.get_my_codes(session["id"])]:
            # POST if user is changing their color
            if request.method == "POST":
                # If the color is valid, change it
                if request.form["color"] in colors:
                    # Update database with color change
                    db.change_color(chatcode, session["id"], request.form["color"])
                    return render_template("members.html", colors=colors, name=session["user"], flash="Color successfully changed", people=db.get_users(chatcode), room=db.get_room_name(chatcode), code=chatcode, rooms=db.get_rooms(session["id"]))
            return render_template("members.html", colors=colors, name=session["user"], people=db.get_users(chatcode), room=db.get_room_name(chatcode), code=chatcode, rooms=db.get_rooms(session["id"]))
        else:
            return redirect(url_for("main.dashboard"))
    else:
        return redirect(url_for("main.login"))

@main.route("/chat/uploads/users/<user>/<filename>")
def show_image(user, filename):
    return send_from_directory("uploads/users/" + user, filename)

def upload(data):
    if data[0]:
        # Ensure the user has a file directory
        call(["php", "dirs.php", json.dumps({"task" : "create dir", "user" : session["id"]})])
        # Generate random file name
        filepath = "uploads/users/" + session["id"] + "/" + str(uuid.uuid4()) + "." + data[1]
        # Write file
        with open(filepath, "wb") as f:
            f.write(data[0])
        # Return location of file
        return filepath
