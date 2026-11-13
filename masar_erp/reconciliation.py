"""Read-only General Ledger reconciliation API for MASAR ERP."""
from __future__ import annotations

from decimal import Decimal

import frappe
from frappe import _
from frappe.utils import getdate


def _authorized_company(company: str):
    if not company:
        frappe.throw(_("يجب اختيار الشركة"), frappe.ValidationError)
    doc = frappe.get_doc("Company", company)
    if not frappe.has_permission("Company", "read", doc=doc):
        frappe.throw(_("ليس لديك صلاحية الوصول إلى هذه الشركة"), frappe.PermissionError)
    return doc


@frappe.whitelist()
def get_gl_reconciliation(company: str, from_date: str, to_date: str):
    """Compare permitted, non-cancelled GL debits and credits without changing data."""
    if frappe.session.user == "Guest":
        frappe.throw(_("يجب تسجيل الدخول أولاً"), frappe.AuthenticationError)

    _authorized_company(company)
    if not frappe.has_permission("GL Entry", "read"):
        frappe.throw(_("ليس لديك صلاحية قراءة دفتر الأستاذ العام"), frappe.PermissionError)

    if not from_date or not to_date:
        frappe.throw(_("تاريخ البداية والنهاية مطلوبان"), frappe.ValidationError)

    start = getdate(from_date)
    end = getdate(to_date)
    if start > end:
        frappe.throw(_("تاريخ البداية يجب أن يسبق تاريخ النهاية"), frappe.ValidationError)

    rows = frappe.get_list(
        "GL Entry",
        filters={
            "company": company,
            "posting_date": ["between", [start, end]],
            "is_cancelled": 0,
        },
        fields=["debit", "credit"],
        limit_page_length=0,
    )

    debit = sum((Decimal(str(row.debit or 0)) for row in rows), Decimal("0"))
    credit = sum((Decimal(str(row.credit or 0)) for row in rows), Decimal("0"))
    difference = debit - credit

    return {
        "company": company,
        "from_date": str(start),
        "to_date": str(end),
        "entries_count": len(rows),
        "total_debit": float(debit),
        "total_credit": float(credit),
        "difference": float(difference),
        "balanced": difference == 0,
        "read_only": True,
    }
