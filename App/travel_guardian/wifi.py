"""Step 2: read the security of the Wi-Fi this laptop is connected to.

Uses the Windows command:  netsh wlan show interfaces
and picks out the network name, security type and signal strength.

Try it:  python -m App.travel_guardian.wifi
"""

import subprocess

def parse_interfaces(text):

    """Turn the text from 'netsh wlan show interfaces' into a dictionary.

    Each useful line looks like:   SSID                   : HotelGuest
    We split each line at the first ':' into a name and a value.
    """
    
    fields = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        fields[name.strip()] = value.strip()
        
    signal_text = fields.get("Signal", "").replace("%", "")
    return {
        "connected": fields.get("State") == "connected",
        "ssid": fields.get("SSID"),
        "authentication": fields.get("Authentication"),
        "cipher": fields.get("Cipher") ,
        "signal": int(signal_text) if signal_text.isdigit() else None,
    }
    
def get_wifi_info():
    """Run netsh and return the Wi-Fi details, or an error message."""
    result = subprocess.run(
        ["netsh", "wlan", "show", "interfaces"],
        capture_output=True, text=True, errors="replace",
    )
    output = result.stdout + result.stderr
    
    # windows 11 hides wifi details unless location services are on.
    if "location" in output.lower() and "SSID" not in output:
        return {"connected": False,
                "error": "Turn on Windows Location service to check wifi details."}
        
    info = parse_interfaces(output)
    if not info["connected"]:
        info["error"] = "This device is not connected to Wi-Fi."
    return info

if __name__ == "__main__":
    wifi = get_wifi_info()
    if wifi.get("error"):
        print(wifi["error"])
    else:
        print(f"Network: {wifi['ssid']}")
        print(f"Security: {wifi['authentication']} ({wifi['cipher']})")
        print(f"Signal: {wifi['signal']}%")