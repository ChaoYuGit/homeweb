import json
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import request, redirect, url_for, session as flask_session

from utils.db import create_session, get_session, delete_session, cleanup_sessions

CONFIG_PATH = "config.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = flask_session.get("session_token")
        if not token or not get_session(token):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def authenticate(username, password):
    config = load_config()
    return username == config["username"] and password == config["password"]


def create_user_session():
    cleanup_sessions()
    config = load_config()
    token = str(uuid.uuid4())
    expires_at = (datetime.now() + timedelta(hours=config["session_lifetime_hours"])).isoformat()
    create_session(token, expires_at)
    flask_session["session_token"] = token


def logout_user():
    token = flask_session.pop("session_token", None)
    if token:
        delete_session(token)
