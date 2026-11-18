"""Step 4: use Nmap to see who is on the network and which doors are open.

  - discover_devices(): lists devices on the network (no port scanning).
  - split_devices(): separates the router and this laptop from other devices,
    which tells us whether guests are kept apart (client isolation).
  - scan_my_ports(): checks the top 100 ports on THIS laptop only.

Only scan networks you are allowed to use.

Try it:  python -m App.travel_guardian.scanner
"""

import ctypes
import nmap

# Where to look for Nmap: first anywhere on the PATH, then the folders the
# Nmap installer uses. This lets the packaged .exe find Nmap on another PC.
NMAP_PLACES = (
    "nmap",
    r"C:\Program Files (x86)\Nmap\nmap.exe",
    r"C:\Program Files\Nmap\nmap.exe",
)

def is_admin():
    """ Return True if the app is running as Administrator. """
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except AttributeError:
        return False
    
def discover_devices(subnet):
    """Return a list of IP addresses that answered on the network.

    -sn  = find devices only, don't check their ports
    -n   = skip name lookups (makes it about 10x faster)
    -T4  = faster timing
    """
    scanner = nmap.PortScanner(nmap_search_path=NMAP_PLACES)
    scanner.scan(hosts=subnet, arguments="-sn -n -T4")
    return scanner.all_hosts()

def split_devices(devices, my_ip, gateway):
    """ Separate the router and this device from everyone else. """
    others = [ip for ip in devices if ip not in (my_ip, gateway)]
    return {
        "router_found": gateway in devices,
        "other_devices": others,
    }

def scan_my_ports(my_ip):
    """Check the 100 most common ports on this laptop.

    -sT              = normal connection test (works without Administrator)
    --top-ports 100  = only the 100 most common ports
    -sV --version-light = quick guess at which program is behind each open port
    """
    scanner = nmap.PortScanner(nmap_search_path=NMAP_PLACES)
    scanner.scan(hosts=my_ip, arguments="-sT --top-ports 100 -sV --version-light -T4")
    
    open_ports = []
    if my_ip in scanner.all_hosts():
        for port, details in scanner[my_ip].get("tcp", {}).items():
            if details["state"] == "open":
                open_ports.append({"port": port, "service": details.get("name")})
    return sorted(open_ports, key=lambda p: p["port"])

if __name__ == "__main__":
    from App.travel_guardian.network import get_network_info

    net = get_network_info()
    print(f"Running as Administrator: {is_admin()}")
    print(f"Looking for devices on {net['subnet']}...")
    devices = discover_devices(net["subnet"])
    result = split_devices(devices, net["ip"], net["gateway"])
    print(f"Router found: {result['router_found']}")
    print(f"Other devices: {len(result['other_devices'])} {result['other_devices']}")

    print(f"Checking open ports on this laptop ({net['ip']})...")
    for port in scan_my_ports(net["ip"]):
        print(f"  Port {port['port']} open ({port['service']})")