import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
import logging

csrf = CSRFProtect()
app = Flask(__name__)
csrf.init_app(app)
app.secret_key = b"changemeGdfgfdR435"
logging.basicConfig(level=logging.DEBUG)

app.config.update(
    # Currently not using HTTPS, so set to False
    SESSION_COOKIE_SECURE = False,
    SESSION_COOKIE_HTTPONLY = True,
    SESSION_COOKIE_SAMESITE = "Lax",
)

script_path = os.path.dirname(os.path.abspath(__file__))
CWD = os.path.normpath(script_path + os.sep + os.pardir)
LOG_PATH = f"{CWD}/logs"
CAP_DIR = f"{CWD}/caps"
CONFIG_PATH = f"{CWD}/config/inetsim.conf"
DATABASE = "database.db"

def create_path(paths:list):
    """
    Create path if it does not exist
    """
    for path in paths:
        if not os.path.exists(path):
            logging.info(f"[INFO] Creating path: '{path}'")
            os.makedirs(path)

create_path([LOG_PATH, CAP_DIR])

# Disable registration
REGISTRATION = False

from console import db, views
