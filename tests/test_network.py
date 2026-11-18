"""Tests for network.py using sample text, so no real network is needed."""

from App.travel_guardian.network import parse_default_gateway

SAMPLE_ROUTE_PRINT = """
IPv4 Route Table
===========================================================================
Active Routes:
Network Destination        Netmask          Gateway       Interface  Metric
          0.0.0.0          0.0.0.0      192.168.1.1    192.168.1.166     35
          0.0.0.0          0.0.0.0       10.0.0.1        10.0.0.50       50
===========================================================================
"""


def test_picks_gateway_for_our_interface():
    assert parse_default_gateway(SAMPLE_ROUTE_PRINT, "10.0.0.50") == "10.0.0.1"


def test_falls_back_to_first_gateway_if_interface_not_listed():
    assert parse_default_gateway(SAMPLE_ROUTE_PRINT, "172.16.0.9") == "192.168.1.1"


def test_returns_none_when_there_is_no_default_route():
    assert parse_default_gateway("No routes here", "192.168.1.166") is None
