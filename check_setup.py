"""Quick setup check for Travel Guardian.

Run with:  tg_env\\Scripts\\python.exe check_setup.py
Each check prints OK or a short reason it failed. Nothing is scanned
and nothing is saved.
"""

import ipaddress
import socket
import subprocess
import sys


def check(name, func):
    """Run one check and print the result without stopping on errors."""
    try:
        detail = func()
        print(f"[OK]   {name}: {detail}")
    except Exception as error:  # report any failure and keep going
        print(f"[FAIL] {name}: {error}")


def python_version():
    return sys.version.split()[0]


def nmap_found():
    import nmap  # python-nmap

    scanner = nmap.PortScanner()  # raises an error if Nmap is not installed
    major, minor = scanner.nmap_version()
    return f"Nmap {major}.{minor} found by python-nmap"


def active_network():
    import psutil

    # Find the address this PC uses to reach other networks. No data is sent:
    # connecting a UDP socket only picks the outgoing interface.
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    probe.connect(("192.0.2.1", 80))
    my_ip = probe.getsockname()[0]
    probe.close()

    for adapter, addresses in psutil.net_if_addrs().items():
        for address in addresses:
            if address.family == socket.AF_INET and address.address == my_ip:
                network = ipaddress.IPv4Network(f"{my_ip}/{address.netmask}", strict=False)
                return f"adapter '{adapter}', IP {my_ip}, subnet {network}"
    return f"IP {my_ip} (adapter not matched)"


def wifi_readable():
    result = subprocess.run(
        ["netsh", "wlan", "show", "networks", "mode=bssid"],
        capture_output=True, text=True, errors="replace",
    )
    output = result.stdout + result.stderr
    if "location" in output.lower() and "SSID" not in output:
        raise RuntimeError("Windows Location services must be turned on for Wi-Fi scanning")
    count = output.count("SSID ") - output.count("BSSID ")
    return f"{count} nearby Wi-Fi network(s) visible"


def llama_ready():
    import llama_cpp

    return f"llama-cpp-python {llama_cpp.__version__} imported (model not loaded yet)"


def widget_opens():
    import threading
    import webview

    window = webview.create_window(
        "Travel Guardian setup check",
        html="<h2 style='font-family:sans-serif'>pywebview works. Closing...</h2>",
        width=360, height=160, on_top=True,
    )
    threading.Timer(3, window.destroy).start()  # close after 3 seconds
    webview.start()
    return "test window opened and closed"


if __name__ == "__main__":
    check("Python", python_version)
    check("Nmap + python-nmap", nmap_found)
    check("Network (psutil)", active_network)
    check("Wi-Fi (netsh)", wifi_readable)
    check("AI runtime", llama_ready)
    check("Widget (pywebview)", widget_opens)
