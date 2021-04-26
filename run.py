from __init__ import create_app, socketio

# Get app instance
app = create_app(debug=True)

# Run app through socketio
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
