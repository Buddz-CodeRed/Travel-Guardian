"""Step 9: ask Windows whether its firewall is protecting this laptop.

The port scan in scanner.py runs on this laptop, so it sees every program
that is listening, even when Windows Firewall stops other devices from
reaching it. This file asks Windows three questions so risk.py can tell
the difference:

  - Is this Wi-Fi set to Public or Private?
  - Is the firewall switched on for Public networks?
  - Is file and printer sharing allowed through the firewall on Public networks?

Try it:  python -m App.travel_guardian.firewall
"""

import subprocess

# PowerShell commands that print three lines such as:
#   Profile: Public
#   Firewall: True
#   SharingRules: 0
# '@FirewallAPI.dll,-28502' is Windows' built-in name for the "File and Printer
# Sharing" group of firewall rules. It is the same in every language.
# ADAPTER is replaced with the adapter name (for example Wi-Fi) before running.
POWERSHELL_SCRIPT = """
$category = (Get-NetConnectionProfile -InterfaceAlias 'ADAPTER').NetworkCategory
"Profile: $category"
"Firewall: " + (Get-NetFirewallProfile -Name Public).Enabled
$rules = @(Get-NetFirewallRule -Group '@FirewallAPI.dll,-28502' -Enabled True -Direction Inbound -Action Allow -ErrorAction SilentlyContinue |
    Where-Object { $_.Profile -match 'Public|Any' })
"SharingRules: " + $rules.Count
"""


def parse_protection(text):
    """Turn the three printed lines into a dictionary.

    "protected" is True only when all three answers are the safe ones:
    the Wi-Fi is Public, the firewall is on, and sharing is not allowed in.
    If any line is missing we can't be sure, so "protected" is False.
    """
    fields = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        fields[name.strip()] = value.strip()

    profile = fields.get("Profile") or None
    firewall_on = fields.get("Firewall") == "True"
    rule_count = fields.get("SharingRules", "")
    sharing_allowed = (not rule_count.isdigit()) or int(rule_count) > 0

    info = {
        "profile": profile,
        "firewall_on": firewall_on,
        "sharing_allowed": sharing_allowed,
        "protected": profile == "Public" and firewall_on and not sharing_allowed,
    }
    if profile is None:
        info["error"] = "Couldn't read the Windows firewall settings."
    return info


def get_protection_info(adapter):
    """Run the PowerShell commands for this adapter and return the answers."""
    # A quote inside the adapter name is doubled so PowerShell reads it as text.
    script = POWERSHELL_SCRIPT.replace("ADAPTER", (adapter or "").replace("'", "''"))
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, text=True, errors="replace", timeout=30,
        )
        return parse_protection(result.stdout)
    except (OSError, subprocess.TimeoutExpired):
        return parse_protection("")


if __name__ == "__main__":
    from App.travel_guardian.network import get_network_info

    info = get_protection_info(get_network_info()["adapter"])
    if info.get("error"):
        print(info["error"])
    print(f"Wi-Fi type:        {info['profile']}")
    print(f"Firewall on:       {info['firewall_on']}")
    print(f"Sharing allowed:   {info['sharing_allowed']}")
    print(f"Protected:         {info['protected']}")
