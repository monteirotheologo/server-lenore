from flask import Flask, request
from flask_socketio import SocketIO
from colorama import Fore, Style
import os
import sqlite3

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

IP = "0.0.0.0"
PORT = 443

app = Flask(__name__)
server = SocketIO(app, cors_allowed_origins="*")

colorAdmin = Fore.RED + Style.BRIGHT
colorUser = Fore.GREEN + Style.BRIGHT
r = Style.RESET_ALL

@server.on("connect")
def handle_connect():
    pass

@server.on("msg")
def new_message(data):
    username = data["username"]
    content = data["content"]

    create_message(username, content)

    server.emit("new_message", {
        "username": username,
        "content": content
    })

@server.on("load_messages")
def handle_load_messages():
    msgs = load_messages()
    print(">>> pedido recebido")
    return [

        {
            "username": username,
            "content": content
        }

        for username, content in msgs

    ]

@server.on("register")
def handle_register(data):
    username = data["username"]
    password = data["password"]

    if if_user_exists(username):
        return {
            "okay": False,
            "error": "Username already exists"
        }

    create_user(username, password)
    
    return {
        "okay": True
    }

@server.on("login")
def handle_login(data):
    username = data["username"]
    password = data["password"]

    if not if_user_exists(username):
        return {
            "okay": False,
            "error": "Username not exists"
        }
    if not if_password_match(username, password):
        return {
            "okay": False,
            "error": "Password not match"
        }
    return {
        "okay": True
    }

def init_db():
    conn = sqlite3.connect("database.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id_user INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        grade INTEGER NOT NULL
    )   
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id_messages INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username)
    )
    """)
    conn.commit()
    conn.close()

def if_user_exists(username):
    conn = sqlite3.connect("database.db")
    result = conn.execute("SELECT id_user FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return result is not None

def if_password_match(username, password):
    conn = sqlite3.connect("database.db")
    result = conn.execute("SELECT id_user FROM users WHERE username = ? AND password = ?", (username, password,)).fetchone()
    conn.close()
    return result is not None

def create_user(username, password):
    conn = sqlite3.connect("database.db")
    conn.execute("INSERT INTO users (username, password, grade) VALUES (?, ?, 0)", (username, password))
    conn.commit()
    conn.close()

def create_message(username, content):
    conn = sqlite3.connect("database.db")
    conn.execute("INSERT INTO messages (username, content) VALUES (?, ?)", (username, content))
    conn.commit()
    conn.close()

def load_messages():
    conn = sqlite3.connect("database.db")
    msg = conn.execute("SELECT username, content FROM messages")
    messages = msg.fetchall()
    conn.close()
    return messages

def show_messages():
    msg = load_messages()
    for info in msg:
        print(f"{colorUser}@{info[0]}{r} | {info[1]}")

if __name__ == "__main__":
    init_db()
    server.run(app, host=IP, port=PORT, allow_unsafe_werkzeug=True)
