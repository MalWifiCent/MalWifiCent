#!/usr/bin/python3
import os
import signal
import time
import subprocess
import psutil
import datetime
from console import app# - For doing app.logger
from fcntl import fcntl, F_GETFL, F_SETFL
from subprocess import Popen, PIPE
from werkzeug.utils import secure_filename
from pathlib import Path

class Process(object):
    def __init__(self, program_path: str):
        self.program_path = program_path
        self.basename = os.path.basename(self.program_path)
        self.proc = None
        self.running = False
        self.stdout = []

        if os.geteuid() != 0:
            exit("This script must be run as root.")
    
    def get_stdout(self):
        """
        Getter for self.stdout
        """
        return self.stdout

    def to_stdout(self, msg):
        """
        Appends messages to the self.stdout
        """
        d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stdout.append(f"[{d}] {msg}\n")

    def start(self, args):
        """
        Function to start a process

        Args:
            args: (list) A list containing the command line arguments for the program
                    to be started.
        """
        if not self.running and not self.status():
            self.proc = Popen(
                [
                    self.program_path,
                    *args
                ],
                stdout=PIPE,
                stdin=PIPE,
                start_new_session=True
            )
            # https://docs.python.org/3.7/library/fcntl.html
            # For O_NONBLOCK:
            # http://man7.org/linux/man-pages/man2/open.2.html
            # Get current stdout flags
            flags = fcntl(self.proc.stdout, F_GETFL)
            # Set new flags
            fcntl(self.proc.stdout, F_SETFL, flags | os.O_NONBLOCK)

            if self.proc.poll() is not None:
                app.logger.info(f"[INFO] Process died immediately. Returncode: {self.proc.Returncode}")
            self.running = True
            self.to_stdout(f"[INFO] {self.basename} started.")
            #print(self.p_read())
            app.logger.info(f"[INFO] {self.basename} started.")
    

    def stop(self):
        """
        Function to stop or kill a Process
        """
        if self.proc != None and self.proc.poll() == None:
            self.proc.stdin.close()
            # https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
            os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
            # Remove zombie processes (defunct state)
            self.proc.wait(timeout=4)
        elif self.status():
            app.logger.info(f"[INFO] Running force kill on {self.basename}")
            self.force_kill()
        self.running = False

        self.to_stdout(f"[INFO] {self.basename} stopped.")
        app.logger.info(f"[INFO] {self.basename} stopped.")


    def p_read(self):
        """ Read from stdout
        
        Returns:
            stdout: (str) The text from the process stdout.
        """
        stdout = ""
        time.sleep(2)
        while True:
            try:
                # Is process still alive?
                if self.proc.poll() == None:
                    # Read from process stdout
                    stdout += os.read(self.proc.stdout.fileno(), 1024).decode("utf-8")
                else:
                    # Process not alive, break loop
                    break
            except OSError:
                break
            except AttributeError:
                break
        return stdout


    def proc_count(self):
        """ Count processes
        
        Returns:
            Int: The number of processes running
        """
        # Did not work to fix the string inside the list in count, so 
        # doing it before
        arg = f"ps aux | grep {self.basename} | wc -l"
        count = subprocess.check_output(
            [arg], 
            shell=True
            ).decode("utf-8").strip()
        return int(count)


    def force_kill(self):
        """
        Force kill all processes. 
        This was needed when the process didn't stop correctly. 
        In cases such as crashes etc
        """
        count = self.proc_count()
        if count > 0:
            app.logger.info(f"[i] Killing {count} {self.basename} processes.")
            self.to_stdout(f"[INFO] Killing {count} {self.basename} processes.")
            os.system(f"pkill {self.basename}")


    def status(self):
        """
        This function will check if a process is already running in the background.
        https://thispointer.com/python-check-if-a-process-is-running-by-name-and-find-its-process-id-pid/

        Return:
            Bool: True if the process is running
        """
        for proc in psutil.process_iter():
            try:
                if self.basename.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False


    def validate_path(self, path:str, whitelist:list):
        """
        This function is used to validate and sanitize the log path when starting up
        INetSim.

        Args:
            path: (str) The path to validate
        Returns:
            path/None: None if path was invalid, returns the path otherwise
        """
        try:
            # Select root_path
            root_path = [item for item in whitelist if path.startswith(item)][0]
            # Sanitize path for path traversal
            sanitized_path = Path(root_path).joinpath(path).resolve().relative_to(root_path)
        except (ValueError, IndexError) as e:
            return None

        path = f"{root_path}{sanitized_path}"
        if os.path.isdir(path):
            return path
