from __init__ import create_app, socketio

# Get app instance
app = create_app(debug=True)

# Run app through socketio
socketio.run(app, host="0.0.0.0", port=5000)
