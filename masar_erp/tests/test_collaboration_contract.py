"""Static contract tests; integration tests require a running Frappe site."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_collaboration_modules_are_valid_python():
    for filename in ("collaboration.py", "permissions.py", "ai_assistant.py"):
        ast.parse((ROOT / filename).read_text(encoding="utf-8"))


def test_room_listing_uses_permission_aware_query():
    source = (ROOT / "collaboration.py").read_text(encoding="utf-8")
    list_rooms = source.split("def list_rooms():", 1)[1].split("@frappe.whitelist()", 1)[0]
    assert "frappe.get_list(" in list_rooms
    assert "frappe.get_all(" not in list_rooms
    assert "def _room(" in source
    assert "frappe.PermissionError" in source
    assert "frappe.publish_realtime" in source
    assert "def upload_attachment(" in source
    assert "is_private=1" in source
    assert "allowed_extensions" in source
    assert "25 * 1024 * 1024" in source
    assert "def list_attachments(" in source


def test_membership_does_not_grant_room_or_message_mutations():
    source = (ROOT / "permissions.py").read_text(encoding="utf-8")
    assert 'permission_type in ("read", "print", "email")' in source
    assert 'return False' in source
    assert 'parentfield = \'members\'' in source


def test_ai_fails_closed_and_does_not_forward_untrusted_context():
    source = (ROOT / "ai_assistant.py").read_text(encoding="utf-8")
    assert "frappe.conf.get" in source
    assert "not_configured" in source
    assert "not forwarded or trusted" in source
