from flask import Flask
from sockets import socketio
import main

def create_app(debug=False):
    global app
    # Create app instance
    app = Flask(__name__)
    app.debug = debug
    app.secret_key = "secret key"
    # Disable file caching
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    # Use all routes defined in the main bluepring
    app.register_blueprint(main.main)
    # Enable socketio
    socketio.init_app(app)
    return app
