"""Provider-neutral, fail-closed AI assistant boundary."""
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
    settings = frappe.conf.get("masar_ai") or {}
    if not settings.get("provider") or not settings.get("api_key"):
        return {"status": "not_configured", "answer": "مساعد الذكاء الاصطناعي لم يتم ربطه بمزود خدمة بعد. ستظل بيانات الشركة داخل النظام."}
    return {"status": "pending_provider_adapter", "answer": "تم حفظ إعدادات المزود، لكن موصل الذكاء الاصطناعي لم يُفعّل قبل اختبار الأمان والخصوصية."}
