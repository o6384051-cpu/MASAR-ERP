"""Access-control helpers for private MASAR collaboration records."""
from __future__ import annotations

import frappe


def _is_system_manager(user: str) -> bool:
    return bool(user and user != "Guest" and "System Manager" in frappe.get_roles(user))


def _is_member(room_name: str | None, user: str | None) -> bool:
    if not room_name or not user or user == "Guest":
        return False
    if _is_system_manager(user):
        return True
    return bool(
        frappe.db.exists(
            "MASAR Chat Room Member",
            {
                "parent": room_name,
                "parenttype": "MASAR Chat Room",
                "parentfield": "members",
                "user": user,
            },
        )
    )


def chat_room_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if _is_system_manager(user):
        return None  # Defer to the DocType role permissions.
    if permission_type in ("read", "print", "email"):
        return _is_member(doc.name, user)
    # Room membership must never grant write, delete, share, or export rights.
    return False


def chat_message_has_permission(doc, user=None, permission_type=None):
    user = user or frappe.session.user
    if _is_system_manager(user):
        return None
    room_name = getattr(doc, "room", None)
    if not room_name and getattr(doc, "name", None):
        room_name = frappe.db.get_value("MASAR Chat Message", doc.name, "room")
    if permission_type in ("read", "print", "email"):
        return _is_member(room_name, user)
    # Message creation is performed only by the membership-checked server API.
    return False


def file_has_permission(doc, user=None, permission_type=None):
    if getattr(doc, "attached_to_doctype", None) != "MASAR Chat Message":
        return None
    user = user or frappe.session.user
    if permission_type != "read":
        return False
    room_name = frappe.db.get_value(
        "MASAR Chat Message", doc.attached_to_name, "room"
    )
    return _is_member(room_name, user)


def chat_room_query(user=None):
    user = user or frappe.session.user
    if _is_system_manager(user):
        return ""
    if not user or user == "Guest":
        return "1=0"
    escaped = frappe.db.escape(user)
    return (
        "name in (select parent from `tabMASAR Chat Room Member` "
        "where parenttype = 'MASAR Chat Room' and parentfield = 'members' "
        f"and user = {escaped})"
    )


def chat_message_query(user=None):
    user = user or frappe.session.user
    if _is_system_manager(user):
        return ""
    if not user or user == "Guest":
        return "1=0"
    escaped = frappe.db.escape(user)
    return (
        "room in (select parent from `tabMASAR Chat Room Member` "
        "where parenttype = 'MASAR Chat Room' and parentfield = 'members' "
        f"and user = {escaped})"
    )
