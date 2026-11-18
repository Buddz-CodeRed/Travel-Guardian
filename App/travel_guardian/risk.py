"""Step 3: the rule book. Decides how risky each finding is and what to do.

The AI never decides risk or advice. It only explains what these rules say.

Try it:  python -m App.travel_guardian.risk
"""

# Risk levels, from best to worst. The number lets us compare them.
LEVELS = {"Low": 1, "Medium": 2, "High": 3}

# Ports that matter on a traveller's laptop: port -> (service, risk, advice)
PORT_RULES = {
    21: ("File transfer (FTP)", "Medium", "Turn off the FTP server if you don't need it."),
    22: ("Remote login (SSH)", "Medium", "Turn off the SSH server while travelling."),
    23: ("Telnet", "High", "Turn off Telnet. It sends passwords without encryption."),
    80: ("Web server", "Medium", "Stop any web server you're not using."),
    135: ("Windows remote services (RPC)", "Medium",
        "Set this Wi-Fi to Public in Windows settings and keep the firewall on."),
    139: ("Windows file sharing (NetBIOS)", "High",
        "Turn off file and printer sharing in Windows settings."),
    445: ("Windows file sharing (SMB)", "High",
        "Turn off file and printer sharing in Windows settings."),
    3389: ("Remote Desktop", "High", "Turn off Remote Desktop while travelling."),
    5900: ("Screen sharing (VNC)", "High", "Turn off screen sharing while travelling."),
}

# Windows services that are always listening. On a Public network with the
# firewall on, Windows blocks other devices from reaching them (see firewall.py).
FIREWALLED_PORTS = (135, 139, 445)

def make_finding(title, risk, reason, advice):
    """ Package one finding as a dictionary so every finding looks the same. """
    return {"title": title, "risk": risk, "reason": reason, "advice": advice}

def check_wifi(wifi):
    """ Rate the Wi-Fi security type """
    auth = (wifi.get("authentication") or "").upper()
    cipher = (wifi.get("cipher") or "").upper()
    
    if not auth:
        return make_finding("Wi-Fi security unknown", "Medium",
                            wifi.get("error") or "Windows didn't report the Wi-Fi security type.",
                            "Turn on Location services, or check the network's security in Windows settings.")
        
    if auth == "OPEN" or cipher == "NONE":
        return make_finding("Wi-Fi has no password", "High",
                            "Anyone nearby could see what you send on the network.",
                            "Use a VPN, or avoid logging into important accounts.")
    if "WEP" in cipher:
        return make_finding("Wi-Fi uses old WEP security", "High",
                            "WEP can be broken in minutes.",
                            "Use a VPN for anything private.")
    if auth.startswith("WPA-") :
        return make_finding("Wi-Fi uses older WPA security", "Medium",
                            "WPA is outdated and weaker than WPA2 or WPA3.",
                            "Use a VPN for anything private.")
    return make_finding("Wi-Fi is password protected", "Low",
                        f"This network uses {wifi.get('authentication')}, which encrypts your traffic.",
                        "No action needed.")

def check_isolation(discovery, protected=False):
    """ Rate whether other guests' devices can be seen.

    protected = True when firewall.py found the Wi-Fi is Public with the firewall on.
    """
    others = discovery.get("other_devices", [])
    if not others:
        return make_finding("Guests are kept apart", "Low",
                            "No other devices can be seen on this Wi-Fi, so other people can't reach your device.",
                            "No action needed.")
    if protected:
        return make_finding(f"{len(others)} other device(s) found on this Wi-Fi", "Low",
                            "Other devices are on this Wi-Fi, but Windows Firewall stops them reaching your device.",
                            "No action needed.")
    return make_finding(f"{len(others)} other device(s) found on this Wi-Fi", "Medium",
                        "Other devices on this Wi-Fi may be able to reach your device directly.",
                        "Set this Wi-Fi to Public in Windows settings and keep the firewall on.")
    
def check_ports(open_ports, protected=False):
    """ Rate each open port on this device using PORT_RULES.

    protected = True when firewall.py found the Wi-Fi is Public with the firewall on.
    """
    findings = []
    for port in open_ports:
        number = port["port"]
        if protected and number in FIREWALLED_PORTS:
            # Still listening, but the firewall keeps other devices out, so Low.
            service = PORT_RULES[number][0]
            findings.append(make_finding(f"Port {number} is listening but blocked: {service}", "Low",
                                        f"{service} is running, but Windows Firewall stops other devices reaching it.",
                                        "No action needed."))
            continue
        if number in PORT_RULES:
            service, risk, advice = PORT_RULES[number]
        else:
            service = port.get("service") or "Unknown service"
            risk, advice = "Low", "Close it if you don't recognise it."
        # "Listening" means a program on this device is waiting for connections.
        # The scan runs on this device, so it can't tell if the firewall blocks others.
        findings.append(make_finding(f"Port {number} is listening: {service}", risk,
                                    f"Your device is running {service} and listening for connections.", advice))
    if not findings:
        findings.append(make_finding("No listening ports found", "Low",
                                    "Your device isn't accepting connections on common ports.",
                                    "No action needed."))
    return findings

def assess(wifi, discovery, open_ports, protection=None):
    """ Run every rule and work out the overall risk (the worst finding).

    protection is the dictionary from firewall.get_protection_info().
    Without it, the rules assume the firewall is not protecting the device.
    """
    protected = bool(protection and protection.get("protected"))
    findings = ([check_wifi(wifi), check_isolation(discovery, protected)]
                + check_ports(open_ports, protected))
    overall = max((f["risk"] for f in findings), key=lambda level: LEVELS[level])
    return {"overall": overall, "findings": findings}

if __name__ == "__main__":
    # Pretend results, so we can test the rules without scanning.
    example = assess(
        wifi={"authentication": "Open", "cipher": "None"},
        discovery={"other_devices": []},
        open_ports=[{"port": 445, "service": "microsoft-ds"}],
    )
    print(f"Overall risk: {example['overall']}")
    for finding in example["findings"]:
        print(f"- [{finding['risk']}] {finding['title']}: {finding['advice']}")