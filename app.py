"""Step 7: the starting point. Opens the Travel Guardian window.

The Api class holds the functions the window's buttons can call.
JavaScript calls them like this:  window.pywebview.api.scan()

Run the app:  python app.py
"""

import ctypes
import os
import subprocess
import sys
from pathlib import Path

# When the app's zip is downloaded, Windows marks every file inside as "from
# the internet" (a hidden Zone.Identifier tag). .NET then refuses to load the
# window's DLL and the app crashes with "Failed to resolve Python.Runtime...".
# Inside the .exe only, remove that tag from the app's own files before the
# window library (webview) is loaded. Same as right-click > Properties > Unblock.
if getattr(sys, "frozen", False):
    for file in Path(sys.executable).parent.rglob("*"):
        try:
            os.remove(f"{file}:Zone.Identifier")
        except OSError:
            pass                             # no tag on this file, or can't change it

import webview
from App.travel_guardian import firewall, network, risk, scanner, session, wifi
from App.travel_guardian import explain

# The packaged .exe (Step 11) has no console. Without this, every command the
# app runs (netsh, route, PowerShell, Nmap) would flash a black window.
# CREATE_NO_WINDOW tells Windows to run those commands invisibly.
if getattr(sys, "frozen", False):          # True only inside the .exe
    _start_command = subprocess.Popen.__init__

    def _start_command_hidden(self, *args, **kwargs):
        kwargs.setdefault("creationflags", subprocess.CREATE_NO_WINDOW)
        _start_command(self, *args, **kwargs)

    subprocess.Popen.__init__ = _start_command_hidden

UI_FILE = Path(__file__).parent / "ui" / "index.html"
ICON_FILE = Path(__file__).parent / "ui" / "icon.ico"

class Api:
    """ Every method here can be called from ui/app.js. """
    
    def get_wifi_name(self):
        """ Used by the consent screen to show which network you're on. """
        info = wifi.get_wifi_info()
        return info.get("ssid")  or "Unknown network"
    
    def scan(self):
        """ Run the whole check and return the results for the window. """
        try:
            messages = []
            net = network.get_network_info()
            wifi_info = wifi.get_wifi_info()
            if wifi_info.get("error"):
                messages.append(wifi_info["error"])
                
            if not scanner.is_admin():
                messages.append("Run as Administrator for a more complete device search.")
            devices = scanner.discover_devices(net["subnet"])
            discovery = scanner.split_devices(devices, net["ip"], net["gateway"])
            open_ports = scanner.scan_my_ports(net["ip"])

            # Ask Windows if the firewall is protecting this laptop on this Wi-Fi.
            protection = firewall.get_protection_info(net["adapter"])
            if protection.get("error"):
                messages.append(protection["error"])

            assessment = risk.assess(wifi_info, discovery, open_ports, protection)
            summary, from_ai = explain.explain(assessment)
            if not from_ai: 
                messages.append("AI explanation unavailable, showing standard advice.")
                
            results = {
                "network": net,
                "wifi": wifi_info,
                "discovery": discovery,
                "protection": protection,
                "overall": assessment["overall"],
                "findings": assessment["findings"],
                "summary": summary,
                "messages": messages,
            }
            session.save(results)
            return results
        except Exception as error:
            if "nmap program was not found" in str(error):
                return {"error": "Nmap isn't installed on this PC. Double-click Setup.bat "
                                 "in the Travel Guardian folder, then restart Travel Guardian."}
            return {"error": f"The scan couldn't finish: {error}"}
        
    def clear_session(self):
        """ Forget the results (used by the Clear session button)"""
        session.clear()
        return True
    
if __name__ == "__main__":
    window = webview.create_window(
        "Travel Guardian",
        str(UI_FILE),
        js_api=Api(),
        width=380,
        height=640,
        on_top=True,
        background_color="#19253f",  # dark while the page loads (no white flash)
    )

    def glass_title_bar():
        """ Give the title bar Windows 11's frosted-glass look (called acrylic).

        DwmSetWindowAttribute asks Windows to change how it draws a window.
        Setting 20 = dark title bar, setting 38 = backdrop material (3 = acrylic).
        On older Windows the request is ignored and the bar stays normal.
        """
        window.events.loaded.wait()             # wait until the page has loaded
        handle = window.native.Handle.ToInt32() # Windows' ID number for our window
        for setting, value in ((20, 1), (38, 3)):
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                handle, setting, ctypes.byref(ctypes.c_int(value)), 4)

    window.events.closed += session.clear       # forget everything when the window closes
    window.events.closed += explain.unload_model # close the AI model cleanly
    # start() runs glass_title_bar in the background once the window exists.
    webview.start(glass_title_bar, icon=str(ICON_FILE))  # icon = shield in the title bar