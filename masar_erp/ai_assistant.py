"""Provider-neutral AI boundary; deliberately disabled until approved."""
from __future__ import annotations

import frappe


@frappe.whitelist()
def ask(question: str, context: str | None = None):
    user = frappe.session.user
    if not user or user == "Guest":
        frappe.throw("يجب تسجيل الدخول أولاً", frappe.AuthenticationError)

    question = (question or "").strip()
    if not question:
        frappe.throw("اكتب سؤالك أولاً")
    if len(question) > 12000:
        frappe.throw("السؤال أطول من الحد المسموح")
    if context and len(context) > 12000:
        frappe.throw("السياق أطول من الحد المسموح")

    # Context is intentionally not forwarded or trusted until permission-aware
    # retrieval, provider approval, retention terms, and audit controls exist.
    settings = frappe.conf.get("masar_ai") or {}
    if not settings.get("provider") or not settings.get("api_key"):
        return {
            "status": "not_configured",
            "answer": "مساعد الذكاء الاصطناعي غير مربوط بمزود خدمة بعد. لم تُرسل أي بيانات خارج النظام.",
        }
    return {
        "status": "pending_provider_adapter",
        "answer": "إعداد المزود موجود، لكن الموصل متوقف حتى اكتمال اختبارات الأمان والخصوصية.",
    }
