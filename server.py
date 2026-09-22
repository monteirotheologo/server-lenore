from flask import Flask
from flask_socketio import SocketIO, send

application = Flask(_name_)
socket = SocketIO(application)

@socketio.on("message")
def recieve_message(message):
  print(f"[msg] : {message}")
  print(f"the server recieved: '{message}'")
if __name__ == "__main__":
  socketio.run(app, host = "127.0.0.1", port=5555)
