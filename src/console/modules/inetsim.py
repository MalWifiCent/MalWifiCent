#!/usr/bin/python3
import os
from console.modules.process import Process
from werkzeug.utils import secure_filename
from pathlib import Path
from cmd import Cmd

class INetSim(Process):
    def __init__(self, program_path="/usr/bin/inetsim"):
        super().__init__(program_path)
        self.inetsim = program_path

        if os.geteuid() != 0:
            exit("This script must be run as root.")

        if not os.path.isfile(program_path):
            raise OSError(f"Cannot find inetsim in {self.inetsim}")

    
    def start(self, outdir:str):
        """
        Function to start the INetSim process.
        Override the start method to handle arguments.

        Args:
            outdir: (str) Path to the directory where the inetsim logs should be stored.
        Returns:
            bool: True if outdir got validated successfully
        """
        # Whitelist for allowed directories
        whitelist = ["/home/", "/var/log/"]
        outdir = self.validate_path(outdir, whitelist)
        if outdir:
            args = ["--log-dir", outdir, "--report-dir", outdir]
            Process.start(self, args)
            return True
        else:
            return False

