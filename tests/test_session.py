"""Tests for session.py: results are kept while the app is open and wiped by clear()."""

from App.travel_guardian import session


def test_saved_results_can_be_read_back():
    session.save({"overall": "Low"})
    assert session.get() == {"overall": "Low"}


def test_clear_forgets_everything():
    session.save({"overall": "High"})
    session.clear()
    assert session.get() == {}


def test_get_returns_a_copy():
    session.save({"overall": "Low"})
    copy = session.get()
    copy["overall"] = "High"
    assert session.get() == {"overall": "Low"}
