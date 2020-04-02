#!/usr/bin/python3
import os
import psutil
from console.modules.process import Process
from werkzeug.utils import secure_filename
from pathlib import Path

class Tcpdump(Process):
    def __init__(self, program_path="/usr/sbin/tcpdump"):
        super().__init__(program_path)
        self.tcpdump = program_path
        self.interface = ""

        if os.geteuid() != 0:
            exit("This script must be run as root.")

        if not os.path.isfile(program_path):
            raise OSError(f"Cannot find inetsim in {self.inetsim}")


    def start(self, interface:str, cap_dir:str):
        """
        Function to start the Tcpdump process.
        Override the start method to handle arguments.

        Args:
            outdir: (str) Path to the directory where the tcpdump caps should be stored.
        Returns:
            bool: True if outdir got validated successfully
        """
        path, name = os.path.split(cap_dir)
        name = secure_filename(name)

        if not interface in self.get_interfaces():
            return False
        self.interface = interface

        whitelist = ["/home/"]
        outdir = self.validate_path(path, whitelist)
        if outdir:
            args = ["-i", interface, "-w", f"{path}/{name}"]
            Process.start(self, args)
            return True
        return False
    
    @staticmethod
    def get_interfaces():
        """
        This function returns all network interfaces.
        """
        return psutil.net_if_addrs().keys()
