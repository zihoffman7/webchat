from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector, random

# Connect to database
db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password",
  database="testing",
  auth_plugin="mysql_native_password"
)

cursor = db.cursor(buffered=True)

with open("schema.sql") as f:
    sql = f.read()
# DELETE MULTI=True, run, then rerun
cursor.execute(sql, multi=True)
db.commit()

# Check if username - password combo is valid
def check_username_password(user, password):
    cursor.execute("SELECT * FROM users WHERE username = '" + user + "';")
    user = cursor.fetchone()
    if user:
        if check_password_hash(user[2], password):
            return user

# Check if email - password combo is valid
def check_username_email(email, password):
    cursor.execute("SELECT * FROM users WHERE email = '" + email + "';")
    user = cursor.fetchone()
    if user:
        if check_password_hash(user[2], password):
            return user

# Detect if email already exists
def check_email(email):
    cursor.execute("SELECT * FROM users WHERE email = '" + email + "';")
    if cursor.fetchone():
        return True
    return False

# Check if username already exists
def check_username(name):
    cursor.execute("SELECT * FROM users WHERE username = '" + name + "';")
    if cursor.fetchone():
        return True
    return False

# Get username from id
def get_name(id):
    if not id == False:
        cursor.execute("SELECT username FROM users WHERE id = '" + id + "'")
        return cursor.fetchone()[0]
    return False

# Create an account from register data
def create_account(username, password, email, id):
    cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s)", (username, email, generate_password_hash(password), id))
    db.commit()

def change_password(id, password):
    cursor.execute("UPDATE users SET password = '" + generate_password_hash(password) + "' WHERE id = '" + id + "';")
    db.commit()

def change_email(id, email):
    cursor.execute("UPDATE users SET email = '" + email + "' WHERE id = '" + id + "';")
    db.commit()

# Deleting an account
def delete_account(id):
    # Remove all user data from tables
    cursor.execute("DELETE FROM users WHERE id = '" + id + "';")
    cursor.execute("DELETE FROM user_rooms WHERE userID = '" + id + "';")
    # Remove all rooms where the deleted account is the owner
    cursor.execute("SELECT code FROM rooms WHERE owner = '" + id + "';")
    rooms = cursor.fetchall()
    for room in rooms:
        delete_room(room[0])
    db.commit()

# Creating a room
def create_room(room_name, code, owner, color):
    # Create room in main room table
    cursor.execute("INSERT INTO rooms VALUES (%s, %s, %s)", (room_name, code, owner))
    # Join the room as owner
    cursor.execute("INSERT INTO user_rooms VALUES (%s, %s, %s, %s)", (get_name(owner), owner, code, room_name))
    # Holds all of the users in a room
    cursor.execute("CREATE TABLE " + code + "_users (user TEXT NOT NULL, id TEXT NOT NULL, color TEXT NOT NULL)")
    # Create chatlog
    cursor.execute("CREATE TABLE " + code + "_log (user TEXT NOT NULL, time TEXT NOT NULL, message TEXT NOT NULL, recipient TEXT NOT NULL, id TEXT NOT NULL)")
    # Add creator to room members
    cursor.execute("INSERT INTO " + code + "_users VALUES (%s, %s, %s)", (get_name(owner), owner, color))
    # Add starting messages
    cursor.execute("INSERT INTO " + code + "_log VALUES (%s, %s, %s, %s, %s)", ("server", " ", "This is the beginning of " + room_name, "all", " "))
    db.commit()

# Join a room if applicable
def join_room(name, id, code, color):
    # Check if room code is valid
    cursor.execute("SELECT * FROM rooms WHERE code = '" + code + "';")
    if not cursor.fetchone():
        return "Room code " + code + " doesn't exist"
    # Check if user is already in the selected room
    cursor.execute("SELECT roomID FROM user_rooms WHERE userID = '" + id + "';")
    if code in [i[0] for i in cursor.fetchall()]:
        return "You are already in this room"
    # Retrive name from new room
    cursor.execute("SELECT name FROM rooms WHERE code = '" + code + "';")
    room_name = cursor.fetchone()[0]
    # Double check that room actually exists
    if room_name:
        # Join room
        cursor.execute("INSERT INTO user_rooms VALUES (%s, %s, %s, %s)", (name, id, code, room_name))
        cursor.execute("INSERT INTO " + code + "_users VALUES (%s, %s, %s)", (name, id, color))
        db.commit()
        return "Room " + room_name + " successfully joined"
    else:
        return "Room " + code + " does not exist"

