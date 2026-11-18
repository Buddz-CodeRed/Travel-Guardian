"""Tests for firewall.py using sample text, so no real PowerShell is needed."""

from App.travel_guardian.firewall import parse_protection


def test_public_with_firewall_on_and_no_sharing_is_protected():
    info = parse_protection("Profile: Public\nFirewall: True\nSharingRules: 0\n")
    assert info["protected"] is True


def test_private_network_is_not_protected():
    info = parse_protection("Profile: Private\nFirewall: True\nSharingRules: 0\n")
    assert info["protected"] is False


def test_firewall_off_is_not_protected():
    info = parse_protection("Profile: Public\nFirewall: False\nSharingRules: 0\n")
    assert info["protected"] is False


def test_sharing_allowed_through_firewall_is_not_protected():
    info = parse_protection("Profile: Public\nFirewall: True\nSharingRules: 4\n")
    assert info["sharing_allowed"] is True
    assert info["protected"] is False


def test_no_answer_from_windows_is_not_protected_and_reports_an_error():
    info = parse_protection("")
    assert info["protected"] is False
    assert "error" in info
