#!/usr/bin/python3
import os
import sys
import subprocess
import time
import unittest
from cmd import Cmd
from modules.inetsim import INetSim

class TestServiceINetSim(unittest.TestCase):

    def test_service(self):
        """
        Test INetSims start and stop function
        """
        net = INetSim("dummy")
        net.start()
        time.sleep(1)
        count = net.proc_count()
        print(f"[*] Start count: {count}")
        self.assertTrue(count > 15)

        net.stop()
        count = net.proc_count()
        print(f"[*] Stop count: {count}")
        self.assertTrue(count == 0)

if __name__ == "__main__":
    unittest.main()