# Delete room from room code
def delete_room(code):
    # Invalidate room code and delete all room data
    cursor.execute("DELETE FROM rooms WHERE code = '" + code + "';")
    # Disable all users from joining the room
    cursor.execute("DELETE FROM user_rooms WHERE roomID = '" + code + "';")
    # Delete chat log and user data table
    cursor.execute("DROP TABLE " + code + "_users;")
    cursor.execute("DROP TABLE " + code + "_log;")
    db.commit()

# Delete user from a room
def leave_room(id, code):
    cursor.execute("DELETE FROM user_rooms WHERE userID = '" + id + "' AND roomID = '" + code + "';")
    cursor.execute("DELETE FROM " + code + "_users WHERE id = '" + id + "';")
    db.commit()

# Retrive the name and code of all rooms a user id is part of
def get_rooms(id):
    cursor.execute("SELECT * FROM user_rooms WHERE userID = '" + id + "';")
    data = []
    for i in [[i[3], i[2]] for i in cursor.fetchall()]:
        cursor.execute("SELECT owner FROM rooms WHERE code = '" + i[1] + "';")
        data.append([i[0], i[1]])
    return data

# Retrive every room code
def get_codes():
    cursor.execute("SELECT code FROM rooms;")
    return cursor.fetchall()

# Retrives all room codesassociated with a certain user id
def get_my_codes(id):
    cursor.execute("SELECT roomID FROM user_rooms WHERE userID = '" + id + "';")
    return cursor.fetchall()

# Check if user id is owner of the given room code
def is_owner(id, code):
    cursor.execute("SELECT * FROM rooms WHERE owner = '" + id + "' AND code = '" + code + "';")
    if cursor.fetchone():
        return True
    return False

# Get the name of all users in a room + their color
# If id is given, retrive all users except for the one associated with id
def get_users(code, id=False):
    if id == False:
        cursor.execute("SELECT * FROM " + code + "_users;")
        return [[i[0], i[2]] for i in cursor.fetchall()]
    cursor.execute("SELECT * FROM " + code + "_users WHERE NOT id = '" + id + "';")
    return [[i[0], i[2]] for i in cursor.fetchall()]

# Remove user from a room
def remove_user(name, code):
    cursor.execute("DELETE FROM " + code + "_users WHERE user = '" + name + "';")
    cursor.execute("DELETE FROM user_rooms WHERE username = '" + name + "' AND roomID = '" + code + "';")
    db.commit()

# Get user id from username and room code
def get_id(name, code):
    cursor.execute("SELECT userID FROM user_rooms WHERE username = '" + name + "' AND roomID = '" + code + "';")
    return cursor.fetchone()

# Retrive user id associated with an email
def get_id_from_email(email):
    cursor.execute("SELECT id FROM users WHERE email = '" + email + "';")
    try:
        return cursor.fetchone()[0]
    except TypeError:
        return False

# Get room name from join code
def get_room_name(code):
    cursor.execute("SELECT name FROM rooms WHERE code = '" + code + "';")
    return cursor.fetchone()[0]

# Insert message into chatlog table
def log_message(code, user, time, message, id, recipient="all"):
    cursor.execute("INSERT INTO " + code + "_log VALUES (%s, %s, %s, %s, %s)", (user, time, message, recipient, id))
    db.commit()
    # Ensure that database isn't too large
    check_rows(code + "_log")

# Retrive all messages from chatlog which were sent to a certain user id
def get_messages(code, id):
    cursor.execute("SELECT * FROM " + code + "_log WHERE recipient = 'all' OR recipient = '" + id + "';")
    return cursor.fetchall()

# Retrieve color associated with id in a room
def get_color(code, id):
    cursor.execute("SELECT color FROM " + code + "_users WHERE id = '" + id +"';")
    try:
        return cursor.fetchone()[0]
    # If person is no longer in room, use default color of darkslategray
    except TypeError:
        return "darkslategray"

# Ensure that no chatlog table has more than 250 messages stored
def check_rows(table):
    # Retrieve row count
    cursor.execute("SELECT COUNT(*) FROM " + table + ";")
    rows = cursor.fetchone()[0]
    if rows > 250:
        # Delete 50 rows if rowcount is above 250
        rows_to_delete = 50
        cursor.execute("DELETE FROM " + table + " LIMIT " + str(rows_to_delete))
        db.commit()

# Allow the user to change their color in a room
def change_color(code, id, color):
    cursor.execute("UPDATE " + code + "_users SET color = '" + color + "' WHERE id = '" + id + "';")
    db.commit()
