"""Static contract tests that do not require a running Frappe site."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_collaboration_checks_membership_and_realtime():
    source = (ROOT / "collaboration.py").read_text(encoding="utf-8")
    assert "def _room(" in source
    assert "frappe.PermissionError" in source
    assert "frappe.publish_realtime" in source
    assert "def print_messages(" in source

def test_ai_fails_closed_without_server_side_provider_config():
    source = (ROOT / "ai_assistant.py").read_text(encoding="utf-8")
    assert "frappe.conf.get" in source
    assert "not_configured" in source
