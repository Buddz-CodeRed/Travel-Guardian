"""Step 1: find out which network this laptop is on.

Answers four questions:
  - Which adapter is in use (Wi-Fi or Ethernet)?
  - What is this laptop's IP address?
  - What is the subnet (the range of addresses on this network)?
  - What is the gateway (the router's address)?

Try it:  python -m App.travel_guardian.network
"""

import ipaddress
import socket
import subprocess

import psutil


def get_my_ip():
    """Return the IP address this laptop uses to reach other networks.

    Connecting a UDP socket sends no data. It just makes Windows choose
    which network connection it would use, so we can read our own address.
    192.0.2.1 is a reserved test address that is never used for real.
    """
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.connect(("192.0.2.1", 80))
        return probe.getsockname()[0]
    finally:
        probe.close()


def find_adapter(my_ip):
    """Return (adapter name, netmask) for the adapter that has my_ip."""
    for adapter_name, addresses in psutil.net_if_addrs().items():
        for address in addresses:
            if address.family == socket.AF_INET and address.address == my_ip:
                return adapter_name, address.netmask
    return None, None


def parse_default_gateway(route_text, my_ip):
    """Find the router's address in the text printed by 'route print'.

    Default-route lines look like this (destination, netmask, gateway,
    interface, metric):
        0.0.0.0          0.0.0.0      192.168.1.1    192.168.1.166     35
    We pick the line whose interface is our own IP.
    """
    fallback = None
    for line in route_text.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
            gateway, interface = parts[2], parts[3]
            if interface == my_ip:
                return gateway
            fallback = fallback or gateway
    return fallback


def get_default_gateway(my_ip):
    """Ask Windows for its route table and pull out the router's address."""
    result = subprocess.run(
        ["route", "print", "-4", "0.0.0.0"],
        capture_output=True, text=True, errors="replace",
    )
    return parse_default_gateway(result.stdout, my_ip)


def get_network_info():
    """Collect everything about the current network into one dictionary."""
    my_ip = get_my_ip()
    adapter, netmask = find_adapter(my_ip)

    subnet = None
    if netmask:
        # strict=False lets us build the network from a host address.
        subnet = str(ipaddress.IPv4Network(f"{my_ip}/{netmask}", strict=False))

    return {
        "adapter": adapter,
        "ip": my_ip,
        "netmask": netmask,
        "subnet": subnet,
        "gateway": get_default_gateway(my_ip),
    }


if __name__ == "__main__":
    info = get_network_info()
    print(f"Adapter:  {info['adapter']}")
    print(f"Your IP:  {info['ip']}")
    print(f"Subnet:   {info['subnet']}")
    print(f"Gateway:  {info['gateway']}")
