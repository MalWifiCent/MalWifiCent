#!/usr/bin/python3
import os
import json
import shutil
import re
import socket
import importlib


class ConfigParser(object):
    """
    This is the parser for the inetsim.conf file. It can read setting values, and write new
    settings. When the user saves, it will write the settings in memory to the inetsim.conf file
    inside malwificent folder, then copy the inetsim.conf into /etc/inetsim/ and overwrite the 
    existing file there.
    """

    def __init__(self, config_path, settings, test=False):
        """
        Args:
            config_path: (str) The path to the inetsim.conf the program is to write/read from.
            settings: (dict/list) The settings to load. If dict, the key should be the name of the 
                    setting to be loaded.
            test: (bool)
        """
        self.config_copy = f"{config_path}.copy"
        self.config = config_path
        self.options = self.__load_settings(settings)
        self.test = test

        # A list containing all allowed services
        self.services = [
            "dns",
            "http",
            "https",
            "smtp",
            "smtps",
            "pop3",
            "pop3s",
            "ftp",
            "ftps",
            "tftp",
            "irc",
            "ntp",
            "finger",
            "ident",
            "syslog",
            "time_tcp",
            "time_udp",
            "daytime_tcp",
            "daytime_udp",
            "echo_tcp",
            "echo_udp",
            "discard_tcp",
            "discard_udp",
            "quotd_tcp",
            "quotd_udp",
            "chargen_tcp",
            "chargen_udp",
            "dummy_tcp",
            "dummy_udp"
        ]

        if not os.path.isfile(self.config_copy):
            raise IOError(f"Cannot find the configuration file '{self.config_copy}'")
    
    
    def __load_settings(self, settings):
        """
        Loads the needed configurations from inetsim.conf into memory for the system to use.

        Args:
            settings: (dict/list) A list containing the names of the settings needed.
        Returns:
            options: (dict) A Python dictionary with the setting values read from inetsim.conf.
                    The keys might contain a #, which indicates that the setting is commented out
                    in the inetsim.conf file.
        """
        options = {}
        # If a dictionary is given instead of a list, build a list based
        # on the keys.
        if isinstance(settings, dict):
            settings = settings.keys()
        for item in settings:
            temp = self.read(item)

            # Do the list contain multiple elements?
            if len(temp) > 1:
                options[item] = []
                for i in temp:
                    options[item].append(i.split(" ")[1])
            else:
                # Doing it this way to see if the setting is commented out or not
                # opt[0] = setting name, opt[1] = setting value
                opt = temp[0].split(" ")
                options[opt[0]] = " ".join(opt[1:])
        return options
    

    def __load_test_data(self, reload=False):
        """
        Function to load test data
        TODO: Not in use anymore. Letting it stay incase more testing is needed.
        """
        try:
            #from tests.data.inetsimconf import options as test_opt
            import tests.data.inetsimconf
        except ImportError:
            raise ImportError(f"Unable to import INetSim test data")
        
        # The test dictionary is a Python file and must be recompiled
        # if it is edited
        if reload:
            # https://docs.python.org/3/library/importlib.html#importlib.reload
            importlib.reload(tests.data.inetsimconf)
        self.options = tests.data.inetsimconf.options
        

    def _read_config(self):
        """
        Helper function to read the configuration file into memory.
        """
        try:
            with open(self.config_copy, "r") as fd:
                return fd.readlines()
        except IOError:
            raise IOError(f"Error opening file '{self.config_copy}'")


    def _replace_mutiple(self, key:str, data:list):
        """
        This function replaces a configuration key that might be repeated.
        Example: 
            start_service dns
            start_service http
        
        Args:
            key: The name of the setting to be replaced
            data: A list of the current configuration to be replaced
        Return:
            new_data:  (list) This is the modified list of inetsim.conf in memory, ready
                    to be written to file.
        TODO: Refactor the function... It is quite messy
        """
        # Dictionart holding the new options
        new_data = []
        # Index of found item
        index = -1
        # Found key in line?
        found = False
        #Replace insted of adding a new item
        rep = False
        # Loop through the option dictionary
        for i, line in enumerate(data):
            if key in line:
                found = True
            if key in line and not line.startswith("#"):
                if index == -1:
                    index = data.index(line)
                continue

            # In case there are occurrences of the key after the comment section
            # but the item is commented out
            elif key in line or (key.startswith("#") and key[1:] in line):
                if line.startswith('# '):
                    continue
                if index == -1:
                    index = i
                    rep = True

            # In case there are no occurrences of the key after the
            # comment section
            elif found and line == '\n':
                if index == -1:
                    index = i
            new_data.append(line)
        
        # Insert the new values into the list starting from saved index
        for value in self.options[key]:
            if rep:
                new_data[index] = f"{key} {value}\n"
            else:
                new_data.insert(index, f"{key} {value}\n")
            index += 1

        return new_data
    

    def _replace_single(self, key:str, value:str, data:list):
        """
        Replace a single setting in the config based on key and value.

        Args:
            key: The key/setting to replace the value for
            value: The new value
            data: A list of the current configuration to be replaced
        """
        new_data = []
        for line in data:
            # Loop over all items in options dictionary
            if key in line or (key.startswith("#") and key[1:] in line):
                if line.startswith('# '):
                    continue
                line = line.replace(line, f"{key} {value}\n")
            new_data.append(line)
        return new_data

    def _update_options(self, updates:dict):
        """
        This function will update the JSON object loaded into memory
        with the items found in "updates"

        Args:
            updates: (dict) A dictionary containing the items that will be updated
        """
        for k,v in updates.items():
            if k in self.options.keys():
                self.options[k] = v
            else:
                new_k = k[1:] if k.startswith("#") else f"#{k}"
                if new_k in self.options.keys():
                    del self.options[new_k]
                    self.options[k] = v


    def _write_config(self, options:dict):
        """
        This is the main function in this class, it will load the 
        data from the config file into memory including the options
        to be used. It will then update the options in memory and 
        write it to disk / inetsim.conf.

        Args:  
            options: (dict) A dictionary containing the settings name and the new value
                to be written to disc
        """
        # Load options from JSON file
        #self.__load_json()
        self._update_options(options)
        # Read the current config file to memory
        data = self._read_config()
        # Modify/ create a new list with the modified values
        for k,v in self.options.items():
            if isinstance(v, list):
                data = self._replace_mutiple(k, data)
            else:
                data = self._replace_single(k, v, data)
        # Write data to file (inetsim.conf)
        self._save(data)
                

    def _save(self, new_data:list):
        """
        Helper function to save data.

        Args:
            new_data: (list) A list containing the lines to be written to file.
        """
        try:
            with open(self.config_copy, "w") as fd:
                fd.writelines(new_data)
        except IOError:
            raise IOError(f"Error opening file for writing '{self.config_copy}'")
        self.copy_config()


    def _find(self, key:str):
        """
        This function will return option index(es) 

        Args:
            key: (str) Name of the setting to be found
        Returns:
            indexes: (list) A list containing all the indexes found, aka line numbers
                where "key" is located.
        """
        # Load inetsim.conf into memory
        data = self._read_config()
        indexes = []
        for line in data:
            if key in line or (key.startswith("#") and key[1:] in line):
                if line.startswith('# '):
                    continue
                indexes.append(data.index(line))
        return indexes
    

    def read(self, key:str):
        """
        This function gets the value of the setting "key" from the INetSim 
        config file and returns it.

        Args:
            key: (str) The setting to be found
        Returns:
            values: (list) A list containing 
        """
        values = []
        items = self._find(key)
        data = self._read_config()
        for i in items:
            values.append(data[i].strip())
        return values
    

    def read_list(self, items:list):
        """
        This functions generates a Python dictionary based on the given list "items"
        and fills it with the values from the INetSim config file.

        NB: Not for multi-settings

        Args:
            items:list = A list containing the names of the settings to get values from
        Return: 
            config_items: (dict) A Python dictionary containing the setting as key
                    and the value for that setting as value, read from inetsim.conf
        """
        config_items = {}
        for item in items:
            if item in self.options.keys(): 
                config_items[item] = self.options[item]
            elif f"#{item}" in self.options.keys():
                config_items[f"#{item}"] = self.options[f"#{item}"]
        return config_items
    

    def validate_input(self, form:dict, whitelist:dict):
        """
        This function validates the user input that is supposed to be used in
        the INetSim config file.

        Args:
            form: (dict) A dictionary containing the key/value pairs to be validated
            whitelist: (dict) A dictionary containing the whitlisted key names and 
                    what type of validation is needed for the value.
                    Accepted whitelist values:
                        IPv4, PORT
        Returns:
            status: (bool) True if all input was accepted, False otherwise.
            error: (list) A list containing the setting names / key for the input
                    not accepted.
        """
        error = []
        prepared = {}
        name = ""
        for form_k,form_v in form.items():
            if form_k in whitelist.keys():
                name = form_k if form.get(f"{form_k}_status") == "enable" else f"#{form_k}"
                # Validate IPv4
                if whitelist[form_k] == "IPv4":
                    if self.is_valid_ipv4_address(form_v):
                        prepared[name] = form_v
                    else:
                        error.append("Invalid IP")
                
                # Validate port number
                elif whitelist[form_k] == "PORT":
                    if self.is_valid_port(form_v):
                        prepared[name] = form_v
                    else:
                        error.append(form_k)
                elif whitelist[form_k] == "BOOL":
                    services = form.getlist(form_k)
                    #missing = set(self.services).difference(services)
                    prepared[form_k] = services
                else:
                    # Validated with the use of regex
                    if re.fullmatch(whitelist[form_k], form_v):
                        prepared[name] = form_v
                    else:
                        error.append(form_k)
            # Write data to inetsim.conf
            self._write_config(prepared)
        # Return validation status and errors
        status = True if not error else False
        return status, error


    def copy_config(self):
        shutil.copy(self.config_copy, "/etc/inetsim/inetsim.conf")


    @staticmethod
    def is_valid_ipv4_address(address:str):
        """
        Helper function to validate IPv4 addresses.

        https://stackoverflow.com/questions/319279/how-to-validate-ip-address-in-python
        """
        try:
            socket.inet_pton(socket.AF_INET, address)
        except AttributeError:
            try:
                socket.inet_aton(address)
            except socket.error:
                return False
            return address.count('.') == 3
        except socket.error:
            return False
        return True
    
    @staticmethod
    def is_valid_port(port):
        """
        Helper function to validate a port number
        Args:
            port: (int/str) The number to be validated
        Return:
            Bool: True if it is a valid port number
        """
        try:
            if not 1 <= int(port) <= 65535:
                return False
        except ValueError:
            return False
        return True
