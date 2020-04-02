#!/usr/bin/python3
import psutil
import socket

def get_interfaces():
    """
    This function returns all network interfaces.
    """
    return psutil.net_if_addrs().keys()


def ip_addresses():
    """
        Get the IPv4 and IPv6 addresses of all network interfaces (except the loopback interface).

        :return: The outer dictionary's key is the name of the network interface, the corresponding
                 value is a dictionary with possibly two entries: one with key ``IPVersion.v4``
                 for the IPv4 address of the interface, the other with key ``'IPVersion.v6'`` for
                 the IPv6 address of the interface.
                 
    https://github.com/BMeu/Orchard/blob/master/orchard/system_status/system/network.py
    """
    unfiltered_addresses = psutil.net_if_addrs()
    filtered_addresses = {}
    for interface, addresses in unfiltered_addresses.items():
        # Ignore the loopback interface.
        if interface == 'lo':
            continue

        filtered_addresses[interface] = {}
        for address in addresses:
            # Add IPv4 and IPv6 addresses to the output.
            if address.family == socket.AF_INET:
                filtered_addresses[interface]["IPv4"] = address.address
            elif address.family == socket.AF_INET6:
                filtered_addresses[interface]["IPv6"] = address.address

    return filtered_addresses