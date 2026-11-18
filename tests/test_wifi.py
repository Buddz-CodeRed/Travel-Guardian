"""Tests for wifi.py using sample netsh text, so no real Wi-Fi is needed."""

from App.travel_guardian.wifi import parse_interfaces

SAMPLE = """
    Name                   : Wi-Fi
    State                  : connected
    SSID                   : HotelGuest
    AP BSSID               : 0c:8e:29:9f:19:d7
    Authentication         : Open
    Cipher                 : None
    Signal                 : 72%
"""


def test_reads_network_details():
    info = parse_interfaces(SAMPLE)
    assert info["connected"] is True
    assert info["ssid"] == "HotelGuest"
    assert info["authentication"] == "Open"
    assert info["cipher"] == "None"
    assert info["signal"] == 72


def test_not_connected():
    info = parse_interfaces("    State                  : disconnected")
    assert info["connected"] is False
    assert info["ssid"] is None