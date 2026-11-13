"""Access-control helpers for internal collaboration records and attachments."""
import frappe

def _is_member(room_name, user):
    if not room_name or not user or user == "Guest":
        return False
    if "System Manager" in frappe.get_roles(user):
        return True
    return bool(frappe.db.exists("MASAR Chat Room Member", {"parent": room_name, "user": user}))

def chat_room_has_permission(doc, user=None, permission_type=None):
    return _is_member(doc.name, user or frappe.session.user)

def chat_message_has_permission(doc, user=None, permission_type=None):
    room_name = doc.room if hasattr(doc, "room") else frappe.db.get_value("MASAR Chat Message", doc.name, "room")
    return _is_member(room_name, user or frappe.session.user)

def file_has_permission(doc, user=None, permission_type=None):
    if getattr(doc, "attached_to_doctype", None) != "MASAR Chat Message":
        return None
    room_name = frappe.db.get_value("MASAR Chat Message", doc.attached_to_name, "room")
    return _is_member(room_name, user or frappe.session.user)

def chat_room_query(user=None):
    user = user or frappe.session.user
    if "System Manager" in frappe.get_roles(user):
        return ""
    escaped = frappe.db.escape(user)
    return "name in (select parent from `tabMASAR Chat Room Member` where user = {0})".format(escaped)

def chat_message_query(user=None):
    user = user or frappe.session.user
    if "System Manager" in frappe.get_roles(user):
        return ""
    escaped = frappe.db.escape(user)
    return "room in (select parent from `tabMASAR Chat Room Member` where user = {0})".format(escaped)
