"""
lib/backend.py

Includes code for working with network manager programs
"""

import os
import sys
import subprocess

class NetworkManager(object):
    """ Backend for NetworkManager network manager
    """

    def __init__(self, iface):
        """ Initialize the object
        """
        self.iface = iface

    def include(self):
        """ Allow NetworkManager to manage the interface
        """
        subprocess.check_output(f"nmcli device set {self.iface.iface} managed yes".split(" ")).decode()
        return None

    def exclude(self):
        """ Disallow NetworkManager from managing the interface
        """
        subprocess.check_output(f"nmcli device set {self.iface.iface} managed no".split(" ")).decode()
