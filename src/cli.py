#!/usr/bin/python3
import sys
import os
import subprocess
import time
from cmd import Cmd
from console.modules.inetsim import INetSim
from console.modules.config import ConfigParser

class Terminal(Cmd):
    intro = "MalWiFiCent Cli.    Type help or ? to list commands.\n"
    prompt = "=> "

    def __init__(self):
        super().__init__()
        # /var/log/inetsim
        self.net = INetSim()


    def do_exit(self, args):
        """ Stops INetSims and exits the command prompt """
        print("[*] Stopping services...")
        self.net.stop()
        print("Goodbye!")
        exit()
    
    
    def do_conf(self, args):
        """ INetSim Configuration
            test: Run test
        """
        if args == "test":
            ConfigParser("inetsim.conf", test=True).write_config()
        
        elif args == "view":
            parser = ConfigParser("inetsim.conf")
            #val = parser.read("start_service")
            val = parser.read("dns_bind_port")
            print(val)

    
    def do_inet(self, args):
        """ INetSim commands:
            start: Will start INetSim
            stop: Will stop INetSim
            log_path: Directory to store logs in

        Debugging commands:
            count: Prints a count of all INetSim processes
            pread: Read text from INetSim stdout (Will probably hang the terminal)
            fkill: Force kill all INetSim processes
        """
        if args == "start":
            self.net.start("/home/molly/scripts/log")
            # Allow it to startup...
            time.sleep(2)
            print(self.net.p_read())

        elif args == "stop":
            self.net.stop()
        # elif args == "log_path":
        #     new_path = input("Path: ")
        #     if self.net.check_log_path(new_path):
        #         print(f"[+] log-dir and report-dir set to {new_path}")
        elif args == "count":
            print(str(self.net.proc_count()))
        elif args == "pread":
            print(self.net.p_read())
        elif args == "fkill":
            self.net.force_kill()

term = Terminal()
term.cmdloop()