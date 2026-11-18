"""Tests for the rule book in risk.py."""

from App.travel_guardian.risk import assess, check_isolation, check_ports, check_wifi


def test_open_wifi_is_high_risk():
    assert check_wifi({"authentication": "Open", "cipher": "None"})["risk"] == "High"


def test_wpa2_wifi_is_low_risk():
    assert check_wifi({"authentication": "WPA2-Personal", "cipher": "CCMP"})["risk"] == "Low"


def test_unknown_wifi_security_is_medium_risk():
    assert check_wifi({"error": "Not connected"})["risk"] == "Medium"


def test_isolated_network_is_low_risk():
    assert check_isolation({"other_devices": []})["risk"] == "Low"


def test_visible_devices_are_medium_risk():
    assert check_isolation({"other_devices": ["192.168.1.20"]})["risk"] == "Medium"


def test_file_sharing_port_is_high_risk():
    findings = check_ports([{"port": 445, "service": "microsoft-ds"}])
    assert findings[0]["risk"] == "High"


def test_overall_risk_is_the_worst_finding():
    result = assess(
        wifi={"authentication": "WPA2-Personal", "cipher": "CCMP"},
        discovery={"other_devices": []},
        open_ports=[{"port": 3389, "service": "ms-wbt-server"}],
    )
    assert result["overall"] == "High"


def test_file_sharing_port_is_low_risk_when_firewall_protects():
    findings = check_ports([{"port": 445, "service": "microsoft-ds"}], protected=True)
    assert findings[0]["risk"] == "Low"


def test_remote_desktop_stays_high_risk_even_when_firewall_protects():
    findings = check_ports([{"port": 3389, "service": "ms-wbt-server"}], protected=True)
    assert findings[0]["risk"] == "High"


def test_visible_devices_are_low_risk_when_firewall_protects():
    assert check_isolation({"other_devices": ["192.168.1.20"]}, protected=True)["risk"] == "Low"


def test_overall_is_low_on_protected_laptop_with_windows_ports():
    result = assess(
        wifi={"authentication": "WPA2-Personal", "cipher": "CCMP"},
        discovery={"other_devices": []},
        open_ports=[{"port": 135}, {"port": 139}, {"port": 445}],
        protection={"protected": True},
    )
    assert result["overall"] == "Low"
