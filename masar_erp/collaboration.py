"""Membership-checked internal messaging APIs for MASAR ERP."""
from __future__ import annotations

import frappe
from frappe.utils import now_datetime


def _user():
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("يجب تسجيل الدخول أولاً", frappe.AuthenticationError)
    return user


def _is_system_manager(user):
    return "System Manager" in frappe.get_roles(user)


def _room(room_name):
    user = _user()
    room = frappe.get_doc("MASAR Chat Room", room_name)
    if not room.enabled:
        frappe.throw("هذه المحادثة غير متاحة", frappe.PermissionError)
    members = {row.user for row in (room.members or [])}
    if user not in members and not _is_system_manager(user):
        frappe.throw("ليس لديك صلاحية الوصول إلى هذه المحادثة", frappe.PermissionError)
    return room


@frappe.whitelist()
def list_rooms():
    _user()
    # get_list applies the DocType permission query condition; get_all would bypass it.
    return frappe.get_list(
        "MASAR Chat Room",
        filters={"enabled": 1},
        fields=["name", "title", "room_type", "company", "modified"],
        order_by="modified desc",
        limit_page_length=100,
    )


@frappe.whitelist()
def send_message(room: str, content: str):
    user = _user()
    room_doc = _room(room)
    content = (content or "").strip()
    if not content:
        frappe.throw("لا يمكن إرسال رسالة فارغة")
    if len(content) > 20000:
        frappe.throw("الرسالة أطول من الحد المسموح")

    message = frappe.get_doc(
        {
            "doctype": "MASAR Chat Message",
            "room": room_doc.name,
            "sender": user,
            "content": content,
            "sent_at": now_datetime(),
        }
    )
    message.insert(ignore_permissions=True)
    for member in room_doc.members:
        frappe.publish_realtime(
            "masar_chat_message",
            {"room": room_doc.name, "message": message.name},
            user=member.user,
        )
    return {"name": message.name, "sent_at": message.sent_at}


@frappe.whitelist()
def get_messages(room: str, limit: int = 50, before: str | None = None):
    room_doc = _room(room)
    limit = max(1, min(int(limit), 100))
    filters = [["room", "=", room_doc.name]]
    if before:
        filters.append(["sent_at", "<", before])
    rows = frappe.get_list(
        "MASAR Chat Message",
        filters=filters,
        fields=["name", "sender", "content", "sent_at"],
        order_by="sent_at desc",
        limit_page_length=limit,
    )
    rows.reverse()
    return rows


@frappe.whitelist()
def print_messages(
    room: str, from_date: str | None = None, to_date: str | None = None
):
    room_doc = _room(room)
    filters = [["room", "=", room_doc.name]]
    if from_date:
        filters.append(["sent_at", ">=", from_date])
    if to_date:
        filters.append(["sent_at", "<=", to_date])
    messages = frappe.get_list(
        "MASAR Chat Message",
        filters=filters,
        fields=["sender", "content", "sent_at"],
        order_by="sent_at asc",
        limit_page_length=5000,
    )
    return {"title": room_doc.title, "messages": messages}
