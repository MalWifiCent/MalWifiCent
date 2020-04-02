#!/usr/bin/python3
import os
import time
from functools import wraps
from flask import request, render_template, session, flash, redirect, url_for, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from console import *
from console.modules.network import get_interfaces
from console.modules.network import ip_addresses
from console.modules.process import Process
from console.modules.inetsim import INetSim
from console.modules.tcpdump import Tcpdump 
from console.modules.config import ConfigParser

inet = INetSim()
tcpd = Tcpdump()
config_whitelist = {
    "service_bind_address": "IPv4",
    "dns_default_ip": "IPv4",
    "http_bind_port": "PORT",
    "https_bind_port": "PORT",
    "http_default_fakefile": r'^[\w. _/-]{2,100}',
    "start_service": "BOOL"
}
config = ConfigParser(CONFIG_PATH, config_whitelist)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id", None) is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_files(dir_path):
    """ Loads a list that contains tuples with filename and file size
    from every file in  the directory.
    """
    files = os.listdir(dir_path)
    files_list = []
    files_list.extend([(file, os.path.getsize(os.path.join(dir_path, file)) / 1024.0) for file in files])
    return files_list

@app.context_processor
def statuses():
    """
    This gives inet_status and tcpd_status to every page without specifying
    them inside render_template. It sets the inet and tcpd status used
    in the header.html file.
    """
    return dict(
        registration_status = DATABASE,
        inet_status = inet.status(),
        tpcd_status = [tcpd.status(), tcpd.interface],
        network = ip_addresses()
    )


@app.route("/live", methods=["GET", "POST"])
@login_required
def live():
    if request.method == "POST":
        outdir = request.form.get("outdir", "")
        event = request.form.get("event", "").lower()

        if not (outdir and event):
            flash("Log path or command is missing", "warning")
            return redirect(url_for("about"))

        # Handle events
        if event == "start":
            config.copy_config()
            if inet.status():
                flash("INetSim is already running", "info")
                return redirect(url_for("live"))
            
            # Start inetsim, if successful:
            # Read inetsim's stdout and start tcpdump
            if not inet.start(outdir):
                # Inetsim did not start, likely because of errors with inputs
                flash("Invalid log path. Directory must be within /home/ or /var/log/, and the directory must exist.")
        elif event == "stop":
            inet.stop()
            
            ##stdout += inet.p_read()

    config_items = config.read_list(config_whitelist.keys())

    # Get Network Interfaces. Returned as dict_keys() so convert to list
    # then reverse the list so it is more likely that some other interface
    # than LO is selected as default.
    interfaces = list(get_interfaces())[::-1]
    stdout = sorted(inet.get_stdout() + tcpd.get_stdout())
    dir_count = len([name for name in os.listdir(CAP_DIR) if os.path.isfile(f"{CAP_DIR}/{name}")])
    return render_template("control.html", 
        stdout="".join(stdout), 
        logpath=LOG_PATH, 
        inetconfig=config_items,
        services=config.services,
        interfaces=interfaces,
        cap_dir=f"{CAP_DIR}/capture{dir_count}.cap")


@app.route("/capture", methods=["POST"])
@login_required
def capture():
    if request.method == "POST":
        cap_event = request.form.get("cap_event", "").lower()

        if cap_event == "start":
            # If tcpdump is already running, skip starting it
            if tcpd.status():
                flash("Tcpdump is already running", "info")
                return redirect(url_for("live"))
            
            # Get interface and capture save path
            IF = request.form.get("interface", "")
            c_dir = request.form.get("cap_dir", "")
            
            # Start tcpdump
            tcpd.start(IF, c_dir)

        elif cap_event == "stop":
            if tcpd.status():
                tcpd.stop()
    return redirect(url_for("live"))


@app.route("/files", methods=["GET"])
@login_required
def files():
    log_files = get_files(LOG_PATH)
    cap_files = get_files(CAP_DIR)

    return render_template("download.html", log_files=log_files, cap_files=cap_files)

@app.route("/download/<dir>/<path:filename>", methods=["GET"])
@login_required
def download(dir, filename):
    if dir == "log":
        return send_from_directory(directory=LOG_PATH, filename=filename)
    elif dir == "capture":
        return send_from_directory(directory=CAP_DIR, filename=filename)


@app.route("/view/<path:filename>", methods=["GET"])
@login_required
def view(filename):
    try:
        filename = secure_filename(filename)
        text = open(f"{LOG_PATH}/{filename}", "r")
        content = text.read()
        text.close()
    except IOError:
        content = "File does not exist."
    return render_template("view.html", text=content, name=filename)


@app.route("/update_config", methods=["POST"])
@login_required
def update_config():
    """
    Handle POST data to update inetsim config
    """
    if request.method == "POST":
        status, error = config.validate_input(request.form, config_whitelist)
    return redirect(url_for("live"))


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if not (username and password):
            flash("Username or Password cannot be empty.", "warning")
            return redirect(url_for("login"))

        user = ""
        # Check if user exists
        user = db.sql_query("SELECT id, password FROM users WHERE username = ?", 
            [username], one=True)
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid username or password.", "danger")
        else:            
            session["user_id"] = user["id"]
            return redirect(url_for("about"))
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if not REGISTRATION:
        flash("Registration is currently disabled.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if not (username and password):
            flash("Username or Password cannot be empty.")
            return redirect(url_for("signup"))
        
        # No error checking etc...
        if db.insertUser(username, password):
            return redirect(url_for("login"))
        else:
            flash("Username already exists.", "danger")
    return render_template("registration.html")


@app.route("/changepwd", methods=["GET", "POST"])
@login_required
def changepwd():
    if request.method == "POST":
        current_pwd = request.form.get("current-password", "")
        new_pwd = request.form.get("password", "")
        new_pwd2 = request.form.get("password2", "")
    
        # Check if new password is the same as the retyped new password
        if not (new_pwd == new_pwd2):
            flash("Passwords doesn't match.")
            return redirect(url_for("changepwd"))
        
        # Get user info
        user = db.sql_query("SELECT username, password FROM users WHERE id = ?",
            [session["user_id"]], one=True)
        
        # Check if the given password matches the current user password
        if not user or not check_password_hash(user["password"], current_pwd):
            flash("Wrong password supplied.", "danger")
            return redirect(url_for("changepwd"))
        
        # Update database with new password
        db.sql_insert("UPDATE users SET password = ? WHERE username = ?",
            [generate_password_hash(new_pwd), user['username']])

        # Inform user
        flash("Password changed", "info")
        return redirect(url_for("changepwd"))
    return render_template("updatepwd.html")


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")
